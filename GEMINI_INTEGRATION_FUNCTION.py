"""
Updated process_uploaded_file function with Gemini Vision support
Copy this to replace the existing function in form_extraction_service.py
"""

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
