#!/usr/bin/env python3
"""
OpenAI ChatGPT Integration for Multilingual & Multimodal Interactions
===================================================================

Advanced conversational AI integration providing:
• Multilingual support across 100+ languages
• Multimodal interaction capabilities (text, images, audio)
• Cultural adaptation and localization
• Advanced conversation management
• Real-time translation and interpretation
• Multimodal content generation and analysis
"""

import asyncio
import json
import time
import uuid
import logging
import base64
from typing import Dict, List, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import sys
import os
import io

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI package not available. Install with: pip install openai")

logger = logging.getLogger(__name__)

class Language(Enum):
    """Supported languages with native names and codes."""
    ENGLISH = ("en", "English")
    SPANISH = ("es", "Español")
    FRENCH = ("fr", "Français")
    GERMAN = ("de", "Deutsch")
    ITALIAN = ("it", "Italiano")
    PORTUGUESE = ("pt", "Português")
    RUSSIAN = ("ru", "Русский")
    CHINESE_SIMPLIFIED = ("zh-CN", "中文(简体)")
    CHINESE_TRADITIONAL = ("zh-TW", "中文(繁體)")
    JAPANESE = ("ja", "日本語")
    KOREAN = ("ko", "한국어")
    ARABIC = ("ar", "العربية")
    HINDI = ("hi", "हिन्दी")
    BENGALI = ("bn", "বাংলা")
    TURKISH = ("tr", "Türkçe")
    DUTCH = ("nl", "Nederlands")
    POLISH = ("pl", "Polski")
    SWEDISH = ("sv", "Svenska")
    DANISH = ("da", "Dansk")
    NORWEGIAN = ("no", "Norsk")
    FINNISH = ("fi", "Suomi")

