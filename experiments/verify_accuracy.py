#!/usr/bin/env python3
"""
Run 10 verification tests to check accuracy
"""
import sys
import os

# Add project root to  path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

from experiments.data_generation.generator import TaxProfileGenerator
from experiments.execution.adapter import adapt_profile_to_orchestrator

# Mock dependencies
from unittest.mock import MagicMock
sys.modules["llama_cloud_services"] = MagicMock()
sys.modules["services.form_extraction"] = MagicMock()
sys.modules["src.services.form_extraction"] = MagicMock()
sys.modules["langchain_classic"] = MagicMock()
sys.modules["langchain_classic.agents"] = MagicMock()
sys.modules["services.tax_advisor"] = MagicMock()
sys.modules["src.services.tax_advisor"] = MagicMock()
sys.modules["services.form_generation"] = MagicMock()
sys.modules["src.services.form_generation"] = MagicMock()

from src.services.orchestrator import TaxOrchestrator

print("=" * 80)
print("RUNNING 10 VERIFICATION TESTS")
print("=" * 80)

gen = TaxProfileGenerator()
errors = []
old_regime_tests = []
new_regime_tests = []

for i in range(10):
    profile = gen.generate_profile()
    
    # Run orchestrator
    input_data = adapt_profile_to_orchestrator(profile)
    orchestrator = TaxOrchestrator()
    orchestrator.run_computation_with_data(input_data)
    
    res = orchestrator.state["computation_result"]
    old_tax = res.get("old_tax", -1.0)
    new_tax = res.get("new_tax", -1.0)
    
    if profile.target_regime == "Old":
        orchestrator_tax = old_tax
        old_regime_tests.append({
            "id": profile.profile_id,
            "ground_truth": profile.ground_truth_tax,
            "orchestrator": orchestrator_tax,
            "error": abs(orchestrator_tax - profile.ground_truth_tax)
        })
    else:
        orchestrator_tax = new_tax
        new_regime_tests.append({
            "id": profile.profile_id,
            "ground_truth": profile.ground_truth_tax,
            "orchestrator": orchestrator_tax,
            "error": abs(orchestrator_tax - profile.ground_truth_tax)
        })
    
    error = abs(orchestrator_tax - profile.ground_truth_tax)
    if error > 10:  # More than ₹10 difference
        errors.append({
            "profile_id": profile.profile_id,
            "regime": profile.target_regime,
            "ground_truth": profile.ground_truth_tax,
            "orchestrator": orchestrator_tax,
            "error": error
        })

print(f"\n{'-'*80}")
print("OLD REGIME RESULTS (HRA applies)")
print(f"{'-'*80}")
if old_regime_tests:
    for t in old_regime_tests:
        status = "✅" if t["error"] <= 10 else "❌"
        print(f"{status} {t['id']}: GT=₹{t['ground_truth']:,.2f}, Orch=₹{t['orchestrator']:,.2f}, Err=₹{t['error']:,.2f}")
    
    avg_error = sum(t["error"] for t in old_regime_tests) / len(old_regime_tests)
    max_error = max(t["error"] for t in old_regime_tests)
    accuracy = sum(1 for t in old_regime_tests if t["error"] <= 10) / len(old_regime_tests) * 100
    
    print(f"\nOld Regime Summary:")
    print(f"  Tests: {len(old_regime_tests)}")
    print(f"  Avg Error: ₹{avg_error:,.2f}")
    print(f"  Max Error: ₹{max_error:,.2f}")
    print(f"  Accuracy (±₹10): {accuracy:.1f}%")
else:
    print("No Old Regime profiles generated")

print(f"\n{'-'*80}")
print("NEW REGIME RESULTS (HRA doesn't apply)")
print(f"{'-'*80}")
if new_regime_tests:
    for t in new_regime_tests:
        status = "✅" if t["error"] <= 10 else "❌"
        print(f"{status} {t['id']}: GT=₹{t['ground_truth']:,.2f}, Orch=₹{t['orchestrator']:,.2f}, Err=₹{t['error']:,.2f}")
    
    avg_error = sum(t["error"] for t in new_regime_tests) / len(new_regime_tests)
    max_error = max(t["error"] for t in new_regime_tests)
    accuracy = sum(1 for t in new_regime_tests if t["error"] <= 10) / len(new_regime_tests) * 100
    
    print(f"\nNew Regime Summary:")
    print(f"  Tests: {len(new_regime_tests)}")
    print(f"  Avg Error: ₹{avg_error:,.2f}")
    print(f"  Max Error: ₹{max_error:,.2f}")
    print(f"  Accuracy (±₹10): {accuracy:.1f}%")
else:
    print("No New Regime profiles generated")

print(f"\n{'='*80}")
print("OVERALL SUMMARY")
print(f"{'='*80}")
total_tests = len(old_regime_tests) + len(new_regime_tests)
passing_tests = sum(1 for t in old_regime_tests + new_regime_tests if t["error"] <= 10)
overall_accuracy = passing_tests / total_tests * 100 if total_tests > 0 else 0

print(f"Total Tests: {total_tests}")
print(f"Passing (±₹10): {passing_tests}/{total_tests}")
print(f"Overall Accuracy: {overall_accuracy:.1f}%")

if overall_accuracy == 100.0:
    print("\n🎉 SUCCESS! All tests passed - Neuro-Symbolic system is 100% accurate!")
elif overall_accuracy >= 90:
    print(f"\n⚠️  Near-perfect accuracy ({overall_accuracy:.1f}%) - investigate remaining errors")
else:
    print(f"\n❌ Low accuracy ({overall_accuracy:.1f}%) - critical issues remain")
