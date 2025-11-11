# Performance Benchmarks for Atmosphere Arcade
# ==========================================

import pytest
import asyncio
import time
import psutil
import os
from unittest.mock import Mock, patch, AsyncMock
import sys
from pathlib import Path
import statistics

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from secure_env_manager import SecureEnvManager


class TestPerformanceBenchmarks:
    """Performance and load testing benchmarks."""

    @pytest.fixture
    def env_manager(self):
        """Create SecureEnvManager instance for testing."""
        return SecureEnvManager()

    def test_environment_check_performance(self, env_manager, benchmark):
        """Benchmark environment check performance."""
        def run_env_check():
            return env_manager.check_environment()

        result = benchmark(run_env_check)

        # Should complete in under 100ms
        assert result.stats.mean < 0.1
        assert len(result.stats.data) > 0

    def test_validation_performance(self, env_manager, benchmark):
        """Benchmark API key validation performance."""
        # Set up test environment
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):
            def run_validation():
                return env_manager.validate_all_keys()

            result = benchmark(run_validation)

            # Should complete in under 50ms
            assert result.stats.mean < 0.05
            assert result is True

    @pytest.mark.asyncio
    async def test_concurrent_environment_checks(self):
        """Test concurrent environment checks performance."""
        manager = SecureEnvManager()

        async def single_check():
            return manager.check_environment()

        # Run 10 concurrent checks
        start_time = time.time()
        tasks = [single_check() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time

        # All results should be dictionaries
        assert all(isinstance(r, dict) for r in results)
        assert len(results) == 10

        # Should complete in under 1 second
        assert total_time < 1.0

        # Calculate average time per check
        avg_time = total_time / 10
        assert avg_time < 0.1  # Under 100ms per check

    def test_memory_usage_baseline(self, env_manager):
        """Test memory usage for basic operations."""
        process = psutil.Process(os.getpid())

        # Get baseline memory
        baseline_memory = process.memory_info().rss

        # Perform operations
        for _ in range(100):
            env_manager.check_environment()
            env_manager.validate_all_keys()

        # Check memory after operations
        final_memory = process.memory_info().rss
        memory_increase = final_memory - baseline_memory

        # Memory increase should be reasonable (less than 10MB)
        assert memory_increase < 10 * 1024 * 1024

    def test_startup_time_benchmark(self):
        """Benchmark application startup time."""
        start_time = time.time()

        # Import and initialize core components
        from secure_env_manager import SecureEnvManager

        manager = SecureEnvManager()
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):
            result = manager.secure_startup_check()

        end_time = time.time()
        startup_time = end_time - start_time

        # Startup should complete in under 2 seconds
        assert startup_time < 2.0
        assert result is True

    @pytest.mark.asyncio
    async def test_async_operation_performance(self):
        """Test performance of async operations."""
        # Mock async operations that would normally call external APIs
        async def mock_async_operation(delay=0.01):
            await asyncio.sleep(delay)
            return {"result": "success"}

        # Test concurrent async operations
        start_time = time.time()
        tasks = [mock_async_operation(0.01) for _ in range(50)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time

        # All operations should succeed
        assert all(r["result"] == "success" for r in results)
        assert len(results) == 50

        # Should complete reasonably fast (under 1 second total)
        assert total_time < 1.0

    def test_large_environment_processing(self, env_manager):
        """Test performance with large environment data."""
        # Create a large environment simulation
        large_env = {}
        for i in range(100):
            large_env[f'TEST_VAR_{i}'] = f'value_{i}' * 100  # Large values

        # Add our test key
        large_env['OPENAI_API_KEY'] = 'sk-proj-1234567890abcdefghijklmnopqrstuv'

        with patch.dict(os.environ, large_env, clear=True):
            start_time = time.time()
            result = env_manager.check_environment()
            end_time = time.time()

            processing_time = end_time - start_time

            # Should still process quickly despite large environment
            assert processing_time < 0.5  # Under 500ms
            assert isinstance(result, dict)
            assert 'OPENAI_API_KEY' in result

    def test_template_generation_performance(self, env_manager, tmp_path):
        """Benchmark environment template generation."""
        template_file = tmp_path / ".env.template"

        start_time = time.time()
        env_manager.create_env_template(str(template_file))
        end_time = time.time()

        generation_time = end_time - start_time

        # Template generation should be fast
        assert generation_time < 0.1  # Under 100ms
        assert template_file.exists()

        # Verify template content
        content = template_file.read_text()
        assert len(content) > 1000  # Should be substantial
        assert "OPENAI_API_KEY" in content


class TestLoadTesting:
    """Load testing scenarios."""

    def test_multiple_managers_concurrent(self):
        """Test multiple SecureEnvManager instances running concurrently."""
        managers = [SecureEnvManager() for _ in range(5)]

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):
            start_time = time.time()

            # Run checks on all managers
            results = []
            for manager in managers:
                result = manager.check_environment()
                results.append(result)

            end_time = time.time()
            total_time = end_time - start_time

            # All should succeed
            assert all(isinstance(r, dict) for r in results)
            assert len(results) == 5

            # Should complete quickly
            assert total_time < 0.5

    @pytest.mark.asyncio
    async def test_high_frequency_checks(self):
        """Test high-frequency environment checks."""
        manager = SecureEnvManager()

        async def check_with_delay():
            await asyncio.sleep(0.001)  # Small delay between checks
            return manager.check_environment()

        # Run 100 rapid checks
        start_time = time.time()
        tasks = [check_with_delay() for _ in range(100)]
        results = await asyncio.gather(*tasks)
        end_time = time.time()

        total_time = end_time - start_time

        # All should succeed
        assert all(isinstance(r, dict) for r in results)
        assert len(results) == 100

        # Should handle high frequency well
        assert total_time < 2.0  # Under 2 seconds for 100 checks

    def test_memory_leak_detection(self):
        """Test for memory leaks during repeated operations."""
        manager = SecureEnvManager()
        process = psutil.Process(os.getpid())

        memory_readings = []

        # Perform operations and track memory
        for i in range(50):
            manager.check_environment()
            manager.validate_all_keys()

            if i % 10 == 0:  # Sample every 10 iterations
                memory_readings.append(process.memory_info().rss)

        if len(memory_readings) > 1:
            # Check for significant memory growth
            initial_memory = memory_readings[0]
            final_memory = memory_readings[-1]
            memory_growth = final_memory - initial_memory

            # Memory growth should be minimal (less than 5MB)
            assert memory_growth < 5 * 1024 * 1024

            # Memory should not continuously increase
            # Check that later readings aren't significantly higher than earlier ones
            for i in range(1, len(memory_readings)):
                growth_since_start = memory_readings[i] - memory_readings[0]
                assert growth_since_start < 3 * 1024 * 1024  # Less than 3MB total growth


