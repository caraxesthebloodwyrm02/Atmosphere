"""
Tests for atmosphere_audio.core.security module.

This module tests the comprehensive security controls including authentication,
authorization, rate limiting, input validation, and audit logging.
"""

import asyncio
import json
import time
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from atmosphere_audio.core.security import (
    APIKeyManager, InputValidator, JWTManager, RateLimiter,
    SecurityConfig, UserManager, create_admin_user, get_current_user,
    log_security_event, require_auth, require_role
)


class TestSecurityConfig:
    """Tests for SecurityConfig class."""

    def test_default_values(self):
        """Test default security configuration values."""
        assert SecurityConfig.SECRET_KEY is not None
        assert len(SecurityConfig.SECRET_KEY) >= 32
        assert SecurityConfig.ALGORITHM == "HS256"
        assert SecurityConfig.ACCESS_TOKEN_EXPIRE_MINUTES == 30
        assert SecurityConfig.REFRESH_TOKEN_EXPIRE_DAYS == 7
        assert SecurityConfig.RATE_LIMIT_REQUESTS == 100
        assert SecurityConfig.RATE_LIMIT_WINDOW == 60
        assert SecurityConfig.MIN_PASSWORD_LENGTH == 12
        assert SecurityConfig.PASSWORD_REGEX is not None
        assert SecurityConfig.API_KEY_HEADER == "X-API-Key"
        assert SecurityConfig.API_KEY_LENGTH == 32

    def test_security_headers(self):
        """Test security headers configuration."""
        headers = SecurityConfig.SECURITY_HEADERS
        assert "X-Content-Type-Options" in headers
        assert "X-Frame-Options" in headers
        assert "X-XSS-Protection" in headers
        assert "Strict-Transport-Security" in headers
        assert "Content-Security-Policy" in headers
        assert "Referrer-Policy" in headers


class TestUserManager:
    """Tests for UserManager class."""

    def test_initialization(self):
        """Test UserManager initialization."""
        manager = UserManager()
        assert manager.users == {}
        assert isinstance(manager._password_cache, dict)

    def test_create_user_success(self):
        """Test successful user creation."""
        manager = UserManager()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "researcher"
        }

        success = manager.create_user(user_data, "TestPassword123!")
        assert success
        assert "testuser" in manager.users
        assert manager.users["testuser"]["role"] == "researcher"

    def test_create_user_duplicate(self):
        """Test creating duplicate user."""
        manager = UserManager()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "researcher"
        }

        # Create first user
        manager.create_user(user_data, "TestPassword123!")
        # Try to create duplicate
        success = manager.create_user(user_data, "TestPassword123!")

        assert not success

    def test_authenticate_user_success(self):
        """Test successful user authentication."""
        manager = UserManager()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "researcher"
        }

        manager.create_user(user_data, "TestPassword123!")
        user = manager.authenticate_user("testuser", "TestPassword123!")

        assert user is not None
        assert user.username == "testuser"
        assert user.role == "researcher"

    def test_authenticate_user_wrong_password(self):
        """Test authentication with wrong password."""
        manager = UserManager()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "researcher"
        }

        manager.create_user(user_data, "TestPassword123!")
        user = manager.authenticate_user("testuser", "WrongPassword!")

        assert user is None

    def test_authenticate_user_unknown_user(self):
        """Test authentication for unknown user."""
        manager = UserManager()
        user = manager.authenticate_user("unknown", "password")

        assert user is None

    def test_get_user(self):
        """Test getting user by username."""
        manager = UserManager()

        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "role": "researcher"
        }

        manager.create_user(user_data, "TestPassword123!")
        user = manager.get_user("testuser")

        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_get_unknown_user(self):
        """Test getting unknown user."""
        manager = UserManager()
        user = manager.get_user("unknown")

        assert user is None


