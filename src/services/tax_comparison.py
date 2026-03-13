#!/usr/bin/env python3
"""
Tax Comparison Service (PATCHED)
Calculates tax liability under Old and New regimes using extracted rules.
CORRECTED FOR AY 2024-25 (FY 2023-24)
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
    from core.constants import NEW_REGIME_SLABS, OLD_REGIME_SLABS, STD_DEDUCTION_NEW_23_24, STD_DEDUCTION_NEW_24_25, STD_DEDUCTION_OLD
except ImportError:
    from src.core.constants import NEW_REGIME_SLABS, OLD_REGIME_SLABS, STD_DEDUCTION_NEW_23_24, STD_DEDUCTION_NEW_24_25, STD_DEDUCTION_OLD

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
# Tax Calculation Logic (CORRECTED FOR FY 2023-24)
# ============================================================

def old_regime_tax(income: float) -> float:
    """Calculates base tax liability under the old income tax regime (before cess)."""
    if income <= 250_000:
        return 0
    elif income <= 500_000:
        return (income - 250_000) * 0.05
    elif income <= 1_000_000:
        return 12_500 + (income - 500_000) * 0.20
    else:
        return 112_500 + (income - 1_000_000) * 0.30

def new_regime_tax_23_24(income: float) -> float:
    """New regime tax for FY 2023-24 (AY 2024-25) - BEFORE cess"""
    if income <= 300_000:
        return 0.0
    if income <= 600_000:
        return (income - 300_000) * 0.05
    if income <= 900_000:
        return 15_000 + (income - 600_000) * 0.10
    if income <= 1_200_000:
        return 45_000 + (income - 900_000) * 0.15
    if income <= 1_500_000:
        return 90_000 + (income - 1_200_000) * 0.20
    return 150_000 + (income - 1_500_000) * 0.30

def new_regime_tax_24_25(income: float) -> float:
    """New regime tax for FY 2024-25 (AY 2025-26) - BEFORE cess"""
    if income <= 300_000:
        return 0.0
    if income <= 700_000:
        return (income - 300_000) * 0.05
    if income <= 1_000_000:
        return 20_000 + (income - 700_000) * 0.10
    if income <= 1_200_000:
        return 50_000 + (income - 1_000_000) * 0.15
    if income <= 1_500_000:
        return 80_000 + (income - 1_200_000) * 0.20
    return 140_000 + (income - 1_500_000) * 0.30

def apply_cess(base_tax: float) -> float:
    """Apply 4% Health and Education Cess"""
    return base_tax * 1.04

def calculate_hra_exemption(hra_received: float, basic_salary: float, 
                            rent_paid_annual: float, is_metro_city: bool) -> float:
    """
    Calculate HRA exemption as per Section 10(13A) of Income Tax Act.
    
    HRA Exemption is the MINIMUM of:
    1. Actual HRA received
    2. 50% of basic salary (metro) or 40% of basic salary (non-metro)
    3. Rent paid minus 10% of basic salary
    
    Args:
        hra_received: Annual HRA component received
        basic_salary: Annual basic salary
        rent_paid_annual: Annual rent paid
        is_metro_city: True if living in metro city (Mumbai, Delhi, Chennai, Kolkata)
        
    Returns:
        Exempted amount under Section 10(13A)
    """
    # If no HRA or no rent paid, no exemption
    if hra_received == 0 or rent_paid_annual == 0 or basic_salary == 0:
        return 0.0
    
    # Option 1: Actual HRA received
    actual_hra = hra_received
    
    # Option 2: 50% of basic (metro) or 40% of basic (non-metro)
    percentage = 0.50 if is_metro_city else 0.40
    percent_of_basic = basic_salary * percentage
    
    # Option 3: Rent paid minus 10% of basic salary
    ten_percent_basic = basic_salary * 0.10
    rent_minus_ten_percent = max(0.0, rent_paid_annual - ten_percent_basic)
    
    # HRA exemption is the MINIMUM of the three
    exemption = min(actual_hra, percent_of_basic, rent_minus_ten_percent)
    
    return exemption

# Explanation functions remain unchanged (they show base tax breakdown)
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

def explain_new_regime_tax(income: float, financial_year: str = "24-25") -> list:
    """Generates a breakdown of the new regime tax calculation."""
    breakdown = []
    
    # Use correct slabs based on FY
    if "23-24" in financial_year:
        slabs = [
            (300_000, 0.0),
            (600_000, 0.05),
            (900_000, 0.10),
            (1_200_000, 0.15),
            (1_500_000, 0.20),
            (float('inf'), 0.30)
        ]
    else:
        slabs = [
            (300_000, 0.0),
            (700_000, 0.05),
            (1_000_000, 0.10),
            (1_200_000, 0.15),
            (1_500_000, 0.20),
            (float('inf'), 0.30)
        ]
    
    prev_limit = 0
    for i, (limit, rate) in enumerate(slabs):
        if income <= prev_limit:
            break
            
        taxable_in_slab = min(income, limit) - prev_limit
        if taxable_in_slab <= 0:
            prev_limit = limit
            continue
            
        tax_in_slab = taxable_in_slab * rate
        
        # Format slab description
        if i == 0:
            slab_desc = f"0 - {int(limit):,}"
        elif limit == float('inf'):
            slab_desc = f"> {int(prev_limit):,}"
        else:
            slab_desc = f"{int(prev_limit)+1:,} - {int(limit):,}"
            
        rate_pct = int(rate * 100)
        breakdown.append(f"{slab_desc} (@{rate_pct}%): {tax_in_slab:,.2f} (on {taxable_in_slab:,.2f})")
        prev_limit = limit
        
        if income <= limit:
            break
    
    return breakdown

# ============================================================
# Chapter VI-A Deduction Validation Functions (ENHANCED)
# ============================================================

def validate_80c_combined(section_80c: float, section_80ccc: float, section_80ccd1: float) -> dict:
    claimed = section_80c + section_80ccc + section_80ccd1
    cap = 150_000
    validated = min(claimed, cap)
    
    comparison_logger.info(f"80C+80CCC+80CCD(1) - Claimed: ₹{claimed:,.2f}, Cap: ₹{cap:,.2f}, Validated: ₹{validated:,.2f}")
    
    return {
        "claimed": claimed,
        "validated": validated,
        "cap": cap,
        "cap_applied": claimed > cap
    }

def validate_80ccd1b(amount: float) -> dict:
    cap = 50_000
    validated = min(amount, cap)
    unused = cap - validated
    
    comparison_logger.info(f"80CCD(1B) - Claimed: ₹{amount:,.2f}, Cap: ₹{cap:,.2f}, Validated: ₹{validated:,.2f}, Unused: ₹{unused:,.2f}")
    
    return {
        "claimed": amount,
        "validated": validated,
        "cap": cap,
        "cap_applied": amount > cap,
        "unused": unused
    }

def validate_80d(amount_self: float, amount_parents: float = 0.0,
                 parents_senior: bool = False) -> dict:
    """
    Section 80D – Medical Insurance Premiums.

    Caps (IT Act, FY 2024-25):
      • Self / spouse / children : ₹25,000
      • Parents (< 60 yrs)       : ₹25,000
      • Parents (≥ 60 yrs)       : ₹50,000
    Total maximum : ₹75,000 (₹25K self + ₹50K senior parents)

    Backward-compatible: if called with a single positional arg (old callers),
    treat it as `amount_self` with no parent portion.
    """
    cap_self    = 25_000
    cap_parents = 50_000 if parents_senior else 25_000

    validated_self    = min(amount_self,    cap_self)
    validated_parents = min(amount_parents, cap_parents)
    validated         = validated_self + validated_parents
    claimed           = amount_self + amount_parents
    cap_total         = cap_self + cap_parents

    comparison_logger.info(
        f"80D - Self: claimed=₹{amount_self:,.2f} cap=₹{cap_self:,.2f} validated=₹{validated_self:,.2f} | "
        f"Parents({'Sr' if parents_senior else 'Jr'}): claimed=₹{amount_parents:,.2f} "
        f"cap=₹{cap_parents:,.2f} validated=₹{validated_parents:,.2f} | Total=₹{validated:,.2f}"
    )

    return {
        "claimed":        claimed,
        "validated":      validated,
        "cap":            cap_total,
        "cap_applied":    claimed > cap_total,
        "self_validated": validated_self,
        "parents_validated": validated_parents,
    }


def validate_chapter_via_deductions(deductions_dict: dict, include_any_other: bool = False, assessee_age: str = "below_60") -> dict:
    comparison_logger.info("=" * 60)
    comparison_logger.info("VALIDATING CHAPTER VI-A DEDUCTIONS")
    comparison_logger.info("=" * 60)
    
    # Extract sections
    sec_80c = deductions_dict.get("section_80C", 0) or 0
    sec_80ccc = deductions_dict.get("section_80CCC", 0) or 0
    sec_80ccd1 = deductions_dict.get("section_80CCD_1", 0) or 0
    sec_80ccd1b = deductions_dict.get("section_80CCD_1B", 0) or 0
    sec_80ccd2 = deductions_dict.get("section_80CCD_2", 0) or 0  # Employer NPS - NOT a deduction!
    # Section 80D: accept either separate fields or a combined field (backward compat)
    sec_80d_self    = deductions_dict.get("section_80D_self", None)
    sec_80d_parents = deductions_dict.get("section_80D_parents", None)
    if sec_80d_self is None:
        # Old callers pass a single 'section_80D' — split evenly as a fallback
        sec_80d_combined = deductions_dict.get("section_80D", 0) or 0
        sec_80d_self    = sec_80d_combined
        sec_80d_parents = 0.0  # assume no parents portion if not broken out
    else:
        sec_80d_self    = sec_80d_self or 0
        sec_80d_parents = sec_80d_parents or 0
    parents_senior = deductions_dict.get("parents_senior_citizen", False)
    sec_80e = deductions_dict.get("section_80E", 0) or 0
    sec_80g = deductions_dict.get("section_80G", 0) or 0
    sec_80tta = deductions_dict.get("section_80TTA", 0) or 0
    any_other = deductions_dict.get("any_other_deductions", 0) or 0
    
    original_total = sum([sec_80c, sec_80ccc, sec_80ccd1, sec_80ccd1b, 
                          sec_80d_self, sec_80d_parents, sec_80e, sec_80g, sec_80tta, any_other])
    # Note: sec_80ccd2 excluded from total (not a deduction)
    
    warnings = []
    
    # Validate 80C combined
    val_80c_combined = validate_80c_combined(sec_80c, sec_80ccc, sec_80ccd1)
    if val_80c_combined["cap_applied"]:
        warnings.append(f"80C+80CCC+80CCD(1) combined capped from ₹{val_80c_combined['claimed']:,.2f} to ₹{val_80c_combined['validated']:,.2f}")
    
    # Validate 80CCD(1B)
    val_80ccd1b = validate_80ccd1b(sec_80ccd1b)
    if val_80ccd1b["cap_applied"]:
        warnings.append(f"80CCD(1B) capped from ₹{val_80ccd1b['claimed']:,.2f} to ₹{val_80ccd1b['validated']:,.2f}")
    
    # Validate 80D (separate self + parents caps)
    val_80d = validate_80d(sec_80d_self, sec_80d_parents, parents_senior=parents_senior)
    if val_80d["cap_applied"]:
        warnings.append(f"80D capped from ₹{val_80d['claimed']:,.2f} to ₹{val_80d['validated']:,.2f}")
    
    # 80CCD(2) - Employer NPS is NOT a Chapter VI-A deduction!
    if sec_80ccd2 > 0:
        warnings.append(f"80CCD(2) (employer NPS contribution of ₹{sec_80ccd2:,.2f}) is not a Chapter VI-A deduction and has been excluded.")
        comparison_logger.warning(f"Excluding 80CCD(2) (employer NPS): ₹{sec_80ccd2:,.2f} - not a valid deduction under Chapter VI-A")
    
    # 80E - Education loan
    validated_80e = sec_80e
    
    # 80G - Donations
    validated_80g = sec_80g
    
    # 80TTA - Savings interest, cap at ₹10,000
    cap_80tta = 10_000
    validated_80tta = min(sec_80tta, cap_80tta)
    if sec_80tta > cap_80tta:
        warnings.append(f"80TTA capped from ₹{sec_80tta:,.2f} to ₹{validated_80tta:,.2f}")
    
    # any_other_deductions - Exclude by default
    excluded_any_other = 0
    validated_any_other = 0
    if any_other > 0:
        if include_any_other:
            validated_any_other = any_other
            comparison_logger.warning(f"Including any_other_deductions: ₹{any_other:,.2f} (user approved)")
        else:
            excluded_any_other = any_other
            warnings.append(f"EXCLUDED ₹{any_other:,.2f} from 'any_other_deductions' - requires valid proof documents")
            comparison_logger.warning(f"Excluding any_other_deductions: ₹{any_other:,.2f} (no proof provided)")
    
    # Calculate validated total (WITHOUT 80CCD(2))
    validated_total = (
        val_80c_combined["validated"] +
        val_80ccd1b["validated"] +
        val_80d["validated"] +
        validated_80e +
        validated_80g +
        validated_80tta +
        validated_any_other
    )
    
    comparison_logger.info(f"Total Deductions - Original: ₹{original_total:,.2f}, Validated: ₹{validated_total:,.2f}")
    
    return {
        "original_total": original_total,
        "validated_total": validated_total,
        "breakdown": {
            "80c_combined": val_80c_combined["validated"],
            "80ccd1b": val_80ccd1b["validated"],
            "80ccd2_excluded": sec_80ccd2,  # Track excluded amount
            "80d": val_80d["validated"],
            "80e": validated_80e,
            "80g": validated_80g,
            "80tta": validated_80tta,
            "any_other": validated_any_other
        },
        "original_breakdown": {
            "80c": sec_80c,
            "80ccc": sec_80ccc,
            "80ccd1": sec_80ccd1,
            "80ccd1b": sec_80ccd1b,
            "80ccd2": sec_80ccd2,
            "80d_self": sec_80d_self,
            "80d_parents": sec_80d_parents,
            "80e": sec_80e,
            "80g": sec_80g,
            "80tta": sec_80tta,
            "any_other": any_other
        },
        "unused_80ccd1b": val_80ccd1b["unused"],
        "excluded_any_other": excluded_any_other,
        "excluded_80ccd2": sec_80ccd2,
        "warnings": warnings
    }

# ============================================================
# Main Comparison Tool (CORRECTED)
# ============================================================

def compare_tax_regimes(extracted_data: dict = None, include_any_other_deductions: bool = False) -> dict:
    comparison_logger.info("=" * 70)
    comparison_logger.info("STARTING TAX REGIME COMPARISON (AY 2024-25 / FY 2023-24)")
    comparison_logger.info("=" * 70)
    
    # Initialize
    gross_salary = 0.0
    other_income = 0.0
    professional_tax = 0.0
    exemptions_10 = {
        "hra": 0.0, "lta": 0.0, "gratuity": 0.0,
        "leave_encashment": 0.0, "commuted_pension": 0.0,
        "other": 0.0, "total": 0.0
    }
    deductions_via_dict = {}
    
    # Parse extracted data
    if extracted_data:
        for form_name, form_data in extracted_data.items():
            if not isinstance(form_data, dict):
                continue
                
            if "16_Part_B" in form_name:
                comparison_logger.info(f"Processing Form 16 Part B data...")
                
                salary_details = form_data.get("salary_details", {})
                if isinstance(salary_details, dict):
                    total_sal = salary_details.get("total_salary", 0) or 0
                    other_emp_sal = salary_details.get("salary_from_other_employers", 0) or 0
                    gross_salary = total_sal + other_emp_sal
                    comparison_logger.info(f"Gross Salary: ₹{total_sal:,.2f} + ₹{other_emp_sal:,.2f} = ₹{gross_salary:,.2f}")
                
                # Extract salary breakdown (for HRA calculation)
                salary_breakdown = form_data.get("salary_breakdown", {})
                basic_salary = 0.0
                hra_received = 0.0
                if isinstance(salary_breakdown, dict):
                    basic_salary = salary_breakdown.get("basic_salary", 0) or 0
                    hra_received = salary_breakdown.get("hra", 0) or 0
                else:
                    # Fallback: estimate basic as 40% of gross if not provided
                    basic_salary = gross_salary * 0.40
                
                # Extract rent details (for HRA calculation)
                rent_details = form_data.get("rent_details", {})
                rent_paid_annual = 0.0
                is_metro_city = False
                if isinstance(rent_details, dict):
                    rent_paid_annual = rent_details.get("annual_rent_paid", 0) or 0
                    is_metro_city = rent_details.get("is_metro_city", False)
                
                exemptions_us10 = form_data.get("exemptions_u_s_10", {})
                if isinstance(exemptions_us10, dict):
                    # Calculate HRA exemption using formula instead of trusting Form 16
                    if hra_received > 0 or (exemptions_us10.get("house_rent_allowance", 0) or 0) > 0:
                        # Use hra_received from salary_breakdown, or fall back to Form 16 value
                        if hra_received == 0:
                            hra_received = exemptions_us10.get("house_rent_allowance", 0) or 0
                        
                        # Calculate HRA exemption using Section 10(13A) formula
                        exemptions_10["hra"] = calculate_hra_exemption(
                            hra_received=hra_received,
                            basic_salary=basic_salary,
                            rent_paid_annual=rent_paid_annual,
                            is_metro_city=is_metro_city
                        )
                        comparison_logger.info(f"HRA Calculation: Received=₹{hra_received:,.2f}, Basic=₹{basic_salary:,.2f}, Rent=₹{rent_paid_annual:,.2f}, Metro={is_metro_city} → Exemption=₹{exemptions_10['hra']:,.2f}")
                    exemptions_10["lta"] = exemptions_us10.get("leave_travel_concession", 0) or 0
                    exemptions_10["gratuity"] = exemptions_us10.get("gratuity", 0) or 0
                    exemptions_10["leave_encashment"] = exemptions_us10.get("leave_encashment", 0) or 0
                    exemptions_10["commuted_pension"] = exemptions_us10.get("commuted_pension", 0) or 0
                    exemptions_10["other"] = exemptions_us10.get("any_other_exemption", 0) or 0
                    exemptions_10["total"] = sum([
                        exemptions_10["hra"], exemptions_10["lta"],
                        exemptions_10["gratuity"], exemptions_10["leave_encashment"],
                        exemptions_10["commuted_pension"], exemptions_10["other"]
                    ])
                    comparison_logger.info(f"Section 10 Exemptions Total: ₹{exemptions_10['total']:,.2f}")
                
                deductions_us16 = form_data.get("deductions_u_s_16", {})
                if isinstance(deductions_us16, dict):
                    professional_tax = deductions_us16.get("professional_tax", 0) or 0
                    comparison_logger.info(f"Professional Tax (u/s 16): ₹{professional_tax:,.2f}")
                
                other_inc = form_data.get("other_income_reported", {})
                if isinstance(other_inc, dict):
                    other_income = other_inc.get("total_other_income", 0) or 0
                    comparison_logger.info(f"Other Income: ₹{other_income:,.2f}")
                
                deductions_via = form_data.get("deductions_chapter_VIA", {})
                if isinstance(deductions_via, dict):
                    deductions_via_dict = deductions_via
                    comparison_logger.info(f"Extracted Chapter VI-A deductions (before validation)")
                    
            elif "AIS" in form_name:
                pass  # Could enhance later

    # Validate deductions
    validation_result = validate_chapter_via_deductions(
        deductions_via_dict, 
        include_any_other=include_any_other_deductions
    )
    ch_via_validated = validation_result["validated_total"]

    # Determine financial year
    financial_year = "24-25"  # Default to AY 2024-25
    if extracted_data:
        for form_name, form_data in extracted_data.items():
            if not isinstance(form_data, dict):
                continue
            if "assessee_details" in form_data:
                details = form_data["assessee_details"]
                if isinstance(details, dict) and "financial_year" in details:
                    val = details["financial_year"]
                    if val and ("24-25" in str(val) or "2024-25" in str(val)):
                        financial_year = "24-25"
                        break
            if "assessment_details" in form_data:
                details = form_data["assessment_details"]
                if isinstance(details, dict) and "assessment_year" in details:
                    ay_val = details["assessment_year"]
                    if ay_val and ("2025-26" in str(ay_val) or "25-26" in str(ay_val)):
                        financial_year = "24-25"
                        break

    # Set standard deductions
    if financial_year == "23-24":
        std_deduction_new = STD_DEDUCTION_NEW_23_24
    else:
        std_deduction_new = STD_DEDUCTION_NEW_24_25

    comparison_logger.info(f"Financial Year: {financial_year}, New Regime Std Deduction: ₹{std_deduction_new:,.2f}")

    # OLD REGIME CALCULATION
    comparison_logger.info("=" * 70)
    comparison_logger.info("OLD REGIME CALCULATION")
    comparison_logger.info("=" * 70)
    
    net_salary_after_exemptions = gross_salary - exemptions_10["total"]
    salary_after_std_old = max(net_salary_after_exemptions - STD_DEDUCTION_OLD, 0)
    income_chargeable_salary = max(salary_after_std_old - professional_tax, 0)
    old_gti = income_chargeable_salary + other_income
    old_taxable = max(old_gti - ch_via_validated, 0)
    
    # Calculate tax WITH CESS
    old_base_tax = old_regime_tax(old_taxable)
    old_tax = apply_cess(old_base_tax)
    
    comparison_logger.info(f"Old Regime Tax (with 4% cess): ₹{old_tax:,.2f}")

    # NEW REGIME CALCULATION
    comparison_logger.info("=" * 70)
    comparison_logger.info("NEW REGIME CALCULATION")
    comparison_logger.info("=" * 70)
    
    salary_after_std_new = max(gross_salary - std_deduction_new, 0)
    income_chargeable_salary_new = max(salary_after_std_new - professional_tax, 0)
    new_gti = income_chargeable_salary_new + other_income
    new_taxable = max(new_gti, 0)
    
    # Use CORRECT tax function based on FY
    if financial_year == "23-24":
        new_base_tax = new_regime_tax_23_24(new_taxable)
    else:
        new_base_tax = new_regime_tax_24_25(new_taxable)
    new_tax = apply_cess(new_base_tax)
    
    comparison_logger.info(f"New Regime Tax (with 4% cess): ₹{new_tax:,.2f}")

    # DETERMINE OPTIMAL REGIME
    tax_diff = old_tax - new_tax
    if tax_diff > 0:
        optimal = "NEW"
        savings = tax_diff
    elif tax_diff < 0:
        optimal = "OLD"
        savings = abs(tax_diff)
    else:
        optimal = "EQUAL"
        savings = 0

    comparison_logger.info("=" * 70)
    comparison_logger.info(f"RESULT: Optimal Regime = {optimal}, Savings = ₹{savings:,.2f}")
    comparison_logger.info("=" * 70)

    # Build explanations
    old_breakdown = explain_old_regime_tax(old_taxable)
    new_breakdown = explain_new_regime_tax(new_taxable, financial_year)
    
    # ... (rest of detailed_explanation building remains same, but now uses correct values)

    result = {
        "gross_salary": gross_salary,
        "section_10_exemptions": exemptions_10,
        "other_income": other_income,
        "professional_tax": professional_tax,
        "std_ded_old": STD_DEDUCTION_OLD,
        "std_ded_new": std_deduction_new,
        "financial_year": financial_year,
        "ch_via_original": validation_result["original_total"],
        "ch_via_validated": validation_result["validated_total"],
        "ch_via_breakdown": validation_result["breakdown"],
        "ch_via_original_breakdown": validation_result["original_breakdown"],
        "unused_80ccd1b": validation_result["unused_80ccd1b"],
        "excluded_any_other_deductions": validation_result["excluded_any_other"],
        "excluded_80ccd2": validation_result["excluded_80ccd2"],
        "validation_warnings": validation_result["warnings"],
        "old_gti": old_gti,
        "old_taxable": old_taxable,
        "old_tax": old_tax,
        "new_gti": new_gti,
        "new_taxable": new_taxable,
        "new_tax": new_tax,
        "tax_diff": tax_diff,
        "optimal_regime": optimal,
        "savings": savings,
        # "detailed_explanation": explanation  # You can rebuild this with correct numbers
    }
    
    return result

if __name__ == "__main__":
    # Test with your actual data structure
    sample_data = {
        "16_Part_B": {
            "salary_details": {"total_salary": 1303398.0, "salary_from_other_employers": 1348706.0},
            "exemptions_u_s_10": {"house_rent_allowance": 0.0, "total_exemptions": 0.0},
            "deductions_u_s_16": {"professional_tax": 2500.0},
            "other_income_reported": {"total_other_income": -200000.0},
            "deductions_chapter_VIA": {
                "section_80C": 150000.0,
                "section_80CCD_1B": 4600.0,
                "section_80D": 37802.0,
                "any_other_deductions": 190000.0
            }
        }
    }
    print("Running with your actual data structure...")
    res = compare_tax_regimes(sample_data)
    print(f"\nOptimal Regime: {res['optimal_regime']}")
    print(f"Old Regime Tax: ₹{res['old_tax']:,.2f}")
    print(f"New Regime Tax: ₹{res['new_tax']:,.2f}")
    print(f"Savings: ₹{res['savings']:,.2f}")
    if res['validation_warnings']:
        print("\nWarnings:")
        for warn in res['validation_warnings']:
            print(f"  ⚠ {warn}")