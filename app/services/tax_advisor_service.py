import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

from langchain_classic.agents import AgentExecutor, create_react_agent  # Note: corrected import
from langchain_classic import hub 
from langchain_openai import ChatOpenAI
from langchain.tools import tool
# Load env
load_dotenv()

# Add src to path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent.parent
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

# Ensure these imports exist in your project structure
from app.models.hybridsearch import retriever
try:
    from app.models.graphdb import query_tax_graph
except ImportError:
    # Fallback if graphdb is missing or has issues
    @tool
    def query_tax_graph(query: str) -> str:
        """Fallback tool if graphdb is not available."""
        return "Graph database query is currently unavailable."

from tavily import TavilyClient

# ============================================================
# Logging
# ============================================================
def setup_advisor_logger():
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tax_advisor.log"
    
    logger = logging.getLogger("tax_advisor")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        fh = RotatingFileHandler(
            log_file, 
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
            encoding="utf-8"
        )
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
        
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("ADVISOR: %(message)s"))
        logger.addHandler(ch)
    
    return logger

advisor_logger = setup_advisor_logger()

# ============================================================
# Configuration & Tools
# ============================================================
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not OPENROUTER_API_KEY:
    advisor_logger.warning("OPENROUTER_API_KEY not found in environment variables.")

if not TAVILY_API_KEY:
    advisor_logger.warning("TAVILY_API_KEY not found in environment variables.")
    tavily_client = None
else:
    tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def retrieve_context(query: str) -> str:
    """
    Look up the Indian Income Tax Act (Chapter VI-A).
    Input: a specific question about sections like 80C, 80CCD(1B), deduction limits, or eligibility.
    """
    advisor_logger.info(f"Retrieving context for: {query}")
    try:
        docs = retriever.invoke(query)
        if hasattr(docs, 'page_content'):
             return docs.page_content
        if isinstance(docs, list):
             return "\n\n".join(doc.page_content for doc in docs)
        return str(docs)
    except Exception as e:
        return f"Context retrieval failed: {e}"

@tool
def web_search(query: str) -> str:
    """
    Use this ONLY if `retrieve_context` returns no relevant tax provisions.
    Searches the web for recent budget updates or notifications.
    """
    if not tavily_client:
        return "Web search is unavailable (Missing API Key)."
        
    try:
        response = tavily_client.search(
            query=query,
            search_depth="advanced",
            include_answer=True,
            max_results=3
        )
        answer = response.get("answer", "No clear answer found.")
        sources = "\n".join(f"- {res['url']}" for res in response.get("results", [])[:3])
        return f"{answer}\n\nSources:\n{sources}"
    except Exception as e:
        return f"Web search failed: {str(e)}"

# Setup Agent
tools = [retrieve_context, web_search, query_tax_graph]

# Only initialize LLM if key is present to avoid crash on import
llm = None
if OPENROUTER_API_KEY:
    llm = ChatOpenAI(
        base_url="https://openrouter.ai/api/v1",
        model="tngtech/deepseek-r1t-chimera:free",
        api_key=OPENROUTER_API_KEY.strip(),
        temperature=0,
        max_tokens=4096,  # Increased from 1024 to prevent truncation
    )

# Pull Prompt
prompt = hub.pull("hwchase17/react")

# Create Agent
agent = None
agent_executor = None

if llm:
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=20
    )

# ============================================================
# Main Tool Function
# ============================================================

# ... imports
from app.db.connection import get_sync_db
from bson import ObjectId

# ... (existing code)

# ============================================================
# Main Tool Function
# ============================================================

def get_tax_advice(question: str, deductions: List[str] = None, income_details: Dict[str, Any] = None, user_id: str = None) -> str:
    """Gets AI tax advice."""
    advisor_logger.info(f"Generating advice for: {question}")
    
    if not agent_executor:
         error_msg = "Tax Advisor Agent is not initialized (likely missing API key)."
         advisor_logger.error(error_msg)
         return error_msg
    
    # DB Fetch Context if missing
    if not income_details and user_id:
        try:
            db = get_sync_db()
            # Helper to find by string or ObjectId
            def sensible_find(collection, uid):
                q = {"user_id": str(uid)}
                doc = collection.find_one(q, sort=[("created_at", -1)])
                if not doc:
                    try:
                        doc = collection.find_one({"user_id": ObjectId(uid)}, sort=[("created_at", -1)])
                    except: pass
                return doc

            f16b = sensible_find(db.form16_part_bs, user_id)
            if f16b:
                income_details = {
                    "Gross Salary": f"₹{f16b.get('gross_total_income', 0):,.2f}",
                    "Taxable Income": f"₹{f16b.get('taxable_income', 0):,.2f}"
                }
                advisor_logger.info(f"Loaded context from DB for user {user_id}")
        except Exception as e:
            advisor_logger.warning(f"Failed to fetch DB context for advice: {e}")

    context_str = ""
    if income_details:
        context_str += "\nIncome Context:\n" + "\n".join([f"- {k}: {v}" for k, v in income_details.items()])
    if deductions:
        context_str += "\n\nCurrent Deductions:\n" + ", ".join(deductions)
        
    full_prompt = f"{question}\n{context_str}"
    
    try:
        result = agent_executor.invoke({"input": full_prompt})
        return result.get("output", "No advice generated.")
    except Exception as e:
        advisor_logger.error(f"Advisor Loop Failed: {e}")
        return f"Sorry, I could not generate advice due to an error: {e}"

if __name__ == "__main__":
    print(get_tax_advice("How can I save tax?"))