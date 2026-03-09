from fastmcp import FastMCP
import asyncio
from bson import ObjectId
from typing import Dict, Any, List, Optional

# Import TaxMate services
from app.services.orchestrator_service import (
    run_orchestrator,
    extract_all_forms,
    compare_tax_regimes
)
from app.db.connection import get_sync_db
from app.services.db_helpers import load_user_tax_data

# Initialize FastMCP server
mcp = FastMCP("TaxMate")

@mcp.tool()
async def list_uploaded_documents(user_id: str) -> List[Dict[str, Any]]:
    """
    Lists metadata of uploaded tax documents for a user.
    """
    db = get_sync_db()
    # Search in common collections where documents are stored
    # Based on project structure, it seems filings or a specific docs collection might exist
    # Let's check 'details' as seen in API routes
    docs = list(db.details.find({"user_id": user_id}))
    return serialize_data(docs)

@mcp.tool()
async def extract_tax_forms(user_id: str) -> Dict[str, Any]:
    """
    Triggers the LlamaExtract pipeline for the user's uploaded files.
    """
    # Note: the current extract_all_forms might need user_id context 
    # if it's designed to process a specific directory.
    # We'll run it and return the status.
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, extract_all_forms)
    
    db = get_sync_db()
    data = load_user_tax_data(db, user_id)
    return serialize_data({
        "status": "success",
        "message": "Extraction triggered and data loaded.",
        "data_preview": data
    })

@mcp.tool()
async def compare_tax_regimes_tool(user_id: str) -> Dict[str, Any]:
    """
    Compares old vs new tax regimes based on extracted data for the user.
    """
    db = get_sync_db()
    extracted_data = load_user_tax_data(db, user_id)
    
    if not extracted_data:
        return {"error": "No tax documents found. Please extract data first."}

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None, 
        compare_tax_regimes,
        extracted_data,
        user_id
    )
    return serialize_data(result)

@mcp.tool()
async def get_tax_advice(user_id: str, query: str = "Optimize my tax situation") -> Dict[str, Any]:
    """
    Runs the orchestrator to provide personalized tax recommendations based on a query.
    """
    loop = asyncio.get_event_loop()
    final_state = await loop.run_in_executor(
        None,
        run_orchestrator,
        query,
        user_id
    )
    return serialize_data(final_state)

@mcp.resource("taxmate://{user_id}/filing_status")
def get_filing_status(user_id: str) -> str:
    """
    Returns the current status of the user's ITR filing.
    """
    db = get_sync_db()
    itr = db.filings.find_one({"user_id": ObjectId(user_id)}, sort=[("created_at", -1)])
    if itr:
        return f"Status for {user_id}: {itr.get('status', 'DRAFT')}"
    return f"No filing found for {user_id}. Setup required."

@mcp.resource("taxmate://{user_id}/extraction_summary")
def get_extraction_summary(user_id: str) -> str:
    """
    Returns the summary of the latest extracted tax data.
    """
    db = get_sync_db()
    data = load_user_tax_data(db, user_id)
    if data:
        import json
        return json.dumps(serialize_data(data), indent=2)
    return "No extracted data available."

# Helper for JSON serialization
def serialize_data(data: Any) -> Any:
    if isinstance(data, dict):
        return {k: serialize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_data(item) for item in data]
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

if __name__ == "__main__":
    mcp.run()
