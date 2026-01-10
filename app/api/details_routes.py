from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List, Dict, Any, Optional
from app.api.auth_routes import get_current_user
from app.services import details_service
import logging

router = APIRouter(prefix="/api/details", tags=["details"])
logger = logging.getLogger("DetailsAPI")

@router.get("/all")
async def get_all_user_documents(current_user: dict = Depends(get_current_user)):
    """
    Fetch all available extracted documents for the current user.
    Returns a summary structure.
    """
    user_id = str(current_user["_id"])
    try:
        form16as = details_service.get_all_documents(user_id, "form16a")
        form16bs = details_service.get_all_documents(user_id, "form16b")
        ais_docs = details_service.get_all_documents(user_id, "ais")
        
        return {
            "form16a": form16as,
            "form16b": form16bs,
            "ais": ais_docs
        }
    except Exception as e:
        logger.error(f"Error fetching all documents: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@router.get("/{doc_type}/{doc_id}")
async def get_document_details(
    doc_type: str, 
    doc_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Get a specific document by ID.
    """
    user_id = str(current_user["_id"])
    
    if doc_type not in ["form16a", "form16b", "ais"]:
        raise HTTPException(status_code=400, detail="Invalid document type")
        
    try:
        doc = details_service.get_document(user_id, doc_type, doc_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        return doc
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/{doc_type}/{doc_id}")
async def update_document_details(
    doc_type: str, 
    doc_id: str, 
    updates: Dict[str, Any] = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Update specific fields in a document.
    """
    user_id = str(current_user["_id"])
    
    if doc_type not in ["form16a", "form16b", "ais"]:
        raise HTTPException(status_code=400, detail="Invalid document type")
        
    try:
        updated_doc = details_service.update_document(user_id, doc_type, doc_id, updates)
        if not updated_doc:
             raise HTTPException(status_code=404, detail="Document not found or update failed")
        return updated_doc
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{doc_type}/{doc_id}")
async def delete_document(
    doc_type: str, 
    doc_id: str, 
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a document.
    """
    user_id = str(current_user["_id"])
    
    if doc_type not in ["form16a", "form16b", "ais"]:
        raise HTTPException(status_code=400, detail="Invalid document type")
        
    try:
        success = details_service.delete_document(user_id, doc_type, doc_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found or delete failed")
        return {"status": "success", "message": "Document deleted"}
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
