#!/usr/bin/env python3
"""
Deep diagnostic for Old Regime errors.
Runs a fresh batch of profiles and traces exactly where the calculation diverges
for each error profile: what ground truth expects vs what the neuro-symbolic engine calculates.
"""
import sys
import os
import json

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
if project_root not in sys.path:
    sys.path.append(project_root)

# Mock heavy dependencies
from unittest.mock import MagicMock
sys.modules["llama_cloud_services"] = MagicMock()
sys.modules["services.form_extraction"] = MagicMock()
sys.modules["src.services.form_extraction"] = MagicMock()
sys.modules["langchain_classic"] = MagicMock()
sys.modules["langchain_classic.agents"] = MagicMock()
sys.modules["services.tax_advisor"] = MagicMock()
sys.modules["src.services.tax_advisor"] = MagicMock()
sys.modules["services.form_generation"] = MagicMock()
sys.modules["src.services.form_generation"] = MagicMock()

from experiments.data_generation.generator import TaxProfileGenerator
from experiments.execution.adapter import adapt_profile_to_orchestrator, calculate_hra_exemption
from experiments.data_generation.constants import SECTION_80C_LIMIT, OLD_REGIME_STANDARD_DEDUCTION
from src.services.orchestrator import TaxOrchestrator
from src.services.tax_comparison import old_regime_tax, apply_cess

print("=" * 80)
print("OLD REGIME ERROR DIAGNOSTIC")
print("=" * 80)

gen = TaxProfileGenerator()
error_profiles = []

# Generate until we have 200 Old Regime profiles, or enough for analysis
profiles_checked = 0
old_regime_total = 0
error_count = 0
BATCH = 300

profiles = gen.generate_batch(BATCH)

for profile in profiles:
    if profile.target_regime != "Old":
        continue
    old_regime_total += 1

    input_data = adapt_profile_to_orchestrator(profile)
    orchestrator = TaxOrchestrator()
    orchestrator.run_computation_with_data(input_data)
    res = orchestrator.state["computation_result"]
    neuro_tax = res.get("old_tax", -1.0)
    gt = profile.ground_truth_tax
    err = abs(neuro_tax - gt)

    if err > 10:
        error_count += 1
        inc = profile.income
        ded = profile.deductions

        # Manually trace the ground truth deduction steps
        hra_gt = gen._calculate_hra_exemption(inc.basic_salary, inc.hra_received, ded.rent_paid_annual, ded.is_metro_city)
        total_80c_gt = min(ded.pf_contribution + ded.elss + ded.lic_premium + ded.ppf, SECTION_80C_LIMIT)
        total_80d_gt = ded.medical_insurance_self + ded.medical_insurance_parents
        prof_tax_gt  = 2500.0 if inc.gross_salary > 300000 else 0.0
        sec_80tta_gt = min(inc.other_sources_income, 10000.0)

        taxable_gt   = max(0, inc.gross_salary + inc.other_sources_income - OLD_REGIME_STANDARD_DEDUCTION - prof_tax_gt - hra_gt - total_80c_gt - total_80d_gt - sec_80tta_gt)
        tax_check    = apply_cess(old_regime_tax(taxable_gt))

        # Trace what neuro-symbolic got
        ns_hra    = res["section_10_exemptions"]["hra"]
        ns_ch_via = res["ch_via_validated"]
        ns_gti    = res["old_gti"]
        ns_taxable= res["old_taxable"]
        ns_prof   = res["professional_tax"]

        # Differences
        hra_diff = hra_gt - ns_hra
        ch_via_gt = total_80c_gt + total_80d_gt + sec_80tta_gt
        ch_via_diff = ch_via_gt - ns_ch_via

        error_profiles.append({
            "profile_id": profile.profile_id,
            "complexity": profile.complexity_category,
            "gross": inc.gross_salary,
            "basic": inc.basic_salary,
            "hra_received": inc.hra_received,
            "rent_paid": ded.rent_paid_annual,
            "is_metro": ded.is_metro_city,
            "other_income": inc.other_sources_income,
            "ground_truth_tax": round(gt, 2),
            "neuro_sym_tax": round(neuro_tax, 2),
            "error": round(err, 2),
            "trace": {
                "hra_exemption_gt": round(hra_gt, 2),
                "hra_exemption_ns": round(ns_hra, 2),
                "hra_diff": round(hra_diff, 2),
                "prof_tax_gt": prof_tax_gt,
                "prof_tax_ns": round(ns_prof, 2),
                "chapterVIA_gt": round(ch_via_gt, 2),
                "chapterVIA_ns": round(ns_ch_via, 2),
                "chapterVIA_diff": round(ch_via_diff, 2),
                "taxable_income_gt": round(taxable_gt, 2),
                "taxable_income_ns": round(ns_taxable, 2),
                "taxable_diff": round(taxable_gt - ns_taxable, 2),
            }
        })

