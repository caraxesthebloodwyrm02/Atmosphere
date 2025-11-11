#!/usr/bin/env python3
"""
Enhanced Arcade Terminal Launcher
================================

Interactive launcher for the Enhanced Arcade Terminal with AI capabilities.
"""

import argparse
import sys
import os
from pathlib import Path

def check_environment():
    """Check if required environment is set up."""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found!")
        print("📝 Copy .env.example to .env and add your API keys for full functionality.")
        print("🔗 Get API keys from:")
        print("   • OpenAI: https://platform.openai.com/api-keys")
        print("   • Anthropic: https://console.anthropic.com/")
        print("   • Google: https://makersuite.google.com/app/apikey")
        return False
    return True

def launch_server(port: int = 7681, host: str = "0.0.0.0", reload: bool = True):
    """Launch the enhanced server."""
    print("🚀 Launching Enhanced Arcade Terminal...")
    print(f"🌐 Server will be available at: http://localhost:{port}")
    print(f"🤖 AI Learning Companion: http://localhost:{port}/learning/")
    print(f"📊 API Documentation: http://localhost:{port}/docs")

    # Import and run the enhanced server
    try:
        from api.enhanced_server import app
        import uvicorn

        uvicorn.run(
            "api.enhanced_server:app",
            host=host,
            port=port,
            log_level="info",
            reload=reload
        )
    except ImportError as e:
        print(f"❌ Failed to import enhanced server: {e}")
        sys.exit(1)

def launch_interactive():
    """Launch in interactive mode."""
    print("🎮 Enhanced Arcade Terminal - Interactive Mode")
    print("=" * 50)

    if not check_environment():
        print("\nContinuing with limited functionality...")

    print("\n🤖 AI Features:")
    print("   • Intelligent command assistance")
    print("   • Code explanation and learning")
    print("   • Context-aware help")
    print("   • Emotionally-adaptive learning")

    print("\n🎯 Available Commands:")
    print("   • ai help - AI assistant commands")
    print("   • ai ask <question> - Ask anything")
    print("   • ai explain <command> - Get command explanation")
    print("   • ai learn - Enable learning mode")

    try:
        port = int(input("\n🌐 Port (default 7681): ") or "7681")
        host = input("🏠 Host (default 0.0.0.0): ") or "0.0.0.0"
        reload = input("🔄 Enable auto-reload? (y/n, default y): ").lower() != "n"

        launch_server(port, host, reload)

    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def show_help():
    """Show help information."""
    print("🎮 Enhanced Arcade Terminal")
    print("=" * 30)
    print()
    print("Usage:")
    print("  python -m arcade [command] [options]")
    print()
    print("Commands:")
    print("  launch, l     Launch the server")
    print("  interactive,i Interactive setup and launch")
    print("  help, h       Show this help")
    print()
    print("Options:")
    print("  --port PORT   Server port (default: 7681)")
    print("  --host HOST   Server host (default: 0.0.0.0)")
    print("  --no-reload   Disable auto-reload")
    print()
    print("Examples:")
    print("  python -m arcade launch")
    print("  python -m arcade launch --port 8000")
    print("  python -m arcade interactive")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enhanced Arcade Terminal")
    parser.add_argument("command", nargs="?", default="interactive",
                       choices=["launch", "l", "interactive", "i", "help", "h"])
    parser.add_argument("--port", type=int, default=7681, help="Server port")
    parser.add_argument("--host", default="0.0.0.0", help="Server host")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")

    args = parser.parse_args()

    # Change to the Arcade directory
    arcade_dir = Path(__file__).parent
    os.chdir(arcade_dir)

    if args.command in ["help", "h"]:
        show_help()
    elif args.command in ["launch", "l"]:
        if check_environment():
            reload = not args.no_reload
            launch_server(args.port, args.host, reload)
        else:
            print("❌ Environment not configured. Run 'python -m arcade interactive' first.")
            sys.exit(1)
    elif args.command in ["interactive", "i"]:
        launch_interactive()
    else:
        show_help()

if __name__ == "__main__":
    main()
