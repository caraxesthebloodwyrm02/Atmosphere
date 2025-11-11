#!/usr/bin/env python3
"""
Secure Environment Variable Manager for Atmosphere Arcade
=========================================================

Ensures all API keys and sensitive configuration are retrieved
safely from environment variables with no user prompts.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Optional, List
import argparse

class SecureEnvManager:
    """Secure environment variable management for Atmosphere Arcade."""

    def __init__(self):
        self.required_keys = {
            'OPENAI_API_KEY': {
                'description': 'OpenAI GPT-4 API Key (Required)',
                'required': True,
                'validation': self._validate_openai_key
            }
        }

        self.optional_keys = {
            'ANTHROPIC_API_KEY': {
                'description': 'Anthropic Claude API Key (Optional)',
                'required': False,
                'validation': self._validate_generic_key
            },
            'GOOGLE_API_KEY': {
                'description': 'Google AI API Key (Optional)',
                'required': False,
                'validation': self._validate_generic_key
            },
            'HUGGINGFACE_API_KEY': {
                'description': 'Hugging Face API Key (Optional)',
                'required': False,
                'validation': self._validate_generic_key
            },
            'REPLICATE_API_KEY': {
                'description': 'Replicate API Key (Optional)',
                'required': False,
                'validation': self._validate_generic_key
            }
        }

    def _validate_openai_key(self, key: str) -> bool:
        """Validate OpenAI API key format."""
        if not key or len(key.strip()) < 20:
            return False
        # OpenAI keys start with 'sk-'
        return key.strip().startswith('sk-')

    def _validate_generic_key(self, key: str) -> bool:
        """Validate generic API key format."""
        if not key or len(key.strip()) < 10:
            return False
        # Generic validation - not empty and reasonable length
        return len(key.strip()) >= 10

    def check_environment(self) -> Dict[str, Dict]:
        """Check all environment variables and return status."""
        results = {}

        # Check required keys
        for key, config in self.required_keys.items():
            value = os.getenv(key)
            is_set = bool(value and value.strip())
            is_valid = is_set and config['validation'](value)

            results[key] = {
                'description': config['description'],
                'required': config['required'],
                'is_set': is_set,
                'is_valid': is_valid,
                'value_preview': self._get_value_preview(value) if is_set else None
            }

        # Check optional keys
        for key, config in self.optional_keys.items():
            value = os.getenv(key)
            is_set = bool(value and value.strip())
            is_valid = not is_set or config['validation'](value)  # Optional, so valid if not set

            results[key] = {
                'description': config['description'],
                'required': config['required'],
                'is_set': is_set,
                'is_valid': is_valid,
                'value_preview': self._get_value_preview(value) if is_set else None
            }

        return results

    def _get_value_preview(self, value: str) -> str:
        """Get a safe preview of the API key value."""
        if not value:
            return None
        # Show first 8 and last 4 characters
        val = value.strip()
        if len(val) <= 12:
            return "****"
        return f"{val[:8]}****{val[-4:]}"

    def display_status(self):
        """Display current environment variable status."""
        print("🔐 Atmosphere Arcade - Secure Environment Check")
        print("=" * 55)

        results = self.check_environment()

        required_ok = True
        optional_count = 0

        for key, status in results.items():
            icon = "✅" if status['is_valid'] else "❌" if status['required'] else "⚠️"
            required_text = "(Required)" if status['required'] else "(Optional)"

            print(f"{icon} {key} {required_text}")
            print(f"   {status['description']}")

            if status['is_set'] and status['value_preview']:
                print(f"   Preview: {status['value_preview']}")
            elif status['required'] and not status['is_set']:
                print("   Status: ❌ Not configured")
            elif not status['required'] and not status['is_set']:
                print("   Status: ⏭️  Not configured (optional)")
            else:
                print(f"   Status: {'✅ Valid' if status['is_valid'] else '❌ Invalid'}")

            if status['required'] and not status['is_valid']:
                required_ok = False
            if not status['required'] and status['is_set'] and status['is_valid']:
                optional_count += 1

            print()

        # Summary
        if required_ok:
            print("🎉 All required API keys are properly configured!")
            if optional_count > 0:
                print(f"📊 {optional_count} optional service(s) also configured.")
        else:
            print("❌ Some required API keys are missing or invalid.")
            print("\n🔧 To configure API keys:")
            print("   Windows PowerShell:")
            print("   $env:OPENAI_API_KEY = 'your_key_here'")
            print("   ")
            print("   Windows Command Prompt:")
            print("   set OPENAI_API_KEY=your_key_here")
            print("   ")
            print("   Linux/Mac:")
            print("   export OPENAI_API_KEY=your_key_here")
            print("\n   Then restart the application.")

    def validate_all_keys(self) -> bool:
        """Validate that all required keys are properly configured."""
        results = self.check_environment()

        for key, status in results.items():
            if status['required'] and not status['is_valid']:
                return False

        return True

    def get_missing_keys(self) -> List[str]:
        """Get list of missing or invalid required keys."""
        results = self.check_environment()
        missing = []

        for key, status in results.items():
            if status['required'] and not status['is_valid']:
                missing.append(key)

        return missing

    def create_env_template(self, output_file: str = ".env.template"):
        """Create a secure environment template file."""
        template_content = """# Atmosphere Arcade - Secure Environment Configuration
