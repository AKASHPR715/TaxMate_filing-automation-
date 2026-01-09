"""
Orchestrator API Component
Handles tax orchestration endpoints: extraction, calculation, and analysis.
Uses: orchestrator_service.py (LangGraph)
"""
from fastapi import APIRouter, HTTPException, Request, Depends
from typing import Dict, Any
import asyncio

# Import run_orchestrator and direct services
from app.services.orchestrator_service import (
    run_orchestrator, 
    extract_all_forms, 
    compare_tax_regimes
)
from app.api.auth_routes import get_current_user

router = APIRouter(tags=["orchestrator"])


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
                # NOTE: extract_all_forms primarily works with local files in data/uploads
                # Ideally, we should ensure files are associated with user_id
                extract_all_forms()
                # Re-fetch after extraction
                extracted_data = load_user_tax_data(db, user_id)
            
            return extracted_data
        
        result = await loop.run_in_executor(None, check_and_extract)
        
        if result:
            return {
                "status": "success",
                "user_id": user_id,
                "data": result,
                "message": f"Extracted data loaded for user {user_id}"
            }
        else:
            return {
                "status": "no_data",
                "user_id": user_id,
                "data": {},
                "message": "No tax documents found. Please upload PDFs via the UI."
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/details/calculate")
async def calculate_with_details(data: Dict[str, Any], request: Request, current_user: dict = Depends(get_current_user)):
    """
    Receive confirmed/modified data and run tax computation.
    """
    try:
        
        print(f"DEBUG: calculate_with_details received data keys: {list(data.keys())}")
        loop = asyncio.get_event_loop()
        
        # Get user_id from authenticated user
        user_id = str(current_user["_id"])
        
        # Helper to run comparison with provided data
        def run_calculation():
            # adapting dict to service expectation
            # We can use the service directly OR the orchestrator with pre-filled state
            result = compare_tax_regimes(extracted_data=data, user_id=user_id)
            return result

        result = await loop.run_in_executor(None, run_calculation)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analyze")
async def analyze_taxes():
    """
    Run the full tax analysis orchestrator.
    """
    try:
        loop = asyncio.get_event_loop()
        prompt = "Analyze my tax situation and provide detailed recommendations."
        # run_orchestrator returns the final state (AgentState dict)
        final_state = await loop.run_in_executor(None, run_orchestrator, prompt)
        
        return final_state
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
