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
from services.orchestrator import TaxOrchestrator, run_orchestrator
from services.chat_service import ChatService
from typing import Dict, Any

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/details/extract")
async def extract_details():
    """
    Trigger extraction only and return the raw data for user review.
    """
    try:
        loop = asyncio.get_event_loop()
        boss = TaxOrchestrator()
        # Run extraction in executor
        extracted_data = await loop.run_in_executor(None, boss.run_extraction_only)
        return extracted_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/details/calculate")
async def calculate_with_details(data: Dict[str, Any]):
    """
    Receive confirmed/modified data and run tax computation.
    """
    try:
        loop = asyncio.get_event_loop()
        boss = TaxOrchestrator()
        # Run computation in executor
        result_state = await loop.run_in_executor(
            None, 
            boss.run_computation_with_data, 
            data, 
            "Finalize Tax Calculation"
        )
        return result_state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        try:
            # Enforce a 10-minute timeout for extraction to match LlamaExtract logic
            extracted_data = await asyncio.wait_for(
                loop.run_in_executor(
                    None, 
                    process_uploaded_file, 
                    str(file_path), 
                    doc_type
                ),
                timeout=600.0 
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=504, detail="Extraction timed out. The document might be too complex or the service is unresponsive.")
        
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
    
    # Create a new ChatService instance for this connection
    chat_service = ChatService()
    
    try:
        while True:
            # Receive text from client
            raw_data = await websocket.receive_text()
            
            try:
                payload = json.loads(raw_data)
            except json.JSONDecodeError:
                # Handle plain text if legacy or simple test
                payload = {"type": "message", "content": raw_data}

            msg_type = payload.get("type")
            
            if msg_type == "context_update":
                # User uploaded a form; update context
                context_data = payload.get("data", {})
                confirmation = chat_service.set_context(context_data)
                
                # Acknowledge context update
                await websocket.send_text(json.dumps({
                    "type": "message", 
                    "content": confirmation,
                    "sender": "bot"
                }))
                
            elif msg_type == "message":
                user_message = payload.get("content", "")
                
                # Get response from the chat service
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, 
                    chat_service.get_response, 
                    user_message
                )
                
                # Send response back to client
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "content": response,
                    "sender": "bot"
                }))
                
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"Error in websocket loop: {e}")
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
