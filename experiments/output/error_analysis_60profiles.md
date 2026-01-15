# Error Profile Analysis: 60 Problematic Cases

**Date:** 2026-01-14  
**Total Error Profiles:** 60 out of 500 (12%)  
**Source File:** `experiments/output/error_profiles_60.json`

---

## 🔍 Critical Finding: 100% Old Regime Errors

### Pattern Discovered

**ALL 60 error profiles share these characteristics:**
- ✅ **Target Regime:** OLD (100% - 60/60)
- ✅ **Complexity:** Medium/Complex (93% Medium, 7% Complex)
- ❌ **New Regime:** 0 errors (0/60)
- ❌ **Simple Cases:** 0 errors in this group

**Conclusion:** The errors are **NOT random** - there's a systematic issue with **Old Regime calculations** in **Medium/Complex profiles**.

---

## Error Statistics

| Metric | Value |
|--------|-------|
| **Total Profiles** | 60 |
| **Min Error** | ₹260 |
| **Max Error** | ₹15,600 |
| **Average Error** | ₹3,987 |

### Error Distribution

| Range | Count | Percentage |
|-------|-------|------------|
| **Medium (₹10-₹1K)** | 8 | 13.3% |
| **Large (₹1K-₹10K)** | 47 | 78.3% |
| **Very Large (>₹10K)** | 5 | 8.3% |

---

## Root Cause Hypothesis

Since ALL errors are in:
1. **Old Regime** profiles
2. **Medium/Complex** cases

The likely culprits are components that only apply to Old Regime + complex scenarios:

### Top Suspects

1. **HRA Exemption Calculation**
   - Only in Old Regime
   - Complex formula with 3 conditions
   - Requires rent paid, basic salary calculation
   - **Most likely cause**

2. **Chapter VI-A Deduction Validation**
   - More complex in Old Regime
   - Multiple sections (80C, 80D, 80CCD, etc.)
   - Cap calculations and interactions
   - **Secondary suspect**

3. **Professional Tax**
   - State-specific variations
   - May differ between ground truth and neuro-symbolic
   - **Minor contributor**

4. **Standard Deduction Application**
   - Old Regime: ₹50,000
   - Should be straightforward
   - **Unlikely cause**

---

## Detailed Investigation Needed

### Compare Ground Truth vs Neuro-Symbolic Logic

For the 60 error profiles, we need to check:

1. **HRA Exemption Formula**
   - Ground truth in `generator.py`
   - Neuro-symbolic in `tax_comparison.py`
   - **Verify:** Basic salary calculation method
   - **Verify:** Rent paid - 10% basic calculation
   - **Verify:** Metro vs non-metro (50% vs 40%)

2. **Chapter VI-A Caps**
   - Section 80C cap: ₹1,50,000
   - Section 80D caps: ₹25,000 (self), ₹50,000 (parents if 60+)
   - Section 80CCD(1B): ₹50,000
   - **Verify:** Ground truth applies same caps

3. **Professional Tax**
   - Check if ₹2,500 constant or variable
   - Verify consistency between systems

---

## Recommended Fix Strategy

### Phase 1: Identify Exact Mismatch (10 min)

1. Pick one error profile (start with max error ₹15,600)
2. Run through both paths manually:
   - Ground truth calculation (from `generator.py`)
   - Neuro-symbolic calculation (from `tax_comparison.py`)
3. Compare step-by-step values
4. Identify the exact line where they diverge

### Phase 2: Common Pattern (20 min)

1. Check 5 random error profiles
2. Verify same issue occurs
3. Confirm hypothesis

### Phase 3: Fix (30 min)

1. Update either `generator.py` or `tax_comparison.py` (whichever is incorrect)
2. Re-run recalculation script on the 60 profiles
3. Verify errors drop to 0

### Phase 4: Validate (10 min)

1. Re-run full 500-profile benchmark
2. Confirm 100% accuracy
3. Update metrics

---

## Expected Outcome

**If hypothesis is correct and we fix HRA/Chapter VI-A:**
- Current: 88% accuracy (440/500)
- After fix: **100% accuracy** (500/500)
- Error drop: From ₹478 mean to **₹0**

---

## Files for Investigation

1. **Error Profiles:** `experiments/output/error_profiles_60.json`
2. **Ground Truth Logic:** `experiments/data_generation/generator.py`
3. **Neuro-Symbolic Logic:** `src/services/tax_comparison.py`
4. **Diagnostic Script:** `experiments/data_generation/simple_diagnose.py`

---

## Next Steps

**Option 1: Automated Analysis**
```bash
# Run diagnostic on first error profile
python3 experiments/data_generation/simple_diagnose.py \
  --profiles experiments/output/error_profiles_60.json \
  --max 1
```

**Option 2: Manual Investigation**
1. Open `error_profiles_60.json`
2. Find profile with max error (₹15,600)
3. Trace through both calculation paths
4. Identify mismatch

**Option 3: Statistical Analysis**
- Look for correlation with:
  - Income levels
  - HRA amounts
  - Deduction amounts
  - Age (senior citizen status)

---

## Confidence Level

**Hypothesis Confidence:** 🟢 **High (85%)**

**Reasoning:**
- 100% of errors in Old Regime = systematic issue
- 0% in New Regime = New Regime logic is correct
- Medium/Complex only = triggered by HRA/deductions
- Bimodal distribution = discrete logic difference

**Most likely:** HRA exemption calculation uses different Basic Salary estimate between ground truth and neuro-symbolic.

---

**Analysis Complete**  
**Generated:** 2026-01-14 17:48  
**Profile Count:** 60  
**Pattern:** Old Regime Medium/Complex only
