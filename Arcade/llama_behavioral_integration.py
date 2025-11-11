#!/usr/bin/env python3
"""
Llama AI Integration for User Interactions & Behavioral Intelligence
===================================================================

Advanced Llama AI integration focused on user interactions, behavioral aspects
of AI outputs, and leveraging Llama Stack for scalable AI development.

Features:
• Behavioral AI for personalized user interactions
• Emotional intelligence and conversational dynamics
• User behavior analysis and adaptation
• Personality-driven AI responses
• Llama Stack integration for scalable development
• Interaction pattern recognition and optimization
• Behavioral analytics and performance insights
• Adaptive conversation management
"""

import asyncio
import json
import time
import uuid
import logging
import re
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics
import random

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Llama integration would use appropriate client library
    # For demo purposes, we'll create a compatible interface
    import requests
    LLAMA_AVAILABLE = True
except ImportError:
    LLAMA_AVAILABLE = False
    print("Warning: Llama integration requires appropriate client library")

logger = logging.getLogger(__name__)

class BehavioralTrait(Enum):
    """Behavioral traits for AI personality."""
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    ENTHUSIASTIC = "enthusiastic"
    CALM = "calm"
    WITTY = "witty"
    EMPATHETIC = "empathetic"
    DIRECT = "direct"
    CREATIVE = "creative"
    ANALYTICAL = "analytical"
    SUPPORTIVE = "supportive"

class InteractionPattern(Enum):
    """Types of user interaction patterns."""
    QUESTION_ASKING = "question_asking"
    PROBLEM_SOLVING = "problem_solving"
    LEARNING = "learning"
    EXPLORATION = "exploration"
    COLLABORATION = "collaboration"
    CREATIVE_EXPRESSION = "creative_expression"
    EMOTIONAL_SUPPORT = "emotional_support"
    PRACTICAL_APPLICATION = "practical_application"

class ConversationStyle(Enum):
    """Conversation styles for adaptive interactions."""
    FORMAL = "formal"
    CASUAL = "casual"
    TECHNICAL = "technical"
    FRIENDLY = "friendly"
    MENTORING = "mentoring"
    COLLABORATIVE = "collaborative"
    ENCOURAGING = "encouraging"
    ANALYTICAL = "analytical"

class EmotionalState(Enum):
    """User emotional states detected through interaction."""
    CURIOUS = "curious"
    FRUSTRATED = "frustrated"
    EXCITED = "excited"
    CONFUSED = "confused"
    SATISFIED = "satisfied"
    OVERWHELMED = "overwhelmed"
    MOTIVATED = "motivated"
    BORED = "bored"

@dataclass
class UserProfile:
    """User profile with behavioral and interaction preferences."""
    user_id: str
    behavioral_traits: Dict[BehavioralTrait, float] = field(default_factory=dict)
    preferred_interaction_patterns: List[InteractionPattern] = field(default_factory=list)
    conversation_style: ConversationStyle = ConversationStyle.FRIENDLY
    emotional_baseline: EmotionalState = EmotionalState.CURIOUS
    interaction_history: List[Dict[str, Any]] = field(default_factory=list)
    adaptation_score: float = 0.0
    last_interaction: float = field(default_factory=time.time)
    session_count: int = 0

@dataclass
class BehavioralResponse:
    """Response enhanced with behavioral intelligence."""
    content: str
    behavioral_traits: Dict[str, float]
    emotional_tone: str
    engagement_level: float
    adaptability_score: float
    conversation_style: ConversationStyle
    interaction_patterns: List[InteractionPattern]
    generated_at: float = field(default_factory=time.time)

@dataclass
class InteractionAnalysis:
    """Analysis of user interaction patterns."""
    interaction_id: str
    user_id: str
    pattern_type: InteractionPattern
    emotional_state: EmotionalState
    engagement_metrics: Dict[str, float]
    behavioral_indicators: Dict[str, Any]
    adaptation_suggestions: List[str]
    confidence_score: float
    analyzed_at: float = field(default_factory=time.time)

