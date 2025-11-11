#!/usr/bin/env python3
"""
Claude Code Integration Demo
============================

Demonstrate the Claude-powered coding game mechanics and AI-assisted development
features integrated into the Enhanced Arcade Terminal.
"""

import asyncio
import requests
import json
import time
from pathlib import Path
import sys

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_claude_code_integration():
    """Demonstrate Claude Code integration features."""

    print("🎮 Claude Code Integration Demo")
    print("=" * 40)

    base_url = "http://localhost:7681"

    # Check if server is running
    try:
        response = requests.get(f"{base_url}/arcade/status", timeout=5)
        if response.status_code != 200:
            print("❌ Server not running. Please start the enhanced server first:")
            print("   python -m arcade launch")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the enhanced server first:")
        print("   python -m arcade launch")
        return

    print("✅ Server is running with Claude Code integration!")

    # Demo 1: Challenge Types
    print("\n1️⃣ Available Challenge Types")
    print("-" * 25)
    try:
        response = requests.get(f"{base_url}/claude/challenges/types")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {len(data['challenge_types'])} challenge types:")
            for challenge in data['challenge_types']:
                print(f"   • {challenge['name']}: {challenge['description']}")
        else:
            print(f"   ❌ Failed to get challenge types: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Challenge types error: {e}")

    # Demo 2: Start Coding Session
    print("\n2️⃣ Starting Claude Coding Session")
    print("-" * 32)
    try:
        user_id = "demo_user"
        response = requests.post(f"{base_url}/claude/session/start", data={"user_id": user_id})

        if response.status_code == 200:
            session_data = response.json()
            session_id = session_data['session_id']
            print("   ✅ Session started successfully!"            print(f"   Session ID: {session_id}")
            print(f"   User: {session_data['user_id']}")
            print(f"   Level: {session_data['level']}")
            print(f"   Score: {session_data['score']}")
            print(f"   State: {session_data['game_state']}")
        else:
            print(f"   ❌ Failed to start session: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Session start error: {e}")
        return

    # Demo 3: Generate Challenge
    print("\n3️⃣ Generating Coding Challenge")
    print("-" * 30)
    try:
        challenge_data = {
            "session_id": session_id,
            "challenge_type": "algorithm_puzzle",
            "difficulty": "medium"
        }

        response = requests.post(f"{base_url}/claude/challenge/generate", data=challenge_data)

        if response.status_code == 200:
            challenge = response.json()
            print("   ✅ Challenge generated!"            print(f"   Title: {challenge['title']}")
            print(f"   Type: {challenge['challenge_type']}")
            print(f"   Difficulty: {challenge['difficulty_level']}")
            print(f"   Points: {challenge['points_value']}")
            print(f"   Time Limit: {challenge['time_limit']} seconds")

            if challenge.get('starter_code'):
                print("   💻 Starter code available")
            if challenge.get('hints'):
                print(f"   💡 {len(challenge['hints'])} hints available")
        else:
            print(f"   ❌ Failed to generate challenge: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Challenge generation error: {e}")

    # Demo 4: Get Coding Assistance
    print("\n4️⃣ Claude Coding Assistance")
    print("-" * 25)
    try:
        assistance_data = {
            "session_id": session_id,
            "query": "how do I implement binary search in Python?",
            "code_context": "# I need to implement binary search\ndef binary_search(arr, target):\n    # TODO: implement"
        }

        response = requests.post(f"{base_url}/claude/assistance", data=assistance_data)

        if response.status_code == 200:
            assistance = response.json()
            print("   🤖 Claude Assistance Response:"            print(f"   Type: {assistance['response_type']}")
            content = assistance['content']
            print(f"   Content: {content[:200]}...")

            if assistance.get('code_suggestions'):
                print(f"   💻 {len(assistance['code_suggestions'])} code suggestions provided")
            if assistance.get('next_steps'):
                print(f"   🎯 {len(assistance['next_steps'])} next steps suggested")
        else:
            print(f"   ❌ Failed to get assistance: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Assistance error: {e}")

    # Demo 5: Submit Solution
    print("\n5️⃣ Submitting Code Solution")
    print("-" * 27)
    try:
        # Sample solution for the binary tree challenge
        sample_solution = '''
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution:
    def inorderTraversal(self, root: TreeNode) -> List[int]:
        result = []
        if root:
            result.extend(self.inorderTraversal(root.left))
            result.append(root.val)
            result.extend(self.inorderTraversal(root.right))
        return result

    def preorderTraversal(self, root: TreeNode) -> List[int]:
        result = []
        if root:
            result.append(root.val)
            result.extend(self.preorderTraversal(root.left))
            result.extend(self.preorderTraversal(root.right))
        return result

    def postorderTraversal(self, root: TreeNode) -> List[int]:
        result = []
        if root:
            result.extend(self.postorderTraversal(root.left))
            result.extend(self.postorderTraversal(root.right))
            result.append(root.val)
        return result
        '''

        solution_data = {
            "session_id": session_id,
            "code": sample_solution
        }

        response = requests.post(f"{base_url}/claude/solution/submit", data=solution_data)

        if response.status_code == 200:
            result = response.json()
            print("   ✅ Solution submitted!"            print(f"   Score: {result.get('score', 'N/A')}/100")
            print(f"   Time Taken: {result.get('time_taken', 'N/A')} seconds")
            print(f"   Feedback: {result.get('feedback', 'No feedback')[:100]}...")

            if result.get('new_achievements'):
                print(f"   🏆 New Achievements: {', '.join(result['new_achievements'])}")
        else:
            print(f"   ❌ Failed to submit solution: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Solution submission error: {e}")

    # Demo 6: Session Status
    print("\n6️⃣ Session Status Check")
    print("-" * 20)
    try:
        response = requests.get(f"{base_url}/claude/session/{session_id}/status")

        if response.status_code == 200:
            status = response.json()
            print("   📊 Current Session Status:"            print(f"   Score: {status['score']}")
            print(f"   Level: {status['level']}")
            print(f"   Game State: {status['game_state']}")
            print(f"   Time Elapsed: {status['time_elapsed']:.0f} seconds")
            print(f"   Claude Interactions: {status['claude_interactions']}")

            if status.get('achievements'):
                print(f"   🏆 Achievements: {', '.join(status['achievements'])}")
        else:
            print(f"   ❌ Failed to get status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")

    # Demo 7: User Statistics
    print("\n7️⃣ User Statistics")
    print("-" * 15)
    try:
        response = requests.get(f"{base_url}/claude/user/{user_id}/stats")

        if response.status_code == 200:
            stats = response.json()
            if "error" not in stats:
                print("   📈 User Progress:"                print(f"   Level: {stats['level']}")
                print(f"   Total Score: {stats['total_score']}")
                print(f"   Challenges Completed: {stats['challenges_completed']}")
                print(f"   Skills Mastered: {', '.join(stats['skills_mastered'][:3])}")
                print(f"   Streak Count: {stats['streak_count']}")

                if stats['achievements']:
                    print(f"   🏆 Achievements: {', '.join(stats['achievements'][:5])}")
            else:
                print(f"   User stats: {stats['error']}")
        else:
            print(f"   ❌ Failed to get user stats: {response.status_code}")
    except Exception as e:
        print(f"   ❌ User stats error: {e}")

    print("\n🎉 Claude Code Integration Demo Complete!")
    print("\n🎮 Claude Code Features:")
    print("   • AI-powered coding challenges with real-time evaluation")
    print("   • Intelligent code assistance and debugging help")
    print("   • Progressive difficulty and achievement system")
    print("   • Collaborative coding sessions with Claude")
    print("   • RESTful API for programmatic access")
    print("   • Terminal integration for seamless workflow")
    print("\n🚀 Claude Code is now fully integrated as a game mechanic!")

def show_terminal_commands():
    """Show terminal commands for Claude Code."""

    print("💻 Claude Code Terminal Commands")
    print("=" * 35)
    print()

    print("Session Management:")
    print("  claude start                    # Start coding session")
    print("  claude status                   # Check session status")
    print("  claude leaderboard              # View rankings")
    print()

    print("Challenge System:")
    print("  claude challenge algorithm_puzzle    # Generate algorithm challenge")
    print("  claude challenge code_optimization   # Generate optimization challenge")
    print("  claude challenge debugging_quest     # Generate debugging challenge")
    print("  claude challenge architecture_design # Generate design challenge")
    print("  claude challenge security_audit      # Generate security challenge")
    print()

    print("Coding Assistance:")
    print("  claude help \"debugging tips\"        # Get coding assistance")
    print("  claude help \"algorithm complexity\"  # Ask about concepts")
    print("  claude help \"design patterns\"       # Get design guidance")
    print()

    print("Solution Submission:")
    print("  claude submit \"def hello(): return 'Hello World!'\"  # Submit code solution")
    print()

    print("Examples:")
    print("  # Start a session")
    print("  claude start")
    print()
    print("  # Generate an algorithm challenge")
    print("  claude challenge algorithm_puzzle")
    print()
    print("  # Get help with debugging")
    print("  claude help \"how do I debug a recursive function?\"")
    print()
    print("  # Submit a solution")
    print("  claude submit \"def factorial(n): return 1 if n <= 1 else n * factorial(n-1)\"")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "commands":
        show_terminal_commands()
    else:
        asyncio.run(demo_claude_code_integration())
