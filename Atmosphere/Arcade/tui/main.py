"""
TUI Entry Point
Main entry point for Arcade Terminal TUI.
"""

import argparse
import sys
from pathlib import Path

# Add Arcade to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tui.app import ArcadeApp


def main():
    """Main entry point for TUI."""
    parser = argparse.ArgumentParser(
        description="Arcade Terminal TUI - Full-stack Text User Interface"
    )
    parser.add_argument(
        "--server",
        action="store_true",
        help="Connect to server (not implemented yet)"
    )
    parser.add_argument(
        "--standalone",
        action="store_true",
        default=True,
        help="Run in standalone mode (default)"
    )
    
    args = parser.parse_args()
    
    # Create and run app
    app = ArcadeApp()
    app.standalone_mode = args.standalone
    
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nExiting...")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

