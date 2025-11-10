<<<<<<< HEAD
"""Environment configuration management."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class EnvSettings(BaseSettings):
    """Environment settings with secure defaults."""
    
    # API Keys - using secure defaults
    API_KEYS: List[str] = []
    OPENAI_API_KEY: Optional[str] = None
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.urandom(32).hex()  # Generate secure random key if not set
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Security Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60
    
    class Config:
        """Pydantic config."""
        env_file = '.env'
        case_sensitive = True

# Create settings instance
settings = EnvSettings()

def get_api_key() -> Optional[str]:
    """Safely retrieve API key from environment."""
    return settings.OPENAI_API_KEY

def get_api_keys() -> List[str]:
    """Get list of valid API keys."""
    return settings.API_KEYS

def is_production() -> bool:
    """Check if running in production environment."""
=======
"""Environment configuration management."""

import os
from pathlib import Path
from typing import List, Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load .env file if it exists
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

class EnvSettings(BaseSettings):
    """Environment settings with secure defaults."""
    
    # API Keys - using secure defaults
    API_KEYS: List[str] = []
    OPENAI_API_KEY: Optional[str] = None
    
    # JWT Settings
    JWT_SECRET_KEY: str = os.urandom(32).hex()  # Generate secure random key if not set
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Security Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 60
    RATE_LIMIT_WINDOW: int = 60
    
    class Config:
        """Pydantic config."""
        env_file = '.env'
        case_sensitive = True

# Create settings instance
settings = EnvSettings()

def get_api_key() -> Optional[str]:
    """Safely retrieve API key from environment."""
    return settings.OPENAI_API_KEY

def get_api_keys() -> List[str]:
    """Get list of valid API keys."""
    return settings.API_KEYS

def is_production() -> bool:
    """Check if running in production environment."""
>>>>>>> 94e7240e4017e5ff163804c12cc582d2f8092628
    return settings.ENVIRONMENT.lower() == "production"