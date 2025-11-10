"""
Arcade API Module
Web API layer for terminal-based entertainment space.
"""

__version__ = "1.0.0"
__author__ = "Atmosphere Team"

from .server import app, create_app
from .terminal_handler import TerminalHandler
from .security import SecurityManager, CommandValidator
from .game_engine import GameEngine
from .routing_integration import RoutingIntegration

__all__ = [
    "app",
    "create_app",
    "TerminalHandler",
    "SecurityManager",
    "CommandValidator",
    "GameEngine",
    "RoutingIntegration",
]

