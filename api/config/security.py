"""Security settings and configuration."""

from pydantic_settings import BaseSettings
from typing import List

class SecuritySettings(BaseSettings):
    """Security-related configuration settings."""
    
    # JWT Settings
    jwt_secret_key: str = "YOUR-SECRET-KEY"  # Change in production
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # API Key Settings
    require_api_key: bool = True
    api_key_header: str = "X-API-Key"
    allowed_api_keys: List[str] = []
    
    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 60
    rate_limit_window: int = 60  # seconds
    
    # CORS Settings
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]
    
    # Security Headers
    security_headers: dict = {
        "X-Frame-Options": "DENY",
        "X-Content-Type-Options": "nosniff",
        "X-XSS-Protection": "1; mode=block",
        "Content-Security-Policy": "default-src 'self'",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
    }
    
    class Config:
        env_prefix = "SECURITY_"