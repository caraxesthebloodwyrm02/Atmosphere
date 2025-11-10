"""
Routing API Connector
Dynamic connection between Routing module and Direct OpenAI API.
"""

try:
    from ..api_connector_main import RoutingAPIConnector, get_routing_connector, route_with_ai, test_routing_api
except ImportError:
    # Fallback for direct execution
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from api_connector_main import RoutingAPIConnector, get_routing_connector, route_with_ai, test_routing_api

__all__ = [
    "RoutingAPIConnector",
    "get_routing_connector", 
    "route_with_ai",
    "test_routing_api"
]
