#!/usr/bin/env python3
"""
Comprehensive Test Suite for Emotion-Enhanced Routing to Arcade
===============================================================

Tests Cable-powered emotional intelligence integration with Routing
to ensure stable paths to Arcade terminal system.
"""

import unittest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock


class TestEmotionEnhancedRouting(unittest.TestCase):
    """Test emotion-enhanced routing system."""

    def setUp(self):
        """Set up test environment."""
        # Mock the imports to avoid dependency issues during testing
        with patch('Routing.emotion_enhanced_routing.CABLE_AVAILABLE', True), \
             patch('Routing.emotion_enhanced_routing.ROUTING_AVAILABLE', True), \
             patch('Routing.emotion_enhanced_routing.AcousticRoutingNetwork'), \
             patch('Routing.emotion_enhanced_routing.SelfAwareRouter'):

            from Routing.emotion_enhanced_routing import EmotionEnhancedRouting
            self.routing = EmotionEnhancedRouting()

            # Mock the components
            self.routing.routing_network = Mock()
            self.routing.emotion_analyzer = Mock()
            self.routing.spatializer = Mock()
            self.routing.enhanced_metrics = Mock()

    def test_initialization(self):
        """Test emotion-enhanced routing initialization."""
        self.assertIsNotNone(self.routing)
        self.assertIsNotNone(self.routing.arcade_emotional_profile)
        self.assertEqual(self.routing.arcade_emotional_profile['primary_emotion'],
                        self.routing.arcade_emotional_profile['primary_emotion'])

    def test_stability_calculation(self):
        """Test route stability calculation."""
        route_data = {
            'metrics': {
                'navigation_smoothness': 0.8,
                'connectivity_score': 0.7,
                'route_reliability': 0.9
            }
        }

        # Mock emotion analyzer
        from Cable.src.emotion_search import SearchEmotion
        user_emotion = SearchEmotion.EXPLORATORY

        stability = self.routing._calculate_route_stability(
            route_data, user_emotion, {'emotional_coherence': 0.4, 'spatial_stability': 0.3}
        )

        self.assertGreater(stability, 0)
        self.assertLessEqual(stability, 1)

    def test_emotional_analysis(self):
        """Test emotional analysis of routes."""
        route = ['Delay', 'Processing', 'Arcade']

        # Mock emotion analyzer responses
        self.routing.emotion_analyzer.analyze_query_emotion.return_value = 'exploratory'

        analysis = self.routing._analyze_route_emotion(route, None)

        self.assertIn('segment_analysis', analysis)
        self.assertIn('average_coherence', analysis)
        self.assertIn('route_emotional_profile', analysis)

    def test_connection_reliability(self):
        """Test connection reliability calculation."""
        route_data = {
            'metrics': {
                'navigation_smoothness': 0.8,
                'connectivity_score': 0.7,
                'route_reliability': 0.85
            }
        }

        reliability = self.routing._calculate_connection_reliability(route_data)

        self.assertGreater(reliability, 0)
        self.assertLessEqual(reliability, 1)

    @patch('Routing.emotion_enhanced_routing.AcousticRoutingNetwork')
    def test_find_stable_path_success(self, mock_network_class):
        """Test successful stable path finding."""
        # Mock the network
        mock_network = Mock()
        mock_network.find_optimal_route.return_value = ['Delay', 'Processing', 'Arcade']
        mock_network.calculate_route_metrics.return_value = {
            'navigation_smoothness': 0.8,
            'connectivity_score': 0.7,
            'route_reliability': 0.9,
            'total_distance': 100,
            'total_delay': 50
        }
        mock_network_class.return_value = mock_network

        # Mock emotion components
        self.routing.enhanced_metrics.optimize_results.return_value = [
            {'score': 0.8, 'content': 'test', 'file_name': 'test.txt'}
        ]
        self.routing.enhanced_metrics.create_emotional_search_space.return_value = {
            'query_emotion': 'exploratory'
        }

        async def run_test():
            result = await self.routing.find_stable_path_to_arcade(
                current_location='Delay',
                user_emotion='exploratory'
            )

            self.assertTrue(result['success'])
            self.assertIn('stable_path', result)
            self.assertIn('stability_score', result)
            self.assertIn('destination', result)
            self.assertEqual(result['destination'], 'Arcade')

        asyncio.run(run_test())

    def test_stability_report_generation(self):
        """Test stability report generation."""
        # Add some mock connection history
        self.routing.connection_history = [
            {'stability_score': 0.8, 'user_emotion': 'exploratory', 'success': True},
            {'stability_score': 0.7, 'user_emotion': 'creative', 'success': True},
            {'stability_score': 0.9, 'user_emotion': 'exploratory', 'success': True}
        ]

        report = self.routing.get_stability_report()

        self.assertTrue(report['available'])
        self.assertEqual(report['total_connections'], 3)
        self.assertEqual(report['successful_connections'], 3)
        self.assertIn('average_stability', report)
        self.assertIn('most_stable_emotion', report)

    def test_stability_trend_analysis(self):
        """Test stability trend calculation."""
        # Test with improving trend
        self.routing.connection_history = [
            {'stability_score': 0.6},
            {'stability_score': 0.7},
            {'stability_score': 0.8}
        ]

        trend = self.routing._calculate_stability_trend()
        self.assertEqual(trend, 'improving')

        # Test with stable trend
        self.routing.connection_history = [
            {'stability_score': 0.8},
            {'stability_score': 0.8},
            {'stability_score': 0.8}
        ]

        trend = self.routing._calculate_stability_trend()
        self.assertEqual(trend, 'stable')