# ===================================================
#
# IMPORTANT SECURITY NOTICE:
# - Never commit API keys to version control
# - Use environment variables for production deployment
# - This file is a template - copy to .env and configure
#
# Required API Keys (configure these):
"""

        # Add required keys
        for key, config in self.required_keys.items():
            template_content += f"""
# {config['description']}
# Get your key from: https://platform.openai.com/api-keys
{key}=your_api_key_here
"""

        template_content += """
# Optional API Keys (uncomment and configure if needed):
"""

        # Add optional keys
        for key, config in self.optional_keys.items():
            template_content += f"""
# {config['description']}
# {key}=your_api_key_here
"""

        template_content += """
# Application Configuration
ARCADE_HOST=localhost
ARCADE_PORT=7681
ARCADE_DEBUG=false

# Security Settings
ARCADE_SECRET_KEY=generate_a_random_secret_key_here
SANDBOX_ENABLED=true
COMMAND_TIMEOUT=30

# Monitoring (optional)
ARCADE_ENABLE_METRICS=false
PROMETHEUS_PORT=9090
"""

        Path(output_file).write_text(template_content)
        print(f"✅ Environment template created: {output_file}")
        print("   Copy this to .env and configure your API keys.")

    def secure_startup_check(self) -> bool:
        """Perform secure startup validation."""
        print("🔐 Performing secure startup validation...")

        if not self.validate_all_keys():
            missing = self.get_missing_keys()
            print(f"❌ Missing or invalid required API keys: {', '.join(missing)}")

            print("\n🔧 Secure Configuration Instructions:")
            print("1. Set environment variables (recommended for security):")
            print("   Windows: $env:OPENAI_API_KEY = 'your_key'")
            print("   Linux/Mac: export OPENAI_API_KEY=your_key")
            print("")
            print("2. Or create a .env file (less secure for production):")
            print("   cp .env.template .env")
            print("   # Edit .env with your API keys")
            print("")
            print("3. Never commit API keys to version control!")

            return False

        print("✅ All security checks passed!")
        return True


def main():
    """Main entry point for secure environment management."""
    parser = argparse.ArgumentParser(description="Secure Environment Manager for Atmosphere Arcade")
    parser.add_argument("command", nargs="?", default="check",
                       choices=["check", "template", "validate", "help"])
    parser.add_argument("--output", default=".env.template",
                       help="Output file for template command")

    args = parser.parse_args()

    manager = SecureEnvManager()

    if args.command == "check":
        manager.display_status()
    elif args.command == "template":
        manager.create_env_template(args.output)
    elif args.command == "validate":
        if manager.validate_all_keys():
            print("✅ All API keys are valid!")
            sys.exit(0)
        else:
            print("❌ API key validation failed!")
            sys.exit(1)
    elif args.command == "help":
        print("Secure Environment Manager Commands:")
        print("  check    - Check current API key configuration")
        print("  template - Create environment template file")
        print("  validate - Validate API keys (returns exit code)")
        print("  help     - Show this help")


if __name__ == "__main__":
    main()
