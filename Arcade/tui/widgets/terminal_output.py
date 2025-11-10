"""
Terminal Output Widget
Scrollable terminal output with ANSI color support.
"""

from textual.widgets import RichLog
from rich.console import Console
from rich.text import Text
from typing import Optional


class TerminalOutput(RichLog):
    """Terminal output widget with ANSI color support."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.console = Console()
        self.max_lines = 1000  # Maximum lines to keep in buffer
    
    def write_text(self, text: str, style: Optional[str] = None):
        """Write text to terminal output."""
        # Preserve ANSI codes and write to RichLog
        if style:
            styled_text = Text(text, style=style)
            super().write(styled_text)
        else:
            # Parse ANSI codes and convert to rich Text
            super().write(text)
    
    def write_colored(self, text: str, color: str = "default"):
        """Write colored text."""
        color_map = {
            "green": "[green]",
            "cyan": "[cyan]",
            "yellow": "[yellow]",
            "red": "[red]",
            "magenta": "[magenta]",
            "gray": "[dim]",
            "default": ""
        }
        
        markup = color_map.get(color, "")
        if markup:
            self.write(f"{markup}{text}[/{markup[1:-1]}]")
        else:
            self.write_text(text)
    
    def clear_output(self):
        """Clear terminal output."""
        super().clear()

