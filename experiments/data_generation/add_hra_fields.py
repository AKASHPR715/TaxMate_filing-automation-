#!/usr/bin/env python3
"""
Add salary_breakdown and rent_details to existing profiles.json
for robust HRA calculation
"""
import json
import shutil
from pathlib import Path

def update_profiles_with_new_fields(profiles_file: str):
    """Add salary_breakdown and rent_details to existing profiles"""
    
    # Load existing profiles
    print(f"Loading {profiles_file}...")
    with open(profiles_file) as f:
        profiles = json.load(f)
    
    print(f"Loaded {len(profiles)} profiles")
    
    # Create backup
    backup_file = f"{profiles_file}.backup_prehra"
    shutil.copy(profiles_file, backup_file)
    print(f"Created backup: {backup_file}")
    
    # Update each profile
    updated_count = 0
    for profile in profiles:
        form16 = profile.get("16_Part_B", {})
        
        # Check if already has new fields
        if "salary_breakdown" in form16:
            continue
        
        # Get salary details
        salary_details = form16.get("salary_details", {})
        gross = salary_details.get("total_salary", 0)
        
        # Get exemptions
        exemptions = form16.get("exemptions_u_s_10", {})
        hra_value = exemptions.get("house_rent_allowance", 0)
        
        # Estimate basic salary (40% of gross is common)
        # This is a reasonable heuristic
        basic = gross * 0.40
        
        # Estimate rent from HRA exemption (rough reverse calculation)
        # If HRA exemption is significant, assume rent was paid
        is_metro = False  # Conservative estimate
        if hra_value > 0:
            # Rough estimate: if HRA exemption exists, estimate rent
            # Assume non-metro (40% rule) and work backwards
            rent = max(0, hra_value + (basic * 0.10))
        else:
            rent = 0
        
        # Add salary_breakdown
        form16["salary_breakdown"] = {
            "basic_salary": basic,
            "hra": hra_value if hra_value > 0 else gross * 0.20,  # Estimate HRA as 20% of gross if not exempt
            "special_allowance": gross - basic - (hra_value if hra_value > 0 else gross * 0.20)
        }
        
        # Add rent_details  
        form16["rent_details"] = {
            "annual_rent_paid": rent,
            "is_metro_city": is_metro
        }
        
        updated_count += 1
    
    # Save updated profiles
    print(f"\nUpdated {updated_count} profiles with new fields")
    print(f"Saving to {profiles_file}...")
    
    with open(profiles_file, 'w') as f:
        json.dump(profiles, f, indent=2)
    
    print(f"✅ Successfully updated profiles!")
    print(f"\nNote: Basic salary and rent are ESTIMATED from existing data.")
    print(f"For accurate testing, regenerate profiles or use known test data.")
    
    return updated_count

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--profiles", default="experiments/profiles.json",
                        help="Path to profiles.json file")
    
    args = parser.parse_args()
    
    update_profiles_with_new_fields(args.profiles)
