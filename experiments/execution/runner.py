import sys
import os
import csv
import json
import logging
import argparse
import numpy as np
from datetime import datetime
from tqdm import tqdm
from dotenv import load_dotenv

# Load environment variables from .env files (check multiple locations)
for env_path in [".env", "experiments/.env", "experiments/batch_run/.env"]:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
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
        logging.FileHandler("experiments/execution_runner.log", encoding="utf-8"),
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
    # Setup output directory and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = "experiments/output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Generate Data
    logger.info(f"Generating {count} synthetic tax profiles...")
    generator = TaxProfileGenerator()
    profiles = generator.generate_batch(count)
    
    # Save synthetic profiles to JSON for future reference
    profiles_data = []
    for profile in profiles:
        # Calculate total 80C components
        total_80c = (profile.deductions.pf_contribution + 
                     profile.deductions.elss + 
                     profile.deductions.lic_premium + 
                     profile.deductions.ppf)
        total_80d = (profile.deductions.medical_insurance_self + 
                     profile.deductions.medical_insurance_parents)
        
        profiles_data.append({
            "profile_id": profile.profile_id,
            "age": profile.age,
            "complexity_category": profile.complexity_category,
            "target_regime": profile.target_regime,
            "ground_truth_tax": profile.ground_truth_tax,
            # Income details
            "gross_salary": profile.income.gross_salary,
            "basic_salary": profile.income.basic_salary,
            "hra_received": profile.income.hra_received,
            "other_income": profile.income.other_sources_income,
            # Deduction details
            "pf_contribution": profile.deductions.pf_contribution,
            "elss": profile.deductions.elss,
            "lic_premium": profile.deductions.lic_premium,
            "ppf": profile.deductions.ppf,
            "total_80c": total_80c,
            "medical_insurance_self": profile.deductions.medical_insurance_self,
            "medical_insurance_parents": profile.deductions.medical_insurance_parents,
            "total_80d": total_80d,
            "rent_paid_annual": profile.deductions.rent_paid_annual,
            "is_metro_city": profile.deductions.is_metro_city
        })
    
    profiles_json_file = f"{output_dir}/synthetic_profiles_{timestamp}.json"
    with open(profiles_json_file, "w") as f:
        json.dump(profiles_data, f, indent=2)
    logger.info(f"Saved synthetic profiles to {profiles_json_file}")
    
    # 2. Setup LLM (Baseline)
    # If dry_run, mock the LLM to save costs
    llm = None
    if not dry_run:
        llm = ResearchLLM(model_name=model or "gpt-4o-mini")
    
    results = []
    detailed_logs = []
    
    logger.info("Starting Benchmark Loop...")
    for i, profile in enumerate(tqdm(profiles, desc="Benchmarking")):
        input_data = adapt_profile_to_orchestrator(profile)
        target_regime = profile.target_regime
        ground_truth = profile.ground_truth_tax
        
        log_entry = {
            "profile_id": profile.profile_id,
            "timestamp": datetime.now().isoformat(),
            "input_profile": profiles_data[i],
            "models": {}
        }
        
        # --- A. Neuro-Symbolic (Orchestrator) ---
        neuro_tax = -1.0
        neuro_error_msg = None
        try:
            orchestrator = TaxOrchestrator()
            # We use 'run_computation_with_data' which calls compare_tax_regimes
            orchestrator.run_computation_with_data(input_data)
            
            res = orchestrator.state["computation_result"]
            if target_regime == "Old":
                neuro_tax = res.get("old_tax", -1.0)
            else:
                neuro_tax = res.get("new_tax", -1.0)
            
            log_entry["models"]["neuro_symbolic"] = {
                "prediction": neuro_tax,
                "error": abs(neuro_tax - ground_truth),
                "error_percentage": (abs(neuro_tax - ground_truth) / max(ground_truth, 1)) * 100,
                "status": "success"
            }
                
        except Exception as e:
            logger.error(f"NeuroSym Error on {profile.profile_id}: {e}")
            neuro_tax = -999.0 # Error Code
            neuro_error_msg = str(e)
            log_entry["models"]["neuro_symbolic"] = {
                "prediction": neuro_tax,
                "error": -999.0,
                "status": "error",
                "error_message": neuro_error_msg
            }
            
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
            
            log_entry["models"]["zero_shot"] = {
                "prediction": zs_tax,
                "error": abs(zs_tax - ground_truth),
                "error_percentage": (abs(zs_tax - ground_truth) / max(ground_truth, 1)) * 100,
                "raw_output": zs_raw,
                "prompt": zs_prompt,
                "status": "success"
            }
            
            # Chain of Thought
            cot_prompt = get_cot_prompt(profile, target_regime)
            cot_raw = llm.predict(cot_prompt)
            cot_tax = extract_number_from_text(cot_raw)
            
            log_entry["models"]["chain_of_thought"] = {
                "prediction": cot_tax,
                "error": abs(cot_tax - ground_truth),
                "error_percentage": (abs(cot_tax - ground_truth) / max(ground_truth, 1)) * 100,
                "raw_output": cot_raw,
                "prompt": cot_prompt,
                "status": "success"
            }
        else:
            # Mock values for dry run
            zs_tax = ground_truth * 0.9 # Simulate error
            cot_tax = ground_truth * 0.95
            
            log_entry["models"]["zero_shot"] = {
                "prediction": zs_tax,
                "error": abs(zs_tax - ground_truth),
                "status": "dry_run_mock"
            }
            log_entry["models"]["chain_of_thought"] = {
                "prediction": cot_tax,
                "error": abs(cot_tax - ground_truth),
                "status": "dry_run_mock"
            }
        
        detailed_logs.append(log_entry)
            
        # Record Result for CSV
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
    
    # 3. Save Results - Multiple Formats
    
    # 3a. CSV Summary
    csv_filename = f"{output_dir}/benchmark_{timestamp}.csv"
    keys = results[0].keys()
    with open(csv_filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    logger.info(f"CSV results saved to {csv_filename}")
    
    # 3b. Detailed JSON Log
    json_filename = f"{output_dir}/detailed_log_{timestamp}.json"
    with open(json_filename, "w") as f:
        json.dump(detailed_logs, f, indent=2)
    logger.info(f"Detailed JSON log saved to {json_filename}")
    
    # 3c. Human-Readable Text Log
    text_log_filename = f"{output_dir}/readable_log_{timestamp}.txt"
    with open(text_log_filename, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write(f"TAX COMPUTATION BENCHMARK - {timestamp}\n")
        f.write(f"Model: {model or 'gpt-4o-mini'}\n")
        f.write(f"Total Profiles: {count}\n")
        f.write(f"Dry Run: {dry_run}\n")
        f.write("=" * 80 + "\n\n")
        
        for i, (profile, result, log) in enumerate(zip(profiles, results, detailed_logs), 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"PROFILE {i}/{count}: {profile.profile_id}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Complexity: {profile.complexity_category}\n")
            f.write(f"Target Regime: {profile.target_regime}\n")
            f.write(f"Age: {profile.age}\n")
            f.write(f"Gross Salary: ₹{profile.income.gross_salary:,.2f}\n")
            f.write(f"Basic Salary: ₹{profile.income.basic_salary:,.2f}\n")
            f.write(f"HRA Received: ₹{profile.income.hra_received:,.2f}\n")
            f.write(f"Other Income: ₹{profile.income.other_sources_income:,.2f}\n")
            f.write(f"\nDeductions:\n")
            f.write(f"  Total 80C: ₹{profiles_data[i-1]['total_80c']:,.2f}\n")
            f.write(f"    - PF: ₹{profile.deductions.pf_contribution:,.2f}\n")
            f.write(f"    - ELSS: ₹{profile.deductions.elss:,.2f}\n")
            f.write(f"    - LIC: ₹{profile.deductions.lic_premium:,.2f}\n")
            f.write(f"    - PPF: ₹{profile.deductions.ppf:,.2f}\n")
            f.write(f"  Total 80D: ₹{profiles_data[i-1]['total_80d']:,.2f}\n")
            f.write(f"    - Self/Family: ₹{profile.deductions.medical_insurance_self:,.2f}\n")
            f.write(f"    - Parents: ₹{profile.deductions.medical_insurance_parents:,.2f}\n")
            f.write(f"  Rent Paid: ₹{profile.deductions.rent_paid_annual:,.2f} (Metro: {profile.deductions.is_metro_city})\n")
            f.write(f"\nGROUND TRUTH: ₹{profile.ground_truth_tax:,.2f}\n")
            f.write(f"\n{'-' * 80}\n")
            f.write("MODEL PREDICTIONS:\n")
            f.write(f"{'-' * 80}\n")
            
            # Neuro-Symbolic
            f.write(f"\n1. NEURO-SYMBOLIC (TaxOrchestrator):\n")
            if "neuro_symbolic" in log["models"]:
                ns = log["models"]["neuro_symbolic"]
                f.write(f"   Prediction: ₹{ns['prediction']:,.2f}\n")
                if ns['status'] == 'success':
                    f.write(f"   Error: ₹{ns['error']:,.2f} ({ns['error_percentage']:.2f}%)\n")
                else:
                    f.write(f"   Status: ERROR - {ns.get('error_message', 'Unknown error')}\n")
            
            # Zero Shot
            f.write(f"\n2. ZERO-SHOT LLM:\n")
            if "zero_shot" in log["models"]:
                zs = log["models"]["zero_shot"]
                f.write(f"   Prediction: ₹{zs['prediction']:,.2f}\n")
                if zs['status'] == 'success':
                    f.write(f"   Error: ₹{zs['error']:,.2f} ({zs['error_percentage']:.2f}%)\n")
                    if not dry_run:
                        f.write(f"   Raw Output (first 200 chars): {zs['raw_output'][:200]}...\n")
            
            # Chain of Thought
            f.write(f"\n3. CHAIN-OF-THOUGHT LLM:\n")
            if "chain_of_thought" in log["models"]:
                cot = log["models"]["chain_of_thought"]
                f.write(f"   Prediction: ₹{cot['prediction']:,.2f}\n")
                if cot['status'] == 'success':
                    f.write(f"   Error: ₹{cot['error']:,.2f} ({cot['error_percentage']:.2f}%)\n")
                    if not dry_run:
                        f.write(f"   Raw Output (first 200 chars): {cot['raw_output'][:200]}...\n")
            
            f.write("\n")
    
    logger.info(f"Human-readable log saved to {text_log_filename}")
        
    # 4. Calculate and Display Statistics
    neuro_errors = np.array([r["neuro_error"] for r in results])
    zs_errors    = np.array([r["zs_error"]    for r in results])
    cot_errors   = np.array([r["cot_error"]   for r in results])
    ground_truths = np.array([r["ground_truth"] for r in results])

    # Exact Match Accuracy (EMA): within Rs 10
    ns_acc  = np.mean(neuro_errors <= 10)
    zs_acc  = np.mean(zs_errors    <= 10)
    cot_acc = np.mean(cot_errors   <= 10)

    # MAE, Median, Std Dev
    ns_mae    = np.mean(neuro_errors)
    ns_median = np.median(neuro_errors)
    ns_std    = np.std(neuro_errors)
    ns_min    = np.min(neuro_errors)
    ns_max    = np.max(neuro_errors)

    # Mean Relative Error
    relative_errors = np.where(ground_truths > 0, (neuro_errors / ground_truths) * 100, 0.0)
    ns_mean_rel_err   = np.mean(relative_errors)
    ns_median_rel_err = np.median(relative_errors)
    ns_std_rel_err    = np.std(relative_errors)

    # Slab Hallucination Rate: profiles with >50% relative error
    slab_hallucinations = int(np.sum(relative_errors > 50))
    slab_hallucination_rate = slab_hallucinations / len(results)

    # Error Magnitude Distribution
    dist_perfect = int(np.sum(neuro_errors < 10))
    dist_small   = int(np.sum((neuro_errors >= 10)  & (neuro_errors < 100)))
    dist_medium  = int(np.sum((neuro_errors >= 100) & (neuro_errors < 1000)))
    dist_large   = int(np.sum((neuro_errors >= 1000) & (neuro_errors < 10000)))
    dist_xlarge  = int(np.sum(neuro_errors >= 10000))

    # Per-regime breakdown
    old_errors = np.array([r["neuro_error"] for r in results if r["regime"] == "Old"])
    new_errors = np.array([r["neuro_error"] for r in results if r["regime"] == "New"])
    old_acc    = float(np.mean(old_errors <= 10)) if len(old_errors) > 0 else 0.0
    new_acc    = float(np.mean(new_errors <= 10)) if len(new_errors) > 0 else 0.0

    # Per-complexity breakdown
    for_complexity = {}
    for cx in ["Simple", "Medium", "Complex"]:
        cx_errors = np.array([r["neuro_error"] for r in results if r["complexity"] == cx])
        if len(cx_errors) > 0:
            for_complexity[cx] = {
                "count": len(cx_errors),
                "acc": float(np.mean(cx_errors <= 10)),
                "mae": float(np.mean(cx_errors)),
            }

    # Print full report
    print(f"\n{'=' * 80}")
    print(f"BENCHMARK RESULTS SUMMARY ({len(results)} samples)")
    print(f"{'=' * 80}")

    print(f"\n--- Exact Match Accuracy (within Rs 10) ---")
    print(f"  Neuro-Symbolic:    {ns_acc:>6.1%}")
    print(f"  Zero-Shot LLM:     {zs_acc:>6.1%}")
    print(f"  Chain-of-Thought:  {cot_acc:>6.1%}")

    print(f"\n--- Neuro-Symbolic Error Statistics ---")
    print(f"  Mean Absolute Error (MAE):  Rs {ns_mae:>10,.2f}")
    print(f"  Median Error:               Rs {ns_median:>10,.2f}")
    print(f"  Std Deviation:              Rs {ns_std:>10,.2f}")
    print(f"  Min Error:                  Rs {ns_min:>10,.2f}")
    print(f"  Max Error:                  Rs {ns_max:>10,.2f}")

    print(f"\n--- Relative Error ---")
    print(f"  Mean Relative Error:    {ns_mean_rel_err:>6.2f}%")
    print(f"  Median Relative Error:  {ns_median_rel_err:>6.2f}%")
    print(f"  Std Dev Relative Error: {ns_std_rel_err:>6.2f}%")

    print(f"\n--- Slab Hallucination Rate (>50% error) ---")
    print(f"  Count:  {slab_hallucinations} profiles")
    print(f"  Rate:   {slab_hallucination_rate:.1%}")

    print(f"\n--- Error Magnitude Distribution ---")
    print(f"  Perfect   (<Rs 10):          {dist_perfect:>4} profiles  ({dist_perfect/len(results):.1%})")
    print(f"  Small     (Rs 10-100):       {dist_small:>4} profiles  ({dist_small/len(results):.1%})")
    print(f"  Medium    (Rs 100-1K):       {dist_medium:>4} profiles  ({dist_medium/len(results):.1%})")
    print(f"  Large     (Rs 1K-10K):       {dist_large:>4} profiles  ({dist_large/len(results):.1%})")
    print(f"  Very Large(>Rs 10K):         {dist_xlarge:>4} profiles  ({dist_xlarge/len(results):.1%})")

    print(f"\n--- Accuracy by Regime ---")
    print(f"  Old Regime ({len(old_errors)} profiles): {old_acc:.1%}")
    print(f"  New Regime ({len(new_errors)} profiles): {new_acc:.1%}")

    print(f"\n--- Accuracy by Complexity ---")
    for cx, cx_stats in for_complexity.items():
        print(f"  {cx:<8} ({cx_stats['count']:>3} profiles): Acc={cx_stats['acc']:.1%}  MAE=Rs {cx_stats['mae']:,.2f}")

    print(f"\n{'=' * 80}")
    print(f"\nOutput Files:")
    print(f"  Synthetic Profiles:  {profiles_json_file}")
    print(f"  CSV Summary:         {csv_filename}")
    print(f"  Detailed JSON Log:   {json_filename}")
    print(f"  Readable Text Log:   {text_log_filename}")
    print(f"{'=' * 80}\n")

    # Save metrics to JSON
    metrics_file = f"{output_dir}/final_metrics_{count}profiles_{timestamp}.json"
    metrics = {
        "total_profiles": len(results),
        "exact_match_accuracy": {"neuro_symbolic": float(ns_acc), "zero_shot": float(zs_acc), "chain_of_thought": float(cot_acc)},
        "neuro_symbolic_error_stats": {
            "mae": float(ns_mae), "median": float(ns_median),
            "std_dev": float(ns_std), "min": float(ns_min), "max": float(ns_max)
        },
        "relative_error": {"mean": float(ns_mean_rel_err), "median": float(ns_median_rel_err), "std_dev": float(ns_std_rel_err)},
        "slab_hallucination": {"count": slab_hallucinations, "rate": float(slab_hallucination_rate)},
        "error_distribution": {
            "perfect_lt10": dist_perfect, "small_10_100": dist_small,
            "medium_100_1k": dist_medium, "large_1k_10k": dist_large, "very_large_gt10k": dist_xlarge
        },
        "by_regime": {"old": {"count": len(old_errors), "accuracy": old_acc}, "new": {"count": len(new_errors), "accuracy": new_acc}},
        "by_complexity": for_complexity
    }
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    logger.info(f"Metrics JSON saved to {metrics_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tax Computation Benchmark: Compare Neuro-Symbolic vs LLM approaches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Free Models (recommended):
  google/gemini-2.0-flash-exp:free    (Default - Fast & Accurate)
  google/gemini-flash-1.5:free        (Good balance)
  meta-llama/llama-3.2-3b-instruct:free
  
Paid Models:
  openai/gpt-4o-mini                  ($0.15/1M tokens)
  openai/gpt-4o                       ($5/1M tokens)

Examples:
  python3 runner.py --count 10 --dry-run
  python3 runner.py --count 50 --model google/gemini-2.0-flash-exp:free
  python3 runner.py --count 100 --model openai/gpt-4o-mini
        """
    )
    parser.add_argument("--count", type=int, default=5, help="Number of profiles to generate and test")
    parser.add_argument("--dry-run", action="store_true", help="Skip LLM calls (mock results to save costs)")
    parser.add_argument("--model", type=str, default="google/gemini-2.0-flash-exp:free", 
                       help="Model to use (default: free Gemini 2.0 Flash)")
    
    args = parser.parse_args()
    run_benchmark(args.count, args.dry_run, args.model)
