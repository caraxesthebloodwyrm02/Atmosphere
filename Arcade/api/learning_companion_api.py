#!/usr/bin/env python3
"""
Learning Companion API Endpoints
================================

REST API endpoints for the Emotionally-Adaptive Learning Companion.
Integrates with the Arcade Terminal server for testing and demonstration.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
from pathlib import Path

# Import the learning companion
try:
    from ..learning_companion.emotionally_adaptive_learning_companion import EmotionallyAdaptiveLearningCompanion
except ImportError:
    # For direct testing
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from learning_companion.emotionally_adaptive_learning_companion import EmotionallyAdaptiveLearningCompanion

# Create router
router = APIRouter(prefix="/learning", tags=["learning_companion"])

@router.get("/", summary="Learning Companion API Root", 
          description="Welcome to the Emotionally-Adaptive Learning Companion API")
async def root():
    """Return welcome message and available endpoints."""
    return {
        "message": "Welcome to the Emotionally-Adaptive Learning Companion API",
        "endpoints": [
            {"path": "/learning/", "method": "GET", "description": "API root (this page)"},
            {"path": "/learning/session/start", "method": "POST", "description": "Start a new learning session"},
            {"path": "/learning/session/{session_id}", "method": "GET", "description": "Get session status"},
            {"path": "/learning/session/{session_id}/end", "method": "POST", "description": "End a learning session"},
            {"path": "/learning/interact", "method": "POST", "description": "Process a learning interaction"},
            {"path": "/learning/progress/{learner_id}", "method": "GET", "description": "Get learning progress"},
            {"path": "/learning/topics", "method": "GET", "description": "Get available learning topics"},
            {"path": "/learning/demo", "method": "GET", "description": "Run a demonstration of the learning companion"}
        ]
    }

# Initialize learning companion
learning_companion = EmotionallyAdaptiveLearningCompanion()

# Pydantic models for API
class LearnerAssessment(BaseModel):
    response_times: Optional[List[float]] = []
    error_count: Optional[int] = 0
    total_attempts: Optional[int] = 1
    help_requests: Optional[int] = 0
    session_duration: Optional[float] = 0.0
    interaction_frequency: Optional[float] = 0.0
    content_difficulty: Optional[float] = 0.5
    progress_rate: Optional[float] = 0.0
    time_since_last_interaction: Optional[float] = 0.0

class InteractionData(BaseModel):
    response_time: Optional[float] = None
    confidence: Optional[float] = None
    exploration_depth: Optional[str] = None
    frustration_level: Optional[float] = None
    topic: Optional[str] = None
    urgent: Optional[bool] = None
    stuck_completely: Optional[bool] = None
    module_index: Optional[int] = None
    success_rate: Optional[float] = None
    comprehension_level: Optional[str] = None

class ProcessInteractionRequest(BaseModel):
    session_id: str
    interaction_type: str
    interaction_data: InteractionData

class StartSessionRequest(BaseModel):
    learner_id: str
    topic: str = "python_functions"
    initial_assessment: Optional[LearnerAssessment] = None

@router.post("/session/start")
async def start_learning_session(request: StartSessionRequest):
    """
    Start a new emotionally-adaptive learning session.

    Args:
        request: Session start request data

    Returns:
        Session initialization data
    """
    try:
        # Convert Pydantic model to dict
        assessment_data = request.initial_assessment.dict() if request.initial_assessment else None

        result = await learning_companion.start_learning_session(
            learner_id=request.learner_id,
            topic=request.topic,
            initial_assessment=assessment_data
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start learning session: {str(e)}")

@router.post("/session/interact")
async def process_learning_interaction(
    request: ProcessInteractionRequest,
    background_tasks: BackgroundTasks
):
    """
    Process a learning interaction and adapt content accordingly.

    Args:
        request: Interaction request with session_id, type, and data

    Returns:
        Response with next content or adaptation
    """
    try:
        result = await learning_companion.process_interaction(
            session_id=request.session_id,
            interaction_type=request.interaction_type,
            interaction_data=request.interaction_data.dict()
        )

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process interaction: {str(e)}")

@router.post("/session/end/{session_id}")
async def end_learning_session(session_id: str):
    """
    End a learning session and get comprehensive feedback.

    Args:
        session_id: Active learning session ID

    Returns:
        Session completion report
    """
    try:
        result = await learning_companion.end_learning_session(session_id)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end learning session: {str(e)}")

@router.get("/session/status/{session_id}")
async def get_session_status(session_id: str):
    """
    Get current status of a learning session.

    Args:
        session_id: Learning session ID

    Returns:
        Session status information
    """
    try:
        result = learning_companion.get_session_status(session_id)

        return {
            "success": True,
            "data": result
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")

@router.get("/progress/{learner_id}")
async def get_learning_progress(
    learner_id: str,
    topic: Optional[str] = None
):
    """
    Get comprehensive learning progress for a learner.

    Args:
        learner_id: Unique learner identifier
        topic: Optional specific topic filter

    Returns:
        Learning progress data
    """
    try:
        progress = learning_companion.progress_tracker.get_learning_progress(learner_id, topic)

        return {
            "success": True,
            "data": {
                "learner_id": progress.learner_id,
                "topic": progress.topic,
                "overall_mastery": progress.overall_mastery,
                "skill_breakdown": progress.skill_breakdown,
                "learning_velocity": progress.learning_velocity,
                "recommended_difficulty": progress.recommended_difficulty,
                "next_focus_areas": progress.next_focus_areas
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get learning progress: {str(e)}")

@router.get("/insights/{learner_id}")
async def get_behavioral_insights(
    learner_id: str,
    time_window_days: int = 30
):
    """
    Get behavioral insights and learning patterns for a learner.

    Args:
        learner_id: Unique learner identifier
        time_window_days: Analysis time window in days

    Returns:
        Behavioral insights and recommendations
    """
    try:
        insights = learning_companion.progress_tracker.get_behavioral_insights(
            learner_id, time_window_days
        )

        return {
            "success": True,
            "data": insights
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get behavioral insights: {str(e)}")

@router.get("/topics")
async def get_available_topics():
    """
    Get list of available learning topics.

    Returns:
        List of available learning topics
    """
    try:
        topics = learning_companion.get_available_topics()

        return {
            "success": True,
            "data": {
                "topics": topics,
                "count": len(topics)
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")

@router.post("/demo/run")
async def run_learning_demo():
    """
    Run a comprehensive learning companion demonstration.

    Returns:
        Demo execution results
    """
    try:
        # Run the demo script logic here
        demo_results = await run_demo_scenarios()

        return {
            "success": True,
            "data": demo_results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo execution failed: {str(e)}")

@router.get("/status")
async def get_learning_companion_status():
    """
    Get the status of the learning companion system.

    Returns:
        System status and capabilities
    """
    try:
        # Get basic system info
        topics = learning_companion.get_available_topics()

        return {
            "success": True,
            "data": {
                "system_status": "operational",
                "available_topics": topics,
                "emotional_states_supported": [
                    "exploratory", "creative", "analytical",
                    "urgent", "calm", "frustrated", "confused", "engaged"
                ],
                "content_types": [
                    "interactive_exercise", "concept_explanation",
                    "visual_demonstration", "practical_project",
                    "quiz_assessment", "story_based_learning"
                ],
                "intervention_types": [
                    "stress_relief", "engagement_boost",
                    "confusion_support", "frustration_relief"
                ],
                "capabilities": [
                    "real_time_emotional_detection",
                    "adaptive_content_routing",
                    "intervention_triggers",
                    "progress_tracking",
                    "behavioral_analytics"
                ]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")

async def run_demo_scenarios() -> Dict[str, Any]:
    """Run demonstration scenarios for the learning companion."""

    demo_results = {
        "scenarios_run": 0,
        "sessions_completed": 0,
        "interventions_triggered": 0,
        "adaptations_performed": 0,
        "emotional_states_detected": [],
        "scenario_results": []
    }

    # Demo Scenario 1: Exploratory Learner
    try:
        print("🎯 Running Demo Scenario 1: Exploratory Learner")

        exploratory_assessment = {
            'response_times': [0.5, 0.8, 0.6],
            'error_count': 1,
            'total_attempts': 5,
            'help_requests': 0,
            'session_duration': 120,
            'interaction_frequency': 2.5,
            'content_difficulty': 0.6,
            'progress_rate': 0.8,
            'time_since_last_interaction': 0
        }

        session = await learning_companion.start_learning_session(
            "demo_exploratory", "python_functions", exploratory_assessment
        )

        # Simulate interactions
        interactions = [
            ("correct_answer", {"response_time": 0.7, "confidence": 0.9}),
            ("module_completed", {"module_index": 0, "success_rate": 0.9})
        ]

        for interaction_type, data in interactions:
            await learning_companion.process_interaction(session["session_id"], interaction_type, data)

        completion = await learning_companion.end_learning_session(session["session_id"])

        demo_results["scenarios_run"] += 1
        demo_results["sessions_completed"] += 1
        demo_results["emotional_states_detected"].append("exploratory")
        demo_results["scenario_results"].append({
            "scenario": "exploratory_learner",
            "success": True,
            "emotional_journey": completion["completion_summary"]["emotional_journey"]
        })

    except Exception as e:
        demo_results["scenario_results"].append({
            "scenario": "exploratory_learner",
            "success": False,
            "error": str(e)
        })

    # Demo Scenario 2: Frustrated Learner with Intervention
    try:
        print("🎯 Running Demo Scenario 2: Frustrated Learner with Intervention")

        frustrated_assessment = {
            'response_times': [4.5, 5.2, 6.1],
            'error_count': 4,
            'total_attempts': 5,
            'help_requests': 3,
            'session_duration': 180,
            'interaction_frequency': 0.8,
            'content_difficulty': 0.8,
            'progress_rate': 0.2,
            'time_since_last_interaction': 30
        }

        session = await learning_companion.start_learning_session(
            "demo_frustrated", "python_functions", frustrated_assessment
        )

        # Simulate frustration-building interactions
        interactions = [
            ("incorrect_answer", {"response_time": 5.0, "frustration_level": 0.8}),
            ("incorrect_answer", {"response_time": 6.0, "error_streak": 2}),
            ("help_request", {"urgent": True, "stuck_completely": True})
        ]

        interventions_detected = 0
        for interaction_type, data in interactions:
            response = await learning_companion.process_interaction(session["session_id"], interaction_type, data)
            if "intervention_type" in response:
                interventions_detected += 1

        completion = await learning_companion.end_learning_session(session["session_id"])

        demo_results["scenarios_run"] += 1
        demo_results["sessions_completed"] += 1
        demo_results["interventions_triggered"] += interventions_detected
        demo_results["emotional_states_detected"].append("frustrated")
        demo_results["scenario_results"].append({
            "scenario": "frustrated_learner",
            "success": True,
            "interventions_triggered": interventions_detected,
            "emotional_journey": completion["completion_summary"]["emotional_journey"]
        })

    except Exception as e:
        demo_results["scenario_results"].append({
            "scenario": "frustrated_learner",
            "success": False,
            "error": str(e)
        })

    # Demo Scenario 3: Emotional Shift
    try:
        print("🎯 Running Demo Scenario 3: Emotional Shift Adaptation")

        analytical_assessment = {
            'response_times': [2.0, 1.8, 2.2],
            'error_count': 0,
            'total_attempts': 5,
            'help_requests': 0,
            'session_duration': 200,
            'interaction_frequency': 1.8,
            'content_difficulty': 0.6,
            'progress_rate': 0.7,
            'time_since_last_interaction': 0
        }

        session = await learning_companion.start_learning_session(
            "demo_shift", "python_functions", analytical_assessment
        )

        # Start analytical, then shift to frustration
        interactions = [
            ("correct_answer", {"response_time": 2.0, "methodical_approach": True}),
            ("incorrect_answer", {"response_time": 4.0, "frustration_building": True}),
            ("incorrect_answer", {"response_time": 5.0, "error_streak": 2}),
            ("incorrect_answer", {"response_time": 6.0, "losing_confidence": True})
        ]

        adaptations_detected = 0
        for interaction_type, data in interactions:
            response = await learning_companion.process_interaction(session["session_id"], interaction_type, data)
            if response.get("adaptation_type") == "emotional_shift":
                adaptations_detected += 1

        completion = await learning_companion.end_learning_session(session["session_id"])

        demo_results["scenarios_run"] += 1
        demo_results["sessions_completed"] += 1
        demo_results["adaptations_performed"] += adaptations_detected
        demo_results["emotional_states_detected"].extend(["analytical", "frustrated"])
        demo_results["scenario_results"].append({
            "scenario": "emotional_shift",
            "success": True,
            "adaptations_performed": adaptations_detected,
            "emotional_journey": completion["completion_summary"]["emotional_journey"]
        })

    except Exception as e:
        demo_results["scenario_results"].append({
            "scenario": "emotional_shift",
            "success": False,
            "error": str(e)
        })

    demo_results["overall_success"] = all(result["success"] for result in demo_results["scenario_results"])

    return demo_results

# Export the router for integration with main server
__all__ = ["router"]
