#!/usr/bin/env python3
"""
Generates 500 synthetic tax profiles in Form 16 Part B format.
Output is directly compatible with compare_tax_regimes() function.
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from experiments.data_generation.generator import TaxProfileGenerator

def calculate_hra_exemption(basic: float, hra_received: float, rent_paid: float, is_metro: bool) -> float:
    """Calculate HRA exemption per Income Tax Act."""
    if rent_paid <= 0:
        return 0.0
    
    limit1 = hra_received
    limit2 = basic * (0.50 if is_metro else 0.40)
    limit3 = max(0, rent_paid - (0.10 * basic))
    
    return min(limit1, limit2, limit3)

def convert_to_form16_format(profile) -> dict:
    """
    Convert TaxProfile to Form 16 Part B format expected by compare_tax_regimes().
    """
    # Calculate HRA exemption
    hra_exempt = calculate_hra_exemption(
        profile.income.basic_salary,
        profile.income.hra_received,
        profile.deductions.rent_paid_annual,
        profile.deductions.is_metro_city
    )
    
    # Calculate total 80C components
    total_80c = (
        profile.deductions.pf_contribution +
        profile.deductions.elss +
        profile.deductions.lic_premium +
        profile.deductions.ppf
    )
    
    # Build Form 16 structure
    form16_data = {
        "profile_id": profile.profile_id,
        "age": profile.age,
        "complexity": profile.complexity_category,
        "target_regime": profile.target_regime,
        # ground_truth_tax removed - will be calculated by validation system
        
        # Form 16 Part B structure
        "16_Part_B": {
            # 1. Salary Details
            "salary_details": {
                "total_salary": profile.income.gross_salary,
                "salary_from_other_employers": 0.0  # Assuming single employer
            },
            
            # 1a. Salary Breakdown (for HRA calculation)
            "salary_breakdown": {
                "basic_salary": profile.income.basic_salary,
                "hra": profile.income.hra_received,
                "special_allowance": profile.income.special_allowance
            },
            
            # 1b. Rent Details (for HRA calculation)
            "rent_details": {
                "annual_rent_paid": profile.deductions.rent_paid_annual,
                "is_metro_city": profile.deductions.is_metro_city
            },
            
            # 2. Section 10 Exemptions
            "exemptions_u_s_10": {
                "house_rent_allowance": hra_exempt,
                "leave_travel_concession": 0.0,
                "gratuity": 0.0,
                "leave_encashment": 0.0,
                "commuted_pension": 0.0,
                "any_other_exemption": 0.0,
                "total_exemptions": hra_exempt
            },
            
            # 3. Section 16 Deductions (Professional Tax)
            "deductions_u_s_16": {
                "standard_deduction": 75000.0,  # FY 2024-25 standard deduction
                "professional_tax": 2500.0 if profile.income.gross_salary > 300000 else 0.0
            },
            
            # 4. Other Income
            "other_income_reported": {
                "total_other_income": profile.income.other_sources_income,
                "interest_income": profile.income.other_sources_income,
                "dividend_income": 0.0
            },
            
            # 5. Chapter VI-A Deductions
            "deductions_chapter_VIA": {
                # 80C components (PF goes in 80C, rest in 80CCD_1)
               "section_80C": total_80c,  # All 80C components combined
                "section_80CCC": 0.0,
                "section_80CCD_1": 0.0,  # Moved to 80C above
                "section_80CCD_1B": 0.0,  # Additional NPS
                "section_80CCD_2": 0.0,   # Employer NPS (not a deduction!)
                "section_80D": profile.deductions.medical_insurance_self + profile.deductions.medical_insurance_parents,
                "section_80E": 0.0,       # Education loan
                "section_80G": 0.0,       # Donations
                "section_80TTA": min(profile.income.other_sources_income, 10000.0) if profile.income.other_sources_income > 0 else 0.0,
                "any_other_deductions": 0.0
            },
            
            # 6. Assessment Details (for FY determination)
            "assessment_details": {
                "assessment_year": "2025-26",
                "financial_year": "2024-25"
            }
        }
    }
    
    return form16_data

def generate_profiles(count: int = 500, output_file: str = None):
    """Generate tax profiles and save to JSON."""
    print(f"🔄 Generating {count} synthetic tax profiles...")
    
    # Generate profiles using existing generator
    generator = TaxProfileGenerator()
    profiles = generator.generate_batch(count)
    
    print(f"✅ Generated {len(profiles)} raw profiles")
    print(f"🔄 Converting to Form 16 Part B format...")
    
    # Convert to Form 16 format
    form16_profiles = []
    for i, profile in enumerate(profiles, 1):
        if i % 50 == 0:
            print(f"   Processed {i}/{count} profiles...")
        form16_data = convert_to_form16_format(profile)
        form16_profiles.append(form16_data)
    
    # Determine output file
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"form16_profiles_{count}_{timestamp}.json"
    else:
        output_file = Path(output_file)
        output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Save to JSON
    print(f"💾 Saving to {output_file}...")
    with open(output_file, 'w') as f:
        json.dump(form16_profiles, f, indent=2)
    
    print(f"✅ Successfully saved {len(form16_profiles)} profiles!")
    
    # Print statistics
    print(f"\n📊 Profile Statistics:")
    print(f"   Total Profiles: {len(form16_profiles)}")
    
    regimes = {"Old": 0, "New": 0}
    complexity = {"Simple": 0, "Medium": 0, "Complex": 0}
    
    for p in form16_profiles:
        regimes[p["target_regime"]] += 1
        complexity[p["complexity"]] += 1
    
    print(f"   Target Regimes:")
    print(f"     - Old: {regimes['Old']} ({regimes['Old']/len(form16_profiles)*100:.1f}%)")
    print(f"     - New: {regimes['New']} ({regimes['New']/len(form16_profiles)*100:.1f}%)")
    
    print(f"   Complexity:")
    print(f"     - Simple:  {complexity['Simple']} ({complexity['Simple']/len(form16_profiles)*100:.1f}%)")
    print(f"     - Medium:  {complexity['Medium']} ({complexity['Medium']/len(form16_profiles)*100:.1f}%)")
    print(f"     - Complex: {complexity['Complex']} ({complexity['Complex']/len(form16_profiles)*100:.1f}%)")
    
    # Sample profile preview
    print(f"\n📋 Sample Profile (first one):")
    print(json.dumps(form16_profiles[0], indent=2)[:500] + "...")
    
    print(f"\n✨ Output file: {output_file}")
    return str(output_file)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate synthetic tax profiles in Form 16 Part B format"
    )
    parser.add_argument(
        "--count", 
        type=int, 
        default=500,
        help="Number of profiles to generate (default: 500)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output JSON file path (default: auto-generated with timestamp)"
    )
    
    args = parser.parse_args()
    
    generate_profiles(args.count, args.output)
