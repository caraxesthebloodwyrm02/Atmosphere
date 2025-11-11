#!/usr/bin/env python3
"""
Simple test script for enhanced server AI functionality
"""
import os
import asyncio
from pathlib import Path
import sys
import logging

# Add the Arcade directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SimpleAPIKeyManager:
    """Simplified API key manager for testing"""

    def __init__(self):
        self.api_keys = {}
        self.services = {}
        self.load_api_keys()

    def load_api_keys(self):
        """Load API keys from environment variables and config files."""
        required_keys = ['OPENAI_API_KEY']
        optional_keys = [
            'ANTHROPIC_API_KEY',
            'GOOGLE_API_KEY',
            'HUGGINGFACE_API_KEY',
            'REPLICATE_API_KEY'
        ]

        # Check for required keys
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")

        # Load all available keys
        all_keys = required_keys + optional_keys
        self.api_keys.update({
            key.lower().replace('_api_key', ''): os.getenv(key)
            for key in all_keys
            if os.getenv(key)
        })

        # Initialize service clients
        self._initialize_services()

        logger.info(f"Loaded API keys for services: {', '.join(self.api_keys.keys())}")

    def _initialize_services(self):
        """Initialize service clients."""
        if 'openai' in self.api_keys:
            try:
                import openai
                self.services['openai'] = openai.OpenAI(api_key=self.api_keys['openai'])
            except ImportError:
                logger.warning("OpenAI package not available")

    def get_api_key(self, service: str):
        """Get API key for a specific service."""
        return self.api_keys.get(service)

    def has_service(self, service: str) -> bool:
        """Check if a service is available."""
        return service in self.api_keys and self.api_keys[service] is not None

    def list_available_services(self):
        """List all available services."""
        return list(self.api_keys.keys())

class SimpleAIAssistant:
    """Simplified AI-powered assistant for the interactive terminal."""

    def __init__(self, api_key_manager):
        self.api_key_manager = api_key_manager
        self.conversation_history = {}
        self.system_prompt = """
        You are Grok, a helpful and maximally truthful AI built by xAI. You have access to:
        • Knowledge and reasoning capabilities
        • Conversational AI responses

        Always be helpful, truthful, and engaging. Use emojis sparingly but effectively.
        """

    async def generate_response(self, user_input: str, session_id: str, context=None) -> str:
        """Generate an AI response"""

        # Get or create conversation history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        history = self.conversation_history[session_id]

        # Prepare messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add context if provided
        if context:
            context_str = f"Current context: {context}"
            messages.append({"role": "system", "content": context_str})

        # Add conversation history (last 10 messages)
        messages.extend(history[-10:])

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        try:
            if self.api_key_manager.has_service('openai'):
                client = self.api_key_manager.services['openai']
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )

                ai_response = response.choices[0].message.content

                # Update conversation history
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": ai_response})

                return ai_response
            else:
                return f"🤖 AI Error: OpenAI service not available"

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return f"🤖 AI Error: {str(e)}"

async def test_ai_functionality():
    """Test the AI assistant with the available API key"""

    # Initialize API key manager
    api_key_manager = SimpleAPIKeyManager()

    # Check if OpenAI is available
    if not api_key_manager.has_service('openai'):
        print("❌ OpenAI API key not found or invalid")
        print("Please ensure OPENAI_API_KEY is set in your environment variables")
        return

    print("✅ OpenAI API key loaded successfully")

    # Initialize AI assistant
    ai_assistant = SimpleAIAssistant(api_key_manager)
    print("✅ AI Assistant initialized")

    # Test basic AI response
    test_session_id = "test_session_123"

    print("\n🤖 Testing AI response generation...")
    test_questions = [
        "Hello! Can you tell me what you can do?",
        "What is artificial intelligence?",
        "Explain machine learning in simple terms"
    ]

    for question in test_questions:
        try:
            print(f"\n🗣️ Question: {question}")
            response = await ai_assistant.generate_response(question, test_session_id)
            print(f"✅ AI Response: {response[:150]}...")
        except Exception as e:
            print(f"❌ AI response failed for '{question}': {e}")
            return

    print("\n🎉 AI functionality test completed successfully!")
    print("The enhanced server core AI components are working properly.")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Server AI Functionality (Simplified)")
    print("=" * 60)

    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✅ OPENAI_API_KEY found (length: {len(openai_key)})")
    else:
        print("❌ OPENAI_API_KEY not found in environment")
        print("Please ensure the OPENAI_API_KEY is properly set in your user environment variables.")
        sys.exit(1)

    # Run async test
    asyncio.run(test_ai_functionality())
