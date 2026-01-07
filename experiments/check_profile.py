#!/usr/bin/env python3
"""
Check the SPECIFIC profile that had the error
"""
import sys
import os
import json

# Add project root to path  
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Load the detailed log
with open("experiments/output/detailed_log_20260107_173402.json", 'r') as f:
    detailed = json.load(f)

# Get first profile (the one with 179% error)
profile_data = detailed[0]
profile_info = profile_data['input_profile']

print("=" * 80)
print(f"ANALYZING: {profile_info['profile_id']}")
print("=" * 80)

print(f"\nTarget Regime: {profile_info['target_regime']}")
print(f"Ground Truth Tax: ₹{profile_info['ground_truth_tax']:,.2f}")

print(f"\nOrchestrator Result:")
ns = profile_data['models']['neuro_symbolic']
print(f"  Prediction: ₹{ns['prediction']:,.2f}")
print(f"  Error: ₹{ns['error']:,.2f} ({ns.get('error_percentage', 0):.1f}%)")

# The problem: Look at the profile's rent
print(f"\nProfile Details:")
print(f"  Gross Salary: ₹{profile_info['gross_salary']:,.2f}")
print(f"  Basic: ₹{profile_info['basic_salary']:,.2f}")
print(f"  HRA Received: ₹{profile_info['hra_received']:,.2f}")
print(f"  Rent Paid: ₹{profile_info['rent_paid_annual']:,.2f}")  # <-- LOOK HERE!
print(f"  Metro: {profile_info['is_metro_city']}")

# AHA! The rent is ₹1,044,000 which is MORE than the basic salary!
# This might be causing an HRA calculation mismatch

print(f"\n{'='*80}")
print("HYPOTHESIS:")
print(f"{'='*80}")
print(f"Rent (₹{profile_info['rent_paid_annual']:,.2f}) > 3x Basic (₹{profile_info['basic_salary'] * 3:,.2f})")
print("This is unrealistic and might be causing calculation differences!")
print("\nThe generator might have a bug in the rent generation logic.")
