import sys
import os
from pathlib import Path
from pymongo import ASCENDING, DESCENDING

# Add project root to python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from app.db.connection import get_sync_db

def init_db():
    print("🚀 Initializing Database Collections & Indexes...")
    db = get_sync_db()
    
    # 1. Users
    # ---------------------------------------------------------
    print("🔹 Initializing 'users'...")
    if "users" not in db.list_collection_names():
        db.create_collection("users")
    
    # Create Indexes
    db.users.create_index([("email", ASCENDING)], unique=True)
    db.users.create_index([("username", ASCENDING)], unique=True)
    print("   ✅ Indexes created: email (unique), username (unique)")

    # 2. Form 16 Part A
    # ---------------------------------------------------------
    print("🔹 Initializing 'form16_part_as'...")
    if "form16_part_as" not in db.list_collection_names():
        db.create_collection("form16_part_as")
        
    db.form16_part_as.create_index([("user_id", ASCENDING)])
    print("   ✅ Indexes created: user_id")

    # 3. Form 16 Part B
    # ---------------------------------------------------------
    print("🔹 Initializing 'form16_part_bs'...")
    if "form16_part_bs" not in db.list_collection_names():
        db.create_collection("form16_part_bs")
    
    db.form16_part_bs.create_index([("user_id", ASCENDING)])
    print("   ✅ Indexes created: user_id")

    # 4. AIS
    # ---------------------------------------------------------
    print("🔹 Initializing 'ais'...")
    if "ais" not in db.list_collection_names():
        db.create_collection("ais")
        
    db.ais.create_index([("user_id", ASCENDING)])
    print("   ✅ Indexes created: user_id")

    # 5. Filings (ITR)
    # ---------------------------------------------------------
    print("🔹 Initializing 'filings'...")
    if "filings" not in db.list_collection_names():
        db.create_collection("filings")
        
    db.filings.create_index([("user_id", ASCENDING)])
    db.filings.create_index([("created_at", DESCENDING)])
    print("   ✅ Indexes created: user_id, created_at")
    
    # 6. Token Blacklist (Auth)
    # ---------------------------------------------------------
    print("🔹 Initializing 'token_blacklist'...")
    if "token_blacklist" not in db.list_collection_names():
        db.create_collection("token_blacklist")
    
    # TTL Index for token expiration (optional, assuming 24h)
    # db.token_blacklist.create_index("blacklisted_on", expireAfterSeconds=86400)
    
    print("\n✨ Database Initialization Complete! Schemas (Collections/Indexes) are ready.")

if __name__ == "__main__":
    init_db()
