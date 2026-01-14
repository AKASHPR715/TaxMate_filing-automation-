"""
Orchestrator API Component
Handles tax orchestration endpoints: extraction, calculation, and analysis.
Uses: orchestrator_service.py (LangGraph)
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any, List
import asyncio
from bson import ObjectId

# Import run_orchestrator and direct services
from app.services.orchestrator_service import (
    run_orchestrator, 
    extract_all_forms, 
    compare_tax_regimes
)
from app.api.auth_routes import get_current_user
from app.db.models import User, ITR
from app.services import details_service
from pydantic import BaseModel
from typing import Optional

router = APIRouter(tags=["orchestrator"])

# Helper for JSON serialization
def serialize_data(data: Any) -> Any:
    """Recursively convert ObjectId to str for JSON serialization."""
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

@router.post("/api/details/extract")
async def extract_details(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Trigger extraction and return the raw data for user review.
    Directly calls the extraction service.
    """
    try:
        from app.services.db_helpers import load_user_tax_data
        from app.db.connection import get_sync_db
        from app.services.form_extraction_service import get_or_create_default_user
        
        # Get user_id from authenticated user
        loop = asyncio.get_event_loop()
        user_id = str(current_user["_id"])
        
        # Check if data already exists for this user
        def check_and_extract():
            db = get_sync_db()
            extracted_data = load_user_tax_data(db, user_id)
            
            if not extracted_data:
                # No data found, trigger extraction
                extract_all_forms()
                # Re-fetch after extraction
                extracted_data = load_user_tax_data(db, user_id)
            
            return extracted_data
        
        result = await loop.run_in_executor(None, check_and_extract)
        
        if result:
            return serialize_data({
                "status": "success",
                "user_id": user_id,
                "data": result,
                "message": f"Extracted data loaded for user {user_id}"
            })
        else:
            return serialize_data({
                "status": "no_data",
                "user_id": user_id,
                "data": {},
                "message": "No tax documents found. Please upload PDFs via the UI."
            })
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/details/calculate")
async def calculate_with_details(request: Request, current_user: dict = Depends(get_current_user)):
    """
    Fetch user data from DB and run tax computation.
    """
    try:
        from app.services.db_helpers import load_user_tax_data
        from app.db.connection import get_sync_db
        
        loop = asyncio.get_event_loop()
        
        # Get user_id from authenticated user
        user_id = str(current_user["_id"])
        
        # Helper to run comparison with provided data
        def run_calculation():
            db = get_sync_db()
            extracted_data = load_user_tax_data(db, user_id)
            
            if not extracted_data:
                raise ValueError("No tax documents found. Please upload Form 16 or AIS first.")

            # adapting dict to service expectation
            result = compare_tax_regimes(extracted_data=extracted_data, user_id=user_id)
            return result

        result = await loop.run_in_executor(None, run_calculation)
        return serialize_data(result)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analyze")
async def analyze_taxes(current_user: dict = Depends(get_current_user)):
    """
    Run the full tax analysis orchestrator for the authenticated user.
    """
    try:
        loop = asyncio.get_event_loop()
        user_id = str(current_user["_id"])
        prompt = "Analyze my tax situation and provide detailed recommendations."
        
        # Pass user_id to orchestrator
        final_state = await loop.run_in_executor(
            None, 
            run_orchestrator, 
            prompt,
            user_id
        )
        
        return serialize_data(final_state)
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

# Request Models
class DocumentUpdate(BaseModel):
    doc_id: str
    updates: Dict[str, Any]

class ReviewAndCalculateRequest(BaseModel):
    updates: Optional[List[DocumentUpdate]] = None
    force_restart: bool = False

@router.post("/api/orchestrator/review_and_calculate")
async def review_and_calculate(
    payload: ReviewAndCalculateRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Trigger the Archerstrator Agent after review.
    - Validates user role (Boss/Agent).
    - Updates provided document fields.
    - Runs the orchestrator.
    """
    try:
        from app.db.connection import get_sync_db
        db = get_sync_db()
        
        user_id = str(current_user["_id"])
        
        # 1. Validate Role
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        is_boss = user.get("role") == "boss"
        is_agent = user.get("role") == "agent" or "Archerstrator" in user.get("username", "")
        
        if not (is_boss or is_agent):
            # Fallback for dev/admin
            if user.get("username") == "admin":
                 pass
            else:
                 raise HTTPException(
                    status_code=403, 
                    detail="Unauthorized: Only Boss or Archerstrator Agent can trigger this workflow."
                )

        # 2. Check State (Optional, but requested)
        # We check ITR status if it exists
        itr = db.itr_filings.find_one({"user_id": ObjectId(user_id)}, sort=[("created_at", -1)])
        if itr:
            status = itr.get("status", "DRAFT")
            # We allow REVIEW or DRAFT (since DRAFT is the initial state)
            if status not in ["REVIEW", "DRAFT"]:
                 # If it's FINAL or FILED, maybe we shouldn't allow updates
                 if status in ["FINAL", "FILED"]:
                      raise HTTPException(status_code=400, detail=f"Cannot update record in {status} state.")

        # 3. Apply Updates
        if payload.updates:
            for update_item in payload.updates:
                details_service.update_document(
                    user_id=user_id,
                    doc_id=update_item.doc_id,
                    updates=update_item.updates
                )

        # 4. Trigger Archerstrator Agent
        loop = asyncio.get_event_loop()
        prompt = "Review complete. Calculate taxes and generate forms."
        
        final_state = await loop.run_in_executor(
            None, 
            run_orchestrator, 
            prompt,
            user_id
        )
        
        return serialize_data({
            "status": "success",
            "message": "Review processed and Archerstrator Agent triggered.",
            "orchestrator_result": final_state
        })

    except HTTPException as he:
        raise he
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

