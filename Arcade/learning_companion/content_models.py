#!/usr/bin/env python3
"""
Content Models for Learning Companion
====================================

Shared data models and enums for the learning companion system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List

class ContentType(Enum):
    INTERACTIVE_EXERCISE = "interactive_exercise"
    CONCEPT_EXPLANATION = "concept_explanation"
    VISUAL_DEMONSTRATION = "visual_demonstration"
    PRACTICAL_PROJECT = "practical_project"
    QUIZ_ASSESSMENT = "quiz_assessment"
    STORY_BASED_LEARNING = "story_based_learning"
    BREAK_ACTIVITY = "break_activity"

class DifficultyLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

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
class ContentModule:
    content_id: str
    title: str
    content_type: ContentType
    difficulty: DifficultyLevel
    emotional_alignment: List[Emotion]
    estimated_duration: int  # minutes
    prerequisites: List[str]
    learning_objectives: List[str]
    content_data: dict
    success_criteria: dict

@dataclass
class AdaptedContent:
    session_id: str
    learner_id: str
    emotional_state: 'EmotionalState'  # Forward reference to avoid import
    content_path: List[ContentModule]
    adaptation_reasoning: str
    estimated_completion: int
    progress_checkpoints: List[dict]
    intervention_triggers: List[dict]
