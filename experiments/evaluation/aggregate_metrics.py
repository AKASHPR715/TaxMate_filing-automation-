#!/usr/bin/env python3
"""
Aggregate and Calculate Comprehensive Metrics from Benchmark Results
Supports evaluation of neuro-symbolic vs LLM approaches
"""
import json
import sys
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


def load_results(results_file: str) -> List[Dict]:
    """Load benchmark results from JSON"""
    with open(results_file, 'r') as f:
        data = json.load(f)
    
    # Handle different JSON structures
    if isinstance(data, list):
        return data
    elif isinstance(data, dict) and 'profiles' in data:
        return data['profiles']
    else:
        return data


def calculate_metrics(profiles: List[Dict], approach_key: str) -> Dict[str, Any]:
    """Calculate comprehensive metrics for one approach"""
    
    errors = []
    relative_errors = []
    slab_hallucinations = 0
    total_valid = 0
    exact_matches = 0
    
    error_buckets = {
        'perfect': 0,      # <₹10
        'small': 0,        # ₹10-₹100
        'medium': 0,       # ₹100-₹1000
        'large': 0,        # ₹1000-₹10000
       'very_large': 0    # >₹10000
    }
    
    for profile in profiles:
        # Get ground truth
        gt = profile.get('input_profile', {}).get('ground_truth_tax')
        if gt is None:
            gt = profile.get('ground_truth_tax', 0)
        
        # Get prediction based on approach
        models = profile.get('models', {})
        if approach_key == 'neuro_symbolic':
            pred_data = models.get('neuro_symbolic', {})
        elif approach_key == 'zero_shot':
            pred_data = models.get('zero_shot', {})
        elif approach_key == 'chain_of_thought':
            pred_data = models.get('chain_of_thought', {})
        else:
            continue
        
        if not pred_data or pred_data.get('status') != 'success':
            continue
        
        pred = pred_data.get('prediction', -1)
        if pred < 0:
            continue
        
        total_valid += 1
        error = abs(pred - gt)
        errors.append(error)
        
        # Relative error
        if gt > 0:
            rel_err = (error / gt) * 100
            relative_errors.append(rel_err)
            
            # Slab hallucination (error > 50% of true value)
            if rel_err > 50:
                slab_hallucinations += 1
        
        # Exact match
        if error < 10:
            exact_matches += 1
        
        # Error distribution
        if error < 10:
            error_buckets['perfect'] += 1
        elif error < 100:
            error_buckets['small'] += 1
        elif error < 1000:
            error_buckets['medium'] += 1
        elif error < 10000:
            error_buckets['large'] += 1
        else:
            error_buckets['very_large'] += 1
    
    if total_valid == 0:
        return {"error": "No valid predictions", "total_valid": 0}
    
    return {
        "total_valid_predictions": total_valid,
        "1_exact_match_accuracy_EMA": {
            "count": exact_matches,
            "percentage": (exact_matches / total_valid) * 100,
            "threshold": "< ₹10"
        },
        "2_mean_absolute_error_MAE": {
            "mean": float(np.mean(errors)),
            "median": float(np.median(errors)),
            "std_dev": float(np.std(errors)),
            "min": float(np.min(errors)),
            "max": float(np.max(errors))
        },
        "3_relative_error": {
            "mean_percentage": float(np.mean(relative_errors)) if relative_errors else 0,
            "median_percentage": float(np.median(relative_errors)) if relative_errors else 0,
            "std_dev": float(np.std(relative_errors)) if relative_errors else 0
        },
        "4_slab_hallucination_rate": {
            "count": slab_hallucinations,
            "percentage": (slab_hallucinations / total_valid) * 100,
            "definition": "Predictions with >50% error (likely wrong tax slab)"
        },
        "5_error_magnitude_distribution": {
            "perfect_<10": {
                "count": error_buckets['perfect'],
                "percentage": (error_buckets['perfect'] / total_valid) * 100
            },
            "small_10-100": {
                "count": error_buckets['small'],
                "percentage": (error_buckets['small'] / total_valid) * 100
            },
            "medium_100-1000": {
                "count": error_buckets['medium'],
                "percentage": (error_buckets['medium'] / total_valid) * 100
            },
            "large_1000-10000": {
                "count": error_buckets['large'],
                "percentage": (error_buckets['large'] / total_valid) * 100
            },
            "very_large_>10000": {
                "count": error_buckets['very_large'],
                "percentage": (error_buckets['very_large'] / total_valid) * 100
            }
        }
    }


