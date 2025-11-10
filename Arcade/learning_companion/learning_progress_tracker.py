#!/usr/bin/env python3
"""
Learning Progress Tracker for Learning Companion
==============================================

Tracks learning progress, analyzes behavioral patterns, and provides insights
for adaptive content delivery based on Atmosphere behavioral analysis principles.
"""

import json
import time
import statistics
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
import asyncio

from .emotional_detector import Emotion

@dataclass
class LearningSession:
    session_id: str
    learner_id: str
    topic: str
    start_time: float
    end_time: Optional[float]
    emotional_states: List[Dict[str, Any]]
    interactions: List[Dict[str, Any]]
    content_modules: List[Dict[str, Any]]
    progress_metrics: Dict[str, Any]
    behavioral_insights: Dict[str, Any]

@dataclass
class LearningProgress:
    learner_id: str
    topic: str
    overall_mastery: float  # 0.0 to 1.0
    skill_breakdown: Dict[str, float]
    learning_velocity: float  # concepts mastered per hour
    confidence_trend: List[Tuple[float, float]]  # (timestamp, confidence)
    emotional_patterns: Dict[str, Any]
    recommended_difficulty: str
    next_focus_areas: List[str]

class LearningProgressTracker:
    """Tracks learning progress and analyzes behavioral patterns for adaptive learning."""

    def __init__(self, data_storage_path: str = "learning_data"):
        self.data_storage = Path(data_storage_path)
        self.data_storage.mkdir(exist_ok=True)

        self.active_sessions: Dict[str, LearningSession] = {}
        self.learner_profiles: Dict[str, Dict[str, Any]] = {}

        # Load existing data
        self._load_existing_data()

    def start_learning_session(
        self,
        learner_id: str,
        topic: str,
        session_metadata: Dict[str, Any] = None
    ) -> str:
        """Start a new learning session and return session ID."""

        session_id = f"{learner_id}_{topic}_{int(time.time())}"

        session = LearningSession(
            session_id=session_id,
            learner_id=learner_id,
            topic=topic,
            start_time=time.time(),
            end_time=None,
            emotional_states=[],
            interactions=[],
            content_modules=[],
            progress_metrics={},
            behavioral_insights={}
        )

        self.active_sessions[session_id] = session

        # Initialize learner profile if new
        if learner_id not in self.learner_profiles:
            self.learner_profiles[learner_id] = {
                "learner_id": learner_id,
                "created_at": time.time(),
                "total_sessions": 0,
                "topics_attempted": set(),
                "skill_mastery": {},
                "learning_preferences": {},
                "emotional_patterns": {}
            }

        self.learner_profiles[learner_id]["total_sessions"] += 1
        self.learner_profiles[learner_id]["topics_attempted"].add(topic)

        return session_id

    def record_interaction(
        self,
        session_id: str,
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ):
        """Record a learning interaction (question, answer, hint request, etc.)."""

        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]

        interaction = {
            "timestamp": time.time(),
            "type": interaction_type,
            "data": interaction_data,
            "session_time": time.time() - session.start_time
        }

        session.interactions.append(interaction)

    def record_emotional_state(
        self,
        session_id: str,
        emotional_state: Dict[str, Any]
    ):
        """Record emotional state during learning session."""

        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]

        emotional_record = {
            "timestamp": time.time(),
            "state": emotional_state,
            "session_time": time.time() - session.start_time
        }

        session.emotional_states.append(emotional_record)

    def record_content_completion(
        self,
        session_id: str,
        module_id: str,
        completion_data: Dict[str, Any]
    ):
        """Record completion of a content module."""

        if session_id not in self.active_sessions:
            return

        session = self.active_sessions[session_id]

        completion_record = {
            "module_id": module_id,
            "timestamp": time.time(),
            "data": completion_data,
            "session_time": time.time() - session.start_time
        }

        session.content_modules.append(completion_record)

    def end_learning_session(self, session_id: str) -> Dict[str, Any]:
        """End learning session and generate comprehensive progress report."""

        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]
        session.end_time = time.time()

        # Analyze session data
        session_analysis = self._analyze_session_data(session)

        # Update learner profile
        self._update_learner_profile(session.learner_id, session_analysis)

        # Generate progress report
        progress_report = self._generate_progress_report(session, session_analysis)

        # Save session data
        self._save_session_data(session)

        # Remove from active sessions
        del self.active_sessions[session_id]

        return progress_report

    def get_learning_progress(self, learner_id: str, topic: str = None) -> LearningProgress:
        """Get comprehensive learning progress for a learner."""

        profile = self.learner_profiles.get(learner_id, {})

        if not profile:
            return self._create_empty_progress(learner_id, topic or "general")

        # Calculate overall mastery
        skill_mastery = profile.get("skill_mastery", {})
        overall_mastery = statistics.mean(skill_mastery.values()) if skill_mastery else 0.0

        # Calculate learning velocity (concepts per hour)
        total_sessions = profile.get("total_sessions", 1)
        learning_velocity = len(skill_mastery) / max(total_sessions * 2.0, 1.0)  # Assume 2 hours per session

        # Get confidence trend (simplified)
        confidence_trend = [(time.time(), overall_mastery)]  # Placeholder

        # Analyze emotional patterns
        emotional_patterns = profile.get("emotional_patterns", {})

        # Determine recommended difficulty
        recommended_difficulty = self._calculate_recommended_difficulty(overall_mastery)

        # Identify next focus areas
        next_focus_areas = self._identify_focus_areas(skill_mastery, topic)

        return LearningProgress(
            learner_id=learner_id,
            topic=topic or "general",
            overall_mastery=overall_mastery,
            skill_breakdown=skill_mastery,
            learning_velocity=learning_velocity,
            confidence_trend=confidence_trend,
            emotional_patterns=emotional_patterns,
            recommended_difficulty=recommended_difficulty,
            next_focus_areas=next_focus_areas
        )

    def get_behavioral_insights(self, learner_id: str, time_window_days: int = 30) -> Dict[str, Any]:
        """Generate behavioral insights based on learning patterns."""

        cutoff_time = time.time() - (time_window_days * 24 * 60 * 60)

        # Load historical session data
        historical_sessions = self._load_historical_sessions(learner_id, cutoff_time)

        if not historical_sessions:
            return {"insights": [], "patterns": {}, "recommendations": []}

        insights = []

        # Analyze learning consistency
        session_dates = [s['start_time'] for s in historical_sessions]
        if len(session_dates) > 1:
            intervals = [(session_dates[i] - session_dates[i-1]) for i in range(1, len(session_dates))]
            avg_interval = statistics.mean(intervals) / (24 * 60 * 60)  # days

            if avg_interval < 2:
                insights.append("Consistent daily learning pattern - excellent momentum!")
            elif avg_interval > 7:
                insights.append("Learning sessions are spaced out - consider more frequent practice")

        # Analyze preferred learning times
        session_hours = [datetime.fromtimestamp(s['start_time']).hour for s in historical_sessions]
        if session_hours:
            preferred_hour = statistics.mode(session_hours)
            insights.append(f"Most productive learning time: {preferred_hour}:00")

        # Analyze emotional learning patterns
        emotional_trends = self._analyze_emotional_trends(historical_sessions)
        insights.extend(emotional_trends)

        # Analyze topic progression
        topic_progression = self._analyze_topic_progression(historical_sessions)
        insights.extend(topic_progression)

        # Generate recommendations
        recommendations = self._generate_behavioral_recommendations(insights, historical_sessions)

        return {
            "insights": insights,
            "patterns": self._extract_behavioral_patterns(historical_sessions),
            "recommendations": recommendations,
            "time_window_days": time_window_days
        }

    def _analyze_session_data(self, session: LearningSession) -> Dict[str, Any]:
        """Analyze comprehensive session data for insights."""

        analysis = {
            "duration": session.end_time - session.start_time if session.end_time else 0,
            "total_interactions": len(session.interactions),
            "emotional_shifts": len(session.emotional_states),
            "modules_completed": len(session.content_modules),
            "learning_efficiency": 0.0,
            "emotional_stability": 0.0,
            "progress_indicators": {}
        }

        # Calculate learning efficiency
        if analysis["duration"] > 0:
            analysis["learning_efficiency"] = analysis["modules_completed"] / (analysis["duration"] / 3600)  # modules per hour

        # Analyze emotional stability
        if session.emotional_states:
            primary_emotions = [state["state"]["primary_emotion"] for state in session.emotional_states]
            unique_emotions = len(set(primary_emotions))
            analysis["emotional_stability"] = 1.0 - (unique_emotions / len(primary_emotions))

        # Calculate progress indicators
        if session.interactions:
            successful_interactions = sum(1 for i in session.interactions if i["data"].get("success", False))
            analysis["progress_indicators"]["success_rate"] = successful_interactions / len(session.interactions)

        if session.content_modules:
            avg_completion_time = statistics.mean(
                module["session_time"] for module in session.content_modules
            )
            analysis["progress_indicators"]["avg_completion_time"] = avg_completion_time

        return analysis

    def _update_learner_profile(self, learner_id: str, session_analysis: Dict[str, Any]):
        """Update learner profile with session insights."""

        profile = self.learner_profiles[learner_id]

        # Update skill mastery based on session performance
        topic_skills = ["problem_solving", "concept_understanding", "code_writing", "debugging"]

        for skill in topic_skills:
            current_mastery = profile["skill_mastery"].get(skill, 0.5)
            session_performance = session_analysis.get("progress_indicators", {}).get("success_rate", 0.5)

            # Weighted update: 70% current, 30% new session
            updated_mastery = (current_mastery * 0.7) + (session_performance * 0.3)
            profile["skill_mastery"][skill] = min(1.0, updated_mastery)

        # Update learning preferences
        profile["learning_preferences"]["preferred_session_duration"] = session_analysis["duration"]
        profile["learning_preferences"]["optimal_efficiency"] = session_analysis["learning_efficiency"]

        # Update emotional patterns
        profile["emotional_patterns"]["avg_stability"] = session_analysis["emotional_stability"]

    def _generate_progress_report(self, session: LearningSession, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive progress report."""

        return {
            "session_id": session.session_id,
            "learner_id": session.learner_id,
            "topic": session.topic,
            "session_duration": analysis["duration"],
            "performance_metrics": {
                "modules_completed": analysis["modules_completed"],
                "interactions_count": analysis["total_interactions"],
                "learning_efficiency": analysis["learning_efficiency"],
                "emotional_stability": analysis["emotional_stability"]
            },
            "progress_indicators": analysis["progress_indicators"],
            "insights": self._generate_session_insights(analysis),
            "recommendations": self._generate_session_recommendations(analysis),
            "next_session_suggestions": self._suggest_next_session(session.learner_id, session.topic)
        }

    def _generate_session_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from session analysis."""

        insights = []

        efficiency = analysis["learning_efficiency"]
        if efficiency > 2.0:
            insights.append("Excellent learning efficiency - concepts mastered quickly!")
        elif efficiency > 1.0:
            insights.append("Good learning pace with steady progress")
        else:
            insights.append("Consider breaking down concepts into smaller chunks")

        stability = analysis["emotional_stability"]
        if stability > 0.8:
            insights.append("Emotionally consistent learning session")
        elif stability < 0.5:
            insights.append("Emotional fluctuations detected - content adapted well")

        if analysis["progress_indicators"].get("success_rate", 0) > 0.8:
            insights.append("High success rate indicates strong comprehension")
        elif analysis["progress_indicators"].get("success_rate", 0) < 0.6:
            insights.append("Additional practice may help solidify understanding")

        return insights

    def _generate_session_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on session analysis."""

        recommendations = []

        if analysis["learning_efficiency"] < 1.0:
            recommendations.append("Try shorter, more focused learning sessions")
            recommendations.append("Incorporate more interactive exercises")

        if analysis["emotional_stability"] < 0.6:
            recommendations.append("Consider taking breaks during challenging sections")
            recommendations.append("Use stress-reduction techniques between modules")

        if analysis["progress_indicators"].get("success_rate", 0) < 0.7:
            recommendations.append("Review fundamental concepts before advancing")
            recommendations.append("Practice with simpler examples first")

        if analysis["duration"] > 3600:  # Over 1 hour
            recommendations.append("Break long sessions into 30-45 minute segments")

        return recommendations

    def _suggest_next_session(self, learner_id: str, current_topic: str) -> Dict[str, Any]:
        """Suggest optimal parameters for next learning session."""

        profile = self.learner_profiles.get(learner_id, {})

        suggested_duration = profile.get("learning_preferences", {}).get("preferred_session_duration", 1800)
        optimal_efficiency = profile.get("learning_preferences", {}).get("optimal_efficiency", 1.0)

        return {
            "suggested_duration_minutes": min(60, max(15, suggested_duration / 60)),
            "recommended_difficulty": self._calculate_recommended_difficulty(
                statistics.mean(profile.get("skill_mastery", {}).values() or [0.5])
            ),
            "focus_areas": ["practice", "review", "advancement"][:2],  # First two priorities
            "emotional_preparation": "Start with calming exercises if previous session had high stress"
        }

    def _calculate_recommended_difficulty(self, mastery_level: float) -> str:
        """Calculate recommended difficulty level."""

        if mastery_level < 0.3:
            return "beginner"
        elif mastery_level < 0.6:
            return "intermediate"
        elif mastery_level < 0.8:
            return "advanced"
        else:
            return "expert"

    def _identify_focus_areas(self, skill_mastery: Dict[str, float], topic: str) -> List[str]:
        """Identify areas needing focus based on skill mastery."""

        if not skill_mastery:
            return ["fundamentals", "practice"]

        # Find weakest skills
        sorted_skills = sorted(skill_mastery.items(), key=lambda x: x[1])

        focus_areas = []
        for skill, mastery in sorted_skills[:2]:  # Focus on 2 weakest areas
            if mastery < 0.6:
                focus_areas.append(f"strengthen_{skill}")
            else:
                focus_areas.append(f"advance_{skill}")

        return focus_areas

    def _analyze_emotional_trends(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Analyze emotional trends across sessions."""

        insights = []

        # Extract emotional data from sessions
        all_emotions = []
        for session in sessions:
            for state in session.get("emotional_states", []):
                all_emotions.append(state["state"]["primary_emotion"])

        if not all_emotions:
            return insights

        # Find most common emotion
        try:
            common_emotion = statistics.mode(all_emotions)
            insights.append(f"Most common learning emotion: {common_emotion}")
        except statistics.StatisticsError:
            insights.append("Varied emotional states during learning")

        # Analyze emotional consistency
        unique_emotions = len(set(all_emotions))
        consistency_ratio = 1.0 - (unique_emotions / len(all_emotions))

        if consistency_ratio > 0.7:
            insights.append("Consistent emotional patterns - stable learning environment")
        elif consistency_ratio < 0.4:
            insights.append("Varied emotional responses - adaptive content working well")

        return insights

    def _analyze_topic_progression(self, sessions: List[Dict[str, Any]]) -> List[str]:
        """Analyze progression through topics."""

        insights = []

        topics = [s["topic"] for s in sessions]
        topic_counts = {}

        for topic in topics:
            topic_counts[topic] = topic_counts.get(topic, 0) + 1

        # Find most practiced topic
        if topic_counts:
            most_practiced = max(topic_counts.items(), key=lambda x: x[1])
            insights.append(f"Most practiced topic: {most_practiced[0]} ({most_practiced[1]} sessions)")

        # Check topic diversity
        unique_topics = len(set(topics))
        if unique_topics > 3:
            insights.append("Good topic diversity - well-rounded learning approach")
        elif unique_topics == 1:
            insights.append("Focused on single topic - consider broadening scope")

        return insights

    def _generate_behavioral_recommendations(self, insights: List[str], sessions: List[Dict[str, Any]]) -> List[str]:
        """Generate recommendations based on behavioral insights."""

        recommendations = []

        insight_text = " ".join(insights).lower()

        if "consistent" in insight_text and "daily" in insight_text:
            recommendations.append("Maintain current learning schedule - it's working well!")

        if "spaced out" in insight_text:
            recommendations.append("Try more frequent, shorter learning sessions")

        if "varied emotional" in insight_text:
            recommendations.append("Continue using adaptive content - it's effectively handling emotional changes")

        if "single topic" in insight_text:
            recommendations.append("Explore related topics to build broader understanding")

        if "productive learning time" in insight_text:
            recommendations.append("Schedule important learning sessions during your most productive hours")

        return recommendations

    def _extract_behavioral_patterns(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract behavioral patterns from session data."""

        patterns = {
            "avg_session_duration": 0,
            "preferred_learning_times": [],
            "topic_sequence": [],
            "success_patterns": {}
        }

        if not sessions:
            return patterns

        # Calculate average session duration
        durations = [s.get("end_time", s["start_time"]) - s["start_time"] for s in sessions if s.get("end_time")]
        if durations:
            patterns["avg_session_duration"] = statistics.mean(durations)

        # Extract preferred learning times
        hours = [datetime.fromtimestamp(s["start_time"]).hour for s in sessions]
        if hours:
            patterns["preferred_learning_times"] = [statistics.mode(hours)] if len(set(hours)) > 1 else [hours[0]]

        # Topic sequence
        patterns["topic_sequence"] = [s["topic"] for s in sessions]

        return patterns

    def _create_empty_progress(self, learner_id: str, topic: str) -> LearningProgress:
        """Create empty progress for new learners."""

        return LearningProgress(
            learner_id=learner_id,
            topic=topic,
            overall_mastery=0.0,
            skill_breakdown={},
            learning_velocity=0.0,
            confidence_trend=[],
            emotional_patterns={},
            recommended_difficulty="beginner",
            next_focus_areas=["fundamentals", "introduction"]
        )

    def _load_existing_data(self):
        """Load existing learner profiles and session data."""

        # Load learner profiles
        profiles_file = self.data_storage / "learner_profiles.json"
        if profiles_file.exists():
            try:
                with open(profiles_file, 'r') as f:
                    self.learner_profiles = json.load(f)
            except Exception as e:
                print(f"Error loading learner profiles: {e}")

    def _save_session_data(self, session: LearningSession):
        """Save completed session data to storage."""

        session_data = {
            "session_id": session.session_id,
            "learner_id": session.learner_id,
            "topic": session.topic,
            "start_time": session.start_time,
            "end_time": session.end_time,
            "emotional_states": session.emotional_states,
            "interactions": session.interactions,
            "content_modules": session.content_modules,
            "progress_metrics": session.progress_metrics,
            "behavioral_insights": session.behavioral_insights
        }

        # Save session data
        session_file = self.data_storage / f"session_{session.session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)

        # Save updated learner profiles
        profiles_file = self.data_storage / "learner_profiles.json"
        with open(profiles_file, 'w') as f:
            json.dump(self.learner_profiles, f, indent=2, default=str)

    def _load_historical_sessions(self, learner_id: str, cutoff_time: float) -> List[Dict[str, Any]]:
        """Load historical session data for a learner."""

        sessions = []

        # Find all session files for this learner
        for session_file in self.data_storage.glob(f"session_{learner_id}_*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)

                if session_data["start_time"] >= cutoff_time:
                    sessions.append(session_data)

            except Exception as e:
                print(f"Error loading session file {session_file}: {e}")

        return sessions
