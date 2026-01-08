import sys
import os
import json
import glob
from pathlib import Path
from datetime import datetime
from bson import ObjectId

# Add project root to python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from app.db.connection import get_sync_db
from app.db.models import User, FilingMission, ExtractedData, Filing, TaxDocument

def populate_db():
    print("🚀 Starting Database Population...")
    db = get_sync_db()
    
    # 1. Create Default User
    users_coll = db["users"]
    user_data = {
        "email": "test@example.com",
        "full_name": "Test User",
        "profile_data": load_user_profile(),
        "created_at": datetime.utcnow()
    }
    
    # Upsert user
    user = users_coll.find_one({"email": user_data["email"]})
    if not user:
        result = users_coll.insert_one(user_data)
        user_id = result.inserted_id
        print(f"✔ Created User: {user_id}")
    else:
        user_id = user["_id"]
        print(f"ℹ Found existing User: {user_id}")

    # 2. Create Defaults Mission
    missions_coll = db["filing_missions"]
    mission_data = {
        "user_id": user_id,
        "financial_year": "2024-25",
        "assessment_year": "2025-26",
        "status": "IN_PROGRESS",
        "created_at": datetime.utcnow()
    }
    
    mission = missions_coll.find_one({"user_id": user_id, "financial_year": "2024-25"})
    if not mission:
        res = missions_coll.insert_one(mission_data)
        mission_id = res.inserted_id
        print(f"✔ Created Mission: {mission_id}")
    else:
        mission_id = mission["_id"]
        print(f"ℹ Found Mission: {mission_id}")

    # 3. Populate Extracted Data
    extracted_coll = db["extracted_data"]
    extracted_dir = project_root / "app" / "data" / "extracted"
    
    for file_path in extracted_dir.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            doc_type = determine_doc_type(file_path.name)
            
            # Check if exists
            exists = extracted_coll.find_one({
                "mission_id": mission_id,
                "doc_type": doc_type,
                "raw_data": data # Naive check, mainly to prevent dupes in naive runs
            })
            
            # Better check: by filename content hash or unique key logic from extracted data
            # For now, let's just insert if not exact duplicate
            if not exists:
                record = {
                    "mission_id": mission_id,
                    "doc_type": doc_type,
                    "raw_data": data,
                    "verified_data": data, # Assume initially valid
                    "human_verification_status": "PENDING",
                    "created_at": datetime.fromtimestamp(file_path.stat().st_ctime)
                }
                extracted_coll.insert_one(record)
                print(f"✔ Imported Extraction: {file_path.name}")
        except Exception as e:
            print(f"❌ Failed to import {file_path.name}: {e}")

    # 4. Populate Filings
    filings_coll = db["filings"]
    filing_dir = project_root / "app" / "data" / "filing"
    
    for file_path in filing_dir.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            
            form_type = "ITR-2" if "ITR2" in data.get("ITR", {}) else "ITR-1"
            
            exists = filings_coll.find_one({"mission_id": mission_id, "form_type": form_type})
            
            # Always keep latest? Or insert all versions?
            # Let's insert as new version
            version = filings_coll.count_documents({"mission_id": mission_id, "form_type": form_type}) + 1
            
            record = {
                "mission_id": mission_id,
                "form_type": form_type,
                "form_data": data,
                "version": version,
                "is_final": False,
                "created_at": datetime.fromtimestamp(file_path.stat().st_ctime)
            }
            filings_coll.insert_one(record)
            print(f"✔ Imported Filing: {file_path.name} (v{version})")

        except Exception as e:
            print(f"❌ Failed to import filing {file_path.name}: {e}")

    print("✨ Database Population Complete!")

def determine_doc_type(filename):
    lower = filename.lower()
    if "form16a" in lower: return "FORM16_PART_A"
    if "form16b" in lower: return "FORM16_PART_B"
    if "ais" in lower: return "AIS"
    return "UNKNOWN"

def load_user_profile():
    path = project_root / "app" / "data" / "user_profile.json"
    if path.exists():
        try:
            with open(path, "r") as f: return json.load(f)
        except: return {}
    return {}

if __name__ == "__main__":
    populate_db()
