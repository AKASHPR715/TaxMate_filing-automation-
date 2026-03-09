from fastmcp import FastMCP
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.services.tax_comparison_service import compare_tax_regimes

mcp = FastMCP("TaxMate-TaxCore")

@mcp.tool()
async def compare_regimes(extracted_data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Calculates and compares old vs new tax regimes mathematically based on the raw extracted data.
    Takes the JSON dictionary from the storage service.
    """
    loop = asyncio.get_event_loop()
    try:
        # Pass the data directly so the DB fetch inside compare_tax_regimes is skipped
        result = await loop.run_in_executor(None, compare_tax_regimes, extracted_data, user_id)
        
        # Serialize the result to remove ObjectIds
        from microservices.storage.mcp_server import serialize_data
        return serialize_data(result)
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    mcp.run()
