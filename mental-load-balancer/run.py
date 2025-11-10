#!/usr/bin/env python3
"""
Robust launcher for Mental Load Balancer.
Handles environment setup and Python executable resolution.
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

def find_python_executable():
    """Find the most appropriate Python executable to use."""
    # Try the current Python interpreter first
    python_exec = sys.executable
    if python_exec and os.path.exists(python_exec):
        return python_exec
    
    # Try common Python executable names
    python_names = ['python3', 'python']
    if platform.system() == 'Windows':
        python_names = ['python.exe', 'python3.exe', 'py.exe']
    
    # Check in PATH
    for name in python_names:
        try:
            result = subprocess.run(
                [name, '--version'],
                capture_output=True,
                text=True,
                check=True
            )
            if 'Python 3' in result.stdout or 'Python 3' in result.stderr:
                return name
        except (subprocess.SubprocessError, FileNotFoundError):
            continue
    
    # Check common installation paths on Windows
    if platform.system() == 'Windows':
        common_paths = [
            Path(os.environ.get('LOCALAPPDATA', ''), 'Programs/Python'),
            Path('C:/Program Files/Python3*'),
            Path('C:/Python3*'),
        ]
        
        for path_pattern in common_paths:
            for path in path_pattern.parent.glob(path_pattern.name):
                python_path = path / 'python.exe'
                if python_path.exists():
                    return str(python_path)
    
    # If all else fails, return the default Python command
    return 'python3' if platform.system() != 'Windows' else 'python'

def main():
    """Main entry point for the launcher."""
    # Find Python executable
    python_exec = find_python_executable()
    
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(script_dir, 'mental_load_balancer.py')
    
    # Prepare the command
    args = [python_exec, main_script] + sys.argv[1:]
    
    # Print debug info if requested
    if '--debug' in sys.argv:
        print(f"Python executable: {python_exec}")
        print(f"Script path: {main_script}")
        print(f"Command: {' '.join(f'"{arg}"' if ' ' in arg else arg for arg in args)}")
    
    try:
        # Run the actual script
        result = subprocess.run(
            args,
            cwd=script_dir,
            check=False,
            text=True,
            stdout=sys.stdout,
            stderr=sys.stderr,
            stdin=sys.stdin
        )
        return result.returncode
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        return 1
    except Exception as e:
        print(f"Error launching application: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
