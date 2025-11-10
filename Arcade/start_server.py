#!/usr/bin/env python3
"""
Start Arcade Terminal Server
Quick start script for the Arcade terminal web interface.
"""

import sys
import logging
from pathlib import Path

# Add Arcade to path
arcade_root = Path(__file__).parent
sys.path.insert(0, str(arcade_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

if __name__ == "__main__":
    try:
        import uvicorn
        from api.server import app
        
        print("🎮 Starting Arcade Terminal Server...")
        print("📍 Server will be available at: http://localhost:7681")
        print("🔒 Security: Sandbox mode enabled")
        print("⚡ Press Ctrl+C to stop\n")
        
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=7681,
            log_level="info",
            reload=False
        )
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)

