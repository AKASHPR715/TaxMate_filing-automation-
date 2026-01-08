"""
Form Extraction API Component
Handles tax document upload and processing.
Uses: form_extraction_service.py
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pathlib import Path
import shutil
import asyncio
from concurrent.futures import ThreadPoolExecutor
import functools

from app.services.form_extraction_service import process_uploaded_file

router = APIRouter(prefix="/api", tags=["upload"])

# Create a dedicated thread pool for blocking I/O operations
_executor = ThreadPoolExecutor(max_workers=3)


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), doc_type: str = Form("form16a"), user_id: str = Form(None)):
    """
    Upload and process a tax document.
    
    Args:
        file: Uploaded PDF file
        doc_type: Document type - options: "form16a", "form16b", "form26as", "ais"
        user_id: Optional user ID to associate document with
        
    Returns:
        dict: Upload status and extracted data
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path(__file__).resolve().parents[1] / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        # Use filename directly as it is now prefixed by the frontend
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the file in a separate thread to not block the event loop
        # Use our dedicated executor to avoid event loop conflicts
        loop = asyncio.get_event_loop()
        try:
            # Enforce a 10-minute timeout for extraction to match LlamaExtract logic
            # Use functools.partial to properly pass arguments to the executor
            func = functools.partial(
                process_uploaded_file,
                str(file_path),
                doc_type,
                user_id  # Pass user_id to service
            )
            extracted_data = await asyncio.wait_for(
                loop.run_in_executor(_executor, func),
                timeout=600.0 
            )
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=504, 
                detail="Extraction timed out. The document might be too complex or the service is unresponsive."
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
