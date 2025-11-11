#!/usr/bin/env python3
"""
Atmosphere Arcade - Terminal Launcher
A simple launcher for the Atmosphere Arcade TUI terminal.
"""

import os
import sys
import platform
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed."""
    required = ["textual>=0.34.0", "rich>=13.0.0"]
    missing = []
    
    try:
        import pkg_resources
        for package in required:
            try:
                pkg_name = package.split('>=')[0]
                pkg_resources.require(package)
            except (pkg_resources.DistributionNotFound, pkg_resources.VersionConflict):
                missing.append(package)
    except ImportError:
        # Fallback if pkg_resources is not available
        missing = required
    
    return missing

def install_dependencies():
    """Install required dependencies."""
    print("Installing required dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "--upgrade", "textual>=0.34.0", "rich>=13.0.0"
        ])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        return False

def clear_screen():
    """Clear the terminal screen."""
    if platform.system() == 'Windows':
        os.system('cls')
    else:
        os.system('clear')

def print_banner():
    """Print the application banner."""
    banner = """
    ╔══════════════════════════════════════════╗
    ║   █████╗ ████████╗███╗   ███╗ ██████╗    ║
    ║  ██╔══██╗╚══██╔══╝████╗ ████║██╔═══██╗   ║
    ║  ███████║   ██║   ██╔████╔██║██║   ██║   ║
    ║  ██╔══██║   ██║   ██║╚██╔╝██║██║   ██║   ║
    ║  ██║  ██║   ██║   ██║ ╚═╝ ██║╚██████╔╝   ║
    ║  ╚═╝  ╚═╝   ╚═╝   ╚═╝     ╚═╝ ╚═════╝    ║
    ╚══════════════════════════════════════════╝
    Atmosphere Arcade - Advanced TUI Terminal
    """
    print(banner)

def main():
    """Main entry point for the launcher."""
    # Check Python version
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        return 1
    
    # Clear screen and show banner
    clear_screen()
    print_banner()
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print("The following required packages are missing or outdated:")
        for pkg in missing:
            print(f"  - {pkg}")
        
        install = input("\nDo you want to install them now? [Y/n]: ").strip().lower()
        if install in ('', 'y', 'yes'):
            if not install_dependencies():
                return 1
        else:
            print("Please install the required packages manually and try again.")
            return 1
    
    # Import the terminal app after ensuring dependencies are installed
    from terminal_tui import run_terminal
    
    # Run the terminal
    try:
        clear_screen()
        return run_terminal()
    except KeyboardInterrupt:
        print("\nTerminal closed by user.")
        return 0
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        if input("Show detailed error? [y/N]: ").lower() == 'y':
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
