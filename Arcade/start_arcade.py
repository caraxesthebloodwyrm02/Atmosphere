#!/usr/bin/env python3
"""
Atmosphere Arcade Launcher
========================

Advanced AI terminal with safety features, multilingual support, and enterprise capabilities.
Supports both terminal and web-based ChatKit interfaces.
"""

import os
import sys
import asyncio
import argparse
from pathlib import Path
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from api.enhanced_server_test import interactive_terminal
    # from api.chatgpt_manager import ChatGPTManager  # Lazy import later
    from secure_env_manager import SecureEnvManager
    from safety_monitor import safety_monitor
    from safety_api import create_safety_api
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the correct directory.")
    sys.exit(1)


class ArcadeQuickStart:
    """Quick start manager for Atmosphere Arcade."""

    def __init__(self):
        self.project_root = Path(__file__).parent
        self.config_dir = self.project_root / "config"
        self.logs_dir = self.project_root / "logs"

    def check_environment(self) -> bool:
        """Check if the environment is properly configured with secure validation."""
        env_manager = SecureEnvManager()

        # Perform secure validation
        if not env_manager.secure_startup_check():
            return False

        # Additional ChatGPT Manager check
        try:
            from api.chatgpt_manager import ChatGPTManager
            chatgpt = ChatGPTManager()
            print("✅ ChatGPT Manager ready for multilingual support")
        except Exception as e:
            print(f"⚠️ ChatGPT Manager limited: {e}")

        # Create necessary directories
        self.config_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)

        print("✅ Environment validation complete!")
        return True

    def show_welcome(self):
        """Show welcome message and feature overview."""
        print("""
🎮 🌟 ATMOSPHERE ARCADE - ENHANCED TERMINAL 🌟 🎮
═══════════════════════════════════════════════════════════

✨ FULLY INTEGRATED AI-POWERED TERMINAL ✨

🌐 MULTILINGUAL SUPPORT
   • Input commands in ANY language!
   • "kire? ki koros?" (Bengali) → "hey! what's up?"
   • "Muéstrame los archivos" (Spanish) → Shows files
   • "Zeige mir die Dateien" (German) → Shows files

🤖 NATURAL CONVERSATION
   • No "ai ask" prefixes needed!
   • Pure natural language processing
   • Friendly, human-like responses
   • Context-aware conversations

💾 REAL FILE ACCESS
   • Actually read/write real files
   • Safe directory navigation
   • Secure sandboxed operations

🛡️ SAFETY & SECURITY
   • Comprehensive content moderation
   • Input validation and filtering
   • User reporting system
   • Human oversight capabilities
   • Adversarial testing support

🚨 REPORTING ISSUES
   • Use 'report safety' command for safety concerns
   • Use 'report bug' command for technical issues
   • Use 'report inappropriate' command for content issues

═══════════════════════════════════════════════════════════
""")

    def show_help(self):
        """Show help information."""
        print("""
🎯 QUICK START COMMANDS:

  python start_arcade.py                # Basic terminal mode
  python start_arcade.py --chatkit     # ChatKit web interface (recommended)
  python start_arcade.py --terminal    # Web-based terminal interface
  python start_arcade.py --web         # Web interface mode (future)
  python start_arcade.py --check       # Environment check only
  python start_arcade.py --safety-api  # Start safety monitoring API

🔐 SECURE API KEY SETUP:

  # Check current configuration
  python secure_env_manager.py check

  # Create environment template
  python secure_env_manager.py template

  # Validate API keys
  python secure_env_manager.py validate

🌟 FEATURES:

  💬 Natural Language:
    "What can you do?"          → AI explains capabilities
    "Show me the files"         → Lists directory contents
    "Create a file called test.txt" → Creates actual file

  🌐 Multilingual:
    "किरे? की करोस?"            → Bengali → "Hey! What's up?"
    "¿Qué hay en esta carpeta?" → Spanish → Shows files
    "Qu'est-ce que tu peux faire?" → French → Explains features

  💾 File Operations:
    "Go to desktop"             → Navigates to Desktop
    "Read README.md"            → Shows file contents
    "Where am I?"               → Shows current directory

  🎮 Terminal Commands:
    help                        → Show available commands
    exit                        → Quit the terminal

  🛡️ Safety Commands:
    report safety <message>     → Report safety concerns
    report bug <message>        → Report technical bugs
    report inappropriate <msg>  → Report inappropriate content
    safety status               → Show safety system status
    safety help                 → Show safety guidelines

═══════════════════════════════════════════════════════════
""")

    async def run_terminal(self):
        """Run the interactive terminal."""
        print("\n🚀 Starting Atmosphere Arcade Terminal...")
        print("💡 Type 'help' for commands or just chat naturally!")
        print("🌐 Try commands in any language!\n")

        try:
            await interactive_terminal()
        except KeyboardInterrupt:
            print("\n👋 Thanks for using Atmosphere Arcade!")
        except Exception as e:
            print(f"\n❌ Terminal error: {e}")
            print("💡 Try running with --check to diagnose issues")

    def run_web_interface(self):
        """Run the web interface (placeholder for future implementation)."""
        print("🌐 Web interface not yet implemented in this version")
        print("💡 Use terminal mode: python start_arcade.py")
        print("\n📋 To implement web interface:")
        print("   1. Install FastAPI: pip install fastapi uvicorn")
        print("   2. Run: python start_arcade.py --web")


