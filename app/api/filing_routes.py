import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import glob
import os

# Import form generation service to trigger regeneration
try:
    from app.services.form_generation_service import generate_filing_forms
except ImportError:
    # Handle potentially different import paths if needed, though this should work
    pass

from app.api.auth_routes import get_current_user
from app.db.connection import get_sync_db
from bson import ObjectId
from datetime import datetime


router = APIRouter(prefix="/api/filing", tags=["filing"])

logger = logging.getLogger("FilingAPI")

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
FILING_DIR = DATA_DIR / "filing"
USER_PROFILE_PATH = DATA_DIR / "user_profile.json"

class UpdateProfileRequest(BaseModel):
    updates: Dict[str, Any]

def load_user_profile() -> Dict[str, Any]:
    if USER_PROFILE_PATH.exists():
        try:
            with open(USER_PROFILE_PATH, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading user profile: {e}")
            return {}
    return {}

def save_user_profile(profile: Dict[str, Any]):
    try:
        with open(USER_PROFILE_PATH, "w") as f:
            json.dump(profile, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving user profile: {e}")
        raise HTTPException(status_code=500, detail="Failed to save user profile")

def find_missing_fields(data: Dict[str, Any], profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Scans the ITR data for proxy values and returns a list of fields that need attention.
    Checks against current profile values to verify if they are already 'fixed' but maybe not yet applied if form wasn't regenerated.
    """
    missing = []
    
    # Helper to check value
    def check(key_label, current_val, proxy_val, json_path):
        # If current value is the proxy, AND not in profile (or profile matches proxy?? no profile should satisfy)
        # Actually, if it's in the ITR as proxy, it's missing, unless user just updated profile and we haven't regenerated.
        is_missing = False
        if str(current_val) == str(proxy_val):
            is_missing = True
        
        # Check if we have a better value in profile
        profile_val = profile.get(key_label)
        
        if is_missing or (profile_val and str(current_val) != str(profile_val)):
             missing.append({
                "label": key_label,
                "current_value": current_val,
                "proxy_value": proxy_val,
                "json_path": json_path,
                "profile_value": profile_val # Suggest from profile if exists
            })

    # ITR-1 Structure assumptions (adjust based on actual schema)
    # We can use a recursive search or hardcode common paths
    
    # Traverse to Personal Info for ITR-1
    try:
        if "ITR" in data and "ITR1" in data["ITR"]:
            personal = data["ITR"]["ITR1"].get("PersonalInfo", {})
            address = personal.get("Address", {})
            
            check("mobile", address.get("MobileNo"), "9999999999", "ITR.ITR1.PersonalInfo.Address.MobileNo")
            check("email", address.get("EmailAddress"), "test@example.com", "ITR.ITR1.PersonalInfo.Address.EmailAddress")
            check("aadhaar", personal.get("AadhaarNo"), "123456789012", "ITR.ITR1.PersonalInfo.AadhaarNo")
            check("dob", personal.get("DOB"), "1990-01-01", "ITR.ITR1.PersonalInfo.DOB")
            
            # Father name might be under Verification or PersonalInfo depending on schema
            verification = data["ITR"]["ITR1"].get("Verification", {}).get("Declaration", {})
            check("father_name", verification.get("FatherName"), "FATHER NAME", "ITR.ITR1.Verification.Declaration.FatherName")

    except Exception as e:
        logger.error(f"Error scanning ITR-1: {e}")

    # ITR-2 Logic (similar, different paths)
    try:
        if "ITR" in data and "ITR2" in data["ITR"]:
             # Add ITR-2 paths if needed
             pass
    except Exception:
        pass

    return missing

@router.get("/latest/{itr_type}")
async def get_latest_filing(itr_type: str, current_user: dict = Depends(get_current_user)):
    """
    Get the latest generated JSON for the given ITR type (e.g., ITR1, ITR2).
    """
    clean_type = itr_type.replace("-", "")
    pattern = str(FILING_DIR / f"{clean_type}_*.json")
    files = glob.glob(pattern)
    
    if not files:
        # Return generic structure if no file found, to avoid UI breaking? 
        # Or 404. Let's return 404 but with message
        raise HTTPException(status_code=404, detail=f"No filing generated for {itr_type}")
    
    # Get latest file
    latest_file = max(files, key=os.path.getctime)
    
    try:
        with open(latest_file, "r") as f:
            data = json.load(f)
            
        profile = load_user_profile()
        missing_fields = find_missing_fields(data, profile)
        
        return {
            "file_path": latest_file,
            "filename": os.path.basename(latest_file),
            "data": data,
            "missing_fields": missing_fields,
            "user_profile": profile
        }
    except Exception as e:
        logger.error(f"Error reading filing: {e}")
        raise HTTPException(status_code=500, detail="Error reading filing data")

@router.post("/update")
async def update_filing_profile(request: UpdateProfileRequest, background_tasks: BackgroundTasks, current_user: dict = Depends(get_current_user)):
    """
    Updates the user profile with new values and triggers a regeneration/update of the ITR forms.
    """
    current_profile = load_user_profile()
    
    # Update profile
    current_profile.update(request.updates)
    save_user_profile(current_profile)
    
    # Ideally, we should trigger the form generation service to re-run with the existing extracted data
    # But checking if we have extracted data might be complex if it's not persisted in a simple way.
    # However, form_generation_service saves the ITR json.
    # For now, we will just update the user_profile.
    # PROACTIVE: Let's try to update the latest JSON directly as a quick fix, 
    # ensuring the user sees the update immediately in the "View ITR" modal.
    
    # Find latest ITR1 (default priority)
    files = glob.glob(str(FILING_DIR / "ITR1_*.json"))
    if files:
        latest_file = max(files, key=os.path.getctime)
        try:
            with open(latest_file, "r") as f:
                data = json.load(f)
            
            # Apply updates deep into the JSON - manual Mapping for now
            # This logic mimics populate_itr_form but applies overrides
            itr1 = data.get("ITR", {}).get("ITR1", {})
            
            if "mobile" in request.updates:
                if "PersonalInfo" in itr1 and "Address" in itr1["PersonalInfo"]:
                    itr1["PersonalInfo"]["Address"]["MobileNo"] = int(request.updates["mobile"])
            
            if "email" in request.updates:
                 if "PersonalInfo" in itr1 and "Address" in itr1["PersonalInfo"]:
                    itr1["PersonalInfo"]["Address"]["EmailAddress"] = request.updates["email"]

            if "aadhaar" in request.updates:
                 if "PersonalInfo" in itr1:
                    itr1["PersonalInfo"]["AadhaarNo"] = request.updates["aadhaar"]
            
            if "father_name" in request.updates:
                 if "Verification" in itr1 and "Declaration" in itr1["Verification"]:
                     itr1["Verification"]["Declaration"]["FatherName"] = request.updates["father_name"]
            
            # Save back
            with open(latest_file, "w") as f:
                json.dump(data, f, indent=4)
                
        except Exception as e:
            logger.error(f"Failed to hot-patch ITR file: {e}")
            # Non-critical, since profile is saved for next generation

    return {"status": "success", "message": "Profile updated", "profile": current_profile}

# ---------------------------------------------------------------------------- #
#                                 DB BASED ITR ENDPOINTS                       #
# ---------------------------------------------------------------------------- #

@router.get("/itr/db/{itr_id}")
async def get_itr_from_db(itr_id: str, current_user: dict = Depends(get_current_user)):
    """
    Fetch a specific ITR document from MongoDB by ID.
    Human-in-the-Loop: Agent fetches this to review before filing.
    """
    user_id = str(current_user["_id"])
    try:
        db = get_sync_db()
        if not ObjectId.is_valid(itr_id):
             raise HTTPException(status_code=400, detail="Invalid ITR ID format")
             
        itr = db.itrs.find_one({"_id": ObjectId(itr_id), "user_id": ObjectId(user_id)})
        
        if not itr:
            raise HTTPException(status_code=404, detail="ITR document not found")
            
        # Convert ObjectId to str for JSON response
        itr["_id"] = str(itr["_id"])
        itr["user_id"] = str(itr["user_id"])
        if "form16_part_a_ids" in itr:
            itr["form16_part_a_ids"] = [str(i) for i in itr["form16_part_a_ids"]]
        if "form16_part_b_ids" in itr:
            itr["form16_part_b_ids"] = [str(i) for i in itr["form16_part_b_ids"]]
        if "ais_ids" in itr:
            itr["ais_ids"] = [str(i) for i in itr["ais_ids"]]
            
        return itr
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error fetching ITR from DB: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

class UpdateITRRequest(BaseModel):
    updates: Dict[str, Any]
    status: Optional[str] = None # e.g. "REVIEWED", "APPROVED"

@router.put("/itr/db/{itr_id}")
async def update_itr_in_db(
    itr_id: str, 
    request: UpdateITRRequest, 
    current_user: dict = Depends(get_current_user)
):
    """
    Update ITR data in MongoDB.
    Human-in-the-Loop pattern: User submits corrections via UI, which calls this endpoint.
    """
    user_id = str(current_user["_id"])
    try:
        db = get_sync_db()
        if not ObjectId.is_valid(itr_id):
             raise HTTPException(status_code=400, detail="Invalid ITR ID format")
        
        # Verify ownership
        itr = db.itrs.find_one({"_id": ObjectId(itr_id), "user_id": ObjectId(user_id)})
        if not itr:
            raise HTTPException(status_code=404, detail="ITR document not found")

        update_fields = {}
        
        # 1. Update structure (Manual recursive update or full replace?)
        # For now, we assume 'updates' contains partial paths or full replacement of sections.
        # But commonly, the UI sends the modified 'itr_submission'.
        
        if "itr_submission" in request.updates:
            update_fields["itr_submission"] = request.updates["itr_submission"]
        else:
            # Flatten/Merge updates logic if needed, or just allow updating specific keys
            # For simplicity in this iteration: expect full or partial dicts under specific keys
            for key, value in request.updates.items():
                # Prevent updating restricted fields
                if key not in ["_id", "user_id", "created_at"]:
                    update_fields[key] = value

        if request.status:
            update_fields["status"] = request.status
            
        update_fields["updated_at"] = datetime.utcnow()
        
        result = db.itrs.update_one(
            {"_id": ObjectId(itr_id)},
            {"$set": update_fields}
        )
        
        if result.modified_count == 0:
             logger.info(f"ITR {itr_id} update request received but no changes detected.")

        return {"status": "success", "message": "ITR updated successfully"}
        
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error updating ITR in DB: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update ITR: {str(e)}")
