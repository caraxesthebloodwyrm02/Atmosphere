#!/usr/bin/env python3
"""
Enhanced Arcade Terminal Demo
============================

Demonstration script showing the AI-powered features of the Enhanced Arcade Terminal.
"""

import time
import requests
import json
from pathlib import Path

def demo_ai_features():
    """Demonstrate AI features of the enhanced terminal."""
    print("🎮 Enhanced Arcade Terminal - AI Features Demo")
    print("=" * 50)

    base_url = "http://localhost:7681"

    # Check if server is running
    try:
        response = requests.get(f"{base_url}/arcade/status")
        if response.status_code != 200:
            print("❌ Server not running. Please start the enhanced server first:")
            print("   python -m arcade launch")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the enhanced server first:")
        print("   python -m arcade launch")
        return

    print("✅ Server is running!")

    # Demo 1: Check AI status
    print("\n🤖 Demo 1: AI System Status")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/arcade/ai/status")
        if response.status_code == 200:
            status = response.json()
            print("✅ AI Status retrieved:")
            print(f"   • Services available: {status.get('ai_services', [])}")
            print("   • Enhanced features: conversation_mode, learning_insights, command_explanation"
        else:
            print("⚠️  AI status check failed - API keys may not be configured")
    except Exception as e:
        print(f"❌ AI status check failed: {e}")

    # Demo 2: Learning Companion API
    print("\n🎓 Demo 2: Learning Companion API")
    print("-" * 35)
    try:
        response = requests.get(f"{base_url}/learning/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Learning API accessible:")
            print(f"   • Message: {data.get('message', 'N/A')}")
            endpoints = data.get('endpoints', [])
            print(f"   • Available endpoints: {len(endpoints)}")
            for endpoint in endpoints[:3]:  # Show first 3
                print(f"     - {endpoint['method']} {endpoint['path']}")
            if len(endpoints) > 3:
                print(f"     ... and {len(endpoints) - 3} more")
        else:
            print("❌ Learning API not accessible")
    except Exception as e:
        print(f"❌ Learning API check failed: {e}")

    # Demo 3: Start a learning session
    print("\n📚 Demo 3: Starting Learning Session")
    print("-" * 38)
    try:
        session_data = {
            "learner_id": "demo_user",
            "topic": "python_functions"
        }
        response = requests.post(
            f"{base_url}/learning/session/start",
            json=session_data,
            headers={"Content-Type": "application/json"}
        )

        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                session_id = result["data"]["session_id"]
                print("✅ Learning session started:")
                print(f"   • Session ID: {session_id}")
                print(f"   • Topic: {result['data']['welcome_message'][:50]}...")
                print(f"   • Status: {result['data']['status']}")

                # Demo 4: Process an interaction
                print("\n🎯 Demo 4: Processing Learning Interaction")
                print("-" * 42)
                interaction_data = {
                    "session_id": session_id,
                    "interaction_type": "correct_answer",
                    "interaction_data": {
                        "response_time": 2.5,
                        "confidence": 0.9,
                        "frustration_level": 0.1,
                        "topic": "python_functions"
                    }
                }

                response = requests.post(
                    f"{base_url}/learning/interact",
                    json=interaction_data,
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ Interaction processed successfully!")
                        adaptation = result["data"].get("adaptation_type", "none")
                        print(f"   • Adaptation triggered: {adaptation}")
                    else:
                        print("❌ Interaction processing failed")
                else:
                    print(f"❌ Interaction request failed: {response.status_code}")

                # Demo 5: End session
                print("\n🏁 Demo 5: Ending Learning Session")
                print("-" * 35)
                response = requests.post(f"{base_url}/learning/session/end/{session_id}")

                if response.status_code == 200:
                    result = response.json()
                    if result.get("success"):
                        print("✅ Session ended successfully!")
                        print("   • Comprehensive feedback generated")
                    else:
                        print("❌ Session ending failed")
                else:
                    print(f"❌ End session request failed: {response.status_code}")

            else:
                print("❌ Failed to start learning session")
        else:
            print(f"❌ Session start failed: {response.status_code} - {response.text}")

    except Exception as e:
        print(f"❌ Demo failed: {e}")

    print("\n🎉 Demo Complete!")
    print("\n💡 To explore more features:")
    print("   • Open http://localhost:7681 in your browser")
    print("   • Try AI commands: ai help, ai ask 'what is python?'")
    print("   • Access API docs: http://localhost:7681/docs")
    print("   • Check learning companion: http://localhost:7681/learning/")

def show_setup_instructions():
    """Show setup instructions."""
    print("🔧 Enhanced Arcade Terminal Setup Instructions")
    print("=" * 45)
    print()
    print("1. Install dependencies:")
    print("   pip install -r requirements.txt")
    print()
    print("2. Setup API keys (for AI features):")
    print("   python api_key_manager.py setup")
    print()
    print("3. Launch the enhanced server:")
    print("   python -m arcade launch")
    print()
    print("4. Run this demo:")
    print("   python enhanced_demo.py")
    print()
    print("5. Access the terminal:")
    print("   http://localhost:7681")
    print()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        show_setup_instructions()
    else:
        demo_ai_features()
