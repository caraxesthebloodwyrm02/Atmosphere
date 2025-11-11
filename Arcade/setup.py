#!/usr/bin/env python3
"""
Atmosphere Arcade - Complete Setup and Installation Script
==========================================================

This script handles the complete setup, configuration, and deployment
of Atmosphere Arcade including dependencies, environment setup, and
initial configuration.
"""

import os
import sys
import platform
import subprocess
import argparse
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import json

class ArcadeSetup:
    """Complete setup manager for Atmosphere Arcade."""

    def __init__(self, install_dir: Optional[Path] = None, args=None):
        self.system = platform.system().lower()
        self.project_root = Path(__file__).parent.absolute()
        self.args = args

        if install_dir:
            self.install_dir = Path(install_dir).absolute()
        else:
            if self.system == "windows":
                self.install_dir = Path(os.environ.get('PROGRAMFILES', 'C:\\Program Files')) / 'AtmosphereArcade'
            else:
                self.install_dir = Path('/opt/atmosphere-arcade')

        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load setup configuration."""
        return {
            'app_name': 'atmosphere-arcade',
            'version': '2.0.0',
            'python_version': '3.8',
            'port': 7681,
            'host': 'localhost',
            'required_packages': [
                'fastapi', 'uvicorn', 'websockets', 'openai', 'python-dotenv',
                'pydantic', 'pyyaml', 'rich', 'click', 'textual', 'watchdog', 'psutil'
            ],
            'dev_packages': [
                'pytest', 'pytest-asyncio', 'pytest-cov', 'pytest-mock', 'pytest-xdist',
                'coverage', 'faker', 'httpx', 'black', 'isort', 'flake8', 'mypy'
            ]
        }

    def check_prerequisites(self) -> bool:
        """Check system prerequisites."""
        print("🔍 Checking system prerequisites...")

        # Check Python version
        python_version = sys.version_info
        if python_version < (3, 8):
            print(f"❌ Python {self.config['python_version']}+ required, found {python_version.major}.{python_version.minor}")
            return False
        print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")

        # Check if we're in the right directory
        if not (self.project_root / 'start_arcade.py').exists():
            print("❌ Not running from Atmosphere Arcade directory")
            return False
        print("✅ Correct project directory")

        return True

    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        print("📦 Installing Python dependencies...")

        try:
            # Upgrade pip
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Install core packages
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + self.config['required_packages'],
                                stdout=subprocess.DEVNULL)

            print("✅ Core dependencies installed")

            # Check for dev setup preference from environment or args
            install_dev = ((self.args and self.args.dev) or
                          os.getenv('ARCADE_DEV_SETUP', '').lower() in ('true', '1', 'yes'))

            if install_dev:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + self.config['dev_packages'],
                                    stdout=subprocess.DEVNULL)
                print("✅ Development dependencies installed")
            elif os.getenv('ARCADE_INTERACTIVE', '').lower() in ('true', '1', 'yes'):
                # Only prompt if explicitly requested
                if input("Install development dependencies? (y/N): ").lower().startswith('y'):
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + self.config['dev_packages'],
                                        stdout=subprocess.DEVNULL)
                    print("✅ Development dependencies installed")

            return True

        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False

    def setup_environment(self) -> bool:
        """Setup environment configuration."""
        print("🔧 Setting up environment configuration...")

        env_file = self.project_root / '.env'
        env_example = self.project_root / '.env.example'

        # Check if API key is already set in environment variables
        existing_api_key = os.getenv('OPENAI_API_KEY')

        if env_file.exists():
            # Check if we should overwrite from environment or args
            should_overwrite = (os.getenv('ARCADE_OVERWRITE_ENV', '').lower() in ('true', '1', 'yes'))

            if not should_overwrite:
                print("⏭️  Skipping environment setup (file exists)")
                return True

        # Copy example file
        if env_example.exists():
            shutil.copy2(env_example, env_file)
            print("✅ Environment file created from template")
        else:
            # Create basic env file
            env_content = f"""# Atmosphere Arcade Configuration
