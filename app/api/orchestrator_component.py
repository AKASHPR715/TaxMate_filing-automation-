"""
Orchestrator API Component
Handles tax orchestration endpoints: extraction, calculation, and analysis.
Uses: orchestrator_service.py (LangGraph)
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import asyncio

# Import run_orchestrator and direct services
from app.services.orchestrator_service import (
    run_orchestrator, 
    extract_all_forms, 
    compare_tax_regimes
)

router = APIRouter(tags=["orchestrator"])


@router.post("/api/details/extract")
async def extract_details(request: Request):
    """
    Trigger extraction and return the raw data for user review.
    Directly calls the extraction service.
    """
    try:
        from app.services.db_helpers import get_user_id_from_header, load_user_tax_data
        from app.db.connection import get_sync_db
        from app.services.form_extraction_service import get_or_create_default_user
        
        # Get user_id from header or default to test user
        loop = asyncio.get_event_loop()
        headers = dict(request.headers)
        user_id = get_user_id_from_header(headers)
        
        # If no user_id, get default test user
        if not user_id:
            def get_default_user():
                db = get_sync_db()
                return str(get_or_create_default_user(db))
            user_id = await loop.run_in_executor(None, get_default_user)
        
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
async def calculate_with_details(data: Dict[str, Any], request: Request):
    """
    Receive confirmed/modified data and run tax computation.
    Supports user_id in request body or X-User-Id header.
    """
    try:
        from app.services.db_helpers import get_user_id_from_header
        
        print(f"DEBUG: calculate_with_details received data keys: {list(data.keys())}")
        loop = asyncio.get_event_loop()
        
        # Get user_id from data or header
        user_id = data.pop("user_id", None)
        if not user_id:
            headers = dict(request.headers)
            user_id = get_user_id_from_header(headers)
        
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
