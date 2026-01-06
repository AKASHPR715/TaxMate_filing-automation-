# Form 16 Profile Generator - Usage Guide

## 🎯 Purpose

Generates **500 synthetic tax profiles** in the exact **Form 16 Part B format** expected by `compare_tax_regimes()`.

## 📋 Generated File

**Script:** [`generate_form16_profiles.py`](file:///home/akash.prathap@acsiatech.com/Desktop/TaxMate_filing-automation-/experiments/data_generation/generate_form16_profiles.py)

**Output:** `experiments/output/form16_profiles_500_<timestamp>.json`

## 🚀 Usage

### Basic Usage
```bash
# Generate 500 profiles (default)
python3 experiments/data_generation/generate_form16_profiles.py

# Generate custom number
python3 experiments/data_generation/generate_form16_profiles.py --count 1000

# Specify output file
python3 experiments/data_generation/generate_form16_profiles.py --count 500 --output my_profiles.json
```

### View Help
```bash
python3 experiments/data_generation/generate_form16_profiles.py --help
```

## 📊 Output Format

Each profile is a complete Form 16 Part B structure:

```json
{
  "profile_id": "TAX-269A3233",
  "age": 44,
  "complexity": "Medium",
  "target_regime": "New",
  "ground_truth_tax": 24800.0,
  
  "16_Part_B": {
    "salary_details": {
      "total_salary": 723000.0,
      "salary_from_other_employers": 0.0
    },
    
    "exemptions_u_s_10": {
      "house_rent_allowance": 127280.0,  // Calculated per Section 10(13A)
      "leave_travel_concession": 0.0,
      "gratuity": 0.0,
      "leave_encashment": 0.0,
      "commuted_pension": 0.0,
      "any_other_exemption": 0.0,
      "total_exemptions": 127280.0
    },
    
    "deductions_u_s_16": {
      "standard_deduction": 50000.0,     // Auto-applied by system
      "professional_tax": 2500.0         // Based on salary
    },
    
    "other_income_reported": {
      "total_other_income": 0.0,
      "interest_income": 0.0,
      "dividend_income": 0.0
    },
    
    "deductions_chapter_VIA": {
      "section_80C": 150000.0,           // PF + ELSS + LIC + PPF combined
      "section_80CCC": 0.0,
      "section_80CCD_1": 0.0,
      "section_80CCD_1B": 0.0,           // Additional NPS
      "section_80CCD_2": 0.0,            // Employer NPS (excluded)
      "section_80D": 25000.0,            // Medical insurance
      "section_80E": 0.0,
      "section_80G": 0.0,
      "section_80TTA": 0.0,
      "any_other_deductions": 0.0
    },
    
    "assessment_details": {
      "assessment_year": "2024-25",
      "financial_year": "2023-24"
    }
  }
}
```

## ✅ Compatibility

The generated profiles are **100% compatible** with:

1. ✅ `compare_tax_regimes()` - Direct input
2. ✅ `TaxOrchestrator.run_computation_with_data()` - Via orchestrator
3. ✅ Tax calculation pipeline
4. ✅ All validation functions

## 🔧 Implementation Details

### Chapter VI-A Deduction Mapping
**Important:** All 80C components (PF, ELSS, LIC, PPF) are **combined into `section_80C`** field:

```python
total_80c = (pf_contribution + elss + lic_premium + ppf)

"deductions_chapter_VIA": {
    "section_80C": total_80c,  // All components together
    "section_80CCD_1": 0.0,    // Not used separately
    ...
}
```

This matches how `compare_tax_regimes()` validates deductions (combined cap of ₹1.5L).

### HRA Exemption Calculation
Follows **Section 10(13A)** formula:
```python
hra_exempt = min(
    hra_received,                          // Condition 1
    basic * (0.50 if metro else 0.40),    // Condition 2
    rent_paid - (0.10 * basic)            // Condition 3
)
```

### Professional Tax
- Applied if salary > ₹3L
- Fixed at ₹2,500/year (typical for salaried individuals)

## 📈 Distribution (500 Profiles)

**Target Regimes:**
- Old Regime: ~50-52% (250-260 profiles)
- New Regime: ~48-50% (240-250 profiles)

**Complexity:**
- Simple: ~12% (50-70 profiles)
- Medium: ~85% (410-440 profiles)
- Complex: ~3% (10-20 profiles)

**Salary Range:**
- ₹5L - ₹10L: ~40%
- ₹10L - ₹20L: ~35%
- ₹20L - ₹50L: ~20%
- ₹50L+: ~5%

## 🔍 Features

### 1. Complete Field Coverage
All fields required by `compare_tax_regimes()`:
- ✅ Salary details
- ✅ Section 10 exemptions (calculated HRA)
- ✅ Section 16 deductions
- ✅ Other income
- ✅ Chapter VI-A deductions
- ✅ Assessment year details

### 2. Realistic Data
- Log-normal salary distribution
- Proper HRA exemption calculation
- Professional tax based on salary
- 80C components split correctly
- Age-appropriate deductions

### 3. Ground Truth Included
Each profile has:
- `ground_truth_tax` - Pre-calculated using production tax logic
- `target_regime` - Which regime to evaluate
- Metadata for analysis (age, complexity)

## 💻 Using Generated Profiles

### Load and Test
```python
import json
from src.services.tax_comparison import compare_tax_regimes

# Load profiles
with open('experiments/output/form16_profiles_500_*.json') as f:
    profiles = json.load(f)

# Test with one profile
profile = profiles[0]
result = compare_tax_regimes(profile['16_Part_B'])

print(f"Old Tax: ₹{result['old_tax']:,.2f}")
print(f"New Tax: ₹{result['new_tax']:,.2f}")
print(f"Optimal: {result['optimal_regime']}")
```

### Batch Processing
```python
for profile in profiles:
    result = compare_tax_regimes(profile['16_Part_B'])
    
    # Compare with ground truth
    if profile['target_regime'] == 'Old':
        calculated = result['old_tax']
    else:
        calculated = result['new_tax']
    
    error = abs(calculated - profile['ground_truth_tax'])
    print(f"{profile['profile_id']}: Error = ₹{error:,.2f}")
```

### Filter by Criteria
```python
# Get only complex profiles
complex_profiles = [p for p in profiles if p['complexity'] == 'Complex']

# Get high-income profiles
high_income = [p for p in profiles 
               if p['16_Part_B']['salary_details']['total_salary'] > 2000000]

# Get profiles with HRA
hra_profiles = [p for p in profiles 
                if p['16_Part_B']['exemptions_u_s_10']['house_rent_allowance'] > 0]
```

## 🎯 Next Steps

After generating profiles, you can:

1. **Validate System:** Run all 500 through `compare_tax_regimes()` to verify logic
2. **Benchmark LLMs:** Compare system vs LLM predictions
3. **Find Edge Cases:** Identify profiles where system struggles
4. **Statistical Analysis:** Analyze tax distribution patterns

## 📝 Example: Full Validation Script

```python
import json
from src.services.tax_comparison import compare_tax_regimes

# Load profiles
with open('experiments/output/form16_profiles_500_*.json') as f:
    profiles = json.load(f)

errors = []
for profile in profiles:
    result = compare_tax_regimes(profile['16_Part_B'])
    
    # Extract result for target regime
    if profile['target_regime'] == 'Old':
        calculated = result['old_tax']
    else:
        calculated = result['new_tax']
    
    # Calculate error
    error = abs(calculated - profile['ground_truth_tax'])
    errors.append({
        'profile_id': profile['profile_id'],
        'ground_truth': profile['ground_truth_tax'],
        'calculated': calculated,
        'error': error
    })

# Statistics
avg_error = sum(e['error'] for e in errors) / len(errors)
max_error = max(errors, key=lambda x: x['error'])

print(f"Average Error: ₹{avg_error:,.2f}")
print(f"Max Error: ₹{max_error['error']:,.2f} (Profile: {max_error['profile_id']})")
```

## 🚨 Important Notes

### ⚠️ Ground Truth Limitation
**CRITICAL:** The ground truth is calculated using the **same `tax_comparison.py` logic** as TaxMate's neuro-symbolic system.

**What This Means:**
- ✅ Validates **data transformation** and **workflow**
- ✅ Tests if Form 16 format is processed correctly
- ❌ Does NOT validate **tax calculation accuracy**
- ❌ If there's a bug in `tax_comparison.py`, both ground truth AND neuro-symbolic will be wrong

**For True Validation:**
To verify your tax calculations are actually correct:
1. Use **official Income Tax Department calculator** as ground truth
2. Get **Chartered Accountant verification** for sample cases
3. Use **third-party calculators** (ClearTax, ETMoney) for cross-validation
4. Implement **independent tax calculation** from scratch using Income Tax Act

### Other Notes
- **Random Seed:** Not set - each run generates different profiles
- **File Size:** 500 profiles ≈ 1.5-2 MB JSON
- **Generation Time:** ~2-3 seconds
- **Deduction Mapping:** All 80C components combined in `section_80C` field

## 🔗 Related Files

- Generation Logic: [`experiments/data_generation/generator.py`](file:///home/akash.prathap@acsiatech.com/Desktop/TaxMate_filing-automation-/experiments/data_generation/generator.py)
- Tax Comparison: [`src/services/tax_comparison.py`](file:///home/akash.prathap@acsiatech.com/Desktop/TaxMate_filing-automation-/src/services/tax_comparison.py)
- Input Format Guide: [`docs/INPUT_STRUCTURE.md`](file:///home/akash.prathap@acsiatech.com/Desktop/TaxMate_filing-automation-/docs/INPUT_STRUCTURE.md)
