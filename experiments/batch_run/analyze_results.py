#!/usr/bin/env python3
"""
Analyze benchmark results and generate IEEE paper tables
"""
import pandas as pd
import numpy as np
from pathlib import Path

def calculate_accuracy(df, error_col, threshold=10):
    """Calculate exact match accuracy within threshold"""
    return (df[error_col] <= threshold).mean() * 100

def calculate_mae(df, error_col):
    """Calculate Mean Absolute Error"""
    return df[error_col].mean()

def analyze_results():
    results_file = Path("results/final_benchmark_500.csv")
    
    if not results_file.exists():
        print("❌ final_benchmark_500.csv not found")
        print("Run merge_results.py first")
        return
    
    df = pd.read_csv(results_file)
    
    print("=" * 80)
    print("BENCHMARK RESULTS ANALYSIS")
    print("=" * 80)
    
    # Overall Statistics
    print(f"\nDataset Size: {len(df)} profiles")
    print(f"\nComplexity Distribution:")
    print(df['complexity'].value_counts())
    print(f"\nRegime Distribution:")
    print(df['regime'].value_counts())
    
    # Accuracy by System
    print("\n" + "=" * 80)
    print("TABLE I: ARITHMETIC PERFORMANCE COMPARISON")
    print("=" * 80)
    
    systems = {
        'Neuro-Symbolic': 'neuro_error',
        'Zero-Shot (GPT-4o-mini)': 'zs_error',
        'Chain-of-Thought (GPT-4o-mini)': 'cot_error'
    }
    
    results = []
    for name, error_col in systems.items():
        accuracy = calculate_accuracy(df, error_col)
        mae = calculate_mae(df, error_col)
        results.append({
            'System': name,
            'Accuracy (%)': f"{accuracy:.1f}%",
            'MAE (₹)': f"₹{mae:,.2f}"
        })
    
    results_df = pd.DataFrame(results)
    print(results_df.to_string(index=False))
    
    # Breakdown by Complexity
    print("\n" + "=" * 80)
    print("ACCURACY BY COMPLEXITY TIER")
    print("=" * 80)
    
    for complexity in ['Simple', 'Medium', 'Complex']:
        subset = df[df['complexity'] == complexity]
        if len(subset) == 0:
            continue
        
        print(f"\n{complexity} ({len(subset)} profiles):")
        for name, error_col in systems.items():
            acc = calculate_accuracy(subset, error_col)
            print(f"  {name}: {acc:.1f}%")
    
    # Breakdown by Regime
    print("\n" + "=" * 80)
    print("ACCURACY BY TAX REGIME")
    print("=" * 80)
    
    for regime in ['Old', 'New']:
        subset = df[df['regime'] == regime]
        if len(subset) == 0:
            continue
        
        print(f"\n{regime} Regime ({len(subset)} profiles):")
        for name, error_col in systems.items():
            acc = calculate_accuracy(subset, error_col)
            mae = calculate_mae(subset, error_col)
            print(f"  {name}: {acc:.1f}% accuracy, ₹{mae:,.2f} MAE")
    
    # Error Magnitude Analysis
    print("\n" + "=" * 80)
    print("TABLE III: ERROR MAGNITUDE ANALYSIS")
    print("=" * 80)
    
    def error_buckets(errors):
        return {
            '0-100': (errors <= 100).sum(),
            '101-500': ((errors > 100) & (errors <= 500)).sum(),
            '501-1000': ((errors > 500) & (errors <= 1000)).sum(),
            '1001-5000': ((errors > 1000) & (errors <= 5000)).sum(),
            '>5000': (errors > 5000).sum()
        }
    
    for name, error_col in systems.items():
        buckets = error_buckets(df[error_col])
        print(f"\n{name}:")
        for bucket, count in buckets.items():
            pct = count / len(df) * 100
            print(f"  ₹{bucket}: {count} ({pct:.1f}%)")
    
    # Save detailed report
    report_file = Path("results/analysis_report.md")
    with open(report_file, 'w') as f:
        f.write("# TaxMate Benchmark Analysis Report\n\n")
        f.write(f"**Dataset**: {len(df)} profiles\n\n")
        f.write("## Overall Performance\n\n")
        f.write(results_df.to_markdown(index=False))
        f.write("\n\n## Key Findings\n\n")
        
        ns_acc = calculate_accuracy(df, 'neuro_error')
        zs_acc = calculate_accuracy(df, 'zs_error')
        cot_acc = calculate_accuracy(df, 'cot_error')
        
        f.write(f"1. **Neuro-Symbolic**: Achieved {ns_acc:.1f}% accuracy\n")
        f.write(f"2. **Zero-Shot LLM**: Achieved {zs_acc:.1f}% accuracy ({ns_acc - zs_acc:.1f}% gap)\n")
        f.write(f"3. **Chain-of-Thought**: Achieved {cot_acc:.1f}% accuracy ({ns_acc - cot_acc:.1f}% gap)\n")
    
    print(f"\n✅ Detailed report saved to: {report_file}")
    print("=" * 80)

if __name__ == "__main__":
    analyze_results()
