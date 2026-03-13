# TaxMate 500-Profile Benchmark Results

**Date:** 2026-03-13  
**Profiles Analyzed:** 500  
**Financial Year:** FY 2024-25 (AY 2025-26)  
**Approach:** Neuro-Symbolic (Rule-Based)

> All metrics are **programmatically computed** using `experiments/execution/runner.py` with numpy statistics.

---

## Executive Summary

🏆 **Overall Performance:** The TaxMate neuro-symbolic system achieves **100% exact match accuracy** on 500 diverse synthetic tax profiles, with **₹0 mean error**, **₹0 median error**, and **0 slab hallucinations**. This result follows the resolution of two systematic bugs:
1. **HRA Adapter Bug** — `adapter.py` was not passing `salary_breakdown` and `rent_details` to the engine.
2. **Section 80D Cap Bug** — The engine applied a single ₹25,000 cap on combined self+parent medical insurance, violating IT Act rules (separate caps apply).

### Key Findings

| Metric | Value | Grade |
|--------|-------|-------|
| **Exact Match Accuracy (EMA)** | 100.0% (500/500) | 🟢 Perfect |
| **Mean Absolute Error (MAE)** | ₹0.00 | 🟢 Perfect |
| **Median Error** | ₹0.00 | 🟢 Perfect |
| **Std Deviation** | ₹0.00 | 🟢 Perfect |
| **Slab Hallucination Rate** | 0.0% (0 profiles) | 🟢 Perfect |
| **Large Errors (>₹1K)** | 0.0% (0 profiles) | 🟢 Perfect |

---

## Detailed Metrics

### 1. Exact Match Accuracy (EMA)

| Approach | Accuracy |
|----------|----------|
| **Neuro-Symbolic (TaxMate)** | **100.0%** (500/500) |
| Zero-Shot LLM (mock baseline) | ~1.0% |
| Chain-of-Thought LLM (mock baseline) | ~1.4% |

### 2. Error Statistics

| Statistic | Value |
|-----------|-------|
| **Mean (MAE)** | ₹0.00 |
| **Median** | ₹0.00 |
| **Std Deviation** | ₹0.00 |
| **Min** | ₹0.00 |
| **Max** | ₹0.00 |

### 3. Relative Error

| Metric | Value |
|--------|-------|
| **Mean Relative Error** | 0.00% |
| **Median Relative Error** | 0.00% |
| **Std Dev Relative Error** | 0.00% |

### 4. Slab Hallucination Rate

- **Count:** 0 profiles
- **Rate:** 0.0%

### 5. Error Magnitude Distribution

| Error Range | Count | % |
|-------------|-------|---|
| **Perfect (<₹10)** | 500 | 100.0% ✅ |
| Small (₹10–₹100) | 0 | 0.0% |
| Medium (₹100–₹1K) | 0 | 0.0% |
| Large (₹1K–₹10K) | 0 | 0.0% |
| Very Large (>₹10K) | 0 | 0.0% |

---

## Breakdown by Regime

| Regime | Count | Accuracy | MAE |
|--------|-------|----------|-----|
| **Old Regime** | 222 | **100.0%** ✅ | ₹0.00 |
| **New Regime** | 278 | **100.0%** ✅ | ₹0.00 |

---

## Breakdown by Complexity

| Complexity | Count | Accuracy | MAE |
|------------|-------|----------|-----|
| **Simple** | 73 | **100.0%** ✅ | ₹0.00 |
| **Medium** | 416 | **100.0%** ✅ | ₹0.00 |
| **Complex** | 11 | **100.0%** ✅ | ₹0.00 |

---

## Bug History & Resolution

| Bug | Root Cause | Fix Applied |
|-----|-----------|-------------|
| HRA Exemption (12% error) | `adapter.py` missing `salary_breakdown` + `rent_details` fields | Added fields to pass basic salary, HRA received, rent paid, metro status |
| Section 80D Cap (25% Old Regime error) | Engine used single ₹25K cap on combined self+parents instead of separate caps | Rewrote `validate_80d()` to apply independent ₹25K (self) + ₹25K/₹50K (parents) caps per IT Act |

---

## Production Readiness

### Current Status: ✅ **FULLY PRODUCTION-READY**

| Dimension | Status |
|-----------|--------|
| New Regime taxpayers | ✅ 100% accuracy |
| Old Regime – Simple | ✅ 100% accuracy |
| Old Regime – Medium | ✅ 100% accuracy |
| Old Regime – Complex | ✅ 100% accuracy |
| Slab Hallucinations | ✅ Zero |
| Academic Publication | ✅ Ready |

---

## Files Generated

All results saved in `experiments/output/`:

1. `benchmark_20260313_<ts>.csv` — Full per-profile results
2. `detailed_log_20260313_<ts>.json` — Per-profile computation trace
3. `readable_log_20260313_<ts>.txt` — Human-readable log
4. `synthetic_profiles_20260313_<ts>.json` — Generated profile inputs
5. `final_metrics_500profiles_<ts>.json` — All computed statistics (JSON)

---

**Report Generated:** 2026-03-13  
**Total Profiles:** 500  
**System:** TaxMate Neuro-Symbolic FY 2024-25
