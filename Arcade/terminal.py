#!/usr/bin/env python3
"""
Atmosphere Arcade - Python Terminal
A robust terminal interface with rich text formatting.
"""

import os
import sys
import json
import signal
import asyncio
from pathlib import Path
from typing import List, Optional
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

# Constants
VERSION = "1.0.0"
HISTORY_FILE = Path.home() / ".atmosphere_history"
MAX_HISTORY = 1000

class Terminal:
    def __init__(self):
        self.console = Console()
        self.running = True
        self.history: List[str] = []
        self.current_dir = str(Path.cwd())
        self.load_history()

    def load_history(self):
        """Load command history from file."""
        try:
            if HISTORY_FILE.exists():
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not load history: {e}[/]")

    def save_history(self):
        """Save command history to file."""
        try:
            HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history[-MAX_HISTORY:], f)
        except Exception as e:
            self.console.print(f"[yellow]Warning: Could not save history: {e}[/]")

    def print_welcome(self):
        """Print welcome message."""
        welcome = f"""[blue]
┌───────────────────────────────────────────────┐
│   [bold]Atmosphere Arcade Terminal[/bold] v{VERSION}       │
│   [dim]Type 'help' for available commands[/dim]        │
└───────────────────────────────────────────────┘[/]"""
        self.console.print(welcome)

    def show_help(self):
        """Show help information."""
        help_text = """[bold]Available Commands:[/]

[bold]Basic:[/]
  help          Show this help message
  clear         Clear the terminal
  history       Show command history
  exit, quit    Exit the terminal

[bold]File Operations:[/]
  ls, dir       List directory contents
  cd <dir>      Change directory
  pwd           Print working directory
  cat <file>    Display file contents

[bold]System:[/]
  sysinfo       Show system information
  diskusage     Show disk usage
  processes     List running processes"""
        self.console.print(Panel(help_text, title="Help", border_style="blue"))

    async def process_command(self, command: str) -> Optional[str]:
        """Process a command and return the output."""
        if not command.strip():
            return None

        cmd = command.lower().split()[0]
        args = command.split()[1:]

        try:
            if cmd in ('exit', 'quit'):
                self.running = False
                return None
            elif cmd in ('help', '?'):
                self.show_help()
                return None
            elif cmd == 'clear':
                self.console.clear()
                return None
            elif cmd == 'history':
                return self.show_command_history()
            elif cmd in ('ls', 'dir'):
                return self.list_directory(' '.join(args) if args else '.')
            elif cmd == 'cd':
                return self.change_directory(' '.join(args) if args else '~')
            elif cmd == 'pwd':
                return str(Path(self.current_dir).resolve())
            else:
                return f"[yellow]Command not found: {cmd}[/]"
        except Exception as e:
            return f"[red]Error: {str(e)}[/]"

    def list_directory(self, path: str) -> str:
        """List directory contents."""
        target = (Path(self.current_dir) / path).resolve()
        if not target.exists():
            return f"[red]Directory not found: {path}[/]"
        
        if target.is_file():
            return f"[yellow]{path} is a file, not a directory[/]"
            
        items = []
        for item in target.iterdir():
            if item.is_dir():
                items.append(f"[blue]{item.name}/[/]")
            else:
                items.append(item.name)
        return "  ".join(sorted(items))

    def change_directory(self, path: str) -> str:
        """Change the current working directory."""
        try:
            if path == '~':
                new_dir = str(Path.home())
            else:
                new_dir = str((Path(self.current_dir) / path).resolve())
            
            if not Path(new_dir).is_dir():
                return f"[red]No such directory: {path}[/]"
                
            self.current_dir = new_dir
            os.chdir(new_dir)
            return f"Changed directory to {new_dir}"
        except Exception as e:
            return f"[red]Error changing directory: {str(e)}[/]"

    def show_command_history(self) -> str:
        """Return formatted command history."""
        if not self.history:
            return "[dim]No command history[/]"
            
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=6)
        table.add_column("Command")
        
        for i, cmd in enumerate(self.history[-20:], 1):
            table.add_row(str(len(self.history) - 20 + i), cmd)
        
        return str(table)

    async def run(self):
        """Run the terminal main loop."""
        self.print_welcome()
        
        while self.running:
            try:
                # Get user input
                try:
                    user_input = Prompt.ask(f"[green]{Path(self.current_dir).name}[/] $")
                except (EOFError, KeyboardInterrupt):
                    self.console.print("\n[red]^C[/]")
                    continue
                
                if not user_input.strip():
                    continue
                
                # Add to history
                if not self.history or self.history[-1] != user_input:
                    self.history.append(user_input)
                    self.save_history()
                
                # Process command
                result = await self.process_command(user_input)
                if result is not None:
                    self.console.print(result)
                    
            except Exception as e:
                self.console.print(f"[red]Error: {str(e)}[/]")
                if self.console.input("Show traceback? [y/N]: ").lower() == 'y':
                    import traceback
                    traceback.print_exc()
        
        self.console.print("[green]Goodbye![/]")

def main():
    """Main entry point."""
    try:
        # Check Python version
        if sys.version_info < (3, 7):
            print("Error: Python 3.7 or higher is required.", file=sys.stderr)
            return 1
        
        # Initialize and run terminal
        terminal = Terminal()
        asyncio.run(terminal.run())
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())