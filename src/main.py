import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import shutil
import os

# Add src to path so we can import services
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from services.tax_advisor import get_tax_advice
from services.form_extraction import process_uploaded_file
from services.orchestrator import run_orchestrator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/analyze")
async def analyze_taxes():
    """
    Run the full tax analysis orchestrator.
    """
    try:
        # Run the orchestrator logic
        # Run in executor to avoid blocking
        loop = asyncio.get_event_loop()
        # Use a prompt that specifically asks for recommendations based on the analysis
        prompt = "Analyze my tax situation and provide detailed recommendations for next year's tax planning, specifically highlighting underutilized 80C, 80D, and 80CCD limits."
        result = await loop.run_in_executor(None, run_orchestrator, prompt)
        
        return result
    except Exception as e:
        print(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...), doc_type: str = Form("form16a")):
    """
    Upload and process a tax document.
    doc_type options: "form16a", "form16b", "form26as", "ais"
    """
    try:
        # Create upload directory if it doesn't exist
        upload_dir = Path(__file__).resolve().parents[1] / "data" / "uploads"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded file
        file_path = upload_dir / f"{doc_type}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Process the file in a separate thread to not block the event loop
        loop = asyncio.get_event_loop()
        extracted_data = await loop.run_in_executor(
            None, 
            process_uploaded_file, 
            str(file_path), 
            doc_type
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

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive text from client
            data = await websocket.receive_text()
            
            # Send acknowledgement or "thinking" state if needed (optional)
            # await websocket.send_text(json.dumps({"type": "status", "message": "Thinking..."}))

            # Process with Orchestrator to get context-aware advice
            loop = asyncio.get_event_loop()
            
            # We run the full orchestrator for every query to ensure latest context
            # In a prod system, you might want to cache the "extraction" and "computation" steps
            # and only re-run the advisory part. For now, running full logic is safer for correctness.
            result = await loop.run_in_executor(None, run_orchestrator, data)
            
            # The orchestrator returns a state dictionary. 
            # We want to send the "advisory_result" back to the chat.
            # If advisory_result is empty (which might happen if steps fail), we fallback to a generic message.
            response_text = result.get("advisory_result")
            if not response_text:
                if result.get("errors"):
                     response_text = f"I encountered some errors: {'; '.join(result['errors'])}"
                else:
                     response_text = "I couldn't generate specific advice. Please try scanning your documents first."

            # Send response back to client
            await websocket.send_text(json.dumps({
                "type": "message",
                "content": response_text,
                "sender": "bot"
            }))
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        try:
            await websocket.send_text(json.dumps({
                "type": "error",
                "content": "An error occurred processing your request."
            }))
        except:
            pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
