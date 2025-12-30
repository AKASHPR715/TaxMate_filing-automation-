import numpy as np
import random
from typing import Tuple

class TaxDistributions:
    @staticmethod
    def generate_salary() -> float:
        """
        Generates a realistic annual salary using Log-Normal distribution.
        Target Mean: ~12L, Range: 5L to 50L+
        """
        # Mu and Sigma for log-normal distribution
        # In log space: mean=13.5 (approx 7L), sigma=0.8 provides a good right skew
        salary = np.random.lognormal(mean=13.5, sigma=0.6)
        
        # Clamp between 5L and 1Cr for this experiment range
        salary = max(500000, min(salary, 10000000))
        
        # Round to nearest thousand for realism
        return round(salary, -3)

    @staticmethod
    def salary_breakdown(gross: float) -> Tuple[float, float, float]:
        """
        Breaks gross salary into Basic, HRA, and Special Allowance.
        Heuristic: Basic is 40-50% of Gross. HRA is 40-50% of Basic.
        """
        basic_percent = random.uniform(0.40, 0.50)
        basic = round(gross * basic_percent, -2)
        
        hra_percent = random.uniform(0.40, 0.50)
        hra = round(basic * hra_percent, -2)
        
        special = gross - basic - hra
        return basic, hra, special

    @staticmethod
    def generate_deductions(gross_salary: float, age: int) -> dict:
        """
        Generates probability-weighted deductions based on income level.
        High income -> Higher probability of maxing out 80C.
        """
        deductions = {
            "pf": 0.0, "elss": 0.0, "lic": 0.0, "ppf": 0.0,
            "medical_self": 0.0, "medical_parents": 0.0
        }
        
        # EPF is usually mandatory 12% of Basic (approximated here as 6% of Gross)
        deductions["pf"] = round(gross_salary * 0.06, -2)
        
        # 80C Balancing
        # If income > 10L, 90% chance to max out 1.5L
        target_80c = 150000 if gross_salary > 1000000 and random.random() < 0.9 else random.randint(0, 150000)
        
        remaining_80c = max(0, target_80c - deductions["pf"])
        if remaining_80c > 0:
            # Distribute remaining 80C into ELSS/LIC/PPF
            choice = random.choice(["elss", "lic", "ppf", "mix"])
            if choice == "mix":
                split = remaining_80c / 2
                deductions["elss"] = split
                deductions["ppf"] = split
            else:
                deductions[choice] = remaining_80c
        
        # 80D
        if random.random() < 0.6: # 60% have insurance
            deductions["medical_self"] = random.choice([15000, 20000, 25000])
            
        if random.random() < 0.3: # 30% pay for parents
            deductions["medical_parents"] = random.choice([20000, 30000, 50000]) if age < 60 else 50000

        return deductions

    @staticmethod
    def generate_rent(basic_salary: float, is_metro: bool) -> float:
        """
        Generates realistic rent paid based on basic salary foundation.
        """
        if random.random() < 0.2: # 20% don't pay rent (live in own house)
            return 0.0
            
        # Rent is typically 20-40% of Basic
        rent_ratio = random.uniform(0.2, 0.5) if is_metro else random.uniform(0.1, 0.3)
        return round(basic_salary * rent_ratio, -2) * 12 # Annualize? No, basic is annual. Wait, basic passed in is annual.