class TestScalabilityMetrics:
    """Scalability and performance metrics."""

    def test_response_time_distribution(self):
        """Test response time distribution for consistent performance."""
        manager = SecureEnvManager()
        response_times = []

        # Collect multiple response times
        for _ in range(20):
            start_time = time.time()
            manager.check_environment()
            end_time = time.time()
            response_times.append(end_time - start_time)

        # Calculate statistics
        avg_time = statistics.mean(response_times)
        median_time = statistics.median(response_times)
        max_time = max(response_times)

        # Performance requirements
        assert avg_time < 0.05    # Average under 50ms
        assert median_time < 0.05 # Median under 50ms
        assert max_time < 0.1     # Max under 100ms

        # Check consistency (95th percentile should be reasonable)
        sorted_times = sorted(response_times)
        p95_index = int(0.95 * len(sorted_times))
        p95_time = sorted_times[min(p95_index, len(sorted_times) - 1)]
        assert p95_time < 0.08  # 95th percentile under 80ms

    def test_resource_efficiency(self):
        """Test resource efficiency under load."""
        manager = SecureEnvManager()

        # Track CPU usage during operations
        initial_cpu = psutil.cpu_percent(interval=None)

        # Perform intensive operations
        for _ in range(100):
            manager.check_environment()
            manager.validate_all_keys()

        final_cpu = psutil.cpu_percent(interval=None)

        # CPU usage should remain reasonable
        # Note: This is a rough check and may vary by system
        cpu_increase = final_cpu - initial_cpu
        assert cpu_increase < 50  # Less than 50% CPU increase

    def test_error_handling_performance(self):
        """Test that error handling doesn't impact performance significantly."""
        manager = SecureEnvManager()

        # Test with invalid keys
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid-key'}, clear=True):
            start_time = time.time()
            result = manager.validate_all_keys()
            end_time = time.time()

            error_handling_time = end_time - start_time

            # Error handling should be fast
            assert error_handling_time < 0.1  # Under 100ms
            assert result is False  # Should fail validation

        # Test with valid keys
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'sk-proj-1234567890abcdefghijklmnopqrstuv'}, clear=True):
            start_time = time.time()
            result = manager.validate_all_keys()
            end_time = time.time()

            success_time = end_time - start_time

            # Success case should also be fast
            assert success_time < 0.1  # Under 100ms
            assert result is True  # Should pass validation


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
