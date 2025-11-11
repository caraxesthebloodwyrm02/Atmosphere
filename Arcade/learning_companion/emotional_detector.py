#!/usr/bin/env python3
"""
Emotional Detection Module for Learning Companion
===============================================

Analyzes multiple signals to detect learner emotional states for adaptive content delivery.
"""

import time
import statistics
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sensor_integration import (
    get_typing_patterns,
    get_facial_expressions,
    get_physiological_data,
    get_all_sensor_readings,
    get_sensor_status
)

class Emotion(Enum):
    EXPLORATORY = "exploratory"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    URGENT = "urgent"
    CALM = "calm"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    ENGAGED = "engaged"

@dataclass
class EmotionalState:
    primary_emotion: Emotion
    confidence: float
    secondary_emotions: List[tuple[Emotion, float]]
    engagement_level: float
    stress_indicators: float
    timestamp: float

@dataclass
class InteractionMetrics:
    response_times: List[float]
    error_rate: float
    help_requests: int
    session_duration: float
    interaction_frequency: float

class EmotionalDetector:
    """Multi-modal emotional state detection for learners."""

    def __init__(self):
        self.interaction_history: List[InteractionMetrics] = []
        self.emotional_states: List[EmotionalState] = []
        self.baseline_metrics = {
            'avg_response_time': 5.0,  # seconds
            'error_threshold': 0.3,    # 30% errors
            'engagement_window': 300,  # 5 minutes
        }

    async def detect_emotional_state(self, learner_id: str, current_session_data: Dict[str, Any]) -> EmotionalState:
        """
        Analyze multiple signals to determine learner's emotional state.

        Args:
            learner_id: Unique identifier for the learner
            current_session_data: Current session metrics and interactions

        Returns:
            EmotionalState with primary emotion and confidence levels
        """

        # Gather multi-modal signals
        signals = await self._gather_emotional_signals(current_session_data)

        # Analyze interaction patterns
        interaction_analysis = self._analyze_interaction_patterns(signals)

        # Apply emotion classification algorithm
        emotion_scores = self._classify_emotions(interaction_analysis, signals)

        # Determine primary and secondary emotions
        primary_emotion, confidence = self._determine_primary_emotion(emotion_scores)
        secondary_emotions = self._get_secondary_emotions(emotion_scores, primary_emotion)

        # Calculate engagement and stress indicators
        engagement_level = self._calculate_engagement_level(signals, interaction_analysis)
        stress_indicators = self._calculate_stress_indicators(signals, interaction_analysis)

        emotional_state = EmotionalState(
            primary_emotion=primary_emotion,
            confidence=confidence,
            secondary_emotions=secondary_emotions,
            engagement_level=engagement_level,
            stress_indicators=stress_indicators,
            timestamp=time.time()
        )

        # Store for trend analysis
        self.emotional_states.append(emotional_state)

        return emotional_state

    async def _gather_emotional_signals(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Gather signals from various sources for emotional analysis."""

        signals = {
            'response_times': session_data.get('response_times', []),
            'error_count': session_data.get('error_count', 0),
            'total_attempts': session_data.get('total_attempts', 1),
            'help_requests': session_data.get('help_requests', 0),
            'session_duration': session_data.get('session_duration', 0),
            'interaction_frequency': session_data.get('interaction_frequency', 0),
            'content_difficulty': session_data.get('content_difficulty', 0.5),
            'progress_rate': session_data.get('progress_rate', 0.0),
            'time_since_last_interaction': session_data.get('time_since_last_interaction', 0),
        }

        # Real sensor integrations (when available)
        signals.update({
            'typing_patterns': get_typing_patterns(),
            'facial_expressions': get_facial_expressions(),
            'physiological_data': get_physiological_data(),
        })

        return signals

    def _analyze_interaction_patterns(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze interaction patterns for emotional indicators."""

        analysis = {}

        # Response time analysis
        if signals['response_times']:
            avg_response = statistics.mean(signals['response_times'])
            response_variability = statistics.stdev(signals['response_times']) if len(signals['response_times']) > 1 else 0

            analysis['response_time_pressure'] = avg_response < self.baseline_metrics['avg_response_time'] * 0.5
            analysis['response_time_frustration'] = avg_response > self.baseline_metrics['avg_response_time'] * 2.0
            analysis['response_consistency'] = response_variability < 2.0  # Low variability = focused
        else:
            analysis['response_time_pressure'] = False
            analysis['response_time_frustration'] = False
            analysis['response_consistency'] = True

        # Error pattern analysis
        error_rate = signals['error_count'] / max(signals['total_attempts'], 1)
        analysis['error_frustration'] = error_rate > self.baseline_metrics['error_threshold']
        analysis['error_learning'] = error_rate < 0.1 and signals['total_attempts'] > 5

        # Help-seeking behavior
        analysis['help_dependency'] = signals['help_requests'] > 3
        analysis['help_exploration'] = signals['help_requests'] == 0 and signals['session_duration'] > 600

        # Engagement indicators
        analysis['high_engagement'] = (
            signals['interaction_frequency'] > 0.5 and  # Interactions per minute
            signals['progress_rate'] > 0.7 and
            not analysis['error_frustration']
        )

        analysis['low_engagement'] = (
            signals['time_since_last_interaction'] > 300 or  # 5+ minutes inactive
            signals['interaction_frequency'] < 0.1
        )

        # Learning flow indicators
        analysis['smooth_learning'] = (
            not analysis['error_frustration'] and
            analysis['response_consistency'] and
            signals['progress_rate'] > 0.3
        )

        analysis['challenging_learning'] = (
            analysis['error_frustration'] or
            analysis['response_time_frustration'] or
            signals['content_difficulty'] > 0.8
        )

        return analysis

    def _classify_emotions(self, interaction_analysis: Dict[str, Any], signals: Dict[str, Any]) -> Dict[Emotion, float]:
        """Classify emotions based on interaction patterns and signals."""

        emotion_scores = {emotion: 0.0 for emotion in Emotion}

        # Exploratory: High engagement, low errors, frequent interactions
        if (interaction_analysis['high_engagement'] and
            not interaction_analysis['error_frustration'] and
            signals['interaction_frequency'] > 0.3):
            emotion_scores[Emotion.EXPLORATORY] = 0.85

        # Creative: Moderate errors (experimentation), good progress, help-seeking
        if (interaction_analysis['error_learning'] or
            signals['help_requests'] > 0 and signals['help_requests'] < 3):
            emotion_scores[Emotion.CREATIVE] = 0.75

        # Analytical: Consistent responses, low errors, structured progress
        if (interaction_analysis['smooth_learning'] and
            interaction_analysis['response_consistency'] and
            signals['progress_rate'] > 0.5):
            emotion_scores[Emotion.ANALYTICAL] = 0.90

        # Urgent: Fast responses, high error rate, time pressure
        if (interaction_analysis['response_time_pressure'] or
            signals['session_duration'] < 300 and signals['progress_rate'] < 0.3):
            emotion_scores[Emotion.URGENT] = 0.80

        # Calm: Steady progress, moderate engagement, no stress indicators
        if (interaction_analysis['smooth_learning'] and
            not interaction_analysis['high_engagement'] and
            not interaction_analysis['challenging_learning']):
            emotion_scores[Emotion.CALM] = 0.70

        # Frustrated: High errors, slow responses, frequent help requests
        if (interaction_analysis['error_frustration'] and
            interaction_analysis['response_time_frustration']):
            emotion_scores[Emotion.FRUSTRATED] = 0.85

        # Confused: Moderate errors, inconsistent responses, help dependency
        if (interaction_analysis['help_dependency'] and
            not interaction_analysis['response_consistency']):
            emotion_scores[Emotion.CONFUSED] = 0.75

        # Engaged: High interaction frequency, good progress, positive indicators
        if (interaction_analysis['high_engagement'] and
            signals['progress_rate'] > 0.6):
            emotion_scores[Emotion.ENGAGED] = 0.95

        return emotion_scores

    def _determine_primary_emotion(self, emotion_scores: Dict[Emotion, float]) -> tuple[Emotion, float]:
        """Determine the primary emotion with highest confidence."""

        if not emotion_scores:
            return Emotion.CALM, 0.5

        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        return primary_emotion

    def _get_secondary_emotions(self, emotion_scores: Dict[Emotion, float], primary: Emotion) -> List[tuple[Emotion, float]]:
        """Get secondary emotions sorted by confidence."""

        # Remove primary emotion and sort by confidence
        secondary_scores = {k: v for k, v in emotion_scores.items() if k != primary}
        sorted_secondary = sorted(secondary_scores.items(), key=lambda x: x[1], reverse=True)

        return sorted_secondary[:2]  # Return top 2 secondary emotions

    def _calculate_engagement_level(self, signals: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Calculate overall engagement level (0.0 to 1.0)."""

        engagement_factors = [
            min(signals['interaction_frequency'] / 1.0, 1.0),  # Normalize to 1.0 max
            signals['progress_rate'],
            1.0 if analysis['high_engagement'] else 0.0,
            0.5 if analysis['smooth_learning'] else 0.0,
        ]

        # Penalize for low engagement indicators
        if analysis['low_engagement']:
            engagement_factors.append(-0.3)

        return max(0.0, min(1.0, statistics.mean(engagement_factors)))

    def _calculate_stress_indicators(self, signals: Dict[str, Any], analysis: Dict[str, Any]) -> float:
        """Calculate stress level (0.0 to 1.0)."""

        stress_factors = []

        if analysis['error_frustration']:
            stress_factors.append(0.4)
        if analysis['response_time_frustration']:
            stress_factors.append(0.3)
        if analysis['help_dependency']:
            stress_factors.append(0.2)
        if signals['error_count'] > signals['total_attempts'] * 0.5:
            stress_factors.append(0.3)

        # Reduce stress for positive indicators
        if analysis['smooth_learning']:
            stress_factors.append(-0.2)
        if analysis['high_engagement']:
            stress_factors.append(-0.1)

        return max(0.0, min(1.0, statistics.mean(stress_factors) if stress_factors else 0.0))

    def get_emotional_trends(self, learner_id: str, time_window: int = 3600) -> Dict[str, Any]:
        """Analyze emotional trends over time for the learner."""

        recent_states = [
            state for state in self.emotional_states
            if time.time() - state.timestamp < time_window
        ]

        if not recent_states:
            return {"trend": "insufficient_data", "insights": []}

        # Analyze emotional stability
        primary_emotions = [state.primary_emotion for state in recent_states]
        emotion_stability = len(set(primary_emotions)) / len(primary_emotions)  # Lower = more stable

        # Analyze engagement trends
        engagement_trend = statistics.mean([state.engagement_level for state in recent_states])

        # Analyze stress patterns
        stress_trend = statistics.mean([state.stress_indicators for state in recent_states])

        return {
            "trend": "stable" if emotion_stability < 0.5 else "variable",
            "avg_engagement": engagement_trend,
            "avg_stress": stress_trend,
            "dominant_emotion": max(set(primary_emotions), key=primary_emotions.count),
            "insights": self._generate_trend_insights(recent_states)
        }

    def _generate_trend_insights(self, states: List[EmotionalState]) -> List[str]:
        """Generate insights based on emotional trends."""

        insights = []

        if len(states) < 3:
            return insights

        # Check for improving engagement
        recent_engagement = [s.engagement_level for s in states[-3:]]
        if recent_engagement[-1] > recent_engagement[0] + 0.2:
            insights.append("Engagement improving - learning momentum building")

        # Check for increasing stress
        recent_stress = [s.stress_indicators for s in states[-3:]]
        if recent_stress[-1] > recent_stress[0] + 0.2:
            insights.append("Stress levels rising - consider adjusting pace or difficulty")

        # Check for emotional consistency
        recent_emotions = [s.primary_emotion for s in states[-5:]]
        if len(set(recent_emotions)) == 1:
            emotion = recent_emotions[0]
            insights.append(f"Consistently {emotion.value} emotional state - content well-matched")

        return insights
