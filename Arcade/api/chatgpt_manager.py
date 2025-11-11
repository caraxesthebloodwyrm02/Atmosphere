#!/usr/bin/env python3
"""
ChatGPT Manager for Multilingual Support
Provides ChatGPT integration for translation and multilingual processing
"""

import os
import asyncio
import hashlib
import logging
from typing import Optional, Dict, Any, List

# Add safety imports
import re
from datetime import datetime, timedelta

import openai

class ChatGPTManager:
    """Manager for ChatGPT multilingual processing and translation services."""

    def __init__(self):
        self.api_key = os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required for OpenAI API access")

        # Validate API key format (should start with sk-)
        if not self.api_key.startswith('sk-'):
            raise ValueError("Invalid OpenAI API key format. Key should start with 'sk-'")

        # Initialize OpenAI client with production settings
        self.client = openai.OpenAI(
            api_key=self.api_key,
            # Explicitly set production API base (no custom endpoints)
            # base_url=None means use default OpenAI production endpoints
        )

        self.conversation_history = {}

        # Production-ready configurations
        self.max_retries = 3
        self.retry_delay = 1.0
        self.request_timeout = 30.0  # 30 second timeout for production

        # Safety configurations
        self.moderation_enabled = True
        self.max_input_tokens = 1000  # Limit input length
        self.max_output_tokens = 500  # Limit output length
        self.safety_violations = []  # Track safety incidents
        self.user_sessions = {}  # Track user sessions for safety identifiers

        # Safety thresholds
        self.moderation_thresholds = {
            'hate': 0.5,
            'hate/threatening': 0.5,
            'self-harm': 0.5,
            'sexual': 0.5,
            'sexual/minors': 0.5,
            'violence': 0.5,
            'violence/graphic': 0.5
        }

        # Input validation patterns
        self.suspicious_patterns = [
            r'ignore.*previous.*instructions',
            r'forget.*previous.*prompt',
            r'override.*safety',
            r'bypass.*restrictions',
            r'jailbreak',
            r'dan.*mode',  # DAN = Do Anything Now
            r'uncensored.*mode'
        ]

        print("✅ ChatGPT Manager initialized with authentic OpenAI API endpoints")
        print(f"   📍 API Endpoint: https://api.openai.com/v1")
        print(f"   🤖 Model: GPT-4")
        print(f"   🔐 Key Format: Valid (starts with 'sk-')")
        print(f"   🛡️ Safety Features: Enabled (Moderation API, Input Validation)")

    def generate_safety_identifier(self, user_id: str = None, session_id: str = None) -> str:
        """
        Generate a safety identifier for OpenAI API requests.
        Uses hashed user/session ID to avoid exposing personal information.
        """
        if user_id:
            # Hash the user ID for privacy
            return f"user_{hashlib.sha256(user_id.encode()).hexdigest()[:16]}"
        elif session_id:
            # Use session ID directly (already anonymous)
            return f"session_{session_id[:16]}"
        else:
            # Generate anonymous session ID
            import uuid
            return f"anon_{str(uuid.uuid4())[:16]}"

    def validate_input(self, message: str) -> Dict[str, Any]:
        """
        Validate user input for safety and appropriateness.

        Args:
            message: User input message

        Returns:
            Dict with validation results
        """
        validation = {
            'is_valid': True,
            'warnings': [],
            'blocked': False,
            'reason': None
        }

        # Check input length
        if len(message) > self.max_input_tokens * 4:  # Rough token estimate
            validation['is_valid'] = False
            validation['blocked'] = True
            validation['reason'] = 'Input too long'
            return validation

        # Check for suspicious patterns (potential jailbreaks)
        message_lower = message.lower()
        for pattern in self.suspicious_patterns:
            if re.search(pattern, message_lower, re.IGNORECASE):
                validation['is_valid'] = False
                validation['blocked'] = True
                validation['reason'] = 'Potential safety violation detected'
                self._log_safety_violation('jailbreak_attempt', message, pattern)
                return validation

        # Check for excessive special characters (potential injection)
        special_chars = sum(1 for c in message if not c.isalnum() and not c.isspace())
        if special_chars / len(message) > 0.3:  # More than 30% special chars
            validation['warnings'].append('High special character ratio detected')

        # Check for repeated patterns (potential spam/injection)
        if len(set(message.split())) < len(message.split()) * 0.5:  # Less than 50% unique words
            validation['warnings'].append('Repeated content detected')

        return validation

    async def check_moderation(self, content: str) -> Dict[str, Any]:
        """
        Check content using OpenAI's Moderation API.

        Args:
            content: Content to moderate

        Returns:
            Moderation results
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.moderations.create(input=content)
            )

            result = response.results[0]
            moderation = {
                'flagged': result.flagged,
                'categories': {},
                'scores': {}
            }

            # Extract categories and scores
            for category in result.categories:
                moderation['categories'][category] = getattr(result.categories, category)
                moderation['scores'][category] = getattr(result.category_scores, category)

            # Check against thresholds
            violations = []
            for category, score in moderation['scores'].items():
                if score > self.moderation_thresholds.get(category, 0.5):
                    violations.append(category)

            if violations:
                moderation['violations'] = violations
                self._log_safety_violation('moderation_violation', content, f"Violations: {', '.join(violations)}")

            return moderation

        except Exception as e:
            print(f"⚠️ Moderation check failed: {e}")
            return {'flagged': False, 'error': str(e)}

    def _log_safety_violation(self, violation_type: str, content: str, details: str):
        """Log a safety violation for monitoring and analysis."""
        violation = {
            'timestamp': datetime.now().isoformat(),
            'type': violation_type,
            'content_preview': content[:200] + '...' if len(content) > 200 else content,
            'details': details,
            'severity': 'high' if violation_type in ['jailbreak_attempt', 'moderation_violation'] else 'medium'
        }

        self.safety_violations.append(violation)

        # Keep only last 100 violations
        if len(self.safety_violations) > 100:
            self.safety_violations = self.safety_violations[-100:]

        # Log to console for immediate awareness
        print(f"🚨 Safety violation detected: {violation_type} - {details}")

    def get_safety_report(self) -> Dict[str, Any]:
        """Get a comprehensive safety report."""
        return {
            'total_violations': len(self.safety_violations),
            'recent_violations': self.safety_violations[-10:],  # Last 10
            'violation_types': list(set(v['type'] for v in self.safety_violations)),
            'moderation_enabled': self.moderation_enabled,
            'input_limits': {
                'max_input_tokens': self.max_input_tokens,
                'max_output_tokens': self.max_output_tokens
            },
            'safety_thresholds': self.moderation_thresholds
        }

    async def process_multilingual_message(self, conversation_id: str, message: str,
                                        user_id: str = None, session_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Process a multilingual message using ChatGPT with comprehensive safety measures.

        Args:
            conversation_id: Unique identifier for the conversation
            message: The message to process
            user_id: User identifier for safety tracking
            session_id: Session identifier for safety tracking

        Returns:
            Response object with 'content' attribute containing the processed message
        """
        try:
            # Step 1: Input Validation
            validation = self.validate_input(message)
            if not validation['is_valid']:
                return type('SafetyResponse', (), {
                    'content': "I'm sorry, but I cannot process this request due to safety guidelines.",
                    'safety_blocked': True,
                    'reason': validation['reason']
                })()

            if validation['warnings']:
                print(f"⚠️ Input warnings: {', '.join(validation['warnings'])}")

            # Step 2: Moderation Check (if enabled)
            if self.moderation_enabled:
                moderation = await self.check_moderation(message)
                if moderation.get('flagged'):
                    self._log_safety_violation('moderation_blocked', message,
                                             f"Moderation flagged: {moderation.get('violations', [])}")
                    return type('SafetyResponse', (), {
                        'content': "I'm sorry, but this content violates our safety guidelines.",
                        'safety_blocked': True,
                        'moderation_violations': moderation.get('violations', [])
                    })()

            # Get or create conversation history
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []

            history = self.conversation_history[conversation_id]

            # Prepare messages for ChatGPT
            messages = [
                {
                    "role": "system",
                    "content": """You are a multilingual communication assistant specializing in natural, conversational translations and responses.

Your role is to:
- Translate messages to natural, conversational English while preserving tone and intent
- Respond in a friendly, human-like manner
- Maintain cultural sensitivity and appropriate social cues
- Keep translations casual and conversational (not formal/literal)
- For greetings like "kire? ki koros?", respond naturally like "hey! what's up?"
- Always respond in a way that feels like talking to a friend

Guidelines for translation:
- Preserve the casual, friendly tone of the original
- Use natural English expressions and idioms when appropriate
- Don't make translations sound robotic or overly formal
- Consider cultural context and social norms
- Return only the translated/processed text without additional commentary

You are helping in a friendly terminal environment where users interact naturally."""
                }
            ]

            # Add recent conversation history for context (last 5 messages)
            messages.extend(history[-5:])

            # Add current message
            messages.append({"role": "user", "content": message})

            # Generate safety identifier
            safety_identifier = self.generate_safety_identifier(user_id, session_id)

            # Call ChatGPT API with retry logic and safety identifier
            response = await self._make_openai_request(messages, safety_identifier)

            # Extract response content
            content = response.choices[0].message.content

            # Step 3: Output Moderation (check generated content)
            if self.moderation_enabled:
                output_moderation = await self.check_moderation(content)
                if output_moderation.get('flagged'):
                    self._log_safety_violation('output_moderation_violation', content,
                                             f"Output flagged: {output_moderation.get('violations', [])}")
                    return type('SafetyResponse', (), {
                        'content': "I'm sorry, but the generated response contains content that violates safety guidelines.",
                        'safety_blocked': True,
                        'output_moderation_violations': output_moderation.get('violations', [])
                    })()

            # Update conversation history
            history.append({"role": "user", "content": message})
            history.append({"role": "assistant", "content": content})

            # Keep history manageable (max 20 messages per conversation)
            if len(history) > 20:
                history[:] = history[-20:]

            # Return response object matching expected interface
            return type('ChatGPTResponse', (), {
                'content': content,
                'safety_check_passed': True,
                'warnings': validation['warnings']
            })()

        except openai.APIError as e:
            print(f"❌ OpenAI API Error: {e}")
            return None
        except openai.RateLimitError as e:
            print(f"❌ OpenAI Rate Limit Exceeded: {e}")
            print("   Please check your OpenAI API usage and billing")
            return None
        except openai.AuthenticationError as e:
            print(f"❌ OpenAI Authentication Failed: {e}")
            print("   Please verify your OPENAI_API_KEY is correct")
            return None
        except Exception as e:
            print(f"❌ ChatGPT processing error: {str(e)}")
            return None

    async def _make_openai_request(self, messages: list, safety_identifier: str = None) -> Any:
        """
        Make authenticated request to OpenAI API with retry logic and safety monitoring.

        Args:
            messages: List of message dictionaries for the conversation
            safety_identifier: Hashed user/session identifier for safety monitoring

        Returns:
            OpenAI API response object

        Raises:
            Exception: If all retry attempts fail
        """
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.chat.completions.create(
                        model="gpt-4",  # Authentic GPT-4 model
                        messages=messages,
                        max_tokens=self.max_output_tokens,  # Apply output limits
                        temperature=0.7,
                        presence_penalty=0.2,
                        frequency_penalty=0.2,
                        timeout=self.request_timeout,  # Production timeout
                        safety_identifier=safety_identifier  # OpenAI safety monitoring
                    )
                )
                return response

            except (openai.APIError, openai.Timeout) as e:
                if attempt == self.max_retries - 1:
                    raise e
                print(f"⚠️ OpenAI API attempt {attempt + 1} failed, retrying in {self.retry_delay}s: {e}")
                await asyncio.sleep(self.retry_delay)
                self.retry_delay *= 2  # Exponential backoff

            except Exception as e:
                # For non-OpenAI errors, don't retry
                raise e

    def verify_openai_connection(self) -> Dict[str, Any]:
        """
        Verify OpenAI API connection and endpoint authenticity.

        Returns:
            Dictionary with connection verification results
        """
        verification = {
            'api_key_present': bool(self.api_key),
            'api_key_format_valid': self.api_key.startswith('sk-') if self.api_key else False,
            'client_initialized': hasattr(self, 'client') and self.client is not None,
            'endpoint_url': 'https://api.openai.com/v1',
            'model': 'gpt-4',
            'connection_tested': False,
            'connection_successful': False,
            'error_message': None
        }

        if not verification['client_initialized']:
            verification['error_message'] = 'OpenAI client not initialized'
            return verification

        try:
            # Test connection with a minimal request
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=10.0
            )

            verification['connection_tested'] = True
            verification['connection_successful'] = True
            verification['response_received'] = bool(response.choices)

        except openai.AuthenticationError as e:
            verification['connection_tested'] = True
            verification['error_message'] = f'Authentication failed: {str(e)}'
        except openai.RateLimitError as e:
            verification['connection_tested'] = True
            verification['error_message'] = f'Rate limit exceeded: {str(e)}'
        except Exception as e:
            verification['connection_tested'] = True
            verification['error_message'] = f'Connection failed: {str(e)}'

        return verification

    def get_api_status(self) -> Dict[str, Any]:
        """
        Get comprehensive API status for deployment verification.

        Returns:
            Dictionary with API status information
        """
        status = {
            'service': 'OpenAI GPT-4 API',
            'endpoint': 'https://api.openai.com/v1/chat/completions',
            'authentication': 'API Key (Bearer token)',
            'supported_models': ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
            'current_model': 'gpt-4',
            'features': [
                'Multilingual text processing',
                'Real-time translation',
                'Conversational AI',
                'Natural language understanding'
            ],
            'rate_limits': 'Varies by account tier',
            'timeout_config': f'{self.request_timeout}s',
            'retry_config': f'{self.max_retries} attempts with exponential backoff'
        }

        # Add verification results
        verification = self.verify_openai_connection()
        status['verification'] = verification

        return status

    async def translate_text(self, text: str, target_language: str = "en", source_language: str = None) -> Optional[str]:
        """
        Translate text to specified language.

        Args:
            text: Text to translate
            target_language: Target language code (default: 'en' for English)
            source_language: Source language code (auto-detect if None)

        Returns:
            Translated text or None if translation fails
        """
        try:
            prompt = f"Translate the following text to {target_language}"
            if source_language:
                prompt += f" from {source_language}"
            prompt += f":\n\n{text}\n\nProvide only the translation, nothing else."

            response = await self.process_multilingual_message(f"translate_{hash(text)}", prompt)
            if response and hasattr(response, 'content'):
                return response.content.strip()
            return None

        except Exception as e:
            print(f"❌ Translation error: {str(e)}")
            return None

    async def detect_language(self, text: str) -> Optional[str]:
        """
        Detect the language of the given text.

        Args:
            text: Text to analyze

        Returns:
            Language code (e.g., 'en', 'es', 'fr') or None if detection fails
        """
        try:
            prompt = f"What language is this text in? Respond with only the ISO language code (e.g., 'en', 'es', 'fr', 'de', 'bn' for Bengali, etc.): {text}"

            response = await self.process_multilingual_message(f"detect_{hash(text)}", prompt)
            if response and hasattr(response, 'content'):
                lang_code = response.content.strip().lower()
                # Validate it's a reasonable language code (2-3 characters)
                if 2 <= len(lang_code) <= 3 and lang_code.isalpha():
                    return lang_code
            return None

        except Exception as e:
            print(f"❌ Language detection error: {str(e)}")
            return None

    def get_supported_languages(self) -> list:
        """
        Get list of supported languages for translation.

        Returns:
            List of language codes and names
        """
        return [
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
            ('de', 'German'),
            ('it', 'Italian'),
            ('pt', 'Portuguese'),
            ('ru', 'Russian'),
            ('ja', 'Japanese'),
            ('ko', 'Korean'),
            ('zh', 'Chinese'),
            ('ar', 'Arabic'),
            ('hi', 'Hindi'),
            ('bn', 'Bengali'),
            ('ur', 'Urdu'),
            ('th', 'Thai'),
            ('vi', 'Vietnamese'),
            ('nl', 'Dutch'),
            ('sv', 'Swedish'),
            ('da', 'Danish'),
            ('no', 'Norwegian'),
            ('fi', 'Finnish'),
            ('pl', 'Polish'),
            ('cs', 'Czech'),
            ('hu', 'Hungarian'),
            ('tr', 'Turkish'),
            ('he', 'Hebrew'),
            ('el', 'Greek'),
            ('ro', 'Romanian'),
            ('bg', 'Bulgarian'),
            ('hr', 'Croatian'),
            ('sk', 'Slovak'),
            ('sl', 'Slovenian'),
            ('et', 'Estonian'),
            ('lv', 'Latvian'),
            ('lt', 'Lithuanian'),
        ]

    def clear_conversation_history(self, conversation_id: str = None):
        """
        Clear conversation history.

        Args:
            conversation_id: Specific conversation to clear, or all if None
        """
        if conversation_id:
            self.conversation_history.pop(conversation_id, None)
        else:
            self.conversation_history.clear()

    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about conversations.

        Returns:
            Dictionary with conversation statistics
        """
        total_conversations = len(self.conversation_history)
        total_messages = sum(len(history) for history in self.conversation_history.values())

        return {
            'total_conversations': total_conversations,
            'total_messages': total_messages,
            'average_messages_per_conversation': total_messages / max(total_conversations, 1)
        }
