"""
Command-line interface for Atmosphere Audio.
"""
import argparse
import logging
import sys
from typing import List, Optional

def main(args: Optional[List[str]] = None) -> int:
    """Main entry point for the command-line interface.
    
    Args:
        args: Command-line arguments (defaults to sys.argv[1:])
        
    Returns:
        int: Exit code
    """
    parser = argparse.ArgumentParser(
        description="Atmosphere Audio - Comprehensive audio processing and routing system"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Show version and exit"
    )
    
    # Parse arguments
    parsed_args = parser.parse_args(args)
    
    # Configure logging
    log_level = logging.DEBUG if parsed_args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    if parsed_args.version:
        from . import __version__
        print(f"Atmosphere Audio v{__version__}")
        return 0
    
    print("Atmosphere Audio - Use '--help' for usage information")
    return 0

if __name__ == "__main__":
    sys.exit(main())
