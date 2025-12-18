import sys
import os
import json
import logging

# Add src to path
sys.path.append(os.path.abspath("src"))

from services.form_generation import generate_itr_json, save_filing_data

# Mock Data (based on ANISH JOSEPH's profile)
EXTRACTED_DATA = {
    "Form_16_Part_A": {
        "assessee_details": {
            "name": "ANISH JOSEPH",
            "PAN": "ARMPJ1889M",
            "address": "VALEMPARAMBIL, XI/306 MNRA 40, MANNAD LANE, AMBALAMUKE PEROORKADA, TRIVANDRUM - 695005 Kerala"
        }
    },
    "AIS": {
        # Trigger ITR-2
        "securities_transactions": [{"details": "Stock Sale"}] 
    }
}

COMPUTATION_RESULT = {
    "gross_salary": 2652104,
    "other_income": 0,
    "ch_via": 764804,
    "optimal_regime": "OLD",
    "old_tax": 363690,
    "new_tax": 470631,
    "old_taxable": 1887300,
    "new_taxable": 2602104,
    "financial_year": "24-25"
}

def run_test():
    print("Test 1: Generating ITR-2 (Expected)")
    payload = generate_itr_json(EXTRACTED_DATA, COMPUTATION_RESULT)
    
    # Verify Critical Structure Points
    try:
        assert payload["ITR"]["ITR2"]["Form_ITR2"]["FormName"] == "ITR-2"
        # Check PartA_GEN1 existence (The fix)
        pan = payload["ITR"]["ITR2"]["PartA_GEN1"]["PersonalInfo"]["PAN"]
        print(f"✔ Found PAN in PartA_GEN1: {pan}")
        
        # Check PartB-TI existence (The fix)
        income = payload["ITR"]["ITR2"]["PartB-TI"]["GrossTotalIncome"]
        print(f"✔ Found GrossTotalIncome in PartB-TI: {income}")
        
        filepath = save_filing_data(payload)
        print(f"✔ File saved to: {filepath}")
        
    except KeyError as e:
        print(f"❌ Verification Failed. Missing Key: {e}")
        print("Dump of generated payload structure keys:")
        print(payload.keys())
        if "ITR" in payload:
            print(payload["ITR"].get("ITR2", {}).keys())
    except AssertionError as e:
        print(f"❌ Assertion Failed: {e}")

if __name__ == "__main__":
    run_test()
