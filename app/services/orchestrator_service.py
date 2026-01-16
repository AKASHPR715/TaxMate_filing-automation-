#!/usr/bin/env python3
"""
TaxMate Orchestrator - LangGraph Edition
Coordinates the tax filing workflow using a state machine.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, TypedDict, Annotated
import logging
from logging.handlers import RotatingFileHandler

# LangGraph Imports
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage

# Import Services
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent.parent
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

try:
    from app.services.form_extraction_service import extract_all_forms, get_or_create_default_user
    from app.services.tax_comparison_service import compare_tax_regimes
    from app.services.tax_advisor_service import get_tax_advice
    from app.services.form_generation_service import generate_filing_forms
    from app.db.connection import get_sync_db
except ImportError:
    # Fallback for direct execution
    from form_extraction_service import extract_all_forms, get_or_create_default_user
    from tax_comparison_service import compare_tax_regimes
    from tax_advisor_service import get_tax_advice
    from form_generation_service import generate_filing_forms
    from app.db.connection import get_sync_db

# ============================================================
# 1. Logging Configuration
# ============================================================
def setup_orchestrator_logger():
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "orchestrator_graph.log"
    
    logger = logging.getLogger("OrchestratorGraph")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        fh = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=2)
        fh.setFormatter(logging.Formatter("%(asctime)s - [GRAPH] - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
        
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("GRAPH: %(message)s"))
        logger.addHandler(ch)
    return logger

logger = setup_orchestrator_logger()

# ============================================================
# 2. State Definition
# ============================================================

class AgentState(TypedDict):
    """The shared state of the tax filing workflow."""
    mission_id: str
    user_id: str
    user_query: str
    extracted_data: Optional[Dict[str, Any]]
    computation_result: Optional[Dict[str, Any]]
    advisory_result: Optional[str]
    filling_result: Optional[Dict[str, Any]]
    errors: List[str]
    status: str

# ============================================================
# 3. Nodes
# ============================================================

def input_collection_node(state: AgentState) -> AgentState:
    """Checks DB for data, triggers extraction if missing."""
    logger.info("▶ NODE: Input Collection")
    try:
        from app.services.db_helpers import load_user_tax_data
        
        db = get_sync_db()
        
        # Resolve User Logic
        if not state.get("user_id"):
            user_id = get_or_create_default_user(db)
            state["user_id"] = str(user_id)
        else:
            user_id = state["user_id"]
        
        # 1. Try to fetch existing data from DB
        if not state.get("extracted_data"):
            logger.info(f"Checking DB for existing tax docs for User: {user_id}")
            extracted_data = load_user_tax_data(db, user_id)
            
            if extracted_data:
                logger.info(f"Loaded {len(extracted_data)} documents from DB. Skipping re-extraction.")
                state["extracted_data"] = extracted_data
        
        # 2. Trigger extraction only if NO data found
        if not state.get("extracted_data"):
            logger.info("No data in DB. Triggering form extraction service...")
            try:
                extract_all_forms() 
                state["status"] = "EXTRACTION_TRIGGERED"
            except Exception as e:
                logger.warning(f"Extraction returned: {e}")
        else:
             state["status"] = "INPUT_COLLECTED"
             
        return state

    except Exception as e:
        logger.error(f"Input Collection Failed: {e}")
        state["errors"].append(str(e))
        state["status"] = "FAILED"
        return state

def compute_tax_node(state: AgentState) -> AgentState:
    """Calculates tax liability."""
    logger.info("▶ NODE: Tax Computation")
    if state["status"] == "FAILED": 
        return state

    try:
        user_id = state["user_id"]
        # Call service with user_id to fetch from DB
        result = compare_tax_regimes(
            extracted_data=state.get("extracted_data"), 
            user_id=user_id
        )
        state["computation_result"] = result
        state["status"] = "COMPUTED"
        
        optimal = result.get('optimal_regime', 'UNKNOWN')
        logger.info(f"  Optimal Regime: {optimal}")
        return state

    except Exception as e:
        logger.error(f"Computation Failed: {e}")
        state["errors"].append(str(e))
        state["status"] = "FAILED"
        return state

def advisory_node(state: AgentState) -> AgentState:
    """Generates tax saving advice."""
    logger.info("▶ NODE: Strategic Advisory")
    if state["status"] == "FAILED": 
        return state

    try:
        res = state["computation_result"]
        # Construct summary context for advisor
        income_context = {
            "Gross Salary": f"₹{res.get('gross_salary', 0):,.2f}",
            "Taxable Income": f"₹{res.get('new_taxable', 0):,.2f}",
            "Optimal Regime": res.get("optimal_regime", "Unknown")
        }
        
        # Simple prompt construction
        question = "What can I do to save more tax next year?"
        
        advice = get_tax_advice(
            question=question,
            deductions=[],
            income_details=income_context
        )
        state["advisory_result"] = advice
        logger.info("  Advisory generated.")
        return state

    except Exception as e:
        # Advisory failure is non-critical
        logger.warning(f"Advisory Failed: {e}")
        return state

def form_generation_node(state: AgentState) -> AgentState:
    """Prepares the ITR form."""
    logger.info("▶ NODE: Form Generation")
    if state["status"] == "FAILED": 
        return state

    try:
        user_id = state["user_id"]
        
        # Get extracted data
        extracted_data = state.get("extracted_data")
        
        if not extracted_data:
            logger.info("No extracted_data in state, will rely on service to fetch from DB")
        
        # Get computation result
        computation_result = state.get("computation_result")
        
        if not computation_result:
            logger.warning("No computation_result available for form generation")
            state["errors"].append("Missing tax computation data for form generation")
            state["status"] = "FAILED"
            return state
        
        # Call the actual form generation service
        logger.info("Calling generate_filing_forms service...")
        result = generate_filing_forms(
            extracted_data=extracted_data,
            computation_result=computation_result,
            user_id=user_id
        )
        
        if result and "file_path" in result:
            state["filling_result"] = result
            state["status"] = "COMPLETED"
            logger.info(f"✅ Form generated successfully: {result.get('form_type')} at {result.get('file_path')}")
            
            # ------------------------------------------------------------------
            # PERSIST TO DATABASE
            # ------------------------------------------------------------------
            try:
                from app.db.models import ITR, ComputedData
                from bson import ObjectId
                
                db = get_sync_db()
                
                # Load the generated JSON content
                with open(result["file_path"], "r") as f:
                    submission_data = json.load(f)
                    
                form_type = result.get("form_type", "ITR-1")
                
                # Create ComputedData object
                comp_data = ComputedData(
                    total_income=float(computation_result.get("new_taxable", 0)),
                    total_deductions=float(computation_result.get("ch_via_validated", 0)),
                    total_tax_payable=float(computation_result.get("new_tax", 0)),
                    regime=computation_result.get("optimal_regime", "NEW")
                )
                
                # Check for existing draft/review ITR
                existing_itr = db.filings.find_one(
                    {"user_id": ObjectId(user_id), "status": {"$in": ["DRAFT", "REVIEW"]}}
                )
                
                update_data = {
                    "user_id": ObjectId(user_id),
                    "assessment_year": "2025-26",
                    "status": "REVIEW", # Set to REVIEW as it's generated by Agent
                    "form_type": form_type,
                    "computed_data": comp_data.dict(),
                    "itr_submission": submission_data,
                    "updated_at": datetime.utcnow()
                }
                
                if existing_itr:
                    db.filings.update_one(
                        {"_id": existing_itr["_id"]},
                        {"$set": update_data}
                    )
                    logger.info(f"Updated existing filing record in filings collection: {existing_itr['_id']}")
                else:
                    update_data["created_at"] = datetime.utcnow()
                    # Link source docs if available in extracted_data (logic omitted for brevity, can populate if IDs known)
                    res = db.filings.insert_one(update_data)
                    logger.info(f"Created new filing record in filings collection: {res.inserted_id}")
                    
            except Exception as db_err:
                logger.error(f"Failed to persist ITR to DB: {db_err}")
                # Don't fail the whole workflow, just log error
                state["errors"].append(f"DB Persistence Failed: {db_err}")

        else:
            logger.error("Form generation returned invalid result")
            state["errors"].append("Form generation failed to produce output")
            state["status"] = "FAILED"
            
        return state

    except Exception as e:
        logger.error(f"Form Generation Failed: {e}")
        state["errors"].append(str(e))
        state["status"] = "FAILED"
        return state

# ============================================================
# 4. Graph Construction
# ============================================================

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("input_collection", input_collection_node)
workflow.add_node("tax_computation", compute_tax_node)
workflow.add_node("strategic_advisory", advisory_node)
workflow.add_node("form_generation", form_generation_node)

# Add Edges (Linear Flow)
workflow.add_edge("input_collection", "tax_computation")
workflow.add_edge("tax_computation", "strategic_advisory")
workflow.add_edge("strategic_advisory", "form_generation")
workflow.add_edge("form_generation", END)

# Set Entry Point
workflow.set_entry_point("input_collection")

# Compile
app = workflow.compile()

# ============================================================
# 5. Execution Wrapper
# ============================================================

def run_orchestrator(question: str = "Optimize my tax", user_id: str = None):
    """External API to run the graph."""
    initial_state = AgentState(
        mission_id=datetime.now().strftime("%Y%m%d-%H%M%S"),
        user_id=user_id if user_id else "", 
        user_query=question,
        extracted_data=None,
        computation_result=None,
        advisory_result=None,
        filling_result=None,
        errors=[],
        status="INIT"
    )
    
    logger.info(f"{'='*60}")
    logger.info(f"STARTING LANGGRAPH ORCHESTRATOR")
    logger.info(f"{'='*60}")
    
    final_state = app.invoke(initial_state)
    
    if final_state["status"] == "COMPLETED":
        logger.info("✅ MISSION ACCOMPLISHED")
        logger.info(f"Tax Liability: ₹{final_state['computation_result'].get('new_tax', 0):,.2f}")
    else:
        logger.error(f"❌ MISSION FAILED: {final_state['errors']}")
        
    return final_state

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How can I reduce my tax liability?"
    run_orchestrator(q)
