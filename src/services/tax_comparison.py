#!/usr/bin/env python3
"""
Tax Comparison Service
Calculates tax liability under Old and New regimes using extracted rules.
"""
import json
import sys
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler

# Add src to path
current_dir = Path(__file__).resolve().parent
src_dir = current_dir.parent
if str(src_dir) not in sys.path:
    sys.path.append(str(src_dir))

try:
    from core.constants import NEW_REGIME_SLABS, OLD_REGIME_SLABS, STD_DEDUCTION_NEW, STD_DEDUCTION_OLD
except ImportError:
    from src.core.constants import NEW_REGIME_SLABS, OLD_REGIME_SLABS, STD_DEDUCTION_NEW, STD_DEDUCTION_OLD

# ============================================================
# Logging Configuration
# ============================================================
def setup_comparison_logger():
    """Set up logging for tax comparison."""
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "tax_comparison.log"
    
    logger = logging.getLogger("tax_comparison")
    logger.setLevel(logging.INFO)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        fh = RotatingFileHandler(
            log_file, 
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=2,
            encoding="utf-8"
        )
        fh.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(fh)
        
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter("COMPARE: %(message)s"))
        logger.addHandler(ch)
    
    return logger

comparison_logger = setup_comparison_logger()

# ============================================================
# Tax Calculation Logic
# ============================================================

def calculate_tax(income: float, slabs: dict) -> float:
    """
    Generic tax calculator based on slabs.
    Slabs dict format: {tax_rate: upper_limit}
    Note: For simplicity in this demo, we use the specific functions below
    which map exactly to the Indian Tax Regime rules.
    """
    pass 

def old_regime_tax(income: float) -> float:
    """Calculates tax liability under the old income tax regime."""
    if income <= 250_000:
        return 0
    elif income <= 500_000:
        return (income - 250_000) * 0.05
    elif income <= 1_000_000:
        return 12_500 + (income - 500_000) * 0.20
    else:
        return 112_500 + (income - 1_000_000) * 0.30

def explain_old_regime_tax(income: float) -> list:
    """Generates a breakdown of the old regime tax calculation."""
    breakdown = []
    
    # Slab 1: 0 - 2.5L
    s1_limit = 250_000
    s1_tax = 0
    breakdown.append(f"0 - {s1_limit:,}: 0 (Exempt)")
    
    remaining = income - s1_limit
    if remaining <= 0:
        return breakdown
        
    # Slab 2: 2.5L - 5L @ 5%
    s2_limit = 250_000 # width
    taxable_s2 = min(remaining, s2_limit)
    tax_s2 = taxable_s2 * 0.05
    breakdown.append(f"2,50,001 - 5,00,000 (@5%): {tax_s2:,.2f} (on {taxable_s2:,.2f})")
    
    remaining -= s2_limit
    if remaining <= 0:
        return breakdown

    # Slab 3: 5L - 10L @ 20%
    s3_limit = 500_000 # width
    taxable_s3 = min(remaining, s3_limit)
    tax_s3 = taxable_s3 * 0.20
    breakdown.append(f"5,00,001 - 10,00,000 (@20%): {tax_s3:,.2f} (on {taxable_s3:,.2f})")
    
    remaining -= s3_limit
    if remaining <= 0:
        return breakdown
        
    # Slab 4: > 10L @ 30%
    tax_s4 = remaining * 0.30
    breakdown.append(f"> 10,00,000 (@30%): {tax_s4:,.2f} (on {remaining:,.2f})")
    
    return breakdown

def new_regime_tax(inc: float) -> float:
    """New regime tax – FY 2025-26 slabs."""
    if inc <= 300_000:
        return 0.0
    if inc <= 700_000:
        return (inc - 300_000) * 0.05
    if inc <= 1_000_000:
        return 20_000 + (inc - 700_000) * 0.10
    if inc <= 1_200_000:
        return 50_000 + (inc - 1_000_000) * 0.15
    if inc <= 1_500_000:
        return 80_000 + (inc - 1_200_000) * 0.20
    return 140_000 + (inc - 1_500_000) * 0.30

def explain_new_regime_tax(inc: float) -> list:
    """Generates a breakdown of the new regime tax calculation."""
    breakdown = []
    
    # Slab 1: 0 - 3L
    s1_limit = 300_000
    breakdown.append(f"0 - {s1_limit:,}: 0 (Exempt)")
    
    remaining = inc - s1_limit
    if remaining <= 0:
        return breakdown
        
    # Slab 2: 3L - 7L @ 5%
    s2_width = 400_000
    taxable_s2 = min(remaining, s2_width)
    tax_s2 = taxable_s2 * 0.05
    breakdown.append(f"3,00,001 - 7,00,000 (@5%): {tax_s2:,.2f} (on {taxable_s2:,.2f})")
    
    remaining -= s2_width
    if remaining <= 0:
        return breakdown
        
    # Slab 3: 7L - 10L @ 10%
    s3_width = 300_000
    taxable_s3 = min(remaining, s3_width)
    tax_s3 = taxable_s3 * 0.10
    breakdown.append(f"7,00,001 - 10,00,000 (@10%): {tax_s3:,.2f} (on {taxable_s3:,.2f})")
    
    remaining -= s3_width
    if remaining <= 0:
        return breakdown

    # Slab 4: 10L - 12L @ 15%
    s4_width = 200_000
    taxable_s4 = min(remaining, s4_width)
    tax_s4 = taxable_s4 * 0.15
    breakdown.append(f"10,00,001 - 12,00,000 (@15%): {tax_s4:,.2f} (on {taxable_s4:,.2f})")
    
    remaining -= s4_width
    if remaining <= 0:
        return breakdown

    # Slab 5: 12L - 15L @ 20%
    s5_width = 300_000
    taxable_s5 = min(remaining, s5_width)
    tax_s5 = taxable_s5 * 0.20
    breakdown.append(f"12,00,001 - 15,00,000 (@20%): {tax_s5:,.2f} (on {taxable_s5:,.2f})")
    
    remaining -= s5_width
    if remaining <= 0:
        return breakdown
        
    # Slab 6: > 15L @ 30%
    tax_s6 = remaining * 0.30
    breakdown.append(f"> 15,00,000 (@30%): {tax_s6:,.2f} (on {remaining:,.2f})")
    
    return breakdown

