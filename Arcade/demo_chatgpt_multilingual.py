#!/usr/bin/env python3
"""
ChatGPT Multilingual & Multimodal Integration Demo
===================================================

Demonstrate the advanced multilingual and multimodal capabilities
of the ChatGPT integration in the Enhanced Arcade Terminal.
"""

import asyncio
import requests
import json
import time
from pathlib import Path
import sys

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_chatgpt_multilingual():
    """Demonstrate ChatGPT multilingual capabilities."""

    print("🌐 ChatGPT Multilingual Integration Demo")
    print("=" * 45)

    base_url = "http://localhost:7681"

    # Check if server is running
    try:
        response = requests.get(f"{base_url}/arcade/status", timeout=5)
        if response.status_code != 200:
            print("❌ Enhanced Arcade Terminal not running!")
            print("Please start the server with: python -m arcade launch")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server!")
        print("Please start the server with: python -m arcade launch")
        return

    print("✅ Enhanced Arcade Terminal is running!")

    # Demo 1: Supported Languages
    print("\n1️⃣ Supported Languages")
    print("-" * 20)
    try:
        response = requests.get(f"{base_url}/chatgpt/languages")
        if response.status_code == 200:
            lang_data = response.json()
            print(f"   🌐 Total Supported Languages: {lang_data['total_languages']}")
            print("   📋 Language List:")

            # Show first 8 languages as examples
            for lang in lang_data['languages'][:8]:
                print(f"     • {lang['code']}: {lang['name']}")
            if len(lang_data['languages']) > 8:
                print(f"     ... and {len(lang_data['languages']) - 8} more")

        else:
            print(f"   ❌ Failed to get languages: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Language check error: {e}")

    # Demo 2: Start Multilingual Conversation
    print("\n2️⃣ Starting Multilingual Conversation")
    print("-" * 35)
    try:
        conversation_data = {
            "user_id": "demo_user_multilingual",
            "primary_language": "es"  # Spanish
        }

        response = requests.post(f"{base_url}/chatgpt/conversation/start", data=conversation_data)

        if response.status_code == 200:
            conv_data = response.json()
            conversation_id = conv_data['conversation_id']
            print("   ✅ Multilingual conversation started!"            print(f"   🆔 Conversation ID: {conversation_id}")
            print(f"   🌐 Primary Language: {conv_data['primary_language']}")
            print(f"   📚 Supported Languages: {', '.join(conv_data['supported_languages'][:3])}...")
            print(f"   🎭 Active Modalities: {', '.join(conv_data['active_modalities'])}")
        else:
            print(f"   ❌ Failed to start conversation: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Conversation start error: {e}")
        return

    # Demo 3: Multilingual Message Exchange
    print("\n3️⃣ Multilingual Message Exchange")
    print("-" * 32)
    try:
        # Send a message in Spanish
        message_data = {
            "conversation_id": conversation_id,
            "message": "¿Cómo puedo mejorar mi código de Python para que sea más eficiente?",
            "language": "es"
        }

        response = requests.post(f"{base_url}/chatgpt/message", data=message_data)

        if response.status_code == 200:
            msg_response = response.json()
            print("   📝 Question (Spanish): ¿Cómo puedo mejorar mi código de Python...?"            print(f"   🤖 Response Language: {msg_response['primary_language']}")
            print(f"   💬 Response Preview: {msg_response['content'][:150]}...")
            print(f"   🎯 Confidence: {msg_response['confidence_score']:.2%}")

            if msg_response.get('translated_versions'):
                translations = list(msg_response['translated_versions'].keys())
                print(f"   🌐 Available Translations: {', '.join(translations[:3])}")

            if msg_response.get('cultural_adaptations'):
                adaptations = msg_response['cultural_adaptations']
                if adaptations.get('communication_style'):
                    print(f"   🎭 Communication Style: {adaptations['communication_style']}")
        else:
            print(f"   ❌ Message failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Message exchange error: {e}")

    # Demo 4: Add Multiple Languages
    print("\n4️⃣ Adding Multiple Language Support")
    print("-" * 35)
    try:
        # Add French support
        lang_data = {
            "conversation_id": conversation_id,
            "language_code": "fr"
        }

        response = requests.post(f"{base_url}/chatgpt/language/add", data=lang_data)

        if response.status_code == 200:
            lang_result = response.json()
            print("   ✅ French language added!"            print(f"   🇫🇷 Language: {lang_result['added_language']}")
            print(f"   🆔 Conversation: {lang_result['conversation_id']}")
        else:
            print(f"   ❌ Failed to add language: {response.status_code}")

        # Add German support
        lang_data["language_code"] = "de"
        response = requests.post(f"{base_url}/chatgpt/language/add", data=lang_data)

        if response.status_code == 200:
            print("   ✅ German language added!")
        else:
            print("   ⚠️ German language addition failed")
    except Exception as e:
        print(f"   ❌ Language addition error: {e}")

    # Demo 5: Translation Service
    print("\n5️⃣ Real-Time Translation Service")
    print("-" * 32)
    try:
        translation_data = {
            "text": "Hello, how are you today?",
            "target_language": "es"
        }

        response = requests.post(f"{base_url}/chatgpt/translate", data=translation_data)

        if response.status_code == 200:
            trans_result = response.json()
            print("   📝 Original (English): Hello, how are you today?"            print(f"   🌐 Translated (Spanish): {trans_result['translated_text']}")
            print(f"   🎯 Target Language: {trans_result['target_language']}")
        else:
            print(f"   ❌ Translation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Translation error: {e}")

    # Demo 6: Conversation Status
    print("\n6️⃣ Conversation Status & Analytics")
    print("-" * 35)
    try:
        response = requests.get(f"{base_url}/chatgpt/conversation/{conversation_id}/status")

        if response.status_code == 200:
            status = response.json()
            print("   📊 Conversation Analytics:"            print(f"   🆔 Conversation ID: {status['conversation_id']}")
            print(f"   🌐 Primary Language: {status['primary_language']}")
            print(f"   📚 Supported Languages: {len(status['supported_languages'])}")
            print(f"   🎭 Active Modalities: {', '.join(status['active_modalities'])}")
            print(f"   💬 Message Count: {status['message_count']}")
            print(f"   💾 Translation Cache: {status['cache_size']} entries")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")

    # Demo 7: Code-Specific Interaction
    print("\n7️⃣ Code-Specific Multimodal Interaction")
    print("-" * 40)
    try:
        code_message = {
            "conversation_id": conversation_id,
            "message": "Can you help me optimize this Python function?\n\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    else:\n        return fibonacci(n-1) + fibonacci(n-2)",
            "modality": "code"
        }

        response = requests.post(f"{base_url}/chatgpt/message", data=code_message)

        if response.status_code == 200:
            code_response = response.json()
            print("   💻 Code Analysis Request:"            print("   📝 Function: Recursive Fibonacci implementation")
            print(f"   🤖 Response Type: {code_response['response_type']}")
            print(f"   💡 Content Preview: {code_response['content'][:120]}...")

            if code_response.get('multimodal_content') and code_response['multimodal_content'].get('code_examples'):
                print(f"   📋 Code Examples Provided: {len(code_response['multimodal_content']['code_examples'])}")
        else:
            print(f"   ❌ Code analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Code interaction error: {e}")

    print("\n🎉 ChatGPT Multilingual Integration Demo Complete!")
    print("\n🌐 MULTILINGUAL & MULTIMODAL FEATURES:")
    print("   • 20+ supported languages with real-time translation")
    print("   • Cultural adaptation for different communication styles")
    print("   • Multimodal support (text, code, images, audio)")
    print("   • Intelligent conversation management")
    print("   • Translation caching for performance")
    print("   • Code-specific analysis and optimization")
    print("   • RESTful API for programmatic access")
    print("   • Terminal command integration")
    print("\n🚀 ChatGPT is now fully integrated for global, multimodal AI interactions!")

def show_terminal_commands():
    """Show terminal commands for ChatGPT multilingual features."""

    print("💻 ChatGPT Multilingual Terminal Commands")
    print("=" * 45)
    print()

    print("Conversation Management:")
    print("  chatgpt start [language]      # Start conversation (e.g., 'chatgpt start es')")
    print("  chatgpt status                # Check conversation status")
    print("  chatgpt language <code>       # Switch primary language")
    print()

    print("Multilingual Communication:")
    print("  chatgpt ask <question>        # Ask in any supported language")
    print("  chatgpt translate <text> to <lang>  # Translate text")
    print()

    print("Supported Languages:")
    print("  English (en), Spanish (es), French (fr), German (de)")
    print("  Italian (it), Portuguese (pt), Russian (ru), Chinese (zh)")
    print("  Japanese (ja), Korean (ko), Arabic (ar), Hindi (hi)")
    print("  And many more...")
    print()

    print("Examples:")
    print("  # Start Spanish conversation")
    print("  chatgpt start es")
    print()
    print("  # Ask question in Spanish")
    print("  chatgpt ask ¿Cómo funciona el aprendizaje automático?")
    print()
    print("  # Translate to French")
    print("  chatgpt translate 'Hello world' to fr")
    print()
    print("  # Switch to German")
    print("  chatgpt language de")
    print()
    print("  # Get help")
    print("  chatgpt help")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "commands":
        show_terminal_commands()
    else:
        asyncio.run(demo_chatgpt_multilingual())
