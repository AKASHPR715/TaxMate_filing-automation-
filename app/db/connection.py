import os
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Default to local mongo if not set
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "taxmate_db")

logger = logging.getLogger("Database")

class Database:
    client: AsyncIOMotorClient = None
    db_name: str = DB_NAME

    def connect(self):
        """Connect to MongoDB (Async)"""
        try:
            self.client = AsyncIOMotorClient(MONGO_URI)
            logger.info(f"Connected to MongoDB at {MONGO_URI}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e

    def get_db(self):
        if self.client is None:
             self.connect()
        return self.client[self.db_name]

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")

# Sync Connection for Scripts
def get_sync_db():
    try:
        client = MongoClient(MONGO_URI)
        return client[DB_NAME]
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        raise e

db = Database()
