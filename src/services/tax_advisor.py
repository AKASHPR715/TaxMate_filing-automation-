import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
import logging
from logging.handlers import RotatingFileHandler
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings  # Still used for embeddings (cheap & local)
from langchain.tools import tool 
from langchain_classic.agents import AgentExecutor, create_react_agent  # Note: corrected import
from langchain_classic import hub 
from langchain_openai import ChatOpenAI  # For OpenRouter
from models.hybridsearch import retriever  
from langchain_core.prompts import  ChatPromptTemplate ,MessagesPlaceholder
from tavily import TavilyClient
from models.graphdb import query_tax_graph  # ← import the tool

# ============================================================
# Logging Configuration for tax_advisor.py
# ============================================================
def setup_advisor_logger():
    """Set up logging for tax advisor to separate log file."""
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tax_advisor.log"
    
    logger = logging.getLogger("tax_advisor")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        # File handler with rotation
        fh = RotatingFileHandler(
            log_file, 
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
            encoding="utf-8"
        )
        fh.setLevel(logging.INFO)
        fh.setFormatter(logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        ))
        logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        ch.setFormatter(logging.Formatter(
            "%(levelname)s: %(message)s"
        ))
        logger.addHandler(ch)
    
    return logger

advisor_logger = setup_advisor_logger()

# -------------------------------
# Configuration
# -------------------------------
DB_DIR = "./chroma_db"
MODEL_EMBED = "nomic-embed-text"  # Keep this local — embeddings are fast

# 🔑 Set your OpenRouter API key as environment variable
OPENROUTER_API_KEY = "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"
if not OPENROUTER_API_KEY:
    raise ValueError("Please set the OPENROUTER_API_KEY environment variable.")

# -------------------------------
# 1. Vector Store (Unchanged)
# -------------------------------
embeddings = OllamaEmbeddings(model=MODEL_EMBED)

# if os.path.isdir(DB_DIR) and os.listdir(DB_DIR):
#     print("🔁 Re-using existing Chroma DB …")
#     vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
# else:
#     print("🆕 Creating fresh Chroma DB …")
#     try:
#         with open("sections.json", "r", encoding="utf-8") as f:
#             data = json.load(f)

#         docs = []
#         for sec in data:
#             txt = sec.get("full_text", "")
#             meta = {k: v for k, v in sec.items() if k != "full_text"}
#             clean = {k: v for k, v in meta.items() if isinstance(v, (str, int, float, bool)) or v is None}
#             header = f"Section {sec['section_id']} - {sec['title']}\n"
#             docs.append(Document(page_content=header + txt, metadata=clean))

#         vectorstore = Chroma.from_documents(
#             documents=docs,
#             embedding=embeddings,
#             persist_directory=DB_DIR
#         )
#     except FileNotFoundError:
#         print("sections.json not found. Please create the file to build the initial DB.")
#         exit()


# -------------------------------
# 2b. Web Search Tool (Tavily – Fallback)
# -------------------------------


TAVILY_API_KEY = "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"
if not TAVILY_API_KEY:
    raise ValueError("Please set the TAVILY_API_KEY environment variable.")

tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

@tool
def web_search(query: str) -> str:
    """
    Use this ONLY if `retrieve_context` returns no relevant tax provisions 
    (e.g., for recent budget updates, notifications, or external interpretations).
    """
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
# -------------------------------
# 2. Tool Definition (Unchanged)
# -------------------------------
@tool
def retrieve_context(query: str) -> str:
    """
    Use this to look up the Indian Income Tax Act. 
    Input: a specific question about sections like 80C, 80CCD(1B), deduction limits, or eligibility.
    """
    # docs = vectorstore.similarity_search(query, k=6)
    docs = retriever.invoke(query) 
    return "\n\n".join(doc.page_content for doc in docs)

tools = [retrieve_context, web_search,query_tax_graph]
# -------------------------------
# 3. Agent Setup (Now with OpenRouter!)
# -------------------------------

# ✅ Use OpenRouter via OpenAI-compatible API
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    model="tngtech/deepseek-r1t-chimera:free",  # Best for reasoning + cost
    api_key=OPENROUTER_API_KEY,
    temperature=0,
    max_tokens=1024,
)

# Pull ReAct prompt

prompt = hub.pull("hwchase17/react")


