"""
ITR Form Generation Service (CORRECTED)
Maps extracted tax data (Form 16, AIS) and computed tax liability into 
official ITR-1/ITR-2 JSON schemas (AY 2025-26).
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import copy
from typing import Dict, Any, Optional

try:
    from app.services.itr_schemas_service import ITR1_TEMPLATE, ITR2_TEMPLATE
except ImportError:
    from itr_schemas_service import ITR1_TEMPLATE, ITR2_TEMPLATE

from app.db.models import ITR, ComputedData


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
    # Check for Capital Gains in AIS
    for form_name, form_data in extracted_data.items():
        if "AIS" in form_name:
            securities = form_data.get("securities_transactions", [])
            mutual_funds = form_data.get("mutual_fund_transactions", [])
            if securities or mutual_funds:
                logger.info("Detected Capital Gains/Securities in AIS -> Recommending ITR-2")
                return "ITR-2"
                
    # Check for multiple house properties (not in current data, but future-proof)
    # Check for foreign assets (not in current data)
    
    return "ITR-1"

def load_user_profile() -> Dict[str, Any]:
    """Loads user manual overrides from profile file."""
    try:
        profile_path = Path(__file__).resolve().parents[1] / "data" / "user_profile.json"
        if profile_path.exists():
            with open(profile_path, "r") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load user profile: {e}")
    return {}

def populate_itr_form(template: Dict, data: Dict, computation: Dict, form_type: str) -> Dict:
    """Populates ITR schema with data (works for both ITR-1 and ITR-2)."""
    itr = copy.deepcopy(template)
    
    # Load user profile overrides
    user_profile = load_user_profile()
    
    # Determine form structure
    if form_type == "ITR-2":
        form = itr["ITR"]["ITR2"]
        form_root = form
    else:
        form = itr["ITR"]["ITR1"]
        form_root = form

    # 1. CREATION INFO (Mandatory for all forms)
    creation_info = {
        "SWVersionNo": "1.0",
        "SWCreatedBy": "SW00000001", 
        "JSONCreatedBy": "SW00000001",
        "JSONCreationDate": datetime.now().strftime("%Y-%m-%d"),
        "IntermediaryCity": "Delhi",
        "Digest": "--------------------------------------------" # Placeholder
    }
    form_root["CreationInfo"] = creation_info

    # 2. FILING STATUS (Mandatory)
    filing_status = {
        "ReturnFileSec": 11, # 139(1) - On or before due date
        "OptOutNewTaxRegime": "N", # Default to New Regime
        "ItrFilingDueDate": "2025-07-31" # Standard due date
    }
    
    if form_type == "ITR-2":
        if "PartA_GEN1" not in form: form["PartA_GEN1"] = {}
        if "FilingStatus" not in form["PartA_GEN1"]: form["PartA_GEN1"]["FilingStatus"] = {}
        form["PartA_GEN1"]["FilingStatus"].update(filing_status)
        # ITR-2 specific logic for FilingStatus can be added here
    else:
        if "FilingStatus" not in form: form["FilingStatus"] = {}
        form["FilingStatus"].update(filing_status)
        # ITR-1 specific logic

    
    # Helper for robust key matching
    def matches_key(key: str, identifiers: list) -> bool:
        k_lower = key.lower()
        for ident in identifiers:
            if ident.lower() in k_lower:
                return True
        return False

    # 1. PERSONAL INFORMATION
    personal_info = {}
    for fname, fdata in data.items():
        if matches_key(fname, ["16", "form16", "Part_A", "Part_B"]):
            emp = fdata.get("employee_details", {})
            if emp:
                personal_info = emp
                break
        elif matches_key(fname, ["AIS"]):
            personal_info = fdata.get("assessee_details", {})
             
    if personal_info:
        name = personal_info.get("name", "Unknown").strip()
        # Handle name variations
        name_parts = name.split()
        if len(name_parts) >= 2:
            first_name = name_parts[0]
            surname = " ".join(name_parts[1:])
        else:
            first_name = name
            surname = "."
            
        # Import defaults
        from app.core.defaults import get_defaults_dict
        defaults = get_defaults_dict()
            
        # USER PROFILE OVERRIDES
        aadhaar = user_profile.get("aadhaar") or defaults["aadhaar"]
        mobile = int(user_profile.get("mobile") or defaults["mobile"])
        email = user_profile.get("email") or defaults["email"]
            
        if form_type == "ITR-2":
            # ITR-2: PersonalInfo under PartA_GEN1
            p_info = form.setdefault("PartA_GEN1", {}).setdefault("PersonalInfo", {})
            p_info.setdefault("AssesseeName", {})["FirstName"] = first_name
            p_info["AssesseeName"]["SurNameOrOrgName"] = surname
            p_info["PAN"] = personal_info.get("PAN", "ABCDE1234F")
            p_info["AadhaarCardNo"] = aadhaar
            p_info["DOB"] = personal_info.get("dob", "1990-01-01")
            p_info["Status"] = "I"
            
            # Address
            addr = p_info.setdefault("Address", {})
            address_str = personal_info.get("address", "Unknown Address")
            addr["ResidenceNo"] = "1"
            addr["LocalityOrArea"] = address_str[:50]
            addr["CityOrTownOrDistrict"] = "City"
            addr["StateCode"] = "01"
            addr["CountryCode"] = "91"
            addr["PinCode"] = 110001
            addr["CountryCodeMobile"] = 91
            addr["MobileNo"] = mobile
            addr["EmailAddress"] = email
            
        else:
            # ITR-1: PersonalInfo direct
            p_info = form.setdefault("PersonalInfo", {})
            p_info.setdefault("AssesseeName", {})["FirstName"] = first_name
            p_info["AssesseeName"]["SurNameOrOrgName"] = surname
            p_info["PAN"] = personal_info.get("PAN", "ABCDE1234F")
            p_info["AadhaarCardNo"] = aadhaar
            p_info["DOB"] = personal_info.get("dob", "1990-01-01")
            
            # Address
            addr = p_info.setdefault("Address", {})
            address_str = personal_info.get("address", "Unknown Address")
            addr["ResidenceNo"] = "1"
            addr["LocalityOrArea"] = address_str[:50]
            addr["CityOrTownOrDistrict"] = "City"
            addr["StateCode"] = "01"
            addr["CountryCode"] = "91"
            addr["PinCode"] = 110001
            addr["CountryCodeMobile"] = 91
            addr["MobileNo"] = mobile
            addr["EmailAddress"] = email
            
            # Employer
            p_info["EmployerCategory"] = "OTH"

    # Verification Block
    father_name = user_profile.get("father_name", "FATHER NAME")
    if form_type == "ITR-2":
        verification = form.setdefault("Verification", {}).setdefault("Declaration", {})
    else:
        verification = form.setdefault("Verification", {}).setdefault("Declaration", {})
        
    verification["FatherName"] = father_name
    verification["AssesseeVerName"] = f"{first_name} {surname}".strip()
    verification["PAN"] = personal_info.get("PAN", "ABCDE1234F")
    verification["Capacity"] = "S"
    verification["Place"] = "Delhi"
    verification["Date"] = datetime.now().strftime("%Y-%m-%d")

    # 2. INCOME CALCULATION
    gross_salary = 0.0
    house_property_income = 0.0
    interest_income = 0.0
    
    # Aggregate salary from all Form 16 Part B
    for fname, fdata in data.items():
        if matches_key(fname, ["16_Part_B", "form16b"]):
            salary_det = fdata.get("salary_details", {})
            if isinstance(salary_det, dict):
                total_sal = salary_det.get("total_salary", 0) or 0
                other_emp_sal = salary_det.get("salary_from_other_employers", 0) or 0
                gross_salary += total_sal + other_emp_sal
                
            # House property income
            other_inc = fdata.get("other_income_reported", {})
            if isinstance(other_inc, dict):
                house_property_income = other_inc.get("house_property_income", 0) or 0
    
    # Aggregate interest income from AIS
    for fname, fdata in data.items():
        if matches_key(fname, ["AIS"]):
            interest_entries = fdata.get("interest_income", [])
            if isinstance(interest_entries, list):
                interest_income = sum(
                    float(entry.get("interest_amount", 0)) for entry in interest_entries
                )
    
    total_other_income = house_property_income + interest_income
    gross_total_income = gross_salary + total_other_income
    
    # 3. REGIME AND DEDUCTIONS
    # Determine regime from computation or default to NEW
    is_new_regime = True
    if computation:
        is_new_regime = computation.get("regime_selected", "new").lower() == "new"

    if is_new_regime:
        total_deductions = 0.0
        section_80c = 0
        section_80d = 0
    else:
        total_deductions = computation.get("ch_via_validated", 0.0) if computation else 0.0
        breakdown = computation.get("ch_via_breakdown", {}) if computation else {}
        section_80c = int(breakdown.get("80c_combined", 0))
        section_80d = int(breakdown.get("80d", 0))
    
    total_income = max(0, gross_total_income - total_deductions)
    
    # 4. POPULATE FORM-SPECIFIC INCOME FIELDS
    if form_type == "ITR-2":
        # ITR-2: PartB_TI
        form["PartB_TI"]["Salaries"] = int(gross_salary)
        form["PartB_TI"]["IncomeFromHP"] = int(house_property_income)
        form["PartB_TI"]["IncomeFromOS"] = int(interest_income)
        form["PartB_TI"]["GrossTotalIncome"] = int(gross_total_income)
        form["PartB_TI"]["TotalIncome"] = int(total_income)
        
        # Deductions
        if not is_new_regime:
            form["PartB_TI"]["DeductionsUnderChapterVIA"]["Section80C"] = section_80c
            form["PartB_TI"]["DeductionsUnderChapterVIA"]["Section80D"] = section_80d
            form["PartB_TI"]["DeductionsUnderChapterVIA"]["TotalChapVIADed"] = int(total_deductions)
        else:
            form["PartB_TI"]["DeductionsUnderChapterVIA"]["Section80C"] = 0
            form["PartB_TI"]["DeductionsUnderChapterVIA"]["Section80D"] = 0
            form["PartB_TI"]["DeductionsUnderChapterVIA"]["TotalChapVIADed"] = 0
            
    else:  # ITR-1
        form["ITR1_IncomeDeductions"]["GrossSalary"] = int(gross_salary)
        form["ITR1_IncomeDeductions"]["IncomeFromSal"] = int(gross_salary)
        form["ITR1_IncomeDeductions"]["IncomeFromHouseProperty"] = int(house_property_income)
        form["ITR1_IncomeDeductions"]["IncomeOthSrc"] = int(interest_income)
        form["ITR1_IncomeDeductions"]["GrossTotIncome"] = int(gross_total_income)
        form["ITR1_IncomeDeductions"]["TotalIncome"] = int(total_income)
        
        # Deductions
        if not is_new_regime:
            form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["Section80C"] = section_80c
            form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["Section80D"] = section_80d
            form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["TotalChapVIADed"] = int(total_deductions)
        else:
            form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["Section80C"] = 0
            form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["Section80D"] = 0
            form["ITR1_IncomeDeductions"]["DeductUndChapVIA"]["TotalChapVIADed"] = 0

    # 5. TAX COMPUTATION
    # Initialize variables to avoid NameError
    gross_tax_liability = 0
    total_tax_payable = 0
    
    if computation:
        # Get tax values
        if is_new_regime:
            base_tax = computation.get("new_tax", 0)
            taxable_income = computation.get("new_taxable", 0)
        else:
            base_tax = computation.get("old_tax", 0)
            taxable_income = computation.get("old_taxable", 0)
            
        # Apply rebate if eligible
        rebate_87a = 0
        if is_new_regime:
            if taxable_income <= 700000:
                rebate_87a = min(base_tax, 25000)
        else:
            if taxable_income <= 500000:
                rebate_87a = min(base_tax, 12500)
                
        # Tax computation fields
        tax_after_rebate = max(base_tax - rebate_87a, 0)
        cess = round(tax_after_rebate * 0.04)
        gross_tax_liability = tax_after_rebate + cess
        total_tax_payable = gross_tax_liability
        
        # Set regime flag and populate tax fields
        if form_type == "ITR-2":
            form["PartA_GEN1"]["FilingStatus"]["OptOutNewTaxRegime"] = "N" if is_new_regime else "Y"
            # Tax computation under PartB_TTI
            form["PartB_TTI"]["ComputationOfTaxLiability"]["TaxPayableOnTotalIncome"] = int(tax_after_rebate) # Base
            form["PartB_TTI"]["ComputationOfTaxLiability"]["Rebate87A"] = int(rebate_87a)
            form["PartB_TTI"]["ComputationOfTaxLiability"]["TaxPayableAfterRebate"] = int(tax_after_rebate)
            form["PartB_TTI"]["ComputationOfTaxLiability"]["HealthAnd EducationCess"] = int(cess)
            form["PartB_TTI"]["ComputationOfTaxLiability"]["GrossTaxLiability"] = int(gross_tax_liability)
            form["PartB_TTI"]["ComputationOfTaxLiability"]["NetTaxLiability"] = int(total_tax_payable)
            form["PartB_TTI"]["ComputationOfTaxLiability"]["TotalTaxPayable"] = int(total_tax_payable)
            
        else:
            form["FilingStatus"]["OptOutNewTaxRegime"] = "N" if is_new_regime else "Y"
            form["ITR1_TaxComputation"]["GrossTaxLiability"] = int(gross_tax_liability)
            form["ITR1_TaxComputation"]["Rebate87A"] = int(rebate_87a)
            form["ITR1_TaxComputation"]["TaxPayableOnRebate"] = int(tax_after_rebate)
            form["ITR1_TaxComputation"]["EducationCess"] = int(cess)
            form["ITR1_TaxComputation"]["TotalTaxPayable"] = int(total_tax_payable)
            form["ITR1_TaxComputation"]["NetTaxLiability"] = int(total_tax_payable)

    # POPULATE SCHEDULES (Only for ITR-2, as ITR-1 uses aggregated sections)
    if form_type == "ITR-2":
        # ScheduleS - Salary Details
        salary_schedule = []
        for fname, fdata in data.items():
            if matches_key(fname, ["16_Part_B", "form16b"]):
                emp_details = fdata.get("employer_details", {})
                salary_det = fdata.get("salary_details", {})
                if isinstance(emp_details, dict) and isinstance(salary_det, dict):
                    total_sal = salary_det.get("total_salary", 0) or 0
                    other_emp = salary_det.get("salary_from_other_employers", 0) or 0
                    if total_sal > 0 or other_emp > 0:
                        salary_schedule.append({
                            "NameOfEmployer": emp_details.get("name", "Unknown"),
                            "TANOfEmployer": emp_details.get("TAN", ""),
                            "GrossSalary": int(total_sal + other_emp),
                            "IncomeChargeable": int(total_sal + other_emp)
                        })
        if salary_schedule:
            form["ScheduleS"]["Salaries"] = salary_schedule
            
        # ScheduleHP - House Property
        hp_schedule = []
        for fname, fdata in data.items():
            if matches_key(fname, ["16_Part_B", "form16b"]):
                other_inc = fdata.get("other_income_reported", {})
                if isinstance(other_inc, dict):
                    hp_income = other_inc.get("house_property_income", 0) or 0
                    if hp_income != 0:  # Include losses
                        hp_schedule.append({
                            "PropertyType": "SOP",  # Self-Occupied Property
                            "Address": "Self-Occupied Property",
                            "GrossRentReceived": 0,
                            "TaxesPaid": 0,
                            "StandardDeduction": 0,
                            "InterestPayable": abs(hp_income) if hp_income < 0 else 0,
                            "IncomeFromHP": int(hp_income)
                        })
        if hp_schedule:
            form["ScheduleHP"]["IFHP"] = hp_schedule
            
        # ScheduleOS - Other Sources (Interest)
        os_schedule = []
        for fname, fdata in data.items():
            if matches_key(fname, ["AIS"]):
                interest_entries = fdata.get("interest_income", [])
                if isinstance(interest_entries, list):
                    for entry in interest_entries:
                        if isinstance(entry, dict):
                            interest_amt = entry.get("interest_amount", 0)
                            if interest_amt > 0:
                                os_schedule.append({
                                    "NatureOfIncome": "INT",  # Interest
                                    "NameOfPayer": entry.get("bank_or_entity_name", "Unknown"),
                                    "PANOfPayer": "",
                                    "Amount": float(interest_amt)
                                })
        if os_schedule:
            form["ScheduleOS"]["IncOthSrc"] = os_schedule
            
        # ScheduleCG - Capital Gains
        cg_schedule = []
        for fname, fdata in data.items():
            if matches_key(fname, ["AIS"]):
                sec_txns = fdata.get("securities_transactions", [])
                if isinstance(sec_txns, list):
                    for txn in sec_txns:
                        if isinstance(txn, dict) and txn.get("transaction_type") in ["Sale", "SALE"]:
                            cg_schedule.append({
                                "ISINCode": txn.get("isin_code", ""),
                                "NameOfShare": txn.get("script_name", ""),
                                "NoOfUnits": float(txn.get("quantity", 0)),
                                "SaleValue": float(txn.get("transaction_value", 0)),
                                "DateOfTransfer": txn.get("transaction_date", ""),
                                "Exchange": txn.get("exchange", "NSE"),
                                "TypeOfAsset": "LSS",  # Listed Equity Shares
                                "STTApplicable": "Y"
                            })
        if cg_schedule:
            # Aggregate summary
            total_stcg = sum(float(item.get("SaleValue", 0)) for item in cg_schedule)
            form["ScheduleCG"]["CapGainSummary"]["STCG15Pct"] = int(total_stcg) if total_stcg > 0 else 0
            form["ScheduleCG"]["LTCGDtls"] = cg_schedule

    # 6. TAX PAID (TDS) - COLLECT FROM ALL SOURCES
    tds_entries = []
    total_tds = 0
    employer_tds_map = {}  # Track TDS by employer to avoid duplicates
    
    # Get TDS from all Form 16 Part A files
    for fname, fdata in data.items():
        if matches_key(fname, ["16_Part_A", "form16a"]):
            employer = fdata.get("employer_details", {})
            employer_name = employer.get("name", "Unknown")
            employer_tan = employer.get("TAN", "")
            
            tds_summary = fdata.get("tds_summary", [])
            employer_total_salary = 0
            employer_total_tds = 0
            
            if isinstance(tds_summary, list):
                for item in tds_summary:
                    if isinstance(item, dict):
                        amount_credited = item.get("amount_paid_credited", 0) or 0
                        tax_deducted = item.get("tax_deducted", 0) or 0
                        employer_total_salary += amount_credited
                        employer_total_tds += tax_deducted
                
                if employer_total_tds > 0:
                    # Store by TAN to avoid duplicates
                    if employer_tan not in employer_tds_map:
                        employer_tds_map[employer_tan] = {
                            "TAN": employer_tan,
                            "EmployerName": employer_name,
                            "IncChrgSal": int(employer_total_salary),
                            "TotalTDSSal": int(employer_total_tds)
                        }
                        total_tds += employer_total_tds

    # Fallback: Check Form 16 Part B if no Part A data
    if not tds_entries:
        for fname, fdata in data.items():
            if matches_key(fname, ["16_Part_B", "form16b"]):
                tax_comp = fdata.get("tax_computation", {})
                emp_details = fdata.get("employer_details", {})
                if isinstance(tax_comp, dict):
                    tds_total = tax_comp.get("tax_deducted_at_source", 0) or 0
                    if tds_total > 0:
                        tds_entries.append({
                            "TAN": emp_details.get("TAN", "UNKNOWN"),
                            "EmployerName": emp_details.get("name", "Unknown Employer"),
                            "IncChrgSal": int(gross_salary),
                            "TotalTDSSal": int(tds_total)
                        })
                        total_tds += tds_total
    
    # Populate TDS fields (structure differs between ITR-1 and ITR-2)
    if form_type == "ITR-2":
        # ITR-2 has TDS under TaxPaid.TaxesPaid
        if tds_entries:
            form["TaxPaid"]["TaxesPaid"]["TDSonSalaries"] = tds_entries
    else:
        # ITR-1 has TDS directly under TaxPaid
        if tds_entries:
            form["TaxPaid"]["TDSonSalary"] = tds_entries

    # 7. REFUND CALCULATION - CORRECTED
    # Use actual total TDS from all employers
    tax_payable = total_tax_payable if computation else 0
    tds_credit = total_tds
    # Refund = Total TDS - Net Tax Liability
    refund_due = max(tds_credit - tax_payable, 0)
    tax_due = max(tax_payable - tds_credit, 0)  # Tax payable if TDS < liability
    
    form["Refund"]["RefundDue"] = int(refund_due)
    if form_type == "ITR-2":
        form["PartB_TTI"]["ComputationOfTaxLiability"]["TotalTaxPaid"] = int(tds_credit)

    return itr

# ... imports
from app.db.connection import get_sync_db
from bson import ObjectId

# ... (existing code)

def save_itr_to_db(user_id: str, form_type: str, itr_data: Dict, computation_result: Dict = None):
    """Persists the generated ITR to the database."""
    if not user_id:
        logger.warning("Skipping DB persistence: No user_id provided")
        return

    try:
        db = get_sync_db()
        
        # Prepare computed data
        comp_data = ComputedData()
        if computation_result:
             regime = computation_result.get("regime_selected", "OLD").upper()
             is_new = regime == "NEW"
             
             if is_new:
                 comp_data.total_income = float(computation_result.get("new_taxable", 0.0))
                 comp_data.total_tax_payable = float(computation_result.get("new_tax", 0.0))
                 comp_data.total_deductions = 0.0
             else:
                 comp_data.total_income = float(computation_result.get("old_taxable", 0.0))
                 comp_data.total_tax_payable = float(computation_result.get("old_tax", 0.0))
                 comp_data.total_deductions = float(computation_result.get("ch_via_validated", 0.0))
                 
             comp_data.regime = regime

        # Convert user_id to ObjectId if needed
        try:
            if isinstance(user_id, str):
                user_oid = ObjectId(user_id)
            else:
                user_oid = user_id
        except Exception:
            logger.error(f"Invalid user_id format: {user_id}")
            return

        itr_doc = ITR(
            user_id=user_oid,
            form_type=form_type,
            status="DRAFT",
            computed_data=comp_data,
            itr_submission=itr_data
        )
        
        # Insert
        itr_dict = itr_doc.model_dump(by_alias=True, exclude={"id"})
        result = db.itrs.insert_one(itr_dict)
        logger.info(f"Saved ITR to DB with ID: {result.inserted_id}")
        return result.inserted_id
        
    except Exception as e:
        logger.error(f"Failed to save ITR to DB: {e}")
        return None

def generate_filing_forms(extracted_data: Dict[str, Any] = None, computation_result: Dict[str, Any] = None, user_id: str = None) -> Dict[str, str]:
    """
    Main entry point to generate the ITR JSON.
    
    Args:
        extracted_data: Dictionary containing data from Form 16 A/B, AIS.
        computation_result: Result from tax_comparison.
        user_id: User ID to fetch data from DB if extracted_data not provided.
        
    Returns:
        Dictionary with 'form_type' and 'file_path' of the generated JSON.
    """
    logger.info("Generating Filing Forms...")
    
    # If extracted_data not provided but user_id is, fetch from DB
    if not extracted_data and user_id:
        try:
            from app.services.db_helpers import load_user_tax_data
            from app.db.connection import get_sync_db
            
            logger.info(f"Fetching extracted data from DB for user_id: {user_id}")
            db = get_sync_db()
            extracted_data = load_user_tax_data(db, user_id)
            
            if not extracted_data:
                logger.error(f"No tax data found in DB for user {user_id}")
                raise ValueError(f"No tax data found for user {user_id}")
                
        except Exception as e:
            logger.error(f"Failed to fetch data from DB: {e}")
            raise
    
    if not extracted_data:
        raise ValueError("No extracted data provided and no user_id given for DB fetch")
    
    # 1. Determine Form Type
    form_type = determine_itr_form_type(extracted_data)
    logger.info(f"Selected Form Type: {form_type}")
    
    # 2. Select Template & Populate
    if form_type == "ITR-2":
        if "ITR2" not in ITR2_TEMPLATE.get("ITR", {}):
            # Handle template structure differences
            logger.error("ITR2_TEMPLATE structure invalid. Check schema.")
            # Fallback to basic structure
            final_json = {"ITR": {"ITR2": {}}}
        else:
            final_json = populate_itr_form(ITR2_TEMPLATE, extracted_data, computation_result, "ITR-2")
    else:
        final_json = populate_itr_form(ITR1_TEMPLATE, extracted_data, computation_result, "ITR-1")
    
    # 3. Save to File
    output_dir = Path(__file__).resolve().parents[1] / "data" / "filing"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Clean form type for filename
    clean_form_type = form_type.replace("-", "")
    file_name = f"{clean_form_type}_{timestamp}.json"
    file_path = output_dir / file_name
    
    with open(file_path, "w") as f:
        json.dump(final_json, f, indent=4)
        
    logger.info(f"Generated {form_type} at {file_path}")
    
    # 4. Save to DB
    if user_id:
        save_itr_to_db(user_id, form_type, final_json, computation_result)
    
    
    return {
        "form_type": form_type,
        "file_path": str(file_path)
    }

if __name__ == "__main__":
    # Test stub
    print("Form Generation Module - Ready")