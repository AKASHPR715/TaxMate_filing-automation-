import sys
import os
import uuid
import random
from typing import List
import numpy as np

# Ensure we can import from src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import local modules
from experiments.data_generation.schema import TaxProfile, IncomeDetails, DeductionDetails
from experiments.data_generation.distributions import TaxDistributions
from experiments.data_generation.constants import (
    OLD_REGIME_SLABS, NEW_REGIME_SLABS, 
    STANDARD_DEDUCTION, OLD_REGIME_STANDARD_DEDUCTION,
    SECTION_80C_LIMIT
)

# Import tax logic from src (reusing slab logic)
try:
    from src.services.tax_comparison import old_regime_tax, new_regime_tax_23_24 as new_regime_tax, apply_cess
except ImportError:
    # Fallback if src import fails (e.g. during standalone testing without proper path)
    # Define simple lambdas or fail hard. Fail hard is better for ensuring consistency.
    print(f"Failed to import src.services.tax_comparison. sys.path: {sys.path}")
    raise

class TaxProfileGenerator:
    def __init__(self):
        pass

    def _calculate_hra_exemption(self, basic: float, hra_received: float, rent_paid: float, is_metro: bool) -> float:
        if rent_paid <= 0:
            return 0.0
        
        # Rule: Min of
        # 1. Actual HRA Received
        # 2. 50% of Basic (Metro) or 40% (Non-Metro)
        # 3. Rent Paid - 10% of Basic
        
        limit1 = hra_received
        limit2 = basic * (0.50 if is_metro else 0.40)
        limit3 = max(0, rent_paid - (0.10 * basic))
        
        return min(limit1, limit2, limit3)

    def generate_profile(self) -> TaxProfile:
        # 1. Generate Income
        gross = TaxDistributions.generate_salary()
        basic, hra, special = TaxDistributions.salary_breakdown(gross)
        other_income = 0.0
        if random.random() < 0.3:
            other_income = random.choice([5000, 10000, 25000, 50000])
        
        income_details = IncomeDetails(
            gross_salary=gross,
            basic_salary=basic,
            hra_received=hra,
            special_allowance=special,
            other_sources_income=other_income
        )
        
        # 2. Generate Deductions & Metadata
        age = random.choice(range(22, 60)) # Working professional
        
        # Deductions
        ded_raw = TaxDistributions.generate_deductions(gross, age)
        is_metro = random.choice([True, False])
        rent_paid = TaxDistributions.generate_rent(basic, is_metro)
        
        deduction_details = DeductionDetails(
            pf_contribution=ded_raw["pf"],
            elss=ded_raw["elss"],
            lic_premium=ded_raw["lic"],
            ppf=ded_raw["ppf"],
            medical_insurance_self=ded_raw["medical_self"],
            medical_insurance_parents=ded_raw["medical_parents"],
            rent_paid_annual=rent_paid,
            is_metro_city=is_metro
        )
        
        # 3. Determine Regime and ID
        # Randomly assign target regime for the "Question"
        target_regime = random.choice(["Old", "New"])
        pid = f"TAX-{uuid.uuid4().hex[:8].upper()}"
        
        complexity = "Simple"
        if rent_paid > 0 or ded_raw["medical_parents"] > 0:
            complexity = "Medium"
        if gross > 1500000 and (rent_paid > 0 and ded_raw["medical_parents"] > 0):
            complexity = "Complex"

        profile = TaxProfile(
            profile_id=pid,
            age=age,
            income=income_details,
            deductions=deduction_details,
            target_regime=target_regime,
            complexity_category=complexity,
        )
        
        # Ground truth NOT calculated to avoid circular validation
        # It should come from an independent source (official calculator, CA, etc.)
        
        return profile

    def generate_batch(self, count: int = 10) -> List[TaxProfile]:
        return [self.generate_profile() for _ in range(count)]

if __name__ == "__main__":
    # Quick test
    gen = TaxProfileGenerator()
    p = gen.generate_profile()
    print(p.model_dump_json(indent=2))
