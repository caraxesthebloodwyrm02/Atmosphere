#!/usr/bin/env python3
"""
Adaptive Content Engine for Learning Companion
============================================

Dynamically generates and adapts educational content based on learner emotional states
and optimal learning paths determined by emotional routing.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import random

from .emotional_detector import Emotion, EmotionalState

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
    content_data: Dict[str, Any]
    success_criteria: Dict[str, Any]

@dataclass
class AdaptedContent:
    session_id: str
    learner_id: str
    emotional_state: EmotionalState
    content_path: List[ContentModule]
    adaptation_reasoning: str
    estimated_completion: int
    progress_checkpoints: List[Dict[str, Any]]
    intervention_triggers: List[Dict[str, Any]]

class AdaptiveContentEngine:
    """Engine for generating emotionally-adaptive educational content."""

    def __init__(self):
        self.content_library: Dict[str, List[ContentModule]] = {}
        self.learning_paths: Dict[str, Dict[str, Any]] = {}
        self.emotional_routing_cache: Dict[str, Any] = {}

        # Initialize content library
        self._initialize_content_library()

    def _initialize_content_library(self):
        """Initialize the content library with emotion-aligned modules."""

        # Python Functions Content Modules
        self.content_library["python_functions"] = [
            ContentModule(
                content_id="func_intro_exploratory",
                title="Function Discovery Lab",
                content_type=ContentType.INTERACTIVE_EXERCISE,
                difficulty=DifficultyLevel.BEGINNER,
                emotional_alignment=[Emotion.EXPLORATORY, Emotion.CREATIVE],
                estimated_duration=15,
                prerequisites=[],
                learning_objectives=[
                    "Understand what functions are",
                    "Create basic function definitions",
                    "Experiment with function calls"
                ],
                content_data={
                    "exercise_prompt": "Let's discover functions by creating drawing patterns!",
                    "starter_code": """def draw_pattern(size):
    for i in range(size):
        print("*" * (i + 1))

