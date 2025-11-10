"""Tests for security middleware."""
import pytest
from fastapi import FastAPI, Request, Response
from fastapi.testclient import TestClient
from starlette.types import ASGIApp, Scope, Receive, Send
from api.middleware.security import LocalHostOnlyMiddleware

# Test application
app = FastAPI()

# Add a test route
@app.get("/test")
async def test_route():
    return {"message": "Test successful"}

# Client for testing without middleware
client = TestClient(app)

# Client for testing with middleware
app_with_middleware = FastAPI()
app_with_middleware.add_middleware(LocalHostOnlyMiddleware)
app_with_middleware.include_router(app.router)
client_with_middleware = TestClient(app_with_middleware)

def test_localhost_allowed():
    """Test that localhost requests are allowed."""
    # Test with middleware
    response = client_with_middleware.get(
        "/test",
        headers={"host": "localhost:8000"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Test successful"}

def test_non_localhost_blocked():
    """Test that non-localhost requests are blocked."""
    # Test with middleware and non-localhost host
    response = client_with_middleware.get(
        "/test",
        headers={"host": "example.com"},
        # Override client IP for testing
        base_url="http://192.168.1.100"
    )
    assert response.status_code == 403
    assert response.json() == {"detail": "Access restricted to localhost only"}

def test_middleware_skips_non_http():
    """Test that non-HTTP requests are passed through."""
    # Create a test request with non-HTTP type
    scope = {"type": "websocket"}
    
    async def app(scope: Scope, receive: Receive, send: Send):
        await send({"type": "websocket.accept"})
    
    # Wrap with middleware
    middleware = LocalHostOnlyMiddleware(app)
    
    # Test that the middleware doesn't block non-HTTP requests
    async def receive():
        return {"type": "websocket.connect"}
    
    messages = []
    async def send(message):
        messages.append(message)
    
    import asyncio
    asyncio.run(middleware(scope, receive, send))
    
    # Should have passed through to the app's send
    assert messages == [{"type": "websocket.accept"}]