OPENAI_API_KEY=your_openai_api_key_here
ARCADE_HOST={self.config['host']}
ARCADE_PORT={self.config['port']}
ARCADE_DEBUG=false
"""
            env_file.write_text(env_content)
            print("✅ Basic environment file created")

        # Handle API key configuration
        if existing_api_key:
            # Use existing environment variable
            self._update_env_file(env_file, 'OPENAI_API_KEY', existing_api_key)
            print("✅ API key configured from environment variable")
        else:
            print("⚠️  OPENAI_API_KEY not found in environment variables")
            print("   Please set it using:")
            print("   Windows: set OPENAI_API_KEY=your_key_here")
            print("   Linux/Mac: export OPENAI_API_KEY=your_key_here")
            print("   Or edit the .env file directly")
            print("   Then run the application with: python start_arcade.py")

        return True

    def _update_env_file(self, env_file: Path, key: str, value: str):
        """Update environment file with new value."""
        content = env_file.read_text()
        lines = content.split('\n')
        updated = False

        for i, line in enumerate(lines):
            if line.startswith(f'{key}='):
                lines[i] = f'{key}={value}'
                updated = True
                break

        if not updated:
            lines.append(f'{key}={value}')

        env_file.write_text('\n'.join(lines))

    def create_directories(self) -> bool:
        """Create necessary directories."""
        print("📁 Creating application directories...")

        directories = [
            self.project_root / 'logs',
            self.project_root / 'data',
            self.project_root / 'sandbox',
            self.project_root / 'config'
        ]

        for directory in directories:
            directory.mkdir(exist_ok=True)
            print(f"✅ Created {directory.name}/")

        return True

    def run_tests(self) -> bool:
        """Run test suite."""
        print("🧪 Running test suite...")

        try:
            result = subprocess.run([sys.executable, '-m', 'pytest', 'tests/', '-v', '--tb=short'],
                                  capture_output=True, text=True, cwd=self.project_root)

            if result.returncode == 0:
                print("✅ All tests passed")
                return True
            else:
                print("❌ Some tests failed")
                print(result.stdout)
                print(result.stderr)
                return False

        except FileNotFoundError:
            print("⚠️  pytest not installed, skipping tests")
            return True

    def check_installation(self) -> bool:
        """Perform final installation checks."""
        print("🔍 Performing installation checks...")

        checks = [
            ("start_arcade.py", "Main startup script"),
            ("api/chatgpt_manager.py", "ChatGPT manager"),
            ("api/enhanced_server_test.py", "Enhanced server"),
            ("requirements.txt", "Dependencies file"),
            (".env", "Environment configuration")
        ]

        for file_path, description in checks:
            if (self.project_root / file_path).exists():
                print(f"✅ {description}")
            else:
                print(f"❌ Missing {description}: {file_path}")
                return False

        # Test basic import
        try:
            sys.path.insert(0, str(self.project_root))
            from start_arcade import ArcadeQuickStart
            print("✅ Core modules import successfully")
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False

        return True

    def create_shortcuts(self) -> bool:
        """Create desktop shortcuts and start menu entries."""
        if self.system == "windows":
            return self._create_windows_shortcuts()
        elif self.system == "linux":
            return self._create_linux_shortcuts()
        else:
            print("⏭️  Shortcut creation not supported on this platform")
            return True

    def _create_windows_shortcuts(self) -> bool:
        """Create Windows shortcuts."""
        try:
            import winshell
            from win32com.client import Dispatch

            desktop = winshell.desktop()
            start_menu = winshell.start_menu()

            # Create desktop shortcut
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(str(desktop / 'Atmosphere Arcade.lnk'))
            shortcut.Targetpath = str(self.project_root / 'start_arcade.py')
            shortcut.WorkingDirectory = str(self.project_root)
            shortcut.IconLocation = str(self.project_root / 'icon.ico') if (self.project_root / 'icon.ico').exists() else ''
            shortcut.save()

            print("✅ Windows shortcuts created")
            return True

        except ImportError:
            print("⏭️  Windows shortcut creation requires pywin32")
            return True

    def _create_linux_shortcuts(self) -> bool:
        """Create Linux desktop entry."""
        desktop_file = Path.home() / '.local/share/applications/atmosphere-arcade.desktop'

        desktop_content = f"""[Desktop Entry]
Name=Atmosphere Arcade
Comment=Enhanced AI Terminal
Exec=python3 {self.project_root}/start_arcade.py
Icon={self.project_root}/icon.png
Terminal=false
Type=Application
Categories=Development;Utility;
"""

        try:
            desktop_file.write_text(desktop_content)
            desktop_file.chmod(0o755)
            print("✅ Linux desktop entry created")
            return True
        except Exception as e:
            print(f"⚠️  Failed to create desktop entry: {e}")
            return True

    def show_completion_message(self):
        """Show completion message with next steps."""
        print("""
🎉 ATMOSPHERE ARCADE SETUP COMPLETED SUCCESSFULLY! 🎉
═══════════════════════════════════════════════════════

Your multilingual AI terminal is now ready!

🚀 QUICK START:
   python start_arcade.py

🌐 WEB INTERFACE:
   Visit: http://localhost:7681

📚 DOCUMENTATION:
   README.md - Complete user guide
   API_REFERENCE.md - API documentation

🧪 RUN TESTS:
   python -m pytest tests/

🔧 CONFIGURATION:
   Edit .env file for API keys and settings

🌟 FEATURES READY:
   • Natural language processing
   • 20+ languages supported
   • Real file operations
   • AI-powered assistance
   • Secure sandboxing

📞 SUPPORT:
   Check logs/ directory for troubleshooting
   Run: python start_arcade.py --help

🎯 HAPPY CODING WITH ATMOSPHERE ARCADE!
""")


def main():
    parser = argparse.ArgumentParser(description='Atmosphere Arcade Setup')
    parser.add_argument('--install-dir', help='Custom installation directory')
    parser.add_argument('--skip-tests', action='store_true', help='Skip running tests')
    parser.add_argument('--dev', action='store_true', help='Development setup (includes dev dependencies)')

    args = parser.parse_args()

    setup = ArcadeSetup(install_dir=args.install_dir if args.install_dir else None, args=args)

    print("🚀 Atmosphere Arcade - Complete Setup")
    print("=" * 50)

    steps = [
        ("Prerequisites", setup.check_prerequisites),
        ("Dependencies", setup.install_dependencies),
        ("Environment", setup.setup_environment),
        ("Directories", setup.create_directories),
        ("Shortcuts", setup.create_shortcuts),
    ]

    if not args.skip_tests:
        steps.insert(-1, ("Tests", setup.run_tests))

    steps.append(("Verification", setup.check_installation))

    success = True
    for step_name, step_func in steps:
        print(f"\n🔧 {step_name}...")
        if not step_func():
            success = False
            break

    if success:
        setup.show_completion_message()
        return 0
    else:
        print("\n❌ Setup failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