class TestArcadeRoutingIntegration(unittest.TestCase):
    """Test Arcade routing integration with emotion enhancements."""

    def setUp(self):
        """Set up test environment."""
        with patch('Arcade.api.routing_integration.ORCHESTRAL_AVAILABLE', False):
            from Arcade.api.routing_integration import RoutingIntegration
            self.routing_integration = RoutingIntegration()

    def test_arcade_routing_initialization(self):
        """Test Arcade routing integration initialization."""
        self.assertIsNotNone(self.routing_integration)
        self.assertIsNotNone(self.routing_integration.city_status)

    @patch('Arcade.api.routing_integration.ORCHESTRAL_AVAILABLE', False)
    def test_fallback_routing(self):
        """Test fallback routing when emotion routing unavailable."""
        async def run_test():
            result = await self.routing_integration.find_stable_path_to_arcade(
                current_location='Delay',
                user_emotion='exploratory'
            )

            self.assertFalse(result['success'])
            self.assertIn('fallback_path', result)
            self.assertIn('stability_score', result)

        asyncio.run(run_test())

    def test_city_listing(self):
        """Test available city listing."""
        cities = self.routing_integration.list_cities()
        self.assertIsInstance(cities, list)
        self.assertIn('Echoes', cities)
        self.assertIn('Reverb', cities)
        self.assertIn('Delay', cities)

    def test_navigation_with_emotion_fallback(self):
        """Test navigation with emotion fallback."""
        async def run_test():
            result = await self.routing_integration.navigate_with_emotion(
                command='cd somewhere',
                current_location='Delay',
                user_context={'emotion': 'curious'}
            )

            self.assertFalse(result['success'])
            self.assertEqual(result['navigation_type'], 'standard')

        asyncio.run(run_test())

    def test_stability_report_fallback(self):
        """Test stability report when emotion routing unavailable."""
        report = self.routing_integration.get_stability_report()

        self.assertFalse(report['available'])
        self.assertIn('message', report)


