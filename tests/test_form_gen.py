import sys
from pathlib import Path
import json

# Add src to path
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from services.form_generation import generate_filing_forms

def test_generation():
    # Dummy Extracted Data
    extracted = {
        "Form_16_Part_B_123": {
            "employee_details": {
                "name": "JOHN DOE",
                "PAN": "ABCDE1234F",
                "address": "123 Main St"
            },
            "salary_details": {
                "total_salary": 1500000
            },
            "deductions_chapter_VIA": {
                "section_80C": 150000,
                "section_80D": 25000,
                "total_deductions": 175000
            },
             "tds_summary": [
                {
                    "amount_paid_credited": 1500000,
                    "tax_deducted": 150000
                }
            ],
            "employer_details": {
                "TAN": "DELE12345F",
                "name": "ACME Corp"
            }
        },
        "Form_16_Part_A_123": {
             "tds_summary": [
                {
                    "amount_paid_credited": 1500000,
                    "tax_deducted": 150000
                }
            ],
            "employer_details": {
                "TAN": "DELE12345F",
                "name": "ACME Corp"
            }
        }
    }
    
    # Dummy Computation Result
    computed = {
        "optimal_regime": "NEW",
        "new_tax": 125000,
        "new_taxable": 1325000,
        "old_tax": 140000,
        "old_taxable": 1325000
    }
    
    result = generate_filing_forms(extracted, computed)
    print(f"Test Result: {json.dumps(result, indent=2)}")
    
    # Verify file exists
    if Path(result["file_path"]).exists():
        print("✅ File created successfully.")
        
        # Read file to check content
        with open(result["file_path"]) as f:
            data = json.load(f)
            print("Keys in generated JSON:", data.keys())
            if "ITR" in data and "ITR1" in data["ITR"]:
                print("✅ ITR Structure verified.")
            else:
                print("❌ Invalid ITR Structure.")
    else:
        print("❌ File creation failed.")

if __name__ == "__main__":
    test_generation()
