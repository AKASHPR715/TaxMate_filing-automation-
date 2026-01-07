"""
Chat API Component
Handles WebSocket chat endpoint for interactive tax assistance.
Uses: chat_service.py
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import json
import asyncio

from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for chat functionality.
    
    Supports two message types:
    - context_update: Update chat context with tax data
    - message: Send user message and receive bot response
    """
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
