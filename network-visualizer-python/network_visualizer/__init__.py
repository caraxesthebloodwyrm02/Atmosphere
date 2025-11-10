"""
Network Visualizer - Advanced Network Visualization and Analysis Toolkit

A comprehensive Python library for network visualization and analysis,
inspired by Gephi but built with modern Python tools and libraries.
"""

__version__ = "0.1.0"
__author__ = "Network Visualizer Team"
__email__ = "team@network-visualizer.org"
__license__ = "MIT"

from .core import NetworkVisualizer
from .core.visualizer import NetworkVisualizer as Visualizer
from .core.algorithms import NetworkAnalyzer
from .core.layouts import LayoutManager

__all__ = [
    "NetworkVisualizer",
    "Visualizer",
    "NetworkAnalyzer",
    "LayoutManager",
    "__version__",
    "__author__",
    "__email__",
    "__license__",
]

def create_visualizer(**kwargs):
    """
    Create and return a NetworkVisualizer instance.

    Args:
        **kwargs: Configuration parameters for the visualizer

    Returns:
        NetworkVisualizer: Configured visualizer instance
    """
    return NetworkVisualizer(**kwargs)
