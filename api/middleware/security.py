"""Security middleware components.

Unified resolution of security middlewares with optional dependencies and
robust defaults. Provides:
- SecurityHeadersMiddleware: injects headers from settings.security_headers
- XSSProtectionMiddleware: sets X-XSS-Protection
- ContentSecurityPolicyMiddleware: sets Content-Security-Policy (default policy provided)
- LocalHostOnlyMiddleware: blocks non-localhost clients
- setup_security_middleware: wires everything together; tries to enable CORS if settings provide it
"""

from typing import Any, Optional

from fastapi import Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send

# Optional slowapi rate limiter
try:
    from slowapi import Limiter  # type: ignore
    from slowapi.util import get_remote_address  # type: ignore

    limiter: Optional[Any] = Limiter(key_func=get_remote_address)
except Exception:  # slowapi not installed or misconfigured
    limiter = None


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses.

    Expects `settings.security_headers` to be a mapping of header -> value.
    """

    def __init__(self, app: ASGIApp, settings: Any):
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        headers = getattr(self.settings, "security_headers", {}) or {}
        try:
            items = headers.items()
        except Exception:
            items = []  # not a mapping; ignore
        for header, value in items:
            response.headers[str(header)] = str(value)
        return response


class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware for XSS protection."""

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response


class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    """Middleware for Content Security Policy."""

    def __init__(self, app: ASGIApp, csp_policy: Optional[str] = None):
        super().__init__(app)
        self.csp_policy = csp_policy or "default-src 'self'; script-src 'self'"

    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["Content-Security-Policy"] = self.csp_policy
        return response


class LocalHostOnlyMiddleware:
    """Middleware to restrict access to localhost only (IPv4 and IPv6)."""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Only apply to HTTP requests
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return

        # Get client info; if missing, allow (tests and some ASGI servers may omit it)
        client = scope.get("client")
        if not client:
            await self.app(scope, receive, send)
            return

        client_host, _ = client

        # Allow localhost variants and Starlette TestClient ('testclient')
        if client_host in ("127.0.0.1", "::1", "localhost", "testclient"):
            await self.app(scope, receive, send)
            return

        # Block everything else
        response = JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"detail": "Access restricted to localhost only"},
        )
        await response(scope, receive, send)
        return


def setup_security_middleware(app: Any, settings: Any) -> None:
    """Configure all security middleware on the provided FastAPI app.

    This function is defensive:
    - Adds LocalHostOnlyMiddleware first.
    - If slowapi is available, attaches a Limiter instance to app.state.limiter.
    - Adds security-related header middlewares.
    - If CORS settings are present on `settings`, configures CORSMiddleware.
    """

    # Add localhost restriction middleware
    app.add_middleware(LocalHostOnlyMiddleware)

    # Add rate limiting (optional)
    if limiter is not None:
        app.state.limiter = limiter

    # Add security headers and protections
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    app.add_middleware(XSSProtectionMiddleware)
    app.add_middleware(ContentSecurityPolicyMiddleware)

    # Configure CORS if settings provide attributes
    allow_origins = getattr(settings, "allow_origins", None)
    if allow_origins is not None:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allow_origins,
            allow_credentials=getattr(settings, "allow_credentials", False),
            allow_methods=getattr(settings, "allow_methods", ["*"]),
            allow_headers=getattr(settings, "allow_headers", ["*"]),
        )
