"""
Cable Assistant API Server

A FastAPI server providing HTTP endpoints for the Cable Assistant.
Handles chat completions, streaming, and conversation management.
"""
import os
from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import json

from src.assistant import CableAssistant, Message, MessageRole, ChatResponse

# Initialize FastAPI app
app = FastAPI(
    title="Cable Assistant API",
    description="API for the Cable Assistant - A lightweight OpenAI chat interface",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response schemas
class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    name: Optional[str] = None

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: str = "gpt-4-1106-preview"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    stream: bool = False
    max_tokens: Optional[int] = None

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Dict[str, Any]]
    usage: Optional[Dict[str, int]] = None

# Dependency to get the assistant
def get_assistant():
    return CableAssistant()

# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Response status: {response.status_code}")
    return response

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "cable-assistant"}

# Chat completion endpoint
@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completion(
    request: ChatRequest,
    assistant: CableAssistant = Depends(get_assistant)
):
    """Handle chat completion requests."""
    try:
        # Convert messages to the format expected by the assistant
        messages = [
            Message(role=msg.role, content=msg.content, name=msg.name)
            for msg in request.messages
        ]
        
        # For non-streaming requests
        if not request.stream:
            # Use the last user message
            last_message = next(
                (msg for msg in reversed(messages) if msg.role == MessageRole.USER),
                None
            )
            
            if not last_message:
                raise HTTPException(status_code=400, detail="No user message found in request")
            
            # Get the response
            response = assistant.chat(
                message=last_message.content,
                temperature=request.temperature,
                max_tokens=request.max_tokens
            )
            
            # Format the response to match OpenAI's format
            return {
                "id": "chatcmpl-123",  # In a real app, generate a unique ID
                "object": "chat.completion",
                "created": 1677652288,  # Current timestamp
                "model": request.model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.content
                    },
                    "finish_reason": "stop"
                }],
                "usage": response.usage or {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
        
        # For streaming requests
        async def event_stream():
            try:
                # Use the last user message for streaming
                last_message = next(
                    (msg for msg in reversed(messages) if msg.role == MessageRole.USER),
                    None
                )
                
                if not last_message:
                    yield "data: " + json.dumps({"error": "No user message found"}) + "\n\n"
                    return
                
                # Stream the response
                full_response = []
                for chunk in assistant.stream_chat(
                    message=last_message.content,
                    temperature=request.temperature,
                    max_tokens=request.max_tokens
                ):
                    # Format as Server-Sent Events (SSE)
                    data = {
                        "id": "chatcmpl-123",
                        "object": "chat.completion.chunk",
                        "created": 1677652288,
                        "model": request.model,
                        "choices": [{
                            "delta": {"content": chunk},
                            "index": 0,
                            "finish_reason": None
                        }]
                    }
                    yield f"data: {json.dumps(data)}\n\n"
                    full_response.append(chunk)
                
                # Send the final done message
                done_data = {
                    "id": "chatcmpl-123",
                    "object": "chat.completion.chunk",
                    "created": 1677652288,
                    "model": request.model,
                    "choices": [{
                        "delta": {},
                        "index": 0,
                        "finish_reason": "stop"
                    }]
                }
                yield f"data: {json.dumps(done_data)}\n\n"
                yield "data: [DONE]\n\n"
                
            except Exception as e:
                error_data = {"error": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
        
        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Error handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"message": exc.detail, "type": "api_error"}}
    )

def start_server(host: str = "0.0.0.0", port: int = 8000):
    """Start the FastAPI server."""
    print(f"Starting Cable Assistant server on http://{host}:{port}")
    print("API Documentation: http://localhost:8000/docs")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    start_server()
