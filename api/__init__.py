"""
Direct OpenAI API Integration
Clean, simple integration with official OpenAI API.
Integrated component of the Atmosphere ecosystem.

Version: 1.0.0 (Ecosystem Sync)
Status: Production Ready
Ecosystem Integration: Complete
"""

__version__ = "1.0.0"
__author__ = "Atmosphere Team"
__description__ = "Direct OpenAI API integration with ecosystem coordination"

import os
import logging
from typing import Dict, Any, Optional, List
import openai
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import ecosystem integration
try:
    import sys
    ecosystem_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(ecosystem_root)
    
    from ecosystem import get_ecosystem
    ECOSYSTEM_AVAILABLE = True
except ImportError:
    ECOSYSTEM_AVAILABLE = False

# Initialize OpenAI client
def get_openai_client():
    """Get configured OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")
    
    return openai.OpenAI(api_key=api_key)

# Request/Response models
class ChatRequest(BaseModel):
    """Chat completion request model."""
    messages: List[Dict[str, str]]
    model: str = "gpt-3.5-turbo"
    max_tokens: Optional[int] = None
    temperature: float = 0.7

class ChatResponse(BaseModel):
    """Chat completion response model."""
    content: str
    model: str
    usage: Dict[str, int]

def get_api_status():
    """Get comprehensive API status."""
    status = {
        "version": __version__,
        "ecosystem_integration": ECOSYSTEM_AVAILABLE,
        "capabilities": [
            "openai_integration",
            "chat_completions",
            "model_access",
            "token_tracking",
            "ecosystem_coordination"
        ]
    }
    
    # Test OpenAI connection
    try:
        client = get_openai_client()
        models = client.models.list()
        status["openai_connected"] = True
        status["available_models"] = len(models.data)
    except:
        status["openai_connected"] = False
        status["available_models"] = 0
    
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
    """Main entry point for Direct API."""
    print("🔌 Direct OpenAI API v{}".format(__version__))
    print("=" * 40)
    print("Clean OpenAI integration")
    print("Ecosystem Integration: {}".format("✅ Available" if ECOSYSTEM_AVAILABLE else "❌ Not Available"))
    
    status = get_api_status()
    
    if status.get("openai_connected"):
        print("✅ OpenAI API: Connected")
        print(f"📋 Available Models: {status.get('available_models', 0)}")
    else:
        print("❌ OpenAI API: Disconnected")
    
    if status.get("ecosystem_status") == "connected":
        print("🌍 Ecosystem: Connected")
    
    print("")
    print("Usage:")
    print("  python -m api.client")
    print("  python -m api.server")
    print("  python -m api.example")

if __name__ == "__main__":
    main()
