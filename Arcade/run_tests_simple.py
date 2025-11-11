#!/usr/bin/env python3
"""
Simple Test Runner for Atmosphere Arcade
=========================================

Runs basic functionality tests without pytest dependencies.
"""

import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_secure_env_manager():
    """Test Secure Environment Manager functionality."""
    print("🧪 Testing Secure Environment Manager...")

    try:
        from secure_env_manager import SecureEnvManager

        manager = SecureEnvManager()

        # Test initialization
        assert hasattr(manager, 'required_keys')
        assert hasattr(manager, 'optional_keys')
        assert 'OPENAI_API_KEY' in manager.required_keys
        print("✅ Initialization test passed")

        # Test key validation
        valid_key = "sk-proj-1234567890abcdefghijklmnopqrstuv"
        assert manager._validate_openai_key(valid_key) is True

        invalid_keys = ["", "sk-123", "pk-1234567890abcdefghijklmnopqrstuv"]
        for key in invalid_keys:
            assert manager._validate_openai_key(key) is False
        print("✅ Key validation tests passed")

        # Test environment checking
        from unittest.mock import patch
        with patch.dict(os.environ, {}, clear=True):
            results = manager.check_environment()
            assert results['OPENAI_API_KEY']['is_valid'] is False

        with patch.dict(os.environ, {'OPENAI_API_KEY': valid_key}, clear=True):
            results = manager.check_environment()
            assert results['OPENAI_API_KEY']['is_valid'] is True
        print("✅ Environment checking tests passed")

        # Test validation functions
        with patch.dict(os.environ, {}, clear=True):
            assert manager.validate_all_keys() is False
            assert len(manager.get_missing_keys()) > 0

        with patch.dict(os.environ, {'OPENAI_API_KEY': valid_key}, clear=True):
            assert manager.validate_all_keys() is True
            assert len(manager.get_missing_keys()) == 0
        print("✅ Validation function tests passed")

        return True

    except Exception as e:
        print(f"❌ Secure Environment Manager test failed: {e}")
        return False

def test_performance_basics():
    """Test basic performance metrics."""
    print("⚡ Testing basic performance metrics...")

    try:
        import time
        from secure_env_manager import SecureEnvManager

        manager = SecureEnvManager()

        # Test response time
        start_time = time.time()
        for _ in range(10):
            manager.check_environment()
        end_time = time.time()

        avg_time = (end_time - start_time) / 10
        assert avg_time < 0.1  # Should be under 100ms
        print(f"✅ Average response time: {avg_time:.4f}s")
        return True

    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False

def test_integration_workflow():
    """Test basic integration workflow."""
    print("🔗 Testing integration workflow...")

    try:
        from secure_env_manager import SecureEnvManager
        import tempfile
        from pathlib import Path

        manager = SecureEnvManager()

        # Test template creation
        with tempfile.TemporaryDirectory() as tmp_dir:
            template_file = Path(tmp_dir) / ".env.template"
            manager.create_env_template(str(template_file))

            assert template_file.exists()
            content = template_file.read_text()
            assert "OPENAI_API_KEY" in content
            assert "ANTHROPIC_API_KEY" in content

        print("✅ Template creation test passed")

        # Test full workflow
        from unittest.mock import patch
        test_key = 'sk-proj-1234567890abcdefghijklmnopqrstuv'

        with patch.dict(os.environ, {'OPENAI_API_KEY': test_key}, clear=True):
            assert manager.validate_all_keys() is True
            assert manager.secure_startup_check() is True
            assert len(manager.get_missing_keys()) == 0

        print("✅ Full workflow test passed")

        return True

    except Exception as e:
        print(f"❌ Integration workflow test failed: {e}")
        return False

def run_all_tests():
    """Run all available tests."""
    print("🚀 Atmosphere Arcade - Simple Test Runner")
    print("=" * 50)

    tests = [
        ("Secure Environment Manager", test_secure_env_manager),
        ("Basic Performance", test_performance_basics),
        ("Integration Workflow", test_integration_workflow),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔧 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Atmosphere Arcade testing infrastructure is working!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
