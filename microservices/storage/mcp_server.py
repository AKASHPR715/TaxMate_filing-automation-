from fastmcp import FastMCP
import asyncio
from bson import ObjectId
from typing import Dict, Any, List
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.db.connection import get_sync_db
from app.services.db_helpers import load_user_tax_data

mcp = FastMCP("TaxMate-Storage")

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

@mcp.tool()
async def get_user_tax_data(user_id: str) -> Dict[str, Any]:
    """Fetches extracted Form 16 and AIS data for a specific user."""
    db = get_sync_db()
    data = load_user_tax_data(db, user_id)
    return serialize_data(data)

@mcp.tool()
async def save_user_tax_data(user_id: str, document_type: str, data: Dict[str, Any]) -> Dict[str, str]:
    """
    Persists extracted or computed tax data for a user.
    document_type must be one of: form16a, form16b, ais, details.
    """
    db = get_sync_db()
    
    collection_map = {
        "form16a": db.form16_part_as,
        "form16b": db.form16_part_bs,
        "ais": db.ais,
        "details": db.details
    }
    
    collection = collection_map.get(document_type.lower())
    if not collection:
        return {"error": f"Invalid document_type. Must be one of {list(collection_map.keys())}"}
    
    # Store ID strictly as string to avoid ObjectId serialization issues across microservices
    data["user_id"] = str(user_id)
    result = collection.insert_one(data)
    return {"status": "success", "inserted_id": str(result.inserted_id)}

@mcp.tool()
async def get_filing_status(user_id: str) -> Dict[str, str]:
    """Returns the current status of the user's ITR filing."""
    db = get_sync_db()
    # Try ObjectId first
    try:
        itr = db.filings.find_one({"user_id": ObjectId(user_id)}, sort=[("created_at", -1)])
        if itr:
            return {"status": itr.get("status", "DRAFT")}
    except:
        pass
        
    # Try string ID fallback
    itr_str = db.filings.find_one({"user_id": str(user_id)}, sort=[("created_at", -1)])
    if itr_str:
        return {"status": itr_str.get("status", "DRAFT")}
        
    return {"status": "NOT_STARTED", "message": "No filing found"}

if __name__ == "__main__":
    mcp.run()
