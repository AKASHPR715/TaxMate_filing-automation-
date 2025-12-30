import sys
import os
import csv
import json
import logging
import argparse
from datetime import datetime
from tqdm import tqdm

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

from experiments.data_generation.generator import TaxProfileGenerator
from experiments.execution.adapter import adapt_profile_to_orchestrator
from experiments.execution.llm_client import ResearchLLM
from experiments.execution.prompts import get_zero_shot_prompt, get_cot_prompt

# MOCK DEPENDENCIES to avoid ImportError on TaxOrchestrator load
# We do not use extraction in this experiment, so we can mock it out.
from unittest.mock import MagicMock
sys.modules["llama_cloud_services"] = MagicMock()
sys.modules["services.form_extraction"] = MagicMock()
sys.modules["src.services.form_extraction"] = MagicMock()

# Mock Tax Advisor and its dependencies
sys.modules["langchain_classic"] = MagicMock()
sys.modules["langchain_classic.agents"] = MagicMock()
sys.modules["services.tax_advisor"] = MagicMock()
sys.modules["src.services.tax_advisor"] = MagicMock()

# Mock Form Generation
sys.modules["services.form_generation"] = MagicMock()
sys.modules["src.services.form_generation"] = MagicMock()

# Now import Orchestrator
try:
    from src.services.orchestrator import TaxOrchestrator
except ImportError:
    # If src is not in path correctly
    sys.path.append(os.path.abspath(os.path.join(current_dir, "../../src")))
    from services.orchestrator import TaxOrchestrator

# Setup Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - RUNNER - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("experiments/execution_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("experiments.runner")

def extract_number_from_text(text: str) -> float:
    """
    Heuristic to extract the last number from LLM output.
    It looks for "FINAL TAX: <number>" or just grabs the last number found.
    """
    import re
    # Clean text
    text = text.replace(",", "").replace("₹", "")
    
    # Try finding explicit marker first
    match = re.search(r"FINAL TAX[:\s]+(\d+(\.\d+)?)", text, re.IGNORECASE)
    if match:
        return float(match.group(1))
        
    # Fallback: Find all numbers and take the last one
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", text)
    if numbers:
        try:
            return float(numbers[-1])
        except:
            return -1.0
            
    return -1.0

def run_benchmark(count: int = 10, dry_run: bool = False, model: str = None):
    # 1. Generate Data
    logger.info(f"Generating {count} synthetic tax profiles...")
    generator = TaxProfileGenerator()
    profiles = generator.generate_batch(count)
    
    # 2. Setup LLM (Baseline)
    # If dry_run, mock the LLM to save costs
    llm = None
    if not dry_run:
        llm = ResearchLLM(model_name=model or "gpt-4o-mini")
    
    results = []
    
    logger.info("Starting Benchmark Loop...")
    for i, profile in enumerate(tqdm(profiles, desc="Benchmarking")):
        input_data = adapt_profile_to_orchestrator(profile)
        target_regime = profile.target_regime
        ground_truth = profile.ground_truth_tax
        
        # --- A. Neuro-Symbolic (Orchestrator) ---
        neuro_tax = -1.0
        try:
            orchestrator = TaxOrchestrator()
            # We use 'run_computation_with_data' which calls compare_tax_regimes
            orchestrator.run_computation_with_data(input_data)
            
            res = orchestrator.state["computation_result"]
            if target_regime == "Old":
                neuro_tax = res.get("old_tax", -1.0)
            else:
                neuro_tax = res.get("new_tax", -1.0)
                
        except Exception as e:
            logger.error(f"NeuroSym Error on {profile.profile_id}: {e}")
            neuro_tax = -999.0 # Error Code
            
        # --- B. LLM Baselines ---
        zs_tax = -1.0
        cot_tax = -1.0
        zs_raw = ""
        cot_raw = ""
        
        if not dry_run:
            # Zero Shot
            zs_prompt = get_zero_shot_prompt(profile, target_regime)
            zs_raw = llm.predict(zs_prompt)
            zs_tax = extract_number_from_text(zs_raw)
            
            # Chain of Thought
            cot_prompt = get_cot_prompt(profile, target_regime)
            cot_raw = llm.predict(cot_prompt)
            cot_tax = extract_number_from_text(cot_raw)
        else:
            # Mock values for dry run
            zs_tax = ground_truth * 0.9 # Simulate error
            cot_tax = ground_truth * 0.95
            
        # Record Result
        results.append({
            "profile_id": profile.profile_id,
            "complexity": profile.complexity_category,
            "regime": target_regime,
            "ground_truth": ground_truth,
            "neuro_sym_tax": neuro_tax,
            "zero_shot_tax": zs_tax,
            "cot_tax": cot_tax,
            "neuro_error": abs(neuro_tax - ground_truth),
            "zs_error": abs(zs_tax - ground_truth),
            "cot_error": abs(cot_tax - ground_truth),
            "zs_raw": zs_raw,
            "cot_raw": cot_raw
        })
        
    # 3. Save Results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "experiments/output"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{output_dir}/benchmark_{timestamp}.csv"
    
    keys = results[0].keys()
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
        
    logger.info(f"Benchmark Complete. Results saved to {filename}")
    
    # Calculate simple accuracy (Exact Match within ₹10)
    ns_acc = sum(1 for r in results if r["neuro_error"] <= 10) / len(results)
    print(f"\nResults Summary ({len(results)} samples):")
    print(f"Neuro-Symbolic Exact Match: {ns_acc:.1%}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=5, help="Number of profiles")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls")
    parser.add_argument("--model", type=str, default="gpt-4o-mini")
    
    args = parser.parse_args()
    run_benchmark(args.count, args.dry_run, args.model)
