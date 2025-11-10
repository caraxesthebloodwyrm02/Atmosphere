"""
Arcade Terminal TUI Application
Main application class for the TUI.
"""

import logging
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from pathlib import Path

from .screens.main_screen import MainScreen

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ArcadeApp(App):
    """Main Arcade Terminal TUI application."""
    
    CSS_PATH = str(Path(__file__).parent / "themes" / "arcade_theme.css")
    
    TITLE = "Arcade Terminal"
    SUB_TITLE = "Retro Entertainment Space"
    
    BINDINGS = [
        Binding("f1", "help", "Help", priority=True),
        Binding("escape", "back", "Back"),
        Binding("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.standalone_mode = True
        logger.debug("ArcadeApp initialized")
    
    def compose(self) -> ComposeResult:
        """Compose application."""
        yield MainScreen()
    
    def on_mount(self) -> None:
        """Called when app is mounted."""
        logger.debug("ArcadeApp.on_mount called")
        try:
            self.push_screen(MainScreen())
            logger.debug("MainScreen pushed successfully")
        except Exception as e:
            logger.error(f"Failed to push MainScreen: {e}", exc_info=True)
    
    async def action_help(self) -> None:
        """Show help."""
        logger.debug("Help action triggered")
        # Help is handled by MainScreen
    
    async def action_back(self) -> None:
        """Go back."""
        logger.debug("Back action triggered")
        # Back navigation handled by screens
    
    async def action_quit(self) -> None:
        """Quit application."""
        logger.debug("Quit action triggered")
        self.exit()

