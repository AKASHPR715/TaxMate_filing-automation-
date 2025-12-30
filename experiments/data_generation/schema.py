from typing import List, Optional, Literal
from pydantic import BaseModel, Field

class IncomeDetails(BaseModel):
    gross_salary: float = Field(..., description="Annual Gross Salary")
    basic_salary: float = Field(..., description="Basic component of salary")
    hra_received: float = Field(0.0, description="HRA component received")
    special_allowance: float = Field(0.0, description="Special/Other allowances")
    other_sources_income: float = Field(0.0, description="Income from interest, etc.")

class DeductionDetails(BaseModel):
    # Section 80C
    pf_contribution: float = Field(0.0, description="Provident Fund Contribution")
    elss: float = Field(0.0, description="Equity Linked Savings Scheme")
    lic_premium: float = Field(0.0, description="Life Insurance Premium")
    ppf: float = Field(0.0, description="Public Provident Fund")
    
    # Section 80D
    medical_insurance_self: float = Field(0.0, description="Health Insurance for Self/Family")
    medical_insurance_parents: float = Field(0.0, description="Health Insurance for Parents")
    
    # HRA Related
    rent_paid_annual: float = Field(0.0, description="Actual rent paid annually")
    is_metro_city: bool = Field(False, description="True if living in Metro city (50% HRA exemption)")

class TaxProfile(BaseModel):
    profile_id: str = Field(..., description="Unique ID for the profile")
    age: int = Field(..., description="Age of the taxpayer")
    
    income: IncomeDetails
    deductions: DeductionDetails
    
    # Metadata for experiment
    target_regime: Literal["Old", "New"] = Field(..., description="The regime to analyze against")
    complexity_category: Literal["Simple", "Medium", "Complex"]
    ground_truth_tax: Optional[float] = Field(None, description="Pre-calculated tax execution")
