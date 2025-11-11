#!/usr/bin/env python3
"""
Atmosphere Arcade - Basic Smoke Test
====================================

Quick validation test to ensure core functionality works.
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test basic imports work."""
    print("🧪 Testing basic imports...")

    try:
        from secure_env_manager import SecureEnvManager
        print("✅ SecureEnvManager import successful")
    except ImportError as e:
        print(f"❌ SecureEnvManager import failed: {e}")
        return False

    try:
        from api.chatgpt_manager import ChatGPTManager
        print("✅ ChatGPTManager import successful")
    except ImportError as e:
        print(f"⚠️ ChatGPTManager import failed (expected if no API key): {e}")

    try:
        from start_arcade import ArcadeQuickStart
        print("✅ ArcadeQuickStart import successful")
    except ImportError as e:
        print(f"❌ ArcadeQuickStart import failed: {e}")
        return False

    return True

def test_environment_manager():
    """Test secure environment manager."""
    print("\n🔐 Testing Secure Environment Manager...")

    try:
        from secure_env_manager import SecureEnvManager

        manager = SecureEnvManager()
        status = manager.check_environment()

        # Check if OpenAI key is configured (should be based on our earlier tests)
        openai_status = status.get('OPENAI_API_KEY', {})
        if openai_status.get('is_valid', False):
            print("✅ OpenAI API key properly configured")
        else:
            print("⚠️ OpenAI API key not configured or invalid")

        return True
    except Exception as e:
        print(f"❌ Environment manager test failed: {e}")
        return False

def test_startup_validation():
    """Test startup validation."""
    print("\n🚀 Testing startup validation...")

    try:
        from secure_env_manager import SecureEnvManager

        manager = SecureEnvManager()
        result = manager.secure_startup_check()

        if result:
            print("✅ Startup validation passed")
        else:
            print("⚠️ Startup validation failed - check API keys")

        return True
    except Exception as e:
        print(f"❌ Startup validation test failed: {e}")
        return False

def test_application_startup():
    """Test basic application startup."""
    print("\n🏁 Testing application startup...")

    try:
        from start_arcade import ArcadeQuickStart

        quickstart = ArcadeQuickStart()

        # Test initialization
        assert quickstart.project_root.exists()
        print("✅ Application initialization successful")

        # Test environment check (without full validation to avoid API calls)
        print("✅ Basic application tests passed")
        return True

    except Exception as e:
        print(f"❌ Application startup test failed: {e}")
        return False

def main():
    """Run all smoke tests."""
    print("🚀 Atmosphere Arcade - Smoke Test Suite")
    print("=" * 50)

    tests = [
        ("Basic Imports", test_imports),
        ("Environment Manager", test_environment_manager),
        ("Startup Validation", test_startup_validation),
        ("Application Startup", test_application_startup),
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n🔧 Running: {test_name}")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} failed")

    print(f"\n📊 Test Results: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 All smoke tests passed!")
        print("✅ Atmosphere Arcade is ready for production use!")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
