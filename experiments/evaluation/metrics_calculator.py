#!/usr/bin/env python3
"""
Advanced Evaluation Metrics Calculator for Tax Computation Benchmark
Calculates comprehensive metrics for comparing neuro-symbolic vs LLM approaches
"""
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class BenchmarkEvaluator:
    """Calculate comprehensive evaluation metrics from benchmark results"""
    
    def __init__(self, results_file: str):
        """Load benchmark results from JSON"""
        with open(results_file, 'r') as f:
            self.data = json.load(f)
        
        self.profiles = self.data.get('profiles', [])
        self.metadata = self.data.get('metadata', {})
    
    def calculate_all_metrics(self) -> Dict[str, Any]:
        """Calculate all evaluation metrics"""
        
        metrics = {
            'metadata': self.metadata,
            'neuro_symbolic': self._calculate_metrics('neuro_symbolic'),
            'zero_shot_llm': self._calculate_metrics('zero_shot_llm'),
            'chain_of_thought_llm': self._calculate_metrics('cot_llm'),
            'comparison': self._calculate_comparative_metrics()
        }
        
        return metrics
    
    def _calculate_metrics(self, approach: str) -> Dict[str, Any]:
        """Calculate metrics for a specific approach"""
        
        errors = []
        relative_errors = []
        exact_matches = 0
        total = 0
        
        slab_errors = 0
        regime_errors = 0
        
        error_buckets = {
            'perfect': 0,      # <₹10
            'small': 0,        # ₹10-₹100
            'medium': 0,       # ₹100-₹1000
            'large': 0,        # ₹1000-₹10000
            'very_large': 0    # >₹10000
        }
        
        for profile in self.profiles:
            ground_truth = profile['ground_truth_tax']
            
            # Get prediction based on approach
            if approach == 'neuro_symbolic':
                predicted = profile.get('neuro_symbolic_tax', 0)
            elif approach == 'zero_shot_llm':
                predicted = profile.get('zero_shot_tax', 0)
            elif approach == 'cot_llm':
                predicted = profile.get('cot_tax', 0)
            else:
                continue
            
            # Skip if prediction failed (negative value indicates error)
            if predicted < 0:
                continue
            
            total += 1
            error = abs(predicted - ground_truth)
            errors.append(error)
            
            # Relative error (percentage)
            if ground_truth > 0:
                rel_error = (error / ground_truth) * 100
                relative_errors.append(rel_error)
            
            # Exact match (within ₹10 threshold)
            if error < 10:
                exact_matches += 1
            
            # Error magnitude distribution
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
            
            # Slab hallucination detection (large deviations suggest wrong slab)
            if ground_truth > 0 and (error / ground_truth) > 0.5:
                slab_errors += 1
            
            # Regime confusion (check if output suggests wrong regime)
            # This would need more context from LLM outputs
            # Placeholder for now
        
        if total == 0:
            return {"error": "No valid predictions"}
        
        return {
            "total_profiles": total,
            "exact_match_accuracy": {
                "count": exact_matches,
                "percentage": (exact_matches / total) * 100
            },
            "mean_absolute_error": {
                "value": np.mean(errors),
                "median": np.median(errors),
                "std_dev": np.std(errors),
                "min": np.min(errors),
                "max": np.max(errors)
            },
            "relative_error": {
                "mean_percentage": np.mean(relative_errors) if relative_errors else 0,
                "median_percentage": np.median(relative_errors) if relative_errors else 0,
                "std_dev": np.std(relative_errors) if relative_errors else 0
            },
            "error_distribution": {
                "perfect_<10": {
                    "count": error_buckets['perfect'],
                    "percentage": (error_buckets['perfect'] / total) * 100
                },
                "small_10-100": {
                    "count": error_buckets['small'],
                    "percentage": (error_buckets['small'] / total) * 100
                },
                "medium_100-1000": {
                    "count": error_buckets['medium'],
                    "percentage": (error_buckets['medium'] / total) * 100
                },
                "large_1000-10000": {
                    "count": error_buckets['large'],
                    "percentage": (error_buckets['large'] / total) * 100
                },
                "very_large_>10000": {
                    "count": error_buckets['very_large'],
                    "percentage": (error_buckets['very_large'] / total) * 100
                }
            },
            "slab_hallucination_rate": {
                "count": slab_errors,
                "percentage": (slab_errors / total) * 100
            }
        }
    
    def _calculate_comparative_metrics(self) -> Dict[str, Any]:
        """Calculate comparison metrics between approaches"""
        
        neuro_better = 0
        zero_shot_better = 0
        cot_better = 0
        total = 0
        
        for profile in self.profiles:
            gt = profile['ground_truth_tax']
            neuro = profile.get('neuro_symbolic_tax', -1)
            zero = profile.get('zero_shot_tax', -1)
            cot = profile.get('cot_tax', -1)
            
            if neuro < 0 or zero < 0 or cot < 0:
                continue
            
            total += 1
            
            neuro_err = abs(neuro - gt)
            zero_err = abs(zero - gt)
            cot_err = abs(cot - gt)
            
            min_err = min(neuro_err, zero_err, cot_err)
            
            if neuro_err == min_err:
                neuro_better += 1
            if zero_err == min_err:
                zero_shot_better += 1
            if cot_err == min_err:
                cot_better += 1
        
        return {
            "total_comparisons": total,
            "neuro_symbolic_wins": {
                "count": neuro_better,
                "percentage": (neuro_better / total * 100) if total > 0 else 0
            },
            "zero_shot_wins": {
                "count": zero_shot_better,
                "percentage": (zero_shot_better / total * 100) if total > 0 else 0
            },
            "chain_of_thought_wins": {
                "count": cot_better,
                "percentage": (cot_better / total * 100) if total > 0 else 0
            }
        }
    
    def generate_report(self, output_file: str = None):
        """Generate comprehensive evaluation report"""
        
        metrics = self.calculate_all_metrics()
        
        # Save JSON
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(metrics, f, indent=2)
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE EVALUATION METRICS")
        print("="*80)
        
        for approach_name, approach_key in [
            ("Neuro-Symbolic", "neuro_symbolic"),
            ("Zero-Shot LLM", "zero_shot_llm"),
            ("Chain-of-Thought LLM", "chain_of_thought_llm")
        ]:
            if approach_key not in metrics or 'error' in metrics[approach_key]:
                continue
            
            data = metrics[approach_key]
            
            print(f"\n{approach_name}:")
            print(f"  Total Profiles: {data['total_profiles']}")
            print(f"  Exact Match Accuracy: {data['exact_match_accuracy']['percentage']:.2f}% ({data['exact_match_accuracy']['count']} profiles)")
            print(f"  Mean Absolute Error: ₹{data['mean_absolute_error']['value']:,.2f}")
            print(f"  Median Absolute Error: ₹{data['mean_absolute_error']['median']:,.2f}")
            print(f"  Relative Error: {data['relative_error']['mean_percentage']:.2f}%")
            print(f"  Slab Hallucination Rate: {data['slab_hallucination_rate']['percentage']:.2f}%")
            
            print(f"\n  Error Distribution:")
            for category, info in data['error_distribution'].items():
                print(f"    {category}: {info['count']} ({info['percentage']:.1f}%)")
        
        # Comparison
        if 'comparison' in metrics:
            comp = metrics['comparison']
            print(f"\n" + "="*80)
            print("COMPARATIVE ANALYSIS")
            print("="*80)
            print(f"  Neuro-Symbolic Wins: {comp['neuro_symbolic_wins']['percentage']:.1f}%")
            print(f"  Zero-Shot Wins: {comp['zero_shot_wins']['percentage']:.1f}%")
            print(f"  Chain-of-Thought Wins: {comp['chain_of_thought_wins']['percentage']:.1f}%")
        
        print("\n" + "="*80)
        
        return metrics


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("results_file", help="Path to benchmark results JSON")
    parser.add_argument("--output", help="Output file for metrics JSON")
    
    args = parser.parse_args()
    
    evaluator = BenchmarkEvaluator(args.results_file)
    evaluator.generate_report(args.output)
