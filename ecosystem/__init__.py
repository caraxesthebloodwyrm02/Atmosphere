"""
Atmosphere Ecosystem Integration
Shared integration layer for all Atmosphere components.
"""

__version__ = "1.0.0"
__author__ = "Atmosphere Team"
__description__ = "Cohesive ecosystem integration for all components"

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AtmosphereEcosystem:
    """Central ecosystem manager for all Atmosphere components."""
    
    def __init__(self):
        """Initialize the ecosystem."""
        self.components = {}
        self.api_client = None
        self.integration_status = {}
        self.health_metrics = {}
        
        logger.info("🌍 Initializing Atmosphere Ecosystem...")
    
    async def initialize_components(self):
        """Initialize all ecosystem components."""
        logger.info("🔧 Initializing ecosystem components...")
        
        # Initialize core components
        components_to_init = {
            "echoes": self._init_echoes,
            "delay": self._init_delay,
            "reverb": self._init_reverb,
            "routing": self._init_routing,
            "api": self._init_api
        }
        
        for component_name, init_func in components_to_init.items():
            try:
                logger.info(f"📦 Initializing {component_name}...")
                result = await init_func()
                self.components[component_name] = result
                self.integration_status[component_name] = "integrated"
                logger.info(f"✅ {component_name.title()} integrated successfully")
            except Exception as e:
                logger.error(f"❌ Failed to integrate {component_name}: {e}")
                self.integration_status[component_name] = "failed"
    
    async def _init_echoes(self) -> Dict[str, Any]:
        """Initialize EchoesAI component."""
        try:
            # Import Echoes
            import sys
            atmosphere_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.append(atmosphere_root)
            
            from Echoes import __version__ as echoes_version
            
            # Try to get core version
            try:
                from Echoes.echoes import __version__ as core_version
            except ImportError:
                core_version = "unknown"
            
            # Initialize Echoes with API integration
            echoes_config = {
                "version": echoes_version,
                "core_version": core_version,
                "api_integration": True,
                "status": "active",
                "capabilities": [
                    "selective_attention",
                    "resilience_monitoring",
                    "ai_research",
                    "pattern_detection"
                ]
            }
            
            # Connect to OpenAI API if available
            if self.api_client:
                echoes_config["openai_connected"] = True
                logger.info("🔌 Echoes connected to OpenAI API")
            
            return echoes_config
            
        except ImportError as e:
            raise Exception(f"Echoes not available: {e}")
    
    async def _init_delay(self) -> Dict[str, Any]:
        """Initialize Delay component."""
        try:
            from Delay import __version__ as delay_version
            
            delay_config = {
                "version": delay_version,
                "status": "active",
                "capabilities": [
                    "time_based_processing",
                    "audio_effects",
                    "delay_modulation"
                ],
                "api_integration": False
            }
            
            return delay_config
            
        except ImportError as e:
            raise Exception(f"Delay not available: {e}")
    
    async def _init_reverb(self) -> Dict[str, Any]:
        """Initialize Reverb component."""
        try:
            from Reverb import __version__ as reverb_version
            
            reverb_config = {
                "version": reverb_version,
                "status": "active",
                "capabilities": [
                    "spatial_audio",
                    "reverb_effects",
                    "audio_processing"
                ],
                "api_integration": False
            }
            
            return reverb_config
            
        except ImportError as e:
            raise Exception(f"Reverb not available: {e}")
    
    async def _init_routing(self) -> Dict[str, Any]:
        """Initialize Routing component with API integration."""
        try:
            from Routing import __version__ as routing_version
            from Routing.api_connector_main import test_routing_api
            
            routing_config = {
                "version": routing_version,
                "status": "active",
                "capabilities": [
                    "audio_routing",
                    "spatial_management",
                    "ai_optimization"
                ],
                "api_integration": True
            }
            
            # Test API connection
            if test_routing_api():
                routing_config["openai_connected"] = True
                logger.info("🔌 Routing connected to OpenAI API")
            else:
                routing_config["openai_connected"] = False
            
            return routing_config
            
        except ImportError as e:
            raise Exception(f"Routing not available: {e}")
    
    async def _init_api(self) -> Dict[str, Any]:
        """Initialize API component."""
        try:
            from api import __version__ as api_version
            from api.client import test_api
            
            api_config = {
                "version": api_version,
                "status": "active",
                "capabilities": [
                    "openai_integration",
                    "chat_completions",
                    "model_access",
                    "token_tracking"
                ],
                "direct_api": True
            }
            
            # Test API connection
            if test_api():
                api_config["openai_connected"] = True
                self.api_client = "connected"
                logger.info("🔌 Direct OpenAI API connected")
            else:
                api_config["openai_connected"] = False
            
            return api_config
            
        except ImportError as e:
            raise Exception(f"API not available: {e}")
    
    async def get_ecosystem_status(self) -> Dict[str, Any]:
        """Get comprehensive ecosystem status."""
        total_components = len(self.components)
        integrated_components = sum(1 for status in self.integration_status.values() if status == "integrated")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "ecosystem_version": __version__,
            "total_components": total_components,
            "integrated_components": integrated_components,
            "integration_rate": f"{(integrated_components/total_components)*100:.1f}%" if total_components > 0 else "0%",
            "components": self.components,
            "integration_status": self.integration_status,
            "api_connected": self.api_client is not None,
            "health": "healthy" if integrated_components == total_components else "partial"
        }
    
    async def sync_versions(self):
        """Sync all component versions to ecosystem standard."""
        logger.info("🔄 Syncing component versions...")
        
        target_version = "1.0.0"
        
        # Update version information
        for component_name, component_config in self.components.items():
            if component_config.get("status") == "active":
                component_config["ecosystem_version"] = target_version
                logger.info(f"📝 {component_name.title()} synced to ecosystem v{target_version}")
        
        logger.info("✅ Version synchronization complete")

# Global ecosystem instance
_ecosystem = None

def get_ecosystem() -> AtmosphereEcosystem:
    """Get global ecosystem instance."""
    global _ecosystem
    if _ecosystem is None:
        _ecosystem = AtmosphereEcosystem()
    return _ecosystem

async def initialize_ecosystem():
    """Initialize the complete ecosystem."""
    ecosystem = get_ecosystem()
    await ecosystem.initialize_components()
    await ecosystem.sync_versions()
    return ecosystem

def main():
    """Main entry point for ecosystem."""
    print("🌍 Atmosphere Ecosystem v{}".format(__version__))
    print("=" * 40)
    print("Cohesive integration layer")
    print("")
    print("Usage:")
    print("  python -m ecosystem.init")
    print("  python -m ecosystem.status")

if __name__ == "__main__":
    main()
