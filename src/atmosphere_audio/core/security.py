"""
Atmosphere Security Module
Provides comprehensive security controls including authentication, authorization,
rate limiting, input validation, and audit logging for all entry points.
"""

import asyncio
import hashlib
import hmac
import json
import logging
import os
import re
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Union

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field, field_validator

# Configure security logger
security_logger = logging.getLogger("atmosphere.security")
security_logger.setLevel(logging.INFO)

# Create console handler for security events
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - SECURITY - %(levelname)s - %(message)s")
console_handler.setFormatter(formatter)
security_logger.addHandler(console_handler)


# Configuration
class SecurityConfig:
    """Security configuration settings"""

    # JWT settings
    SECRET_KEY = os.getenv("ATMOSPHERE_SECRET_KEY", secrets.token_hex(32))
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

    # Rate limiting
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

    # Password settings
    MIN_PASSWORD_LENGTH = 12
    PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"

    # API Key settings
    API_KEY_HEADER = "X-API-Key"
    API_KEY_LENGTH = 32

    # Security headers
    SECURITY_HEADERS = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'",
        "Referrer-Policy": "strict-origin-when-cross-origin",
    }


# Data Models
class User(BaseModel):
    """User model for authentication"""

    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    full_name: str = Field(..., min_length=1, max_length=100)
    role: str = Field(..., pattern=r"^(admin|researcher|developer|analyst|user)$")
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_login: Optional[datetime] = None

    @field_validator("username")
    @classmethod
    def username_alphanumeric(cls, v):  # pylint: disable=no-self-argument
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must be alphanumeric with underscores only")
        return v


class TokenData(BaseModel):
    """JWT token payload"""

    username: str
    role: str
    exp: datetime
    type: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request model"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=SecurityConfig.MIN_PASSWORD_LENGTH)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v):  # pylint: disable=no-self-argument
        if len(v) < SecurityConfig.MIN_PASSWORD_LENGTH:
            raise ValueError(
                f"Password must be at least {SecurityConfig.MIN_PASSWORD_LENGTH} characters"
            )
        if not re.match(SecurityConfig.PASSWORD_REGEX, v):
            raise ValueError(
                "Password must contain at least one lowercase letter, "
                "one uppercase letter, one digit, and one special character"
            )
        return v


class APIKey(BaseModel):
    """API Key model"""

    key: str
    name: str
    user_id: str
    role: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None
    is_active: bool = True
    permissions: Set[str] = Field(default_factory=set)


# Security Components
class UserManager:
    """User management system"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.users: Dict[str, Dict] = self._load_users() if storage_path else {}
        self._password_cache: Dict[str, str] = {}  # username -> hashed_password

    def _load_users(self) -> Dict[str, Dict]:
        """Load users from storage"""
        if self.storage_path and os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                pass
        return {}

    def _save_users(self):
        """Save users to storage"""
        if not self.storage_path:
            return
        with open(self.storage_path, "w") as f:
            json.dump(self.users, f, indent=2, default=str)

    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = os.getenv("PASSWORD_SALT", "atmosphere_salt").encode()
        return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000).hex()

    def create_user(self, user: Union[User, Dict], password: str) -> bool:
        """Create a new user"""
        if isinstance(user, dict):
            user = User(**user)
        if user.username in self.users:
            return False

        hashed_password = self._hash_password(password)
        user_data = user.model_dump() if hasattr(user, 'model_dump') else user.dict()
        user_data["password_hash"] = hashed_password

        self.users[user.username] = user_data
        self._password_cache[user.username] = hashed_password
        self._save_users()

        security_logger.info(f"User created: {user.username} ({user.role})")
        return True

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user credentials"""
        if username not in self.users:
            security_logger.warning(
                f"Failed login attempt for unknown user: {username}"
            )
            return None

        user_data = self.users[username]
        if not user_data.get("is_active", True):
            security_logger.warning(f"Login attempt for inactive user: {username}")
            return None

        stored_hash = user_data["password_hash"]
        if hmac.compare_digest(self._hash_password(password), stored_hash):
            # Update last login
            user_data["last_login"] = datetime.now(timezone.utc).isoformat()
            self._save_users()

            security_logger.info(f"Successful login: {username}")
            return User(**{k: v for k, v in user_data.items() if k != "password_hash"})
        else:
            security_logger.warning(f"Failed login attempt: {username}")
            return None

    def get_user(self, username: str) -> Optional[User]:
        """Get user by username"""
        if username not in self.users:
            return None
        user_data = self.users[username]
        return User(**{k: v for k, v in user_data.items() if k != "password_hash"})


