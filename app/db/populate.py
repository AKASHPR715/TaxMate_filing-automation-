import sys
import os
import json
import glob
from pathlib import Path
from datetime import datetime
from bson import ObjectId

# Add project root to python path
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent.parent
sys.path.append(str(project_root))

from app.db.connection import get_sync_db
from app.db.models import (
    User, Form16PartA, Form16PartB, AIS, 
    Form16PartA_Schema, Form16PartB_Schema, AIS_Schema
)

def populate_db():
    print("🚀 Starting Database Population (New Schema)...")
    db = get_sync_db()
    
    # 1. Create Default User
    users_coll = db["users"]
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "full_name": "Test User",
        "pan_number": "ABCDE1234F",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    # Check if user exists
    user = users_coll.find_one({"email": user_data["email"]})
    if not user:
        result = users_coll.insert_one(user_data)
        user_id = result.inserted_id
        print(f"✔ Created User: {user_id}")
    else:
        user_id = user["_id"]
        print(f"ℹ Found existing User: {user_id}")
        
    # Helpers for insertion
    def insert_doc(collection_name, model_class, schema_class, data, source_file):
        coll = db[collection_name]
        
        # Avoid duplicates based on source_file for this user
        existing = coll.find_one({"user_id": user_id, "source_file": source_file})
        if existing:
            print(f"ℹ Skipping {collection_name} from {source_file} (already exists)")
            return

        try:
            # Validate and create model
            # Note: We need to ensure the data matches the schema. 
            # If data is raw JSON from extraction, it should map to Schema.
            # We add user_id and source_file.
            
            # Pydantic parsing
            valid_data = schema_class(**data)
            
            # DB Model
            db_doc = model_class(
                user_id=user_id,
                source_file=source_file,
                **valid_data.model_dump()
            )
            
            doc_dict = db_doc.model_dump(by_alias=True, exclude={"id"})
            coll.insert_one(doc_dict)
            print(f"✔ Inserted into {collection_name} from {source_file}")
            
        except Exception as e:
            print(f"❌ Error inserting {collection_name} from {source_file}: {e}")

    # 2. Populate from Extracted Data Directory
    extracted_dir = project_root / "app" / "data" / "extracted"
    
    # Fallback Sample Data if directory is empty
    has_files = False
    
    # Process Form 16A
    # (Assuming filenames contain specific keywords as per extraction service)
    # The extraction service outputs JSONs roughly matching the schema if LlamaParse worked well.
    # But if the dir is empty, we should create dummy data.
    
    if extracted_dir.exists():
        for file_path in extracted_dir.glob("*.json"):
            has_files = True
            filename = file_path.name.lower()
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    
                if "form16a" in filename or "part_a" in filename:
                    insert_doc("form16_part_as", Form16PartA, Form16PartA_Schema, data, file_path.name)
                elif "form16b" in filename or "part_b" in filename:
                    insert_doc("form16_part_bs", Form16PartB, Form16PartB_Schema, data, file_path.name)
                elif "ais" in filename:
                    insert_doc("ais", AIS, AIS_Schema, data, file_path.name)
                    
            except Exception as e:
                print(f"⚠ Skipping file {filename}: {e}")
    
    if not has_files:
        print("⚠ No extracted JSON files found. Creating dummy data...")
        create_dummy_data(user_id, db)

    print("✨ Database Population Complete!")

def create_dummy_data(user_id, db):
    # Dummy Form 16 Part B
    f16b_data = {
        "employer_details": {
            "name": "Acme Corp", "address": "Metropolis", "PAN": "ACME12345X", 
            "TAN": "TAN12345", "contact_number": "123", "email": "hr@acme.com"
        },
        "employee_details": {
            "name": "Test User", "address": "Gotham", "PAN": "ABCDE1234F"
        },
        "assessment_details": {
            "assessment_year": "2024-25", "period_from": "2023-04-01", "period_to": "2024-03-31",
            "CIT_TDS_office": "Circle 1"
        },
        "salary_details": {
            "salary_u_s_17_1_a": 1200000, "salary_u_s_17_1_b": 0, "salary_u_s_17_3": 0,
            "total_salary": 1200000, "salary_from_other_employers": 0, "perquisites_u_s_17_2": 0
        },
        "exemptions_u_s_10": {
            "leave_travel_concession": 0, "gratuity": 0, "leave_encashment": 0,
            "house_rent_allowance": 100000, "commuted_pension": 0, "any_other_exemption": 0,
            "total_exemptions": 100000
        },
        "net_salary_after_exemptions": 1100000,
        "deductions_u_s_16": {
            "standard_deduction": 50000, "entertainment_allowance": 0,
            "professional_tax": 2400, "total_deductions": 52400
        },
        "income_chargeable_under_salary": 1047600,
        "other_income_reported": {
            "house_property_income": 0, "other_sources_income": 10000, "total_other_income": 10000
        },
        "gross_total_income": 1057600,
        "deductions_chapter_VIA": {
            "section_80C": 150000, "section_80CCC": 0, "section_80CCD_1": 0,
            "section_80CCD_1B": 0, "section_80CCD_2": 50000, "section_80D": 25000,
            "section_80E": 0, "section_80G": 0, "section_80TTA": 0, 
            "any_other_deductions": 0, "total_deductions": 225000
        },
        "taxable_income": 832600,
        "tax_computation": {
            "income_tax": 50000, "surcharge": 0, "rebate_u_s_87A": 0,
            "health_education_cess": 2000, "relief_u_s_89": 0,
            "total_tax_liability": 52000, "tax_deducted_at_source": 60000,
            "net_tax_payable_or_refundable": -8000
        },
        "certificate_details": {
            "certificate_number": "CERT123", "issue_date": "2024-06-15",
            "place": "Metropolis", "signatory_name": "Lex", "designation": "CEO"
        }
    }
    
    try:
        db.form16_part_bs.insert_one({
            "user_id": user_id,
            "source_file": "dummy_part_b.pdf",
            "created_at": datetime.utcnow(),
            **f16b_data
        })
        print("✔ Created Dummy Form 16 Part B")
    except Exception as e:
        print(f"❌ Failed to create dummy data: {e}")


if __name__ == "__main__":
    populate_db()
