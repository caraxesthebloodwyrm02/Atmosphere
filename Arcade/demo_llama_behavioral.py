#!/usr/bin/env python3
"""
Llama Behavioral AI Integration Demo
=====================================

Demonstrate the advanced behavioral AI capabilities of the Llama integration
in the Enhanced Arcade Terminal, focusing on user interactions and behavioral
intelligence.
"""

import asyncio
import requests
import json
import time
from pathlib import Path
import sys

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_llama_behavioral():
    """Demonstrate Llama behavioral AI capabilities."""

    print("🦙 Llama Behavioral AI Integration Demo")
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

    # Demo 1: Start Behavioral Session
    print("\n1️⃣ Starting Behavioral AI Session")
    print("-" * 32)
    try:
        user_id = "demo_behavioral_user"
        session_data = {"user_id": user_id}

        response = requests.post(f"{base_url}/llama/session/start", data=session_data)

        if response.status_code == 200:
            session = response.json()
            print("   ✅ Behavioral AI Session Started!"            print(f"   👤 User ID: {session['user_id']}")
            print(f"   💬 Conversation Style: {session['conversation_style'].title()}")
            print(f"   🔢 Session Count: {session['session_count']}")
            print(f"   🎯 Preferred Patterns: {', '.join(session['preferred_patterns'][:2])}")
        else:
            print(f"   ❌ Failed to start session: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Session start error: {e}")
        return

    # Demo 2: Behavioral AI Interactions
    print("\n2️⃣ Behavioral AI Interactions")
    print("-" * 29)

    test_messages = [
        "I'm really frustrated with this coding problem. Can you help?",
        "Wow, that's amazing! Tell me more about AI!",
        "I don't understand this concept. Can you explain it simply?",
        "This is so interesting! What else can you show me?"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n   Test {i}: Behavioral Response Analysis")
        print(f"   📝 Message: \"{message}\"")

        try:
            interaction_data = {
                "user_id": user_id,
                "message": message
            }

            response = requests.post(f"{base_url}/llama/interaction", data=interaction_data)

            if response.status_code == 200:
                interaction = response.json()
                print(f"   🤖 Response Preview: {interaction['content'][:100]}...")
                print(f"   🎭 Emotional Tone: {interaction['emotional_tone'].title()}")
                print(f"   📊 Engagement Level: {interaction['engagement_level']:.1%}")
                print(f"   🔄 Adaptability Score: {interaction['adaptability_score']:.1%}")
                print(f"   💬 Conversation Style: {interaction['conversation_style'].title()}")

                if interaction.get('interaction_patterns'):
                    patterns = interaction['interaction_patterns'][:2]
                    print(f"   🎯 Detected Patterns: {', '.join(patterns)}")
            else:
                print(f"   ❌ Interaction failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ Interaction error: {e}")

    # Demo 3: Behavioral Analysis
    print("\n3️⃣ Behavioral Pattern Analysis")
    print("-" * 31)
    try:
        response = requests.get(f"{base_url}/llama/analysis/{user_id}")

        if response.status_code == 200:
            analysis = response.json()
            print("   🧠 Behavioral Analysis Results:"            print(f"   🎯 Dominant Pattern: {analysis['pattern_type'].replace('_', ' ').title()}")
            print(f"   😊 Emotional State: {analysis['emotional_state'].title()}")
            print(f"   📊 Average Engagement: {analysis['engagement_metrics']['average_engagement']:.1%}")
            print(f"   🔢 Total Interactions: {analysis['engagement_metrics']['total_interactions']}")
            print(f"   🎯 Confidence Score: {analysis['confidence_score']:.1%}")

            if analysis.get('adaptation_suggestions'):
                print(f"\n   💡 Adaptation Suggestions:")
                for suggestion in analysis['adaptation_suggestions'][:3]:
                    print(f"      • {suggestion}")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")

    # Demo 4: Llama Stack Management
    print("\n4️⃣ Llama Stack Management")
    print("-" * 26)
    try:
        response = requests.get(f"{base_url}/llama/stack/status")

        if response.status_code == 200:
            stack_status = response.json()
            print("   🏗️ Llama Stack Status:"            print(f"   📛 Stack Name: {stack_status['stack_name']}")
            print(f"   📊 Status: {stack_status['status']}")
            print(f"   👥 Active Users: {stack_status['active_users']}")
            print(f"   💬 Total Interactions: {stack_status['total_interactions']}")

            if stack_status.get('scaling_parameters'):
                scaling = stack_status['scaling_parameters']
                print(f"\n   ⚡ Performance Targets:")
                print(f"      Max Users: {scaling['max_concurrent_users']}")
                print(f"      Response Time: {scaling['response_time_target']}s")
                print(f"      Throughput: {scaling['throughput_target']} req/s")
        else:
            print(f"   ❌ Stack status failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stack status error: {e}")

    # Demo 5: Stack Scaling Analysis
    print("\n5️⃣ Stack Scaling Analysis")
    print("-" * 25)
    try:
        scaling_data = {"target_capacity": 2000}

        response = requests.post(f"{base_url}/llama/stack/scale", json=scaling_data)

        if response.status_code == 200:
            scaling = response.json()
            print("   ⚖️ Scaling Analysis Complete:"            print(f"   📊 Current Capacity: {scaling['current_capacity']}")
            print(f"   🎯 Target Capacity: {scaling['target_capacity']}")
            print(f"   🔄 Scaling Needed: {'Yes' if scaling['scaling_needed'] else 'No'}")

            if scaling.get('scaling_actions'):
                print(f"\n   ⚡ Recommended Actions:")
                for action in scaling['scaling_actions']:
                    print(f"      • {action}")
        else:
            print(f"   ❌ Scaling analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Scaling analysis error: {e}")

    # Demo 6: Behavioral Statistics
    print("\n6️⃣ Behavioral AI Statistics")
    print("-" * 27)
    try:
        response = requests.get(f"{base_url}/llama/behavioral/stats")

        if response.status_code == 200:
            stats = response.json()
            print("   📊 Behavioral AI Statistics:"            print(f"   👥 Total Users: {stats['total_users']}")
            print(f"   💬 Total Responses: {stats['total_responses']}")
            print(f"   🧠 Total Analyses: {stats['total_analyses']}")
            print(f"   📈 Average Engagement: {stats['average_engagement']:.1%}")

            if stats.get('emotional_distribution'):
                print(f"\n   😊 Emotional Distribution:")
                for emotion, count in stats['emotional_distribution'].items():
                    print(f"      {emotion.title()}: {count}")

            if stats.get('most_common_emotion'):
                print(f"   🎭 Most Common Emotion: {stats['most_common_emotion'].title()}")
        else:
            print(f"   ❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")

    # Demo 7: Active Users Overview
    print("\n7️⃣ Active Behavioral AI Users")
    print("-" * 30)
    try:
        response = requests.get(f"{base_url}/llama/users")

        if response.status_code == 200:
            users_data = response.json()
            print(f"   👥 Total Active Users: {users_data['total_users']}")

            if users_data['users']:
                print(f"\n   👤 User Profiles:")
                for user_id, user_info in list(users_data['users'].items())[:3]:  # Show first 3
                    print(f"      🆔 {user_id}:")
                    print(f"         Style: {user_info['conversation_style'].title()}")
                    print(f"         Sessions: {user_info['session_count']}")
                    print(f"         Patterns: {', '.join(user_info['preferred_patterns'][:2])}")
                    print(f"         Adaptation: {user_info['adaptation_score']:.1%}")
        else:
            print(f"   ❌ Users overview failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Users overview error: {e}")

    print("\n🎉 Llama Behavioral AI Integration Demo Complete!")
    print("\n🦙 LLAMA BEHAVIORAL AI FEATURES:")
    print("   • Adaptive behavioral responses based on user emotional state")
    print("   • Intelligent conversation pattern recognition and adaptation")
    print("   • Personality-driven AI interactions with customizable traits")
    print("   • Real-time engagement monitoring and optimization")
    print("   • Llama Stack integration for scalable AI development")
    print("   • Comprehensive behavioral analytics and insights")
    print("   • User profile evolution based on interaction history")
    print("\n🚀 Llama Behavioral AI is now fully integrated for intelligent, adaptive user interactions!")

def show_terminal_commands():
    """Show terminal commands for Llama behavioral AI."""

    print("💻 Llama Behavioral AI Terminal Commands")
    print("=" * 48)
    print()

    print("Session Management:")
    print("  llama session                    # Start behavioral AI session")
    print("  llama analyze                    # Analyze interaction patterns")
    print()

    print("Behavioral Configuration:")
    print("  llama behavior friendly 0.8      # Set behavioral trait strength")
    print("  llama behavior empathetic 0.9    # Adjust empathy level")
    print("  llama behavior enthusiastic 0.7  # Set enthusiasm level")
    print()

    print("Direct Interaction:")
    print("  llama interact <message>         # Interact with behavioral AI")
    print()

    print("Stack Management:")
    print("  llama stack status               # Check Llama Stack status")
    print("  llama stack scale 1500           # Analyze scaling to 1500 users")
    print("  llama stack optimize             # Optimize stack performance")
    print()

    print("Available Behavioral Traits:")
    print("  • friendly      - Approachable and warm communication")
    print("  • professional  - Formal and structured responses")
    print("  • enthusiastic  - Energetic and motivational tone")
    print("  • calm          - Peaceful and composed manner")
    print("  • witty         - Humorous and clever responses")
    print("  • empathetic    - Understanding and supportive")
    print("  • direct        - Straightforward and clear")
    print("  • creative      - Imaginative and innovative")
    print("  • analytical    - Logical and detailed explanations")
    print("  • supportive    - Encouraging and helpful")
    print()

    print("Examples:")
    print("  # Start a behavioral session")
    print("  llama session")
    print()
    print("  # Set a friendly communication style")
    print("  llama behavior friendly 0.9")
    print()
    print("  # Ask a question with behavioral adaptation")
    print("  llama interact I'm feeling stuck on this coding problem")
    print()
    print("  # Analyze your interaction patterns")
    print("  llama analyze")
    print()
    print("  # Check stack scaling needs")
    print("  llama stack scale 2000")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "commands":
        show_terminal_commands()
    else:
        asyncio.run(demo_llama_behavioral())
