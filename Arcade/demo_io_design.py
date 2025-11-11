#!/usr/bin/env python3
"""
IO Design Integration Demo for User-System Correspondence & Continuous Improvement
==================================================================================

Demonstrate the IO-inspired design intelligence system for analyzing user-system
correspondence, making critical design decisions, and driving continuous improvement.

Features:
• Four-zone habitat model for system organization
• Geometric compass for user experience navigation
• User-system correspondence analysis
• Design decision-making framework
• Continuous improvement cycles
• Network visualization of user interactions
"""

import asyncio
import requests
import json
import time
from pathlib import Path
import sys

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

async def demo_io_design_integration():
    """Demonstrate IO design integration for user-system correspondence."""

    print("🎯 IO Design Integration Demo - User-System Correspondence & Continuous Improvement")
    print("=" * 85)

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

    # Demo 1: Correspondence Zones Overview
    print("\n1️⃣ User-System Correspondence Zones (IO Design Model)")
    print("-" * 55)
    try:
        response = requests.get(f"{base_url}/io/zones")
        if response.status_code == 200:
            zones_data = response.json()
            print(f"   🏠 Total Zones: {zones_data['total_zones']}")

            for zone_key, zone_info in zones_data['zones'].items():
                print(f"\n   🏠 {zone_info['name']}")
                print(f"      Nodes: {zone_info['node_count']}")
                print(f"      Description: {zone_info['description'][:100]}...")
        else:
            print(f"   ❌ Failed to get zones: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Zones check error: {e}")

    # Demo 2: Correspondence Network
    print("\n2️⃣ User-System Correspondence Network")
    print("-" * 38)
    try:
        response = requests.get(f"{base_url}/io/network")
        if response.status_code == 200:
            network = response.json()
            print("   🌐 Network Analysis:"            print(f"   🟢 Total Nodes: {network['metrics']['total_nodes']}")
            print(f"   🔗 Total Connections: {network['metrics']['total_connections']}")
            print(f"   📊 Network Density: {network['metrics']['density']:.3f}")
            print(f"   🔗 Avg Connections/Node: {network['metrics']['average_connections_per_node']:.1f}")

            print(f"\n   🏠 Zone Distribution:")
            for zone_name, count in network['metrics']['zone_distribution'].items():
                print(f"      {zone_name.replace('_', ' ').title()}: {count} nodes")
        else:
            print(f"   ❌ Failed to get network: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Network check error: {e}")

    # Demo 3: User Correspondence Analysis
    print("\n3️⃣ User-System Correspondence Analysis")
    print("-" * 38)
    try:
        user_id = "demo_user_correspondence"
        interaction_data = {
            "interactions": [
                {"component": "authentication", "frequency": 10, "satisfaction": 0.9, "success": True, "efficiency": 0.85},
                {"component": "navigation", "frequency": 20, "satisfaction": 0.8, "success": True, "efficiency": 0.75},
                {"component": "settings", "frequency": 5, "satisfaction": 0.7, "success": True, "efficiency": 0.70},
                {"component": "api_access", "frequency": 3, "satisfaction": 0.6, "success": False, "efficiency": 0.50},
                {"component": "advanced_tools", "frequency": 1, "satisfaction": 0.8, "success": True, "efficiency": 0.90}
            ]
        }

        response = requests.post(f"{base_url}/io/analyze/{user_id}", json=interaction_data)

        if response.status_code == 200:
            analysis = response.json()
            print("   🎯 Correspondence Analysis Complete!"            print(f"   👤 User ID: {analysis['user_id']}")
            print(f"   🎭 Primary Zone: {analysis['primary_zone'].replace('_', ' ').title()}")
            print(f"   🧭 Compass Position: ({analysis['compass_coordinates'][0]:.1f}, {analysis['compass_coordinates'][1]:.1f})")

            print(f"\n   📊 Zone Affinities:")
            for zone, affinity in analysis['zone_affinities'].items():
                print(f"      {zone.replace('_', ' ').title()}: {affinity:.1%}")

            print(f"\n   📈 Design Metrics:")
            for metric, value in analysis['design_metrics'].items():
                print(f"      {metric.replace('_', ' ').title()}: {value:.1%}")

            if analysis.get('improvement_suggestions'):
                print(f"\n   💡 Improvement Suggestions:")
                for suggestion in analysis['improvement_suggestions'][:3]:
                    print(f"      • {suggestion}")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Analysis error: {e}")

    # Demo 4: Compass Navigation
    print("\n4️⃣ Geometric Compass Navigation")
    print("-" * 32)
    try:
        navigation_data = {"target_zone": "bridge_territory"}

        response = requests.post(f"{base_url}/io/compass/{user_id}", json=navigation_data)

        if response.status_code == 200:
            navigation = response.json()
            print("   🧭 Compass Navigation Results:"            print(f"   🎯 Target Zone: {navigation['target_zone'].replace('_', ' ').title()}")
            print(f"   📍 Current Position: ({navigation['current_position'][0]:.1f}, {navigation['current_position'][1]:.1f})")
            print(f"   🎯 Target Position: ({navigation['target_position'][0]:.1f}, {navigation['target_position'][1]:.1f})")
            print(f"   📏 Distance: {navigation['distance']:.1f} units")
            print(f"   🧭 Bearing: {navigation['bearing']:.1f}° ({navigation['cardinal_direction']})")
            print(f"   💡 Navigation Hint: {navigation['navigation_hint']}")
            print(f"   📝 Zone Description: {navigation['zone_description']}")
        else:
            print(f"   ❌ Navigation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Navigation error: {e}")

    # Demo 5: Design Decision Making
    print("\n5️⃣ Critical Design Decision Making")
    print("-" * 35)
    try:
        decision_data = {
            "zone": "core_nexus",
            "decision_type": "interface_optimization",
            "context": {
                "current_metrics": {"usability": 0.75, "efficiency": 0.68},
                "user_feedback": ["navigation could be simpler", "need better error messages"],
                "stakeholders": ["end_users", "developers", "designers"]
            }
        }

        response = requests.post(f"{base_url}/io/decision", json=decision_data)

        if response.status_code == 200:
            decision = response.json()
            print("   🎯 Design Decision Made!"            print(f"   🆔 Decision ID: {decision['decision_id'][:8]}...")
            print(f"   🏠 Zone: {decision['zone'].replace('_', ' ').title()}")
            print(f"   🎯 Decision Type: {decision['decision_type'].replace('_', ' ').title()}")
            print(f"   📝 Rationale: {decision['rationale'][:100]}...")

            print(f"\n   📊 Impact Assessment:")
            for aspect, score in decision['impact_assessment'].items():
                print(f"      {aspect.replace('_', ' ').title()}: {score:.1%}")

            print(f"\n   📋 Implementation Plan:")
            for i, step in enumerate(decision['implementation_plan'][:3], 1):
                print(f"      {i}. {step}")

            print(f"\n   🎯 Success Metrics:")
            for metric in decision['success_metrics'][:2]:
                print(f"      • {metric}")
        else:
            print(f"   ❌ Decision making failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Decision error: {e}")

    # Demo 6: Continuous Improvement Cycle
    print("\n6️⃣ Continuous Improvement Cycle")
    print("-" * 32)
    try:
        cycle_data = {
            "zone": "hub_zone",
            "trigger_metrics": {
                "usability_score": 0.72,
                "efficiency_rating": 0.65,
                "user_satisfaction": 0.78,
                "error_rate": 0.12
            }
        }

        response = requests.post(f"{base_url}/io/cycle", json=cycle_data)

        if response.status_code == 200:
            cycle = response.json()
            print("   🔄 Improvement Cycle Started!"            print(f"   🆔 Cycle ID: {cycle['cycle_id']}")
            print(f"   🏠 Focus Zone: {cycle['zone_focus'].replace('_', ' ').title()}")
            print(f"   📊 Current Stage: {cycle['stage'].title()}")
            print(f"   🎯 Improvement Score: {cycle['improvement_score']:.1%}")

            print(f"\n   📈 Trigger Metrics:")
            for metric, value in cycle['trigger_metrics'].items():
                print(f"      {metric.replace('_', ' ').title()}: {value:.1%}")

            if cycle.get('actions_taken'):
                print(f"\n   ⚡ Actions Taken So Far:")
                for action in cycle['actions_taken'][:3]:
                    print(f"      • {action}")

            print(f"\n   ⏱️ Started: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(cycle['started_at']))}")
            print("   💡 The cycle will automatically progress through: Measure → Analyze → Design → Implement → Evaluate"
        else:
            print(f"   ❌ Improvement cycle failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cycle error: {e}")

    # Demo 7: Design Decisions History
    print("\n7️⃣ Design Decisions History")
    print("-" * 28)
    try:
        response = requests.get(f"{base_url}/io/decisions", params={"limit": 5})

        if response.status_code == 200:
            decisions_data = response.json()
            print(f"   📋 Total Decisions: {decisions_data['total_decisions']}")
            print(f"   📄 Returned: {decisions_data['returned_decisions']}")

            if decisions_data['decisions']:
                print(f"\n   🎯 Recent Decisions:")
                for decision in decisions_data['decisions'][-3:]:  # Show last 3
                    print(f"      • {decision['decision_type'].replace('_', ' ').title()}")
                    print(f"        Zone: {decision['zone'].replace('_', ' ').title()}")
                    print(f"        Priority: {decision['priority_level']}")
                    print(f"        Implemented: {'Yes' if decision['implemented'] else 'No'}")
        else:
            print(f"   ❌ Failed to get decisions: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Decisions error: {e}")

    # Demo 8: Improvement Cycles History
    print("\n8️⃣ Improvement Cycles History")
    print("-" * 31)
    try:
        response = requests.get(f"{base_url}/io/cycles", params={"limit": 5})

        if response.status_code == 200:
            cycles_data = response.json()
            print(f"   🔄 Total Cycles: {cycles_data['total_cycles']}")
            print(f"   📄 Returned: {cycles_data['returned_cycles']}")

            if cycles_data['cycles']:
                print(f"\n   🔄 Recent Cycles:")
                for cycle in cycles_data['cycles'][-3:]:  # Show last 3
                    status = "✅ Completed" if cycle['completed_at'] else f"📊 {cycle['stage'].title()}"
                    print(f"      • Zone: {cycle['zone_focus'].replace('_', ' ').title()}")
                    print(f"        Status: {status}")
                    print(f"        Score: {cycle['improvement_score']:.1%}")
                    print(f"        Actions: {cycle['actions_taken']}")
        else:
            print(f"   ❌ Failed to get cycles: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cycles error: {e}")

    print("\n🎉 IO Design Integration Demo Complete!")
    print("\n🎯 IO DESIGN PRINCIPLES FEATURES:")
    print("   • Four-zone habitat model for user-system organization")
    print("   • Geometric compass for user experience navigation")
    print("   • Real-time user-system correspondence analysis")
    print("   • Critical design decision-making framework")
    print("   • Continuous improvement cycles with automated progression")
    print("   • Network visualization of user interactions")
    print("   • Data-driven design metrics and optimization")
    print("   • Terminal command integration for design operations")
    print("\n🚀 IO Design principles are now fully integrated for enhanced user-system correspondence and continuous improvement!")

def show_terminal_commands():
    """Show terminal commands for IO design integration."""

    print("💻 IO Design Terminal Commands - User-System Correspondence & Continuous Improvement")
    print("=" * 90)
    print()

    print("Correspondence Analysis:")
    print("  io analyze                    # Analyze user-system correspondence")
    print("  io compass <zone>             # Navigate design compass to zone")
    print("  io network                    # View correspondence network")
    print("  io zones                      # List all correspondence zones")
    print()

    print("Design Decision Making:")
    print("  io decision <type> <zone>     # Make critical design decision")
    print("                                 # Types: interface_optimization, workflow_streamlining")
    print("                                 # Zones: core_nexus, hub_zone, bridge_territory, peripheral_expanse")
    print()

    print("Continuous Improvement:")
    print("  io cycle <zone>               # Start improvement cycle for zone")
    print()

    print("Available Zones:")
    print("  • core_nexus         - Primary user needs, critical functions")
    print("  • hub_zone           - Secondary interactions, supporting features")
    print("  • bridge_territory   - Connection points, integration layers")
    print("  • peripheral_expanse - Advanced features, extensibility")
    print()

    print("Design Decision Types:")
    print("  • interface_optimization     - Improve user interface design")
    print("  • workflow_streamlining      - Optimize user workflows")
    print("  • feature_enhancement        - Add or improve features")
    print("  • error_prevention          - Prevent user errors")
    print("  • performance_boost         - Improve system performance")
    print("  • user_education            - Better user guidance")
    print()

    print("Examples:")
    print("  # Analyze current user-system correspondence")
    print("  io analyze")
    print()
    print("  # Navigate to bridge territory zone")
    print("  io compass bridge_territory")
    print()
    print("  # Make interface optimization decision for core zone")
    print("  io decision interface_optimization core_nexus")
    print()
    print("  # Start improvement cycle for hub zone")
    print("  io cycle hub_zone")
    print()
    print("  # View correspondence zones")
    print("  io zones")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "commands":
        show_terminal_commands()
    else:
        asyncio.run(demo_io_design_integration())
