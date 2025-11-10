"""Security middleware components."""

from fastapi import Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp, Scope, Receive, Send
from slowapi import Limiter
from slowapi.util import get_remote_address
from api.config.security import SecuritySettings

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    def __init__(self, app, settings: SecuritySettings):
        super().__init__(app)
        self.settings = settings
    
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Add security headers
        for header, value in self.settings.security_headers.items():
            response.headers[header] = value
        
        return response

class XSSProtectionMiddleware(BaseHTTPMiddleware):
    """Middleware for XSS protection."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response

class ContentSecurityPolicyMiddleware(BaseHTTPMiddleware):
    """Middleware for Content Security Policy."""
    
    def __init__(self, app, csp_policy: str = None):
        super().__init__(app)
        self.csp_policy = csp_policy or "default-src 'self'; script-src 'self'"
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["Content-Security-Policy"] = self.csp_policy
        return response

class LocalHostOnlyMiddleware:
    """Middleware to restrict access to localhost only."""
    
    def __init__(self, app: ASGIApp):
        self.app = app
        
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        # Only apply to HTTP requests
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Get client IP
        client_host, _ = scope.get("client", ("0.0.0.0", 0))
        
        # Allow only localhost (IPv4 and IPv6)
        if client_host not in ("127.0.0.1", "::1"):
            response = Response(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Access restricted to localhost only"},
                media_type="application/json"
            )
            await response(scope, receive, send)
            return
            
        return await self.app(scope, receive, send)

def setup_security_middleware(app, settings: SecuritySettings):
    """Configure all security middleware."""
    # Add localhost restriction middleware
    app.add_middleware(LocalHostOnlyMiddleware)
    
    # Add rate limiting
    app.state.limiter = limiter
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    app.add_middleware(XSSProtectionMiddleware)
    app.add_middleware(ContentSecurityPolicyMiddleware)