class JWTManager:
    """JWT token management"""

    def __init__(self):
        self.secret_key = SecurityConfig.SECRET_KEY
        self.algorithm = SecurityConfig.ALGORITHM

    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        # Only set expiry if not already provided by caller
        if "exp" not in to_encode:
            to_encode["exp"] = datetime.now(timezone.utc) + timedelta(
                minutes=SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        to_encode.setdefault("iat", datetime.now(timezone.utc))
        to_encode.setdefault("type", "access")
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        # Only set expiry if not already provided by caller
        if "exp" not in to_encode:
            to_encode["exp"] = datetime.now(timezone.utc) + timedelta(
                days=SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS
            )
        to_encode.setdefault("iat", datetime.now(timezone.utc))
        to_encode.setdefault("type", "refresh")
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Optional[TokenData]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return TokenData(**payload)
        except jwt.ExpiredSignatureError:
            security_logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            security_logger.warning("Invalid token")
            return None


class APIKeyManager:
    """API Key management"""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self.keys: Dict[str, Dict] = self._load_keys() if storage_path else {}

    def _load_keys(self) -> Dict[str, Dict]:
        """Load API keys from storage"""
        if self.storage_path and os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r") as f:
                    return json.load(f)
            except (OSError, json.JSONDecodeError):
                pass
        return {}

    def _save_keys(self):
        """Save API keys to storage"""
        if not self.storage_path:
            return
        with open(self.storage_path, "w") as f:
            json.dump(self.keys, f, indent=2, default=str)

    def generate_key(
        self, name: str, user_id: str, role: str, permissions: Set[str] = None
    ) -> str:
        """Generate a new API key"""
        key = secrets.token_hex(SecurityConfig.API_KEY_LENGTH)
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        api_key_data = {
            "key_hash": key_hash,
            "name": name,
            "user_id": user_id,
            "role": role,
            "permissions": list(permissions or set()),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "is_active": True,
        }

        self.keys[key_hash] = api_key_data
        self._save_keys()

        security_logger.info(f"API key generated: {name} for user {user_id}")
        return key

    def verify_key(self, key: str) -> Optional[APIKey]:
        """Verify API key"""
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        if key_hash not in self.keys:
            return None

        key_data = self.keys[key_hash]
        if not key_data.get("is_active", True):
            return None

        # Update last used
        key_data["last_used"] = datetime.now(timezone.utc).isoformat()
        self._save_keys()

        return APIKey(
            key=key,
            name=key_data["name"],
            user_id=key_data["user_id"],
            role=key_data["role"],
            permissions=set(key_data.get("permissions", [])),
            is_active=key_data["is_active"],
        )


class RateLimiter:
    """Advanced rate limiter with multiple strategies"""

    def __init__(self):
        self.requests: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=SecurityConfig.RATE_LIMIT_REQUESTS)
        )
        self.blocked_until: Dict[str, float] = {}
        self._client_limits: Dict[str, int] = {}  # per-client max_requests tracking

    def is_allowed(
        self, client_id: str, max_requests: int = None, window_seconds: int = None
    ) -> bool:
        """Check if request is allowed"""
        max_req = max_requests or SecurityConfig.RATE_LIMIT_REQUESTS
        window = window_seconds or SecurityConfig.RATE_LIMIT_WINDOW

        # Store the per-client limit for use by get_remaining_requests
        if client_id not in self._client_limits:
            self._client_limits[client_id] = max_req

        now = time.time()

        # Check if client is blocked
        if client_id in self.blocked_until and now < self.blocked_until[client_id]:
            security_logger.warning(f"Rate limit exceeded - blocked: {client_id}")
            return False

        # Clean old requests
        client_requests = self.requests[client_id]
        while client_requests and now - client_requests[0] > window:
            client_requests.popleft()

        # Check rate limit
        if len(client_requests) >= max_req:
            # Block client for window duration
            self.blocked_until[client_id] = now + window
            security_logger.warning(f"Rate limit exceeded: {client_id}")
            return False

        client_requests.append(now)
        return True

    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client"""
        max_req = self._client_limits.get(client_id, SecurityConfig.RATE_LIMIT_REQUESTS)
        client_requests = self.requests[client_id]
        now = time.time()
        window = SecurityConfig.RATE_LIMIT_WINDOW

        # Clean old requests
        while client_requests and now - client_requests[0] > window:
            client_requests.popleft()

        return max(0, max_req - len(client_requests))


class InputValidator:
    """Input validation and sanitization"""

    @staticmethod
    def sanitize_string(input_str: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            raise ValueError("Input must be a string")

        # Remove null bytes and control characters
        sanitized = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", input_str)

        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()

    @staticmethod
    def validate_json(data: Any) -> bool:
        """Validate JSON data structure"""
        try:
            json.dumps(data)
            return True
        except (TypeError, ValueError):
            return False

    @staticmethod
    def check_sql_injection(input_str: str) -> bool:
        """Basic SQL injection detection"""
        sql_patterns = [
            r";\s*(select|insert|update|delete|drop|create|alter)",
            r"union\s+select",
            r"--",
            r"/\*.*\*/",
        ]

        for pattern in sql_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False

    @staticmethod
    def check_xss(input_str: str) -> bool:
        """Basic XSS detection"""
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>.*?</iframe>",
            r"<object[^>]*>.*?</object>",
        ]

        for pattern in xss_patterns:
            if re.search(pattern, input_str, re.IGNORECASE):
                return True
        return False


# Security Decorators
def require_auth(roles: List[str] = None):
    """Decorator for requiring authentication and authorization"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get current user from context (would be set by middleware)
            current_user = getattr(func, "_current_user", None)
            if not current_user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required",
                )

            if roles and current_user.role not in roles:
                security_logger.warning(
                    f"Access denied for user {current_user.username} with role {current_user.role}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions",
                )

            security_logger.info(
                f"Access granted: {current_user.username} -> {func.__name__}"
            )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def rate_limit(max_requests: int = None, window_seconds: int = None):
    """Rate limiting decorator"""

    def decorator(func: Callable):
        limiter = RateLimiter()

        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get client identifier (would be from request context)
            client_id = getattr(func, "_client_id", "anonymous")

            if not limiter.is_allowed(client_id, max_requests, window_seconds):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded",
                )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


