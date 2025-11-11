"""
Unit tests for atmosphere_audio.core.security module
"""

import json
import os
import tempfile
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, mock_open

import pytest
from fastapi import HTTPException

from atmosphere_audio.core.security import (
    User, LoginRequest, APIKey, UserManager, JWTManager, APIKeyManager,
    RateLimiter, InputValidator, require_auth, rate_limit, validate_input,
    get_current_user, require_role, SecurityMiddleware, LocalHostOnlyMiddleware,
    SecurityConfig, log_security_event
)


class TestUserModel:
    """Test User model validation"""

    def test_valid_user(self):
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="user"
        )
        assert user.username == "testuser"
        assert user.role == "user"

    def test_invalid_username(self):
        with pytest.raises(ValueError):
            User(
                username="test-user!",  # Invalid characters
                email="test@example.com",
                full_name="Test User",
                role="user"
            )

    def test_invalid_email(self):
        with pytest.raises(ValueError):
            User(
                username="testuser",
                email="invalid-email",
                full_name="Test User",
                role="user"
            )

    def test_invalid_role(self):
        with pytest.raises(ValueError):
            User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                role="invalid_role"
            )


class TestLoginRequest:
    """Test LoginRequest model validation"""

    def test_valid_login(self):
        login = LoginRequest(
            username="testuser",
            password="ValidPass123!"
        )
        assert login.username == "testuser"

    def test_weak_password(self):
        with pytest.raises(ValueError):
            LoginRequest(
                username="testuser",
                password="weak"
            )


class TestJWTManager:
    """Test JWT token management"""

    @patch('atmosphere_audio.core.security.SecurityConfig')
    def test_create_access_token(self, mock_config):
        mock_config.SECRET_KEY = "test_secret"
        mock_config.ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        manager = JWTManager()
        token = manager.create_access_token({"username": "test", "role": "user"})

        assert isinstance(token, str)
        assert len(token) > 0

    @patch('atmosphere_audio.core.security.SecurityConfig')
    def test_verify_valid_token(self, mock_config):
        mock_config.SECRET_KEY = "test_secret"
        mock_config.ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = 30

        manager = JWTManager()
        token = manager.create_access_token({"username": "test", "role": "user"})

        result = manager.verify_token(token)
        assert result is not None
        assert result.username == "test"
        assert result.role == "user"

    @patch('atmosphere_audio.core.security.SecurityConfig')
    def test_verify_expired_token(self, mock_config):
        mock_config.SECRET_KEY = "test_secret"
        mock_config.ALGORITHM = "HS256"
        mock_config.ACCESS_TOKEN_EXPIRE_MINUTES = -1  # Expired

        manager = JWTManager()
        token = manager.create_access_token({"username": "test", "role": "user"})

        result = manager.verify_token(token)
        assert result is None

    def test_verify_invalid_token(self):
        manager = JWTManager()
        result = manager.verify_token("invalid_token")
        assert result is None