class TestJWTManager:
    """Tests for JWTManager class."""

    def test_initialization(self):
        """Test JWTManager initialization."""
        manager = JWTManager()
        assert manager.secret_key is not None
        assert manager.algorithm == "HS256"

    def test_create_access_token(self):
        """Test creating access token."""
        manager = JWTManager()
        data = {"username": "testuser", "role": "researcher"}

        token = manager.create_access_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        payload = manager.verify_token(token)
        assert payload is not None
        assert payload.username == "testuser"
        assert payload.role == "researcher"
        assert payload.type == "access"

    def test_create_refresh_token(self):
        """Test creating refresh token."""
        manager = JWTManager()
        data = {"username": "testuser", "role": "researcher"}

        token = manager.create_refresh_token(data)

        assert isinstance(token, str)
        assert len(token) > 0

        # Verify token can be decoded
        payload = manager.verify_token(token)
        assert payload is not None
        assert payload.username == "testuser"
        assert payload.type == "refresh"

    def test_verify_valid_token(self):
        """Test verifying valid token."""
        manager = JWTManager()
        data = {"username": "testuser", "role": "researcher"}

        token = manager.create_access_token(data)
        payload = manager.verify_token(token)

        assert payload is not None
        assert payload.username == "testuser"
        assert payload.role == "researcher"

    def test_verify_expired_token(self):
        """Test verifying expired token."""
        manager = JWTManager()

        # Create token that expires immediately
        expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)
        data = {"username": "testuser", "role": "researcher", "exp": expired_time}

        token = manager.create_access_token(data)
        payload = manager.verify_token(token)

        assert payload is None

    def test_verify_invalid_token(self):
        """Test verifying invalid token."""
        manager = JWTManager()

        payload = manager.verify_token("invalid.token.here")
        assert payload is None


class TestAPIKeyManager:
    """Tests for APIKeyManager class."""

    def test_initialization(self):
        """Test APIKeyManager initialization."""
        manager = APIKeyManager()
        assert manager.keys == {}

    def test_generate_key(self):
        """Test generating new API key."""
        manager = APIKeyManager()

        key = manager.generate_key(
            name="test-key",
            user_id="user123",
            role="researcher",
            permissions={"read", "write"}
        )

        assert isinstance(key, str)
        assert len(key) == SecurityConfig.API_KEY_LENGTH * 2  # hex encoded

    def test_verify_valid_key(self):
        """Test verifying valid API key."""
        manager = APIKeyManager()

        key = manager.generate_key(
            name="test-key",
            user_id="user123",
            role="researcher"
        )

        api_key = manager.verify_key(key)
        assert api_key is not None
        assert api_key.name == "test-key"
        assert api_key.user_id == "user123"
        assert api_key.role == "researcher"

    def test_verify_invalid_key(self):
        """Test verifying invalid API key."""
        manager = APIKeyManager()

        api_key = manager.verify_key("invalid-key")
        assert api_key is None

    def test_verify_inactive_key(self):
        """Test verifying inactive API key."""
        manager = APIKeyManager()

        key = manager.generate_key("test-key", "user123", "researcher")

        # Manually set key to inactive
        key_hash = manager.keys[list(manager.keys.keys())[0]]
        key_hash["is_active"] = False

        api_key = manager.verify_key(key)
        assert api_key is None


class TestRateLimiter:
    """Tests for RateLimiter class."""

    def test_initialization(self):
        """Test RateLimiter initialization."""
        limiter = RateLimiter()
        assert limiter.requests == {}
        assert limiter.blocked_until == {}

    def test_is_allowed_normal_usage(self):
        """Test normal usage within rate limits."""
        limiter = RateLimiter()

        # Should allow requests within limit
        for i in range(10):
            assert limiter.is_allowed("test-client", max_requests=10, window_seconds=60)

        # Should deny when limit exceeded
        assert not limiter.is_allowed("test-client", max_requests=10, window_seconds=60)

    def test_is_allowed_after_window(self):
        """Test that limits reset after window expires."""
        limiter = RateLimiter()

        # Exhaust the limit
        for i in range(10):
            limiter.is_allowed("test-client", max_requests=10, window_seconds=1)

        # Wait for window to expire
        time.sleep(1.1)

        # Should allow again
        assert limiter.is_allowed("test-client", max_requests=10, window_seconds=1)

    def test_get_remaining_requests(self):
        """Test getting remaining requests."""
        limiter = RateLimiter()

        # Use some requests
        for i in range(3):
            limiter.is_allowed("test-client", max_requests=10, window_seconds=60)

        remaining = limiter.get_remaining_requests("test-client")
        assert remaining == 7

    def test_blocked_client(self):
        """Test that blocked clients are denied."""
        limiter = RateLimiter()

        # Exhaust limit to get blocked
        for i in range(10):
            limiter.is_allowed("test-client", max_requests=10, window_seconds=60)

        # Should be blocked
        assert not limiter.is_allowed("test-client", max_requests=10, window_seconds=60)

        # Check blocked status
        assert "test-client" in limiter.blocked_until


