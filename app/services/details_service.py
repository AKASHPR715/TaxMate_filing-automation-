# ============================================================
# 📄 Details Service
# Handles fetching and updating distinct tax form documents
# ============================================================

from typing import List, Dict, Any, Optional, Type
from datetime import datetime
from bson import ObjectId
from app.db.connection import get_sync_db
from app.db.models import (
    Form16PartA, Form16PartB, AIS, 
    Form16PartA_Schema, Form16PartB_Schema, AIS_Schema
)
import logging

logger = logging.getLogger("DetailsService")

COLLECTION_MAP = {
    "form16a": "form16_part_as",
    "form16b": "form16_part_bs",
    "ais": "ais"
}

MODEL_MAP = {
    "form16a": Form16PartA,
    "form16b": Form16PartB,
    "ais": AIS
}

def get_all_documents(user_id: str, doc_type: str) -> List[Dict[str, Any]]:
    """
    Fetch all documents of a specific type for a user.
    """
    db_client = get_sync_db()
    collection_name = COLLECTION_MAP.get(doc_type.lower())
    
    if not collection_name:
        raise ValueError(f"Invalid document type: {doc_type}")
        
    try:
        # Query by user_id
        cursor = db_client[collection_name].find({"user_id": ObjectId(user_id)})
        
        results = []
        for doc in cursor:
            # Convert ObjectId to str for frontend
            doc["id"] = str(doc.pop("_id"))
            if "user_id" in doc:
                doc["user_id"] = str(doc["user_id"])
            results.append(doc)
            
        return results
    except Exception as e:
        logger.error(f"Error fetching {doc_type} documents for user {user_id}: {e}")
        raise e

def get_document(user_id: str, doc_type: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single document by ID, verifying user ownership.
    """
    db_client = get_sync_db()
    collection_name = COLLECTION_MAP.get(doc_type.lower())
    
    if not collection_name:
        raise ValueError(f"Invalid document type: {doc_type}")
        
    try:
        doc = db_client[collection_name].find_one({
            "_id": ObjectId(doc_id),
            "user_id": ObjectId(user_id)
        })
        
        if doc:
            doc["id"] = str(doc.pop("_id"))
            doc["user_id"] = str(doc["user_id"])
            return doc
        return None
    except Exception as e:
        logger.error(f"Error fetching {doc_type} document {doc_id}: {e}")
        raise e

def update_document(user_id: str, doc_type: str, doc_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a document. Note: This performs a partial update on fields provided.
    For nested updates, we might need more complex logic or just replace the whole nested object.
    
    Args:
        updates: A dictionary containing the fields to update. 
                 It can be deep nested or top level.
                 For simplicity with Mongo, we often use dot notation for nested fields if passed flat,
                 OR we just set the whole top-level field if passed as a dict.
                 
                 Here we assume the 'updates' dict matches the structure of the document partially.
    """
    db_client = get_sync_db()
    collection_name = COLLECTION_MAP.get(doc_type.lower())
    
    if not collection_name:
        raise ValueError(f"Invalid document type: {doc_type}")
        
    # Validation: Check if exists and ownership
    existing_doc = db_client[collection_name].find_one({
        "_id": ObjectId(doc_id),
        "user_id": ObjectId(user_id)
    })
    
    if not existing_doc:
        return None
        
    # Prepare update dict
    # We use $set to update specific fields. 
    # If the user sends nested dicts, we might want to flatten them into dot notation 
    # to avoid overwriting the whole parent object (unless that is desired).
    # For now, let's assume the frontend sends the relevant top-level sections fully if they are changing, 
    # or we just rely on standard $set behavior which merges at top level but replaces values.
    # WAIT - Standard $set with a dict value REPLACES that field's object. 
    # e.g. $set: {"employer_details": {...}} replaces the whole employer_details. 
    # This is usually acceptable for form editing if we send the whole section back.
    
    # We'll just $set the keys provided in updates.
    # Exclude immutable fields
    updates.pop("_id", None)
    updates.pop("user_id", None)
    updates.pop("created_at", None)
    
    updates["updated_at"] = datetime.utcnow()
    
    try:
        result = db_client[collection_name].update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": updates}
        )
        
        if result.modified_count > 0:
            return get_document(user_id, doc_type, doc_id)
        
        # If nothing modified (values same), accept success
        return get_document(user_id, doc_type, doc_id)

    except Exception as e:
        logger.error(f"Error updating {doc_type} document {doc_id}: {e}")
        raise e

def delete_document(user_id: str, doc_type: str, doc_id: str) -> bool:
    """
    Delete a document.
    """
    db_client = get_sync_db()
    collection_name = COLLECTION_MAP.get(doc_type.lower())
    
    if not collection_name:
        raise ValueError(f"Invalid document type: {doc_type}")
        
    try:
        result = db_client[collection_name].delete_one({
            "_id": ObjectId(doc_id),
            "user_id": ObjectId(user_id)
        })
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting {doc_type} document {doc_id}: {e}")
        raise e
