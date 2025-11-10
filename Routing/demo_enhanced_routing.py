#!/usr/bin/env python3
"""
Enhanced Routing System Demonstration
======================================

Demonstrates the improved routing system with comprehensive test results,
enhanced metrics, and seamless navigation optimization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from acoustic_routing import AcousticRoutingNetwork
from us_highway_model import build_us_highway_network
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List
import time


def run_routing_tests(network: AcousticRoutingNetwork) -> Dict:
    """Run comprehensive routing tests and return results."""
    print("🔬 Running Routing System Tests")
    print("=" * 40)

    test_results = {
        'network_construction': False,
        'route_optimization': False,
        'multi_criteria_routing': False,
        'navigation_optimization': False,
        'performance_metrics': {}
    }

    # Test 1: Network Construction
    try:
        print("✓ Testing network construction...")
        assert len(network.graph.nodes) > 0, "Network has no nodes"
        assert len(network.graph.edges) > 0, "Network has no edges"
        test_results['network_construction'] = True
        print("  ✓ Network construction passed")
    except Exception as e:
        print(f"  ✗ Network construction failed: {e}")

    # Test 2: Route Optimization
    try:
        print("✓ Testing route optimization...")
        start, end = 'Delay', 'Echoes'  # Valid route exists
        criteria = ['distance', 'delay', 'reverb']

        for criterion in criteria:
            route = network.find_optimal_route(start, end, criterion)
            assert route is not None and len(route) > 1, f"Failed to find {criterion} route"
            assert route[0] == start and route[-1] == end, f"Invalid {criterion} route endpoints"

        test_results['route_optimization'] = True
        print("  ✓ Route optimization passed")
    except Exception as e:
        print(f"  ✗ Route optimization failed: {e}")

    # Test 3: Multi-Criteria Routing
    try:
        print("✓ Testing multi-criteria routing...")
        start, end = 'Delay', 'Echoes'  # Valid route exists
        criteria_weights = {'distance': 0.4, 'delay': 0.3, 'reverb': 0.2, 'smoothness': 0.1}

        route = network.find_multi_criteria_route(start, end, criteria_weights)
        assert route is not None and len(route) > 1, "Multi-criteria routing failed"

        test_results['multi_criteria_routing'] = True
        print("  ✓ Multi-criteria routing passed")
    except Exception as e:
        print(f"  ✗ Multi-criteria routing failed: {e}")

    # Test 4: Navigation Optimization
    try:
        print("✓ Testing navigation optimization...")
        preferences = {
            'speed_priority': 'balanced',
            'traffic_avoidance': 'medium',
            'route_type': 'efficient'
        }

        route, metrics = network.optimize_route_for_navigation('Delay', 'Echoes', preferences)
        assert route is not None and len(route) > 1, "Navigation optimization failed"
        assert 'optimization_score' in metrics, "Missing optimization metrics"

        test_results['navigation_optimization'] = True
        print("  ✓ Navigation optimization passed")
    except Exception as e:
        print(f"  ✗ Navigation optimization failed: {e}")

    # Performance Metrics
    print("✓ Measuring performance metrics...")
    start_time = time.time()

    # Run multiple routing operations
    operations = 100
    for _ in range(operations):
        network.find_optimal_route('Delay', 'Echoes', 'distance')

    end_time = time.time()
    total_time = end_time - start_time
    avg_time = total_time / operations

    test_results['performance_metrics'] = {
        'total_operations': operations,
        'total_time_seconds': total_time,
        'avg_time_per_operation': avg_time,
        'operations_per_second': operations / total_time
    }

    print(".4f")
    print(".2f")

    return test_results


def demonstrate_enhanced_metrics(network: AcousticRoutingNetwork):
    """Demonstrate enhanced routing metrics for seamless navigation."""
    print("\n📊 Enhanced Routing Metrics Demonstration")
    print("=" * 45)

    routes = [
        ('Delay', 'Routing'),
        ('Trajectory', 'Endpoint'),
        ('Network', 'Echoes'),
        ('Reverb', 'Orchestration')
    ]

    for start, end in routes:
        print(f"\n🏁 Route: {start} → {end}")
        print("-" * 30)

        # Get different route optimizations
        criteria = ['distance', 'delay', 'reverb']
        route_results = {}

        for criterion in criteria:
            route = network.find_optimal_route(start, end, criterion)
            if route:
                metrics = network.calculate_route_metrics(route)
                route_results[criterion] = {'route': route, 'metrics': metrics}

        # Display results in a formatted table
        print("Criterion    | Distance | Delay(ms) | Reverb | Efficiency | Smoothness | Reliability")
        print("-------------|----------|-----------|--------|------------|------------|------------")

        for criterion, data in route_results.items():
            m = data['metrics']
            print("12"
                  "8.1f"
                  "8.1f"
                  "8.3f"
                  "8.3f"
                  "8.3f")

        # Multi-criteria optimization
        print("\n🔄 Multi-Criteria Optimization:")
        multi_route = network.find_multi_criteria_route(start, end)
        if multi_route:
            multi_metrics = network.calculate_route_metrics(multi_route)
            print(f"  Route: {' → '.join(multi_route[:5])}{'...' if len(multi_route) > 5 else ''}")
            print(f"  Combined Score: {multi_metrics['path_efficiency']:.3f}")
            print(f"  Navigation Smoothness: {multi_metrics['navigation_smoothness']:.3f}")


def demonstrate_seamless_navigation(network: AcousticRoutingNetwork):
    """Demonstrate seamless navigation with user preferences."""
    print("\n🧭 Seamless Navigation Demonstration")
    print("=" * 40)

    scenarios = [
        {
            'name': 'Fastest Route',
            'preferences': {
                'speed_priority': 'fastest',
                'traffic_avoidance': 'low',
                'route_type': 'direct'
            }
        },
        {
            'name': 'Scenic Route',
            'preferences': {
                'speed_priority': 'scenic',
                'traffic_avoidance': 'medium',
                'route_type': 'scenic'
            }
        },
        {
            'name': 'Traffic-Avoiding Route',
            'preferences': {
                'speed_priority': 'balanced',
                'traffic_avoidance': 'high',
                'route_type': 'efficient'
            }
        }
    ]

    start, end = 'Delay', 'Echoes'  # Use valid route

    for scenario in scenarios:
        print(f"\n🎯 {scenario['name']}:")
        print("-" * 25)

        route, metrics = network.optimize_route_for_navigation(start, end, scenario['preferences'])

        if route:
            print(f"  Route: {' → '.join(route[:4])}{'...' if len(route) > 4 else ''}")
            print(".1f")
            print(".1f")
            print(f"  Optimization Score: {metrics.get('optimization_score', 0):.3f}")

            # Show applied preferences
            prefs = metrics.get('preferences_applied', {})
            weights = metrics.get('criteria_weights_used', {})
            print(f"  Preferences: Speed={prefs.get('speed_priority', 'N/A')}, "
                  f"Traffic={prefs.get('traffic_avoidance', 'N/A')}")
            print(f"  Weights: Distance={weights.get('distance', 0):.1f}, "
                  f"Delay={weights.get('delay', 0):.1f}, "
                  f"Reverb={weights.get('reverb', 0):.1f}")
        else:
            print("  ❌ No route found for these preferences")


def demonstrate_route_comparison(network: AcousticRoutingNetwork):
    """Demonstrate detailed route comparison with metrics."""
    print("\n⚖️ Route Comparison Analysis")
    print("=" * 30)

    start, end = 'Network', 'Echoes'

    # Get routes with different optimization criteria
    routes_data = {}
    criteria = ['distance', 'delay', 'reverb']

    for criterion in criteria:
        route = network.find_optimal_route(start, end, criterion)
        if route:
            metrics = network.calculate_route_metrics(route)
            routes_data[criterion] = {'route': route, 'metrics': metrics}

    if not routes_data:
        print("No routes found for comparison")
        return

    # Performance comparison
    print("📈 Performance Comparison:")
    print("Criterion | Length | Delay | Efficiency | Connectivity | Smoothness")
    print("----------|--------|-------|------------|--------------|-----------")

    for criterion, data in routes_data.items():
        m = data['metrics']
        print(f"{criterion.capitalize():<10}| {m['total_distance']:>6.1f} | {m['total_delay']:>6.1f} | {m['path_efficiency']:>10.3f} | {m['connectivity_score']:>12.3f} | {m['navigation_smoothness']:>10.3f}")

    # Route characteristics
    print("\n🛣️ Route Characteristics:")

    for criterion, data in routes_data.items():
        route = data['route']
        metrics = data['metrics']

        print(f"\n{criterion.capitalize()} Route:")
        print(f"  Path: {' → '.join(route[:6])}{'...' if len(route) > 6 else ''}")
        print(f"  Segments: {len(route)-1}")
        print(f"  Route Reliability: {metrics['route_reliability']:.3f}")
        print(f"  Feedback Factor: {metrics['avg_feedback_factor']:.3f} (detour options)")
        print(f"  Decay Factor: {metrics['avg_decay_factor']:.3f} (signal preservation)")


def main():
    """Main demonstration function."""
    print("🚗 Enhanced Acoustic Routing System")
    print("===================================")
    print("Demonstrating seamless navigation with optimized routes")
    print()

    # Build the highway network
    print("🏗️ Building U.S. Highway Network...")
    network = build_us_highway_network()
    print(f"✓ Network built with {len(network.graph.nodes)} cities and {len(network.graph.edges)} highway segments")

    # Run comprehensive tests
    test_results = run_routing_tests(network)

    # Calculate test summary
    passed_tests = sum(1 for result in test_results.values()
                      if isinstance(result, bool) and result)
    total_tests = sum(1 for result in test_results.values()
                     if isinstance(result, bool))

    print("\n📊 Test Results Summary:")
    print(f"  Passed: {passed_tests}/{total_tests} tests")

    if test_results['performance_metrics']:
        perf = test_results['performance_metrics']
        print(f"  Operations: {perf['total_operations']}")
        print(f"  Avg Time: {perf['avg_time_per_operation']:.4f}s per operation")

    # Demonstrations
    if all(test_results.get(key, False) for key in ['network_construction', 'route_optimization']):
        demonstrate_enhanced_metrics(network)
        demonstrate_seamless_navigation(network)
        demonstrate_route_comparison(network)
    else:
        print("\n⚠️ Skipping demonstrations due to test failures")

    print("\n🎉 Enhanced Routing System Demonstration Complete!")
    print("Seamless navigation and optimized routes are now available!")


if __name__ == "__main__":
    main()
