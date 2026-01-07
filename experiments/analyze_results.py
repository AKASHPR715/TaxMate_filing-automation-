#!/usr/bin/env python3
"""
Analyze partial benchmark results from Gemini Flash run
"""
import json
import csv
from pathlib import Path

# Read CSV results
csv_file = "experiments/output/benchmark_20260107_173402.csv"
json_file = "experiments/output/detailed_log_20260107_173402.json"

print("=" * 80)
print("PARTIAL BENCHMARK ANALYSIS (3 Profiles)")
print("=" * 80)

# Load data
with open(csv_file, 'r') as f:
    reader = csv.DictReader(f)
    results = list(reader)

with open(json_file, 'r') as f:
    detailed = json.load(f)

print(f"\n{'Profile ID':<15} {'Complexity':<10} {'Regime':<8} {'Ground Truth':>12} {'NeuraSym':>12} {'NS Error':>12} {'Status'}")
print("-" * 95)

for r in results:
    profile_id = r['profile_id']
    complexity = r['complexity']
    regime = r['regime']
    ground_truth = float(r['ground_truth'])
    neuro_tax = float(r['neuro_sym_tax'])
    neuro_error = float(r['neuro_error'])
    
    # Find detailed info
    detail = next((d for d in detailed if d['profile_id'] == profile_id), None)
    if detail:
        ns_status = detail['models']['neuro_symbolic']['status']
        error_pct = detail['models']['neuro_symbolic'].get('error_percentage', 0)
        
        print(f"{profile_id:<15} {complexity:<10} {regime:<8} ₹{ground_truth:>11,.2f} ₹{neuro_tax:>11,.2f} ₹{neuro_error:>11,.2f} ({error_pct:>6.1f}%)")

print("\n" + "=" * 80)
print("ISSUE DETECTED: Neuro-Symbolic System Has Errors!")
print("=" * 80)

print("\nExpected: Neuro-Symbolic should have 0% error (it's deterministic)")
print("Actual: Errors ranging from ₹3,900 to ₹7,800\n")

print("Root Cause Analysis:")
print("-" * 80)

for i, detail in enumerate(detailed, 1):
    profile = detail['input_profile']
    ns = detail['models']['neuro_symbolic']
    
    print(f"\nProfile {i}: {detail['profile_id']}")
    print(f"  Target Regime: {profile['target_regime']}")
    print(f"  Ground Truth: ₹{profile['ground_truth_tax']:,.2f}")
    print(f"  Neuro-Symbolic Output: ₹{ns['prediction']:,.2f}")
    print(f"  Error: ₹{ns['error']:,.2f} ({ns.get('error_percentage', 0):.1f}%)")
    
    # The issue: Target regime vs what orchestrator calculates
    print(f"\n  HYPOTHESIS: The orchestrator calculates BOTH regimes,")
    print(f"  but ground truth is for the TARGET regime ({profile['target_regime']})")
    print(f"  The runner might be extracting the wrong regime's result!")

print("\n" + "=" * 80)
print("ACTION NEEDED: Fix runner.py to extract correct regime")
print("=" * 80)
