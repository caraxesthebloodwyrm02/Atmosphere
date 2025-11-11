#!/usr/bin/env python3
"""
Atmosphere Arcade - Advanced TUI Terminal
A powerful text-based terminal interface with enhanced capabilities.
"""

import os
import sys
import asyncio
import json
import signal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.box import ROUNDED
from textual.app import App, ComposeResult
from textual.containers import Container, ScrollableContainer
from textual.widgets import Header, Footer, Static, Input, Button, Label
from textual.reactive import reactive
from textual import events, work, on
from textual.worker import Worker, WorkerState

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.absolute()))

# Import local modules
from api.enhanced_server_test import EnhancedTerminalHandler
from api.chatgpt_manager import ChatGPTManager

# Constants
VERSION = "1.0.0"
DEFAULT_PROMPT = "> "
HISTORY_FILE = os.path.expanduser("~/.atmosphere_terminal_history")
MAX_HISTORY = 1000


class TerminalTUI(App):
    """Main TUI application for the Atmosphere Arcade Terminal."""
    
    CSS_PATH = "terminal_tui.css"
    BINDINGS = [
        ("ctrl+c", "interrupt", "Interrupt"),
        ("f1", "toggle_help", "Help"),
        ("f2", "toggle_history", "History"),
        ("f5", "clear_screen", "Clear"),
        ("f10", "quit", "Quit"),
    ]
    
    # Reactive attributes
    current_dir = reactive(str(Path.cwd()))
    connection_status = reactive("disconnected")
    command_history = reactive([])
    history_index = reactive(-1)
    show_help = reactive(False)
    show_history = reactive(False)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.terminal_handler = None
        self.ai_assistant = None
        self.current_command = ""
        self.command_output = []
        self.history = []
        self.load_history()
        
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header(show_clock=True)
        
        with Container(id="main-container"):
            # Output panel
            with ScrollableContainer(id="output-panel"):
                yield Static("", id="output")
                
            # Help panel (hidden by default)
            with Container(id="help-panel", classes="hidden"):
                yield Static(self._get_help_text(), id="help-content")
                
            # History panel (hidden by default)
            with Container(id="history-panel", classes="hidden"):
                yield Static("", id="history-content")
            
            # Input area
            with Container(id="input-area"):
                yield Label("└─ ", id="prompt")
                yield Input(
                    "", 
                    id="command-input", 
                    placeholder="Type a command..."
                )
                
        yield Footer()
    
    def on_mount(self) -> None:
        """Initialize the application."""
        self.title = f"Atmosphere Arcade Terminal [v{VERSION}]"
        self.sub_title = "AI-Powered Command Line"
        
        # Initialize terminal handler and AI assistant
        self.initialize_services()
        
        # Set focus to input
        self.query_one("#command-input", Input).focus()
        
        # Display welcome message
        self.output(self._get_welcome_message())
        self.output("Type 'help' for available commands or press F1 for help.", "dim")
        
    def initialize_services(self) -> None:
        """Initialize terminal handler and AI assistant."""
        try:
            # Initialize AI assistant
            self.ai_assistant = ChatGPTManager()
            
            # Initialize terminal handler with AI capabilities
            self.terminal_handler = EnhancedTerminalHandler(ai_assistant=self.ai_assistant)
            
            # Set up signal handlers
            signal.signal(signal.SIGINT, self.handle_interrupt)
            
            self.connection_status = "connected"
            self.update_status()
            
        except Exception as e:
            self.output(f"[red]Error initializing services: {str(e)}[/]")
            self.connection_status = "error"
            self.update_status()
    
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle command submission with NLP processing."""
        command = event.value.strip()
        if not command:
            return
            
        # Add to history
        self.add_to_history(command)
        
        # Clear input
        input_widget = self.query_one("#command-input", Input)
        input_widget.value = ""
        
        # Process command with NLP
        processed_command = await self.process_nlp_command(command)
        self.output(f"[bold cyan]{DEFAULT_PROMPT}{command}[/]")
        if processed_command != command:
            self.output(f"[dim]→ Executing: {processed_command}[/]")
        await self.process_command(processed_command)
    
    async def process_nlp_command(self, user_input: str) -> str:
        """Process natural language commands and convert to terminal commands."""
        # Convert to lowercase for easier matching
        text = user_input.lower().strip()
        
        # Direct command mappings (pass through)
        if text.startswith(('ls', 'dir', 'cd', 'pwd', 'cat', 'mkdir', 'rm', 'rmdir', 'sysinfo', 'diskusage', 'processes', 'help', 'clear', 'history', 'exit', 'quit')):
            return user_input
        
        # AI commands (pass through)
        if text.startswith(('ask ', 'code ', 'explain ')):
            return user_input
        
        # NLP pattern matching
        try:
            # File operations
            if any(word in text for word in ['list', 'show', 'see', 'display']):
                if any(word in text for word in ['files', 'directory', 'folder', 'contents']):
                    return 'ls'
                elif any(word in text for word in ['history', 'commands']):
                    return 'history'
            
            # Directory navigation
            if any(word in text for word in ['go to', 'change to', 'navigate to', 'cd to']):
                # Extract directory name
                words = text.split()
                for i, word in enumerate(words):
                    if word == 'to' and i + 1 < len(words):
                        return f'cd {words[i+1]}'
            
            elif text in ['go home', 'go back home', 'home directory']:
                return 'cd ~'
            
            elif any(word in text for word in ['go back', 'go up', 'parent directory']):
                return 'cd ..'
            
            # Current directory
            if any(phrase in text for phrase in ['where am i', 'current directory', 'what directory', 'show pwd']):
                return 'pwd'
            
            # System information
            if any(word in text for word in ['system', 'computer', 'machine']):
                if any(word in text for word in ['info', 'information', 'details']):
                    return 'sysinfo'
            
            if any(word in text for word in ['disk', 'storage', 'drive']):
                if any(word in text for word in ['usage', 'space', 'free']):
                    return 'diskusage'
            
            if any(word in text for word in ['process', 'running', 'task']):
                return 'processes'
            
            # File reading
            if any(word in text for word in ['read', 'show', 'display', 'open']):
                if any(word in text for word in ['file', 'contents']):
                    # Extract filename - look for quoted strings or last word
                    import re
                    quoted = re.findall(r'"([^"]*)"', user_input) or re.findall(r"'([^']*)'", user_input)
                    if quoted:
                        return f'cat {quoted[0]}'
                    else:
                        words = user_input.split()
                        if len(words) > 1:
                            return f'cat {words[-1]}'
            
            # Directory creation
            if any(word in text for word in ['create', 'make', 'new']):
                if any(word in text for word in ['directory', 'folder', 'dir']):
                    # Extract directory name
                    words = user_input.split()
                    for i, word in enumerate(words):
                        if word in ['directory', 'folder', 'dir'] and i + 1 < len(words):
                            return f'mkdir {words[i+1]}'
            
            # File deletion
            if any(word in text for word in ['delete', 'remove', 'erase']):
                if any(word in text for word in ['file']):
                    # Extract filename
                    import re
                    quoted = re.findall(r'"([^"]*)"', user_input) or re.findall(r"'([^']*)'", user_input)
                    if quoted:
                        return f'rm {quoted[0]}'
                    else:
                        words = user_input.split()
                        if len(words) > 1:
                            return f'rm {words[-1]}'
            
            # Help commands
            if any(word in text for word in ['help', 'assist', 'guide', 'commands']):
                return 'help'
            
            # Clear commands
            if any(word in text for word in ['clear', 'clean', 'reset']):
                if any(word in text for word in ['screen', 'terminal', 'window']):
                    return 'clear'
            
            # Exit commands
            if any(word in text for word in ['exit', 'quit', 'leave', 'bye', 'goodbye']):
                return 'exit'
            
            # If we have AI assistant available, use it for complex queries
            if self.ai_assistant:
                # For complex or unrecognized commands, try AI interpretation
                try:
                    ai_prompt = f"""Convert this natural language request to a terminal command. 
                    If it's not a clear terminal command, respond with just the original text.
                    
                    Request: "{user_input}"
                    
                    Available commands:
                    - File operations: ls, cd, pwd, cat, mkdir, rm, rmdir
                    - System: sysinfo, diskusage, processes
                    - AI: ask <question>, code <task>, explain <command>
                    - Terminal: clear, history, help, exit
                    
                    Return only the command, no explanation:"""
                    
                    # Use AI to interpret the command
                    ai_response = await self.ai_assistant.generate_response(ai_prompt)
                    if ai_response and ai_response.strip() != user_input:
                        # Clean up the response
                        command = ai_response.strip().strip('`').strip()
                        if command and not command.startswith(('ask ', 'code ', 'explain ')):
                            return command
                            
                except Exception:
                    pass  # Fall back to original input
            
            # If no pattern matches, return original input
            return user_input
            
        except Exception as e:
            # If NLP processing fails, return original input
            self.output(f"[yellow]NLP processing failed: {str(e)}[/]")
            return user_input
    
    async def process_command(self, command: str) -> None:
        """Process a command and display the output."""
        try:
            # Handle special commands
            if command.lower() in ['exit', 'quit']:
                await self.action_quit()
                return
                
            # Process command using terminal handler
            if self.terminal_handler:
                # Run command in a worker to avoid blocking the UI
                self.run_worker(
                    self.execute_command(command),
                    name=f"command-{command[:20]}...",
                    description=f"Executing: {command}",
                    group="commands",
                    exclusive=True,
                )
            else:
                self.output("[red]Terminal handler not initialized.[/]")
                
        except Exception as e:
            self.output(f"[red]Error: {str(e)}[/]")
    
    async def execute_command(self, command: str) -> None:
        """Execute a command and return the output."""
        try:
            # Process command using the terminal handler
            result = await self.terminal_handler.process_command(command)
            
            # Update current directory if changed
            if hasattr(self.terminal_handler, 'current_dir'):
                self.current_dir = str(self.terminal_handler.current_dir)
                self.update_status()
            
            # Display the result
            if result is not None:
                self.output(str(result))
                
        except Exception as e:
            self.output(f"[red]Error executing command: {str(e)}[/]")
    
    def output(self, text: str, style: str = "") -> None:
        """Append text to the output panel."""
        output_widget = self.query_one("#output", Static)
        current_text = output_widget.renderable.plain if hasattr(output_widget.renderable, 'plain') else ""
        
        # Add timestamp if not the first line
        timestamp = f"[{datetime.now().strftime('%H:%M:%S')}] " if current_text else ""
        
        # Update the output
        new_text = f"{current_text}\n{timestamp}{text}" if current_text else f"{timestamp}{text}"
        output_widget.update(Text.from_markup(new_text, style=style))
        
        # Auto-scroll to bottom
        output_panel = self.query_one("#output-panel", ScrollableContainer)
        output_panel.scroll_end(animate=False)
    
    def update_status(self) -> None:
        """Update the status bar."""
        status = [
            f"Status: {"🟢" if self.connection_status == "connected" else "🔴"} {self.connection_status.upper()}",
            f"Dir: {os.path.basename(self.current_dir) or '/'}",
            f"History: {len(self.history)} commands"
        ]
        self.sub_title = " | ".join(status)
    
    def add_to_history(self, command: str) -> None:
        """Add a command to the history."""
        if command and (not self.history or self.history[-1] != command):
            self.history.append(command)
            self.history = self.history[-MAX_HISTORY:]
            self.save_history()
    
    def load_history(self) -> None:
        """Load command history from file."""
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
        except Exception as e:
            self.output(f"[yellow]Warning: Could not load history: {str(e)}[/]")
    
    def save_history(self) -> None:
        """Save command history to file."""
        try:
            os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
            with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.output(f"[yellow]Warning: Could not save history: {str(e)}[/]")
    
    # Action methods
    def action_toggle_help(self) -> None:
        """Toggle help panel visibility."""
        help_panel = self.query_one("#help-panel", Container)
        help_panel.toggle_class("hidden")
        
        if not help_panel.has_class("hidden"):
            # Hide other panels
            self.query_one("#history-panel", Container).add_class("hidden")
            self.show_history = False
            
            # Focus back to input
            self.query_one("#command-input", Input).focus()
    
    def action_toggle_history(self) -> None:
        """Toggle history panel visibility."""
        history_panel = self.query_one("#history-panel", Container)
        history_panel.toggle_class("hidden")
        
        if not history_panel.has_class("hidden"):
            # Hide other panels
            self.query_one("#help-panel", Container).add_class("hidden")
            self.show_help = False
            
            # Update history content
            history_content = self.query_one("#history-content", Static)
            if self.history:
                history_table = Table(show_header=True, header_style="bold magenta")
                history_table.add_column("#", style="dim", width=6)
                history_table.add_column("Command")
                
                for i, cmd in enumerate(reversed(self.history[-50:]), 1):
                    history_table.add_row(
                        str(len(self.history) - 50 + i) if i <= len(self.history) - 50 else str(i),
                        cmd
                    )
                history_content.update(history_table)
            else:
                history_content.update("[dim]No command history.[/]")
            
            # Focus back to input
            self.query_one("#command-input", Input).focus()
    
    def action_clear_screen(self) -> None:
        """Clear the terminal output."""
        self.query_one("#output", Static).update("")
    
    def action_interrupt(self) -> None:
        """Handle Ctrl+C interrupt."""
        self.output("^C", "dim")
        self.query_one("#command-input", Input).value = ""
        self.query_one("#command-input", Input).focus()
    
    async def action_quit(self) -> None:
        """Quit the application."""
        self.output("\n[bold]Exiting Atmosphere Arcade Terminal...[/]")
        await asyncio.sleep(0.5)
        self.exit()
    
    def handle_interrupt(self, signum, frame):
        """Handle system interrupt signals."""
        self.action_interrupt()
    
    # Helper methods
    def _get_welcome_message(self) -> str:
        """Generate the welcome message."""
        return f"""
