#!/usr/bin/env python3
"""
Test runner script for Atmosphere modules
Runs all unit tests and generates coverage reports
"""

import subprocess
import sys
import os
from pathlib import Path

def run_tests():
    """Run all tests with coverage."""

    # Change to project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print("🧪 Running Atmosphere Test Suite")
    print("=" * 50)

    # Run smoke tests first
    print("\n🚀 Running smoke tests...")
    result = subprocess.run([sys.executable, "smoke_tests.py"], capture_output=True, text=True)

    if result.returncode == 0:
        print("✅ Smoke tests passed")
        print(result.stdout)
    else:
        print("❌ Smoke tests failed")
        print(result.stdout)
        print(result.stderr)
        return False

    # Run unit tests for each module
    test_modules = [
        ("Delay/test_delay_comprehensive.py", "Delay Module"),
        ("i_o/test_io_comprehensive.py", "i_o Module"),
        ("i_o/test_smart_optimizer.py", "Smart Optimizer"),
        ("mental-load-balancer/test_mental_load_balancer.py", "Mental Load Balancer"),
    ]

    all_passed = True

    for test_file, module_name in test_modules:
        if Path(test_file).exists():
            print(f"\n🧪 Running {module_name} tests...")
            result = subprocess.run([
                sys.executable, "-m", "pytest", test_file,
                "-v", "--tb=short"
            ], capture_output=True, text=True)

            if result.returncode == 0:
                print(f"✅ {module_name} tests passed")
            else:
                print(f"❌ {module_name} tests failed")
                print(result.stdout)
                print(result.stderr)
                all_passed = False
        else:
            print(f"⚠️  {module_name} test file not found: {test_file}")
            all_passed = False

    # Try to run coverage on core modules
    print("\n📊 Generating coverage report...")
    try:
        result = subprocess.run([
            sys.executable, "-m", "pytest",
            "--cov=src.atmosphere_audio.delay.core.delay_essence",
            "--cov=Delay.delay_essence",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov",
            "-x",  # Stop on first failure
            "Delay/test_delay_comprehensive.py",
            "i_o/test_io_comprehensive.py"
        ], capture_output=True, text=True)

        print("Coverage report:")
        print(result.stdout)

        if result.returncode != 0:
            print("Coverage stderr:")
            print(result.stderr)

    except Exception as e:
        print(f"Coverage generation failed: {e}")

    return all_passed

def run_specific_test(test_path):
    """Run a specific test file."""
    if not Path(test_path).exists():
        print(f"Test file not found: {test_path}")
        return False

    print(f"Running specific test: {test_path}")
    result = subprocess.run([
        sys.executable, "-m", "pytest", test_path, "-v"
    ], capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print("STDERR:")
        print(result.stderr)

    return result.returncode == 0

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run specific test
        test_path = sys.argv[1]
        success = run_specific_test(test_path)
    else:
        # Run all tests
        success = run_tests()

    sys.exit(0 if success else 1)
