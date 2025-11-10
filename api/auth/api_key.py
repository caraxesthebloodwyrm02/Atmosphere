"""API key validation using environment variables."""

from fastapi import HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN
from api.config.security_config import security_config

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def validate_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Validate API key against environment variables."""
    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="No API key provided"
        )
        
    if api_key not in security_config.api_keys:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, 
            detail="Invalid API key"
        )
        
    return api_key

def require_api_key(api_key: str = Security(validate_api_key)):
    """Dependency for routes that require API key authentication."""
    return api_key