# Print summary
print(f"\nProfiles generated:   {BATCH}")
print(f"Old Regime:           {old_regime_total}")
print(f"Old Regime errors:    {error_count}  ({error_count/old_regime_total*100:.1f}%)")

# Categorise errors
hra_errors   = [e for e in error_profiles if abs(e["trace"]["hra_diff"]) > 1]
ch_via_errs  = [e for e in error_profiles if abs(e["trace"]["chapterVIA_diff"]) > 1]
prof_errs    = [e for e in error_profiles if abs(e["trace"]["prof_tax_gt"] - e["trace"]["prof_tax_ns"]) > 1]
taxable_errs = [e for e in error_profiles if abs(e["trace"]["taxable_diff"]) > 1]

print(f"\n--- Root Cause Breakdown (error profiles = {len(error_profiles)}) ---")
print(f"  HRA mismatch:              {len(hra_errors)} ({len(hra_errors)/max(len(error_profiles),1)*100:.0f}%)")
print(f"  Chapter VI-A mismatch:     {len(ch_via_errs)} ({len(ch_via_errs)/max(len(error_profiles),1)*100:.0f}%)")
print(f"  Prof Tax mismatch:         {len(prof_errs)} ({len(prof_errs)/max(len(error_profiles),1)*100:.0f}%)")
print(f"  Taxable Income mismatch:   {len(taxable_errs)} ({len(taxable_errs)/max(len(error_profiles),1)*100:.0f}%)")

print(f"\n--- Top 5 Errors (by error magnitude) ---")
for ep in sorted(error_profiles, key=lambda x: x["error"], reverse=True)[:5]:
    t = ep["trace"]
    print(f"\nProfile: {ep['profile_id']}  Complexity: {ep['complexity']}")
    print(f"  Gross: Rs {ep['gross']:,.0f}  Basic: Rs {ep['basic']:,.0f}  HRA Rcvd: Rs {ep['hra_received']:,.0f}")
    print(f"  Rent: Rs {ep['rent_paid']:,.0f}  Metro: {ep['is_metro']}")
    print(f"  GT Tax:   Rs {ep['ground_truth_tax']:,.2f}  |  NS Tax: Rs {ep['neuro_sym_tax']:,.2f}  |  Error: Rs {ep['error']:,.2f}")
    print(f"  HRA Exemption   -> GT: Rs {t['hra_exemption_gt']:,.2f}  NS: Rs {t['hra_exemption_ns']:,.2f}  Diff: Rs {t['hra_diff']:,.2f}")
    print(f"  Chapter VI-A    -> GT: Rs {t['chapterVIA_gt']:,.2f}  NS: Rs {t['chapterVIA_ns']:,.2f}  Diff: Rs {t['chapterVIA_diff']:,.2f}")
    print(f"  Prof Tax        -> GT: Rs {t['prof_tax_gt']:,.2f}  NS: Rs {t['prof_tax_ns']:,.2f}")
    print(f"  Taxable Income  -> GT: Rs {t['taxable_income_gt']:,.2f}  NS: Rs {t['taxable_income_ns']:,.2f}  Diff: Rs {t['taxable_diff']:,.2f}")

# Save diagnosis to JSON
out_path = os.path.join(current_dir, "output", "old_regime_diagnosis.json")
with open(out_path, "w") as f:
    json.dump({
        "summary": {
            "batch": BATCH,
            "old_regime_total": old_regime_total,
            "error_count": error_count,
            "error_rate": round(error_count / max(old_regime_total, 1), 4),
            "hra_mismatch": len(hra_errors),
            "chapterVIA_mismatch": len(ch_via_errs),
            "prof_tax_mismatch": len(prof_errs),
        },
        "error_profiles": error_profiles
    }, f, indent=2)

print(f"\nFull diagnosis saved to: {out_path}")
