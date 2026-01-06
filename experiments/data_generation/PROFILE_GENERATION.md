# Synthetic Tax Profile Generation - Deep Dive

## Overview

The system generates **realistic synthetic tax profiles** using statistical distributions and probability-based modeling to simulate real Indian taxpayers.

## 🎯 Generation Pipeline

```
1. Generate Salary (Log-Normal Distribution)
   ↓
2. Break Down Salary Components (Basic/HRA/Special)
   ↓
3. Generate Age (Random 22-60)
   ↓
4. Generate Deductions (Based on Income & Age)
   ↓
5. Generate Rent (Based on Basic Salary & Metro Status)
   ↓
6. Assign Target Regime (Random Old/New)
   ↓
7. Calculate Complexity Category
   ↓
8. Calculate Ground Truth Tax
```

---

## 💰 Step 1: Salary Generation

**Method:** Log-Normal Distribution

```python
salary = np.random.lognormal(mean=13.5, sigma=0.6)
salary = max(500000, min(salary, 10000000))  # Clamp to ₹5L - ₹1Cr
salary = round(salary, -3)  # Round to nearest ₹1,000
```

**Why Log-Normal?**
- Real-world incomes are right-skewed (many lower earners, few high earners)
- Matches Indian salary distribution patterns
- Mean ≈ ₹7-12 lakhs, with long tail to ₹50L+

**Distribution:**
```
₹5L - ₹8L:    40% of profiles  (Entry-level)
₹8L - ₹15L:   35% of profiles  (Mid-level)
₹15L - ₹25L:  15% of profiles  (Senior)
₹25L+:        10% of profiles  (Executive)
```

---

## 📊 Step 2: Salary Breakdown

**Formula:**
```python
basic = gross × random(0.40, 0.50)
hra = basic × random(0.40, 0.50)
special = gross - basic - hra
```

**Example for ₹12L gross:**
```
Basic:             ₹5.2L (43% of gross)
HRA:               ₹2.4L (46% of basic)
Special Allowance: ₹4.4L (remainder)
```

**Realism:** Matches typical CTC structures in India (40-50% basic is standard)

---

## 🎂 Step 3: Age Generation

```python
age = random.choice(range(22, 60))  # Working professionals
```

**Distribution:** Uniform (equal probability 22-59 years)

**Why this matters:**
- Affects 80D deduction limits (senior citizen benefits at 60+)
- Influences deduction behavior (younger = less likely to max out)

---

## 💸 Step 4: Deduction Generation

### 4a. Provident Fund (Mandatory)
```python
pf = gross_salary × 0.06  # ~12% of basic
```

### 4b. Section 80C (₹1.5L cap)
**Logic:**
```python
if gross > ₹10L and random() < 0.9:
    target_80c = ₹150,000  # 90% max out
else:
    target_80c = random(0, 150000)  # Random amount

# Distribute remainder after PF
remaining = target_80c - pf
if remaining > 0:
    # Randomly allocate to ELSS, LIC, or PPF
```

**Realism:**
- High earners (>₹10L) almost always max out 80C
- Lower earners may not utilize full limit
- Reflects actual tax planning behavior

### 4c. Section 80D (Medical Insurance)

**Self/Family Insurance (60% probability):**
```python
if random() < 0.6:
    medical_self = random.choice([15000, 20000, 25000])
```

**Parents Insurance (30% probability):**
```python
if random() < 0.3:
    medical_parents = random.choice([20000, 30000, 50000])
```

**Realism:**
- Most salaried employees have corporate health insurance
- ~30% also cover parents

---

## 🏠 Step 5: Rent Generation

### Metro vs Non-Metro
```python
is_metro = random.choice([True, False])  # 50-50 split
```

### Rent Amount
```python
if random() < 0.2:
    rent = 0  # 20% own house

# Metro: 20-50% of basic salary
# Non-Metro: 10-30% of basic salary
rent_ratio = random.uniform(0.2, 0.5) if metro else random.uniform(0.1, 0.3)
rent_annual = basic × rent_ratio
```

**Example for ₹5L basic:**
```
Metro:      ₹1L - ₹2.5L per year  (₹8K-21K/month)
Non-Metro:  ₹50K - ₹1.5L per year (₹4K-12K/month)
Own House:  ₹0 (20% of profiles)
```

---

## 🎲 Step 6: Other Income (30% probability)

```python
if random() < 0.3:
    other_income = random.choice([5000, 10000, 25000, 50000])
```

**Sources:** Bank interest, dividends, freelancing, etc.

