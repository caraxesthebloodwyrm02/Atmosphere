# Unit Tests for Secure Environment Manager
# =======================================

import pytest
import os
from unittest.mock import patch, Mock
from pathlib import Path
import sys

# Remove direct imports - use fixtures from conftest.py
# from secure_env_manager import SecureEnvManager


class TestSecureEnvManager:
    """Test cases for Secure Environment Manager."""

    def test_initialization(self, secure_env_manager):
        """Test SecureEnvManager initializes correctly."""
        assert hasattr(secure_env_manager, 'required_keys')
        assert hasattr(secure_env_manager, 'optional_keys')
        assert 'OPENAI_API_KEY' in secure_env_manager.required_keys
        assert 'ANTHROPIC_API_KEY' in secure_env_manager.optional_keys

    def test_validate_openai_key_valid(self, secure_env_manager):
        """Test OpenAI key validation with valid key."""
        valid_key = "sk-proj-1234567890abcdefghijklmnopqrstuv"
        assert secure_env_manager._validate_openai_key(valid_key) is True

    def test_validate_openai_key_invalid(self, secure_env_manager):
        """Test OpenAI key validation with invalid key."""
        invalid_keys = [
            "",  # Empty
            "sk-123",  # Too short
            "pk-1234567890abcdefghijklmnopqrstuv",  # Wrong prefix
            "sk-proj-1234567890abcdefghijklmnopqrs",  # Too short
        ]
        for key in invalid_keys:
            assert secure_env_manager._validate_openai_key(key) is False

    def test_validate_generic_key_valid(self, secure_env_manager):
        """Test generic key validation with valid key."""
        valid_key = "1234567890abcdefghijklmnopqrstuv"
        assert secure_env_manager._validate_generic_key(valid_key) is True

    def test_validate_generic_key_invalid(self, secure_env_manager):
        """Test generic key validation with invalid key."""
        invalid_keys = [
            "",  # Empty
            "123",  # Too short
        ]
        for key in invalid_keys:
            assert secure_env_manager._validate_generic_key(key) is False

    def test_get_value_preview(self, secure_env_manager):
        """Test API key preview generation."""
        # Long key should be masked
        long_key = "sk-proj-1234567890abcdefghijklmnopqrstuv"
        preview = secure_env_manager._get_value_preview(long_key)
        assert "****" in preview
        assert len(preview) < len(long_key)

        # Short key should be fully masked
        short_key = "123"
        preview = secure_env_manager._get_value_preview(short_key)
        assert preview == "****"

        # None/empty should return None
        assert secure_env_manager._get_value_preview(None) is None
        assert secure_env_manager._get_value_preview("") is None

    @patch.dict(os.environ, {}, clear=True)
    def test_check_environment_no_keys(self, secure_env_manager):
        """Test environment check with no API keys."""
        results = secure_env_manager.check_environment()

        # OpenAI should be marked as not set
        openai_status = results['OPENAI_API_KEY']
        assert openai_status['required'] is True
        assert openai_status['is_set'] is False
        assert openai_status['is_valid'] is False

        # Optional keys should also be not set
        anthropic_status = results['ANTHROPIC_API_KEY']
        assert anthropic_status['required'] is False
        assert anthropic_status['is_set'] is False

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True)
    def test_check_environment_with_openai_key(self, secure_env_manager):
        """Test environment check with valid OpenAI key."""
        results = secure_env_manager.check_environment()

        openai_status = results['OPENAI_API_KEY']
        assert openai_status['required'] is True
        assert openai_status['is_set'] is True
        assert openai_status['is_valid'] is True
        assert openai_status['value_preview'] is not None

    def test_validate_all_keys_no_keys(self, secure_env_manager):
        """Test validate_all_keys with no keys set."""
        with patch.dict(os.environ, {}, clear=True):
            assert secure_env_manager.validate_all_keys() is False

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True)
    def test_validate_all_keys_with_valid_key(self, secure_env_manager):
        """Test validate_all_keys with valid required key."""
        assert secure_env_manager.validate_all_keys() is True

    def test_get_missing_keys_no_keys(self, secure_env_manager):
        """Test get_missing_keys with no keys set."""
        with patch.dict(os.environ, {}, clear=True):
            missing = secure_env_manager.get_missing_keys()
            assert 'OPENAI_API_KEY' in missing

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True)
    def test_get_missing_keys_with_valid_key(self, secure_env_manager):
        """Test get_missing_keys with valid required key."""
        missing = secure_env_manager.get_missing_keys()
        assert len(missing) == 0

    def test_secure_startup_check_failure(self, secure_env_manager):
        """Test secure_startup_check with missing keys."""
        with patch.dict(os.environ, {}, clear=True):
            assert secure_env_manager.secure_startup_check() is False

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True)
    def test_secure_startup_check_success(self, secure_env_manager):
        """Test secure_startup_check with valid keys."""
        assert secure_env_manager.secure_startup_check() is True

    def test_create_env_template(self, secure_env_manager, tmp_path):
        """Test environment template creation."""
        template_file = tmp_path / ".env.template"
        secure_env_manager.create_env_template(str(template_file))

        assert template_file.exists()
        content = template_file.read_text()

        # Check for required sections
        assert "OPENAI_API_KEY" in content
        assert "ANTHROPIC_API_KEY" in content
        assert "Application Configuration" in content
        assert "Security Configuration" in content

    def test_display_status_no_keys(self, secure_env_manager, capsys):
        """Test display_status with no keys (captures output)."""
        with patch.dict(os.environ, {}, clear=True):
            secure_env_manager.display_status()
            captured = capsys.readouterr()

            assert "🔐 Atmosphere Arcade - Secure Environment Check" in captured.out
            assert "❌ OPENAI_API_KEY" in captured.out
            assert "❌ Some required API keys are missing or invalid" in captured.out

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True)
    def test_display_status_with_valid_key(self, secure_env_manager, capsys):
        """Test display_status with valid key."""
        secure_env_manager.display_status()
        captured = capsys.readouterr()

        assert "✅ OPENAI_API_KEY" in captured.out
        assert "🎉 All required API keys are properly configured!" in captured.out