# prompt = ChatPromptTemplate.from_messages([
#     ("system", """You are an expert Indian Income Tax advisor specializing in Chapter VI-A deductions under the old tax regime.

# ## Tools
# You have access to the following tool:
# {tools}

# ## Instructions
# - ALWAYS use the `retrieve_context` tool to fetch up-to-date tax provisions before answering.
# - NEVER rely on internal knowledge—only use retrieved context.
# - Cite section numbers (e.g., "Section 80C"), deduction limits (e.g., "₹1,50,000"), and eligibility conditions.
# - If the context doesn’t answer the query, say: "I cannot determine this from the available tax provisions."

# Available tool names: {tool_names}"""),
#     ("human", "{input}"),
#     MessagesPlaceholder("agent_scratchpad")
# ])
# -------------------------------
# Custom Prompt (RAG-first + Web Fallback)
# -------------------------------
# base_prompt = hub.pull("hwchase17/react-chat")

# # Replace ONLY the system message
# custom_system_message = """You are an expert Indian Income Tax advisor under the old regime.

# ## Tools
# You have access to:
# {tools}

# ## Rules
# 1. ALWAYS call `retrieve_context` FIRST with the user's exact query.
# 2. If the result contains relevant sections (e.g., mentions 80C, 80CCD, limits), use ONLY that to answer.
# 3. If `retrieve_context` returns no relevant tax provisions, THEN call `web_search`.
# 4. NEVER answer from internal knowledge.
# 5. ALWAYS cite sources:
#    - From RAG: "Section 80CCD(1B) allows..."
#    - From web: include full URLs in "Sources:".

# Tool names: {tool_names}"""

# # Rebuild prompt with same structure: [system, human, scratchpad]
# prompt = ChatPromptTemplate.from_messages([
#     ("system", custom_system_message),
#     ("human", "{input}"),
#     base_prompt.messages[2]  # ← This is the ORIGINAL, correct MessagesPlaceholder
# ])
# Create agent
agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# Executor
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
    max_iterations=20,
    early_stopping_method="force"
)

# ============================================================
# 4. Tool Function for Orchestrator Integration
# ============================================================

def get_tax_advice(question: str, deductions: List[str] = None, income_details: Dict[str, Any] = None) -> str:
    """
    Get tax advice as a tool for the orchestrator.
    
    Args:
        question: The user's question about taxes
        deductions: List of claimed deductions (optional)
        income_details: Dictionary with income breakdown (optional)
    
    Returns:
        Advice from the tax advisor agent
    """
    advisor_logger.info(f"Getting tax advice for question: {question}")
    
    # Enhance question with context if available
    enhanced_question = question
    
    if deductions:
        deduction_text = ", ".join(deductions)
        enhanced_question += f"\n\nDeductions claimed: {deduction_text}"
        advisor_logger.info(f"Deductions provided: {deduction_text}")
    
    if income_details:
        income_text = "\n".join([f"  - {k}: {v}" for k, v in income_details.items()])
        enhanced_question += f"\n\nIncome breakdown:\n{income_text}"
        advisor_logger.info(f"Income details provided: {income_text}")
    
    try:
        advisor_logger.info(f"Tax advisor invoked with question: {question}")
        result = agent_executor.invoke({"input": enhanced_question})
        advice = result.get("output", "No advice generated")
        
        # Log the interaction
        try:
            log_dir = Path(__file__).resolve().parents[2] / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "tax_advisor.log"
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"Timestamp: {datetime.now().isoformat()}\n")
                lf.write(f"Question: {question}\n")
                lf.write("Answer:\n")
                lf.write(advice + "\n")
                lf.write("-" * 80 + "\n")
            advisor_logger.info("Advice generated and logged successfully")
        except Exception as e:
            advisor_logger.warning(f"Could not write to log file: {e}")
        
        return advice
    except Exception as e:
        advisor_logger.error(f"Tax advisor error: {e}")
        return f"Error generating advice: {str(e)}"

# ============================================================
# 5. Standalone Run (for testing)
# ============================================================
if __name__ == "__main__":
    question = "Can I claim both 80C and 80CCD(1B) together?"

    print(f"\n❓ Question: {question}\n")
    
    advice = get_tax_advice(question)
    
    print(f"\n✅ Final Answer:\n{advice}")