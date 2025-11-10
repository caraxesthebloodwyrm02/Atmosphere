"""
Status Bar Widget
Status bar displaying game state and connection status.
"""

from textual.widgets import Static
from textual import events
from typing import Optional


class StatusBar(Static):
    """Status bar at bottom of screen."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.location = "Arcade"
        self.score = 0
        self.level = 1
        self.speed = 0.0
        self.connected = False
    
    
    def update_status(self):
        """Update status bar display."""
        connection_status = "●" if self.connected else "○"
        status_text = (
            f"Location: [cyan]{self.location}[/cyan] | "
            f"Score: [yellow]{self.score}[/yellow] | "
            f"Level: [magenta]{self.level}[/magenta] | "
            f"Speed: [green]{self.speed:.1f}[/green] | "
            f"Status: {connection_status}"
        )
        self.update(status_text)
    
    def set_location(self, location: str):
        """Set current location."""
        self.location = location
        self.update_status()
    
    def set_score(self, score: int):
        """Set score."""
        self.score = score
        self.update_status()
    
    def set_level(self, level: int):
        """Set level."""
        self.level = level
        self.update_status()
    
    def set_speed(self, speed: float):
        """Set speed."""
        self.speed = speed
        self.update_status()
    
    def set_connected(self, connected: bool):
        """Set connection status."""
        self.connected = connected
        self.update_status()

