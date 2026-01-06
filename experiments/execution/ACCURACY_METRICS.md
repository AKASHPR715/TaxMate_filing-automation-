# Accuracy Calculation Methodology

## How Accuracy is Determined

The benchmark uses **two complementary metrics** to evaluate model performance:

### 1. **Exact Match Accuracy** (within ₹10 threshold)

**Formula:**
```python
accuracy = (count of predictions within ₹10 of ground truth) / total predictions
```

**Code Implementation:**
```python
ns_acc = sum(1 for r in results if r["neuro_error"] <= 10) / len(results)
```

**What it means:**
- A prediction is considered "correct" if it's within ₹10 of the actual tax amount
- This is a strict metric focusing on near-perfect predictions
- Expressed as percentage (0% to 100%)

**Example:**
```
Ground Truth: ₹50,000
Prediction: ₹50,005 → ✅ MATCH (error = ₹5)
Prediction: ₹50,015 → ❌ NO MATCH (error = ₹15)
```

---

### 2. **Average Absolute Error** (MAE)

**Formula:**
```python
average_error = sum(|prediction - ground_truth|) / total predictions
```

**Code Implementation:**
```python
# Store individual errors
neuro_error = abs(neuro_tax - ground_truth)

# Calculate average
avg_error = sum(r["neuro_error"] for r in results) / len(results)
```

**What it means:**
- Average deviation from the correct tax amount
- Lower is better (₹0 would be perfect)
- Gives you the typical error magnitude
- Expressed in rupees (₹)

**Example:**
```
Profile 1: Error = ₹100
Profile 2: Error = ₹200  
Profile 3: Error = ₹50

Average Error = (100 + 200 + 50) / 3 = ₹116.67
```

---

## Ground Truth Calculation

The "correct answer" is calculated using the **exact same tax computation logic** as the neuro-symbolic system, applied to the synthetic profile data:

```python
def _calculate_ground_truth(self, profile: TaxProfile) -> float:
    if profile.target_regime == "Old":
        # Old regime: Apply exemptions + deductions + slabs
        taxable = (gross - exemptions - std_deduction - chapter_via_deductions)
        return old_regime_tax(taxable)
    else:
        # New regime: Only standard deduction, no chapter VI-A
        taxable = (gross - std_deduction)
        return new_regime_tax(taxable)
```

This uses the **proven tax_comparison.py** logic with correct FY 2023-24 slabs.

---

## Why Two Metrics?

### Exact Match (within ₹10)
- ✅ **Pros**: Strict quality bar, matches real-world expectations
- ❌ **Cons**: Harsh penalty for small errors, doesn't show "how wrong"

### Average Error
- ✅ **Pros**: Shows magnitude of errors, more forgiving
- ❌ **Cons**: Doesn't capture "how often perfect"

**Together they tell the complete story:**
- High exact match + Low average error = **Excellent** ⭐⭐⭐⭐⭐
- Low exact match + Low average error = **Consistent but slightly off** ⭐⭐⭐⭐
- Low exact match + High average error = **Unreliable** ⭐

---

## Example Results Interpretation

```
Exact Match Accuracy (within ₹10):
  Neuro-Symbolic:     92.0%
  Zero-Shot LLM:      54.0%
  Chain-of-Thought:   68.0%

Average Error:
  Neuro-Symbolic:    ₹      245.50
  Zero-Shot LLM:     ₹    8,423.20
  Chain-of-Thought:  ₹    3,156.80
```

**Analysis:**

**Neuro-Symbolic (92% / ₹245)**
- Gets 92 out of 100 predictions within ₹10 (excellent!)
- When it's wrong, typical error is only ₹245 (very small)
- **Grade: A+ ⭐⭐⭐⭐⭐**

**Chain-of-Thought (68% / ₹3,157)**
- Gets 68 out of 100 exactly right
- Average mistake is ₹3,157 (acceptable for complex cases)
- **Grade: B+ ⭐⭐⭐⭐**

**Zero-Shot (54% / ₹8,423)**
- Only 54% accuracy - coin flip
- Very large errors averaging ₹8,423
- **Grade: C ⭐⭐**

---

## Per-Profile Metrics

Each profile also gets:

### Error Percentage
```python
error_percentage = (abs(prediction - ground_truth) / ground_truth) * 100
```

**Example:**
```
Ground Truth: ₹10,000
Prediction: ₹11,000
Error Percentage = (1,000 / 10,000) * 100 = 10%
```

This shows **relative error** which is useful when tax amounts vary widely (₹5K vs ₹500K).

---

## Stored Metrics (in JSON logs)

For each model prediction:
```json
{
  "prediction": 7800.00,
  "error": 1550.00,              // Absolute error in ₹
  "error_percentage": 24.80,      // Relative error %
  "status": "success"
}
```

This allows post-hoc analysis like:
- Error distribution by complexity category
- Median vs mean errors
- Error correlation with income levels
- Worst-case error bounds

---

## Summary

| Metric | Formula | Good Value | Bad Value |
|--------|---------|------------|-----------|
| **Exact Match** | Count within ₹10 / Total | >90% | <50% |
| **Avg Error** | Mean abs difference | <₹500 | >₹10,000 |
| **Error %** | Error / Ground Truth | <5% | >20% |
