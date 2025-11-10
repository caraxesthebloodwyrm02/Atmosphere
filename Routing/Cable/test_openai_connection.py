#!/usr/bin/env python3
"""
Test OpenAI API connection and basic functionality.
"""
import asyncio
import os
from dotenv import load_dotenv
from src.openai_service import OpenAIService

async def test_openai_connection():
    """Test connection to OpenAI API."""
    try:
        print("🔍 Testing OpenAI API connection...")
        
        # Initialize the service
        service = OpenAIService()
        
        # Test embedding
        print("\n🔄 Testing embeddings...")
        embedding = await service.get_embedding("test connection")
        print(f"✅ Embedding received. Vector length: {len(embedding)}")
        
        # Test chat completion
        print("\n💬 Testing chat completion...")
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say 'connection successful'"}
        ]
        response = await service.get_chat_completion(messages)
        print(f"✅ Chat response: {response}")
        
        print("\n🎉 All tests passed! OpenAI connection is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check if OPENAI_API_KEY is set in your .env file")
        print("2. Verify your API key is valid and has sufficient credits")
        print("3. Check your internet connection")
        print("4. Make sure the OpenAI API is not experiencing any outages")

if __name__ == "__main__":
    # Load environment variables
    load_dotenv()
    
    # Run the test
    asyncio.run(test_openai_connection())