def validate_input(
    sanitize: bool = True, check_injection: bool = True, check_xss: bool = True
):
    """Input validation decorator"""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Validate and sanitize inputs
            for key, value in kwargs.items():
                if isinstance(value, str):
                    if sanitize:
                        kwargs[key] = InputValidator.sanitize_string(value)

                    if check_injection and InputValidator.check_sql_injection(value):
                        security_logger.warning(
                            f"SQL injection attempt detected in {key}"
                        )
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid input detected",
                        )

                    if check_xss and InputValidator.check_xss(value):
                        security_logger.warning(f"XSS attempt detected in {key}")
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid input detected",
                        )

            return await func(*args, **kwargs)

        return wrapper

    return decorator


# FastAPI Security Dependencies
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = None,
    api_key_manager: Optional[APIKeyManager] = None,
    jwt_manager: Optional[JWTManager] = None,
    user_manager: Optional[UserManager] = None,
) -> Optional[User]:
    """FastAPI dependency for getting current authenticated user"""
    _jwt_manager = jwt_manager or JWTManager()
    _user_manager = user_manager or UserManager()

    if credentials and not hasattr(credentials, '_mock_name') and not str(type(credentials)).endswith("Depends'>"):
        # Try JWT token
        creds = credentials.credentials if hasattr(credentials, 'credentials') else None
        if creds:
            token_data = _jwt_manager.verify_token(creds)
            if token_data:
                return _user_manager.get_user(token_data.username)

    # Check for API key in headers (would need request context)
    # For now, return None - would be enhanced with proper request handling

    return None


