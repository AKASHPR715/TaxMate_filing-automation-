#!/usr/bin/env python3
"""
Merge all batch CSV results into a single file
"""
import pandas as pd
import glob
from pathlib import Path

def merge_batch_results():
    results_dir = Path("results")
    
    # Find all batch CSV files
    batch_files = sorted(glob.glob(str(results_dir / "batch_*_benchmark.csv")))
    
    if not batch_files:
        print("❌ No batch result files found in results/")
        print("Make sure you've run at least one batch first")
        return
    
    print(f"Found {len(batch_files)} batch files:")
    for f in batch_files:
        print(f"  - {Path(f).name}")
    
    # Merge all CSVs
    dfs = []
    for file in batch_files:
        df = pd.read_csv(file)
        dfs.append(df)
    
    merged_df = pd.concat(dfs, ignore_index=True)
    
    # Save merged results
    output_file = results_dir / "final_benchmark_500.csv"
    merged_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Merged {len(merged_df)} profiles")
    print(f"📊 Saved to: {output_file}")
    
    # Quick stats
    print(f"\nQuick Stats:")
    print(f"  Total Profiles: {len(merged_df)}")
    print(f"  Complexity Breakdown:")
    print(merged_df['complexity'].value_counts().to_string())
    print(f"\n  Regime Distribution:")
    print(merged_df['regime'].value_counts().to_string())
    
    return merged_df

if __name__ == "__main__":
    merge_batch_results()
