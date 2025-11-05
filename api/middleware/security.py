"""Security middleware components."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
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

def setup_security_middleware(app, settings: SecuritySettings):
    """Configure all security middleware."""
    
    # Add rate limiting
    app.state.limiter = limiter
    
    # Add security headers
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    app.add_middleware(XSSProtectionMiddleware)
    app.add_middleware(ContentSecurityPolicyMiddleware)
    
    # Configure CORS if needed
    from fastapi.middleware.cors import CORSMiddleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allow_origins,
        allow_credentials=settings.allow_credentials,
        allow_methods=settings.allow_methods,
        allow_headers=settings.allow_headers,
    )