@dataclass
class LlamaStackConfiguration:
    """Configuration for Llama Stack development."""
    stack_name: str
    model_configurations: Dict[str, Any]
    scaling_parameters: Dict[str, Any]
    optimization_settings: Dict[str, Any]
    monitoring_endpoints: List[str]
    deployment_targets: List[str]

class LlamaBehavioralManager:
    """
    Llama AI integration focused on user interactions and behavioral intelligence.

    Responsibilities:
    • Behavioral AI for personalized user interactions
    • Emotional intelligence and conversational dynamics
    • User behavior analysis and adaptation
    • Personality-driven AI responses
    • Llama Stack integration for scalable development
    • Interaction pattern recognition and optimization
    • Behavioral analytics and performance insights
    • Adaptive conversation management
    """

    def __init__(self, api_key_manager=None):
        self.api_key_manager = api_key_manager
        self.client = None
        self.llama_stack = None

        # Data structures
        self.user_profiles: Dict[str, UserProfile] = {}
        self.interaction_analyses: List[InteractionAnalysis] = []
        self.behavioral_responses: List[BehavioralResponse] = []
        self.llama_stacks: Dict[str, LlamaStackConfiguration] = {}

        # Behavioral intelligence
        self.behavioral_templates = self._initialize_behavioral_templates()
        self.conversation_patterns = self._initialize_conversation_patterns()
        self.emotional_intelligence = self._initialize_emotional_intelligence()

        # Initialize Llama client and stack
        self._initialize_llama()

    def _initialize_llama(self):
        """Initialize Llama client and stack."""
        if LLAMA_AVAILABLE and self.api_key_manager:
            # In production, this would initialize actual Llama client
            # For demo, we'll simulate the integration
            self.client = "llama_client_simulated"
            self.llama_stack = self._initialize_llama_stack()
            logger.info("Llama behavioral integration initialized successfully")
        else:
            logger.warning("Llama AI not available")

    def _initialize_llama_stack(self) -> LlamaStackConfiguration:
        """Initialize Llama Stack configuration."""
        return LlamaStackConfiguration(
            stack_name="behavioral_intelligence_stack",
            model_configurations={
                "base_model": "llama-3.1-70b-instruct",
                "fine_tuned_models": [],
                "behavioral_adaptation": True,
                "emotional_intelligence": True
            },
            scaling_parameters={
                "max_concurrent_users": 1000,
                "response_time_target": 2.0,  # seconds
                "throughput_target": 100,  # requests per second
                "auto_scaling_enabled": True
            },
            optimization_settings={
                "caching_enabled": True,
                "batch_processing": True,
                "model_compression": False,
                "quantization": "4bit"
            },
            monitoring_endpoints=[
                "/llama/health",
                "/llama/metrics",
                "/llama/performance"
            ],
            deployment_targets=[
                "behavioral_ai_service",
                "interaction_optimizer",
                "emotional_intelligence"
            ]
        )

    def _initialize_behavioral_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize behavioral response templates."""
        return {
            BehavioralTrait.FRIENDLY.value: {
                "greeting": "Hey there! I'm excited to help you today! 😊",
                "encouragement": "You're doing great! Keep going! 🚀",
                "empathy": "I understand that can be tricky. Let's work through it together.",
                "success": "Awesome work! You nailed it! 🎉"
            },
            BehavioralTrait.PROFESSIONAL.value: {
                "greeting": "Hello. I'm here to assist you with your request.",
                "encouragement": "Your progress is commendable. Continue with the excellent work.",
                "empathy": "I acknowledge this presents a challenge. Let us proceed systematically.",
                "success": "Task completed successfully. Well done."
            },
            BehavioralTrait.ENTHUSIASTIC.value: {
                "greeting": "WOW! I'm super pumped to work with you! 🎉",
                "encouragement": "YES! You're absolutely crushing it! 🔥",
                "empathy": "No worries! We've got this! Let's turn that challenge into a victory!",
                "success": "INCREDIBLE! You absolutely ROCKED that! 🌟"
            },
            BehavioralTrait.CALM.value: {
                "greeting": "Hello. I'm here and ready to help in a peaceful, focused manner.",
                "encouragement": "Steady progress is being made. Continue at your comfortable pace.",
                "empathy": "Take a deep breath. We can approach this calmly and methodically.",
                "success": "Well done. Achievement accomplished with composure."
            }
        }

    def _initialize_conversation_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize conversation pattern recognition."""
        return {
            "question_driven": {
                "indicators": ["what", "how", "why", "when", "where", "who"],
                "response_style": "informative",
                "engagement_strategy": "curiosity_stimulation"
            },
            "problem_solving": {
                "indicators": ["problem", "issue", "error", "bug", "fix", "solution"],
                "response_style": "analytical",
                "engagement_strategy": "step_by_step_guidance"
            },
            "learning_mode": {
                "indicators": ["learn", "understand", "explain", "teach", "tutorial"],
                "response_style": "educational",
                "engagement_strategy": "progressive_disclosure"
            },
            "creative_mode": {
                "indicators": ["create", "design", "imagine", "build", "innovate"],
                "response_style": "inspirational",
                "engagement_strategy": "idea_generation"
            }
        }

    def _initialize_emotional_intelligence(self) -> Dict[str, Dict[str, Any]]:
        """Initialize emotional intelligence patterns."""
        return {
            EmotionalState.CURIOUS.value: {
                "response_modifiers": ["stimulate_curiosity", "provide_depth", "ask_followup"],
                "engagement_boost": 1.2,
                "complexity_adjustment": 1.1
            },
            EmotionalState.FRUSTRATED.value: {
                "response_modifiers": ["show_empathy", "simplify_explanation", "offer_alternatives"],
                "engagement_boost": 0.8,
                "complexity_adjustment": 0.9
            },
            EmotionalState.EXCITED.value: {
                "response_modifiers": ["match_energy", "build_enthusiasm", "suggest_advancement"],
                "engagement_boost": 1.3,
                "complexity_adjustment": 1.0
            },
            EmotionalState.CONFUSED.value: {
                "response_modifiers": ["clarify_concepts", "provide_examples", "check_understanding"],
                "engagement_boost": 0.9,
                "complexity_adjustment": 0.8
            }
        }

    async def create_user_interaction_session(self, user_id: str,
                                            initial_behavioral_traits: Dict[BehavioralTrait, float] = None) -> UserProfile:
        """
        Create a personalized user interaction session with behavioral intelligence.

        Args:
            user_id: Unique user identifier
            initial_behavioral_traits: Initial behavioral trait preferences

        Returns:
            UserProfile for personalized interactions
        """

        # Initialize or load user profile
        if user_id not in self.user_profiles:
            profile = UserProfile(
                user_id=user_id,
                behavioral_traits=initial_behavioral_traits or self._get_default_behavioral_traits(),
                preferred_interaction_patterns=[InteractionPattern.QUESTION_ASKING, InteractionPattern.LEARNING],
                conversation_style=ConversationStyle.FRIENDLY
            )
            self.user_profiles[user_id] = profile
        else:
            profile = self.user_profiles[user_id]

        profile.session_count += 1
        profile.last_interaction = time.time()

        return profile

    def _get_default_behavioral_traits(self) -> Dict[BehavioralTrait, float]:
        """Get default behavioral traits for new users."""
        return {
            BehavioralTrait.FRIENDLY: 0.7,
            BehavioralTrait.ENTHUSIASTIC: 0.6,
            BehavioralTrait.HELPFUL: 0.8,
            BehavioralTrait.PATIENT: 0.7,
            BehavioralTrait.CLEAR: 0.8
        }

    async def generate_behavioral_response(self, user_id: str, user_input: str,
                                         context: Dict[str, Any] = None) -> BehavioralResponse:
        """
        Generate a response enhanced with behavioral intelligence.

        Args:
            user_id: User identifier
            user_input: User's input message
            context: Additional context for response generation

        Returns:
            BehavioralResponse with behavioral enhancements
        """

        # Get or create user profile
        if user_id not in self.user_profiles:
            await self.create_user_interaction_session(user_id)

        profile = self.user_profiles[user_id]

        # Analyze user input for patterns and emotions
        analysis = await self._analyze_user_input(user_input, profile)

        # Generate base response using Llama
        base_response = await self._generate_llama_response(user_input, analysis, context)

        # Apply behavioral enhancements
        enhanced_response = await self._enhance_with_behavioral_intelligence(
            base_response, analysis, profile
        )

        # Update user profile based on interaction
        self._update_user_profile(profile, analysis, enhanced_response)

        # Create behavioral response object
        behavioral_response = BehavioralResponse(
            content=enhanced_response["content"],
            behavioral_traits=enhanced_response["traits"],
            emotional_tone=enhanced_response["emotional_tone"],
            engagement_level=enhanced_response["engagement_level"],
            adaptability_score=enhanced_response["adaptability_score"],
            conversation_style=profile.conversation_style,
            interaction_patterns=analysis["patterns"]
        )

        self.behavioral_responses.append(behavioral_response)

        return behavioral_response

    async def _analyze_user_input(self, user_input: str, profile: UserProfile) -> Dict[str, Any]:
        """Analyze user input for patterns, emotions, and behavioral indicators."""

        analysis = {
            "patterns": [],
            "emotional_state": EmotionalState.CURIOUS,
            "engagement_level": 0.7,
            "complexity_level": 0.5,
            "confidence_score": 0.8
        }

        # Pattern recognition
        input_lower = user_input.lower()

        for pattern_name, pattern_data in self.conversation_patterns.items():
            if any(indicator in input_lower for indicator in pattern_data["indicators"]):
                analysis["patterns"].append(getattr(InteractionPattern, pattern_name.upper()))

        # Emotional state detection (simplified)
        if any(word in input_lower for word in ["frustrated", "stuck", "confused", "help"]):
            analysis["emotional_state"] = EmotionalState.FRUSTRATED
            analysis["engagement_level"] = 0.6
        elif any(word in input_lower for word in ["excited", "awesome", "great", "love"]):
            analysis["emotional_state"] = EmotionalState.EXCITED
            analysis["engagement_level"] = 0.9
        elif any(word in input_lower for word in ["curious", "interesting", "wonder", "learn"]):
            analysis["emotional_state"] = EmotionalState.CURIOUS
            analysis["engagement_level"] = 0.8

        # Complexity assessment
        word_count = len(user_input.split())
        question_count = user_input.count('?')
        technical_terms = sum(1 for word in ["algorithm", "function", "class", "api", "database", "neural", "quantum"]
                            if word in input_lower)

        analysis["complexity_level"] = min(1.0, (word_count * 0.01) + (question_count * 0.1) + (technical_terms * 0.2))

        return analysis

    async def _generate_llama_response(self, user_input: str, analysis: Dict[str, Any],
                                     context: Dict[str, Any] = None) -> str:
        """Generate base response using Llama AI."""

        if not self.client:
            return self._generate_behavioral_fallback_response(user_input, analysis)

        # Prepare context for Llama
        system_prompt = self._create_behavioral_system_prompt(analysis)

        messages = [
            {"role": "system", "content": system_prompt}
        ]

        # Add conversation history if available
        if context and "conversation_history" in context:
            for msg in context["conversation_history"][-3:]:  # Last 3 messages
                messages.append({
                    "role": "user" if msg.get("role") == "user" else "assistant",
                    "content": msg.get("content", "")
                })

        messages.append({"role": "user", "content": user_input})

        try:
            # In production, this would call actual Llama API
            # For demo, simulate intelligent response
            response = await self._simulate_llama_response(user_input, analysis)
            return response

        except Exception as e:
            logger.error(f"Llama response generation failed: {e}")
            return self._generate_behavioral_fallback_response(user_input, analysis)

    def _create_behavioral_system_prompt(self, analysis: Dict[str, Any]) -> str:
        """Create a system prompt enhanced with behavioral intelligence."""

        emotional_state = analysis.get("emotional_state", EmotionalState.CURIOUS)
        patterns = analysis.get("patterns", [])
        engagement = analysis.get("engagement_level", 0.7)

        prompt_parts = [
            "You are a highly intelligent and emotionally aware AI assistant powered by Llama.",
            "Your responses should be:",
            f"- Emotionally attuned to the user's {emotional_state.value} state",
            f"- Engaging with {engagement:.1%} enthusiasm level",
            "- Behaviorally adaptive based on interaction patterns",
            "- Helpful, truthful, and maximally informative"
        ]

        if patterns:
            pattern_descriptions = [f"- {pattern.value.replace('_', ' ')} focused" for pattern in patterns]
            prompt_parts.extend(pattern_descriptions)

        prompt_parts.extend([
            "",
            "Consider the user's emotional state and adapt your communication style accordingly.",
            "Be encouraging, patient, and provide responses that match their engagement level.",
            "Use behavioral intelligence to create more natural and effective interactions."
        ])

        return "\n".join(prompt_parts)

    async def _simulate_llama_response(self, user_input: str, analysis: Dict[str, Any]) -> str:
        """Simulate intelligent Llama response for demo purposes."""

        emotional_state = analysis.get("emotional_state", EmotionalState.CURIOUS)
        patterns = analysis.get("patterns", [])
        complexity = analysis.get("complexity_level", 0.5)

        # Generate contextually appropriate response
        if emotional_state == EmotionalState.FRUSTRATED:
            base_response = "I understand this is challenging. Let's break it down step by step and work through it together."
        elif emotional_state == EmotionalState.EXCITED:
            base_response = "That's fantastic! I'm excited to help you build on this momentum!"
        elif emotional_state == EmotionalState.CONFUSED:
            base_response = "I can see this concept might be confusing. Let me explain it more clearly with some examples."
        else:
            base_response = "I'm here to help you with that. Let me provide a comprehensive response."

        # Add pattern-specific content
        if InteractionPattern.QUESTION_ASKING in patterns:
            base_response += " Based on your questions, here's what you need to know:"
        elif InteractionPattern.PROBLEM_SOLVING in patterns:
            base_response += " For this problem, let's approach it systematically:"
        elif InteractionPattern.LEARNING in patterns:
            base_response += " Let's explore this concept together:"

        # Adjust complexity
        if complexity > 0.7:
            base_response += " (This is a detailed, technical explanation)"
        elif complexity < 0.3:
            base_response += " (Keeping it simple and straightforward)"

        return base_response + f"\n\nYour query: '{user_input}'\nAnalysis: {emotional_state.value} state, {len(patterns)} interaction patterns detected."

    def _generate_behavioral_fallback_response(self, user_input: str, analysis: Dict[str, Any]) -> str:
        """Generate behavioral fallback response when Llama is unavailable."""

        emotional_state = analysis.get("emotional_state", EmotionalState.CURIOUS)

        templates = {
            EmotionalState.CURIOUS: "That's a fascinating question! I'm excited to explore this with you.",
            EmotionalState.FRUSTRATED: "I can sense this is frustrating. Don't worry, we'll figure this out together.",
            EmotionalState.EXCITED: "Your enthusiasm is contagious! Let's dive into this exciting topic!",
            EmotionalState.CONFUSED: "I understand this might be confusing. Let me clarify and simplify.",
            EmotionalState.SATISFIED: "It's great to see you're satisfied with our progress!",
            EmotionalState.OVERWHELMED: "I see this might feel overwhelming. Let's take it one step at a time.",
            EmotionalState.MOTIVATED: "Your motivation is inspiring! Let's channel that energy productively.",
            EmotionalState.BORED: "I can tell this might not be holding your interest. Let me make it more engaging!"
        }

        return templates.get(emotional_state, "I'm here to help with your request.")

    async def _enhance_with_behavioral_intelligence(self, base_response: str,
                                                  analysis: Dict[str, Any], profile: UserProfile) -> Dict[str, Any]:
        """Enhance response with behavioral intelligence."""

        emotional_state = analysis.get("emotional_state", EmotionalState.CURIOUS)
        engagement_level = analysis.get("engagement_level", 0.7)

        # Get behavioral enhancements
        behavioral_enhancements = self._get_behavioral_enhancements(profile, emotional_state)

        # Apply emotional intelligence
        emotional_modifiers = self.emotional_intelligence.get(emotional_state.value, {})

        # Calculate adaptability score
        adaptability_score = self._calculate_adaptability_score(profile, analysis)

        # Enhance response content
        enhanced_content = self._apply_behavioral_enhancements(
            base_response, behavioral_enhancements, emotional_modifiers
        )

        return {
            "content": enhanced_content,
            "traits": behavioral_enhancements,
            "emotional_tone": emotional_state.value,
            "engagement_level": engagement_level,
            "adaptability_score": adaptability_score
        }

    def _get_behavioral_enhancements(self, profile: UserProfile,
                                   emotional_state: EmotionalState) -> Dict[str, float]:
        """Get behavioral trait enhancements for the user."""

        # Start with profile traits
        enhancements = profile.behavioral_traits.copy()

        # Adjust based on emotional state
        emotional_adjustments = {
            EmotionalState.FRUSTRATED: {"empathy": 0.3, "patience": 0.2, "supportiveness": 0.3},
            EmotionalState.EXCITED: {"enthusiasm": 0.3, "engagement": 0.2},
            EmotionalState.CONFUSED: {"clarity": 0.3, "simplicity": 0.2},
            EmotionalState.CURIOUS: {"informativeness": 0.2, "engagement": 0.2}
        }

        if emotional_state in emotional_adjustments:
            for trait, adjustment in emotional_adjustments[emotional_state].items():
                trait_enum = getattr(BehavioralTrait, trait.upper(), None)
                if trait_enum:
                    enhancements[trait_enum] = min(1.0, enhancements.get(trait_enum, 0.5) + adjustment)

        return enhancements

    def _calculate_adaptability_score(self, profile: UserProfile, analysis: Dict[str, Any]) -> float:
        """Calculate how well the response adapts to the user's needs."""

        # Factors affecting adaptability
        factors = {
            "session_experience": min(1.0, profile.session_count * 0.1),  # More sessions = better adaptation
            "emotional_alignment": 0.8 if analysis.get("emotional_state") else 0.5,
            "pattern_recognition": min(1.0, len(analysis.get("patterns", [])) * 0.2),
            "engagement_optimization": analysis.get("engagement_level", 0.7)
        }

        # Weighted average
        weights = {"session_experience": 0.2, "emotional_alignment": 0.3,
                  "pattern_recognition": 0.2, "engagement_optimization": 0.3}

        adaptability_score = sum(factors[key] * weights[key] for key in factors)
        return min(1.0, adaptability_score)

    def _apply_behavioral_enhancements(self, content: str, enhancements: Dict[str, float],
                                     emotional_modifiers: Dict[str, Any]) -> str:
        """Apply behavioral enhancements to the response content."""

        enhanced_content = content

        # Add behavioral elements based on trait strengths
        for trait, strength in enhancements.items():
            if strength > 0.7:  # Only apply strong traits
                enhancement = self._get_trait_enhancement(trait, strength)
                if enhancement:
                    enhanced_content = self._integrate_enhancement(enhanced_content, enhancement)

        # Apply emotional modifiers
        for modifier in emotional_modifiers.get("response_modifiers", []):
            if modifier == "show_empathy":
                enhanced_content = f"I understand this can be challenging. {enhanced_content}"
            elif modifier == "match_energy":
                enhanced_content = f"That's exciting! {enhanced_content}"
            elif modifier == "simplify_explanation":
                enhanced_content = f"Let me explain this more simply: {enhanced_content}"

        return enhanced_content

    def _get_trait_enhancement(self, trait: BehavioralTrait, strength: float) -> Optional[str]:
        """Get enhancement text for a behavioral trait."""

        enhancements = {
            BehavioralTrait.FRIENDLY: "😊 " if strength > 0.8 else None,
            BehavioralTrait.ENTHUSIASTIC: "🚀 " if strength > 0.8 else None,
            BehavioralTrait.EMPATHETIC: "🤝 " if strength > 0.8 else None,
            BehavioralTrait.SUPPORTIVE: "💪 " if strength > 0.8 else None,
            BehavioralTrait.WITTY: "😄 " if strength > 0.8 else None,
            BehavioralTrait.CALM: "🧘 " if strength > 0.8 else None
        }

        return enhancements.get(trait)

    def _integrate_enhancement(self, content: str, enhancement: str) -> str:
        """Integrate enhancement into content appropriately."""
        if enhancement.startswith("😊") or enhancement.startswith("🚀"):
            return enhancement + content
        elif enhancement.startswith("🤝") or enhancement.startswith("💪"):
            return content + " " + enhancement
        else:
            return content

    def _update_user_profile(self, profile: UserProfile, analysis: Dict[str, Any],
                           response: Dict[str, Any]):
        """Update user profile based on interaction."""

        # Update interaction history
        profile.interaction_history.append({
            "timestamp": time.time(),
            "analysis": analysis,
            "response": response,
            "engagement_level": response.get("engagement_level", 0.7)
        })

        # Limit history to last 50 interactions
        if len(profile.interaction_history) > 50:
            profile.interaction_history = profile.interaction_history[-50:]

        # Update behavioral traits based on interaction
        engagement = response.get("engagement_level", 0.7)
        adaptability = response.get("adaptability_score", 0.5)

        # Positive reinforcement for good engagement
        if engagement > 0.8:
            profile.adaptation_score = min(1.0, profile.adaptation_score + 0.05)

        # Update preferred patterns
        if analysis.get("patterns"):
            for pattern in analysis["patterns"]:
                if pattern not in profile.preferred_interaction_patterns:
                    profile.preferred_interaction_patterns.append(pattern)

        # Update conversation style based on successful interactions
        if adaptability > 0.8:
            # Could adapt conversation style based on user preferences
            pass

    def analyze_interaction_patterns(self, user_id: str) -> InteractionAnalysis:
        """Analyze interaction patterns for a user."""

        if user_id not in self.user_profiles:
            raise ValueError(f"User {user_id} not found")

        profile = self.user_profiles[user_id]

        # Analyze recent interactions
        recent_interactions = profile.interaction_history[-20:]  # Last 20 interactions

        if not recent_interactions:
            return InteractionAnalysis(
                interaction_id=str(uuid.uuid4()),
                user_id=user_id,
                pattern_type=InteractionPattern.QUESTION_ASKING,
                emotional_state=EmotionalState.CURIOUS,
                engagement_metrics={"average_engagement": 0.5},
                behavioral_indicators={},
                adaptation_suggestions=["Need more interaction data"],
                confidence_score=0.3
            )

        # Calculate metrics
        engagement_scores = [interaction.get("engagement_level", 0.5) for interaction in recent_interactions]
        average_engagement = statistics.mean(engagement_scores) if engagement_scores else 0.5

        # Determine dominant patterns
        pattern_counts = {}
        emotional_counts = {}

        for interaction in recent_interactions:
            analysis = interaction.get("analysis", {})
            for pattern in analysis.get("patterns", []):
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1

            emotional_state = analysis.get("emotional_state", EmotionalState.CURIOUS)
            emotional_counts[emotional_state] = emotional_counts.get(emotional_state, 0) + 1

        dominant_pattern = max(pattern_counts.keys(), key=lambda x: pattern_counts[x]) if pattern_counts else InteractionPattern.QUESTION_ASKING
        dominant_emotion = max(emotional_counts.keys(), key=lambda x: emotional_counts[x]) if emotional_counts else EmotionalState.CURIOUS

        # Generate adaptation suggestions
        suggestions = self._generate_adaptation_suggestions(average_engagement, dominant_pattern, dominant_emotion)

        return InteractionAnalysis(
            interaction_id=str(uuid.uuid4()),
            user_id=user_id,
            pattern_type=dominant_pattern,
            emotional_state=dominant_emotion,
            engagement_metrics={
                "average_engagement": average_engagement,
                "engagement_variance": statistics.variance(engagement_scores) if len(engagement_scores) > 1 else 0,
                "total_interactions": len(recent_interactions)
            },
            behavioral_indicators={
                "pattern_distribution": pattern_counts,
                "emotional_distribution": {k.value: v for k, v in emotional_counts.items()},
                "adaptation_score": profile.adaptation_score
            },
            adaptation_suggestions=suggestions,
            confidence_score=min(1.0, len(recent_interactions) * 0.05)
        )

    def _generate_adaptation_suggestions(self, engagement: float, pattern: InteractionPattern,
                                       emotion: EmotionalState) -> List[str]:
        """Generate adaptation suggestions based on user behavior."""

        suggestions = []

        if engagement < 0.6:
            suggestions.append("Increase engagement through more interactive response formats")
            suggestions.append("Consider adjusting communication style to better match user preferences")

        if pattern == InteractionPattern.QUESTION_ASKING:
            suggestions.append("Focus on providing clear, comprehensive answers to questions")
            suggestions.append("Encourage follow-up questions to deepen understanding")

        elif pattern == InteractionPattern.PROBLEM_SOLVING:
            suggestions.append("Provide step-by-step problem-solving guidance")
            suggestions.append("Offer multiple solution approaches for complex problems")

        elif pattern == InteractionPattern.LEARNING:
            suggestions.append("Structure responses with clear learning objectives")
            suggestions.append("Include practical examples and exercises")

        if emotion == EmotionalState.FRUSTRATED:
            suggestions.append("Show more empathy and patience in responses")
            suggestions.append("Provide simpler explanations and more support")

        elif emotion == EmotionalState.CURIOUS:
            suggestions.append("Encourage curiosity with deeper dives into topics")
            suggestions.append("Suggest related areas for exploration")

        return suggestions

    def get_llama_stack_status(self) -> Dict[str, Any]:
        """Get Llama Stack operational status."""

        return {
            "stack_name": self.llama_stack.stack_name if self.llama_stack else "unknown",
            "status": "operational" if self.client else "initializing",
            "model_configurations": self.llama_stack.model_configurations if self.llama_stack else {},
            "scaling_parameters": self.llama_stack.scaling_parameters if self.llama_stack else {},
            "active_users": len(self.user_profiles),
            "total_interactions": len(self.behavioral_responses),
            "monitoring_endpoints": self.llama_stack.monitoring_endpoints if self.llama_stack else [],
            "deployment_targets": self.llama_stack.deployment_targets if self.llama_stack else []
        }

    def scale_llama_stack(self, target_capacity: int) -> Dict[str, Any]:
        """Scale the Llama Stack based on demand."""

        current_status = self.get_llama_stack_status()

        scaling_decision = {
            "current_capacity": current_status.get("active_users", 0),
            "target_capacity": target_capacity,
            "scaling_needed": target_capacity > current_status.get("active_users", 0) * 1.2,
            "scaling_actions": []
        }

        if scaling_decision["scaling_needed"]:
            scaling_decision["scaling_actions"] = [
                "Increase model instances",
                "Optimize caching strategies",
                "Implement load balancing",
                "Scale computational resources"
            ]

        return scaling_decision

# Global Llama behavioral manager instance
llama_behavioral_manager = LlamaBehavioralManager()
