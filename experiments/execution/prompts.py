from experiments.data_generation.schema import TaxProfile

def format_tax_inputs(profile: TaxProfile) -> str:
    """Format profile data for the prompt."""
    inc = profile.income
    ded = profile.deductions
    
    return f"""
    --- TAXPAYER PROFILE (FY 2024-25) ---
    Gross Salary: ₹{inc.gross_salary}
    Basic Salary: ₹{inc.basic_salary}
    HRA Received: ₹{inc.hra_received}
    Other Income: ₹{inc.other_sources_income}
    
    Rent Paid: ₹{ded.rent_paid_annual}
    Living in Metro: {"Yes" if ded.is_metro_city else "No"}
    
    Deductions:
    - PF: ₹{ded.pf_contribution}
    - LIC: ₹{ded.lic_premium}
    - PPF: ₹{ded.ppf}
    - ELSS: ₹{ded.elss}
    - Medical (Self): ₹{ded.medical_insurance_self}
    - Medical (Parents): ₹{ded.medical_insurance_parents}
    -------------------------------------
    """

def get_zero_shot_prompt(profile: TaxProfile, target_regime: str) -> str:
    """
    Standard Zero-Shot Prompt: Just ask for the number.
    Strictly constrained to the target regime (Old or New).
    """
    data = format_tax_inputs(profile)
    
    return f"""{data}
    
    Calculate the exact income tax liability for this taxpayer under the **{target_regime} Regime** for FY 2024-25.
    
    Rules:
    1. Use the official tax slabs for FY 2024-25.
    2. Consider Standard Deduction.
    3. Consider Surcharge and Cess (4%).
    4. For Old Regime, calculate HRA exemption if applicable.
    
    Return ONLY the final tax amount as a number (e.g., 12500). Do not output any text.
    """

def get_cot_prompt(profile: TaxProfile, target_regime: str) -> str:
    """
    Chain-of-Thought Prompt: Ask for step-by-step reasoning.
    """
    data = format_tax_inputs(profile)
    
    return f"""{data}
    
    Calculate the exact income tax liability for this taxpayer under the **{target_regime} Regime** for FY 2024-25.
    
    Please think step by step:
    1. Determine Gross Total Income.
    2. Calculate Exemptions (like HRA) if Old Regime.
    3. Calculate Deductions (Chapter VI-A) if Old Regime.
    4. Determine Taxable Income.
    5. Apply Tax Slabs.
    6. Add Cess.
    
    Finally, state the exact tax liability.
    Ended your response with: "FINAL TAX: <amount>"
    """