[bold blue]┌───────────────────────────────────────────────────┐
│  [bold white]Atmosphere Arcade Terminal v{VERSION}[/]           │
│  [dim]NLP-Enhanced AI Command Line Interface[/]        │
└───────────────────────────────────────────────────┘[/]

You can use [bold]traditional commands[/] or [bold]natural language[/]!
Try: "list files", "show system info", "go to desktop", "clear screen"

Type [bold]help[/] for all commands or press [bold]F1[/] for help.
"""
    
    def _get_help_text(self) -> str:
        """Generate the help text."""
        return """[bold]Atmosphere Arcade Terminal - NLP Enhanced[/]

[bold]Available Commands:[/]

[bold]File Operations:[/]
  ls, dir       List directory contents
  cd <dir>      Change directory
  pwd           Print working directory
  cat <file>    Display file contents
  mkdir <dir>   Create a directory
  rm <file>     Remove a file
  rmdir <dir>   Remove a directory

[bold]System Information:[/]
  sysinfo       Show system information
  diskusage     Show disk usage
  processes     List running processes

[bold]AI Features:[/]
  ask <query>   Ask the AI assistant a question
  code <task>   Generate code for a specific task
  explain <cmd> Get explanation for a command

[bold]Terminal Controls:[/]
  clear         Clear the terminal
  history       Show command history
  help          Show this help message
  exit, quit    Exit the terminal

