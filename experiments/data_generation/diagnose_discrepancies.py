#!/usr/bin/env python3
"""
Diagnostic script to compare ground truth vs neuro-symbolic calculations
and identify exact sources of discrepancy.
"""
import json
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.services.tax_comparison import compare_tax_regimes
from experiments.execution.adapter import adapt_profile_to_orchestrator
from experiments.data_generation.schema import TaxProfile


def load_profile_from_json(profile_dict: dict) -> TaxProfile:
    """Convert JSON dict to TaxProfile object"""
    from experiments.data_generation.schema import IncomeDetails, DeductionDetails
    
    income = IncomeDetails(
        gross_salary=profile_dict["gross_salary"],
        basic_salary=profile_dict["basic_salary"],
        hra_received=profile_dict["hra_received"],
        special_allowance=0,
        other_sources_income=profile_dict["other_income"]
    )
    
    deductions = DeductionDetails(
        pf_contribution=profile_dict["pf_contribution"],
        elss=profile_dict["elss"],
        lic_premium=profile_dict["lic_premium"],
        ppf=profile_dict["ppf"],
        medical_insurance_self=profile_dict["medical_insurance_self"],
        medical_insurance_parents=profile_dict["medical_insurance_parents"],
        rent_paid_annual=profile_dict["rent_paid_annual"],
        is_metro_city=profile_dict["is_metro_city"]
    )
    
    return TaxProfile(
        profile_id=profile_dict["profile_id"],
        age=profile_dict["age"],
        income=income,
        deductions=deductions,
        target_regime=profile_dict["target_regime"],
        complexity_category=profile_dict["complexity_category"],
        ground_truth_tax=profile_dict["ground_truth_tax"]
    )


def diagnose_single_profile(profile_dict: dict, verbose: bool = True):
    """
    Diagnose calculation differences for a single profile.
    Returns detailed breakdown of where differences occur.
    """
    # Convert to TaxProfile object
    profile = load_profile_from_json(profile_dict)
    
    # Get ground truth
    ground_truth = profile_dict["ground_truth_tax"]
    
    # Calculate using neuro-symbolic system
    extracted_data = adapt_profile_to_orchestrator(profile)
    result = compare_tax_regimes(extracted_data=extracted_data)
    
    # Determine which tax to compare based on target regime
    target_regime = profile_dict["target_regime"]
    if target_regime == "Old":
        neuro_tax = result["old_tax"]
    else:
        neuro_tax = result["new_tax"]
    
    # Calculate error
    error = abs(neuro_tax - ground_truth)
    error_pct = (error / ground_truth * 100) if ground_truth > 0 else 0
    
    diagnosis = {
        "profile_id": profile_dict["profile_id"],
        "target_regime": target_regime,
        "ground_truth": ground_truth,
        "neuro_symbolic": neuro_tax,
        "error": error,
        "error_pct": error_pct,
        "match": error < 1.0,  # Within ₹1 is considered a match
        "details": {
            "gross_salary": result["gross_salary"],
            "other_income": result["other_income"],
            "section_10_exemptions": result["section_10_exemptions"],
            "professional_tax": result["professional_tax"],
            "std_ded_old": result["std_ded_old"],
            "std_ded_new": result["std_ded_new"],
            "ch_via_validated": result["ch_via_validated"],
            "old_gti": result["old_gti"],
            "old_taxable": result["old_taxable"],
            "old_tax": result["old_tax"],
            "new_gti": result["new_gti"],
            "new_taxable": result["new_taxable"],
            "new_tax": result["new_tax"],
        }
    }
    
    if verbose and error >= 1.0:
        print(f"\n{'='*80}")
        print(f"DIAGNOSIS: {profile_dict['profile_id']} ({target_regime} Regime)")
        print(f"{'='*80}")
        print(f"Ground Truth:     ₹{ground_truth:,.2f}")
        print(f"Neuro-Symbolic:   ₹{neuro_tax:,.2f}")
        print(f"Error:            ₹{error:,.2f} ({error_pct:.2f}%)")
        print(f"\nIncome Details:")
        print(f"  Gross Salary:        ₹{result['gross_salary']:,.2f}")
        print(f"  Other Income:        ₹{result['other_income']:,.2f}")
        print(f"  HRA Exemption:       ₹{result['section_10_exemptions']['hra']:,.2f}")
        print(f"  Professional Tax:    ₹{result['professional_tax']:,.2f}")
        
        if target_regime == "Old":
            print(f"\nOld Regime Calculation:")
            print(f"  Standard Deduction:  ₹{result['std_ded_old']:,.2f}")
            print(f"  Chapter VI-A:        ₹{result['ch_via_validated']:,.2f}")
            print(f"  Gross Total Income:  ₹{result['old_gti']:,.2f}")
            print(f"  Taxable Income:      ₹{result['old_taxable']:,.2f}")
            print(f"  Tax (with cess):     ₹{result['old_tax']:,.2f}")
        else:
            print(f"\nNew Regime Calculation:")
            print(f"  Standard Deduction:  ₹{result['std_ded_new']:,.2f}")
            print(f"  Gross Total Income:  ₹{result['new_gti']:,.2f}")
            print(f"  Taxable Income:      ₹{result['new_taxable']:,.2f}")
            print(f"  Tax (with cess):     ₹{result['new_tax']:,.2f}")
    
    return diagnosis


