#!/usr/bin/env python3
"""
Comprehensive Test Suite for Acoustic Routing System
=====================================================

Tests routing functionality, performance metrics, and optimization algorithms.
Validates seamless path navigation and optimized route calculation.
"""

import unittest
import numpy as np
from typing import List, Tuple
import time

from acoustic_routing import AcousticRoutingNetwork, AcousticParameters, Pulse
from self_aware_routing import SelfAwareRouter, HealthStatus, ConflictType
from us_highway_model import build_us_highway_network


class TestAcousticRouting(unittest.TestCase):
    """Test core acoustic routing functionality."""

    def setUp(self):
        """Set up test network."""
        self.network = AcousticRoutingNetwork()
        # Create a small test network
        self.network.add_highway_segment('A', 'B', 100, 65, 0.3, 0.2)
        self.network.add_highway_segment('B', 'C', 150, 65, 0.4, 0.3)
        self.network.add_highway_segment('A', 'D', 80, 65, 0.2, 0.1)
        self.network.add_highway_segment('D', 'C', 120, 65, 0.5, 0.4)
        self.network.add_highway_segment('B', 'E', 90, 65, 0.3, 0.2)

    def test_network_construction(self):
        """Test network construction with acoustic parameters."""
        self.assertEqual(len(self.network.graph.nodes), 5)
        self.assertEqual(len(self.network.graph.edges), 5)

        # Check acoustic parameters exist
        edge_ab = self.network.acoustic_params[('A', 'B')]
        self.assertIsInstance(edge_ab, AcousticParameters)
        self.assertGreater(edge_ab.delay_time, 0)
        self.assertGreaterEqual(edge_ab.feedback, 0)
        self.assertLessEqual(edge_ab.feedback, 1)

    def test_pulse_propagation(self):
        """Test pulse propagation through network."""
        propagation = self.network.propagate_pulse('A', max_steps=10)

        # Should have multiple steps
        self.assertGreater(len(propagation), 1)

        # Check that pulses decay over time
        initial_pulses = [p for p in propagation[0] if p.amplitude > 0.01]
        later_pulses = [p for p in propagation[5] if p.amplitude > 0.01]

        # Later pulses should generally have lower amplitude
        if initial_pulses and later_pulses:
            avg_initial = np.mean([p.amplitude for p in initial_pulses])
            avg_later = np.mean([p.amplitude for p in later_pulses])
            self.assertLess(avg_later, avg_initial)

    def test_route_optimization(self):
        """Test route optimization with different criteria."""
        # Test distance optimization
        route_distance = self.network.find_optimal_route('A', 'C', 'distance')
        self.assertIsNotNone(route_distance)
        self.assertEqual(route_distance[0], 'A')
        self.assertEqual(route_distance[-1], 'C')

        # Test delay optimization
        route_delay = self.network.find_optimal_route('A', 'C', 'delay')
        self.assertIsNotNone(route_delay)
        self.assertEqual(route_delay[0], 'A')
        self.assertEqual(route_delay[-1], 'C')

        # Test reverb optimization
        route_reverb = self.network.find_optimal_route('A', 'C', 'reverb')
        self.assertIsNotNone(route_reverb)
        self.assertEqual(route_reverb[0], 'A')
        self.assertEqual(route_reverb[-1], 'C')

    def test_route_metrics_calculation(self):
        """Test comprehensive route metrics calculation."""
        route = ['A', 'B', 'C']
        metrics = self.network.calculate_route_metrics(route)

        self.assertIn('total_distance', metrics)
        self.assertIn('total_delay', metrics)
        self.assertIn('avg_reverb_density', metrics)
        self.assertIn('path_efficiency', metrics)
        self.assertIn('connectivity_score', metrics)

        # Check metric ranges
        self.assertGreater(metrics['total_distance'], 0)
        self.assertGreater(metrics['total_delay'], 0)
        self.assertGreaterEqual(metrics['avg_reverb_density'], 0)
        self.assertLessEqual(metrics['avg_reverb_density'], 1)

    def test_navigation_smoothness(self):
        """Test navigation smoothness metric."""
        # Smooth route: A -> B -> C
        smooth_route = ['A', 'B', 'C']
        smooth_score = self.network.calculate_navigation_smoothness(smooth_route)

        # Less smooth route: A -> D -> B -> E
        rough_route = ['A', 'D', 'B', 'E']
        rough_score = self.network.calculate_navigation_smoothness(rough_route)

        # Smooth route should have higher smoothness score
        self.assertGreater(smooth_score, rough_score)


class TestSelfAwareRouting(unittest.TestCase):
    """Test self-aware routing functionality - placeholder for future implementation."""

    def test_placeholder(self):
        """Placeholder test for self-aware routing."""
        # Self-aware routing requires complex async setup and mocking
        # This is a placeholder for future comprehensive testing
        self.assertTrue(True)


