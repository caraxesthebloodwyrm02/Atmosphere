import pytest
from unittest.mock import patch
from src.atmosphere_audio.core.security import JWTManager, APIKeyManager, User, RateLimiter, log_security_event


def test_jwt_access_token_lifecycle():
    """Test JWT access token creation and verification"""
    manager = JWTManager()

    # Create test user data
    user_data = {
        "username": "testuser",
        "role": "user",
        "user_id": "user123"
    }

    # Generate access token
    token = manager.create_access_token(user_data)
    assert token
    assert isinstance(token, str)

    # Verify token
    payload = manager.verify_token(token)
    assert payload is not None
    assert payload.username == "testuser"
    assert payload.role == "user"


def test_jwt_refresh_token_lifecycle():
    """Test JWT refresh token creation and verification"""
    manager = JWTManager()

    # Create test user data
    user_data = {
        "username": "testuser",
        "role": "user"
    }

    # Generate refresh token
    token = manager.create_refresh_token(user_data)
    assert token
    assert isinstance(token, str)

    # Verify token
    payload = manager.verify_token(token)
    assert payload is not None
    assert payload.username == "testuser"
    assert payload.role == "user"


def test_api_key_generation_and_verification():
    """Test API key generation and verification"""
    manager = APIKeyManager()

    # Generate API key
    key = manager.generate_key(
        name="test_app",
        user_id="user123",
        role="developer",
        permissions={"read", "write"}
    )

    assert key
    assert len(key) == 64  # 32 bytes * 2 hex chars

    # Verify API key
    api_key_obj = manager.verify_key(key)
    assert api_key_obj is not None
    assert api_key_obj.name == "test_app"
    assert api_key_obj.user_id == "user123"
    assert api_key_obj.role == "developer"
    assert "read" in api_key_obj.permissions
    assert "write" in api_key_obj.permissions


def test_rate_limiter_exhaustion():
    """Test rate limiter blocks after exceeding limits"""
    limiter = RateLimiter()

    client_id = "test_client"

    # Use up all requests (default is 100)
    for i in range(100):
        assert limiter.is_allowed(client_id) is True

    # Next request should be blocked
    assert limiter.is_allowed(client_id) is False

    # Check remaining requests shows 0
    assert limiter.get_remaining_requests(client_id) == 0


def test_security_event_logging():
    """Test security event logging"""
    import logging

    # Capture log messages
    with patch('src.atmosphere_audio.core.security.security_logger') as mock_logger:
        log_security_event(
            "api_access",
            {"user": "user123", "resource": "/pipeline"},
            "INFO"
        )

        mock_logger.info.assert_called_once()
        call_args = mock_logger.info.call_args[0][0]
        assert "api_access" in call_args
        assert "user123" in call_args
        assert "/pipeline" in call_args


def test_user_model_validation():
    """Test User model validation"""
    # Valid user
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        role="user"
    )
    assert user.username == "testuser"
    assert user.role == "user"

    # Invalid username (contains invalid characters)
    with pytest.raises(ValueError, match="Username must be alphanumeric"):
        User(
            username="test@user",
            email="test@example.com",
            full_name="Test User",
            role="user"
        )

    # Invalid role
    with pytest.raises(ValueError):
        User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            role="invalid_role"
        )
