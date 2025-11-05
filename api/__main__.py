#!/usr/bin/env python3
"""
Direct OpenAI API Main Entry Point
Run with: python -m api
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .client import test_api
from .server import run_server

def main():
    """Main entry point for Direct OpenAI API."""
    print("🔌 Direct OpenAI API v1.0.0")
    print("=" * 40)
    print("Clean OpenAI integration")
    print("")
    
    # Check API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY environment variable is required")
        print("💡 Set it in your environment or .env file")
        return
    
    # Test connection
    print("🔍 Testing OpenAI connection...")
    if test_api():
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")
        return
    
    print("")
    print("Usage:")
    print("  python -m api.client    # Test client")
    print("  python -m api.server    # Start server")
    print("  python -m api.example    # Run examples")
    print("")
    print("Server will start on: http://localhost:8000")
    print("API docs: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