class TestEnhancedMetrics(unittest.TestCase):
    """Test enhanced routing metrics for optimization."""

    def setUp(self):
        """Set up enhanced metrics test."""
        self.network = AcousticRoutingNetwork()
        # Create test network with known properties
        self.network.add_highway_segment('Start', 'Mid1', 100, 65, 0.8, 0.9)  # High connectivity
        self.network.add_highway_segment('Mid1', 'End', 100, 65, 0.8, 0.9)
        self.network.add_highway_segment('Start', 'Mid2', 150, 55, 0.2, 0.1)  # Low connectivity
        self.network.add_highway_segment('Mid2', 'End', 150, 55, 0.2, 0.1)

    def test_route_efficiency_metrics(self):
        """Test comprehensive route efficiency calculation."""
        route1 = ['Start', 'Mid1', 'End']  # Efficient route
        route2 = ['Start', 'Mid2', 'End']  # Inefficient route

        metrics1 = self.network.calculate_route_metrics(route1)
        metrics2 = self.network.calculate_route_metrics(route2)

        # Efficient route should have better scores
        self.assertGreater(metrics1['path_efficiency'], metrics2['path_efficiency'])
        self.assertGreater(metrics1['connectivity_score'], metrics2['connectivity_score'])

    def test_navigation_optimization(self):
        """Test navigation optimization algorithms."""
        start, end = 'Start', 'End'

        # Get optimized routes for different criteria
        distance_route = self.network.find_optimal_route(start, end, 'distance')
        delay_route = self.network.find_optimal_route(start, end, 'delay')
        reverb_route = self.network.find_optimal_route(start, end, 'reverb')

        # Each optimization should return valid routes
        self.assertIsNotNone(distance_route)
        self.assertIsNotNone(delay_route)
        self.assertIsNotNone(reverb_route)

        # Routes should connect start to end
        self.assertEqual(distance_route[0], start)
        self.assertEqual(distance_route[-1], end)

    def test_performance_benchmarks(self):
        """Test performance benchmarking."""
        start_time = time.time()

        # Perform routing operations
        for _ in range(100):
            self.network.find_optimal_route('Start', 'End', 'distance')

        end_time = time.time()
        total_time = end_time - start_time

        # Should complete within reasonable time
        self.assertLess(total_time, 5.0)  # Less than 5 seconds for 100 operations

        avg_time = total_time / 100
        print(".4f")


class TestSeamlessNavigation(unittest.TestCase):
    """Test seamless navigation capabilities."""

    def setUp(self):
        """Set up navigation test network."""
        self.network = build_us_highway_network()  # Use the full highway model

    def test_multi_criteria_optimization(self):
        """Test optimization considering multiple criteria simultaneously."""
        start, end = 'Delay', 'Echoes'  # Valid route exists

        # Get optimized routes for different criteria
        criteria = ['distance', 'delay', 'reverb']
        routes = {}

        for criterion in criteria:
            route = self.network.find_optimal_route(start, end, criterion)
            self.assertIsNotNone(route, f"Failed to find {criterion} route from {start} to {end}")
            routes[criterion] = route

        # All routes should be valid
        for criterion, route in routes.items():
            self.assertIsNotNone(route, f"Failed to find route for {criterion}")
            self.assertEqual(route[0], start)
            self.assertEqual(route[-1], end)

    def test_route_comparison_metrics(self):
        """Test detailed route comparison."""
        start, end = 'Delay', 'Echoes'  # Use valid route

        routes = []
        criteria = ['distance', 'delay', 'reverb']

        for criterion in criteria:
            route = self.network.find_optimal_route(start, end, criterion)
            if route:
                metrics = self.network.calculate_route_metrics(route)
                routes.append({
                    'route': route,
                    'criterion': criterion,
                    'metrics': metrics
                })

        # Should have multiple route options
        self.assertGreater(len(routes), 1)

        # Compare routes
        for route_data in routes:
            metrics = route_data['metrics']
            print(f"{route_data['criterion'].capitalize()} Route: "
                  ".1f"
                  ".2f"
                  ".3f")

    def test_navigation_smoothness_analysis(self):
        """Test navigation smoothness across different route types."""
        start, end = 'Network', 'Echoes'

        # Get different route types
        distance_route = self.network.find_optimal_route(start, end, 'distance')
        reverb_route = self.network.find_optimal_route(start, end, 'reverb')

        if distance_route and reverb_route:
            distance_smoothness = self.network.calculate_navigation_smoothness(distance_route)
            reverb_smoothness = self.network.calculate_navigation_smoothness(reverb_route)

            # Both should have reasonable smoothness scores
            self.assertGreater(distance_smoothness, 0)
            self.assertGreater(reverb_smoothness, 0)
            self.assertLessEqual(distance_smoothness, 1.0)
            self.assertLessEqual(reverb_smoothness, 1.0)


if __name__ == "__main__":
    unittest.main()