class TestSecureEnvManagerIntegration:
    """Integration tests for SecureEnvManager."""

    def test_full_workflow(self, tmp_path, secure_env_manager):
        """Test complete workflow from template creation to validation."""
        # Create template
        template_file = tmp_path / ".env.template"
        secure_env_manager.create_env_template(str(template_file))
        assert template_file.exists()

        # Simulate setting environment variable
        test_key = 'sk-proj-1234567890abcdefghijklmnopqrstuv'
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
            # Validate the key is recognized
            results = secure_env_manager.check_environment()
            openai_status = results['OPENAI_API_KEY']

            assert openai_status['is_set'] is True
            assert openai_status['is_valid'] is True
            assert openai_status['value_preview'] is not None

            # Test full validation
            assert secure_env_manager.validate_all_keys() is True
            assert secure_env_manager.secure_startup_check() is True

            # Test missing keys list is empty
            missing = secure_env_manager.get_missing_keys()
            assert len(missing) == 0

    def test_mixed_environment(self, secure_env_manager):
        """Test with mix of valid and invalid keys."""
        # Set valid OpenAI key and invalid optional key
        with patch.dict(os.environ, {
            'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv',
            'ANTHROPIC_API_KEY': 'short'
        }, clear=True):
            results = secure_env_manager.check_environment()

            # OpenAI should be valid
            assert results['OPENAI_API_KEY']['is_valid'] is True

            # Anthropic should be set but invalid (too short)
            assert results['ANTHROPIC_API_KEY']['is_set'] is True
            assert results['ANTHROPIC_API_KEY']['is_valid'] is False

            # Overall validation should still pass (OpenAI is required and valid)
            assert secure_env_manager.validate_all_keys() is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
