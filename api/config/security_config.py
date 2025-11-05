"""Security settings using environment variables."""

from typing import List
from api.config.env import settings

class SecurityConfig:
    """Security configuration using environment variables."""
    
    @property
    def api_keys(self) -> List[str]:
        """Get list of valid API keys."""
        return settings.API_KEYS
    
    @property
    def jwt_secret_key(self) -> str:
        """Get JWT secret key."""
        return settings.JWT_SECRET_KEY
    
    @property
    def jwt_algorithm(self) -> str:
        """Get JWT algorithm."""
        return settings.JWT_ALGORITHM
    
    @property
    def jwt_token_expire_minutes(self) -> int:
        """Get JWT token expiration time in minutes."""
        return settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    @property
    def rate_limit_enabled(self) -> bool:
        """Check if rate limiting is enabled."""
        return settings.RATE_LIMIT_ENABLED
    
    @property
    def rate_limit_requests(self) -> int:
        """Get maximum requests per window."""
        return settings.RATE_LIMIT_REQUESTS
    
    @property
    def rate_limit_window(self) -> int:
        """Get rate limit window in seconds."""
        return settings.RATE_LIMIT_WINDOW

# Create global security config instance
security_config = SecurityConfig()