#!/usr/bin/env python3
"""
Breakfast Assistant - Integrates Echoes Assistant with Breakfast Making
"""
import os
import asyncio
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    # Try to import from Echoes package
    from Echoes.assistant_v2_core import EchoesAssistantV2
except ImportError:
    # Fallback to local import if package structure is different
    try:
        sys.path.insert(0, str(Path(__file__).parent / 'Echoes'))
        from assistant_v2_core import EchoesAssistantV2
    except ImportError as e:
        print("Error: Could not import EchoesAssistantV2. Make sure the Echoes module is in your PYTHONPATH.")
        sys.exit(1)

try:
    from breakfast import ResilientBreakfastMaker, make_resilient_breakfast_sync
except ImportError:
    print("Error: Could not import breakfast module. Make sure it's in your PYTHONPATH.")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BreakfastAssistant:
    """Main assistant class for handling breakfast-related queries"""
    
    def __init__(self):
        try:
            self.assistant = EchoesAssistantV2(
                enable_tools=True,
                enable_rag=False,
                enable_streaming=False
            )
            self.breakfast_maker = ResilientBreakfastMaker()
        except Exception as e:
            logger.error(f"Failed to initialize BreakfastAssistant: {str(e)}")
            raise
        
    async def process_query(self, query: str) -> str:
        """Process user query and return response"""
        try:
            # Simple intent detection
            query_lower = query.lower()
            
            if any(word in query_lower for word in ["breakfast", "sandwich", "toast"]):
                return await self._handle_breakfast_request(query)
            else:
                return await self.assistant.process_query(query)
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return "I encountered an error while processing your request."

    async def _handle_breakfast_request(self, query: str) -> str:
        """Handle breakfast-specific requests"""
        try:
            print("\n🍳 Preparing your breakfast...")
            # Make breakfast and get metrics
            result = make_resilient_breakfast_sync()
            metrics = self.breakfast_maker.get_performance_summary()
            
            # Format response
            response = (
                f"🍳 Breakfast prepared successfully!\n"
                f"• Status: {result}\n"
                f"• Preparation Time: {metrics.get('avg_prep_time', 0):.2f}s\n"
                f"• Health Score: {metrics.get('health_score', 0):.1f}/10.0\n"
                f"• Resilience Applied: {metrics.get('resilience_applied', False)}"
            )
            return response
            
        except Exception as e:
            logger.error(f"Breakfast preparation failed: {str(e)}")
            return "I couldn't prepare breakfast. Please try again later."

async def main():
    """Main entry point"""
    print("\n" + "="*50)
    print("🍽️  Welcome to the Breakfast Assistant!")
    print("Type 'exit' to quit.")
    print("="*50 + "\n")
    
    try:
        assistant = BreakfastAssistant()
        
        while True:
            try:
                user_input = input("\nHow can I help you? > ").strip()
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\nGoodbye! 👋")
                    break
                    
                response = await assistant.process_query(user_input)
                print(f"\nAssistant: {response}")
                
            except KeyboardInterrupt:
                print("\nGoodbye! 👋")
                break
            except Exception as e:
                print(f"\nAn error occurred: {str(e)}")
                continue
                
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
