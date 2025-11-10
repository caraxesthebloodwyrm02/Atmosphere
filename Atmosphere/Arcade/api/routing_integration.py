"""
Routing Integration for Arcade Terminal
Connects to the Routing system for city communication (Echoes, Reverb, Delay).
"""

import asyncio
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional
import sys

# Try to import orchestral channel
try:
    # Try absolute import first
    from Arcade.orchestral_channel import (
        OrchestralChannel,
        get_arcade_platform_status,
        receive_orchestral_data
    )
    ORCHESTRAL_AVAILABLE = True
except ImportError:
    try:
        # Fallback: add project root to path and try absolute import
        project_root = Path(__file__).parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))
        from Arcade.orchestral_channel import (
            OrchestralChannel,
            get_arcade_platform_status,
            receive_orchestral_data
        )
        ORCHESTRAL_AVAILABLE = True
    except ImportError:
        try:
            # Final fallback to relative import
            from ..orchestral_channel import (
                OrchestralChannel,
                get_arcade_platform_status,
                receive_orchestral_data
            )
            ORCHESTRAL_AVAILABLE = True
        except ImportError:
            ORCHESTRAL_AVAILABLE = False
            logging.warning("Orchestral channel not available")

logger = logging.getLogger(__name__)


class RoutingIntegration:
    """Integration with Routing system for city communication"""
    
    def __init__(self):
        self.connected = False
        self.orchestral_channel = None
        self.city_status = {
            'Echoes': {'status': 'unknown', 'data': {}},
            'Reverb': {'status': 'unknown', 'data': {}},
            'Delay': {'status': 'unknown', 'data': {}}
        }
        
        if ORCHESTRAL_AVAILABLE:
            try:
                self.orchestral_channel = OrchestralChannel()
            except Exception as e:
                logger.error(f"Failed to initialize orchestral channel: {e}")
    
    async def initialize(self) -> bool:
        """Initialize routing connection"""
        if not ORCHESTRAL_AVAILABLE:
            logger.warning("Orchestral channel not available, using standalone mode")
            return False
        
        try:
            result = await self.orchestral_channel.initialize_arcade_platform()
            if result.get('status') == 'success':
                self.connected = True
                logger.info("Connected to routing system")
                return True
            else:
                logger.warning(f"Failed to connect to routing: {result.get('error')}")
                return False
        except Exception as e:
            logger.error(f"Error initializing routing: {e}")
            return False
    
    async def get_city_status(self, city_name: str) -> Dict[str, Any]:
        """Get status of a specific city"""
        if not self.connected:
            return {
                'status': 'disconnected',
                'message': 'Routing system not connected'
            }
        
        # Request city status from routing system
        # This would typically query the routing system
        city_name_lower = city_name.lower()
        if city_name_lower in ['echoes', 'reverb', 'delay']:
            return self.city_status.get(city_name, {'status': 'unknown'})
        
        return {'status': 'not_found', 'message': f'City {city_name} not found'}
    
    async def navigate_to_city(self, city_name: str) -> Dict[str, Any]:
        """Navigate to a city (game mechanic)"""
        city_name_lower = city_name.lower()
        
        if city_name_lower not in ['echoes', 'reverb', 'delay']:
            return {
                'success': False,
                'message': f'Unknown city: {city_name}'
            }
        
        # Get city status
        status = await self.get_city_status(city_name)
        
        return {
            'success': True,
            'city': city_name,
            'status': status,
            'message': f'Navigating to {city_name}...'
        }
    
    async def send_command_to_city(self, city_name: str, command: str) -> Dict[str, Any]:
        """Send a command to a city through routing system"""
        if not self.connected:
            return {
                'success': False,
                'message': 'Routing system not connected'
            }
        
        # Format command for routing system
        routing_data = {
            'city': city_name,
            'command': command,
            'timestamp': time.time(),
            'orchestral_enhanced': True
        }
        
        try:
            result = await receive_orchestral_data(routing_data)
            return {
                'success': result.get('status') == 'success',
                'result': result
            }
        except Exception as e:
            logger.error(f"Error sending command to city: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def get_routing_status(self) -> Dict[str, Any]:
        """Get overall routing system status"""
        if not ORCHESTRAL_AVAILABLE:
            return {
                'connected': False,
                'message': 'Orchestral channel not available'
            }
        
        try:
            status = get_arcade_platform_status()
            return {
                'connected': self.connected,
                'platform_status': status
            }
        except Exception as e:
            logger.error(f"Error getting routing status: {e}")
            return {
                'connected': False,
                'error': str(e)
            }
    
    def list_cities(self) -> list[str]:
        """List available cities"""
        return ['Echoes', 'Reverb', 'Delay']

