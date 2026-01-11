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

def _find_collection_for_doc(doc_id: str, user_id: str) -> Optional[str]:
    """
    Helper to find which collection a document belongs to.
    Verifies ownership.
    """
    db_client = get_sync_db()
    
    for doc_type, collection_name in COLLECTION_MAP.items():
        try:
            doc = db_client[collection_name].find_one({
                "_id": ObjectId(doc_id)
            })
            if doc:
                # Check ownership - handle both String and ObjectId formats
                doc_user_id = doc.get("user_id")
                if str(doc_user_id) == str(user_id):
                    return doc_type
        except Exception:
            continue
            
    return None

def get_all_documents(user_id: str, doc_type: str = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Fetch all documents for a user, or specific type if provided.
    For get_all, we still need to query by user_id. 
    We should try both ObjectId and String to be safe, OR just assume String if that's what we found.
    """
    db_client = get_sync_db()
    
    # Helper to clean docs
    def clean_docs(cursor):
        results = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            if "user_id" in doc:
                doc["user_id"] = str(doc["user_id"])
            results.append(doc)
        return results

    # Helper to get query
    # We construct a query that matches user_id as String OR ObjectId to be safe
    user_query = {"$or": [
        {"user_id": str(user_id)},
        {"user_id": ObjectId(user_id)}
    ]}

    # If specific type requested
    if doc_type:
        collection_name = COLLECTION_MAP.get(doc_type.lower())
        if not collection_name:
             raise ValueError(f"Invalid document type: {doc_type}")
        
        cursor = db_client[collection_name].find(user_query)
        return clean_docs(cursor)

    # Get all types
    all_docs = {}
    for dtype, collection_name in COLLECTION_MAP.items():
        cursor = db_client[collection_name].find(user_query)
        all_docs[dtype] = clean_docs(cursor)
        
    return all_docs

def get_document(user_id: str, doc_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch a single document by ID, searching all collections.
    """
    db_client = get_sync_db()
    
    for dtype, collection_name in COLLECTION_MAP.items():
        try:
            # Query by ID only first
            doc = db_client[collection_name].find_one({
                "_id": ObjectId(doc_id)
            })
            
            if doc:
                # Verify ownership
                doc_user_id = doc.get("user_id")
                if str(doc_user_id) != str(user_id):
                    # Found document but wrong user
                    continue # Keep searching
                
                doc["id"] = str(doc.pop("_id"))
                doc["user_id"] = str(doc["user_id"])
                doc["doc_type"] = dtype 
                return doc
                
        except Exception as e:
            logger.error(f"Error checking {dtype} for {doc_id}: {e}")
            continue
            
    return None

def update_document(user_id: str, doc_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Update a document by looking it up across collections.
    """
    db_client = get_sync_db()
    
    # Find which collection it is in
    doc_type = _find_collection_for_doc(doc_id, user_id)
    if not doc_type:
        return None
        
    collection_name = COLLECTION_MAP[doc_type]
    
    # Exclude immutable fields
    updates.pop("_id", None)
    updates.pop("user_id", None)
    updates.pop("created_at", None)
    updates.pop("doc_type", None)
    
    updates["updated_at"] = datetime.utcnow()
    
    try:
        result = db_client[collection_name].update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": updates}
        )
        
        return get_document(user_id, doc_id)

    except Exception as e:
        logger.error(f"Error updating document {doc_id}: {e}")
        raise e

def delete_document(user_id: str, doc_id: str) -> bool:
    """
    Delete a document by looking it up across collections.
    """
    db_client = get_sync_db()
    
    doc_type = _find_collection_for_doc(doc_id, user_id)
    if not doc_type:
        return False
        
    collection_name = COLLECTION_MAP[doc_type]
        
    try:
        result = db_client[collection_name].delete_one({
            "_id": ObjectId(doc_id)
        })
        return result.deleted_count > 0
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise e
