#!/usr/bin/env python3
"""
Atmosphere Project Main Entry Point
Run with: python -m atmosphere
"""

import sys
import getpass
from . import main
from .src.security import user_manager, security_logger

def authenticate_user():
    """Authenticate user before allowing access to main interface"""
    print("🔐 Atmosphere Platform Access Control")
    print("=" * 40)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")

            user = user_manager.authenticate_user(username, password)
            if user:
                security_logger.info(f"Main interface access granted to {username}")
                return user
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f"Authentication failed. {remaining} attempts remaining.")
                else:
                    print("Authentication failed. Access denied.")
                    security_logger.warning(f"Failed authentication attempts for main interface")
                    sys.exit(1)
        except KeyboardInterrupt:
            print("\nAuthentication cancelled.")
            sys.exit(1)

if __name__ == "__main__":
    # Require authentication before accessing main interface
    user = authenticate_user()
    print(f"\nWelcome, {user.full_name} ({user.role})!")
    main()
