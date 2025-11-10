"""
User Interface Module

Provides web-based and desktop interfaces for network visualization,
including interactive dashboards and command-line tools.
"""

from .cli import CLI
from .web_app import WebApp

__all__ = [
    "CLI",
    "WebApp",
]
