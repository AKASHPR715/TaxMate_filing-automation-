# Input Data Structure Guide

## 📥 What `compare_tax_regimes()` Takes as Input

### Function Signature
```python
def compare_tax_regimes(
    extracted_data: dict = None,  # Main input
    include_any_other_deductions: bool = False  # Optional flag
) -> dict:
```

---

## 📋 Expected Input Format

The function expects a **nested dictionary** that mimics **Form 16 Part B** structure:

```python
extracted_data = {
    "16_Part_B": {  # Main form key
        
        # 1️⃣ SALARY DETAILS
        "salary_details": {
            "total_salary": 1200000.0,              # Your gross from current employer
            "salary_from_other_employers": 0.0      # Any previous employer this FY
        },
        
        # 2️⃣ SECTION 10 EXEMPTIONS
        "exemptions_u_s_10": {
            "house_rent_allowance": 150000.0,       # HRA exemption
            "leave_travel_concession": 0.0,         # LTA (rarely used)
            "gratuity": 0.0,                        # For exiting employees
            "leave_encashment": 0.0,                # Unused leave
            "commuted_pension": 0.0,                # For pensioners
            "any_other_exemption": 0.0,             # Misc
            "total_exemptions": 150000.0            # Auto-calculated
        },
        
        # 3️⃣ SECTION 16 DEDUCTIONS (Standard deduction is auto-applied)
        "deductions_u_s_16": {
            "professional_tax": 2500.0              # State professional tax
        },
        
        # 4️⃣ OTHER INCOME
        "other_income_reported": {
            "total_other_income": 25000.0           # Bank interest, dividends, etc.
        },
        
        # 5️⃣ CHAPTER VI-A DEDUCTIONS
        "deductions_chapter_VIA": {
            "section_80C": 150000.0,                # PPF, ELSS, LIC, etc.
            "section_80CCC": 0.0,                   # Pension fund
            "section_80CCD_1": 0.0,                 # NPS (employee)
            "section_80CCD_1B": 50000.0,            # Additional NPS
            "section_80CCD_2": 0.0,                 # NPS (employer) - NOT counted!
            "section_80D": 25000.0,                 # Medical insurance
            "section_80E": 0.0,                     # Education loan
            "section_80G": 0.0,                     # Donations
            "section_80TTA": 10000.0,               # Savings interest
            "any_other_deductions": 0.0             # Usually excluded
        }
    }
}
```

---

## 🔍 What Gets Extracted

The function **parses** this nested structure to extract:

### From `salary_details`:
```python
gross_salary = total_salary + salary_from_other_employers
```

### From `exemptions_u_s_10`:
```python
exemptions_10 = {
    "hra": house_rent_allowance,
    "lta": leave_travel_concession,
    # ... etc
    "total": sum(all_exemptions)
}
```

### From `deductions_chapter_VIA`:
```python
# Validates and caps each section
# 80C+80CCC+80CCD(1) combined max: ₹1.5L
# 80CCD(1B) separate max: ₹50K
# 80D varies by age
```

---

## 📝 Real Example

### Input:
```python
input_data = {
    "16_Part_B": {
        "salary_details": {
            "total_salary": 1200000.0,
            "salary_from_other_employers": 0.0
        },
        "exemptions_u_s_10": {
            "house_rent_allowance": 150000.0,
            "total_exemptions": 150000.0
        },
        "deductions_u_s_16": {
            "professional_tax": 2500.0
        },
        "other_income_reported": {
            "total_other_income": 0.0
        },
        "deductions_chapter_VIA": {
            "section_80C": 150000.0,
            "section_80CCD_1B": 50000.0,
            "section_80D": 25000.0
        }
    }
}

result = compare_tax_regimes(input_data)
```

### Output:
```python
{
    "gross_salary": 1200000.0,
    "section_10_exemptions": {...},
    "ch_via_validated": 225000.0,  # After validation
    
    "old_gti": 1047500.0,
    "old_taxable": 822500.0,
    "old_tax": 86580.00,  # With cess
    
    "new_gti": 1197500.0,
    "new_taxable": 1197500.0,
    "new_tax": 164580.00,  # With cess
    
    "optimal_regime": "OLD",
    "savings": 78000.00,
    
    "validation_warnings": [
        "80C capped from ₹150,000 to ₹150,000",
        # ... other warnings
    ]
}
```

---

## 🔄 How It Flows Through the System

```
1. Form Extraction (PDF/Image) 
   ↓
2. LLM/OCR extracts to structured dict
   ↓
3. compare_tax_regimes(extracted_data)
   ↓
   - Validates all deductions
   - Calculates both regimes
   - Applies tax slabs
   - Adds 4% cess
   ↓
4. Returns comparison result
```

---

## 🎯 For Benchmark (Synthetic Profiles)

In the **benchmark**, the `adapter.py` converts synthetic profiles to this format:

```python
# experiments/execution/adapter.py
def adapt_profile_to_orchestrator(profile: TaxProfile) -> dict:
    # Converts TaxProfile → Form 16 format
    return {
        "16_Part_B": {
            "salary_details": {
                "total_salary": profile.income.gross_salary,
                ...
            },
            ...
        }
    }
```

---

## 💡 Key Points

1. **Format mimics Form 16 Part B** - because that's what the OCR extracts
2. **Nested structure** - organized by tax form sections
3. **All values in ₹** - annual amounts
4. **Validation happens inside** - caps are applied automatically
5. **Professional tax** is under Section 16, not Chapter VI-A
6. **80CCD(2)** (employer NPS) is tracked but NOT counted as deduction

---

## 🚨 Common Mistakes

❌ **Wrong:** Passing flat dict
```python
{"salary": 1200000, "80C": 150000}  # Won't work!
```

✅ **Right:** Nested Form 16 structure
```python
{"16_Part_B": {"salary_details": {...}, "deductions_chapter_VIA": {...}}}
```

❌ **Wrong:** Including employer NPS in total
```python
"section_80CCD_2": 50000  # This gets excluded!
```

✅ **Right:** Understand it's tracked but not counted
```python
# System logs it but doesn't reduce taxable income
```

---

## 📖 Need More Help?

- **See sample data:** Line 550 in `tax_comparison.py`
- **See adapter:** `experiments/execution/adapter.py`
- **See schema:** `experiments/data_generation/schema.py`