# ============================================================
# Main Comparison Tool
# ============================================================

def compare_tax_regimes(extracted_data: dict = None) -> dict:
    """
    Compares Old vs New tax regimes based on extracted data.
    """
    comparison_logger.info("Starting tax regime comparison...")
    
    gross_salary = 0.0
    other_income = 0.0
    ch_via = 0.0
    deduction_details_str = ""
    
    # 1. Parse Extracted Data
    if extracted_data:
        for form_name, form_data in extracted_data.items():
            if not isinstance(form_data, dict):
                continue
                
            # Parse Form 16 Part B (Rich Source)
            if "16_Part_B" in form_name:
                # Salary
                salary_details = form_data.get("salary_details", {})
                if isinstance(salary_details, dict):
                    gs = salary_details.get("total_salary", 0) + salary_details.get("salary_from_other_employers", 0)
                    if gs > 0: gross_salary = gs
                
                # Other Income
                other_inc = form_data.get("other_income_reported", {})
                if isinstance(other_inc, dict):
                    oi = other_inc.get("total_other_income", 0)
                    if oi > 0: other_income = oi
                
                # Deductions
                deductions = form_data.get("deductions_chapter_VIA", {})
                if isinstance(deductions, dict):
                    total_ded = sum(v for v in deductions.values() if isinstance(v, (int, float)))
                    if total_ded > 0: ch_via = total_ded
            
            # Fallback: AIS for other income if Form 16 misses it
            elif "AIS" in form_name:
                # Logic to sum interest/dividend income from AIS could go here
                pass

    comparison_logger.info(f"Computed Income Params - Gross Salary: {gross_salary}, Other Income: {other_income}, Deductions: {ch_via}")

    # 2. Calculate Old Regime
    salary_after_std_old = max(gross_salary - STD_DEDUCTION_OLD, 0)
    old_gti = salary_after_std_old + other_income
    old_taxable = max(old_gti - ch_via, 0)
    old_tax = old_regime_tax(old_taxable)

    # 3. Calculate New Regime
    salary_after_std_new = max(gross_salary - STD_DEDUCTION_NEW, 0)
    new_gti = salary_after_std_new + other_income
    new_taxable = max(new_gti, 0) # No VIA deductions
    new_tax = new_regime_tax(new_taxable)

    # 4. Determine Optimal
    tax_diff = old_tax - new_tax
    if tax_diff > 0:
        optimal = "NEW"
    elif tax_diff < 0:
        optimal = "OLD"
    else:
        optimal = "EQUAL"

    # 5. Build Explanations
    old_breakdown = explain_old_regime_tax(old_taxable)
    new_breakdown = explain_new_regime_tax(new_taxable)
    
    explanation = (
        f"--- TAX CALCULATION BREAKDOWN ---\n\n"
        f"INCOME DETAILS:\n"
        f"Gross Salary: ₹{gross_salary:,.2f}\n"
        f"Other Income: ₹{other_income:,.2f}\n"
        f"Deductions (Chapter VI-A): ₹{ch_via:,.2f}\n\n"
        
        f"--- OLD REGIME ---\n"
        f"Standard Deduction: ₹{STD_DEDUCTION_OLD:,.2f}\n"
        f"Taxable Income: ₹{old_taxable:,.2f}\n"
        f"Tax Calculation:\n" + "\n".join(f"  - {line}" for line in old_breakdown) + "\n"
        f"Total Tax (Old): ₹{old_tax:,.2f}\n\n"
        
        f"--- NEW REGIME ---\n"
        f"Standard Deduction: ₹{STD_DEDUCTION_NEW:,.2f}\n"
        f"Taxable Income: ₹{new_taxable:,.2f}\n"
        f"Tax Calculation:\n" + "\n".join(f"  - {line}" for line in new_breakdown) + "\n"
        f"Total Tax (New): ₹{new_tax:,.2f}\n\n"
        
        f"--- RESULT ---\n"
        f"Difference: ₹{abs(tax_diff):,.2f}\n"
        f"Recommendation: Choose {optimal} Regime."
    )

    # 6. Build Result
    result = {
        "gross_salary": gross_salary,
        "other_income": other_income,
        "std_ded_old": STD_DEDUCTION_OLD,
        "std_ded_new": STD_DEDUCTION_NEW,
        "ch_via": ch_via,
        "old_taxable": old_taxable,
        "old_tax": old_tax,
        "new_taxable": new_taxable,
        "new_tax": new_tax,
        "tax_diff": tax_diff,
        "optimal_regime": optimal,
        "detailed_explanation": explanation
    }
    
    comparison_logger.info(f"Comparison Result: Optimal is {optimal}, Savings: {abs(tax_diff)}")
    return result

if __name__ == "__main__":
    # Test run with sample data
    # Simulating data extraction where we found 15L salary and 1.5L deductions
    sample_data = {
        "16_Part_B": {
            "salary_details": {"total_salary": 1_500_000, "salary_from_other_employers": 0},
            "deductions_chapter_VIA": {"80C": 150_000}
        }
    }
    print("Running with sample data (Salary: 15L, 80C: 1.5L)...")
    res = compare_tax_regimes(sample_data)
    print(res["detailed_explanation"])