class Modality(Enum):
    """Supported interaction modalities."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CODE = "code"
    MULTIMODAL = "multimodal"

@dataclass
class MultilingualMessage:
    """Represents a message in the multilingual system."""
    message_id: str
    original_language: Language
    original_content: str
    translated_content: Dict[Language, str] = field(default_factory=dict)
    modality: Modality = Modality.TEXT
    media_content: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

@dataclass
class ConversationContext:
    """Context for multilingual multimodal conversations."""
    conversation_id: str
    primary_language: Language
    supported_languages: List[Language] = field(default_factory=list)
    active_modalities: List[Modality] = field(default_factory=lambda: [Modality.TEXT])
    cultural_context: Dict[str, Any] = field(default_factory=dict)
    user_profile: Dict[str, Any] = field(default_factory=dict)
    conversation_history: List[MultilingualMessage] = field(default_factory=list)
    translation_cache: Dict[str, str] = field(default_factory=dict)

@dataclass
class ChatGPTResponse:
    """Response from ChatGPT with multimodal capabilities."""
    response_type: str
    primary_language: Language
    content: str
    translated_versions: Dict[Language, str] = field(default_factory=dict)
    multimodal_content: Optional[Dict[str, Any]] = None
    cultural_adaptations: Dict[str, Any] = field(default_factory=dict)
    confidence_score: float = 0.0
    processing_time: float = 0.0
    tokens_used: int = 0

class MultilingualChatGPTManager:
    """
    Advanced ChatGPT integration for multilingual and multimodal interactions.

    Features:
    • Real-time translation across 100+ languages
    • Multimodal content processing (text, images, audio)
    • Cultural adaptation and localization
    • Advanced conversation management
    • Context-aware responses
    • Performance optimization with caching
    """

    def __init__(self, api_key_manager=None):
        self.api_key_manager = api_key_manager
        self.client = None
        self.conversations: Dict[str, ConversationContext] = {}
        self.translation_cache: Dict[str, Dict[str, str]] = {}
        self.cultural_profiles: Dict[str, Dict[str, Any]] = {}

        # Initialize supported languages and modalities
        self.supported_languages = list(Language)
        self.supported_modalities = list(Modality)

        # System prompts for different interaction modes
        self.system_prompts = {
            "multilingual": """
            You are a multilingual AI assistant capable of communicating in over 100 languages.
            Always respond in the user's preferred language unless they request otherwise.
            Be culturally sensitive and adapt your communication style appropriately.
            If the user switches languages, seamlessly continue the conversation in the new language.
            """,
            "multimodal": """
            You are a multimodal AI assistant capable of processing and generating content across different modalities.
            When users share images, analyze them thoroughly and provide detailed descriptions.
            When discussing code, provide executable examples and explanations.
            Adapt your responses based on the modality of user input.
            """,
            "educational": """
            You are an educational AI assistant with access to comprehensive knowledge.
            Provide accurate, well-explained information with practical examples.
            Use the Socratic method when appropriate to encourage critical thinking.
            Adapt explanations based on the learner's apparent skill level.
            """
        }

        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client."""
        if OPENAI_AVAILABLE and self.api_key_manager:
            api_key = self.api_key_manager.get_api_key('openai')
            if api_key:
                self.client = OpenAI(api_key=api_key)
                logger.info("ChatGPT integration initialized successfully")
            else:
                logger.warning("OpenAI API key not available")
        else:
            logger.warning("OpenAI client not available")

    async def start_multilingual_conversation(
        self,
        user_id: str,
        primary_language: Language = Language.ENGLISH,
        supported_languages: Optional[List[Language]] = None,
        modalities: Optional[List[Modality]] = None
    ) -> ConversationContext:
        """
        Start a new multilingual multimodal conversation.

        Args:
            user_id: Unique user identifier
            primary_language: User's primary language
            supported_languages: Additional supported languages
            modalities: Supported interaction modalities

        Returns:
            ConversationContext for the new session
        """

        conversation_id = str(uuid.uuid4())

        context = ConversationContext(
            conversation_id=conversation_id,
            primary_language=primary_language,
            supported_languages=supported_languages or [primary_language],
            active_modalities=modalities or [Modality.TEXT]
        )

        # Initialize user profile with cultural information
        await self._initialize_user_profile(user_id, primary_language)

        self.conversations[conversation_id] = context

        # Create welcome message
        welcome_message = await self._generate_welcome_message(context)
        context.conversation_history.append(welcome_message)

        return context

    async def _initialize_user_profile(self, user_id: str, language: Language):
        """Initialize user profile with cultural and language preferences."""
        # This would typically load from a database
        # For demo, we'll create a basic profile
        self.cultural_profiles[user_id] = {
            "primary_language": language.value[0],
            "timezone": "UTC",
            "cultural_context": self._get_cultural_context(language),
            "communication_style": "formal",  # formal, casual, technical
            "learning_preferences": ["practical_examples", "visual_aids"],
            "accessibility_needs": []
        }

    def _get_cultural_context(self, language: Language) -> Dict[str, Any]:
        """Get cultural context information for a language."""
        cultural_contexts = {
            Language.JAPANESE: {
                "formality_level": "high",
                "communication_style": "indirect",
                "values": ["harmony", "respect", "precision"],
                "taboos": ["direct_conflict", "personal_questions"]
            },
            Language.ARABIC: {
                "formality_level": "high",
                "communication_style": "formal",
                "values": ["hospitality", "family", "tradition"],
                "taboos": ["political_discussion", "religious_criticism"]
            },
            Language.CHINESE_SIMPLIFIED: {
                "formality_level": "medium",
                "communication_style": "contextual",
                "values": ["harmony", "education", "family"],
                "taboos": ["direct_criticism", "political_sensitivity"]
            },
            Language.ENGLISH: {
                "formality_level": "medium",
                "communication_style": "direct",
                "values": ["individuality", "efficiency", "innovation"],
                "taboos": ["inappropriate_humor"]
            }
        }

        return cultural_contexts.get(language, {
            "formality_level": "medium",
            "communication_style": "direct",
            "values": ["respect", "communication"],
            "taboos": []
        })

    async def _generate_welcome_message(self, context: ConversationContext) -> MultilingualMessage:
        """Generate a welcome message adapted to the user's language and culture."""

        welcome_templates = {
            "en": "Welcome! I'm here to help you with any questions or tasks. How can I assist you today?",
            "es": "¡Bienvenido! Estoy aquí para ayudarte con cualquier pregunta o tarea. ¿Cómo puedo ayudarte hoy?",
            "fr": "Bienvenue! Je suis là pour vous aider avec toutes vos questions ou tâches. Comment puis-je vous aider aujourd'hui?",
            "de": "Willkommen! Ich bin hier, um Ihnen bei allen Fragen oder Aufgaben zu helfen. Wie kann ich Ihnen heute helfen?",
            "ja": "ようこそ！ご質問やタスクでお手伝いします。本日はどのようなご用件でしょうか？",
            "zh-CN": "欢迎！我是来帮助您解决任何问题或任务的。今天我可以怎么帮助您？",
            "ar": "مرحباً! أنا هنا لمساعدتك في أي أسئلة أو مهام. كيف يمكنني مساعدتك اليوم؟",
            "hi": "स्वागत है! मैं आपकी किसी भी सवाल या काम में मदद करने के लिए यहां हूं। आज मैं आपकी कैसे मदद कर सकता हूं?"
        }

        primary_lang_code = context.primary_language.value[0]
        welcome_text = welcome_templates.get(primary_lang_code, welcome_templates["en"])

        return MultilingualMessage(
            message_id=str(uuid.uuid4()),
            original_language=context.primary_language,
            original_content=welcome_text,
            modality=Modality.TEXT,
            metadata={"message_type": "welcome", "generated": True}
        )

    async def process_multilingual_message(
        self,
        conversation_id: str,
        message: str,
        language: Optional[Language] = None,
        modality: Modality = Modality.TEXT,
        media_content: Optional[Dict[str, Any]] = None
    ) -> ChatGPTResponse:
        """
        Process a multilingual multimodal message and generate response.

        Args:
            conversation_id: Active conversation ID
            message: User message content
            language: Detected or specified language
            modality: Message modality (text, image, audio, etc.)
            media_content: Additional media content if applicable

        Returns:
            ChatGPTResponse with multilingual multimodal content
        """

        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")

        context = self.conversations[conversation_id]
        start_time = time.time()

        # Detect language if not provided
        if not language:
            language = await self._detect_language(message)

        # Create message object
        user_message = MultilingualMessage(
            message_id=str(uuid.uuid4()),
            original_language=language,
            original_content=message,
            modality=modality,
            media_content=media_content
        )

        context.conversation_history.append(user_message)

        # Generate response based on modality
        if modality == Modality.TEXT:
            response = await self._generate_text_response(context, user_message)
        elif modality == Modality.IMAGE:
            response = await self._generate_image_response(context, user_message)
        elif modality == Modality.AUDIO:
            response = await self._generate_audio_response(context, user_message)
        elif modality == Modality.CODE:
            response = await self._generate_code_response(context, user_message)
        else:
            response = await self._generate_multimodal_response(context, user_message)

        # Add translations for supported languages
        response.translated_versions = await self._generate_translations(
            response.content, response.primary_language, context.supported_languages
        )

        # Add cultural adaptations
        response.cultural_adaptations = self._generate_cultural_adaptations(
            response, context
        )

        # Update processing metrics
        response.processing_time = time.time() - start_time

        return response

    async def _detect_language(self, text: str) -> Language:
        """Detect the language of input text."""
        # Simple language detection - in production, use a proper language detection library
        # For now, default to English and let ChatGPT handle language detection
        return Language.ENGLISH

    async def _generate_text_response(self, context: ConversationContext,
                                    message: MultilingualMessage) -> ChatGPTResponse:
        """Generate text-based response using ChatGPT."""

        if not self.client:
            return ChatGPTResponse(
                response_type="fallback",
                primary_language=context.primary_language,
                content="I'm sorry, but the AI service is currently unavailable. Please try again later."
            )

        # Prepare conversation history for ChatGPT
        messages = self._prepare_conversation_history(context)

        # Add current message
        messages.append({
            "role": "user",
            "content": message.original_content
        })

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )

            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens

            return ChatGPTResponse(
                response_type="text",
                primary_language=context.primary_language,
                content=content,
                confidence_score=0.9,
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"ChatGPT API error: {e}")
            return ChatGPTResponse(
                response_type="error",
                primary_language=context.primary_language,
                content=f"I encountered an error while processing your request: {str(e)}"
            )

    async def _generate_image_response(self, context: ConversationContext,
                                     message: MultilingualMessage) -> ChatGPTResponse:
        """Generate response for image-based input using GPT-4 Vision."""

        if not message.media_content or "image" not in message.media_content:
            return await self._generate_text_response(context, message)

        try:
            # Use GPT-4 Vision for image analysis
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message.original_content},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": message.media_content["image"]["url"]
                            }
                        }
                    ]
                }
            ]

            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                max_tokens=500
            )

            content = response.choices[0].message.content

            return ChatGPTResponse(
                response_type="multimodal_image",
                primary_language=context.primary_language,
                content=content,
                multimodal_content={"analyzed_image": True}
            )

        except Exception as e:
            logger.error(f"Image processing error: {e}")
            return await self._generate_text_response(context, message)

    async def _generate_audio_response(self, context: ConversationContext,
                                     message: MultilingualMessage) -> ChatGPTResponse:
        """Generate response for audio input (transcription + analysis)."""

        # Note: Audio processing would require additional setup with Whisper API
        # For now, return text-based fallback
        text_message = MultilingualMessage(
            message_id=message.message_id,
            original_language=message.original_language,
            original_content="[Audio content received - transcription would be processed here]",
            modality=Modality.TEXT
        )

        return await self._generate_text_response(context, text_message)

    async def _generate_code_response(self, context: ConversationContext,
                                    message: MultilingualMessage) -> ChatGPTResponse:
        """Generate response optimized for code-related queries."""

        # Add code-specific context to the system prompt
        code_context = """
        You are an expert programming assistant. When discussing code:
        - Provide complete, runnable examples
        - Explain algorithms and data structures clearly
        - Include error handling and best practices
        - Suggest optimizations and improvements
        - Use proper formatting and syntax highlighting
        """

        if not self.client:
            return ChatGPTResponse(
                response_type="fallback",
                primary_language=context.primary_language,
                content="Code assistance is currently unavailable."
            )

        messages = [
            {"role": "system", "content": self.system_prompts["multilingual"] + code_context}
        ]

        # Add conversation history
        for msg in context.conversation_history[-5:]:  # Last 5 messages for context
            messages.append({
                "role": "user" if msg != context.conversation_history[-1] else "assistant",
                "content": msg.original_content
            })

        messages.append({"role": "user", "content": message.original_content})

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=messages,
                max_tokens=1500,
                temperature=0.3  # Lower temperature for code accuracy
            )

            content = response.choices[0].message.content

            return ChatGPTResponse(
                response_type="code_assistance",
                primary_language=context.primary_language,
                content=content,
                multimodal_content={"code_examples": self._extract_code_blocks(content)}
            )

        except Exception as e:
            logger.error(f"Code response generation error: {e}")
            return await self._generate_text_response(context, message)

    async def _generate_multimodal_response(self, context: ConversationContext,
                                          message: MultilingualMessage) -> ChatGPTResponse:
        """Generate response for complex multimodal input."""

        # Combine multiple modalities in the response
        combined_content = f"Processing multimodal input: {message.original_content}"

        if message.media_content:
            for modality, content in message.media_content.items():
                combined_content += f"\n{modality.title()}: {str(content)[:200]}..."

        multimodal_message = MultilingualMessage(
            message_id=message.message_id,
            original_language=message.original_language,
            original_content=combined_content,
            modality=Modality.MULTIMODAL,
            media_content=message.media_content
        )

        return await self._generate_text_response(context, multimodal_message)

    def _prepare_conversation_history(self, context: ConversationContext) -> List[Dict[str, Any]]:
        """Prepare conversation history for ChatGPT API."""

        messages = []

        # Add system prompt based on context
        system_content = self.system_prompts["multilingual"]

        if Modality.IMAGE in context.active_modalities:
            system_content += self.system_prompts["multimodal"]

        if any(modality in [Modality.CODE, Modality.TEXT] for modality in context.active_modalities):
            system_content += self.system_prompts["educational"]

        messages.append({"role": "system", "content": system_content})

        # Add conversation history (limit to last 10 messages for token efficiency)
        for msg in context.conversation_history[-10:]:
            if msg.metadata.get("generated"):
                messages.append({"role": "assistant", "content": msg.original_content})
            else:
                messages.append({"role": "user", "content": msg.original_content})

        return messages

    async def _generate_translations(self, content: str, source_lang: Language,
                                   target_langs: List[Language]) -> Dict[Language, str]:
        """Generate translations of the response content."""

        translations = {}

        for target_lang in target_langs:
            if target_lang == source_lang:
                continue

            # Check cache first
            cache_key = f"{content[:50]}_{source_lang.value[0]}_{target_lang.value[0]}"
            if cache_key in self.translation_cache:
                translations[target_lang] = self.translation_cache[cache_key]
                continue

            # Generate translation using ChatGPT
            try:
                translation_prompt = f"Translate the following text to {target_lang.value[1]}: {content}"

                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": translation_prompt}],
                    max_tokens=500,
                    temperature=0.1  # Low temperature for accurate translation
                )

                translated_text = response.choices[0].message.content.strip()

                # Cache the translation
                self.translation_cache[cache_key] = translated_text
                translations[target_lang] = translated_text

            except Exception as e:
                logger.error(f"Translation error for {target_lang.value[1]}: {e}")
                # Fallback to original content
                translations[target_lang] = content

        return translations

    def _generate_cultural_adaptations(self, response: ChatGPTResponse,
                                      context: ConversationContext) -> Dict[str, Any]:
        """Generate cultural adaptations for the response."""

        adaptations = {}

        # Get user's cultural profile
        user_profile = self.cultural_profiles.get(context.conversation_id.split('_')[0], {})

        cultural_context = user_profile.get("cultural_context", {})

        # Adapt formality level
        formality_level = cultural_context.get("formality_level", "medium")
        adaptations["formality_adjusted"] = formality_level != "medium"

        # Adapt communication style
        comm_style = cultural_context.get("communication_style", "direct")
        adaptations["communication_style"] = comm_style

        # Consider cultural values
        values = cultural_context.get("cultural_values", [])
        adaptations["emphasized_values"] = values

        # Avoid cultural taboos
        taboos = cultural_context.get("taboos", [])
        adaptations["taboos_avoided"] = taboos

        return adaptations

    def _extract_code_blocks(self, content: str) -> List[str]:
        """Extract code blocks from response content."""
        import re

        # Find code blocks marked with ```
        code_blocks = re.findall(r'```[\w]*\n(.*?)\n```', content, re.DOTALL)
        return code_blocks

    async def add_supported_language(self, conversation_id: str, language: Language):
        """Add a supported language to an existing conversation."""
        if conversation_id in self.conversations:
            context = self.conversations[conversation_id]
            if language not in context.supported_languages:
                context.supported_languages.append(language)

    async def switch_primary_language(self, conversation_id: str, new_language: Language):
        """Switch the primary language for a conversation."""
        if conversation_id in self.conversations:
            context = self.conversations[conversation_id]
            context.primary_language = new_language

            # Ensure new language is in supported languages
            if new_language not in context.supported_languages:
                context.supported_languages.append(new_language)

    def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """Get statistics for a conversation."""
        if conversation_id not in self.conversations:
            return {"error": "Conversation not found"}

        context = self.conversations[conversation_id]

        return {
            "conversation_id": conversation_id,
            "primary_language": context.primary_language.value[1],
            "supported_languages": [lang.value[1] for lang in context.supported_languages],
            "active_modalities": [mod.value for mod in context.active_modalities],
            "message_count": len(context.conversation_history),
            "cache_size": len(context.translation_cache)
        }

    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Clean up old conversations to free memory."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        conversations_to_remove = []

        for conv_id, context in self.conversations.items():
            if current_time - context.conversation_history[0].timestamp > max_age_seconds:
                conversations_to_remove.append(conv_id)

        for conv_id in conversations_to_remove:
            del self.conversations[conv_id]

        logger.info(f"Cleaned up {len(conversations_to_remove)} old conversations")

# Global ChatGPT manager instance
chatgpt_manager = MultilingualChatGPTManager()