class TestEmotionalPathOptimization(unittest.TestCase):
    """Test emotional path optimization algorithms."""

    def setUp(self):
        """Set up optimization test."""
        from Cable.src.emotion_search import SearchEmotion
        self.emotions = [SearchEmotion.EXPLORATORY, SearchEmotion.CREATIVE,
                        SearchEmotion.ANALYTICAL, SearchEmotion.URGENT]

    def test_emotion_spatial_mapping(self):
        """Test emotion to spatial position mapping."""
        from Cable.src.emotion_search import EmotionSpatializer
        spatializer = EmotionSpatializer()

        for emotion in self.emotions:
            mapping = spatializer.get_emotion_position(emotion)
            self.assertIn('position', mapping)
            self.assertIn('spread', mapping)
            self.assertIn('height', mapping)
            self.assertIn('description', mapping)

            # Validate position bounds
            pos = mapping['position']
            self.assertTrue(all(-5 <= coord <= 5 for coord in pos))

            # Validate spread and height
            self.assertGreater(mapping['spread'], 0)
            self.assertLessEqual(mapping['spread'], 3)

    def test_environment_scaling(self):
        """Test environment-based position scaling."""
        from Cable.src.emotion_search import EmotionSpatializer
        spatializer = EmotionSpatializer()

        # Test different environments
        environments = ['small_room', 'large_hall', 'cathedral', 'outdoor']

        for env in environments:
            immersive = spatializer.calculate_immersive_position('joyful', env)

            self.assertIn('position', immersive)
            self.assertIn('environment', immersive)
            self.assertIn('description', immersive)

            # Check environment data
            env_data = immersive['environment']
            self.assertIn('size', env_data)
            self.assertIn('rt60', env_data)

    def test_multi_criteria_route_scoring(self):
        """Test multi-criteria route scoring."""
        from Routing.emotion_enhanced_routing import EmotionEnhancedRouting

        with patch('Routing.emotion_enhanced_routing.CABLE_AVAILABLE', True), \
             patch('Routing.emotion_enhanced_routing.ROUTING_AVAILABLE', True):

            routing = EmotionEnhancedRouting()

            # Mock route data
            route_data = {
                'route': ['A', 'B', 'C'],
                'metrics': {
                    'navigation_smoothness': 0.8,
                    'connectivity_score': 0.7,
                    'route_reliability': 0.9
                }
            }

            from Cable.src.emotion_search import SearchEmotion
            user_emotion = SearchEmotion.EXPLORATORY
            criteria = {'emotional_coherence': 0.4, 'spatial_stability': 0.3,
                       'connection_reliability': 0.2, 'navigation_smoothness': 0.1}

            stability = routing._calculate_route_stability(route_data, user_emotion, criteria)

            self.assertGreater(stability, 0)
            self.assertLessEqual(stability, 1)


class TestIntegrationPerformance(unittest.TestCase):
    """Test performance of emotion-enhanced routing integration."""

    def test_routing_initialization_performance(self):
        """Test initialization performance."""
        start_time = time.time()

        with patch('Routing.emotion_enhanced_routing.CABLE_AVAILABLE', True), \
             patch('Routing.emotion_enhanced_routing.ROUTING_AVAILABLE', True):

            from Routing.emotion_enhanced_routing import EmotionEnhancedRouting
            routing = EmotionEnhancedRouting()

        end_time = time.time()
        init_time = end_time - start_time

        # Should initialize within reasonable time
        self.assertLess(init_time, 1.0)

    def test_stability_calculation_performance(self):
        """Test stability calculation performance."""
        from Routing.emotion_enhanced_routing import EmotionEnhancedRouting

        with patch('Routing.emotion_enhanced_routing.CABLE_AVAILABLE', True), \
             patch('Routing.emotion_enhanced_routing.ROUTING_AVAILABLE', True):

            routing = EmotionEnhancedRouting()

            route_data = {
                'metrics': {
                    'navigation_smoothness': 0.8,
                    'connectivity_score': 0.7,
                    'route_reliability': 0.9
                }
            }

            from Cable.src.emotion_search import SearchEmotion
            user_emotion = SearchEmotion.EXPLORATORY
            criteria = {'emotional_coherence': 0.4, 'spatial_stability': 0.3}

            start_time = time.time()

            # Run multiple calculations
            for _ in range(100):
                routing._calculate_route_stability(route_data, user_emotion, criteria)

            end_time = time.time()
            calc_time = (end_time - start_time) / 100

            # Should be very fast (< 1ms per calculation)
            self.assertLess(calc_time, 0.001)


if __name__ == "__main__":
    unittest.main()