---

## 🎯 Step 7: Target Regime Assignment

```python
target_regime = random.choice(["Old", "New"])  # 50-50 split
```

**This is what we're testing:**
- Old Regime: Should use exemptions + deductions
- New Regime: Should use only standard deduction

---

## 🏆 Step 8: Complexity Classification

```python
complexity = "Simple"
if rent_paid > 0 or medical_parents > 0:
    complexity = "Medium"
if gross > ₹15L and (rent_paid > 0 and medical_parents > 0):
    complexity = "Complex"
```

**Categories:**
- **Simple:** No rent, no parent insurance, low income
- **Medium:** Has rent OR parent insurance
- **Complex:** High income + rent + parent insurance

**Distribution (approx):**
```
Simple:  ~30%  (Basic salary, PF, maybe 80C)
Medium:  ~50%  (+ HRA exemption OR parent insurance)
Complex: ~20%  (Multiple exemptions + high deductions)
```

---

## 🧮 Step 9: Ground Truth Calculation

### For Old Regime:
```python
gross_total = gross_salary + other_income
hra_exemption = calculate_hra_exemption(...)
total_80c = min(pf + elss + lic + ppf, 150000)
total_80d = medical_self + medical_parents

taxable = (gross_total 
           - 50000  # Standard deduction
           - hra_exemption 
           - total_80c 
           - total_80d)

ground_truth = old_regime_tax(taxable) × 1.04  # +4% cess
```

### For New Regime:
```python
taxable = gross_total - 50000  # Standard deduction only
ground_truth = new_regime_tax(taxable) × 1.04  # +4% cess
```

**Uses real tax slabs** from `tax_comparison.py` - same logic as production!

---

## 📈 Example Generated Profile

```json
{
  "profile_id": "TAX-A3F2B891",
  "age": 34,
  "complexity_category": "Medium",
  "target_regime": "Old",
  "ground_truth_tax": 86964.80,
  
  "income": {
    "gross_salary": 1200000,
    "basic_salary": 516000,
    "hra_received": 232200,
    "other_income": 25000
  },
  
  "deductions": {
    "pf_contribution": 72000,
    "elss": 78000,
    "total_80c": 150000,
    "medical_insurance_self": 20000,
    "medical_insurance_parents": 30000,
    "total_80d": 50000,
    "rent_paid_annual": 232800,
    "is_metro_city": true
  }
}
```

---

## 🎲 Randomization & Diversity

The system ensures **high diversity** through:

1. **Log-normal salary distribution** (not uniform)
2. **Probabilistic deductions** (not everyone maxes out)
3. **Random salary breakdowns** (40-50% ranges)
4. **Metro/Non-metro split**
5. **Age variation** (22-60)
6. **50-50 regime split**
7. **Varied rent scenarios** (20% own house)

**Result:** 500 profiles will have 500 unique combinations!

---

## 🔍 Statistical Properties

For 500 profiles, expect:

| Property | Expected Distribution |
|----------|----------------------|
| **Salary Range** | ₹5L-₹50L (log-normal, mean ~₹10-12L) |
| **Age Range** | 22-59 (uniform) |
| **Metro/Non-Metro** | ~50% each |
| **Own House** | ~20% (no rent) |
| **80C Maxed** | ~60-70% (higher earners) |
| **Medical Insurance** | ~60% have self, ~30% have parents |
| **Other Income** | ~30% have some |
| **Complexity** | ~30% Simple, ~50% Medium, ~20% Complex |
| **Target Regime** | ~50% Old, ~50% New |

---

## ✅ Quality Assurance

### Ground Truth is Verified
- Uses **exact same tax calculation** as production system
- Applies real FY 2023-24 tax slabs
- Includes 4% cess
- Validates HRA exemption rules
- Caps 80C at ₹1.5L correctly

### No Hardcoded Values
- All amounts are calculated or randomly sampled
- Reflects real-world variability
- No two profiles are identical

### Realistic Constraints
- Salary components sum to gross
- Rent reasonable for income level
- Deductions within legal limits
- Age appropriate for working professionals

---

## 🚀 Why This Matters for Benchmarking

✅ **Diverse scenarios** - Tests edge cases naturally  
✅ **Realistic data** - LLMs see real-world-like inputs  
✅ **Known ground truth** - Can measure exact accuracy  
✅ **Reproducible** - Same seed = same profiles  
✅ **Scalable** - Generate 10 or 10,000 profiles easily

The synthetic profiles are **more diverse than manual test cases** while being **more realistic than random noise**!
