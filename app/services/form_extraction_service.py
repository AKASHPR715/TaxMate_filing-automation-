# ============================================================
# 📄 Unified Tax Form Extraction Pipeline (VS Code-ready)
# ============================================================

import os
from pathlib import Path
import json
import uuid
from datetime import datetime
from typing import List, Optional, Type
from pydantic import BaseModel
from llama_cloud_services import LlamaExtract
from llama_cloud.types import ExtractConfig
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
from pymongo import MongoClient

# Import DB Models and Connection
from app.db.models import (
    Form16PartA, Form16PartB, AIS, User,
    Form16PartA_Schema, Form16PartB_Schema, AIS_Schema
)
from app.db.connection import get_sync_db

# ============================================================
# Logging Configuration for form_extraction.py
# ============================================================
def setup_extraction_logger():
    """Set up logging for form extraction to separate log file."""
    log_dir = Path(__file__).resolve().parents[1] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "form_extraction.log"
    
    logger = logging.getLogger("form_extraction")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler with rotation
        fh = RotatingFileHandler(
            log_file, 
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
            encoding="utf-8"
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter(
            "%(levelname)s: %(message)s"
        ))
        logger.addHandler(ch)
    
    return logger

extraction_logger = setup_extraction_logger()

# ------------------------------------------------------------
# 🔐 Load environment variables and initialize extractors
# ------------------------------------------------------------
load_dotenv()  # Loads .env file

# Gemini Vision (NEW - Faster!)
USE_GEMINI_VISION = os.getenv("USE_GEMINI_VISION", "true").lower() == "true"
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Legacy LlamaExtract (Fallback)
LLAMA_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# Try to use Gemini Vision first
if USE_GEMINI_VISION and GOOGLE_API_KEY:
    extraction_logger.info("🚀 Using Gemini Vision for extraction (6-12x faster!)")
    try:
        from app.services.gemini_vision_extraction import (
            GeminiVisionExtractor,
            extract_form16a_vision,
            extract_form16b_vision,
            extract_ais_vision
        )
        EXTRACTION_METHOD = "gemini"
        extraction_logger.info("✅ Gemini Vision loaded successfully")
    except ImportError as e:
        extraction_logger.error(f"❌ Failed to import Gemini Vision: {e}")
        extraction_logger.info("Falling back to LlamaExtract")
        USE_GEMINI_VISION = False

# Initialize LlamaExtract if Gemini not available or as fallback
if not USE_GEMINI_VISION or not GOOGLE_API_KEY:
    if not LLAMA_API_KEY:
        raise ValueError("Please set either GOOGLE_API_KEY or LLAMA_CLOUD_API_KEY in your .env file.")
    
    extraction_logger.info("Using LlamaExtract (legacy method)")
    # Initialize extractor with reduced timeouts (was 10 minutes, now 2 minutes)
    extractor = LlamaExtract(
        api_key=LLAMA_API_KEY,
        max_timeout=120000,   # 2 minutes (reduced from 10)
        httpx_timeout=120.0   # 2 minutes
    )
    EXTRACTION_METHOD = "llama"

# ============================================================
# 🛡️ Database Helper Functions
# ============================================================

def get_or_create_default_user(db_client) -> str:
    """
    Get a default user for standalone script execution context.
    If no user exists, create a Test User.
    """
    users_collection = db_client["users"]
    
    # Try to find an existing user - specifically "Test User" if possible
    user = users_collection.find_one({"full_name": "Test User"})
    if not user:
        # If no Test User, try ANY user
        user = users_collection.find_one({})
    
    if user:
        extraction_logger.info(f"Using existing user: {user.get('full_name')} ({user['_id']})")
        return user["_id"]
    
    # Create new Test User if database is empty
    new_user = User(
        email="test_user@example.com",
        full_name="Test User",
        pan_number="ABCDE1234F"
    )
    # Convert to dict for mongo insertion (excluding _id to let mongo or model handle it)
    user_dict = new_user.model_dump(by_alias=True, exclude={"id"})
    result = users_collection.insert_one(user_dict)
    extraction_logger.info(f"Created new Test User with ID: {result.inserted_id}")
    return result.inserted_id

