import asyncio
from typing import Any, Dict, List

import pytest
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from starlette.testclient import TestClient

from api.middleware import security as sec


class DummySettings:
    def __init__(self):
        self.security_headers: Dict[str, str] = {
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "no-referrer",
        }
        # Provide CORS configuration
        self.allow_origins: List[str] = ["*"]
        self.allow_credentials: bool = True
        self.allow_methods: List[str] = ["GET", "POST"]
        self.allow_headers: List[str] = ["*"]


def create_app(settings: Any) -> FastAPI:
    app = FastAPI()

    @app.get("/ping")
    def ping():
        return {"ok": True}

    sec.setup_security_middleware(app, settings)
    return app


def test_security_headers_and_protections_applied():
    settings = DummySettings()
    app = create_app(settings)
    client = TestClient(app)

    res = client.get("/ping")
    assert res.status_code == 200

    # Security headers from settings
    for h, v in settings.security_headers.items():
        assert res.headers.get(h) == v

    # XSS header
    assert res.headers.get("X-XSS-Protection") == "1; mode=block"

    # CSP header default policy
    assert res.headers.get("Content-Security-Policy") == "default-src 'self'; script-src 'self'"


def test_cors_middleware_added_when_settings_provide_cors():
    settings = DummySettings()
    app = create_app(settings)

    # FastAPI stores user middleware configurations in app.user_middleware
    assert any(m.cls.__name__ == "CORSMiddleware" for m in app.user_middleware)


def test_limiter_attached_if_available():
    settings = DummySettings()
    app = create_app(settings)

    # If slowapi is installed, limiter is not None and must be attached
    if sec.limiter is not None:
        assert hasattr(app.state, "limiter")
        assert app.state.limiter is sec.limiter
    else:
        # Nothing to assert when slowapi is not installed
        assert True


@pytest.mark.asyncio
async def test_localhost_only_middleware_allows_localhost():
    # Build a simple ASGI app that returns 200
    async def inner_app(scope, receive, send):
        response = PlainTextResponse("ok", status_code=200)
        await response(scope, receive, send)

    middleware = sec.LocalHostOnlyMiddleware(inner_app)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "client": ("127.0.0.1", 12345),
    }

    messages = []

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        messages.append(message)

    await middleware(scope, receive, send)

    # First message should be response start with 200
    assert any(m.get("type") == "http.response.start" and m.get("status") == 200 for m in messages)


@pytest.mark.asyncio
async def test_localhost_only_middleware_blocks_non_localhost():
    # Build a simple ASGI app that returns 200
    async def inner_app(scope, receive, send):
        response = PlainTextResponse("ok", status_code=200)
        await response(scope, receive, send)

    middleware = sec.LocalHostOnlyMiddleware(inner_app)

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "client": ("8.8.8.8", 12345),
    }

    messages = []

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        messages.append(message)

    await middleware(scope, receive, send)

    # Should start a 403 response
    start_msgs = [m for m in messages if m.get("type") == "http.response.start"]
    assert start_msgs, f"No response start message: {messages!r}"
    assert start_msgs[0].get("status") == 403
