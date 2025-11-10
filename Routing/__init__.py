"""
Routing Module - Audio Routing and Management
Advanced acoustic routing and spatial audio management with dynamic API integration.

Version: 1.0.0 (Ecosystem Sync)
Status: Production Ready
Ecosystem Integration: Complete
"""

__version__ = "1.0.0"
__author__ = "Atmosphere Team"
__description__ = "Audio routing and spatial audio management with AI integration"

# Import ecosystem integration
try:
    import sys
    import os
    ecosystem_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(ecosystem_root)
    
    from ecosystem import get_ecosystem
    ECOSYSTEM_AVAILABLE = True
except ImportError:
    ECOSYSTEM_AVAILABLE = False

# Import API connector
try:
    from .api_connector_main import RoutingAPIConnector, get_routing_connector, test_routing_api
    API_INTEGRATION = True
except ImportError:
    API_INTEGRATION = False

def get_routing_status():
    """Get comprehensive Routing status."""
    status = {
        "version": __version__,
        "ecosystem_integration": ECOSYSTEM_AVAILABLE,
        "api_integration": API_INTEGRATION,
        "capabilities": [
            "audio_routing",
            "spatial_management",
            "ai_optimization",
            "ecosystem_coordination"
        ]
    }
    
    if API_INTEGRATION and test_routing_api():
        status["openai_connected"] = True
    else:
        status["openai_connected"] = False
    
    if ECOSYSTEM_AVAILABLE:
        try:
            ecosystem = get_ecosystem()
            status["ecosystem_status"] = "connected"
        except:
            status["ecosystem_status"] = "available"
    else:
        status["ecosystem_status"] = "disconnected"
    
    return status

def main():
    """Main entry point for Routing module."""
    print("🛣️ Routing v{}".format(__version__))
    print("=" * 30)
    print("Audio routing and management")
    print("Ecosystem Integration: {}".format("✅ Available" if ECOSYSTEM_AVAILABLE else "❌ Not Available"))
    
    if API_INTEGRATION:
        print("🔌 API Integration: Available")
        if test_routing_api():
            print("✅ OpenAI API: Connected")
        else:
            print("⚠️ OpenAI API: Disconnected")
    else:
        print("🔌 API Integration: Not Available")
    
    status = get_routing_status()
    
    if status.get("ecosystem_status") == "connected":
        print("🌍 Ecosystem: Connected")
    
    print("")
    print("Usage:")
    print("  python -m Routing.src.acoustic_routing")
    print("  python -m Routing.demo")
    print("  python -m Routing.api_connector")

if __name__ == "__main__":
    main()
