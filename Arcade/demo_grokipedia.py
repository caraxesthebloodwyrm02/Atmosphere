#!/usr/bin/env python3
"""
Grokipedia Integration Demo
===========================

Demonstrate the integration of Grokipedia as a comprehensive knowledge library
into the Enhanced Arcade Terminal system.
"""

import asyncio
import requests
import json
from pathlib import Path
import sys

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_grokipedia_integration():
    """Demonstrate Grokipedia integration features."""

    print("📚 Grokipedia Integration Demo")
    print("=" * 40)

    base_url = "http://localhost:7681"

    # Check if server is running
    try:
        response = requests.get(f"{base_url}/grokipedia/status", timeout=5)
        if response.status_code != 200:
            print("❌ Server not running. Please start the enhanced server first:")
            print("   python -m arcade launch")
            return
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please start the enhanced server first:")
        print("   python -m arcade launch")
        return

    print("✅ Server is running with Grokipedia integration!")

    # Demo 1: System Status
    print("\n1️⃣ Grokipedia System Status")
    print("-" * 25)
    try:
        response = requests.get(f"{base_url}/grokipedia/status")
        if response.status_code == 200:
            status = response.json()
            print(f"   System: {status['system']}")
            print(f"   Status: {status['status']}")
            print(f"   Total Entries: {status['total_entries']}")
            print(f"   Categories: {len(status['categories'])}")
            print(f"   Features: {', '.join(status['features'])}")
        else:
            print(f"   ❌ Status check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Status check error: {e}")

    # Demo 2: Query Knowledge
    print("\n2️⃣ Knowledge Query - 'quantum mechanics'")
    print("-" * 35)
    try:
        response = requests.get(f"{base_url}/grokipedia/query", params={"q": "quantum mechanics"})
        if response.status_code == 200:
            result = response.json()
            print(f"   Query: '{result['query']}'")
            print(f"   Found: {result['total_found']} results")
            print(f"   Confidence: {result['confidence_score']:.1%}")
            print(f"   Returned: {result['returned']} results")

            if result['results']:
                entry = result['results'][0]
                print(f"\n   Top Result: {entry['title']}")
                print(f"   Category: {entry['category']}")
                print(f"   Difficulty: {entry['difficulty']}")
                print(f"   Preview: {entry['content_preview'][:100]}...")
        else:
            print(f"   ❌ Query failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Query error: {e}")

    # Demo 3: Concept Explanation
    print("\n3️⃣ Concept Explanation - Algorithm Complexity")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/grokipedia/explain/algorithm_complexity")
        if response.status_code == 200:
            explanation = response.json()
            print(f"   Concept: {explanation['title']}")
            print(f"   Category: {explanation['category']}")
            content = explanation['explanation']
            print(f"   Content Length: {len(content)} characters")
            print(f"   Preview: {content[:200]}...")
        else:
            print(f"   ❌ Explanation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Explanation error: {e}")

    # Demo 4: Categories
    print("\n4️⃣ Knowledge Categories")
    print("-" * 20)
    try:
        response = requests.get(f"{base_url}/grokipedia/categories")
        if response.status_code == 200:
            categories_data = response.json()
            print(f"   Total Categories: {categories_data['total_categories']}")
            print("   Category Breakdown:")
            for category, count in categories_data['stats'].items():
                print(f"     • {category.title()}: {count} entries")
        else:
            print(f"   ❌ Categories failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Categories error: {e}")

    # Demo 5: Related Concepts
    print("\n5️⃣ Related Concepts - Neural Networks")
    print("-" * 35)
    try:
        # First find a neural network concept
        response = requests.get(f"{base_url}/grokipedia/query", params={"q": "neural networks", "limit": 1})
        if response.status_code == 200:
            result = response.json()
            if result['results']:
                concept_id = result['results'][0]['id']
                print(f"   Found concept: {concept_id}")

                # Get related concepts
                response = requests.get(f"{base_url}/grokipedia/related/{concept_id}")
                if response.status_code == 200:
                    related = response.json()
                    print(f"   Direct relations: {len(related['related_concepts']['direct'])}")
                    print(f"   Indirect relations: {len(related['related_concepts']['indirect'])}")

                    if related['related_concepts']['direct']:
                        direct = related['related_concepts']['direct'][0]
                        print(f"   Example: {direct['title']} ({direct['category']})")
                else:
                    print(f"   ❌ Related concepts failed: {response.status_code}")
            else:
                print("   No neural network concepts found")
        else:
            print(f"   ❌ Related concepts query failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Related concepts error: {e}")

    # Demo 6: AI Assistant Integration
    print("\n6️⃣ AI Assistant + Grokipedia Integration")
    print("-" * 40)
    try:
        # Test if the AI assistant can access Grokipedia
        print("   Testing AI assistant Grokipedia integration...")
        print("   (This would be tested via WebSocket in a real terminal session)")
        print("   Commands available:")
        print("   • grokipedia query <topic>")
        print("   • grokipedia explain <concept>")
        print("   • grokipedia categories")
        print("   • ai ask 'explain quantum mechanics' (uses Grokipedia context)")
    except Exception as e:
        print(f"   ❌ AI integration test error: {e}")

    print("\n🎉 Grokipedia Integration Demo Complete!")
    print("\n📚 Grokipedia Features:")
    print("   • Comprehensive knowledge base with 7 major categories")
    print("   • Real-world programming examples and industry practices")
    print("   • RESTful API for programmatic access")
    print("   • Integrated with AI assistant for enhanced responses")
    print("   • Terminal commands for direct knowledge access")
    print("   • Related concept discovery and exploration")
    print("\n🚀 Grokipedia is now fully integrated into the Arcade Terminal!")

def show_usage_examples():
    """Show usage examples for Grokipedia."""

    print("📖 Grokipedia Usage Examples")
    print("=" * 30)
    print()

    print("🔍 Terminal Commands:")
    print("  grokipedia query 'machine learning'        # Search for topics")
    print("  grokipedia explain neural_networks_deep_learning  # Get detailed explanation")
    print("  grokipedia categories                        # List all categories")
    print()

    print("🌐 REST API Endpoints:")
    print("  GET /grokipedia/status                       # System status")
    print("  GET /grokipedia/query?q=quantum+physics      # Knowledge search")
    print("  GET /grokipedia/explain/{concept_id}         # Detailed explanation")
    print("  GET /grokipedia/categories                   # Category listing")
    print("  GET /grokipedia/related/{concept_id}         # Related concepts")
    print()

    print("🤖 AI Assistant Integration:")
    print("  ai ask 'explain algorithms'                  # AI uses Grokipedia context")
    print("  ai ask 'what is object oriented programming' # Enhanced with knowledge base")
    print()

    print("📊 Knowledge Categories:")
    print("  • Science: Physics, Chemistry, Biology, Astronomy")
    print("  • Mathematics: Algebra, Calculus, Statistics, Logic")
    print("  • Programming: Algorithms, Design Patterns, Languages")
    print("  • Technology: AI/ML, Systems, Architecture")
    print("  • Philosophy: Ethics, Logic, Reasoning")
    print("  • History: Scientific, Technological, Cultural")
    print("  • Psychology: Learning, Cognition, Behavior")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "examples":
        show_usage_examples()
    else:
        asyncio.run(demo_grokipedia_integration())
