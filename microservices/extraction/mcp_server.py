from fastmcp import FastMCP
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.services.form_extraction_service import extract_all_forms
mcp = FastMCP("TaxMate-Extraction")

@mcp.tool()
async def extract_data_from_documents(user_id: str) -> Dict[str, Any]:
    """
    Processes all PDF documents for the given user via OCR and LlamaExtract.
    Since this can take a long time, it returns a status after triggering.
    """
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, extract_all_forms)
    return {"status": "success", "message": f"Extraction complete for user {user_id}. Data saved locally."}

if __name__ == "__main__":
    mcp.run()
