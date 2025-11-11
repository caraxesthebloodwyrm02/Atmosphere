#!/usr/bin/env python3
"""
API Key Management Utility for Enhanced Arcade Terminal
======================================================

Securely manage API keys for external services used by the AI assistant.
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional
import argparse

class APIKeyManager:
    """Secure API key management."""

    def __init__(self):
        self.env_file = Path(".env")
        self.key_file = Path(".api_keys.enc")  # Encrypted storage (future enhancement)
        self.services = {
            'openai': {
                'name': 'OpenAI',
                'url': 'https://platform.openai.com/api-keys',
                'required': True,
                'description': 'Primary AI assistant and intelligent features'
            },
            'anthropic': {
                'name': 'Anthropic',
                'url': 'https://console.anthropic.com/',
                'required': False,
                'description': 'Alternative AI provider (Claude)'
            },
            'google': {
                'name': 'Google AI',
                'url': 'https://makersuite.google.com/app/apikey',
                'required': False,
                'description': 'Google Gemini models'
            },
            'huggingface': {
                'name': 'Hugging Face',
                'url': 'https://huggingface.co/settings/tokens',
                'required': False,
                'description': 'Open-source AI models'
            },
            'replicate': {
                'name': 'Replicate',
                'url': 'https://replicate.com/account/api-tokens',
                'required': False,
                'description': 'Model deployment and inference'
            }
        }

    def setup_env_file(self):
        """Create or update the .env file."""
        if not self.env_file.exists():
            print("📝 Creating .env file...")
            example_file = Path(".env.example")
            if example_file.exists():
                content = example_file.read_text()
            else:
                content = self._generate_default_env()

            self.env_file.write_text(content)
            print("✅ .env file created. Please edit it with your API keys.")
        else:
            print("✅ .env file already exists.")

    def _generate_default_env(self) -> str:
        """Generate default .env content."""
        content = "# Enhanced Arcade Terminal Environment Configuration\n"
        content += "# =================================================\n\n"

        for service_key, service_info in self.services.items():
            env_key = f"{service_key.upper()}_API_KEY"
            content += f"# {service_info['name']} API Key ({service_info['description']})\n"
            content += f"# Get your key from: {service_info['url']}\n"
            content += f"{env_key}=your_{service_key}_api_key_here\n\n"

        content += "# Arcade Terminal Configuration\n"
        content += "ARCADE_PORT=7681\n"
        content += "ARCADE_HOST=0.0.0.0\n"
        content += "ARCADE_DEBUG=true\n\n"

        content += "# Learning Companion Configuration\n"
        content += "LEARNING_API_ENABLED=true\n"
        content += "EMOTIONAL_ADAPTATION_ENABLED=true\n\n"

        content += "# Security Configuration\n"
        content += "SANDBOX_ENABLED=true\n"
        content += "COMMAND_TIMEOUT=30\n"
        content += "MAX_SESSIONS=100\n"

        return content

    def setup_from_environment(self):
        """Setup API keys from environment variables."""
        print("🔧 Setting up API keys from environment variables...")
        print("=" * 50)

        # Setup .env file
        self.setup_env_file()

        # Check and configure keys from environment
        updated_keys = []

        for service_key, service_info in self.services.items():
            env_key = f"{service_key.upper()}_API_KEY"

            # Check if key is set in environment
            env_value = os.getenv(env_key)
            if env_value and not env_value.startswith("your_") and env_value.strip():
                # Update .env file with environment value
                self.set_env_key(env_key, env_value)
                updated_keys.append(service_info['name'])
                print(f"✅ {service_info['name']}: Configured from environment")
            else:
                print(f"⚠️  {service_info['name']}: Not found in environment variables")

        if updated_keys:
            print(f"\n✅ Successfully configured: {', '.join(updated_keys)}")
        else:
            print("\n⚠️  No API keys found in environment variables.")
            print("   Please set them using:")
            print("   Windows: set OPENAI_API_KEY=your_key_here")
            print("   Linux/Mac: export OPENAI_API_KEY=your_key_here")

        print("\n🔄 Restart any running services to apply changes.")

    def set_env_key(self, key: str, value: str):
        """Set an environment variable in the .env file."""
        if not self.env_file.exists():
            self.setup_env_file()

        content = self.env_file.read_text()
        lines = content.split('\n')

        # Find and update the key
        updated = False
        for i, line in enumerate(lines):
            if line.startswith(f"{key}="):
                lines[i] = f"{key}={value}"
                updated = True
                break

        if not updated:
            # Add the key if it doesn't exist
            lines.append(f"{key}={value}")

        # Write back to file
        self.env_file.write_text('\n'.join(lines))

    def validate_keys(self) -> Dict[str, bool]:
        """Validate that API keys are properly configured."""
        results = {}

        for service_key in self.services:
            env_key = f"{service_key.upper()}_API_KEY"
            value = os.getenv(env_key, "")

            # Check if key exists and is not placeholder
            is_valid = value and not value.startswith("your_") and value != ""
            results[service_key] = is_valid

        return results

    def show_status(self):
        """Show current API key configuration status."""
        print("🔍 API Key Configuration Status")
        print("=" * 35)

        validation = self.validate_keys()
        all_configured = True

        for service_key, service_info in self.services.items():
            status = "✅" if validation[service_key] else "❌"
            required = "(Required)" if service_info['required'] else "(Optional)"

            print(f"{status} {service_info['name']} {required}")
            if not validation[service_key]:
                all_configured = False

        print()
        if all_configured:
            print("🎉 All required services are configured!")
        else:
            print("⚠️  Some services are not configured.")
            print("   Run 'python api_key_manager.py setup' to configure.")

    def test_keys(self):
        """Test API key functionality."""
        print("🧪 Testing API Key Functionality")
        print("=" * 35)

        try:
            import openai
            if os.getenv('OPENAI_API_KEY'):
                try:
                    client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
                    # Simple test request
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[{"role": "user", "content": "Hello"}],
                        max_tokens=10
                    )
                    print("✅ OpenAI: Working")
                except Exception as e:
                    print(f"❌ OpenAI: Failed ({str(e)})")
            else:
                print("❌ OpenAI: No API key configured")

        except ImportError:
            print("⚠️  OpenAI library not installed")

        # Add more service tests here as needed

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="API Key Manager for Enhanced Arcade Terminal")
    parser.add_argument("command", nargs="?", default="status",
                       choices=["setup", "status", "test", "help"])
    parser.add_argument("--env-file", default=".env", help="Environment file path")

    args = parser.parse_args()

    manager = APIKeyManager()

    if args.command == "setup":
        manager.setup_from_environment()
    elif args.command == "status":
        manager.show_status()
    elif args.command == "test":
        manager.test_keys()
    elif args.command == "help":
        print("API Key Manager Commands:")
        print("  setup  - Configure API keys from environment variables")
        print("  status - Show configuration status")
        print("  test   - Test API key functionality")
        print("  help   - Show this help")

if __name__ == "__main__":
    main()