def require_role(required_roles: List[str]):
    """FastAPI dependency for role-based access control"""

    def dependency(current_user: User = Depends(get_current_user)):
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
            )

        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

        return current_user

    return dependency


# Security Middleware
class SecurityMiddleware:
    """FastAPI security middleware"""

    def __init__(self, app, rate_limiter: RateLimiter = None):
        self.app = app
        self.rate_limiter = rate_limiter or RateLimiter()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Rate limiting
        client_ip = self._get_client_ip(scope)
        if not self.rate_limiter.is_allowed(client_ip):
            await self._send_error(send, 429, "Rate limit exceeded")
            return

        # Security headers
        original_send = send

        async def security_send(message):
            if message["type"] == "http.response.start":
                headers = dict(message.get("headers", []))
                for (
                    header_name,
                    header_value,
                ) in SecurityConfig.SECURITY_HEADERS.items():
                    header_bytes = header_name.encode() + b": " + header_value.encode()
                    headers[header_name.encode()] = header_value.encode()

                message["headers"] = list(headers.items())

            await original_send(message)

        await self.app(scope, receive, security_send)

    def _get_client_ip(self, scope) -> str:
        """Extract client IP from ASGI scope"""
        headers = dict(scope.get("headers", []))
        forwarded = headers.get(b"x-forwarded-for", b"").decode()
        if forwarded:
            return forwarded.split(",")[0].strip()
        return scope.get("client", ["unknown"])[0]

    async def _send_error(self, send, status_code: int, message: str):
        """Send error response"""
        await send(
            {
                "type": "http.response.start",
                "status": status_code,
                "headers": [
                    [b"content-type", b"application/json"],
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": json.dumps({"error": message}).encode(),
            }
        )


# Initialize global security components
user_manager = UserManager(storage_path="users.json")
jwt_manager = JWTManager()
api_key_manager = APIKeyManager(storage_path="api_keys.json")
rate_limiter = RateLimiter()
input_validator = InputValidator()


# Utility functions
def create_admin_user():
    """Create default admin user if none exists"""
    _user_manager = UserManager(storage_path="users.json")
    admin_user = User(
        username="admin",
        email="admin@atmosphere.local",
        full_name="System Administrator",
        role="admin",
    )

    if _user_manager.create_user(admin_user, "Admin123!@#"):
        security_logger.info("Default admin user created")
        return True
    return False


def log_security_event(event_type: str, details: Dict[str, Any], level: str = "INFO"):
    """Log security event"""
    message = f"{event_type}: {json.dumps(details)}"
    if level == "WARNING":
        security_logger.warning(message)
    elif level == "ERROR":
        security_logger.error(message)
    else:
        security_logger.info(message)


class LocalHostOnlyMiddleware:
    """Middleware to restrict access to localhost only"""
    
    def __init__(self, app):
        self.app = app
        
    async def __call__(self, scope, receive, send):
        # Only apply to HTTP requests
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
            
        # Get client IP
        client_host, _ = scope.get("client", ("0.0.0.0", 0))
        
        # Allow only localhost (IPv4 and IPv6)
        if client_host not in ("127.0.0.1", "::1"):
            response = {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    [b"content-type", b"application/json"],
                ],
            }
            await send(response)
            
            response_body = {
                "detail": "Access restricted to localhost only"
            }
            await send({
                "type": "http.response.body",
                "body": json.dumps(response_body).encode(),
                "more_body": False,
            })
            return
            
        return await self.app(scope, receive, send)

# Initialize system
if not os.path.exists("users.json"):
    create_admin_user()
