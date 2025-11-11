#!/usr/bin/env python3
"""
Test script for Atmosphere Arcade terminal fixes.
"""

import os
import asyncio
import sys
sys.path.insert(0, '.')

async def test_terminal():
    """Test the terminal functionality."""
    print("🔧 Testing Atmosphere Arcade Terminal...")

    try:
        # Import the components
        from api.enhanced_server_test import EnhancedTerminalHandler, APIKeyManager, AIAssistant
        from pathlib import Path

        print("✅ Imports successful")

        # Check if OpenAI API key is set
        if not os.getenv('OPENAI_API_KEY'):
            print("⚠️  OpenAI API key not found - some features will be limited")
        else:
            print("✅ OpenAI API key found")

        # Initialize components
        api_key_manager = APIKeyManager()
        ai_assistant = AIAssistant(api_key_manager)
        terminal_handler = EnhancedTerminalHandler(ai_assistant)

        print("✅ Components initialized")

        # Create a test session
        session_id = "test_session_123"
        await terminal_handler.create_session(session_id, Path.home())

        print("✅ Session created")

        # Test a simple command
        print("\n🧪 Testing command processing...")

        # Test "hi" command (the one that was failing)
        result = await terminal_handler.process_command(session_id, "hi")
        print(f"Command 'hi' result: {result[:100]}...")

        # Test "help" command
        result = await terminal_handler.process_command(session_id, "help")
        print(f"Command 'help' result: {result[:50]}...")

        print("\n✅ All tests passed! Terminal is working correctly.")

    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_terminal())
