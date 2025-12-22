"""
ITR Form Generation Service
Maps extracted tax data (Form 16, AIS) and computed tax liability into 
Official ITR-1/ITR-2 JSON Schemas (AY 2025-26).
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import copy
from typing import Dict, Any, Optional

try:
    from services.itr_schemas import ITR1_TEMPLATE, ITR2_TEMPLATE
except ImportError:
    from itr_schemas import ITR1_TEMPLATE, ITR2_TEMPLATE

# Setup logger
logger = logging.getLogger("FormGeneration")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

def _get_safe_value(data: Dict, keys: list, default=0):
    """Safely retrieve nested dictionary values."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, {})
        else:
            return default
            
    # If we reached a leaf that is not a dict, return it.
    # If strictly looking for a value, ensure it's not a dict unless intentional
    if isinstance(current, (int, float, str)):
        return current
    elif current == {}:
        return default
    return current

def determine_itr_form_type(extracted_data: Dict[str, Any]) -> str:
    """
    Decides whether to use ITR-1 or ITR-2 based on income sources.
    ITR-1: Salary, One House Property, Other Sources (Interest, etc.) <= 50L
    ITR-2: Capital Gains, >1 House Property, Foreign Assets, etc.
    """
    # Check for Capital Gains in AIS or Form 16
    has_capital_gains = False
    
    # Check AIS for Securities/Mutual Funds
    for form_name, form_data in extracted_data.items():
        if "AIS" in form_name:
            if form_data.get("securities_transactions") or form_data.get("mutual_fund_transactions"):
                has_capital_gains = True
                logger.info("Detected Capital Gains/Securities in AIS -> Recommending ITR-2")
                break
                
    if has_capital_gains:
        return "ITR-2"
        
    return "ITR-1"

def populate_itr1(template: Dict, data: Dict, computation: Dict) -> Dict:
    """Populates ITR-1 Schema with data."""
    itr = copy.deepcopy(template)
    form = itr["ITR"]["ITR1"]
    
    # 1. Personal Information (From Form 16 Part A/B or AIS)
    # Try to find personal info from any available form
    personal_info = {}
    for fname, fdata in data.items():
        if "16" in fname:
             # Form 16 likely has employee details
             emp = fdata.get("employee_details", {})
             if emp:
                 personal_info = emp
                 break
        elif "AIS" in fname:
             personal_info = fdata.get("assessee_details", {})
             
    if personal_info:
        name_parts = personal_info.get("name", "Unknown").split(" ")
        form["PersonalInfo"]["AssesseeName"]["FirstName"] = name_parts[0]
        form["PersonalInfo"]["AssesseeName"]["SurNameOrOrgName"] = name_parts[-1] if len(name_parts) > 1 else ""
        form["PersonalInfo"]["PAN"] = personal_info.get("PAN", "ABCDE1234F")
        # Address - often unstructured in extraction, leaving placeholder or partial mapping
        if "address" in personal_info:
             form["PersonalInfo"]["Address"]["LocalityOrArea"] = personal_info["address"][:50]
    
    # 2. Income & Deductions (From Form 16 Part B mainly)
    # Aggregating from all Form 16 Part Bs found
    total_salary = 0
    total_deductions_via = 0
    deduction_breakdown = {}
    
    for fname, fdata in data.items():
        if "16_Part_B" in fname:
             salary_det = fdata.get("salary_details", {})
             if salary_det:
                 total_salary += salary_det.get("total_salary", 0)
             
             # Chapter VI-A
             via = fdata.get("deductions_chapter_VIA", {})
             if via:
                 total_deductions_via += via.get("total_deductions", 0)
                 # Sum up specific sections
                 for k, v in via.items():
                     if isinstance(v, (int, float)):
                         deduction_breakdown[k] = deduction_breakdown.get(k, 0) + v

    form["ITR1_IncomeDeductions"]["GrossSalary"] = int(total_salary)
    form["ITR1_IncomeDeductions"]["IncomeFromSal"] = int(total_salary) # Simplified: net salary = gross for now
    form["ITR1_IncomeDeductions"]["GrossTotIncome"] = int(total_salary) # Add other sources if available
    
    # Deductions
    form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["Section80C"] = int(deduction_breakdown.get("section_80C", 0))
    form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["Section80D"] = int(deduction_breakdown.get("section_80D", 0))
    form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["TotalChapVIADed"] = int(total_deductions_via)
    
    # Total Income
    form["ITR1_IncomeDeductions"]["TotalIncome"] = int(total_salary - total_deductions_via)
    
    # 3. Tax Computation (From our computation result)
    if computation:
        # Determine Regime and Base Values
        optimal = computation.get("optimal_regime", "NEW")
        is_new_regime = (optimal == "NEW")
        
        # Get Taxable Income and Base Tax from computation result
        if is_new_regime:
            taxable_income = computation.get("new_taxable", 0)
            base_tax = computation.get("new_tax", 0)
        else:
            taxable_income = computation.get("old_taxable", 0)
            base_tax = computation.get("old_tax", 0)
            
        # --- Detailed Calculation Logic ---
        
        # A. Gross Tax Liability (Base Tax on Income)
        gross_tax_liability = base_tax
        
        # B. Rebate u/s 87A
        # New Regime: limit 7L, max rebate 25000
        # Old Regime: limit 5L, max rebate 12500
        rebate_87a = 0
        if is_new_regime:
            if taxable_income <= 700000:
                rebate_87a = min(gross_tax_liability, 25000)
        else:
            if taxable_income <= 500000:
                rebate_87a = min(gross_tax_liability, 12500)
                
        # C. Tax Payable after Rebate
        tax_after_rebate = max(gross_tax_liability - rebate_87a, 0)
        
        # D. Health and Education Cess (4%)
        cess = round(tax_after_rebate * 0.04)
        
        # E. Total Tax Payable
        total_tax_payable = tax_after_rebate + cess
        
        # Update Form Fields
        form["FilingStatus"]["OptOutNewTaxRegime"] = "N" if is_new_regime else "Y"
        
        form["ITR1_TaxComputation"]["GrossTaxLiability"] = int(gross_tax_liability)
        form["ITR1_TaxComputation"]["Rebate87A"] = int(rebate_87a)
        form["ITR1_TaxComputation"]["TaxPayableOnRebate"] = int(tax_after_rebate)
        form["ITR1_TaxComputation"]["EducationCess"] = int(cess)
        form["ITR1_TaxComputation"]["TotalTaxPayable"] = int(total_tax_payable)
        form["ITR1_TaxComputation"]["NetTaxLiability"] = int(total_tax_payable)
        form["ITR1_TaxComputation"]["TotTaxPlusIntrstPay"] = int(total_tax_payable) # Assuming 0 interest for now

    
    # 4. Tax Paid (TDS from Form 16 Part A)
    tds_entries = []
    total_tds = 0
    for fname, fdata in data.items():
        if "16_Part_A" in fname:
            summary = fdata.get("tds_summary", [])
            employer = fdata.get("employer_details", {})
            for item in summary:
                 amount_credited = item.get("amount_paid_credited", 0)
                 tax_deducted = item.get("tax_deducted", 0)
                 total_tds += tax_deducted
                 
                 entry = {
                     "TAN": employer.get("TAN", ""),
                     "EmployerName": employer.get("name", ""),
                     "IncChrgSal": amount_credited,
                     "TotalTDSSal": tax_deducted
                 }
                 tds_entries.append(entry)
    
    # Schema for Form 16 Part A TDS in ITR-1 is usually under TDSonSalary
    # Note: The schema provided in itr_schemas.py has empty list [] for "TDSonSalary".
    # We would populate it here if we had the exact item structure definition from the schema.
    # For now, we will leave it empty to avoid schema validation errors with incorrect keys,
    # or just add it if we are confident.
    if tds_entries:
        form["TaxPaid"]["TDSonSalary"] = tds_entries

    return itr

