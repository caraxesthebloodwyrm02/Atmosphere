#!/usr/bin/env python3
"""
Direct OpenAI API Example
Simple examples of using the direct OpenAI integration.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from client import DirectOpenAIClient, chat, test_api

async def simple_examples():
    """Simple usage examples."""
    print("🔌 Direct OpenAI API Examples")
    print("=" * 50)
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Please set OPENAI_API_KEY environment variable")
        return
    
    # Test connection
    print("1. Testing API connection...")
    if test_api():
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")
        return
    
    # Simple chat
    print("\n2. Simple chat example...")
    try:
        response = await chat("What is artificial intelligence in one sentence?")
        print(f"🤖 {response}")
    except Exception as e:
        print(f"❌ Chat failed: {e}")
    
    # Advanced chat with parameters
    print("\n3. Advanced chat with parameters...")
    try:
        client = DirectOpenAIClient()
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in simple terms."}
        ]
        response = await client.chat_completion(
            messages=messages,
            model="gpt-3.5-turbo",
            max_tokens=100,
            temperature=0.5
        )
        print(f"🤖 {response['content']}")
        print(f"📊 Usage: {response['usage']['total_tokens']} tokens")
    except Exception as e:
        print(f"❌ Advanced chat failed: {e}")
    
    # Get available models
    print("\n4. Getting available models...")
    try:
        client = DirectOpenAIClient()
        models = await client.get_models()
        print(f"📋 Found {len(models)} models")
        # Show GPT models
        gpt_models = [m for m in models if 'gpt' in m.lower()]
        print("🤖 GPT models:")
        for model in gpt_models[:5]:  # Show first 5
            print(f"  - {model}")
    except Exception as e:
        print(f"❌ Failed to get models: {e}")

async def conversation_example():
    """Example of a conversation."""
    print("\n\n💬 Conversation Example")
    print("=" * 30)
    
    try:
        client = DirectOpenAIClient()
        
        conversation = [
            {"role": "system", "content": "You are a helpful AI assistant."},
            {"role": "user", "content": "Hi! Can you help me understand Python?"},
            {"role": "assistant", "content": "Hello! I'd be happy to help you understand Python. What specific aspect would you like to know about?"},
            {"role": "user", "content": "What are Python decorators?"}
        ]
        
        response = await client.chat_completion(
            messages=conversation,
            model="gpt-3.5-turbo",
            max_tokens=150
        )
        
        print(f"🤖 Assistant: {response['content']}")
        print(f"📊 Tokens used: {response['usage']['total_tokens']}")
        
    except Exception as e:
        print(f"❌ Conversation failed: {e}")

if __name__ == "__main__":
    asyncio.run(simple_examples())
    asyncio.run(conversation_example())
