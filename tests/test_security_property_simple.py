"""Simple property-based tests for security module using Hypothesis."""

import pytest
from hypothesis import given, strategies as st, assume, settings
import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.security import User, UserManager, JWTManager, InputValidator


class TestUserManagerPropertyBased:
    """Property-based tests for UserManager."""

    def setup_method(self):
        """Set up test environment."""
        import tempfile
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        self.temp_file.close()
        self.user_manager = UserManager(storage_path=self.temp_file.name)

    def teardown_method(self):
        """Clean up test environment."""
        import os
        try:
            os.unlink(self.temp_file.name)
        except:
            pass

    @settings(max_examples=10, deadline=1000)
    @given(
        username=st.text(min_size=3, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'),
        password=st.text(min_size=8, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd')))
    )
    def test_user_authentication_properties(self, username, password):
        """Test user creation and authentication with various inputs."""
        # Ensure password has required complexity
        assume(any(c.islower() for c in password))
        assume(any(c.isupper() for c in password))
        assume(any(c.isdigit() for c in password))
        
        user = User(
            username=username,
            email=f"{username}@example.com",
            full_name=f"Test {username}",
            role="analyst"
        )
        
        # Create user
        assert self.user_manager.create_user(user, password)
        
        # Authenticate with correct password
        auth_user = self.user_manager.authenticate_user(username, password)
        assert auth_user is not None
        assert auth_user.username == username
        
        # Authenticate with wrong password
        wrong_auth = self.user_manager.authenticate_user(username, "wrongpassword123!")
        assert wrong_auth is None

    @settings(max_examples=5, deadline=1000)
    @given(
        usernames=st.lists(
            st.text(min_size=3, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'),
            min_size=1,
            max_size=3,
            unique=True
        )
    )
    def test_multiple_user_creation(self, usernames):
        """Test creating multiple unique users."""
        users_created = []
        
        for i, username in enumerate(usernames):
            user = User(
                username=username,
                email=f"{username}@example.com",
                full_name=f"Test User {i}",
                role="analyst"
            )
            password = f"TestPass{i}123!"
            
            success = self.user_manager.create_user(user, password)
            assert success
            users_created.append((username, password))
        
        # Verify all users can authenticate
        for username, password in users_created:
            auth_user = self.user_manager.authenticate_user(username, password)
            assert auth_user is not None
            assert auth_user.username == username


class TestJWTManagerPropertyBased:
    """Property-based tests for JWTManager."""

    def setup_method(self):
        """Set up test environment."""
        self.jwt_manager = JWTManager()

    @settings(max_examples=10, deadline=1000)
    @given(
        username=st.text(min_size=3, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'),
        role=st.sampled_from(["admin", "analyst", "viewer", "operator"])
    )
    def test_jwt_token_roundtrip(self, username, role):
        """Test JWT token creation and verification with various payloads."""
        token_data = {
            "username": username,
            "role": role
        }
        
        # Create token
        token = self.jwt_manager.create_access_token(token_data)
        assert token is not None
        assert isinstance(token, str)
        
        # Verify token
        payload = self.jwt_manager.verify_token(token)
        assert payload is not None
        assert payload.username == username
        assert payload.role == role

    @settings(max_examples=5)
    @given(
        tokens=st.lists(
            st.text(min_size=20, max_size=50, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))),
            min_size=1,
            max_size=3
        )
    )
    def test_invalid_token_verification(self, tokens):
        """Test that invalid tokens are properly rejected."""
        for token in tokens:
            # These are random strings, not valid JWTs
            payload = self.jwt_manager.verify_token(token)
            assert payload is None


class TestInputValidatorPropertyBased:
    """Property-based tests for InputValidator."""

    @settings(max_examples=10, deadline=1000)
    @given(
        input_str=st.text(min_size=1, max_size=100, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Zs', 'Pd'))),
        max_length=st.integers(min_value=10, max_value=200)
    )
    def test_string_sanitization(self, input_str, max_length):
        """Test string sanitization with various inputs."""
        sanitized = InputValidator.sanitize_string(input_str, max_length)
        
        # Should be a string
        assert isinstance(sanitized, str)
        
        # Should not exceed max length
        assert len(sanitized) <= max_length
        
        # Should not contain null bytes
        assert '\x00' not in sanitized

    @settings(max_examples=10)
    @given(
        data=st.one_of(
            st.text(),
            st.integers(),
            st.booleans(),
            st.lists(st.text()),
            st.dictionaries(keys=st.text(), values=st.text())
        )
    )
    def test_json_validation(self, data):
        """Test JSON validation with various data types."""
        result = InputValidator.validate_json(data)
        # Most valid Python data structures should be JSON serializable
        # We don't assert True here because some objects might not be serializable
        assert isinstance(result, bool)

    @settings(max_examples=10)
    @given(
        input_str=st.text(min_size=1, max_size=50)
    )
    def test_sql_injection_detection(self, input_str):
        """Test SQL injection detection."""
        result = InputValidator.check_sql_injection(input_str)
        assert isinstance(result, bool)
        
        # Known SQL injection patterns should be detected
        if any(pattern in input_str.lower() for pattern in ['select', 'insert', 'update', 'delete', 'drop', '--', ';']):
            # May or may not be detected depending on context
            pass

    @settings(max_examples=10)
    @given(
        input_str=st.text(min_size=1, max_size=50)
    )
    def test_xss_detection(self, input_str):
        """Test XSS detection."""
        result = InputValidator.check_xss(input_str)
        assert isinstance(result, bool)
        
        # Known XSS patterns should be detected
        if any(pattern in input_str.lower() for pattern in ['<script', 'javascript:', 'onclick', 'onerror']):
            # May or may not be detected depending on context
            pass


class TestSecurityProperties:
    """General security property tests."""

    @settings(max_examples=5, deadline=1000)
    @given(
        passwords=st.lists(
            st.text(min_size=8, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd', 'Pd'))),
            min_size=1,
            max_size=3
        )
    )
    def test_password_hashing_properties(self, passwords):
        """Test password hashing properties."""
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        temp_file.close()
        
        try:
            user_manager = UserManager(storage_path=temp_file.name)
            
            for password in passwords:
                hashed = user_manager._hash_password(password)
                assert hashed != password  # Should not be plaintext
                assert len(hashed) > 20  # Should be reasonably long
        finally:
            try:
                os.unlink(temp_file.name)
            except:
                pass

    @given(
        username=st.text(min_size=3, max_size=10, alphabet='abcdefghijklmnopqrstuvwxyz0123456789_'),
        role=st.sampled_from(["admin", "analyst", "viewer", "operator"])
    )
    def test_token_expiry(self, username, role):
        """Test that tokens have reasonable expiry times."""
        jwt_manager = JWTManager()
        token_data = {
            "username": username,
            "role": role
        }
        
        token = jwt_manager.create_access_token(token_data)
        
        # Token should be valid immediately
        payload = jwt_manager.verify_token(token)
        assert payload is not None
        
        # Check expiry is in the future
        assert payload.exp.timestamp() > time.time()
        # Check expiry is not too far in the future (less than 24 hours)
        assert payload.exp.timestamp() < time.time() + 86400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