class TestInputValidator:
    """Tests for InputValidator class."""

    def test_sanitize_string(self):
        """Test string sanitization."""
        # Normal string
        result = InputValidator.sanitize_string("hello world")
        assert result == "hello world"

        # String with null bytes
        result = InputValidator.sanitize_string("hello\x00world")
        assert result == "helloworld"

        # String exceeding max length
        result = InputValidator.sanitize_string("a" * 1000, max_length=100)
        assert len(result) == 100

    def test_validate_json(self):
        """Test JSON validation."""
        # Valid JSON
        assert InputValidator.validate_json({"test": "value"})
        assert InputValidator.validate_json([1, 2, 3])

        # Invalid JSON (circular reference would cause error)
        class BadObject:
            def __init__(self):
                self.self = self

        bad_obj = BadObject()
        bad_obj.self = bad_obj
        assert not InputValidator.validate_json(bad_obj)

    def test_check_sql_injection(self):
        """Test SQL injection detection."""
        # Safe inputs
        assert not InputValidator.check_sql_injection("SELECT * FROM users WHERE id = 1")
        assert not InputValidator.check_sql_injection("normal query")

        # Dangerous inputs
        assert InputValidator.check_sql_injection("; DROP TABLE users;")
        assert InputValidator.check_sql_injection("UNION SELECT password FROM users")
        assert InputValidator.check_sql_injection("-- comment")

    def test_check_xss(self):
        """Test XSS detection."""
        # Safe inputs
        assert not InputValidator.check_xss("<p>Hello world</p>")
        assert not InputValidator.check_xss("normal text")

        # Dangerous inputs
        assert InputValidator.check_xss("<script>alert('xss')</script>")
        assert InputValidator.check_xss("javascript:alert('xss')")
        assert InputValidator.check_xss("<iframe src='evil.com'></iframe>")
        assert InputValidator.check_xss("<img onerror='alert(1)' />")


class TestSecurityUtilities:
    """Tests for security utility functions."""

    def test_create_admin_user(self):
        """Test creating default admin user."""
        # This would normally create a user file, but we'll mock it
        with patch('atmosphere_audio.core.security.UserManager') as mock_user_manager:
            mock_manager = MagicMock()
            mock_user_manager.return_value = mock_manager
            mock_manager.create_user.return_value = True

            result = create_admin_user()
            assert result is True

    def test_log_security_event(self):
        """Test logging security events."""
        with patch('atmosphere_audio.core.security.security_logger') as mock_logger:
            log_security_event("TEST_EVENT", {"user": "testuser"}, "INFO")

            mock_logger.info.assert_called_once()
            args = mock_logger.info.call_args[0]
            assert "TEST_EVENT" in args[0]
            assert "testuser" in args[0]


class TestFastAPISecurity:
    """Tests for FastAPI security dependencies."""

    @pytest.mark.asyncio
    async def test_get_current_user_no_credentials(self):
        """Test get_current_user with no credentials."""
        user = await get_current_user()
        assert user is None

    @pytest.mark.asyncio
    async def test_require_role_dependency(self):
        """Test require_role dependency function."""
        dependency = require_role(["admin", "researcher"])

        # This should return a dependency function
        assert callable(dependency)

    def test_require_auth_decorator(self):
        """Test require_auth decorator."""
        @require_auth(["admin"])
        def test_function():
            return "success"

        # Decorator should return wrapper function
        assert callable(test_function)

    def test_rate_limit_decorator(self):
        """Test rate_limit decorator."""
        from atmosphere_audio.core.security import rate_limit

        @rate_limit(max_requests=10, window_seconds=60)
        def test_function():
            return "success"

        # Decorator should return wrapper function
        assert callable(test_function)

    def test_validate_input_decorator(self):
        """Test validate_input decorator."""
        from atmosphere_audio.core.security import validate_input

        @validate_input()
        def test_function():
            return "success"

        # Decorator should return wrapper function
        assert callable(test_function)
