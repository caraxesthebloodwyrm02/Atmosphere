"""
Atmosphere Project
Main project initialization and entry point.

This package serves as the root for the Atmosphere ecosystem,
providing unified access to all major components including:
- EchoesAI: Advanced AI research platform
- Delay: Audio processing and effects
- Reverb: Spatial audio processing
- Routing: Audio routing and management
- API: Direct OpenAI integration
"""

__version__ = "1.0.0"
__author__ = "Atmosphere Team"
__description__ = "Advanced audio and AI processing platform"

# Import major components with proper error handling
echoes_version = delay_version = reverb_version = routing_version = api_version = "unknown"

try:
    # Try different import strategies
    try:
        # Try as installed package
        import Echoes
        echoes_version = Echoes.__version__
    except ImportError:
        # Try as relative import
        from .Echoes import __version__ as echoes_version
except ImportError as e:
    print(f"Warning: Echoes import failed - {str(e)}")
    echoes_version = "not_installed"

try:
    import Delay
    delay_version = Delay.__version__
except ImportError:
    try:
        from .Delay import __version__ as delay_version
    except ImportError:
        delay_version = "not_installed"

try:
    import Reverb
    reverb_version = Reverb.__version__
except ImportError:
    try:
        from .Reverb import __version__ as reverb_version
    except ImportError:
        reverb_version = "not_installed"

try:
    import Routing
    routing_version = Routing.__version__
except ImportError:
    try:
        from .Routing import __version__ as routing_version
    except ImportError:
        routing_version = "not_installed"

try:
    import api
    api_version = api.__version__
except ImportError:
    try:
        from .api import __version__ as api_version
    except ImportError:
        api_version = "not_installed"

def get_version_info():
    """Get version information for all components."""
    return {
        "atmosphere": __version__,
        "echoes": echoes_version,
        "delay": delay_version,
        "reverb": reverb_version,
        "routing": routing_version,
        "api": api_version
    }

def main():
    """Main entry point for the Atmosphere project."""
    print("🌍 Atmosphere Platform v{}".format(__version__))
    print("=" * 50)

    versions = get_version_info()
    for component, version in versions.items():
        if version not in ["unknown", "not_installed"]:
            print(f"  {component.title()}: v{version}")
        else:
            print(f"  {component.title()}: {version}")

    print("=" * 50)
    print("Use 'python -m <component>' to start specific modules")
    print("Available components: echoes, delay, reverb, routing, api")

if __name__ == "__main__":
    main()
