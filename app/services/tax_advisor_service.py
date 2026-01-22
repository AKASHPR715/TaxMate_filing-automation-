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
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.output_parsers import BaseOutputParser
import re
from typing import Union
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

# ============================================================
# Output Parser
# ============================================================
class RobustReActOutputParser(BaseOutputParser):
    """
    Parses ReAct-style LLM calls.
    Robustly handles 'Final Answer:' detection even with extra noise.
    """
    
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        # 1. Check for Final Answer
        if "Final Answer:" in text:
            # Check if "Final Answer:" appears multiple times, take the last one or split logic
            # Just take everything after the last "Final Answer:"
            output = text.split("Final Answer:")[-1].strip()
            return AgentFinish(
                return_values={"output": output},
                log=text,
            )
            
        # 2. Check for Action using strict Regex
        # Standard ReAct: 
        # Action: tool_name
        # Action Input: input_str
        
        regex = r"Action: (.*?)\nAction Input: (.*)"
        match = re.search(regex, text, re.DOTALL)
        
        if match:
            action = match.group(1).strip()
            action_input = match.group(2)
            return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=text)
            
        # 3. Fallback: If we can't find Action/Final Answer, we assume it's unfinished thought or loop.
        # But if the Agent output "Agent stopped..." or something similar, handle it.
        
        # If no valid action parsed, return as Final Answer to prevent infinite loop.
        # This is a robust fallback for "I don't know what to do" thoughts.
        return AgentFinish(
             return_values={"output": text},
             log=text
        )



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
    # Add stop tokens to prevent infinite generation after Final Answer
    # The agent outputs "Final Answer:" so we need to stop after that
    llm_with_stop = llm.bind(stop=["\nObservation:", "Observation:", "\n\nQuestion:", "Question:"])
    
    agent = create_react_agent(llm=llm_with_stop, tools=tools, prompt=prompt, output_parser=RobustReActOutputParser())
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True,
        max_iterations=15, # Reduced from 20 to fail faster
        early_stopping_method="force",
        return_intermediate_steps=False  # Don't return intermediate steps to reduce output
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

def strip_markdown(text: str) -> str:
    """Remove markdown formatting for plain text display."""
    import re
    
    # Remove bold markdown first (**text**)
    text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)
    
    # Remove italic markdown (*text* but not list bullets)
    # Only match if not at start of line (to preserve * bullet points)
    text = re.sub(r'(?<!\n)\*(.+?)\*', r'\1', text)
    
    # Remove headers (## Header)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # Remove inline code (`code`)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove emphasis with underscores (__text__ or _text_)
    text = re.sub(r'__(.+?)__', r'\1', text)
    text = re.sub(r'_(.+?)_', r'\1', text)
    
    return text

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
        output = result.get("output", "No advice generated.")
        
        # Check for iteration limit message ("Agent stopped...") or if output suggests failure
        if "Agent stopped" in output and "iteration limit" in output:
             raise Exception("Agent stopped due to iteration limit")
        
        # Clean up the output to extract only the Final Answer content
        # The ReAct agent outputs in format: "Thought: ... Action: ... Observation: ... Final Answer: <answer>"
        # Sometimes it duplicates "Final Answer:" so we need to handle that
        if "Final Answer:" in output:
            # Split on "Final Answer:" and take the last occurrence (in case of duplicates)
            parts = output.split("Final Answer:")
            # Take the last non-empty part
            final_answer = parts[-1].strip() if parts else output
            
            # Remove any remaining agent artifacts
            for artifact in ["Thought:", "Action:", "Observation:", "Action Input:", "Final Answer:"]:
                if artifact in final_answer:
                    final_answer = final_answer.split(artifact)[0].strip()
            
            output = final_answer
        
        # Strip markdown formatting for clean display (remove **bold**, *italic*, etc.)
        output = strip_markdown(output)
        
        # Remove any remaining "Final Answer:" prefix if it somehow remained
        if output.startswith("Final Answer:"):
            output = output.replace("Final Answer:", "", 1).strip()
        
        return output

    except Exception as e:
        advisor_logger.warning(f"Advisor Agent failed (or limit reached): {e}. Falling back to Web Search.")
        
        # Fallback to pure web search
        fallback_res = web_search.invoke(question)
        fallback_res = strip_markdown(fallback_res)  # Also strip markdown from fallback
        return f"Note: The complex reasoning agent hit a limit, so here is a direct web search result:\n\n{fallback_res}"

if __name__ == "__main__":
    print(get_tax_advice("How can I save tax?"))