"""Basic tests for atmosphere_audio.core.security module."""

import pytest
from atmosphere_audio.core.security import SecurityConfig, security_logger


class TestAtmosphereSecurityConfig:
    """Test the SecurityConfig class."""

    def test_security_config_initialization(self):
        """Test that SecurityConfig can be instantiated."""
        config = SecurityConfig()
        assert config is not None

    def test_security_config_attributes(self):
        """Test that SecurityConfig has expected attributes."""
        config = SecurityConfig
        assert hasattr(config, 'SECRET_KEY')
        assert hasattr(config, 'ALGORITHM')
        assert hasattr(config, 'ACCESS_TOKEN_EXPIRE_MINUTES')
        assert hasattr(config, 'RATE_LIMIT_REQUESTS')


class TestAtmosphereSecurityLogger:
    """Test the security logger."""

    def test_security_logger_exists(self):
        """Test that security_logger is available."""
        assert security_logger is not None
        assert hasattr(security_logger, 'info')
        assert hasattr(security_logger, 'warning')
        assert hasattr(security_logger, 'error')
