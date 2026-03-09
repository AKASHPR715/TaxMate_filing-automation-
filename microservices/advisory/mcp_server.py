from fastmcp import FastMCP
import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.append(str(project_root))

from app.services.tax_advisor_service import get_tax_advice

mcp = FastMCP("TaxMate-Advisory")

@mcp.tool()
async def generate_tax_advice(query: str, income_details: Dict[str, Any], deductions: List[str]) -> str:
    """
    Generates strategic personal tax-saving advice using Reasoning LLMs and Indian Tax Act knowledge graphs/RAG.
    """
    loop = asyncio.get_event_loop()
    try:
        result = await loop.run_in_executor(None, get_tax_advice, query, deductions, income_details)
        return result
    except Exception as e:
        return f"Error generating advice: {str(e)}"

if __name__ == "__main__":
    mcp.run()