def save_extraction_to_db(data: dict, schema_class: Type[BaseModel], user_id, source_file: str):
    """
    Save extracted data to the appropriate MongoDB collection based on the schema class.
    """
    db_client = get_sync_db()
    
    # Map Extraction Schema -> DB Model
    # Since we use Base schemas for extraction, but need to save to DB collections
    if schema_class in [Form16PartA, Form16PartA_Schema]:
        collection_name = "form16_part_as"
        db_model = Form16PartA
    elif schema_class in [Form16PartB, Form16PartB_Schema]:
        collection_name = "form16_part_bs"
        db_model = Form16PartB
    elif schema_class in [AIS, AIS_Schema]:
        collection_name = "ais"
        db_model = AIS
    else:
        extraction_logger.warning(f"Unknown schema class {schema_class.__name__}, skipping DB save.")
        return

    try:
        # Instantiate model to validate and add fields
        # Note: input data is pure dict, we need to add user_id and source_file
        model_instance = db_model(
            user_id=user_id,
            source_file=Path(source_file).name,
            **data
        )
        
        # Convert back to dict for storage
        document = model_instance.model_dump(by_alias=True, exclude={"id"})
        
        # Insert
        result = db_client[collection_name].insert_one(document)
        extraction_logger.info(f"✅ Saved to DB collection '{collection_name}' with ID: {result.inserted_id}")
        return result.inserted_id

    except Exception as e:
        extraction_logger.error(f"❌ Failed to save to DB: {e}")
        # We don't raise here to avoid stopping the whole pipeline, but we log explicitly
        return None


# ============================================================
# 🚀 Extraction Pipeline (modified for local files)
# ============================================================

def extract_all_forms():
    """
    Extract all tax forms using Llama Cloud API and save to data/extracted/ AND MongoDB.
    Discovers files in uploads directory based on doc_type prefixes (form16a_, form16b_, ais_).
    """
    extraction_logger.info("Starting form extraction process...")
    
    # Connect to DB and get user context
    try:
        db_client = get_sync_db()
        user_id = get_or_create_default_user(db_client)
    except Exception as e:
        extraction_logger.error(f"Could not connect to database: {e}")
        raise e

    # Map doc_type prefixes to schemas
    doc_type_schemas = {
        "form16a": Form16PartA_Schema,
        "form16b": Form16PartB_Schema,
        "ais": AIS_Schema,
    }

    # Define upload directory
    APP_ROOT = Path(__file__).resolve().parents[1]
    upload_dirs = [
        Path.cwd() / "app" / "data" / "uploads",  # from project root
        APP_ROOT / "data" / "uploads",  # from app root
    ]
    
    # Find the uploads directory that exists
    uploads_dir = None
    for dir_path in upload_dirs:
        if dir_path.exists():
            uploads_dir = dir_path
            extraction_logger.info(f"Using uploads directory: {uploads_dir}")
            break
    
    if not uploads_dir:
        extraction_logger.warning("No uploads directory found")
        raise ValueError("No uploads directory found")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    extracted_count = 0

    # Discover and process files for each doc_type
    for doc_type, schema in doc_type_schemas.items():
        # Find files with this doc_type prefix
        matching_files = []
        try:
            for file_path in uploads_dir.iterdir():
                if file_path.is_file() and file_path.suffix.lower() == '.pdf' and file_path.name.startswith(doc_type + "_"):
                    matching_files.append(file_path)
        except Exception as e:
            extraction_logger.error(f"Error listing files in {uploads_dir}: {e}")
            continue
        
        if not matching_files:
            extraction_logger.warning(f"⚠️  No files found with prefix '{doc_type}_' in {uploads_dir}. Skipping.")
            continue
        
        # Process the most recent file for this doc_type
        file_path = max(matching_files, key=lambda p: p.stat().st_mtime)
        extraction_logger.info(f"Processing {doc_type}: {file_path.name}")
        
        try:
            # Create agent and extract
            agent_name = f"{file_path.stem}-{uuid.uuid4().hex}"
            extraction_logger.info(f"Creating agent with name: {agent_name}")
            extraction_logger.info(f"Using schema: {schema.__name__}")
            
            config = ExtractConfig(invalidate_cache=True)
            agent = extractor.create_agent(name=agent_name, data_schema=schema, config=config)
            extraction_logger.info("Agent created successfully with cache invalidation, starting extraction...")
            
            result = agent.extract(str(file_path))
            
            # Parse result
            if hasattr(result, 'data') and result.data:
                extracted_dict = result.data
            else:
                raise ValueError(f"Unexpected result format from LlamaExtract for {file_path.name}")
            
            # 1. Save to JSON (Backup/Debug)
            output_dir = APP_ROOT / "data" / "extracted"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / f"{doc_type}_{timestamp}.json"
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(extracted_dict, f, indent=4, ensure_ascii=False)
            
            extraction_logger.info(f"JSON saved -> {output_path}")
            
            # 2. Save to DB
            save_extraction_to_db(extracted_dict, schema, user_id, str(file_path))
            
            extracted_count += 1
            
        except Exception as e:
            extraction_logger.error(f"ERROR: Failed to extract {file_path}: {e}")
            continue

    if extracted_count == 0:
        raise ValueError("No tax documents were extracted. Please upload PDF files via the UI (Form 16 Part A, Form 16 Part B, or AIS).")
    
    extraction_logger.info(f"Successfully extracted {extracted_count} document(s)")


