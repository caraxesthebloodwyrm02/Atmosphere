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
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import core components
from Echoes.assistant_v2_core import EchoesAssistantV2
from breakfast import ResilientBreakfastMaker, make_resilient_breakfast_sync

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BreakfastAssistant:
    """Main assistant class for handling breakfast-related queries"""
    
    def __init__(self):
        self.assistant = EchoesAssistantV2(
            enable_tools=True,
            enable_rag=False,
            enable_streaming=False
        )
        self.breakfast_maker = ResilientBreakfastMaker()
        
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
            # Make breakfast and get metrics
            result = make_resilient_breakfast_sync()
            metrics = self.breakfast_maker.get_performance_summary()
            
            # Format response
            response = (
                f"🍳 Breakfast prepared successfully!\n"
                f"• Status: {result}\n"
                f"• Preparation Time: {metrics['avg_prep_time']:.2f}s\n"
                f"• Health Score: {metrics['health_score']:.1f}/10.0\n"
                f"• Resilience Applied: {metrics['resilience_applied']}"
            )
            return response
            
        except Exception as e:
            logger.error(f"Breakfast preparation failed: {str(e)}")
            return "I couldn't prepare breakfast. Please try again later."

async def main():
    """Main entry point"""
    print("🍽️  Welcome to the Breakfast Assistant!")
    print("Type 'exit' to quit.\n")
    
    assistant = BreakfastAssistant()
    
    while True:
        try:
            user_input = input("\nHow can I help you? > ").strip()
            if user_input.lower() in ['exit', 'quit', 'bye']:
                print("Goodbye! 👋")
                break
                
            response = await assistant.process_query(user_input)
            print(f"\nAssistant: {response}")
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"\nAn error occurred: {str(e)}")
            continue

if __name__ == "__main__":
    asyncio.run(main())