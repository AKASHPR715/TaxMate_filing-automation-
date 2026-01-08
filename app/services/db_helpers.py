"""
Database Helper Utilities for TaxMate
Shared functions for database operations to avoid code duplication.
"""
from typing import Any, Dict, Optional
from bson import ObjectId
import logging

logger = logging.getLogger("db_helpers")


def sensible_find(collection, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Find a document by user_id, handling both string and ObjectId formats.
    
    Args:
        collection: MongoDB collection object
        user_id: User ID (string or ObjectId compatible)
        
    Returns:
        Document dict if found, None otherwise
    """
    # Try string ID first (most common in our system)
    query = {"user_id": str(user_id)}
    doc = collection.find_one(query, sort=[("created_at", -1)])
    
    if not doc:
        # Fallback: try as ObjectId
        try:
            doc = collection.find_one(
                {"user_id": ObjectId(user_id)}, 
                sort=[("created_at", -1)]
            )
        except Exception as e:
            logger.debug(f"Could not convert {user_id} to ObjectId: {e}")
    
    return doc


def load_user_tax_data(db, user_id: str) -> Dict[str, Any]:
    """
    Load all tax documents for a user from the database.
    
    Args:
        db: Database client
        user_id: User ID to fetch data for
        
    Returns:
        Dictionary with keys: form16a, form16b, ais (if found)
    """
    context = {}
    
    # Load Form 16 Part A
    f16a = sensible_find(db.form16_part_as, user_id)
    if f16a:
        context["form16a"] = f16a
        logger.info(f"Loaded Form 16 Part A for user {user_id}")
    
    # Load Form 16 Part B
    f16b = sensible_find(db.form16_part_bs, user_id)
    if f16b:
        context["form16b"] = f16b
        logger.info(f"Loaded Form 16 Part B for user {user_id}")
    
    # Load AIS
    ais = sensible_find(db.ais, user_id)
    if ais:
        context["ais"] = ais
        logger.info(f"Loaded AIS for user {user_id}")
    
    if not context:
        logger.warning(f"No tax documents found for user {user_id}")
    
    return context


def get_user_id_from_header(headers: dict, default: Optional[str] = None) -> Optional[str]:
    """
    Extract user ID from request headers.
    
    Args:
        headers: Request headers dict
        default: Default user_id if not found in headers
        
    Returns:
        User ID string or None
    """
    user_id = headers.get("x-user-id") or headers.get("X-User-Id")
    
    if not user_id and default:
        logger.warning(f"No X-User-Id header found, using default: {default}")
        return default
    
    return user_id
