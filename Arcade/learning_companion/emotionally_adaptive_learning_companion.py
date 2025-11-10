#!/usr/bin/env python3
"""
Emotionally-Adaptive Learning Companion
=====================================

Main orchestrator for the emotionally-adaptive learning system that integrates
emotional detection, adaptive content delivery, and progress tracking.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from .emotional_detector import EmotionalDetector, EmotionalState
from .adaptive_content_engine import AdaptiveContentEngine, AdaptedContent
from .learning_progress_tracker import LearningProgressTracker, LearningProgress

@dataclass
class LearningSession:
    session_id: str
    learner_id: str
    topic: str
    start_time: float
    current_emotional_state: Optional[EmotionalState]
    adapted_content: Optional[AdaptedContent]
    progress_data: Dict[str, Any]
    active_interventions: List[Dict[str, Any]]

class EmotionallyAdaptiveLearningCompanion:
    """Main orchestrator for emotionally-adaptive learning experiences."""

    def __init__(self):
        self.emotional_detector = EmotionalDetector()
        self.content_engine = AdaptiveContentEngine()
        self.progress_tracker = LearningProgressTracker()

        self.active_sessions: Dict[str, LearningSession] = {}
        self.intervention_handlers: Dict[str, callable] = {}

        # Register intervention handlers
        self._register_intervention_handlers()

    async def start_learning_session(
        self,
        learner_id: str,
        topic: str,
        initial_assessment: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Start a new emotionally-adaptive learning session.

        Args:
            learner_id: Unique identifier for the learner
            topic: Learning topic (e.g., "python_functions")
            initial_assessment: Optional initial learner assessment data

        Returns:
            Session initialization data
        """

        print("🌟 Starting Emotionally-Adaptive Learning Session")
        print("=" * 50)

        # Get learner progress history
        learner_progress = self.progress_tracker.get_learning_progress(learner_id, topic)

        # Start progress tracking session
        session_id = self.progress_tracker.start_learning_session(learner_id, topic)

        # Perform initial emotional assessment
        initial_session_data = initial_assessment or {
            'response_times': [],
            'error_count': 0,
            'total_attempts': 0,
            'help_requests': 0,
            'session_duration': 0,
            'interaction_frequency': 0,
            'content_difficulty': 0.5,
            'progress_rate': 0.0,
            'time_since_last_interaction': 0
        }

        initial_emotional_state = await self.emotional_detector.detect_emotional_state(
            learner_id, initial_session_data
        )

        # Generate adaptive content based on emotional state and progress
        adapted_content = await self.content_engine.generate_adaptive_content(
            learner_id=learner_id,
            topic=topic,
            emotional_state=initial_emotional_state,
            learning_history={
                'mastery_level': learner_progress.overall_mastery,
                'skill_breakdown': learner_progress.skill_breakdown,
                'emotional_patterns': learner_progress.emotional_patterns
            }
        )

        # Create learning session
        session = LearningSession(
            session_id=session_id,
            learner_id=learner_id,
            topic=topic,
            start_time=time.time(),
            current_emotional_state=initial_emotional_state,
            adapted_content=adapted_content,
            progress_data={},
            active_interventions=[]
        )

        self.active_sessions[session_id] = session

        # Generate welcome message and first content
        welcome_response = self._generate_session_welcome(session, learner_progress)

        return {
            "session_id": session_id,
            "status": "active",
            "welcome_message": welcome_response,
            "initial_content": self._prepare_content_delivery(adapted_content.content_path[0]),
            "progress_checkpoint": adapted_content.progress_checkpoints[0] if adapted_content.progress_checkpoints else None,
            "estimated_duration": adapted_content.estimated_completion
        }

    async def process_interaction(
        self,
        session_id: str,
        interaction_type: str,
        interaction_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process learner interaction and adapt content accordingly.

        Args:
            session_id: Active learning session ID
            interaction_type: Type of interaction (answer, help_request, etc.)
            interaction_data: Interaction details and metadata

        Returns:
            Response with next content or adaptation
        """

        if session_id not in self.active_sessions:
            return {"error": "Session not found or expired"}

        session = self.active_sessions[session_id]

        # Record interaction
        self.progress_tracker.record_interaction(session_id, interaction_type, interaction_data)

        # Update progress data
        self._update_session_progress(session, interaction_type, interaction_data)

        # Check for intervention triggers
        intervention_response = await self._check_intervention_triggers(session)
        if intervention_response:
            return intervention_response

        # Assess if emotional re-evaluation is needed
        needs_emotional_check = self._should_reassess_emotion(
            session, interaction_type, interaction_data
        )

        if needs_emotional_check:
            # Re-assess emotional state
            current_session_data = self._compile_session_data(session)
            new_emotional_state = await self.emotional_detector.detect_emotional_state(
                session.learner_id, current_session_data
            )

            # Check if significant emotional change occurred
            if self._emotional_state_changed(session.current_emotional_state, new_emotional_state):
                # Generate new adapted content path
                adapted_content = await self.content_engine.generate_adaptive_content(
                    learner_id=session.learner_id,
                    topic=session.topic,
                    emotional_state=new_emotional_state,
                    learning_history=self._get_learning_history(session.learner_id)
                )

                session.current_emotional_state = new_emotional_state
                session.adapted_content = adapted_content

                # Record emotional state change
                self.progress_tracker.record_emotional_state(session_id, new_emotional_state.__dict__)

                return {
                    "adaptation_type": "emotional_shift",
                    "new_emotional_state": {
                        "primary": new_emotional_state.primary_emotion.value,
                        "confidence": new_emotional_state.confidence,
                        "engagement": new_emotional_state.engagement_level
                    },
                    "adapted_content": self._prepare_content_delivery(adapted_content.content_path[0]),
                    "adaptation_reason": adapted_content.adaptation_reasoning
                }

        # Record emotional state for trend analysis
        if session.current_emotional_state:
            self.progress_tracker.record_emotional_state(session_id, session.current_emotional_state.__dict__)

        # Determine next content or response
        next_response = self._determine_next_interaction(session, interaction_type, interaction_data)

        return next_response

    async def end_learning_session(self, session_id: str) -> Dict[str, Any]:
        """
        End learning session and provide comprehensive feedback.

        Args:
            session_id: Active learning session ID

        Returns:
            Session completion report
        """

        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        # End progress tracking
        progress_report = self.progress_tracker.end_learning_session(session_id)

        # Generate behavioral insights
        behavioral_insights = self.progress_tracker.get_behavioral_insights(session.learner_id)

        # Generate completion summary
        completion_summary = self._generate_completion_summary(session, progress_report)

        # Remove from active sessions
        del self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "status": "completed",
            "completion_summary": completion_summary,
            "progress_report": progress_report,
            "behavioral_insights": behavioral_insights,
            "next_session_recommendations": progress_report.get("next_session_suggestions", {})
        }

    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get current status of a learning session."""

        if session_id not in self.active_sessions:
            return {"error": "Session not found"}

        session = self.active_sessions[session_id]

        return {
            "session_id": session_id,
            "learner_id": session.learner_id,
            "topic": session.topic,
            "duration": time.time() - session.start_time,
            "current_emotion": session.current_emotional_state.primary_emotion.value if session.current_emotional_state else None,
            "content_progress": len(session.progress_data.get("completed_modules", [])),
            "active_interventions": len(session.active_interventions)
        }

    def get_available_topics(self) -> List[str]:
        """Get list of available learning topics."""
        return self.content_engine.get_available_topics()

    def _register_intervention_handlers(self):
        """Register handlers for different types of interventions."""

        self.intervention_handlers = {
            "stress_intervention": self._handle_stress_intervention,
            "engagement_boost": self._handle_engagement_boost,
            "confusion_support": self._handle_confusion_support,
            "frustration_relief": self._handle_frustration_relief
        }

    async def _check_intervention_triggers(self, session: LearningSession) -> Optional[Dict[str, Any]]:
        """Check if any intervention triggers are activated."""

        if not session.adapted_content or not session.adapted_content.intervention_triggers:
            return None

        for trigger in session.adapted_content.intervention_triggers:
            if self._evaluate_trigger_condition(trigger, session):
                # Execute intervention
                intervention_response = await self._execute_intervention(trigger, session)
                if intervention_response:
                    return intervention_response

        return None

    def _evaluate_trigger_condition(self, trigger: Dict[str, Any], session: LearningSession) -> bool:
        """Evaluate if an intervention trigger condition is met."""

        condition = trigger.get("condition", "")
        trigger_type = trigger.get("trigger_type", "")

        if "stress_level > 0.7" in condition:
            return session.current_emotional_state and session.current_emotional_state.stress_indicators > 0.7

        if "engagement_level < 0.3" in condition:
            return session.current_emotional_state and session.current_emotional_state.engagement_level < 0.3

        if "primary_emotion == confused" in condition:
            return (session.current_emotional_state and
                    session.current_emotional_state.primary_emotion.value == "confused")

        if "primary_emotion == frustrated" in condition:
            return (session.current_emotional_state and
                    session.current_emotional_state.primary_emotion.value == "frustrated")

        return False

    async def _execute_intervention(self, trigger: Dict[str, Any], session: LearningSession) -> Dict[str, Any]:
        """Execute an intervention based on trigger type."""

        trigger_type = trigger.get("trigger_type", "")
        handler = self.intervention_handlers.get(trigger_type)

        if handler:
            return await handler(trigger, session)

        return None

    async def _handle_stress_intervention(self, trigger: Dict[str, Any], session: LearningSession) -> Dict[str, Any]:
        """Handle stress intervention."""

        return {
            "intervention_type": "stress_relief",
            "message": trigger.get("message", "I notice you might be feeling stressed. Would you like to take a short break?"),
            "suggestion": "Try the breathing exercise: Inhale for 4 counts, hold for 4, exhale for 4.",
            "options": ["Continue with break", "Skip break and continue"]
        }

    async def _handle_engagement_boost(self, trigger: Dict[str, Any], session: LearningSession) -> Dict[str, Any]:
        """Handle engagement boost intervention."""

        return {
            "intervention_type": "engagement_boost",
            "message": trigger.get("message", "Let's try a more hands-on approach to keep things engaging!"),
            "new_content_type": "interactive_exercise",
            "engagement_activities": ["hands_on_exercise", "real_world_example", "gamified_challenge"]
        }

    async def _handle_confusion_support(self, trigger: Dict[str, Any], session: LearningSession) -> Dict[str, Any]:
        """Handle confusion support intervention."""

        return {
            "intervention_type": "clarification_support",
            "message": trigger.get("message", "I can see this concept might be tricky. Let me explain it differently."),
            "clarification_methods": ["simplified_explanation", "visual_analogy", "step_by_step_breakdown"],
            "additional_resources": ["concept_map", "video_explanation", "practice_examples"]
        }

    async def _handle_frustration_relief(self, trigger: Dict[str, Any], session: LearningSession) -> Dict[str, Any]:
        """Handle frustration relief intervention."""

        return {
            "intervention_type": "difficulty_adjustment",
            "message": trigger.get("message", "This seems challenging. Let's break it down into smaller, manageable steps."),
            "difficulty_adjustment": "reduce_complexity",
            "support_mechanisms": ["extra_hints", "simplified_examples", "encouragement_messages"],
            "progress_preservation": True
        }

    def _should_reassess_emotion(self, session: LearningSession, interaction_type: str, interaction_data: Dict[str, Any]) -> bool:
        """Determine if emotional state should be reassessed."""

        # Reassess after significant interactions
        significant_interactions = ["incorrect_answer", "help_request", "long_pause", "error_sequence"]

        if interaction_type in significant_interactions:
            return True

        # Reassess periodically (every 5 interactions)
        interaction_count = len(session.progress_data.get("interactions", []))
        if interaction_count > 0 and interaction_count % 5 == 0:
            return True

        # Reassess if engagement/stress indicators change significantly
        if session.current_emotional_state:
            recent_engagement = interaction_data.get("engagement_level", session.current_emotional_state.engagement_level)
            if abs(recent_engagement - session.current_emotional_state.engagement_level) > 0.3:
                return True

        return False

    def _emotional_state_changed(self, old_state: EmotionalState, new_state: EmotionalState) -> bool:
        """Check if emotional state has changed significantly."""

        if not old_state or not new_state:
            return True

        # Check primary emotion change
        if old_state.primary_emotion != new_state.primary_emotion:
            return True

        # Check significant engagement change
        if abs(old_state.engagement_level - new_state.engagement_level) > 0.3:
            return True

        # Check significant stress change
        if abs(old_state.stress_indicators - new_state.stress_indicators) > 0.3:
            return True

        return False

    def _update_session_progress(self, session: LearningSession, interaction_type: str, interaction_data: Dict[str, Any]):
        """Update session progress data."""

        if "interactions" not in session.progress_data:
            session.progress_data["interactions"] = []

        session.progress_data["interactions"].append({
            "type": interaction_type,
            "data": interaction_data,
            "timestamp": time.time()
        })

        # Update completion tracking
        if interaction_type == "module_completed":
            if "completed_modules" not in session.progress_data:
                session.progress_data["completed_modules"] = []
            session.progress_data["completed_modules"].append(interaction_data.get("module_id"))

    def _compile_session_data(self, session: LearningSession) -> Dict[str, Any]:
        """Compile current session data for emotional analysis."""

        interactions = session.progress_data.get("interactions", [])

        # Calculate metrics from interactions
        response_times = [i["data"].get("response_time", 1.0) for i in interactions if "response_time" in i["data"]]
        error_count = sum(1 for i in interactions if i["type"] == "incorrect_answer")
        total_attempts = len([i for i in interactions if i["type"] in ["correct_answer", "incorrect_answer"]])
        help_requests = sum(1 for i in interactions if i["type"] == "help_request")

        session_duration = time.time() - session.start_time
        interaction_frequency = len(interactions) / max(session_duration / 60, 1)  # per minute

        # Calculate progress rate
        completed_modules = len(session.progress_data.get("completed_modules", []))
        total_modules = len(session.adapted_content.content_path) if session.adapted_content else 1
        progress_rate = completed_modules / total_modules

        return {
            'response_times': response_times,
            'error_count': error_count,
            'total_attempts': total_attempts,
            'help_requests': help_requests,
            'session_duration': session_duration,
            'interaction_frequency': interaction_frequency,
            'content_difficulty': 0.5,  # Could be dynamic
            'progress_rate': progress_rate,
            'time_since_last_interaction': 0  # Could track actual timing
        }

    def _get_learning_history(self, learner_id: str) -> Dict[str, Any]:
        """Get learning history for content adaptation."""

        progress = self.progress_tracker.get_learning_progress(learner_id)

        return {
            'mastery_level': progress.overall_mastery,
            'skill_breakdown': progress.skill_breakdown,
            'emotional_patterns': progress.emotional_patterns
        }

    def _generate_session_welcome(self, session: LearningSession, progress: LearningProgress) -> str:
        """Generate personalized welcome message."""

        emotion_desc = session.current_emotional_state.primary_emotion.value if session.current_emotional_state else "neutral"

        welcome_parts = [
            f"🌟 Welcome to your emotionally-adaptive learning session on {session.topic.replace('_', ' ')}!",
            f"🎭 I detect you're feeling {emotion_desc} - I've adapted the content accordingly.",
            f"📊 Your current mastery level: {progress.overall_mastery:.1%}"
        ]

        if progress.overall_mastery < 0.3:
            welcome_parts.append("🎯 We'll start with foundational concepts and build from there.")
        elif progress.overall_mastery < 0.7:
            welcome_parts.append("🚀 Let's build on your existing knowledge with some challenges!")
        else:
            welcome_parts.append("🏆 Ready for advanced concepts and mastery exercises!")

        return " ".join(welcome_parts)

    def _prepare_content_delivery(self, content_module) -> Dict[str, Any]:
        """Prepare content module for delivery to learner."""

        return {
            "module_id": content_module.content_id,
            "title": content_module.title,
            "content_type": content_module.content_type.value,
            "difficulty": content_module.difficulty.value,
            "estimated_duration": content_module.estimated_duration,
            "content_data": content_module.content_data,
            "learning_objectives": content_module.learning_objectives,
            "success_criteria": content_module.success_criteria
        }

    def _determine_next_interaction(self, session: LearningSession, interaction_type: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the next interaction based on current state."""

        # Handle different interaction types
        if interaction_type == "correct_answer":
            return {
                "response_type": "positive_feedback",
                "message": "Excellent! That's correct. 🎉",
                "next_action": "continue_module"
            }

        elif interaction_type == "incorrect_answer":
            return {
                "response_type": "encouraging_feedback",
                "message": "Not quite right, but you're learning! Let's try a different approach.",
                "hint_provided": True,
                "next_action": "retry_with_hint"
            }

        elif interaction_type == "help_request":
            return {
                "response_type": "support_provided",
                "message": "I'm here to help! Here's some guidance:",
                "additional_support": True,
                "next_action": "continue_with_support"
            }

        elif interaction_type == "module_completed":
            # Check if there are more modules in the path
            current_module_index = interaction_data.get("module_index", 0)
            if session.adapted_content and current_module_index + 1 < len(session.adapted_content.content_path):
                next_module = session.adapted_content.content_path[current_module_index + 1]
                return {
                    "response_type": "module_completed",
                    "message": "Great job completing that module! Ready for the next one?",
                    "next_module": self._prepare_content_delivery(next_module),
                    "progress_update": f"Module {current_module_index + 1} of {len(session.adapted_content.content_path)} completed"
                }
            else:
                return {
                    "response_type": "session_progress",
                    "message": "Excellent work! You've completed all modules for this session.",
                    "next_action": "session_ready_for_completion"
                }

        # Default response
        return {
            "response_type": "acknowledgment",
            "message": "I see your interaction. Let's continue learning!",
            "next_action": "continue_module"
        }

    def _generate_completion_summary(self, session: LearningSession, progress_report: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive session completion summary."""

        duration_minutes = (time.time() - session.start_time) / 60

        # Calculate session effectiveness
        modules_completed = len(session.progress_data.get("completed_modules", []))
        total_modules = len(session.adapted_content.content_path) if session.adapted_content else 1
        completion_rate = modules_completed / total_modules

        # Emotional journey summary
        emotional_journey = "stable"
        if session.current_emotional_state and session.adapted_content:
            if session.current_emotional_state.engagement_level > 0.8:
                emotional_journey = "highly_engaged"
            elif session.current_emotional_state.stress_indicators > 0.6:
                emotional_journey = "challenging"
            else:
                emotional_journey = "balanced"

        return {
            "session_topic": session.topic,
            "duration_minutes": round(duration_minutes, 1),
            "modules_completed": modules_completed,
            "completion_rate": completion_rate,
            "emotional_journey": emotional_journey,
            "learning_effectiveness": progress_report.get("performance_metrics", {}).get("learning_efficiency", 0),
            "key_achievements": [
                f"Completed {completion_rate:.1%} of planned modules",
                f"Maintained {emotional_journey.replace('_', ' ')} learning experience",
                f"Demonstrated {progress_report.get('performance_metrics', {}).get('emotional_stability', 0):.1%} emotional stability"
            ],
            "personal_growth": self._assess_personal_growth(session, progress_report)
        }

    def _assess_personal_growth(self, session: LearningSession, progress_report: Dict[str, Any]) -> str:
        """Assess personal growth during the session."""

        growth_indicators = []

        # Check progress improvement
        if progress_report.get("performance_metrics", {}).get("learning_efficiency", 0) > 1.5:
            growth_indicators.append("rapid skill acquisition")

        # Check emotional resilience
        emotional_stability = progress_report.get("performance_metrics", {}).get("emotional_stability", 0)
        if emotional_stability > 0.8:
            growth_indicators.append("strong emotional resilience")
        elif emotional_stability > 0.6:
            growth_indicators.append("developing emotional awareness")

        # Check completion success
        completion_rate = len(session.progress_data.get("completed_modules", [])) / len(session.adapted_content.content_path) if session.adapted_content else 0
        if completion_rate > 0.8:
            growth_indicators.append("consistent task completion")
        elif completion_rate > 0.5:
            growth_indicators.append("steady progress development")

        if growth_indicators:
            return f"You showed {' and '.join(growth_indicators)} during this session."
        else:
            return "This session provided valuable learning experience and foundation building."
