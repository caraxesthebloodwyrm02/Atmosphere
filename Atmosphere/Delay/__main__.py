#!/usr/bin/env python3
"""
Delay Module Main Entry Point
Run with: python -m Delay
"""

import sys
import getpass
from . import __version__
from .src.security import user_manager, security_logger

def authenticate_user():
    """Authenticate user before allowing access to Delay interface"""
    print("🔐 Delay Module Access Control")
    print("=" * 35)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")

            user = user_manager.authenticate_user(username, password)
            if user and user.role in ["admin", "researcher", "developer"]:
                security_logger.info(f"Delay interface access granted to {username}")
                return user
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f"Authentication failed or insufficient permissions. {remaining} attempts remaining.")
                else:
                    print("Authentication failed. Access denied.")
                    security_logger.warning(f"Failed authentication attempts for Delay interface")
                    sys.exit(1)
        except KeyboardInterrupt:
            print("\nAuthentication cancelled.")
            sys.exit(1)

def main():
    """Main entry point for Delay module."""
    print("⏰ Delay v{}".format(__version__))
    print("=" * 30)
    print("Time-based audio processing")
    print("")
    print("Usage:")
    print("  python -m Delay.core")
    print("  python -m Delay.api")

if __name__ == "__main__":
    # Require authentication before accessing Delay interface
    user = authenticate_user()
    print(f"\nWelcome, {user.full_name} ({user.role})!")
    main()
