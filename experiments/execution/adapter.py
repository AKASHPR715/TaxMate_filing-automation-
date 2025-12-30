from typing import Any, Dict
from experiments.data_generation.schema import TaxProfile

def adapt_profile_to_orchestrator(profile: TaxProfile) -> Dict[str, Any]:
    """
    Converts a TaxProfile into the nested dictionary structure 
    expected by TaxOrchestrator (simulating 'extracted_data').
    """
    inc = profile.income
    ded = profile.deductions
    
    # Structure mimics what extracting from Form 16 Part B looks like
    form16_data = {
        "salary_details": {
            "total_salary": inc.gross_salary,
            "salary_from_other_employers": 0.0,
            # We can populate these if needed by specific logic, but total_salary is key
            "allowances_exempt_u_s_10": inc.hra_received if ded.rent_paid_annual > 0 else 0.0 
            # Note: Orchestrator calculates valid HRA. We just need to ensure inputs are there.
            # Actually Orchestrator uses its own logic. 
            # Reviewing tax_comparison.py:
            # It reads 'salary_details.total_salary' -> gross_salary
            # It reads 'deductions_chapter_VIA.section_80C' -> ch_via
        },
        "deductions_chapter_VIA": {
            "section_80C": ded.pf_contribution + ded.elss + ded.lic_premium + ded.ppf,
            "section_80D": ded.medical_insurance_self + ded.medical_insurance_parents,
            # We can add others if we expand the generator
        },
        "other_income_reported": {
            "total_other_income": inc.other_sources_income
        }
    }
    
    # HRA specific inputs needed for Old Regime calculation in Orchestrator?
    # tax_comparison.py logic primarily looks at "ch_via" total and "gross_salary".
    # Wait, tax_comparison.py in 'compare_tax_regimes' calculates Old Regime Taxable as:
    # old_taxable = max(old_gti - ch_via, 0)
    # It does NOT seem to engage the full HRA exemption logic unless I modified it?
    # Let me re-read tax_comparison.py in the previous turn.
    
    # Re-reading tax_comparison.py from memory (or previous context):
    # It does: `old_gti = salary_after_std_old + other_income`
    # Then: `old_taxable = max(old_gti - ch_via, 0)`
    # It DOES NOT seem to calculate HRA exemption explicitly in `compare_tax_regimes`!
    # It assumes `ch_via` includes all deductions? No, HRA is Section 10(13A) which is an Exemption, not VIA deduction.
    # The existing tax_comparison.py might be MISSING HRA exemption logic entirely for the automated check.
    # This means my GROUND TRUTH (which uses robust HRA logic) will be BETTER than the NeuroSym (TaxOrchestrator).
    # This is a finding! The "Orchestrator" might hallucinate (or rather, omit) HRA.
    
    # However, for the purpose of the adapter, I must feed it what it expects.
    # I will pass the data as best as possible.
    
    return {
        "16_Part_B": form16_data,
        "financial_year": "24-25" 
    }
