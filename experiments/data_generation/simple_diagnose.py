#!/usr/bin/env python3
"""
Simple diagnostic: Compare tax_comparison.py output with ground truth
for profiles already in Form 16 format.
"""
import json
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.services.tax_comparison import compare_tax_regimes


def diagnose_profile(profile_dict: dict, verbose: bool = True):
    """
    Diagnose a single profile by running it through tax_comparison.py
    and comparing with ground truth.
    """
    profile_id = profile_dict["profile_id"]
    target_regime = profile_dict["target_regime"]
    ground_truth = profile_dict.get("ground_truth_tax", 0)
    
    # Create extracted_data in the format expected by compare_tax_regimes
    extracted_data = {
        "16_Part_B": profile_dict["16_Part_B"]
    }
    
    # Run through tax comparison
    result = compare_tax_regimes(extracted_data=extracted_data)
    
    # Get the tax for the target regime
    if target_regime == "Old":
        calculated_tax = result["old_tax"]
    else:
        calculated_tax = result["new_tax"]
    
    error = abs(calculated_tax - ground_truth)
    error_pct = (error / ground_truth * 100) if ground_truth > 0 else 0
    
    if verbose:
        print(f"\n{'='*80}")
        print(f"Profile: {profile_id} ({target_regime} Regime)")
        print(f"{'='*80}")
        print(f"Ground Truth:       ₹{ground_truth:,.2f}")
        print(f"Calculated Tax:     ₹{calculated_tax:,.2f}")
        print(f"Error:              ₹{error:,.2f} ({error_pct:.2f}%)")
        print(f"Match: {'✅ YES' if error < 1.0 else '❌ NO'}")
        
        # Show key calculation details
        print(f"\nCalculation Details:")
        print(f"  Gross Salary:       ₹{result['gross_salary']:,.2f}")
        print(f"  Other Income:       ₹{result['other_income']:,.2f}")
        print(f"  Financial Year:     {result['financial_year']}")
        
        if target_regime == "Old":
            print(f"\n  Old Regime:")
            print(f"    HRA Exemption:    ₹{result['section_10_exemptions']['hra']:,.2f}")
            print(f"    Std Deduction:    ₹{result['std_ded_old']:,.2f}")
            print(f"    Professional Tax:  ₹{result['professional_tax']:,.2f}")
            print(f"    Chapter VI-A:     ₹{result['ch_via_validated']:,.2f}")
            print(f"    Taxable Income:   ₹{result['old_taxable']:,.2f}")
            print(f"    Tax (with cess):  ₹{result['old_tax']:,.2f}")
        else:
            print(f"\n  New Regime:")
            print(f"    Std Deduction:    ₹{result['std_ded_new']:,.2f}")
            print(f"    Professional Tax:  ₹{result['professional_tax']:,.2f}")
            print(f"    Taxable Income:   ₹{result['new_taxable']:,.2f}")
            print(f"    Tax (with cess):  ₹{result['new_tax']:,.2f}")
    
    return {
        "profile_id": profile_id,
        "target_regime": target_regime,
        "ground_truth": ground_truth,
        "calculated_tax": calculated_tax,
        "error": error,
        "error_pct": error_pct,
        "match": error < 1.0
    }


def main(profiles_file: str, max_profiles: int = 10):
    """Analyze profiles and show diagnostics"""
    
    print(f"📂 Loading profiles from: {profiles_file}")
    with open(profiles_file, 'r') as f:
        profiles = json.load(f)
    
    if max_profiles:
        profiles = profiles[:max_profiles]
    
    print(f"✅ Loaded {len(profiles)} profiles\n")
    
    results = []
    for i, profile in enumerate(profiles, 1):
        print(f"\n{'#'*80}")
        print(f"PROFILE {i}/{len(profiles)}")
        result = diagnose_profile(profile, verbose=True)
        results.append(result)
    
    # Summary
    print(f"\n\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    
    perfect_match = sum(1 for r in results if r["match"])
    avg_error = sum(r["error"] for r in results) / len(results)
    
    print(f"Total Profiles:       {len(results)}")
    print(f"Perfect Matches:      {perfect_match} ({perfect_match/len(results)*100:.1f}%)")
    print(f"Average Error:        ₹{avg_error:,.2f}")
    
    if results:
        max_error_profile = max(results, key=lambda r: r["error"])
        print(f"\nLargest Error:")
        print(f"  Profile: {max_error_profile['profile_id']}")
        print(f"  Error: ₹{max_error_profile['error']:,.2f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default="experiments/profiles.json")
    parser.add_argument("--max", type=int, default=10)
    
    args = parser.parse_args()
    
    main(args.profiles, args.max)
