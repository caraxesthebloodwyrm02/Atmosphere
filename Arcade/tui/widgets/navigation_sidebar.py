"""
Navigation Sidebar Widget
Sidebar with navigation menu and quick access.
"""

from textual.widgets import Static, Collapsible
from textual.containers import Vertical, Horizontal
from textual import events
from typing import Callable, Optional


class NavigationSidebar(Vertical):
    """Navigation sidebar with location list and tool access."""
    
    def __init__(self, on_location_select: Optional[Callable] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.on_location_select = on_location_select
        self.current_location = "Arcade"
        self.locations = ["Arcade", "Echoes", "Reverb", "Delay"]
    
    def compose(self):
        """Compose sidebar widgets."""
        with Collapsible(title="Locations", collapsed=False):
            for location in self.locations:
                yield Static(f"  {location}", classes="location-item")
        
        with Collapsible(title="Tools", collapsed=False):
            yield Static("  analyze", classes="tool-item")
            yield Static("  visualize", classes="tool-item")
            yield Static("  game", classes="tool-item")
            yield Static("  playground", classes="tool-item")
        
        with Collapsible(title="Quick Actions", collapsed=False):
            yield Static("  help", classes="action-item")
            yield Static("  status", classes="action-item")
            yield Static("  speed", classes="action-item")
    
    def set_location(self, location: str):
        """Set current location and highlight it."""
        self.current_location = location
        # Update location highlighting
        self.refresh()
    
    def on_click(self, event: events.Click) -> None:
        """Handle click on sidebar items."""
        widget = event.widget
        if isinstance(widget, Static):
            text = str(widget.renderable) if hasattr(widget, 'renderable') else ""
            text = text.strip()
            
            if text in self.locations and self.on_location_select:
                self.on_location_select(text)
            elif text.startswith("  "):
                # Tool or action clicked - set command input value
                command = text.strip()
                try:
                    command_input = self.app.query_one("#command-input")
                    command_input.value = command
                    # Focus command input so user can press Enter
                    command_input.focus()
                except Exception:
                    pass