def main():
    parser = argparse.ArgumentParser(description="Atmosphere Arcade - Enhanced AI Terminal")
    parser.add_argument('--web', action='store_true', help='Start web interface (future feature)')
    parser.add_argument('--check', action='store_true', help='Check environment and exit')
    parser.add_argument('--safety-api', action='store_true', help='Start safety monitoring API server')
    parser.add_argument('--chatkit', action='store_true', help='Start ChatKit web interface server')
    parser.add_argument('--terminal', action='store_true', help='Start web-based terminal interface server')

    args = parser.parse_args()

    arcade = ArcadeQuickStart()

    # Show welcome message
    arcade.show_welcome()

    # Check environment
    if not arcade.check_environment():
        print("\n❌ Environment check failed. Please fix issues above.")
        return

    # Environment check only
    if args.check:
        print("\n✅ All checks passed! Ready to launch Arcade.")
        return

    # Safety API server
    if args.safety_api:
        try:
            safety_api = create_safety_api()
            print("\n🛡️ Starting Safety API Server...")
            safety_api.run(host='0.0.0.0', port=8080, debug=False)
        except Exception as e:
            print(f"❌ Failed to start safety API: {e}")
        return

    # ChatKit web interface server
    if args.chatkit:
        try:
            print("\n🤖 Starting ChatKit Web Interface Server...")

            # Make port configurable
            chatkit_port = os.getenv('CHATKIT_PORT', '8081')

            print(f"🌐 Port: {chatkit_port}")
            print(f"🌐 Access at: http://localhost:{chatkit_port}")
            print("🛡️ Safety features: Active | Multilingual: Enabled | Enterprise: Ready")

            # Import and run ChatKit server
            from chatkit_server import app
            import uvicorn

            # Set environment variable for the server
            os.environ['CHATKIT_PORT'] = chatkit_port

            uvicorn.run(app, host='0.0.0.0', port=int(chatkit_port), log_level="info")

        except Exception as e:
            error_msg = str(e)
            if "10048" in error_msg or "address already in use" in error_msg.lower():
                print(f"❌ Port {os.getenv('CHATKIT_PORT', '8081')} is already in use!")
                print("💡 Solutions:")
                print("   1. Kill existing process: taskkill /PID <PID> /F")
                print("   2. Use different port: CHATKIT_PORT=8082 python start_arcade.py --chatkit")
                print("   3. Find process using port: netstat -ano | findstr :8081")
            else:
                print(f"❌ Failed to start ChatKit server: {e}")
                print("💡 Make sure you have installed the required dependencies:")
                print("   pip install openai-chatkit (optional)")
        return

    # Web-based terminal server
    if args.terminal:
        try:
            print("\n🖥️ Starting Web-Based Terminal Server...")

            # Make port configurable
            terminal_port = os.getenv('TERMINAL_PORT', '8083')

            print(f"🌐 Port: {terminal_port}")
            print(f"🌐 Access at: http://localhost:{terminal_port}/terminal")
            print("⚡ Features: Real-time execution | Command history | Auto-completion")

            # Import and run terminal server
            from chatkit_server import app
            import uvicorn

            # Set environment variable for the server
            os.environ['TERMINAL_PORT'] = terminal_port

            uvicorn.run(app, host='0.0.0.0', port=int(terminal_port), log_level="info")

        except Exception as e:
            error_msg = str(e)
            if "10048" in error_msg or "address already in use" in error_msg.lower():
                print(f"❌ Port {os.getenv('TERMINAL_PORT', '8083')} is already in use!")
                print("💡 Solutions:")
                print("   1. Kill existing process: taskkill /PID <PID> /F")
                print("   2. Use different port: TERMINAL_PORT=8084 python start_arcade.py --terminal")
                print("   3. Find process using port: netstat -ano | findstr :8083")
            else:
                print(f"❌ Failed to start terminal server: {e}")
        return

    # Run terminal
    asyncio.run(arcade.run_terminal())


if __name__ == "__main__":
    main()
