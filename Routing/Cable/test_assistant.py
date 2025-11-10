"""
Test script for Cable Assistant

This script demonstrates how to use the CableAssistant class with both
the official OpenAI client and direct HTTP requests.
"""
import os
from dotenv import load_dotenv
from src.assistant import CableAssistant, HTTPClientConfig

def test_chat(use_http: bool = False):
    """Test the chat functionality.
    
    Args:
        use_http: If True, use direct HTTP requests instead of the official client
    """
    print(f"\n{'='*50}")
    print(f"Testing chat with {'HTTP' if use_http else 'official client'}")
    print(f"{'='*50}")
    
    # Initialize the assistant
    config = None
    if use_http:
        config = HTTPClientConfig(api_key=os.getenv('OPENAI_API_KEY'))
    
    assistant = CableAssistant(
        model="gpt-3.5-turbo",
        temperature=0.7,
        use_http=use_http,
        http_config=config
    )
    
    # Test simple chat
    print("\nTesting simple chat...")
    response = assistant.chat("Hello, how are you?")
    print(f"Assistant: {response.content}")
    
    # Test chat with system prompt
    print("\nTesting chat with system prompt...")
    response = assistant.chat(
        "What's the weather like?",
        system_prompt="You are a helpful assistant that knows about weather."
    )
    print(f"Assistant: {response.content}")
    
    # Test streaming
    print("\nTesting streaming chat...")
    print("Assistant: ", end="", flush=True)
    for chunk in assistant.stream_chat("Tell me a short story about a robot."):
        print(chunk, end="", flush=True)
    print("\n")

def main():
    # Load environment variables
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment variables")
        return
    
    # Test with official client
    test_chat(use_http=False)
    
    # Test with direct HTTP
    test_chat(use_http=True)

if __name__ == "__main__":
    main()
