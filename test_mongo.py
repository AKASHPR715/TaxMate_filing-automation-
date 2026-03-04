
import os
from dotenv import load_dotenv
from pymongo import MongoClient
import sys

load_dotenv()

mongo_uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME")

print(f"Connecting to: {mongo_uri.split('@')[-1] if mongo_uri else 'None'}")
print(f"Target DB: {db_name}")

try:
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    # The ismaster command is cheap and does not require auth.
    client.admin.command('ismaster')
    print("✅ MongoDB connection successful!")
    
    db = client[db_name]
    collections = db.list_collection_names()
    print(f"✅ Database access successful! Collections: {collections}")
    
except Exception as e:
    print(f"❌ MongoDB connection failed: {e}")
    sys.exit(1)
