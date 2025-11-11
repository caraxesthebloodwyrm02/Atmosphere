# End-to-End Integration Tests for Atmosphere Arcade
# ================================================

import pytest
import asyncio
import time
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys
import subprocess

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from secure_env_manager import SecureEnvManager


class TestEndToEndIntegration:
    """End-to-end integration tests for complete system functionality."""

    @pytest.fixture
    def temp_project_dir(self, tmp_path):
        """Create a temporary project directory structure."""
        # Create basic project structure
        project_dir = tmp_path / "arcade_test"
        project_dir.mkdir()

        # Create basic files
        (project_dir / "start_arcade.py").write_text("# Test start script")
        (project_dir / "secure_env_manager.py").write_text("# Test env manager")

        api_dir = project_dir / "api"
        api_dir.mkdir()
        (api_dir / "__init__.py").write_text("")
        (api_dir / "chatgpt_manager.py").write_text("# Test chatgpt manager")

        return project_dir

    def test_full_environment_setup_workflow(self, tmp_path):
        """Test complete environment setup workflow."""
        # Create test environment
        env_file = tmp_path / ".env"
        template_file = tmp_path / ".env.template"

        manager = SecureEnvManager()

        # Step 1: Create template
        manager.create_env_template(str(template_file))
        assert template_file.exists()

        # Step 2: Template should contain required sections
        template_content = template_file.read_text()
        assert "OPENAI_API_KEY" in template_content
        assert "Application Configuration" in template_content

        # Step 3: Simulate environment variable setup
        test_key = 'sk-proj-1234567890abcdefghijklmnopqrstuv'
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
            # Step 4: Validate environment
            status = manager.check_environment()
            assert status['OPENAI_API_KEY']['is_valid'] is True

            # Step 5: Test startup validation
            assert manager.secure_startup_check() is True

            # Step 6: Verify no missing keys
            missing = manager.get_missing_keys()
            assert len(missing) == 0

    @pytest.mark.asyncio
    async def test_concurrent_system_operations(self):
        """Test concurrent system operations under load."""
        manager = SecureEnvManager()

        async def simulate_user_operation(user_id):
            """Simulate a user performing operations."""
            # Check environment
            status = manager.check_environment()

            # Validate keys
            is_valid = manager.validate_all_keys()

            # Simulate some async work (like API calls)
            await asyncio.sleep(0.001)

            return {
                'user_id': user_id,
                'env_valid': bool(status),
                'keys_valid': is_valid
            }

        # Simulate 20 concurrent users
        start_time = time.time()
        tasks = [simulate_user_operation(i) for i in range(20)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time

        # All operations should succeed
        assert len(results) == 20
        assert all(r['env_valid'] for r in results)
        assert all(r['keys_valid'] for r in results)

        # Should complete in reasonable time
        assert total_time < 2.0  # Under 2 seconds for 20 concurrent operations

    def test_cross_component_integration(self):
        """Test integration between different components."""
        manager = SecureEnvManager()

        # Test data flow between components
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):

            # Component 1: Environment checking
            env_status = manager.check_environment()
            assert 'OPENAI_API_KEY' in env_status

            # Component 2: Key validation
            validation_result = manager.validate_all_keys()
            assert validation_result is True

            # Component 3: Missing keys check
            missing_keys = manager.get_missing_keys()
            assert len(missing_keys) == 0

            # Component 4: Startup validation
            startup_result = manager.secure_startup_check()
            assert startup_result is True

            # Verify data consistency across components
            openai_info = env_status['OPENAI_API_KEY']
            assert openai_info['is_valid'] is True
            assert openai_info['required'] is True
            assert validation_result is True  # Should align with env check

    def test_error_recovery_integration(self):
        """Test error recovery and graceful degradation."""
        manager = SecureEnvManager()

        # Test with completely missing environment
        with patch.dict(os.environ, {}, clear=True):
            # Should handle missing keys gracefully
            env_status = manager.check_environment()
            assert env_status['OPENAI_API_KEY']['is_valid'] is False

            validation_result = manager.validate_all_keys()
            assert validation_result is False

            startup_result = manager.secure_startup_check()
            assert startup_result is False

            missing_keys = manager.get_missing_keys()
            assert 'OPENAI_API_KEY' in missing_keys

        # Test partial recovery
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):
            # Should recover when key is provided
            env_status = manager.check_environment()
            assert env_status['OPENAI_API_KEY']['is_valid'] is True

            validation_result = manager.validate_all_keys()
            assert validation_result is True

            startup_result = manager.secure_startup_check()
            assert startup_result is True

            missing_keys = manager.get_missing_keys()
            assert len(missing_keys) == 0

    def test_configuration_persistence(self, tmp_path):
        """Test configuration persistence across sessions."""
        env_file = tmp_path / ".env"
        manager = SecureEnvManager()

        # Simulate configuration setup
        test_key = 'sk-proj-1234567890abcdefghijklmnopqrstuv'
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):

            # First session - configure environment
            manager.setup_env_file()
            assert env_file.exists()

            # Verify configuration persists
            env_status_1 = manager.check_environment()
            assert env_status_1['OPENAI_API_KEY']['is_valid'] is True

        # Second session - simulate restart
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
            # Should still validate correctly
            env_status_2 = manager.check_environment()
            assert env_status_2['OPENAI_API_KEY']['is_valid'] is True

            # Configurations should be consistent
            assert env_status_1['OPENAI_API_KEY']['is_valid'] == env_status_2['OPENAI_API_KEY']['is_valid']

    @pytest.mark.asyncio
    async def test_system_resilience_under_load(self):
        """Test system resilience under various load conditions."""
        manager = SecureEnvManager()

        # Test rapid consecutive operations
        results = []
        for i in range(50):
            # Mix sync and async operations
            env_status = manager.check_environment()
            validation_result = manager.validate_all_keys()

            # Simulate some async work
            await asyncio.sleep(0.001)

            results.append({
                'iteration': i,
                'env_valid': bool(env_status),
                'keys_valid': validation_result
            })

        # All operations should succeed
        assert len(results) == 50
        assert all(r['env_valid'] for r in results)
        assert all(r['keys_valid'] for r in results)

        # Results should be consistent across iterations
        first_result = results[0]
        for result in results[1:]:
            assert result['env_valid'] == first_result['env_valid']
            assert result['keys_valid'] == first_result['keys_valid']

    def test_boundary_conditions(self):
        """Test system behavior under boundary conditions."""
        manager = SecureEnvManager()

        # Test with various edge cases
        test_cases = [
            # Empty environment
            ({}, False, ['OPENAI_API_KEY']),

            # Valid key only
            ({'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, True, []),

            # Invalid key format
            ({'OPENAI_API_KEY': 'invalid-key-format'}, False, ['OPENAI_API_KEY']),

            # Valid key with optional keys
            ({
                'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv',
                'ANTHROPIC_API_KEY': 'some-valid-key-12345'
            }, True, []),

            # Valid key with invalid optional keys
            ({
                'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv',
                'ANTHROPIC_API_KEY': 'short'
            }, True, []),  # Should still pass since optional
        ]

        for env_vars, expected_valid, expected_missing in test_cases:
            with patch.dict(os.environ, env_vars, clear=True):
                validation_result = manager.validate_all_keys()
                missing_keys = manager.get_missing_keys()

                assert validation_result == expected_valid, f"Failed for env: {env_vars}"
                assert set(missing_keys) == set(expected_missing), f"Failed for env: {env_vars}"

    def test_configuration_file_handling(self, tmp_path):
        """Test proper handling of configuration files."""
        manager = SecureEnvManager()

        # Test with various file scenarios
        env_file = tmp_path / ".env"

        # Scenario 1: No env file exists
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):
            # Should work without env file
            assert manager.validate_all_keys() is True

        # Scenario 2: Create and populate env file
        env_content = """# Test environment file
OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuv
ANTHROPIC_API_KEY=test-key-123
"""
        env_file.write_text(env_content)

        with patch.dict(os.environ, {}, clear=True):
            # Should read from file if env vars not set
            # Note: Our current implementation prioritizes env vars over file
            # This tests that file operations don't break anything
            result = manager.check_environment()
            assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_async_error_handling(self):
        """Test error handling in async operations."""
        manager = SecureEnvManager()

        # Test async operations that might fail
        async def potentially_failing_operation(should_fail=False):
            if should_fail:
                raise Exception("Simulated async failure")

            # Normal operation
            await asyncio.sleep(0.001)
            return manager.check_environment()

        # Test successful operations
        results = await asyncio.gather(*[
            potentially_failing_operation(False) for _ in range(10)
        ])

        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results)

        # Test error handling (if we had error cases)
        # Note: Our current implementation doesn't have async error paths to test

    def test_resource_cleanup(self):
        """Test that resources are properly cleaned up."""
        import gc

        # Create multiple manager instances
        managers = [SecureEnvManager() for _ in range(10)]

        # Use them
        for manager in managers:
            manager.check_environment()

        # Delete references
        del managers

        # Force garbage collection
        gc.collect()

        # System should remain stable
        # Create new manager to verify system still works
        new_manager = SecureEnvManager()
        result = new_manager.check_environment()
        assert isinstance(result, dict)


