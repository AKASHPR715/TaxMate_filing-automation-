#!/usr/bin/env python3
"""
Debug script to compare ground truth calculation vs orchestrator calculation
"""
import sys
import os

# Add project root to path
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

# Generate one profile
gen = TaxProfileGenerator()
profile = gen.generate_profile()

print("=" * 80)
print("GROUND TRUTH vs ORCHESTRATOR COMPARISON")
print("=" * 80)

print(f"\nProfile ID: {profile.profile_id}")
print(f"Target Regime: {profile.target_regime}")
print(f"Complexity: {profile.complexity_category}")
print(f"\nIncome:")
print(f"  Gross Salary: ₹{profile.income.gross_salary:,.2f}")
print(f"  Basic: ₹{profile.income.basic_salary:,.2f}")
print(f"  HRA: ₹{profile.income.hra_received:,.2f}")
print(f"  Other: ₹{profile.income.other_sources_income:,.2f}")

print(f"\nDeductions:")
pf = profile.deductions.pf_contribution
elss = profile.deductions.elss
lic = profile.deductions.lic_premium
ppf = profile.deductions.ppf
total_80c = pf + elss + lic + ppf
print(f"  80C Total: ₹{total_80c:,.2f}")
print(f"    - PF: ₹{pf:,.2f}")
print(f"    - ELSS: ₹{elss:,.2f}")
print(f"    - LIC: ₹{lic:,.2f}")
print(f"    - PPF: ₹{ppf:,.2f}")

med_self = profile.deductions.medical_insurance_self
med_parents = profile.deductions.medical_insurance_parents
print(f"  80D Total: ₹{med_self + med_parents:,.2f}")
print(f"    - Self: ₹{med_self:,.2f}")
print(f"    - Parents: ₹{med_parents:,.2f}")
print(f"  Rent: ₹{profile.deductions.rent_paid_annual:,.2f} (Metro: {profile.deductions.is_metro_city})")

print(f"\n{'='*80}")
print("GROUND TRUTH CALCULATION (from generator.py)")
print(f"{'='*80}")
print(f"Target Regime: {profile.target_regime}")
print(f"Ground Truth Tax: ₹{profile.ground_truth_tax:,.2f}")

print(f"\n{'='*80}")
print("ORCHESTRATOR CALCULATION")
print(f"{'='*80}")

# Run orchestrator
input_data = adapt_profile_to_orchestrator(profile)
orchestrator = TaxOrchestrator()
orchestrator.run_computation_with_data(input_data)

res = orchestrator.state["computation_result"]
old_tax = res.get("old_tax", -1.0)
new_tax = res.get("new_tax", -1.0)
optimal = res.get("optimal_regime", "UNKNOWN")

print(f"Old Regime Tax: ₹{old_tax:,.2f}")
print(f"New Regime Tax: ₹{new_tax:,.2f}")
print(f"Optimal Regime: {optimal}")

print(f"\n{'='*80}")
print("COMPARISON")
print(f"{'='*80}")

if profile.target_regime == "Old":
    orchestrator_tax = old_tax
else:
    orchestrator_tax = new_tax

print(f"Target Regime: {profile.target_regime}")
print(f"Ground Truth: ₹{profile.ground_truth_tax:,.2f}")
print(f"Orchestrator ({profile.target_regime}): ₹{orchestrator_tax:,.2f}")
print(f"Difference: ₹{abs(orchestrator_tax - profile.ground_truth_tax):,.2f}")

if abs(orchestrator_tax - profile.ground_truth_tax) > 1:
    print("\n❌ MISMATCH DETECTED!")
    print("\nPossible causes:")
    print("1. Generator uses different HRA exemption calculation")
    print("2. Generator uses different standard deduction amount")
    print("3. Generator uses different tax slab/cess logic")
    print("\nDebugging both calculations...")
    
    # Show orchestrator's detailed calculation
    print(f"\nOrchestrator Details:")
    print(f"  Old Tax: ₹{old_tax:,.2f}")
    print(f"  New Tax: ₹{new_tax:,.2f}")
else:
    print("\n✅ MATCH! Ground truth and Orchestrator agree.")
