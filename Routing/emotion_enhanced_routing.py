"""
Emotion-Enhanced Routing Integration for Arcade
===============================================

Uses Cable's emotional intelligence and spatial positioning to find the most stable
path to connect to Arcade, considering emotional coherence and spatial stability.
"""

import asyncio
import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import sys
import math

# Add Cable and Routing to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Import enhanced Cable components
try:
    from Cable.src.emotion_search import (
        EmotionAnalyzer, SearchEmotion, EmotionSpatializer,
        EnhancedSearchMetrics
    )
    CABLE_AVAILABLE = True
except ImportError:
    CABLE_AVAILABLE = False
    logging.warning("Cable emotion search not available")

# Import enhanced Routing components
try:
    from Routing.acoustic_routing import AcousticRoutingNetwork
    from Routing.self_aware_routing import SelfAwareRouter
    ROUTING_AVAILABLE = True
except ImportError:
    ROUTING_AVAILABLE = False
    logging.warning("Enhanced routing not available")

logger = logging.getLogger(__name__)


class EmotionEnhancedRouting:
    """
    Emotion-enhanced routing system that uses Cable's emotional intelligence
    to find the most stable path to Arcade.
    """

    def __init__(self):
        self.cable_available = CABLE_AVAILABLE
        self.routing_available = ROUTING_AVAILABLE

        # Initialize components
        self.emotion_analyzer = EmotionAnalyzer() if CABLE_AVAILABLE else None
        self.spatializer = EmotionSpatializer() if CABLE_AVAILABLE else None
        self.enhanced_metrics = EnhancedSearchMetrics() if CABLE_AVAILABLE else None

        # Routing network for path finding
        self.routing_network = None
        self.self_aware_router = None

        # Stability metrics
        self.connection_history = []
        self.stability_scores = {}

        # Emotional context for Arcade connection
        self.arcade_emotional_profile = {
            'primary_emotion': SearchEmotion.EXPLORATORY,
            'spatial_position': (0, 0, 0),  # Center of emotional space
            'stability_factors': {
                'emotional_coherence': 0.9,
                'spatial_stability': 0.95,
                'connection_reliability': 0.85
            }
        }

    async def initialize(self) -> bool:
        """Initialize emotion-enhanced routing system."""
        if not self.routing_available:
            logger.error("Enhanced routing system not available")
            return False

        try:
            # Initialize routing network
            self.routing_network = AcousticRoutingNetwork()

            # Build the highway network with acoustic properties
            from Routing.us_highway_model import build_us_highway_network
            self.routing_network = build_us_highway_network()

            # Initialize self-aware routing
            if hasattr(SelfAwareRouter, '__init__'):
                # Mock connector for self-aware routing
                class MockConnector:
                    def get_status(self):
                        return {"status": "healthy", "connections": 5}

                    async def get_health_status(self):
                        return {"status": "healthy", "connections": 5}

                mock_connector = MockConnector()
                self.self_aware_router = SelfAwareRouter(mock_connector)

            logger.info("Emotion-enhanced routing system initialized")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize emotion-enhanced routing: {e}")
            return False

    async def find_stable_path_to_arcade(
        self,
        current_location: str = "Delay",
        user_emotion: SearchEmotion = None,
        stability_criteria: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """
        Find the most stable path to Arcade using emotional intelligence.

        Args:
            current_location: Starting point (Delay, Reverb, Echoes)
            user_emotion: User's current emotional state
            stability_criteria: Custom stability weighting criteria

        Returns:
            Dict containing path, stability metrics, and emotional analysis
        """
        if not self.routing_available:
            return {
                'success': False,
                'error': 'Routing system not available',
                'fallback_path': ['Delay', 'Arcade']
            }

        # Set default stability criteria
        if stability_criteria is None:
            stability_criteria = {
                'emotional_coherence': 0.4,
                'spatial_stability': 0.3,
                'connection_reliability': 0.2,
                'navigation_smoothness': 0.1
            }

        # Analyze user's emotional state if not provided
        if user_emotion is None and self.cable_available:
            # Use exploratory as default for Arcade navigation
            user_emotion = SearchEmotion.EXPLORATORY

        # Get emotional mapping for Arcade connection
        arcade_emotion_mapping = self.spatializer.get_emotion_position(
            self.arcade_emotional_profile['primary_emotion']
        ) if self.spatializer else None

        # Find multiple route candidates using different optimization criteria
        route_candidates = []
        criteria_options = ['distance', 'delay', 'reverb']

        for criterion in criteria_options:
            try:
                route = self.routing_network.find_optimal_route(current_location, 'Arcade', criterion)
                if route and len(route) > 1:
                    metrics = self.routing_network.calculate_route_metrics(route)
                    route_candidates.append({
                        'route': route,
                        'optimization_criterion': criterion,
                        'metrics': metrics,
                        'path_length': len(route)
                    })
            except Exception as e:
                logger.warning(f"Failed to find {criterion} route: {e}")
                continue

        if not route_candidates:
            return {
                'success': False,
                'error': 'No routes found to Arcade',
                'candidates_searched': 0
            }

        # Score routes based on stability criteria
        scored_routes = []
        for candidate in route_candidates:
            stability_score = self._calculate_route_stability(
                candidate, user_emotion, stability_criteria
            )

            candidate['stability_score'] = stability_score
            candidate['emotional_analysis'] = self._analyze_route_emotion(
                candidate['route'], user_emotion
            ) if self.cable_available else {}

            scored_routes.append(candidate)

        # Sort by stability score
        scored_routes.sort(key=lambda x: x['stability_score'], reverse=True)

        # Get the most stable route
        best_route = scored_routes[0]

        # Generate spatial positioning for the route
        spatial_positioning = self._create_route_spatial_positioning(
            best_route['route'], user_emotion
        ) if self.spatializer else {}

        # Update connection history
        self.connection_history.append({
            'timestamp': time.time(),
            'route': best_route['route'],
            'stability_score': best_route['stability_score'],
            'user_emotion': user_emotion.value if user_emotion else None,
            'success': True
        })

        return {
            'success': True,
            'stable_path': best_route['route'],
            'stability_score': best_route['stability_score'],
            'optimization_criterion': best_route['optimization_criterion'],
            'route_metrics': best_route['metrics'],
            'emotional_analysis': best_route['emotional_analysis'],
            'spatial_positioning': spatial_positioning,
            'stability_criteria_used': stability_criteria,
            'alternative_routes': len(scored_routes) - 1,
            'connection_reliability': self._calculate_connection_reliability(best_route)
        }

    def _calculate_route_stability(
        self,
        route_data: Dict[str, Any],
        user_emotion: SearchEmotion,
        criteria: Dict[str, float]
    ) -> float:
        """Calculate overall stability score for a route."""
        metrics = route_data['metrics']

        # Base stability components
        emotional_coherence = 1.0  # Default high coherence
        if self.cable_available and user_emotion:
            # Calculate emotional alignment with Arcade's profile
            arcade_emotion = self.arcade_emotional_profile['primary_emotion']
            emotional_coherence = 1.0 if user_emotion == arcade_emotion else 0.6

        spatial_stability = metrics.get('navigation_smoothness', 0.5)
        connection_reliability = metrics.get('route_reliability', 0.7)

        # Weighted stability score
        stability_score = (
            emotional_coherence * criteria.get('emotional_coherence', 0.4) +
            spatial_stability * criteria.get('spatial_stability', 0.3) +
            connection_reliability * criteria.get('connection_reliability', 0.2) +
            metrics.get('connectivity_score', 0.5) * criteria.get('navigation_smoothness', 0.1)
        )

        return min(stability_score, 1.0)  # Cap at 1.0

    def _analyze_route_emotion(
        self,
        route: List[str],
        user_emotion: SearchEmotion
    ) -> Dict[str, Any]:
        """Analyze the emotional characteristics of a route."""
        if not self.cable_available:
            return {'available': False}

        # Analyze each segment for emotional content
        segment_emotions = []
        for i in range(len(route) - 1):
            segment = f"{route[i]} to {route[i+1]}"
            # Simulate emotional analysis of route segments
            segment_emotion = self.emotion_analyzer.analyze_query_emotion(f"travel from {segment}")
            segment_emotions.append({
                'segment': segment,
                'emotion': segment_emotion.value,
                'coherence': 1.0 if segment_emotion == user_emotion else 0.5
            })

        avg_coherence = sum(s['coherence'] for s in segment_emotions) / len(segment_emotions)

        return {
            'available': True,
            'user_emotion': user_emotion.value if user_emotion else None,
            'segment_analysis': segment_emotions,
            'average_coherence': avg_coherence,
            'route_emotional_profile': self._determine_route_emotion(segment_emotions)
        }

    def _determine_route_emotion(self, segment_emotions: List[Dict]) -> str:
        """Determine the overall emotional profile of a route."""
        if not segment_emotions:
            return 'neutral'

        # Count emotion frequencies
        emotion_counts = {}
        for segment in segment_emotions:
            emotion = segment['emotion']
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        # Return most common emotion
        return max(emotion_counts.items(), key=lambda x: x[1])[0]

    def _create_route_spatial_positioning(
        self,
        route: List[str],
        user_emotion: SearchEmotion
    ) -> Dict[str, Any]:
        """Create spatial positioning data for route visualization."""
        if not self.spatializer:
            return {'available': False}

        # Create mock search results for spatial positioning
        mock_results = []
        for i, location in enumerate(route):
            mock_result = {
                'score': 0.8 - (i * 0.1),  # Decreasing scores along route
                'content': f"Navigation point: {location}",
                'title': location
            }
            mock_results.append(mock_result)

        # Generate spatial positioning
        spatial_space = self.enhanced_metrics.create_emotional_search_space(
            mock_results, f"Navigate to {route[-1]}"
        )

        return {
            'available': True,
            'route_positions': spatial_space.get('results', []),
            'emotional_context': spatial_space.get('query_emotion', 'neutral'),
            'spatial_description': spatial_space.get('spatial_description', 'Standard navigation')
        }

    def _calculate_connection_reliability(self, route_data: Dict[str, Any]) -> float:
        """Calculate connection reliability based on route characteristics."""
        metrics = route_data['metrics']

        # Factors affecting reliability
        smoothness = metrics.get('navigation_smoothness', 0.5)
        connectivity = metrics.get('connectivity_score', 0.5)
        reliability = metrics.get('route_reliability', 0.7)

        # Historical reliability (based on past connections)
        historical_factor = 0.8  # Default good history

        # Calculate overall reliability
        overall_reliability = (
            smoothness * 0.3 +
            connectivity * 0.3 +
            reliability * 0.3 +
            historical_factor * 0.1
        )

        return min(overall_reliability, 1.0)

    async def get_connection_status(self) -> Dict[str, Any]:
        """Get comprehensive connection status to Arcade."""
        return {
            'routing_available': self.routing_available,
            'cable_available': self.cable_available,
            'connection_history': len(self.connection_history),
            'recent_connections': self.connection_history[-5:] if self.connection_history else [],
            'stability_scores': self.stability_scores,
            'arcade_emotional_profile': self.arcade_emotional_profile,
            'system_health': 'healthy' if self.routing_available else 'degraded'
        }

    def get_stability_report(self) -> Dict[str, Any]:
        """Generate a comprehensive stability report."""
        if not self.connection_history:
            return {'available': False, 'message': 'No connection history available'}

        # Analyze connection history
        successful_connections = len([c for c in self.connection_history if c.get('success', False)])
        avg_stability = sum(c.get('stability_score', 0) for c in self.connection_history) / len(self.connection_history)

        # Emotional distribution
        emotion_distribution = {}
        for connection in self.connection_history:
            emotion = connection.get('user_emotion')
            if emotion:
                emotion_distribution[emotion] = emotion_distribution.get(emotion, 0) + 1

        return {
            'available': True,
            'total_connections': len(self.connection_history),
            'successful_connections': successful_connections,
            'average_stability': avg_stability,
            'emotional_distribution': emotion_distribution,
            'most_stable_emotion': max(emotion_distribution.items(), key=lambda x: x[1])[0] if emotion_distribution else None,
            'stability_trend': self._calculate_stability_trend()
        }

    def _calculate_stability_trend(self) -> str:
        """Calculate stability trend over time."""
        if len(self.connection_history) < 3:
            return 'insufficient_data'

        recent_scores = [c.get('stability_score', 0) for c in self.connection_history[-5:]]
        avg_recent = sum(recent_scores) / len(recent_scores)

        older_scores = [c.get('stability_score', 0) for c in self.connection_history[:-5]]
        avg_older = sum(older_scores) / len(older_scores) if older_scores else avg_recent

        if avg_recent > avg_older + 0.1:
            return 'improving'
        elif avg_recent < avg_older - 0.1:
            return 'declining'
        else:
            return 'stable'