class TestAPIKeyManager:
    """Test API key management"""

    def test_generate_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = os.path.join(temp_dir, "test_keys.json")
            manager = APIKeyManager(storage_path)

            key = manager.generate_key("test_key", "user123", "admin", {"read", "write"})
            assert isinstance(key, str)
            assert len(key) == SecurityConfig.API_KEY_LENGTH * 2  # hex

            # Verify key was saved
            assert os.path.exists(storage_path)

    def test_verify_valid_key(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            storage_path = os.path.join(temp_dir, "test_keys.json")
            manager = APIKeyManager(storage_path)

            generated_key = manager.generate_key("test_key", "user123", "admin")
            verified_key = manager.verify_key(generated_key)

            assert verified_key is not None
            assert verified_key.name == "test_key"
            assert verified_key.user_id == "user123"
            assert verified_key.role == "admin"

    def test_verify_invalid_key(self):
        manager = APIKeyManager()
        result = manager.verify_key("invalid_key")
        assert result is None


class TestRateLimiter:
    """Test rate limiting logic"""

    def test_is_allowed_normal_usage(self):
        limiter = RateLimiter()
        client_id = "test_client"

        # Should allow initial requests
        for i in range(SecurityConfig.RATE_LIMIT_REQUESTS):
            assert limiter.is_allowed(client_id) is True

    def test_is_allowed_rate_limit_exceeded(self):
        limiter = RateLimiter()
        client_id = "test_client"

        # Use up all requests
        for i in range(SecurityConfig.RATE_LIMIT_REQUESTS):
            limiter.is_allowed(client_id)

        # Next request should be blocked
        assert limiter.is_allowed(client_id) is False

    def test_get_remaining_requests(self):
        limiter = RateLimiter()
        client_id = "test_client"

        # Initially should have full quota
        remaining = limiter.get_remaining_requests(client_id)
        assert remaining == SecurityConfig.RATE_LIMIT_REQUESTS

        # After one request
        limiter.is_allowed(client_id)
        remaining = limiter.get_remaining_requests(client_id)
        assert remaining == SecurityConfig.RATE_LIMIT_REQUESTS - 1


class TestInputValidator:
    """Test input validation and sanitization"""

    def test_sanitize_string_valid(self):
        result = InputValidator.sanitize_string("  hello world  ")
        assert result == "hello world"

    def test_sanitize_string_max_length(self):
        long_string = "a" * 2000
        result = InputValidator.sanitize_string(long_string, max_length=100)
        assert len(result) == 100

    def test_sanitize_string_invalid_type(self):
        with pytest.raises(ValueError):
            InputValidator.sanitize_string(123)

    def test_validate_json_valid(self):
        assert InputValidator.validate_json({"key": "value"}) is True
        assert InputValidator.validate_json([1, 2, 3]) is True

    def test_validate_json_invalid(self):
        assert InputValidator.validate_json(set([1, 2, 3])) is False

    def test_check_sql_injection_safe(self):
        assert InputValidator.check_sql_injection("safe string") is False

    def test_check_sql_injection_dangerous(self):
        assert InputValidator.check_sql_injection("SELECT * FROM users;") is True
        assert InputValidator.check_sql_injection("UNION SELECT password") is True

    def test_check_xss_safe(self):
        assert InputValidator.check_xss("safe string") is False

    def test_check_xss_dangerous(self):
        assert InputValidator.check_xss("<script>alert('xss')</script>") is True
        assert InputValidator.check_xss("javascript:alert('xss')") is True


class TestSecurityDecorators:
    """Test security decorators"""

    @patch('atmosphere_audio.core.security.security_logger')
    def test_require_auth_no_user(self, mock_logger):
        @require_auth()
        async def test_func():
            return "success"

        # Mock no current user
        test_func._current_user = None

        with pytest.raises(HTTPException) as exc_info:
            await test_func()
        assert exc_info.value.status_code == 401

    @patch('atmosphere_audio.core.security.security_logger')
    def test_require_auth_insufficient_role(self, mock_logger):
        user = User(username="test", email="test@test.com", full_name="Test", role="user")

        @require_auth(roles=["admin"])
        async def test_func():
            return "success"

        test_func._current_user = user

        with pytest.raises(HTTPException) as exc_info:
            await test_func()
        assert exc_info.value.status_code == 403

    @patch('atmosphere_audio.core.security.RateLimiter')
    def test_rate_limit_exceeded(self, mock_limiter_class):
        mock_limiter = mock_limiter_class.return_value
        mock_limiter.is_allowed.return_value = False

        @rate_limit()
        async def test_func():
            return "success"

        test_func._client_id = "test_client"

        with pytest.raises(HTTPException) as exc_info:
            await test_func()
        assert exc_info.value.status_code == 429


class TestSecurityMiddleware:
    """Test security middleware"""

    def test_get_client_ip_forwarded(self):
        middleware = SecurityMiddleware(None)
        scope = {
            "headers": [[b"x-forwarded-for", b"192.168.1.100, 10.0.0.1"]]
        }
        ip = middleware._get_client_ip(scope)
        assert ip == "192.168.1.100"

    def test_get_client_ip_direct(self):
        middleware = SecurityMiddleware(None)
        scope = {
            "client": ["192.168.1.100", 12345]
        }
        ip = middleware._get_client_ip(scope)
        assert ip == "192.168.1.100"


class TestLocalHostOnlyMiddleware:
    """Test localhost-only middleware"""

    async def test_localhost_allowed(self):
        middleware = LocalHostOnlyMiddleware(None)
        scope = {
            "type": "http",
            "client": ["127.0.0.1", 12345]
        }

        called = False
        async def mock_app(scope, receive, send):
            nonlocal called
            called = True

        await middleware(scope, None, mock_app)
        assert called is True

    async def test_non_localhost_blocked(self):
        middleware = LocalHostOnlyMiddleware(None)
        scope = {
            "type": "http",
            "client": ["192.168.1.100", 12345]
        }

        send_messages = []
        async def mock_send(message):
            send_messages.append(message)

        await middleware(scope, None, mock_send)

        assert len(send_messages) == 2
        assert send_messages[0]["status"] == 403


class TestUtilityFunctions:
    """Test utility functions"""

    @patch('atmosphere_audio.core.security.security_logger')
    def test_log_security_event(self, mock_logger):
        log_security_event("TEST_EVENT", {"key": "value"})
        mock_logger.info.assert_called_once()

        log_security_event("TEST_EVENT", {"key": "value"}, "WARNING")
        mock_logger.warning.assert_called_once()

        log_security_event("TEST_EVENT", {"key": "value"}, "ERROR")
        mock_logger.error.assert_called_once()