def generate_filing_forms(extracted_data: Dict[str, Any], computation_result: Dict[str, Any]) -> Dict[str, str]:
    """
    Main entry point to generate the ITR JSON.
    
    Args:
        extracted_data: Dictionary containing data from Form 16 A/B, AIS.
        computation_result: Result from tax_comparison.
        
    Returns:
        Dictionary with 'form_type' and 'file_path' of the generated JSON.
    """
    logger.info("Generating Filing Forms...")
    
    # 1. Determine Form Type
    form_type = determine_itr_form_type(extracted_data)
    logger.info(f"Selected Form Type: {form_type}")
    
    # 2. Select Template & Populate
    if form_type == "ITR-1":
        final_json = populate_itr1(ITR1_TEMPLATE, extracted_data, computation_result)
    else:
        # Fallback to ITR-1 logic for now even for ITR-2 or implement basic ITR-2
        # For this task, we'll just populate ITR-2 with similar basic info
        # Or more safely, stick to ITR-1 if ITR-2 implementation is complex
        logger.warning("ITR-2 logic requested but using ITR-1 population logic for common fields.")
        final_json = populate_itr1(ITR1_TEMPLATE, extracted_data, computation_result) # fallback
        final_json["ITR"]["ITR1"]["Form_ITR1"]["FormName"] = "ITR-1 (Fallback)" 

    # 3. Save to File
    output_dir = Path(__file__).resolve().parents[2] / "data" / "filing"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{form_type}_{timestamp}.json"
    file_path = output_dir / file_name
    
    with open(file_path, "w") as f:
        json.dump(final_json, f, indent=4)
        
    logger.info(f"Generated {form_type} at {file_path}")
    
    return {
        "form_type": form_type,
        "file_path": str(file_path)
    }

if __name__ == "__main__":
    # Test stub
    print("Form Generation Module")
