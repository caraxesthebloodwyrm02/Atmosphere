#!/usr/bin/env python3
"""
Atmosphere Installation & Setup Guide
====================================

Complete setup script for the Atmosphere project with all fixes applied.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, cwd=None, check=True):
    """Run a command and handle errors gracefully."""
    try:
        print(f"🔧 Running: {cmd}")
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )

        if check and result.returncode != 0:
            print(f"⚠️ Command failed (exit code {result.returncode})")
            print(f"Error: {result.stderr}")
            return False

        return True
    except Exception as e:
        print(f"❌ Command execution error: {e}")
        return False

def main():
    """Complete Atmosphere setup process."""

    print("🚀 ATMOSPHERE PROJECT SETUP")
    print("=" * 40)

    # Ensure we're in the project root
    project_root = Path(__file__).parent
    os.chdir(project_root)

    print(f"📍 Working directory: {project_root}")

    # Step 1: Install core dependencies
    print("\n📦 STEP 1: Installing Core Dependencies")
    print("-" * 40)

    success = run_command("pip install --upgrade pip")
    if not success:
        print("⚠️ Pip upgrade failed, continuing...")

    # Install with compatible versions for Python 3.14
    success = run_command("pip install numpy>=2.0.0 scipy>=1.12.0 pandas>=2.1.0 matplotlib>=3.8.0")
    if not success:
        print("❌ Core scientific packages installation failed")
        return False

    # Install web framework
    success = run_command("pip install fastapi>=0.104.0 uvicorn[standard]>=0.24.0 pydantic>=2.0.0")
    if not success:
        print("❌ Web framework installation failed")
        return False

    # Install additional dependencies
    success = run_command("pip install httpx>=0.25.0 python-dotenv>=1.0.0 openai>=1.0.0")
    if not success:
        print("❌ Additional dependencies installation failed")
        return False

    # Step 2: Install development dependencies
    print("\n🛠️ STEP 2: Installing Development Dependencies")
    print("-" * 45)

    success = run_command("pip install pytest>=8.0.0 pytest-asyncio>=0.21.0 black>=24.0.0 isort>=5.12.0")
    if not success:
        print("⚠️ Some development dependencies failed, but core functionality should work")

    # Step 3: Validate installation
    print("\n✅ STEP 3: Validating Installation")
    print("-" * 35)

    # Test key imports
    test_imports = [
        ("numpy", "Scientific computing"),
        ("pandas", "Data processing"),
        ("fastapi", "Web framework"),
        ("pydantic", "Data validation"),
        ("httpx", "HTTP client")
    ]

    failed_imports = []
    for module, description in test_imports:
        try:
            __import__(module)
            print(f"✅ {module} - {description}")
        except ImportError:
            print(f"❌ {module} - {description} (FAILED)")
            failed_imports.append(module)

    if failed_imports:
        print(f"\n⚠️ Some imports failed: {', '.join(failed_imports)}")
        print("You may need to install additional packages or check your Python environment")
    else:
        print("\n🎉 All core dependencies successfully installed!")

    # Step 4: Run configuration validation
    print("\n🔍 STEP 4: Running Configuration Validation")
    print("-" * 45)

    success = run_command("python validate_config.py")
    if success:
        print("✅ Configuration validation passed!")
    else:
        print("⚠️ Configuration validation had issues, but basic functionality should work")

    # Step 5: Final instructions
    print("\n🎯 SETUP COMPLETE!")
    print("=" * 20)

    print("\n🚀 To start the Atmosphere server:")
    print("   python Arcade/api/server.py")

    print("\n🔍 To test the learning companion API:")
    print("   python api_test_quick.py")

    print("\n📚 To run configuration validation:")
    print("   python validate_config.py")

    print("\n📖 For development:")
    print("   pip install -r config/requirements-dev.txt")
    print("   black . && isort .  # Format code")
    print("   pytest              # Run tests")

    print("\n🎮 Access the web interface at: http://localhost:7681")
    print("🤖 Learning Companion API at: http://localhost:7681/learning/")

    print("\n✨ Atmosphere is ready for emotionally-adaptive learning!")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
