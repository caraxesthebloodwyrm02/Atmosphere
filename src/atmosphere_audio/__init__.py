"""
Atmosphere Audio
A comprehensive audio processing and routing system for immersive experiences.
"""

__version__ = "0.1.0"

# Import core modules to make them available at the package level
from . import delay
from . import echo
from . import reverb
from . import routing
from . import core

# Define public API
__all__ = [
    '__version__',
    'delay',
    'echo',
    'reverb',
    'routing',
    'core'
]

# Initialize logging when the package is imported
import logging

# Configure package-level logger
logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

# Initialize package
logger.info(f'Atmosphere Audio {__version__} initialized')
