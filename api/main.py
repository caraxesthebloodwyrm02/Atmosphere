"""Main FastAPI application setup with security and monitoring."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.config.security import SecuritySettings
from api.middleware.security import setup_security_middleware
from api.monitoring.middleware import setup_monitoring

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Initialize FastAPI app
    app = FastAPI(
        title="Atmosphere API",
        description="Secure API with authentication, monitoring, and rate limiting",
        version="1.0.0"
    )
    
    # Load security settings
    security_settings = SecuritySettings()
    
    # Setup security middleware
    setup_security_middleware(app, security_settings)
    
    # Setup monitoring
    setup_monitoring(app)
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=security_settings.allow_origins,
        allow_credentials=security_settings.allow_credentials,
        allow_methods=security_settings.allow_methods,
        allow_headers=security_settings.allow_headers,
    )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}
    
    return app

app = create_app()