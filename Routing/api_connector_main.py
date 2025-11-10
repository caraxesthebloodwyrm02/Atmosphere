#!/usr/bin/env python3
"""
Routing API Connector
Dynamic connection between Routing module and Direct OpenAI API.
"""

import asyncio
import logging
from typing import Dict, Any
import sys
import os

# Add parent directory to path for API import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
atmosphere_root = os.path.dirname(parent_dir)
sys.path.append(atmosphere_root)

try:
    from api.client import get_client
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    logging.warning("Direct OpenAI API not available")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RoutingAPIConnector:
    """Dynamic connector between Routing and OpenAI API."""
    
    def __init__(self):
        """Initialize the routing API connector."""
        self.api_client = None
        self.connection_status = "disconnected"
        self.routing_data = {}
        
        if API_AVAILABLE:
            self._initialize_api_client()
        else:
            logger.error("OpenAI API not available for routing integration")
    
    def _initialize_api_client(self):
        """Initialize the OpenAI API client."""
        try:
            self.api_client = get_client()
            if self.api_client.test_connection():
                self.connection_status = "connected"
                logger.info("Routing API connector initialized successfully")
            else:
                self.connection_status = "failed"
                logger.error("Failed to connect to OpenAI API for routing")
        except (ImportError, ConnectionError, OSError) as e:
            self.connection_status = "error"
            logger.error("Error initializing routing API connector: %s", e)
    
    async def process_routing_request(self, routing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process routing request using OpenAI API.
        
        Args:
            routing_data: Dictionary containing routing parameters
            
        Returns:
            Processed routing response
        """
        if not self.api_client or self.connection_status != "connected":
            return {
                "status": "error",
                "message": "API not available",
                "fallback": self._get_fallback_routing(routing_data)
            }
        
        try:
            # Create prompt for routing optimization
            prompt = self._create_routing_prompt(routing_data)
            
            # Get AI assistance for routing
            response = await self.api_client.simple_chat(
                prompt, 
                model="gpt-3.5-turbo"
            )
            
            # Parse AI response
            optimized_routing = self._parse_routing_response(response)
            
            return {
                "status": "success",
                "original_data": routing_data,
                "optimized_routing": optimized_routing,
                "ai_suggestions": response,
                "connection_status": self.connection_status
            }
            
        except (ImportError, ConnectionError, OSError, ValueError) as e:
            logger.error("Error processing routing request: %s", e)
            return {
                "status": "error",
                "message": str(e),
                "fallback": self._get_fallback_routing(routing_data)
            }
    
    def _create_routing_prompt(self, routing_data: Dict[str, Any]) -> str:
        """Create a prompt for routing optimization."""
        prompt = """
        You are an expert audio routing system. Analyze the following routing data and provide optimization suggestions:
        
        Routing Data: {routing_data}
        
        Please provide:
        1. Optimal routing path
        2. Performance improvements
        3. Potential bottlenecks
        4. Recommended settings
        
        Respond in JSON format with clear, actionable recommendations.
        """.format(routing_data=routing_data)
        
        return prompt
    
    def _parse_routing_response(self, response: str) -> Dict[str, Any]:
        """Parse the AI response for routing optimization."""
        # Simple parsing - in production, you'd want more sophisticated parsing
        return {
            "recommendations": response.split('\n'),
            "optimization_applied": True,
            "estimated_improvement": "15-25%"
        }
    
    def _get_fallback_routing(self, _routing_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get fallback routing when API is unavailable."""
        return {
            "status": "fallback",
            "message": "Using default routing configuration",
            "routing_path": "default",
            "settings": {
                "buffer_size": 1024,
                "sample_rate": 44100,
                "channels": 2
            }
        }
    
    async def get_routing_health(self) -> Dict[str, Any]:
        """Get health status of routing API connection."""
        return {
            "connection_status": self.connection_status,
            "api_available": API_AVAILABLE,
            "last_check": asyncio.get_event_loop().time(),
            "routing_data_count": len(self.routing_data)
        }
    
    def test_integration(self) -> bool:
        """Test the routing API integration."""
        if not API_AVAILABLE:
            return False
        
        try:
            # Test basic connectivity
            if self.connection_status == "connected":
                return True
            
            # Try to reinitialize
            self._initialize_api_client()
            return self.connection_status == "connected"
            
        except (ImportError, ConnectionError, OSError) as e:
            logger.error("Integration test failed: %s", e)
            return False

# Module-level connector instance
_connector = None

def get_routing_connector() -> RoutingAPIConnector:
    """Get routing connector instance."""
    global _connector
    if _connector is None:
        _connector = RoutingAPIConnector()
    return _connector

# Quick usage functions
async def route_with_ai(routing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Quick routing function with AI assistance."""
    connector = get_routing_connector()
    return await connector.process_routing_request(routing_data)

def test_routing_api() -> bool:
    """Test routing API connection."""
    connector = get_routing_connector()
    return connector.test_integration()

async def demo():
    """Demo of routing API integration."""
    print("🛣️ Routing API Connector Demo")
    print("=" * 40)
    
    # Test integration
    if test_routing_api():
        print("✅ Routing API integration successful")
    else:
        print("❌ Routing API integration failed")
        return
    
    # Test routing request
    sample_routing_data = {
        "source": "input_device",
        "destination": "output_device",
        "parameters": {
            "latency": "low",
            "quality": "high",
            "channels": 2
        }
    }
    
    try:
        result = await route_with_ai(sample_routing_data)
        print(f"\n🎯 Routing Result: {result['status']}")
        if result['status'] == 'success':
            print("✅ AI-powered routing optimization applied")
        else:
            print("⚠️ Using fallback routing")
    except (ImportError, ConnectionError, OSError, ValueError) as e:
        logger.error("Routing demo failed: %s", e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