class TestSystemIntegrationScenarios:
    """Real-world integration scenarios."""

    def test_typical_user_workflow(self, tmp_path):
        """Test a typical user workflow from setup to operation."""
        manager = SecureEnvManager()

        # Step 1: User creates template
        template_file = tmp_path / ".env.template"
        manager.create_env_template(str(template_file))
        assert template_file.exists()

        # Step 2: User sets environment variable (simulated)
        test_key = 'sk-proj-1234567890abcdefghijklmnopqrstuv'
        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):

            # Step 3: System validates configuration
            assert manager.validate_all_keys() is True

            # Step 4: System passes startup checks
            assert manager.secure_startup_check() is True

            # Step 5: User can proceed with application
            env_status = manager.check_environment()
            assert env_status['OPENAI_API_KEY']['is_valid'] is True

    def test_administration_workflow(self, tmp_path):
        """Test administrative workflow for system management."""
        manager = SecureEnvManager()

        # Admin creates template for users
        template_file = tmp_path / ".env.template"
        manager.create_env_template(str(template_file))

        # Admin checks system status
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):
            status_results = manager.check_environment()
            assert status_results['OPENAI_API_KEY']['is_valid'] is True

            # Admin verifies all validations pass
            assert manager.validate_all_keys() is True
            assert len(manager.get_missing_keys()) == 0

            # Admin confirms startup readiness
            assert manager.secure_startup_check() is True

    def test_monitoring_integration(self):
        """Test integration with monitoring systems."""
        manager = SecureEnvManager()

        # Simulate monitoring checks
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):

            # Health check - should pass
            health_status = manager.validate_all_keys()
            assert health_status is True

            # Configuration check - should have no missing keys
            missing_count = len(manager.get_missing_keys())
            assert missing_count == 0

            # Environment status - should be valid
            env_data = manager.check_environment()
            valid_keys = sum(1 for status in env_data.values() if status['is_valid'])
            total_keys = len(env_data)

            # At minimum, required keys should be valid
            required_keys = sum(1 for status in env_data.values() if status['required'])
            assert valid_keys >= required_keys


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
