"""
Command Input Widget
Command input with history and auto-completion.
"""

from textual.widgets import Input
from textual import events
from pathlib import Path
from typing import List, Optional, Callable
import json


class CommandInput(Input):
    """Command input widget with history support."""
    
    def __init__(self, on_command: Optional[Callable] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_command = on_command
        self.history: List[str] = []
        self.history_index = -1
        self.history_file = Path.home() / ".arcade_tui_history"
        self.load_history()
    
    def on_mount(self) -> None:
        """Called when widget is mounted."""
        self.placeholder = "Enter command (F1 for help, ESC to cancel)"
    
    async def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if event.key == "up":
            event.prevent_default()
            self.navigate_history(-1)
        elif event.key == "down":
            event.prevent_default()
            self.navigate_history(1)
        elif event.key == "enter":
            await self.handle_command()
        else:
            # Reset history navigation on typing
            self.history_index = -1
    
    async def handle_command(self):
        """Handle command submission."""
        command = self.value.strip()
        if not command:
            return
        
        # Add to history
        if not self.history or self.history[-1] != command:
            self.history.append(command)
            if len(self.history) > 100:  # Limit history size
                self.history.pop(0)
            self.save_history()
        
        # Reset history index
        self.history_index = -1
        
        # Clear input
        self.value = ""
        
        # Call command handler
        if self.on_command:
            if callable(self.on_command):
                await self.on_command(command)
    
    def navigate_history(self, direction: int):
        """Navigate through command history."""
        if not self.history:
            return
        
        self.history_index += direction
        
        if self.history_index < 0:
            self.history_index = -1
            self.value = ""
        elif self.history_index >= len(self.history):
            self.history_index = len(self.history) - 1
        
        if 0 <= self.history_index < len(self.history):
            self.value = self.history[-(self.history_index + 1)]
    
    def load_history(self):
        """Load command history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []
    
    def save_history(self):
        """Save command history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f)
        except Exception:
            pass

