#!/usr/bin/env python3
"""
OpenAI API Client Onboarding
Simple setup and verification for new OpenAI API clients.
"""

import os
import asyncio
import json
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_api_key(api_key: str) -> dict:
    """Verify API key validity."""
    try:
        client = OpenAI(api_key=api_key)
        
        # Test with models endpoint
        models = client.models.list()
        
        return {
            "valid": True,
            "models_count": len(models.data),
            "message": "API key is valid"
        }
    except Exception as e:
        return {
            "valid": False,
            "error": str(e),
            "message": "API key is invalid or has issues"
        }

def get_client_info(api_key: str) -> dict:
    """Get client information and capabilities."""
    try:
        client = OpenAI(api_key=api_key)
        
        # Get available models
        models = client.models.list()
        model_list = [model.id for model in models.data]
        
        # Categorize models
        gpt_models = [m for m in model_list if 'gpt' in m.lower()]
        chat_models = [m for m in gpt_models if 'gpt-' in m]
        
        # Test a simple chat completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        return {
            "success": True,
            "total_models": len(model_list),
            "chat_models": len(chat_models),
            "primary_models": [m for m in chat_models if any(x in m for x in ['3.5', '4'])][:5],
            "test_response": response.choices[0].message.content,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def setup_client_config() -> dict:
    """Setup client configuration."""
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "default_model": "gpt-3.5-turbo",
        "max_tokens": 1000,
        "temperature": 0.7,
        "timeout": 30
    }
    
    return config

def save_onboarding_config(client_info: dict, config: dict) -> str:
    """Save onboarding configuration to file."""
    onboarding_data = {
        "timestamp": datetime.now().isoformat(),
        "client_info": client_info,
        "config": config,
        "status": "onboarded" if client_info.get("success") else "failed"
    }
    
    filename = f"openai_client_config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, 'w') as f:
        json.dump(onboarding_data, f, indent=2)
    
    return filename

def main():
    """Main onboarding function."""
    print("🚀 OpenAI API Client Onboarding")
    print("=" * 40)
    
    # Step 1: Check API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No API key found")
        print("💡 Please set OPENAI_API_KEY environment variable")
        print("   or create a .env file with your API key")
        return
    
    print(f"✅ API key found: {api_key[:10]}...{api_key[-4:]}")
    
    # Step 2: Verify API key
    print("\n🔍 Verifying API key...")
    verification = verify_api_key(api_key)
    
    if not verification["valid"]:
        print(f"❌ API key verification failed: {verification['error']}")
        return
    
    print(f"✅ API key verified - {verification['models_count']} models available")
    
    # Step 3: Get client info
    print("\n📊 Getting client information...")
    client_info = get_client_info(api_key)
    
    if not client_info["success"]:
        print(f"❌ Failed to get client info: {client_info['error']}")
        return
    
    print(f"✅ Client info retrieved")
    print(f"   • Total models: {client_info['total_models']}")
    print(f"   • Chat models: {client_info['chat_models']}")
    print(f"   • Primary models: {', '.join(client_info['primary_models'])}")
    print(f"   • Test response: '{client_info['test_response']}'")
    print(f"   • Token usage: {client_info['usage']['total_tokens']}")
    
    # Step 4: Setup configuration
    print("\n⚙️ Setting up client configuration...")
    config = setup_client_config()
    
    print("✅ Configuration created:")
    for key, value in config.items():
        if key == "api_key":
            print(f"   • {key}: {value[:10]}...{value[-4:]}")
        else:
            print(f"   • {key}: {value}")
    
    # Step 5: Save configuration
    print("\n💾 Saving onboarding configuration...")
    config_file = save_onboarding_config(client_info, config)
    print(f"✅ Configuration saved to: {config_file}")
    
    # Step 6: Final verification
    print("\n🎯 Final verification - testing direct communication...")
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=config["default_model"],
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Confirm you're ready for production use."}
            ],
            max_tokens=50,
            temperature=config["temperature"]
        )
        
        print(f"✅ Direct communication successful")
        print(f"🤖 Response: {response.choices[0].message.content}")
        print(f"📊 Tokens used: {response.usage.total_tokens}")
        
    except Exception as e:
        print(f"❌ Direct communication failed: {e}")
        return
    
    # Success message
    print("\n🎉 CLIENT ONBOARDING COMPLETE!")
    print("=" * 40)
    print("✅ API key verified and working")
    print("✅ Client information retrieved")
    print("✅ Configuration setup complete")
    print("✅ Direct communication tested")
    print("✅ Ready for production use")
    print(f"\n📄 Configuration file: {config_file}")
    print("\n🚀 You can now use the OpenAI API with:")
    print("   python -m api.client")
    print("   python -m api.server")

if __name__ == "__main__":
    main()
