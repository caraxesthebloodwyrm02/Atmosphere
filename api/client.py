#!/usr/bin/env python3
"""
Direct OpenAI API Client
Simple, clean integration with official OpenAI API.
Based on https://platform.openai.com/docs/overview
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
import openai
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectOpenAIClient:
    """Direct OpenAI API client with no middlewares."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI client."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        logger.info("OpenAI client initialized")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        max_tokens: Optional[int] = None,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Direct chat completion with OpenAI API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: OpenAI model to use
            max_tokens: Maximum tokens in response
            temperature: Response randomness (0.0-1.0)
        
        Returns:
            Response dictionary with content and metadata
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            result = {
                "content": response.choices[0].message.content,
                "model": response.model,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(f"Chat completion successful: {result['usage']['total_tokens']} tokens")
            return result
            
        except Exception as e:
            logger.error(f"Chat completion failed: {e}")
            raise
    
    async def simple_chat(self, prompt: str, model: str = "gpt-3.5-turbo") -> str:
        """
        Simple chat interface.
        
        Args:
            prompt: User prompt
            model: OpenAI model to use
        
        Returns:
            Response content as string
        """
        messages = [{"role": "user", "content": prompt}]
        response = await self.chat_completion(messages, model=model)
        return response["content"]
    
    async def get_models(self) -> List[str]:
        """Get available OpenAI models."""
        try:
            models = self.client.models.list()
            return [model.id for model in models.data]
        except Exception as e:
            logger.error(f"Failed to get models: {e}")
            return []
    
    def test_connection(self) -> bool:
        """Test connection to OpenAI API."""
        try:
            models = self.client.models.list()
            logger.info(f"Connection successful: {len(models.data)} models available")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# Global client instance
_client = None

def get_client() -> DirectOpenAIClient:
    """Get global OpenAI client instance."""
    global _client
    if _client is None:
        _client = DirectOpenAIClient()
    return _client

# Quick usage functions
async def chat(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Quick chat function."""
    client = get_client()
    return await client.simple_chat(prompt, model)

async def complete(messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
    """Quick completion function."""
    client = get_client()
    return await client.chat_completion(messages, **kwargs)

def test_api() -> bool:
    """Test API connection."""
    client = get_client()
    return client.test_connection()

if __name__ == "__main__":
    async def demo():
        """Demo of direct OpenAI API usage."""
        print("🔌 Direct OpenAI API Demo")
        print("=" * 40)
        
        # Test connection
        if not test_api():
            print("❌ Failed to connect to OpenAI API")
            return
        
        print("✅ Connected to OpenAI API")
        
        # Simple chat
        try:
            response = await chat("Hello! Can you explain what you are in one sentence?")
            print(f"\n🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Chat failed: {e}")
        
        # Get available models
        try:
            models = await get_client().get_models()
            print(f"\n📋 Available models: {len(models)}")
            for model in models[:5]:  # Show first 5
                print(f"  - {model}")
        except Exception as e:
            print(f"❌ Failed to get models: {e}")
    
    asyncio.run(demo())
