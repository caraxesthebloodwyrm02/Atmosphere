#!/usr/bin/env python3
"""
Emotion-Enhanced Routing to Arcade Demonstration
================================================

Demonstrates using Cable's emotional intelligence to find the most stable
path to connect to the Arcade terminal system.
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


async def demonstrate_emotion_routing_to_arcade():
    """Demonstrate emotion-enhanced routing to Arcade."""
    print("🎭 Emotion-Enhanced Routing to Arcade")
    print("=" * 50)

    try:
        # Import the enhanced routing integration
        from Arcade.api.routing_integration import RoutingIntegration
        routing = RoutingIntegration()

        # Initialize the routing system
        print("🚀 Initializing emotion-enhanced routing...")
        init_success = await routing.emotion_routing.initialize() if routing.emotion_routing else False

        if not init_success:
            print("⚠️  Using fallback routing - emotion enhancements not available")
        else:
            print("✅ Emotion-enhanced routing initialized")

        # Test different emotional pathways to Arcade
        test_scenarios = [
            {
                'location': 'Delay',
                'emotion': 'exploratory',
                'description': 'Curious exploration'
            },
            {
                'location': 'Reverb',
                'emotion': 'creative',
                'description': 'Creative inspiration'
            },
            {
                'location': 'Echoes',
                'emotion': 'analytical',
                'description': 'Analytical investigation'
            },
            {
                'location': 'Delay',
                'emotion': 'urgent',
                'description': 'Urgent problem-solving'
            }
        ]

        print("\n🎯 Testing Emotional Pathways to Arcade:")
        print("-" * 45)

        for scenario in test_scenarios:
            print(f"\n📍 From {scenario['location']} ({scenario['description']})")

            # Find stable path
            result = await routing.find_stable_path_to_arcade(
                current_location=scenario['location'],
                user_emotion=scenario['emotion']
            )

            if result['success']:
                path_str = ' → '.join(result['stable_path'])
                stability = result['stability_score']

                print(f"   ✅ Path: {path_str}")
                print(".3f")
                print(f"   🎭 Emotion: {result.get('emotion_analysis', {}).get('query_emotion', 'unknown')}")

                # Show spatial positioning if available
                spatial = result.get('spatial_positioning', {})
                if spatial.get('available'):
                    positions = spatial.get('route_positions', [])
                    if positions:
                        start_pos = positions[0]['position']
                        end_pos = positions[-1]['position']
                        print(f"   📍 Spatial: ({start_pos[0]:.1f}, {start_pos[1]:.1f}, {start_pos[2]:.1f}) → "
                              f"({end_pos[0]:.1f}, {end_pos[1]:.1f}, {end_pos[2]:.1f})")

                # Show optimization criterion
                criterion = result.get('optimization_criterion', 'unknown')
                print(f"   🎯 Optimized by: {criterion}")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}")
                if 'fallback_path' in result:
                    fallback = ' → '.join(result['fallback_path'])
                    print(f"   🔄 Fallback: {fallback}")

        # Show stability report
        print("
📊 Connection Stability Report:"        print("-" * 35)

        stability_report = routing.get_stability_report()
        if stability_report.get('available'):
            print(f"   Total Connections: {stability_report['total_connections']}")
            print(f"   Average Stability: {stability_report['average_stability']:.3f}")
            print(f"   Success Rate: {(stability_report['successful_connections'] / stability_report['total_connections'] * 100):.1f}%")

            trend = stability_report.get('stability_trend', 'unknown')
            trend_emoji = {'improving': '📈', 'declining': '📉', 'stable': '➡️', 'insufficient_data': '❓'}
            print(f"   Trend: {trend_emoji.get(trend, '❓')} {trend.replace('_', ' ').title()}")

            if stability_report.get('most_stable_emotion'):
                print(f"   Most Stable Emotion: {stability_report['most_stable_emotion']}")
        else:
            print("   No stability data available")

        # Demonstrate navigation with emotion
        print("
🧭 Enhanced Navigation Demo:"        print("-" * 30)

        nav_commands = [
            ('cd Arcade', 'Delay', {'emotion': 'exploratory'}),
            ('cd arcade', 'Reverb', {'emotion': 'creative'}),
            ('navigate to arcade', 'Echoes', {'emotion': 'analytical'})
        ]

        for command, location, context in nav_commands:
            print(f"\n🎮 Command: '{command}' from {location}")

            nav_result = await routing.navigate_with_emotion(
                command=command,
                current_location=location,
                user_context=context
            )

            if nav_result['success']:
                print(f"   ✅ Navigation: {nav_result['navigation_type']}")
                if 'path' in nav_result:
                    path_str = ' → '.join(nav_result['path'])
                    print(f"   🛣️  Path: {path_str}")
                if 'stability_score' in nav_result:
                    print(".3f")
                if 'arrival_message' in nav_result:
                    print(f"   🎉 Message: {nav_result['arrival_message']}")
            else:
                print(f"   ❌ Result: {nav_result.get('message', 'Navigation failed')}")

        print("
🎉 Emotion-Enhanced Routing to Arcade Complete!"        print("Cable's emotional intelligence now powers stable Arcade connections!")

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()


async def demonstrate_routing_status():
    """Demonstrate routing system status and capabilities."""
    print("\n🔧 Routing System Status:")
    print("=" * 30)

    try:
        from Arcade.api.routing_integration import RoutingIntegration
        routing = RoutingIntegration()

        # Get emotion routing status
        emotion_status = await routing.get_emotion_routing_status()

        print("Emotion-Enhanced Routing:")
        print(f"   Available: {'✅' if emotion_status.get('available', False) else '❌'}")
        print(f"   Cable Integration: {'✅' if emotion_status.get('cable_available', False) else '❌'}")
        print(f"   Routing Integration: {'✅' if emotion_status.get('routing_available', False) else '❌'}")

        if emotion_status.get('available'):
            print(f"   Connection History: {emotion_status.get('connection_history', 0)}")
            print(f"   Emotional Awareness: {'✅' if emotion_status.get('emotional_awareness') else '❌'}")
            print(f"   Spatial Positioning: {'✅' if emotion_status.get('spatial_positioning') else '❌'}")
            print(f"   Stability Optimization: {'✅' if emotion_status.get('stability_optimization') else '❌'}")

        # Get standard routing status
        standard_status = routing.get_routing_status()
        print("
Standard Routing:"        print(f"   Connected: {'✅' if standard_status.get('connected', False) else '❌'}")
        print(f"   Orchestral Channel: {'✅' if 'ORCHESTRAL_AVAILABLE' in globals() and globals()['ORCHESTRAL_AVAILABLE'] else '❌'}")

        print("
🎮 Available Cities:"        cities = routing.list_cities()
        for city in cities:
            print(f"   • {city}")

    except Exception as e:
        print(f"❌ Error getting routing status: {e}")


def main():
    """Main demonstration function."""
    print("🎭 Cable-Powered Emotion Routing to Arcade")
    print("==========================================")
    print("Using emotional intelligence to find stable paths to Arcade")

    # Run async demonstrations
    asyncio.run(demonstrate_routing_status())
    asyncio.run(demonstrate_emotion_routing_to_arcade())


if __name__ == "__main__":
    main()
