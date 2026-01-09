"""
Form Extraction API Component
Handles tax document upload and processing.
Uses: form_extraction_service.py
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from pathlib import Path
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

from app.services.form_extraction_service import process_uploaded_file
from app.api.auth_routes import get_current_user

router = APIRouter(prefix="/api", tags=["upload"])

# Create a dedicated thread pool for blocking I/O operations
_executor = ThreadPoolExecutor(max_workers=3)


# ---------------------------------------------------------------------------- #
#                                 1. AUTO (SMART)                              #
# ---------------------------------------------------------------------------- #

@router.post("/upload/form16a")
async def upload_form16a(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """Upload Form 16 Part A"""
    return await _handle_upload(file, "form16a", current_user)

@router.post("/upload/form16b")
async def upload_form16b(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """Upload Form 16 Part B"""
    return await _handle_upload(file, "form16b", current_user)

@router.post("/upload/ais")
async def upload_ais(
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_user)
):
    """Upload AIS"""
    return await _handle_upload(file, "ais", current_user)


async def _handle_upload(file: UploadFile, doc_type: str, current_user: dict):
    try:
        user_id = str(current_user["_id"])
        
        # Create upload directory if it doesn't exist
        upload_dir = Path(__file__).resolve().parents[1] / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the file in a separate thread
        loop = asyncio.get_event_loop()
        try:
            func = functools.partial(
                process_uploaded_file,
                str(file_path),
                doc_type,
                user_id
            )
            extracted_data = await asyncio.wait_for(
                loop.run_in_executor(_executor, func),
                timeout=600.0 
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504, 
                detail="Extraction timed out."
            )
        
        return {
            "message": "File processed successfully",
            "file_path": str(file_path),
            "data": extracted_data
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")
