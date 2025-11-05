#!/usr/bin/env python3
"""
Security Test Suite for Atmosphere Platform
Tests authentication, authorization, and security controls
"""

import json
import os
import sys
from datetime import datetime

import pytest
import requests

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.security import (api_key_manager, jwt_manager, security_logger,
                          user_manager)


def test_user_management():
    """Test user creation and authentication"""
    # Test user creation
    from src.security import User
    import time

    # Use unique username with timestamp
    unique_username = f"testuser_{int(time.time())}"

    test_user = User(
        username=unique_username,
        email="test@example.com",
        full_name="Test User",
        role="analyst",
    )

    success = user_manager.create_user(test_user, "TestPass123!")
    assert success, "User creation should succeed"

    # Test authentication
    user = user_manager.authenticate_user(unique_username, "TestPass123!")
    assert user is not None, "Authentication should succeed"
    assert user.username == unique_username, "Authenticated user should have correct username"


def test_jwt_tokens():
    """Test JWT token generation and verification"""
    # Create token
    token_data = {"username": "testuser", "role": "analyst"}
    token = jwt_manager.create_access_token(token_data)
    assert token is not None, "JWT token creation should succeed"

    # Verify token
    decoded = jwt_manager.verify_token(token)
    assert decoded is not None, "JWT token verification should succeed"
    assert decoded.username == "testuser", "Decoded token should have correct username"


def test_api_keys():
    """Test API key generation and verification"""
    # Generate API key
    key = api_key_manager.generate_key(
        name="test_key", user_id="testuser", role="analyst"
    )
    assert key is not None, "API key generation should succeed"

    # Verify API key
    key_info = api_key_manager.verify_key(key)
    assert key_info is not None, "API key verification should succeed"
    assert key_info.name == "test_key", "Verified key should have correct name"


def test_security_headers():
    """Test that security headers are properly configured"""
    from src.security import SecurityConfig

    required_headers = [
        "X-Content-Type-Options",
        "X-Frame-Options",
        "X-XSS-Protection",
        "Strict-Transport-Security",
        "Content-Security-Policy",
        "Referrer-Policy",
    ]

    configured_headers = list(SecurityConfig.SECURITY_HEADERS.keys())
    missing_headers = [h for h in required_headers if h not in configured_headers]

    assert not missing_headers, f"Missing security headers: {missing_headers}"


def test_input_validation():
    """Test input validation and sanitization"""
    from src.security import input_validator

    # Test SQL injection detection
    malicious_input = "'; DROP TABLE users; --"
    assert input_validator.check_sql_injection(malicious_input), "SQL injection should be detected"

    # Test XSS detection
    xss_input = "<script>alert('xss')</script>"
    assert input_validator.check_xss(xss_input), "XSS should be detected"

    # Test input sanitization
    dirty_input = "Hello\x00World\tTest"
    clean_input = input_validator.sanitize_string(dirty_input)
    assert "\x00" not in clean_input, "Null bytes should be removed"
    assert "\t" not in clean_input, "Tab characters should be removed"
