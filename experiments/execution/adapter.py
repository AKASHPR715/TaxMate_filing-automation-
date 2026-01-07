from typing import Any, Dict
from experiments.data_generation.schema import TaxProfile

def calculate_hra_exemption(basic: float, hra_received: float, rent_paid: float, is_metro: bool) -> float:
    """
    Calculate HRA exemption under Section 10(13A).
    This MUST match the logic in generator.py to ensure consistency.
    """
    if rent_paid <= 0:
        return 0.0
    
    # HRA Exemption = Minimum of:
    # 1. Actual HRA Received
    # 2. 50% of Basic (Metro) or 40% (Non-Metro)
    # 3. Rent Paid - 10% of Basic
    
    limit1 = hra_received
    limit2 = basic * (0.50 if is_metro else 0.40)
    limit3 = max(0, rent_paid - (0.10 * basic))
    
    return min(limit1, limit2, limit3)

def adapt_profile_to_orchestrator(profile: TaxProfile) -> Dict[str, Any]:
    """
    Converts a TaxProfile into the nested dictionary structure 
    expected by TaxOrchestrator (simulating 'extracted_data').
    
    CRITICAL: Must calculate HRA exemption here using the same logic
    as the ground truth generator to ensure consistency.
    """
    inc = profile.income
    ded = profile.deductions
    
    # Calculate HRA exemption (Section 10(13A))
    hra_exemption = calculate_hra_exemption(
        basic=inc.basic_salary,
        hra_received=inc.hra_received,
        rent_paid=ded.rent_paid_annual,
        is_metro=ded.is_metro_city
    )
    
    # Structure mimics what extracting from Form 16 Part B looks like
    form16_data = {
        "salary_details": {
            "total_salary": inc.gross_salary,
            "salary_from_other_employers": 0.0,
        },
        "exemptions_u_s_10": {
            "house_rent_allowance": hra_exemption,  # CALCULATED exemption, not raw HRA
            "total_exemptions": hra_exemption  # For now, only HRA
        },
        "deductions_chapter_VIA": {
            "section_80C": ded.pf_contribution + ded.elss + ded.lic_premium + ded.ppf,
            "section_80D": ded.medical_insurance_self + ded.medical_insurance_parents,
        },
        "other_income_reported": {
            "total_other_income": inc.other_sources_income
        }
    }
    
    return {
        "16_Part_B": form16_data,
        "financial_year": "23-24"  # FY 2023-24 for AY 2024-25
    }
