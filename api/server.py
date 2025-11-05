#!/usr/bin/env python3
"""
Direct OpenAI API Server
Simple FastAPI server with direct OpenAI integration.
No middlewares, no complex linting - just clean API endpoints.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from .client import DirectOpenAIClient, get_client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response models
class ChatRequest(BaseModel):
    """Chat completion request."""
    messages: List[Dict[str, str]]
    model: str = "gpt-3.5-turbo"
    max_tokens: Optional[int] = None
    temperature: float = 0.7

class SimpleChatRequest(BaseModel):
    """Simple chat request."""
    prompt: str
    model: str = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    """Chat completion response."""
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str

# Create FastAPI app
app = FastAPI(
    title="Direct OpenAI API",
    description="Clean, simple OpenAI API integration",
    version="1.0.0"
)

# Initialize client
client = None

@app.on_event("startup")
async def startup_event():
    """Initialize OpenAI client on startup."""
    global client
    try:
        client = get_client()
        if client.test_connection():
            logger.info("OpenAI client initialized successfully")
        else:
            logger.error("Failed to initialize OpenAI client")
    except Exception as e:
        logger.error(f"Startup failed: {e}")

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Direct OpenAI API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    if client and client.test_connection():
        return {"status": "healthy", "openai": "connected"}
    else:
        return {"status": "unhealthy", "openai": "disconnected"}

@app.post("/chat", response_model=ChatResponse)
async def chat_completion(request: ChatRequest):
    """
    Chat completion endpoint.
    
    Direct integration with OpenAI chat completions API.
    See: https://platform.openai.com/docs/api-reference/chat
    """
    if not client:
        raise HTTPException(status_code=503, detail="OpenAI client not initialized")
    
    try:
        response = await client.chat_completion(
            messages=request.messages,
            model=request.model,
            max_tokens=request.max_tokens,
            temperature=request.temperature
        )
        
        return ChatResponse(**response)
        
    except Exception as e:
        logger.error(f"Chat completion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/simple")
async def simple_chat(request: SimpleChatRequest):
    """
    Simple chat endpoint.
    
    Takes a prompt and returns a response.
    """
    if not client:
        raise HTTPException(status_code=503, detail="OpenAI client not initialized")
    
    try:
        response = await client.simple_chat(request.prompt, request.model)
        return {"response": response}
        
    except Exception as e:
        logger.error(f"Simple chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
async def get_models():
    """
    Get available OpenAI models.
    
    Returns list of available models from OpenAI API.
    """
    if not client:
        raise HTTPException(status_code=503, detail="OpenAI client not initialized")
    
    try:
        models = await client.get_models()
        return {"models": models}
        
    except Exception as e:
        logger.error(f"Failed to get models: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    run_server()
