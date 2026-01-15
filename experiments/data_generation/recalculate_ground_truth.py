#!/usr/bin/env python3
"""
Recalculate ground truth for profiles in Form 16 Part B format
using the EXACT same logic as tax_comparison.py (FY 2024-25).
"""
import json
import sys
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from src.services.tax_comparison import compare_tax_regimes


def recalculate_ground_truth_form16(profile_dict: dict) -> float:
    """
    Recalculate ground truth using tax_comparison.py.
    Profile is in Form 16 Part B format.
    """
    target_regime = profile_dict["target_regime"]
    
    # Create extracted_data
    extracted_data = {
        "16_Part_B": profile_dict["16_Part_B"]
    }
    
    # Run through tax comparison (this uses FY 2024-25 logic)
    result = compare_tax_regimes(extracted_data=extracted_data)
    
    # Return tax based on target regime
    if target_regime == "Old":
        return result["old_tax"]
    else:
        return result["new_tax"]


def recalculate_all_profiles(input_file: Path, output_file: Path = None):
    """Recalculate ground truth for all profiles"""
    
    if not output_file:
        # Create backup
        backup_file = input_file.with_suffix('.json.backup2')
        if not backup_file.exists():
            # Only backup if not already backed up
            import shutil
            shutil.copy(input_file, backup_file)
            print(f"📦 Created backup: {backup_file}")
        output_file = input_file
    
    print(f"📂 Loading profiles from: {input_file}")
    with open(input_file, 'r') as f:
        profiles = json.load(f)
    
    print(f"✅ Loaded {len(profiles)} profiles")
    print(f"🔄 Recalculating ground truth using FY 2024-25 logic...\n")
    
    stats = {
        "total": 0,
        "old_regime": 0,
        "new_regime": 0,
        "total_old_tax": 0.0,
        "total_new_tax": 0.0
    }
    
    for i, profile in enumerate(profiles, 1):
        old_ground_truth = profile.get("ground_truth_tax", 0)
        new_ground_truth = recalculate_ground_truth_form16(profile)
        
        # Update the profile
        profile["ground_truth_tax"] = new_ground_truth
        
        # Track stats
        stats["total"] += 1
        if profile["target_regime"] == "Old":
            stats["old_regime"] += 1
            stats["total_old_tax"] += new_ground_truth
        else:
            stats["new_regime"] += 1
            stats["total_new_tax"] += new_ground_truth
        
        # Progress
        if i % 50 == 0:
            print(f"   Processed {i}/{len(profiles)} profiles...")
    
    # Save
    print(f"\n💾 Saving updated profiles to: {output_file}")
    with open(output_file, 'w') as f:
        json.dump(profiles, f, indent=2)
    
    print(f"\n✅ SUCCESS! Recalculated {stats['total']} profiles")
    print(f"\n📊 Statistics:")
    print(f"   Old Regime profiles: {stats['old_regime']}")
    print(f"     Average tax: ₹{stats['total_old_tax']/stats['old_regime']:,.2f}" if stats['old_regime'] > 0 else "")
    print(f"   New Regime profiles: {stats['new_regime']}")
    print(f"     Average tax: ₹{stats['total_new_tax']/stats['new_regime']:,.2f}" if stats['new_regime'] > 0 else "")
    print(f"\n✨ Output file: {output_file}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str)
    parser.add_argument("--output", type=str, help="Output file (default: overwrites input)")
    
    args = parser.parse_args()
    
    input_path = Path(args.input_file)
    output_path = Path(args.output) if args.output else None
    
    if not input_path.exists():
        print(f"❌ Error: File not found: {input_path}")
        sys.exit(1)
    
    recalculate_all_profiles(input_path, output_path)
