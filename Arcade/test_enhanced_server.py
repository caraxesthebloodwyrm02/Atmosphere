#!/usr/bin/env python3
"""
Simple test script for enhanced server AI functionality
"""
import os
import asyncio
from pathlib import Path
import sys

# Add the Arcade directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from api.enhanced_server import APIKeyManager, AIAssistant
    print("✅ Successfully imported enhanced_server components")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

async def test_ai_functionality():
    """Test the AI assistant with the available API key"""

    # Initialize API key manager
    api_key_manager = APIKeyManager()

    # Check if OpenAI is available
    if not api_key_manager.has_service('openai'):
        print("❌ OpenAI API key not found or invalid")
        print("Please ensure OPENAI_API_KEY is set in your environment variables")
        return

    print("✅ OpenAI API key loaded successfully")

    # Initialize AI assistant
    ai_assistant = AIAssistant(api_key_manager)
    print("✅ AI Assistant initialized")

    # Test basic AI response
    test_session_id = "test_session_123"

    print("\n🤖 Testing AI response generation...")
    try:
        response = await ai_assistant.generate_response(
            "Hello! Can you tell me what you can do?",
            test_session_id
        )
        print(f"✅ AI Response successful:\n{response[:200]}...")
    except Exception as e:
        print(f"❌ AI response failed: {e}")
        return

    # Test specific command handlers
    print("\n🧠 Testing command handlers...")

    # Test Grokipedia (if available)
    if ai_assistant.grokipedia:
        print("📚 Grokipedia available - testing query...")
        try:
            grok_response = await ai_assistant._handle_grokipedia_command("grokipedia query artificial intelligence", test_session_id)
            print(f"✅ Grokipedia query successful:\n{grok_response[:100]}...")
        except Exception as e:
            print(f"⚠️ Grokipedia query failed (expected if service unavailable): {e}")
    else:
        print("📚 Grokipedia not available (expected)")

    # Test Claude (if available)
    if ai_assistant.claude_game_engine:
        print("🎮 Claude Game Engine available")
    else:
        print("🎮 Claude Game Engine not available (expected)")

    # Test ChatGPT (if available)
    if ai_assistant.chatgpt_manager:
        print("🌐 ChatGPT Manager available")
    else:
        print("🌐 ChatGPT Manager not available (expected)")

    print("\n🎉 Basic functionality test completed successfully!")
    print("The enhanced server should work with the available AI components.")

if __name__ == "__main__":
    print("🚀 Testing Enhanced Server AI Functionality")
    print("=" * 50)

    # Check environment variables
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        print(f"✅ OPENAI_API_KEY found (length: {len(openai_key)})")
    else:
        print("❌ OPENAI_API_KEY not found in environment")
        sys.exit(1)

    # Run async test
    asyncio.run(test_ai_functionality())
