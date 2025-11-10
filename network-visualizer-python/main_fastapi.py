"""
Main entry point for Network Visualizer FastAPI Server

Run this script to start the new Cable-style API server.
"""
import argparse
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from network_visualizer.ui.fastapi_server import start_server


def main():
    """Main entry point for the FastAPI server."""
    parser = argparse.ArgumentParser(
        description="Network Visualizer API Server (Cable-style)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_fastapi.py                    # Start with defaults
  python main_fastapi.py --port 8080       # Custom port
  python main_fastapi.py --debug           # Enable debug mode
  python main_fastapi.py --host 0.0.0.0    # Allow external access
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Server host address (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Server port (default: 8000)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with auto-reload"
    )
    
    parser.add_argument(
        "--docs",
        action="store_true",
        help="Open browser to API documentation"
    )
    
    args = parser.parse_args()
    
    print("🌐 Network Visualizer - Cable-style API Server")
    print("=" * 50)
    
    # Start the server
    start_server(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
    
    # Open docs if requested
    if args.docs:
        import webbrowser
        docs_url = f"http://{args.host}:{args.port}/docs"
        webbrowser.open(docs_url)


if __name__ == "__main__":
    main()
