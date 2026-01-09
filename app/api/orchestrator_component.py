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
