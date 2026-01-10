
import sys
import os
from pathlib import Path
from bson import ObjectId
import json

from bson import ObjectId
import json
from unittest.mock import MagicMock
import sys

# Add app to path
sys.path.append(str(Path(__file__).resolve().parents[1]))

# MOCK Qdrant to avoid lock errors
sys.modules["qdrant_client"] = MagicMock()
sys.modules["app.models.hybridsearch"] = MagicMock()
# We also need to mock where it's used if imports happen at top level
# But replacing the module in sys.modules might be enough if done early.
# However, app.main imports orchestrator -> tax_advisor -> hybridsearch
# Let's try to mock the specific class if possible, or just the whole module as above.

from fastapi.testclient import TestClient
from app.main import app
from app.api.auth_routes import get_current_user
from app.db.connection import get_sync_db

# Mock User
MOCK_USER_ID = str(ObjectId())
MOCK_USER = {"_id": MOCK_USER_ID, "username": "test_verifier"}

# Override Auth
def mock_get_current_user():
    return MOCK_USER

app.dependency_overrides[get_current_user] = mock_get_current_user

client = TestClient(app)
db = get_sync_db()

def setup_test_data():
    """Insert a dummy Form 16 Part B"""
    doc = {
        "user_id": ObjectId(MOCK_USER_ID),
        "source_file": "verification_test.pdf",
        "employer_details": {
            "name": "Test Company",
            "address": "123 Test St",
            "PAN": "ABCDE1234F",
            "TAN": "ABCD12345E",
            "contact_number": "9999999999",
            "email": "test@example.com"
        },
        "employee_details": {
            "name": "Test Employee",
            "address": "456 Employee Rd",
            "PAN": "ABCDE1234G"
        },
        "assessment_details": {
            "assessment_year": "2024-25",
            "period_from": "2023-04-01",
            "period_to": "2024-03-31",
            "CIT_TDS_office": "Test Office"
        },
        "salary_details": {
            "salary_u_s_17_1_a": 1000000,
            "salary_u_s_17_1_b": 0,
            "salary_u_s_17_3": 0,
            "total_salary": 1000000,
            "salary_from_other_employers": 0,
            "perquisites_u_s_17_2": 0
        },
        "exemptions_u_s_10": {
            "leave_travel_concession": 0,
            "gratuity": 0,
            "leave_encashment": 0,
            "house_rent_allowance": 0,
            "commuted_pension": 0,
            "any_other_exemption": 0,
            "total_exemptions": 0
        },
        "net_salary_after_exemptions": 1000000,
        "deductions_u_s_16": {
            "standard_deduction": 50000,
            "entertainment_allowance": 0,
            "professional_tax": 2400,
            "total_deductions": 52400
        },
        "income_chargeable_under_salary": 947600,
        "other_income_reported": {
            "house_property_income": 0,
            "other_sources_income": 0,
            "total_other_income": 0
        },
        "gross_total_income": 947600,
        "deductions_chapter_VIA": {
            "section_80C": 150000,
            "section_80CCC": 0,
            "section_80CCD_1": 0,
            "section_80CCD_1B": 0,
            "section_80CCD_2": 0,
            "section_80D": 0,
            "section_80E": 0,
            "section_80G": 0,
            "section_80TTA": 0,
            "any_other_deductions": 0,
            "total_deductions": 150000
        },
        "taxable_income": 797600,
        "tax_computation": {
            "income_tax": 0,
            "surcharge": 0,
            "rebate_u_s_87A": 0,
            "health_education_cess": 0,
            "relief_u_s_89": 0,
            "total_tax_liability": 0,
            "tax_deducted_at_source": 0,
            "net_tax_payable_or_refundable": 0
        },
        "certificate_details": {
            "certificate_number": "123",
            "issue_date": "2024-06-15",
            "place": "Test City",
            "signatory_name": "Signer",
            "designation": "Manager"
        }
    }
    
    result = db.form16_part_bs.insert_one(doc)
    return str(result.inserted_id)

def run_test():
    print("🚀 Starting verification of Update APIs")
    
    # 1. Setup Data
    doc_id = setup_test_data()
    print(f"✅ Created test document with ID: {doc_id}")
    
    try:
        # 2. Test GET All
        response = client.get("/api/details/all")
        assert response.status_code == 200
        data = response.json()
        assert len(data["form16b"]) >= 1
        found = False
        for item in data["form16b"]:
            if item["id"] == doc_id:
                found = True
                break
        assert found
        print("✅ GET /api/details/all successful")
        
        # 3. Test GET Single
        response = client.get(f"/api/details/form16b/{doc_id}")
        assert response.status_code == 200
        details = response.json()
        assert details["employer_details"]["name"] == "Test Company"
        print(f"✅ GET /api/details/form16b/{doc_id} successful")
        
        # 4. Test PUT Update
        update_payload = {
            "employer_details": {
                "name": "Updated Test Company",
                # NOTE: In a real partial update, we merge. 
                # Our simple service implementation does a $set on the keys provided.
                # If we provide the full nested object, it replaces the nested object.
                # So we must include all fields if we replacing the whole object, 
                # OR we need to modify our service to support dot notation for deep partial updates.
                # For this test, I will provide the FULL employer details object with the change, 
                # mimicking a frontend that sends the section back.
                
                "address": "123 Test St",
                "PAN": "ABCDE1234F",
                "TAN": "ABCD12345E",
                "contact_number": "9999999999",
                "email": "test@example.com"
            }
        }
        
        response = client.put(f"/api/details/form16b/{doc_id}", json=update_payload)
        if response.status_code != 200:
            print(f"❌ Update failed: {response.text}")
        assert response.status_code == 200
        updated_doc = response.json()
        assert updated_doc["employer_details"]["name"] == "Updated Test Company"
        print(f"✅ PUT /api/details/form16b/{doc_id} successful")
        
        # 5. Verify Persistence
        response = client.get(f"/api/details/form16b/{doc_id}")
        assert response.json()["employer_details"]["name"] == "Updated Test Company"
        print(f"✅ Persistence verified")

    finally:
        # Cleanup
        db.form16_part_bs.delete_one({"_id": ObjectId(doc_id)})
        print("🧹 Data cleaned up")

if __name__ == "__main__":
    run_test()
