"""
Source Modules
Core source code for all Atmosphere components.
"""

__version__ = "1.0.0"

# Import all major source modules
try:
    from .delay import __version__ as delay_version
    from .echo import __version__ as echo_version
    from .reverb import __version__ as reverb_version
    from .routing import __version__ as routing_version
except ImportError:
    echo_version = delay_version = reverb_version = routing_version = "unknown"


def get_source_versions():
    """Get version information for source modules."""
    return {
        "echo": echo_version,
        "delay": delay_version,
        "reverb": reverb_version,
        "routing": routing_version,
    }
