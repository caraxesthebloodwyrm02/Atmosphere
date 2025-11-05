#!/usr/bin/env python3
"""
Routing API Connector Main Entry Point
Run with: python -m Routing.api_connector
"""

import sys
import os
import getpass
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import security module
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from src.security import user_manager, security_logger

from api_connector_main import demo

def authenticate_user():
    """Authenticate user before allowing access to Routing API connector"""
    print("🔐 Routing API Connector Access Control")
    print("=" * 42)

    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            username = input("Username: ").strip()
            password = getpass.getpass("Password: ")

            user = user_manager.authenticate_user(username, password)
            if user and user.role in ["admin", "researcher"]:
                security_logger.info(f"Routing API connector access granted to {username}")
                return user
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    print(f"Authentication failed or insufficient permissions. {remaining} attempts remaining.")
                else:
                    print("Authentication failed. Access denied.")
                    security_logger.warning(f"Failed authentication attempts for Routing API connector")
                    sys.exit(1)
        except KeyboardInterrupt:
            print("\nAuthentication cancelled.")
            sys.exit(1)

if __name__ == "__main__":
    # Require authentication before accessing Routing API connector
    user = authenticate_user()
    print(f"\nWelcome, {user.full_name} ({user.role})!")
    print("🔌 Initializing Routing API Connector with OpenAI integration...")
    import asyncio
    asyncio.run(demo())