[bold]Natural Language Commands:[/]
  "list files" or "show directory"    → ls
  "go to desktop" or "change to docs" → cd <directory>
  "where am I" or "current directory" → pwd
  "read file.txt" or "show contents"  → cat <file>
  "create new folder"                → mkdir <directory>
  "delete file.txt"                  → rm <file>
  "system information"               → sysinfo
  "clear the screen"                 → clear
  "show help"                        → help

[bold]Keyboard Shortcuts:[/]
  [dim]F1[/]         Toggle help
  [dim]F2[/]         Toggle command history
  [dim]F5[/]         Clear screen
  [dim]↑/↓[/]        Navigate command history
  [dim]Tab[/]        Auto-complete commands and paths
  [dim]Ctrl+C[/]     Interrupt current command
  [dim]F10[/]        Quit the application
"""


def run_terminal():
    """Run the TUI terminal application."""
    try:
        # Set up console
        console = Console()
        
        # Check terminal size (more lenient check)
        try:
            term_size = os.get_terminal_size()
            if term_size.columns < 60 or term_size.lines < 10:
                console.print(f"[yellow]Warning: Terminal size is {term_size.columns}x{term_size.lines}. For best experience, use 80x24 or larger.[/]")
                console.print("[yellow]Continuing anyway...[/]")
        except:
            pass  # Skip check if we can't get terminal size
            
        # Run the application
        app = TerminalTUI()
        app.run()
        return 0
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        return 1
    except KeyboardInterrupt:
        console.print("\n[red]Interrupted by user.[/]")
        return 1


if __name__ == "__main__":
    sys.exit(run_terminal())
