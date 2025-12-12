#!/usr/bin/env python3
"""
TaxMate Orchestrator - The "Boss" Agent
Coordinates the tax filing workflow with strict validation and error handling.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
import logging
from logging.handlers import RotatingFileHandler
from typing_extensions import TypedDict

# Import existing tools
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

try:
    from services.form_extraction import extract_all_forms
    from services.tax_comparison import compare_tax_regimes
    from services.tax_advisor import get_tax_advice
except ImportError:
    from form_extraction import extract_all_forms
    from tax_comparison import compare_tax_regimes
    from tax_advisor import get_tax_advice

# ============================================================
# 1. Logging Configuration
# ============================================================
def setup_orchestrator_logger():
    """Set up authoritative logging for the Boss agent."""
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "orchestrator.log"
    
    logger = logging.getLogger("OrchestratorBoss")
    logger.setLevel(logging.INFO)
    
    # Reset handlers to avoid duplicates during reloads
    if logger.handlers:
        logger.handlers = []

    # File handler
    fh = RotatingFileHandler(
        log_file, 
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=2,
        encoding="utf-8"
    )
    fh.setFormatter(logging.Formatter(
        "%(asctime)s - [BOSS] - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    ))
    logger.addHandler(fh)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter("BOSS: %(message)s"))
    logger.addHandler(ch)
    
    return logger

logger = setup_orchestrator_logger()

# ============================================================
# 2. State & Workflow Definitions
# ============================================================

class WorkflowState(TypedDict):
    """Tracks the state of the tax filing mission."""
    mission_id: str
    status: str  # 'INIT', 'IN_PROGRESS', 'COMPLETED', 'FAILED'
    user_query: str
    extracted_data: Optional[Dict[str, Any]]
    computation_result: Optional[Dict[str, Any]]
    advisory_result: Optional[str]
    errors: List[str]

class TaxOrchestrator:
    """
     The 'Boss' Agent.
     Manages the lifecycle of the tax filing process.
    """
    
    def __init__(self):
        self.state: WorkflowState = {
            "mission_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
            "status": "INIT",
            "user_query": "",
            "extracted_data": {},
            "computation_result": None,
            "advisory_result": None,
            "errors": []
        }

    def start_mission(self, user_query: str = "File my taxes", extracted_data: Optional[Dict[str, Any]] = None):
        """Initiates the workflow. If extracted_data is provided, skips extraction."""
        self.state["user_query"] = user_query
        self.state["status"] = "IN_PROGRESS"
        
        logger.info(f"{'='*60}")
        logger.info(f"MISSION STARTED: ID {self.state['mission_id']}")
        logger.info(f"Objective: {user_query}")
        logger.info(f"{'='*60}")

        try:
            # Step 1: Data Acquisition
            # If data is provided (from user review), use it directly.
            if extracted_data:
                 logger.info("Using provided extracted_data (Human-in-the-Loop). Skipping extraction.")
                 self.state["extracted_data"] = extracted_data
            else:
                if not self._execute_step("Input Collection", self._collect_inputs):
                    return self._abort_mission("Input collection failed. Cannot proceed.")

            # Step 2: Intelligence & Calculation
            if not self._execute_step("Tax Computation", self._compute_taxes):
                return self._abort_mission("Tax computation failed.")

            # Step 3: Strategic Advisory
            # Advisory is optional but highly recommended; we won't abort if it fails, just warn.
            self._execute_step("Strategic Advisory", self._get_advisory, critical=False)
            
            # Step 4: Final Report
            self._finalize_mission()

        except Exception as e:
            logger.exception("CRITICAL SYSTEM FAILURE")
            self.state["errors"].append(str(e))
            self._abort_mission(str(e))

    def run_extraction_only(self, user_query: str = "Extract Data") -> Dict[str, Any]:
        """Runs only the extraction phase and returns data."""
        self.state["user_query"] = user_query
        self.state["status"] = "EXTRACTING"
        
        try:
            if not self._execute_step("Input Collection", self._collect_inputs):
                raise RuntimeError("Extraction failed")
            return self.state["extracted_data"]
        except Exception as e:
            self._abort_mission(str(e))
            raise e

    def run_computation_with_data(self, extracted_data: Dict[str, Any], user_query: str = "Compute Taxes"):
        """Resumes workflow with provided data."""
        self.start_mission(user_query=user_query, extracted_data=extracted_data)
        return self.state

    def _execute_step(self, step_name: str, function, critical: bool = True) -> bool:
        """Executes a workflow step with Boss-level oversight."""
        logger.info(f"▶ STARTING STEP: {step_name}")
        try:
            function()
            logger.info(f"✔ STEP COMPLETED: {step_name}")
            return True
        except Exception as e:
            error_msg = f"Step '{step_name}' encountered an error: {str(e)}"
            logger.error(error_msg)
            self.state["errors"].append(error_msg)
            if critical:
                return False
            return True

    # ------------------------------------------------------------------
    # WORKER DELEGATION METHODS
    # ------------------------------------------------------------------

    def _collect_inputs(self):
        """Delegates to Input Collection Agent."""
        logger.info("Delegating to Input Collection Agent...")
        
        # Trigger extraction
        extract_all_forms()
        
        # Verify extraction results
        extracted = {}
        extracted_dir = Path(__file__).resolve().parents[2] / "data" / "extracted"
        
        forms_found = 0
        if extracted_dir.exists():
            for json_file in extracted_dir.glob("*.json"):
                # Load only recent files matching this mission if possible, 
                # but for now load all to ensure we have data.
                # In a real system, we'd filter by mission_id or timestamp.
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        extracted[json_file.stem] = data
                        forms_found += 1
                        logger.info(f"  Captured data from: {json_file.name}")
                except Exception as e:
                    logger.warning(f"  Failed to read {json_file.name}: {e}")
        
        if forms_found == 0:
            raise FileNotFoundError("No tax documents were extracted. Please ensure PDF files are present in the root or data/uploads directory.")
            
        self.state["extracted_data"] = extracted
        logger.info(f"Input Collection successful. {forms_found} documents secured.")

    def _compute_taxes(self):
        """Delegates to GTI & Tax Liability Agent."""
        logger.info("Delegating to GTI & Tax Liability Agent...")
        
        data = self.state["extracted_data"]
        
        # The agent expects a specific structure or defaults. 
        # We pass the extracted data explicitly.
        result = compare_tax_regimes(extracted_data=data)
        
        if not result:
            raise ValueError("Tax computation returned empty results.")
            
        self.state["computation_result"] = result
        
        # Log key metrics
        logger.info(f"  Old Regime Tax: ₹{result.get('old_tax', 0):,.2f}")
        logger.info(f"  New Regime Tax: ₹{result.get('new_tax', 0):,.2f}")
        logger.info(f"  Optimal Decision: {result.get('optimal_regime', 'UNKNOWN')}")

    def _get_advisory(self):
        """Delegates to Tax Advisor Agent."""
        logger.info("Consulting Tax Advisor Agent...")
        
        comp_res = self.state["computation_result"]
        
        income_context = {
            "Gross Salary": f"₹{comp_res.get('gross_salary', 0):,.2f}",
            "Total Deductions": f"₹{comp_res.get('ch_via', 0):,.2f}",
            "Optimal Regime": comp_res.get("optimal_regime", "Unknown")
        }
        
        # Extract deductions list for context
        deductions_list = []
        if self.state["extracted_data"]:
             for form_name, form_data in self.state["extracted_data"].items():
                if "16_Part_B" in form_name and isinstance(form_data, dict):
                     ch_via = form_data.get("deductions_chapter_VIA", {})
                     if isinstance(ch_via, dict):
                        for k, v in ch_via.items():
                            if isinstance(v, (int, float)) and v > 0:
                                deductions_list.append(f"{k}: ₹{v}")

        # Ask the advisor
        advice = get_tax_advice(
            question=self.state["user_query"],
            deductions=deductions_list,
            income_details=income_context
        )
        
        self.state["advisory_result"] = advice
        logger.info("Advisory received.")

    def _abort_mission(self, reason: str):
        """Handles mission failure."""
        self.state["status"] = "FAILED"
        logger.error(f"{'='*60}")
        logger.error(f"MISSION ABORTED: {reason}")
        logger.error(f"{'='*60}")
        return {
            "status": "FAILED",
            "reason": reason,
            "errors": self.state["errors"]
        }

    def _finalize_mission(self):
        """Compiles the final report."""
        self.state["status"] = "COMPLETED"
        logger.info(f"{'='*60}")
        logger.info("MISSION ACCOMPLISHED. FINAL REPORT:")
        logger.info(f"{'='*60}")
        
        res = self.state["computation_result"]
        
        # Print Detailed Breakdown
        if res.get("detailed_explanation"):
             logger.info(res.get("detailed_explanation"))
             
        logger.info(f"▶ FINAL TAX LIABILITY: ₹{res.get('new_tax' if res.get('optimal_regime') == 'NEW' else 'old_tax', 0):,.2f}")
        logger.info(f"▶ SUGGESTED REGIME: {res.get('optimal_regime')}")
        
        if self.state["advisory_result"]:
            logger.info("\n--- ADVISOR RECOMMENDATIONS ---")
            logger.info(self.state["advisory_result"])
            logger.info("-------------------------------")
            
        logger.info(f"{'='*60}")

# ============================================================
# 3. Entry Point
# ============================================================

def run_orchestrator(question: str = "Optimize my tax"):
    """External API to run the boss."""
    boss = TaxOrchestrator()
    boss.start_mission(question)
    return boss.state

if __name__ == "__main__":
    # CLI usage
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "How can I reduce my tax liability?"
    run_orchestrator(q)