def analyze_profiles_file(input_file: Path, max_profiles: int = None):
    """Analyze all profiles and identify patterns in errors"""
    
    print(f"📂 Loading profiles from: {input_file}")
    with open(input_file, 'r') as f:
        profiles = json.load(f)
    
    if max_profiles:
        profiles = profiles[:max_profiles]
    
    print(f"✅ Loaded {len(profiles)} profiles")
    print(f"🔍 Analyzing discrepancies...\n")
    
    results = {
        "total": 0,
        "perfect_match": 0,
        "small_error": 0,
        "medium_error": 0,
        "large_error": 0,
        "errors": [],
        "old_regime_errors": [],
        "new_regime_errors": []
    }
    
    for i, profile in enumerate(profiles, 1):
        diagnosis = diagnose_single_profile(profile, verbose=False)
        
        results["total"] += 1
        error = diagnosis["error"]
        
        if error < 1.0:
            results["perfect_match"] += 1
        elif error < 100:
            results["small_error"] += 1
            results["errors"].append(diagnosis)
        elif error < 1000:
            results["medium_error"] += 1
            results["errors"].append(diagnosis)
        else:
            results["large_error"] += 1
            results["errors"].append(diagnosis)
        
        if diagnosis["target_regime"] == "Old":
            if error >= 1.0:
                results["old_regime_errors"].append(diagnosis)
        else:
            if error >= 1.0:
                results["new_regime_errors"].append(diagnosis)
        
        if i % 50 == 0:
            print(f"   Analyzed {i}/{len(profiles)} profiles...")
    
    # Print summary
    print(f"\n{'='*80}")
    print(f"ANALYSIS SUMMARY")
    print(f"{'='*80}")
    print(f"Total Profiles:       {results['total']}")
    print(f"Perfect Match (<₹1):  {results['perfect_match']} ({results['perfect_match']/results['total']*100:.1f}%)")
    print(f"Small Error (<₹100):  {results['small_error']} ({results['small_error']/results['total']*100:.1f}%)")
    print(f"Medium Error (<₹1K):  {results['medium_error']} ({results['medium_error']/results['total']*100:.1f}%)")
    print(f"Large Error (>₹1K):   {results['large_error']} ({results['large_error']/results['total']*100:.1f}%)")
    
    print(f"\nBy Regime:")
    print(f"Old Regime Errors:    {len(results['old_regime_errors'])}")
    print(f"New Regime Errors:    {len(results['new_regime_errors'])}")
    
    # Analyze error patterns
    if results["errors"]:
        errors_list = [d["error"] for d in results["errors"]]
        print(f"\nError Statistics:")
        print(f"  Average Error:      ₹{sum(errors_list)/len(errors_list):,.2f}")
        print(f"  Max Error:          ₹{max(errors_list):,.2f}")
        print(f"  Min Error:          ₹{min(errors_list):,.2f}")
        
        # Show first few problematic profiles
        print(f"\n{'='*80}")
        print(f"DETAILED DIAGNOSIS OF FIRST 5 ERRORS")
        print(f"{'='*80}")
        
        for diagnosis in results["errors"][:5]:
            profile = next(p for p in profiles if p["profile_id"] == diagnosis["profile_id"])
            diagnose_single_profile(profile, verbose=True)
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Diagnose discrepancies between ground truth and neuro-symbolic calculations"
    )
    parser.add_argument(
        "--profiles",
        type=str,
        default="experiments/profiles.json",
        help="Path to profiles JSON file"
    )
    parser.add_argument(
        "--max",
        type=int,
        help="Maximum number of profiles to analyze (default: all)"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.profiles)
    if not input_path.exists():
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)
    
    analyze_profiles_file(input_path, args.max)
