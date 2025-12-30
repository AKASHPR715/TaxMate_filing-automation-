import sys
import os
import json
from experiments.data_generation.generator import TaxProfileGenerator

def run_sanity_check():
    print("Initializing Generator...")
    gen = TaxProfileGenerator()
    
    print("Generating 5 profiles...")
    profiles = gen.generate_batch(5)
    
    output_dir = "experiments/output"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sanity_check_samples.json")
    
    # Convert to list of dicts
    data = [p.model_dump() for p in profiles]
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved {len(profiles)} profiles to {output_path}")
    
    # Basic Validation
    for i, p in enumerate(profiles):
        print(f"\nProfile {i+1}: {p.profile_id}")
        print(f"  Gross: {p.income.gross_salary}")
        print(f"  Regime: {p.target_regime}")
        print(f"  Ground Truth Tax: {p.ground_truth_tax}")
        
        if p.ground_truth_tax is None or p.ground_truth_tax < 0:
            print("  [ERROR] Invalid Ground Truth Tax!")
            sys.exit(1)
            
    print("\nSanity Check Passed!")

if __name__ == "__main__":
    run_sanity_check()
