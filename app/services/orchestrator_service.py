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
src_dir = current_dir.parent.parent
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

try:
    from app.services.form_extraction_service import extract_all_forms
    from app.services.tax_comparison_service import compare_tax_regimes
    from app.services.tax_advisor_service import get_tax_advice
    from app.services.form_generation_service import generate_filing_forms
except ImportError:
    from form_extraction_service import extract_all_forms
    from tax_comparison_service import compare_tax_regimes
    from tax_advisor_service import get_tax_advice
    from form_generation_service import generate_filing_forms

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
            
            # Step 4: Form Generation & Filing Prep
            if not self._execute_step("Form Generation", self._generate_forms):
                 return self._abort_mission("Form generation failed.")

            # Step 5: Final Report
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
        
        extracted_dir = Path(__file__).resolve().parents[1] / "data" / "extracted"
        
        # First check if we already have extracted JSON files
        existing_json_files = list(extracted_dir.glob("*.json")) if extracted_dir.exists() else []
        
        # Only trigger extraction if no JSON files exist
        if len(existing_json_files) == 0:
            logger.info("No extracted files found, triggering extraction...")
            extract_all_forms()
            existing_json_files = list(extracted_dir.glob("*.json")) if extracted_dir.exists() else []
        else:
            logger.info(f"Found {len(existing_json_files)} already extracted files, skipping re-extraction.")
        
        # Load extracted data from JSON files
        extracted = {}
        forms_found = 0
        for json_file in existing_json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Skip empty files (those with all empty values)
                    if data.get("assessee_details", {}).get("PAN", "") or \
                       data.get("employee_details", {}).get("PAN", "") or \
                       len(data.get("tds_tcs_information", [])) > 0:
                        # Normalize key based on filename prefix
                        key = json_file.stem
                        if key.lower().startswith("form16a"):
                            key = "form16a"
                        elif key.lower().startswith("form16b"):
                            key = "form16b"
                        elif key.lower().startswith("ais"):
                            key = "ais"
                        
                        extracted[key] = data
                        forms_found += 1
                        logger.info(f"  Captured data from: {json_file.name}")
                    else:
                        logger.warning(f"  Skipping empty file: {json_file.name}")
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
        """Delegates to Tax Advisor Agent for personalized next-year tax-saving advice."""
        logger.info("Consulting Tax Advisor Agent for Personalized Recommendations...")
        
        comp_res = self.state["computation_result"]
        
        gross_salary = comp_res.get('gross_salary', 0)
        ch_via = comp_res.get('ch_via', 0)
        optimal_regime = comp_res.get("optimal_regime", "Unknown")
        old_tax = comp_res.get('old_tax', 0)
        new_tax = comp_res.get('new_tax', 0)
        
        # Build rich income context
        income_context = {
            "Gross Salary": f"₹{gross_salary:,.2f}",
            "Current Total Deductions (Chapter VI-A)": f"₹{ch_via:,.2f}",
            "Tax Under Old Regime": f"₹{old_tax:,.2f}",
            "Tax Under New Regime": f"₹{new_tax:,.2f}",
            "Optimal Regime for This Year": optimal_regime
        }
        
        # Extract detailed deductions for context
        deductions_list = []
        deductions_dict = {}
        if self.state["extracted_data"]:
            for form_name, form_data in self.state["extracted_data"].items():
                if "16_Part_B" in form_name and isinstance(form_data, dict):
                    ch_via_data = form_data.get("deductions_chapter_VIA", {})
                    if isinstance(ch_via_data, dict):
                        for k, v in ch_via_data.items():
                            if isinstance(v, (int, float)) and v > 0:
                                deductions_list.append(f"{k}: ₹{v:,.2f}")
                                deductions_dict[k] = v

        # Identify underutilized deductions (common limits)
        max_80c = 150000
        max_80ccd_1b = 50000
        max_80d_self = 25000
        max_80d_parents = 50000  # if senior citizen
        
        current_80c = deductions_dict.get("section_80C", 0) + deductions_dict.get("80C", 0)
        current_80ccd = deductions_dict.get("section_80CCD_1B", 0) + deductions_dict.get("80CCD_1B", 0) + deductions_dict.get("80CCD(1B)", 0)
        current_80d = deductions_dict.get("section_80D", 0) + deductions_dict.get("80D", 0)
        
        underutilized = []
        if current_80c < max_80c:
            gap_80c = max_80c - current_80c
            underutilized.append(f"Section 80C: ₹{gap_80c:,.2f} unused (can invest in PPF, ELSS, LIC)")
        if current_80ccd < max_80ccd_1b:
            gap_80ccd = max_80ccd_1b - current_80ccd
            underutilized.append(f"Section 80CCD(1B): ₹{gap_80ccd:,.2f} unused (NPS additional contribution)")
        if current_80d < max_80d_self:
            gap_80d = max_80d_self - current_80d
            underutilized.append(f"Section 80D: ₹{gap_80d:,.2f} unused (Health insurance premiums)")
        
        # Build a very specific and personalized question for the advisor
        personalized_question = f"""
Based on the taxpayer's current financial situation for FY 2024-25:
- Gross Salary: ₹{gross_salary:,.2f}
- Current Deductions Used: ₹{ch_via:,.2f}
- Optimal Regime: {optimal_regime}
- Current Deductions Breakdown: {', '.join(deductions_list) if deductions_list else 'None provided'}
- Underutilized Deduction Potential: {', '.join(underutilized) if underutilized else 'None identified'}

Provide PERSONALIZED tax-saving recommendations for the NEXT financial year (FY 2025-26). Focus on:
1. Specific sections under Chapter VI-A where the taxpayer can maximize deductions (80C, 80CCD(1B), 80D, 80E, etc.)
2. Investment options that would reduce taxable income (PPF, ELSS, NPS, etc.)
3. Any tax-efficient restructuring of salary (HRA optimization, meal vouchers, etc.)
4. Whether to continue with {optimal_regime} regime or reconsider based on potential new deductions

Be specific and actionable. Provide estimated tax savings where possible.
"""

        # Ask the advisor with personalized context
        advice = get_tax_advice(
            question=personalized_question,
            deductions=deductions_list,
            income_details=income_context
        )
        
        self.state["advisory_result"] = advice
        self.state["advisory_result"] = advice
        logger.info("Personalized Advisory received.")

    def _generate_forms(self):
        """Delegates to Form Generation Agent."""
        logger.info("Delegating to Form Generation Agent...")
        
        extracted = self.state["extracted_data"]
        computed = self.state["computation_result"]
        
        result = generate_filing_forms(extracted, computed)
        
        self.state["filling_result"] = result
        logger.info(f"Form Generation Complete: {result['form_type']} generated at {result['file_path']}")

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

        if self.state.get("filling_result"):
            logger.info(f"▶ ITR FORM PREPARED: {self.state['filling_result']['form_type']}")
            logger.info(f"▶ FILING DATA SAFE AT: {self.state['filling_result']['file_path']}")
        
        if self.state["advisory_result"]:
            logger.info("\n" + "="*60)
            logger.info("📋 PERSONALIZED TAX-SAVING ADVICE FOR NEXT YEAR (FY 2025-26)")
            logger.info("="*60)
            logger.info(self.state["advisory_result"])
            logger.info("="*60)
            
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