# Try different sizes!
draw_pattern(3)""",
                    "hints": [
                        "What happens if you use letters instead of *?",
                        "Try making patterns with numbers!",
                        "What if size is 0?"
                    ],
                    "success_indicators": ["function_defined", "function_called", "experimentation_shown"]
                },
                success_criteria={
                    "function_creation": True,
                    "multiple_calls": True,
                    "experimentation": True
                }
            ),

            ContentModule(
                content_id="func_understanding_analytical",
                title="Function Anatomy Deep Dive",
                content_type=ContentType.CONCEPT_EXPLANATION,
                difficulty=DifficultyLevel.INTERMEDIATE,
                emotional_alignment=[Emotion.ANALYTICAL, Emotion.CALM],
                estimated_duration=20,
                prerequisites=["basic_function_creation"],
                learning_objectives=[
                    "Understand function components",
                    "Analyze function structure",
                    "Predict function behavior"
                ],
                content_data={
                    "concept_breakdown": {
                        "definition": "def function_name(parameters):",
                        "components": {
                            "def": "Keyword that defines a function",
                            "function_name": "Identifier for the function",
                            "parameters": "Optional inputs to the function",
                            "colon": "Starts the function body",
                            "body": "Indented code that runs when called"
                        }
                    },
                    "visual_diagram": "Function structure diagram would be here",
                    "examples": [
                        {"code": "def greet(name): return f'Hello {name}!'", "explanation": "Simple greeting function"},
                        {"code": "def calculate_area(length, width): return length * width", "explanation": "Mathematical function"}
                    ]
                },
                success_criteria={
                    "component_identification": True,
                    "behavior_prediction": True,
                    "concept_application": True
                }
            ),

            ContentModule(
                content_id="func_project_creative",
                title="Function Art Gallery",
                content_type=ContentType.PRACTICAL_PROJECT,
                difficulty=DifficultyLevel.INTERMEDIATE,
                emotional_alignment=[Emotion.CREATIVE, Emotion.ENGAGED],
                estimated_duration=30,
                prerequisites=["function_creation", "loop_understanding"],
                learning_objectives=[
                    "Apply functions creatively",
                    "Combine functions with loops",
                    "Create artistic outputs"
                ],
                content_data={
                    "project_prompt": "Create a function art gallery! Make functions that draw different patterns.",
                    "requirements": [
                        "At least 3 different drawing functions",
                        "Use loops creatively",
                        "Include user input for customization"
                    ],
                    "examples": [
                        "draw_pyramid(height)",
                        "draw_checkerboard(size)",
                        "draw_spiral(radius)"
                    ],
                    "bonus_challenges": [
                        "Add color support (if using graphics)",
                        "Create animated patterns",
                        "Make interactive art"
                    ]
                },
                success_criteria={
                    "multiple_functions": True,
                    "creative_application": True,
                    "user_interaction": True
                }
            ),

            ContentModule(
                content_id="func_troubleshooting_urgent",
                title="Function Emergency Repair",
                content_type=ContentType.INTERACTIVE_EXERCISE,
                difficulty=DifficultyLevel.BEGINNER,
                emotional_alignment=[Emotion.URGENT, Emotion.FRUSTRATED],
                estimated_duration=10,
                prerequisites=[],
                learning_objectives=[
                    "Identify common function errors",
                    "Apply quick fixes",
                    "Build debugging confidence"
                ],
                content_data={
                    "error_scenarios": [
                        {
                            "broken_code": "def greet(name) return f'Hello {name}'",
                            "error_type": "Missing colon",
                            "quick_fix": "Add ':' after parameters",
                            "working_code": "def greet(name): return f'Hello {name}'"
                        },
                        {
                            "broken_code": "def calculate(x, y) return x + y",
                            "error_type": "Missing colon",
                            "quick_fix": "Add ':' after parameters",
                            "working_code": "def calculate(x, y): return x + y"
                        }
                    ],
                    "debugging_tips": [
                        "Check for colons after function definitions",
                        "Ensure consistent indentation",
                        "Verify parameter usage in function body"
                    ]
                },
                success_criteria={
                    "error_identification": True,
                    "fix_application": True,
                    "confidence_restoration": True
                }
            ),

            ContentModule(
                content_id="func_meditation_calm",
                title="Function Mindful Practice",
                content_type=ContentType.STORY_BASED_LEARNING,
                difficulty=DifficultyLevel.BEGINNER,
                emotional_alignment=[Emotion.CALM, Emotion.ANALYTICAL],
                estimated_duration=12,
                prerequisites=["basic_coding"],
                learning_objectives=[
                    "Practice deliberate function creation",
                    "Understand function purpose and design",
                    "Appreciate code structure"
                ],
                content_data={
                    "meditation_script": """
                    *Close your eyes and take a deep breath*

                    Think of a function as a helpful assistant in your code kitchen.
                    It takes ingredients (parameters), follows a recipe (the function body),
                    and creates something wonderful (the return value).

                    Let's create a mindful function together...

                    *Pause for reflection*

                    What will your function help with today?
                    """,
                    "reflection_questions": [
                        "What does this function accomplish?",
                        "How does each part contribute to the whole?",
                        "When would you use this function?"
                    ],
                    "mindful_exercises": [
                        "Write a function comment explaining its purpose",
                        "Test your function with different inputs",
                        "Refactor for clarity and simplicity"
                    ]
                },
                success_criteria={
                    "mindful_creation": True,
                    "reflection_completed": True,
                    "understanding_demonstrated": True
                }
            )
        ]

    async def generate_adaptive_content(
        self,
        learner_id: str,
        topic: str,
        emotional_state: EmotionalState,
        learning_history: Dict[str, Any]
    ) -> AdaptedContent:
        """
        Generate emotionally-adaptive content based on learner state and optimal routing.

        Args:
            learner_id: Unique learner identifier
            topic: Learning topic (e.g., "python_functions")
            emotional_state: Current emotional state
            learning_history: Previous learning progress and patterns

        Returns:
            AdaptedContent with optimal learning path and modules
        """

        session_id = f"{learner_id}_{topic}_{int(asyncio.get_event_loop().time())}"

        # Determine optimal content path using emotional routing
        optimal_path = await self._route_emotional_content_path(
            topic, emotional_state, learning_history
        )

        # Generate adaptation reasoning
        adaptation_reasoning = self._generate_adaptation_reasoning(
            emotional_state, optimal_path, learning_history
        )

        # Calculate total estimated completion time
        estimated_completion = sum(module.estimated_duration for module in optimal_path)

        # Generate progress checkpoints
        progress_checkpoints = self._generate_progress_checkpoints(optimal_path, emotional_state)

        # Define intervention triggers
        intervention_triggers = self._generate_intervention_triggers(emotional_state)

        return AdaptedContent(
            session_id=session_id,
            learner_id=learner_id,
            emotional_state=emotional_state,
            content_path=optimal_path,
            adaptation_reasoning=adaptation_reasoning,
            estimated_completion=estimated_completion,
            progress_checkpoints=progress_checkpoints,
            intervention_triggers=intervention_triggers
        )

    async def _route_emotional_content_path(
        self,
        topic: str,
        emotional_state: EmotionalState,
        learning_history: Dict[str, Any]
    ) -> List[ContentModule]:
        """
        Route to optimal content path based on emotional state and learning history.
        Uses emotional routing principles similar to the Atmosphere system.
        """

        available_modules = self.content_library.get(topic, [])

        if not available_modules:
            # Return default exploration module
            return [self._get_default_exploratory_module()]

        # Score modules based on emotional alignment
        scored_modules = []
        for module in available_modules:
            score = self._calculate_emotional_alignment_score(module, emotional_state, learning_history)
            scored_modules.append((module, score))

        # Sort by score (highest first)
        scored_modules.sort(key=lambda x: x[1], reverse=True)

        # Select optimal path (typically 1-3 modules)
        optimal_path = []
        remaining_time = 45  # Max session time in minutes
        covered_objectives = set()

        for module, score in scored_modules:
            if score < 0.3:  # Skip poorly aligned modules
                continue

            if module.estimated_duration <= remaining_time:
                # Check if this module covers new objectives
                new_objectives = set(module.learning_objectives) - covered_objectives
                if new_objectives or len(optimal_path) == 0:  # Always include at least one module
                    optimal_path.append(module)
                    remaining_time -= module.estimated_duration
                    covered_objectives.update(module.learning_objectives)

            if len(optimal_path) >= 3 or remaining_time < 10:
                break

        # Ensure we have at least one module
        if not optimal_path:
            optimal_path = [scored_modules[0][0]]

        return optimal_path

    def _calculate_emotional_alignment_score(
        self,
        module: ContentModule,
        emotional_state: EmotionalState,
        learning_history: Dict[str, Any]
    ) -> float:
        """Calculate how well a content module aligns with learner's emotional state."""

        score = 0.0

        # Primary emotion alignment (40% weight)
        if emotional_state.primary_emotion in module.emotional_alignment:
            score += 0.4
        elif self._emotions_are_compatible(emotional_state.primary_emotion, module.emotional_alignment):
            score += 0.2

        # Secondary emotions alignment (20% weight)
        secondary_matches = sum(
            1 for emotion, _ in emotional_state.secondary_emotions
            if emotion in module.emotional_alignment
        )
        score += 0.2 * (secondary_matches / len(emotional_state.secondary_emotions) if emotional_state.secondary_emotions else 0)

        # Difficulty appropriateness (20% weight)
        difficulty_score = self._assess_difficulty_appropriateness(module.difficulty, learning_history)
        score += 0.2 * difficulty_score

        # Engagement and stress consideration (20% weight)
        engagement_score = self._calculate_engagement_alignment(
            module.content_type, emotional_state.engagement_level, emotional_state.stress_indicators
        )
        score += 0.2 * engagement_score

        return min(1.0, score)  # Cap at 1.0

    def _emotions_are_compatible(self, emotion: Emotion, alignment_list: List[Emotion]) -> bool:
        """Check if emotions are compatible for learning."""

        compatibility_map = {
            Emotion.EXPLORATORY: [Emotion.CREATIVE, Emotion.ENGAGED],
            Emotion.CREATIVE: [Emotion.EXPLORATORY, Emotion.ENGAGED],
            Emotion.ANALYTICAL: [Emotion.CALM, Emotion.ENGAGED],
            Emotion.CALM: [Emotion.ANALYTICAL, Emotion.ENGAGED],
            Emotion.URGENT: [Emotion.FRUSTRATED],  # Limited compatibility when urgent
            Emotion.FRUSTRATED: [Emotion.URGENT],  # May need immediate help
            Emotion.CONFUSED: [],  # Needs specific help
            Emotion.ENGAGED: [Emotion.EXPLORATORY, Emotion.CREATIVE, Emotion.ANALYTICAL]
        }

        return any(compat_emotion in alignment_list for compat_emotion in compatibility_map.get(emotion, []))

    def _assess_difficulty_appropriateness(self, difficulty: DifficultyLevel, learning_history: Dict[str, Any]) -> float:
        """Assess if difficulty level is appropriate based on learning history."""

        mastery_level = learning_history.get('mastery_level', 0.5)  # 0.0 to 1.0

        difficulty_scores = {
            DifficultyLevel.BEGINNER: 1.0 if mastery_level < 0.3 else 0.3,
            DifficultyLevel.INTERMEDIATE: 1.0 if 0.3 <= mastery_level < 0.7 else 0.5,
            DifficultyLevel.ADVANCED: 1.0 if 0.7 <= mastery_level < 0.9 else 0.7,
            DifficultyLevel.EXPERT: 1.0 if mastery_level >= 0.9 else 0.2
        }

        return difficulty_scores.get(difficulty, 0.5)

    def _calculate_engagement_alignment(self, content_type: ContentType, engagement: float, stress: float) -> float:
        """Calculate alignment based on content type and emotional indicators."""

        # Content type preferences based on emotional state
        if engagement > 0.7 and stress < 0.3:
            # High engagement, low stress: Prefer creative/interactive content
            preferred_types = [ContentType.INTERACTIVE_EXERCISE, ContentType.PRACTICAL_PROJECT, ContentType.STORY_BASED_LEARNING]
            return 1.0 if content_type in preferred_types else 0.6

        elif engagement > 0.5 and stress < 0.5:
            # Moderate engagement: Prefer balanced content
            preferred_types = [ContentType.CONCEPT_EXPLANATION, ContentType.VISUAL_DEMONSTRATION]
            return 1.0 if content_type in preferred_types else 0.7

        elif stress > 0.6:
            # High stress: Prefer calming, structured content
            preferred_types = [ContentType.QUIZ_ASSESSMENT, ContentType.CONCEPT_EXPLANATION]
            return 1.0 if content_type in preferred_types else 0.4

        else:
            # Default: Moderate preference
            return 0.7

    def _generate_adaptation_reasoning(
        self,
        emotional_state: EmotionalState,
        content_path: List[ContentModule],
        learning_history: Dict[str, Any]
    ) -> str:
        """Generate human-readable reasoning for content adaptation."""

        reasoning_parts = []

        # Primary emotion consideration
        emotion_desc = f"primary emotion ({emotional_state.primary_emotion.value}, {emotional_state.confidence:.1%} confidence)"
        reasoning_parts.append(f"Adapted for {emotion_desc}")

        # Engagement and stress context
        engagement_desc = "high" if emotional_state.engagement_level > 0.7 else "moderate" if emotional_state.engagement_level > 0.4 else "low"
        stress_desc = "elevated" if emotional_state.stress_indicators > 0.6 else "moderate" if emotional_state.stress_indicators > 0.3 else "low"

        reasoning_parts.append(f"with {engagement_desc} engagement and {stress_desc} stress indicators")

        # Content path summary
        if len(content_path) == 1:
            reasoning_parts.append(f"selected single focused module: {content_path[0].title}")
        else:
            module_types = [module.content_type.value.replace('_', ' ') for module in content_path]
            reasoning_parts.append(f"sequenced {len(content_path)} modules: {', '.join(module_types)}")

        # Learning history consideration
        mastery = learning_history.get('mastery_level', 0.5)
        reasoning_parts.append(f"based on {mastery:.1%} topic mastery")

        return ". ".join(reasoning_parts) + "."

    def _generate_progress_checkpoints(
        self,
        content_path: List[ContentModule],
        emotional_state: EmotionalState
    ) -> List[Dict[str, Any]]:
        """Generate progress checkpoints for the learning session."""

        checkpoints = []

        cumulative_time = 0
        for i, module in enumerate(content_path):
            cumulative_time += module.estimated_duration

            checkpoint = {
                "checkpoint_id": f"cp_{i+1}",
                "module_title": module.title,
                "estimated_time": cumulative_time,
                "success_criteria": module.success_criteria,
                "emotional_check": i < len(content_path) - 1,  # Check emotions between modules
                "intervention_available": emotional_state.stress_indicators > 0.5
            }

            checkpoints.append(checkpoint)

        return checkpoints

    def _generate_intervention_triggers(self, emotional_state: EmotionalState) -> List[Dict[str, Any]]:
        """Generate intervention triggers based on emotional state."""

        triggers = []

        if emotional_state.stress_indicators > 0.7:
            triggers.append({
                "trigger_type": "stress_intervention",
                "condition": "stress_level > 0.7",
                "action": "offer_break_activity",
                "message": "I notice you might be feeling stressed. Would you like to take a short break?"
            })

        if emotional_state.engagement_level < 0.3:
            triggers.append({
                "trigger_type": "engagement_boost",
                "condition": "engagement_level < 0.3",
                "action": "switch_to_interactive_content",
                "message": "Let's try a more hands-on approach to keep things engaging!"
            })

        if emotional_state.primary_emotion == Emotion.CONFUSED:
            triggers.append({
                "trigger_type": "confusion_support",
                "condition": "primary_emotion == confused",
                "action": "provide_additional_explanations",
                "message": "I can see this concept might be tricky. Let me explain it differently."
            })

        if emotional_state.primary_emotion == Emotion.FRUSTRATED:
            triggers.append({
                "trigger_type": "frustration_relief",
                "condition": "primary_emotion == frustrated",
                "action": "simplify_content",
                "message": "This seems challenging. Let's break it down into smaller, manageable steps."
            })

        return triggers

    def _get_default_exploratory_module(self) -> ContentModule:
        """Get a default exploratory module when no specific content is available."""

        return ContentModule(
            content_id="default_exploratory",
            title="Exploration Sandbox",
            content_type=ContentType.INTERACTIVE_EXERCISE,
            difficulty=DifficultyLevel.BEGINNER,
            emotional_alignment=[Emotion.EXPLORATORY, Emotion.CREATIVE],
            estimated_duration=15,
            prerequisites=[],
            learning_objectives=["Explore basic concepts", "Build confidence through experimentation"],
            content_data={
                "prompt": "Welcome to the exploration sandbox! Feel free to experiment and discover.",
                "starter_activities": [
                    "Try simple commands and see what happens",
                    "Modify examples and observe changes",
                    "Ask questions when curious"
                ]
            },
            success_criteria={
                "experimentation": True,
                "curiosity_demonstrated": True
            }
        )

    def get_available_topics(self) -> List[str]:
        """Get list of available learning topics."""
        return list(self.content_library.keys())

    def get_topic_modules(self, topic: str) -> List[ContentModule]:
        """Get all modules for a specific topic."""
        return self.content_library.get(topic, [])