def generate_report(results_file: str, output_file: str = None):
    """Generate comprehensive metrics report"""
    
    print(f"\n{'='*80}")
    print(f"LOADING BENCHMARK RESULTS")
    print(f"{'='*80}")
    print(f"File: {results_file}\n")
    
    profiles = load_results(results_file)
    print(f"✅ Loaded {len(profiles)} profiles\n")
    
    # Calculate metrics for each approach
    metrics = {
        "source_file": results_file,
        "total_profiles": len(profiles),
        "approaches": {}
    }
    
    for approach_name, approach_key in [
        ("Neuro-Symbolic (Rule-Based)", "neuro_symbolic"),
        ("Zero-Shot LLM", "zero_shot"),
        ("Chain-of-Thought LLM", "chain_of_thought")
    ]:
        print(f"Calculating metrics for: {approach_name}...")
        result = calculate_metrics(profiles, approach_key)
        metrics["approaches"][approach_name] = result
    
    # Save to JSON
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"\n✅ Saved metrics to: {output_file}")
    
    # Print summary report
    print(f"\n{'='*80}")
    print(f"COMPREHENSIVE EVALUATION METRICS REPORT")
    print(f"{'='*80}\n")
    
    for approach_name, data in metrics["approaches"].items():
        if "error" in data:
            print(f"\n{approach_name}:")
            print(f"  ❌ {data['error']}")
            continue
        
        print(f"\n{approach_name}:")
        print(f"  Total Valid Predictions: {data['total_valid_predictions']}")
        
        # EMA
        ema = data['1_exact_match_accuracy_EMA']
        print(f"\n  1. EXACT MATCH ACCURACY (EMA):")
        print(f"     {ema['percentage']:.2f}% ({ema['count']}/{data['total_valid_predictions']} profiles)")
        
        # MAE
        mae = data['2_mean_absolute_error_MAE']
        print(f"\n  2. MEAN ABSOLUTE ERROR (MAE):")
        print(f"     Mean:   ₹{mae['mean']:,.2f}")
        print(f"     Median: ₹{mae['median']:,.2f}")
        print(f"     Range:  ₹{mae['min']:,.2f} - ₹{mae['max']:,.2f}")
        
        # Relative Error
        rel = data['3_relative_error']
        print(f"\n  3. RELATIVE ERROR:")
        print(f"     Mean:   {rel['mean_percentage']:.2f}%")
        print(f"     Median: {rel['median_percentage']:.2f}%")
        
        # Slab Hallucination
        slab = data['4_slab_hallucination_rate']
        print(f"\n  4. SLAB HALLUCINATION RATE:")
        print(f"     {slab['percentage']:.2f}% ({slab['count']} profiles)")
        
        # Error Distribution
        dist = data['5_error_magnitude_distribution']
        print(f"\n  5. ERROR MAGNITUDE DISTRIBUTION:")
        for category, info in dist.items():
            print(f"     {category.ljust(20)}: {info['count']:3d} ({info['percentage']:5.1f}%)")
    
    print(f"\n{'='*80}\n")
    return metrics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Calculate comprehensive evaluation metrics from benchmark results"
    )
    parser.add_argument("results_file", help="Path to detailed_log_*.json file")
    parser.add_argument("--output", "-o", help="Output file for metrics JSON (optional)")
    
    args = parser.parse_args()
    
    if not Path(args.results_file).exists():
        print(f"❌ Error: File not found: {args.results_file}")
        sys.exit(1)
    
    generate_report(args.results_file, args.output)
