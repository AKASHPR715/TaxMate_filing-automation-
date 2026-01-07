"""
Orchestrator API Component
Handles tax orchestration endpoints: extraction, calculation, and analysis.
Uses: orchestrator_service.py
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import asyncio

from app.services.orchestrator_service import TaxOrchestrator, run_orchestrator

router = APIRouter(tags=["orchestrator"])


@router.post("/api/details/extract")
async def extract_details():
    """
    Trigger extraction only and return the raw data for user review.
    
    Returns:
        dict: Extracted tax data from uploaded documents
    """
    try:
        loop = asyncio.get_event_loop()
        boss = TaxOrchestrator()
        # Run extraction in executor
        extracted_data = await loop.run_in_executor(None, boss.run_extraction_only)
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/details/calculate")
async def calculate_with_details(data: Dict[str, Any]):
    """
    Receive confirmed/modified data and run tax computation.
    
    Args:
        data: User-confirmed tax data
        
    Returns:
        dict: Tax calculation results and state
    """
    try:
        loop = asyncio.get_event_loop()
        boss = TaxOrchestrator()
        # Run computation in executor
        print(f"DEBUG: calculate_with_details received data keys: {list(data.keys())}")
        result_state = await loop.run_in_executor(
            None, 
            boss.run_computation_with_data, 
            data, 
            "Finalize Tax Calculation"
        )
        return result_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/analyze")
async def analyze_taxes():
    """
    Run the full tax analysis orchestrator.
    
    Returns:
        dict: Tax analysis results with recommendations
    """
    try:
        # Run the orchestrator logic in executor to avoid blocking
        loop = asyncio.get_event_loop()
        # Use a prompt that specifically asks for recommendations based on the analysis
        prompt = "Analyze my tax situation and provide detailed recommendations for next year's tax planning, specifically highlighting underutilized 80C, 80D, and 80CCD limits."
        result = await loop.run_in_executor(None, run_orchestrator, prompt)
        
        return result
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