def process_uploaded_file(file_path: str, doc_type: str, user_id=None):
    """
    Process a single uploaded file based on its document type.
    Uses Gemini Vision if enabled, otherwise falls back to LlamaExtract.
    """
    extraction_logger.info(f"📄 Processing: {file_path} as {doc_type}")
    
    if not user_id:
         # Fallback for testing/manual calls
         try:
            db_client = get_sync_db()
            user_id = get_or_create_default_user(db_client)
         except Exception as e:
              extraction_logger.error(f"DB Connection failed: {e}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    schema_map = {
        "form16a": Form16PartA_Schema,
        "form16b": Form16PartB_Schema,
        "ais": AIS_Schema,
    }
    
    schema = schema_map.get(doc_type.lower())
    if not schema:
        raise ValueError(f"Unknown document type: {doc_type}")
    
    try:
        # Try Gemini Vision first if enabled
        if EXTRACTION_METHOD == "gemini":
            extraction_logger.info(f"🤖 Using Gemini Vision")
            
            # Map doc_type to extraction function
            gemini_extractors = {
                "form16a": extract_form16a_vision,
                "form16b": extract_form16b_vision,
                "ais": extract_ais_vision,
            }
            
            extractor_func = gemini_extractors.get(doc_type.lower())
            if not extractor_func:
                raise ValueError(f"Unknown document type for Gemini: {doc_type}")
            
            # Extract using Gemini Vision
            result_data = extractor_func(file_path)
            extraction_logger.info(f"✅ Gemini extraction successful")
            
        else:
            # Use LlamaExtract (legacy)
            extraction_logger.info(f"🔄 Using LlamaExtract")
            
            agent_name = f"{Path(file_path).stem}-{uuid.uuid4().hex}"
            extraction_logger.info(f"Creating agent: {agent_name}")
            extraction_logger.info(f"Using schema: {schema.__name__}")
            
            config = ExtractConfig(invalidate_cache=True)
            agent = extractor.create_agent(name=agent_name, data_schema=schema, config=config)
            extraction_logger.info(f"Agent created, starting extraction...")
            
            result = agent.extract(file_path)
            result_data = result.data
            extraction_logger.info(f"Result preview: {json.dumps(result_data, indent=2, default=str)[:200]}...")
        
        # Save to JSON (Backup/Debug)
        APP_ROOT = Path(__file__).resolve().parents[1]
        output_dir = APP_ROOT / "data" / "extracted"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{Path(file_path).stem}_{timestamp}.json"
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result_data, f, indent=4, ensure_ascii=False)
            
        # Save to DB
        save_extraction_to_db(result_data, schema, user_id, file_path)

        extraction_logger.info(f"✅ Complete → {output_path}")
        return result_data

    except Exception as e:
        extraction_logger.error(f"❌ Extraction failed: {e}")
        
        # If Gemini failed and LlamaExtract is available, try fallback
        if EXTRACTION_METHOD == "gemini" and LLAMA_API_KEY:
            extraction_logger.warning("⚠️  Trying LlamaExtract fallback...")
            try:
                # Initialize LlamaExtract on-demand for fallback
                llama_extractor = LlamaExtract(
                    api_key=LLAMA_API_KEY,
                    max_timeout=120000,
                    httpx_timeout=120.0
                )
                
                agent_name = f"{Path(file_path).stem}-{uuid.uuid4().hex}"
                config = ExtractConfig(invalidate_cache=True)
                agent = llama_extractor.create_agent(name=agent_name, data_schema=schema, config=config)
                
                result = agent.extract(file_path)
                result_data = result.data
                
                # Save fallback result
                APP_ROOT = Path(__file__).resolve().parents[1]
                output_dir = APP_ROOT / "data" / "extracted"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"{Path(file_path).stem}_{timestamp}.json"
                
                with open(output_path, "w", encoding="utf-8") as f:
                    json.dump(result_data, f, indent=4, ensure_ascii=False)
                    
                save_extraction_to_db(result_data, schema, user_id, file_path)
                extraction_logger.info(f"✅ Fallback successful → {output_path}")
                return result_data
                
            except Exception as fallback_error:
                extraction_logger.error(f"❌ Fallback also failed: {fallback_error}")
                raise fallback_error
        
        raise e

# ============================================================
# 🧩 Run
# ============================================================
if __name__ == "__main__":
    extract_all_forms()