#!/usr/bin/env python3
"""
LangGraph Tax Filing Orchestrator
Coordinates existing tax tools: form_extraction.py, tax_comparison.py, tax_advisor.py
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict
import logging
from logging.handlers import RotatingFileHandler

# Import existing tools
from form_extraction import extract_all_forms
from tax_comparison import compare_tax_regimes
from tax_advisor import get_tax_advice

# ============================================================
# Logging Configuration for orchestrator.py
# ============================================================
def setup_orchestrator_logger():
    """Set up logging for orchestrator to separate log file."""
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "orchestrator.log"
    
    logger = logging.getLogger("orchestrator")
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

orchestrator_logger = setup_orchestrator_logger()

# ============================================================
# State Management
# ============================================================

class OrchestratorState(TypedDict):
    """State managed throughout the orchestrator workflow."""
    user_question: str
    extracted_data: Optional[Dict[str, Any]]
    tax_comparison_result: Optional[Dict[str, Any]]
    tax_advice: Optional[str]
    tax_explanation: Optional[str]
    deductions_found: List[str]
    optimal_regime: Optional[str]
    current_step: str

# ============================================================
# Node Functions (Orchestrator Workflow)
# ============================================================

def analyze_intent(state: OrchestratorState) -> OrchestratorState:
    """
    Analyze user question to determine which tools to invoke.
    """
    state["current_step"] = "analyze_intent"
    orchestrator_logger.info(f"Analyzing intent: {state['user_question']}")
    
    question = state["user_question"].lower()
    print(f"\n🔍 Analyzing intent: {state['user_question']}")
    
    # Determine what tools to use based on keywords
    intents = []
    if any(word in question for word in ["extract", "form", "16", "26", "ais", "data"]):
        intents.append("extract_forms")
    if any(word in question for word in ["compare", "regime", "old", "new", "deduction", "tax"]):
        intents.append("compare_regimes")
    if any(word in question for word in ["advice", "suggest", "recommend", "how", "can i", "claim"]):
        intents.append("get_advice")
    
    # Default to all if no specific intent
    if not intents:
        intents = ["extract_forms", "compare_regimes", "get_advice"]
    
    orchestrator_logger.info(f"Identified intents: {', '.join(intents)}")
    print(f"✓ Identified intents: {', '.join(intents)}")
    return state


def extract_forms(state: OrchestratorState) -> OrchestratorState:
    """
    Call form_extraction.py to extract forms.
    """
    state["current_step"] = "extract_forms"
    orchestrator_logger.info("Starting form extraction...")
    print("\n📄 Extracting forms using form_extraction.py...")
    try:
        # Call existing form_extraction function
        extract_all_forms()
        
        # Try to load extracted JSON files from data/extracted
        extracted = {}
        extracted_dir = Path(__file__).resolve().parents[2] / "data" / "extracted"
        if extracted_dir.exists():
            for json_file in extracted_dir.glob("*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        form_name = json_file.stem
                        extracted[form_name] = json.load(f)
                        print(f"✓ Loaded {form_name}")
                except Exception as e:
                    print(f"⚠ Could not load {json_file.name}: {e}")
        
        state["extracted_data"] = extracted if extracted else None
        
        # Extract deductions from Form_16_Part_B if available
        deductions = []
        for form_name, form_data in extracted.items():
            if "16_Part_B" in form_name and isinstance(form_data, dict):
                if "deductions_chapter_VIA" in form_data:
                    ch_via = form_data["deductions_chapter_VIA"]
                    if isinstance(ch_via, dict):
                        for key, value in ch_via.items():
                            if isinstance(value, (int, float)) and value > 0:
                                deductions.append(f"{key}: ₹{value:,.0f}")
        
        state["deductions_found"] = deductions
        print(f"✓ Forms extraction complete. Found {len(deductions)} deductions")
        
    except Exception as e:
        print(f"⚠ Form extraction failed: {e}")
    
    return state


def compare_regimes(state: OrchestratorState) -> OrchestratorState:
    """
    Call tax_comparison.py tool to compare old vs new regimes.
    """
    state["current_step"] = "compare_regimes"
    orchestrator_logger.info("Starting tax regime comparison...")
    
    print("\n📊 Comparing tax regimes using tax_comparison.py...")
    try:
        # Call compare_tax_regimes tool from tax_comparison.py
        result = compare_tax_regimes(extracted_data=state["extracted_data"])
        orchestrator_logger.info(f"Tax comparison complete. Optimal regime: {result.get('optimal_regime')}")
        
        # Print the detailed explanation from the tool
        print(result["detailed_explanation"])
        
        # Store results in state
        state["tax_explanation"] = result["detailed_explanation"]
        state["optimal_regime"] = result["optimal_regime"]
        state["tax_comparison_result"] = result
        
        print("✓ Tax comparison complete")
        
    except Exception as e:
        print(f"⚠ Tax comparison failed: {e}")
        import traceback
        traceback.print_exc()
    
    return state


def get_advice(state: OrchestratorState) -> OrchestratorState:
    """
    Call tax_advisor.py to get tax advice.
    """
    state["current_step"] = "get_advice"
    orchestrator_logger.info("Starting tax advisor query...")
    
    print("\n🤖 Getting tax advice using tax_advisor.py...")
    try:
        # Build a comprehensive question based on context
        deductions_str = ", ".join(state["deductions_found"]) if state["deductions_found"] else "None identified"
        
        # Get income details if available
        income_details = {}
        if state["tax_comparison_result"]:
            income_details = {
                "Gross Salary": f"₹{state['tax_comparison_result'].get('gross_salary', 0):,.0f}",
                "Other Income": f"₹{state['tax_comparison_result'].get('other_income', 0):,.0f}",
                "Optimal Regime": state["tax_comparison_result"].get("optimal_regime", "Unknown"),
            }
        
        # Main question: How to pay less tax in the coming year
        primary_question = "How can I pay less tax in the coming year?"
        
        # Enhance with deductions and income context
        if state["user_question"] and state["user_question"].lower() != "default":
            primary_question = state["user_question"]
        
        # Call tax advisor as a tool (not as an agent executor)
        advice = get_tax_advice(
            question=primary_question,
            deductions=state["deductions_found"] if state["deductions_found"] else None,
            income_details=income_details if income_details else None
        )
        
        state["tax_advice"] = advice
        orchestrator_logger.info("Tax advice generated successfully")
        print("✓ Tax advice generated")
        
    except Exception as e:
        orchestrator_logger.error(f"Tax advice generation failed: {e}")
        print(f"⚠ Tax advice generation failed: {e}")
        state["tax_advice"] = None
    
    return state


def summarize_findings(state: OrchestratorState) -> OrchestratorState:
    """
    Summarize all findings and log results.
    """
    state["current_step"] = "summarize"
    orchestrator_logger.info("Summarizing orchestrator findings...")
    
    summary = []
    summary.append("\n" + "=" * 80)
    summary.append("TAX FILING ORCHESTRATOR SUMMARY")
    summary.append("=" * 80)
    summary.append("")
    
    if state["extracted_data"]:
        summary.append("📄 EXTRACTED DATA:")
        summary.append(f"  Forms found: {len(state['extracted_data'])}")
        summary.append("")
    
    if state["deductions_found"]:
        summary.append("💰 DEDUCTIONS IDENTIFIED:")
        for deduction in state["deductions_found"]:
            summary.append(f"  • {deduction}")
        summary.append("")
    
    # Include detailed tax explanation
    if state["tax_explanation"]:
        summary.append(state["tax_explanation"])
        summary.append("")
    
    if state["tax_advice"]:
        summary.append("🤖 AI TAX ADVISOR RECOMMENDATIONS:")
        summary.append("-" * 70)
        summary.append(state["tax_advice"])
        summary.append("")
    
    summary.append("=" * 80)
    
    # Print summary
    output = "\n".join(summary)
    print(output)
    
    # Log to file
    try:
        log_dir = Path(__file__).resolve().parents[2] / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / "orchestrator.log"
        with open(log_file, "a", encoding="utf-8") as lf:
            lf.write(f"\n{'='*80}\n")
            lf.write(f"Timestamp: {datetime.now().isoformat()}\n")
            lf.write(f"Question: {state['user_question']}\n")
            lf.write(output + "\n")
    except Exception as e:
        print(f"⚠ Could not write log: {e}")
    
    return state

# ============================================================
# Orchestrator Main Function
# ============================================================

def run_orchestrator(user_question: str) -> Dict[str, Any]:
    """
    Run the orchestrator with a user question.
    Coordinates form_extraction, tax_comparison, and tax_advisor tools.
    """
    orchestrator_logger.info(f"{'='*80}")
    orchestrator_logger.info(f"TAX FILING ORCHESTRATOR STARTED - Question: {user_question}")
    orchestrator_logger.info(f"{'='*80}")
    
    print(f"\n{'='*80}")
    print("🎯 TAX FILING ORCHESTRATOR STARTED")
    print(f"{'='*80}")
    print(f"Question: {user_question}")
    
    # Initialize state
    state: OrchestratorState = {
        "user_question": user_question,
        "extracted_data": None,
        "tax_comparison_result": None,
        "tax_advice": None,
        "tax_explanation": None,
        "deductions_found": [],
        "optimal_regime": None,
        "current_step": "init",
    }
    
    # Run orchestration workflow
    state = analyze_intent(state)
    state = extract_forms(state)
    state = compare_regimes(state)
    state = get_advice(state)
    state = summarize_findings(state)
    
    orchestrator_logger.info(f"TAX FILING ORCHESTRATOR COMPLETED - Optimal regime: {state['optimal_regime']}")
    print(f"\n{'='*80}")
    print("✅ ORCHESTRATOR COMPLETED")
    print(f"{'='*80}\n")
    
    # Return results
    return {
        "question": user_question,
        "extracted_data": state["extracted_data"],
        "deductions": state["deductions_found"],
        "tax_explanation": state["tax_explanation"],
        "optimal_regime": state["optimal_regime"],
        "tax_comparison": state["tax_comparison_result"],
        "tax_advice": state["tax_advice"],
    }

# ============================================================
# CLI Entry Point
# ============================================================

if __name__ == "__main__":
    import sys
    
    # Get question from command line or use default
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "How can I pay less tax in the coming year?"
    
    # Run orchestrator
    result = run_orchestrator(question)
    
    # Optionally print JSON result
    # print("\n📋 Full Result:")
    # print(json.dumps(result, indent=2, default=str))
