#!/usr/bin/env python3
"""
Enhanced Interactive Arcade Terminal with AI Intelligence
======================================================

An intelligent, interactive terminal that integrates AI capabilities,
API key management, and advanced features for the Arcade system.
"""

import os
import json
import asyncio
import logging
import uuid
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from contextlib import asynccontextmanager
import sys

# Add the Arcade directory to the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import aiohttp
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import existing components
try:
    from .terminal_handler import TerminalHandler
    from .security import SecurityManager
    from .game_engine import GameEngine
    from .routing_integration import RoutingIntegration
    from .tool_integration import ToolIntegration
    from .learning_companion_api import router as learning_router
except ImportError:
    # For direct execution
    from terminal_handler import TerminalHandler
    from security import SecurityManager
    from game_engine import GameEngine
    from routing_integration import RoutingIntegration
    from tool_integration import ToolIntegration
    from learning_companion_api import router as learning_router

# Import AI integration modules
try:
    from grokipedia import Grokipedia
    from claude_game_engine import ClaudeGameEngine
    from chatgpt_manager import ChatGPTManager
    from gemini_maintenance import GeminiMaintenanceManager
    from mistral_integration import MistralManager
    from io_design_intelligence import IODesignIntelligence
    from atmosphere_orchestrator import AtmosphereOrchestrator

    # Initialize AI components
    grokipedia = Grokipedia()
    claude_game_engine = ClaudeGameEngine()
    chatgpt_manager = ChatGPTManager()
    gemini_maintenance_manager = GeminiMaintenanceManager()
    mistral_manager = MistralManager()
    llama_behavioral_manager = llama_behavioral_manager
    io_design_intelligence = IODesignIntelligence()
    atmosphere_orchestrator = AtmosphereOrchestrator()

except ImportError as e:
    logger.warning(f"Some AI integration modules not available: {e}")
    # Set to None so the code can handle missing modules gracefully
    grokipedia = None
    claude_game_engine = None
    chatgpt_manager = None
    gemini_maintenance_manager = None
    mistral_manager = None
    llama_behavioral_manager = None
    io_design_intelligence = None
    atmosphere_orchestrator = None

# Import Llama Behavioral Integration
try:
    from ..llama_behavioral_integration import llama_behavioral_manager
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from llama_behavioral_integration import llama_behavioral_manager

# Import Architectural Business Management
try:
    from ..architectural_business_management import architectural_business_manager
except ImportError:
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from architectural_business_management import architectural_business_manager

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Manages API keys and external service integrations."""

    def __init__(self):
        self.api_keys = {}
        self.services = {}
        self.load_api_keys()

    def load_api_keys(self):
        """Load API keys from environment variables and config files."""
        required_keys = ['OPENAI_API_KEY']
        optional_keys = [
            'ANTHROPIC_API_KEY',
            'GOOGLE_API_KEY',
            'HUGGINGFACE_API_KEY',
            'REPLICATE_API_KEY'
        ]
        
        # Check for required keys
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")
            
        # Load all available keys
        all_keys = required_keys + optional_keys
        self.api_keys.update({
            key.lower().replace('_api_key', ''): os.getenv(key)
            for key in all_keys
            if os.getenv(key)
        })

        # Initialize service clients
        self._initialize_services()
        
        logger.info(f"Loaded API keys for services: {', '.join(self.api_keys.keys())}")

    def _initialize_services(self):
        """Initialize service clients."""
        if 'openai' in self.api_keys:
            self.services['openai'] = openai.OpenAI(api_key=self.api_keys['openai'])

    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        return self.api_keys.get(service)

    def has_service(self, service: str) -> bool:
        """Check if a service is available."""
        return service in self.api_keys and self.api_keys[service] is not None

    def list_available_services(self) -> List[str]:
        """List all available services."""
        return list(self.api_keys.keys())


class AIAssistant:
    """AI-powered assistant for the interactive terminal."""

    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.conversation_history = {}
        self.system_prompt = """
        You are Grok, a helpful and maximally truthful AI built by xAI. You have access to:
        • Grokipedia: Comprehensive knowledge library
        • Claude Code: AI-powered coding challenges and assistance
        • ChatGPT: Advanced multilingual and multimodal interactions

        When users ask questions, you can:
        1. Answer directly from your knowledge
        2. Query Grokipedia for detailed explanations using 'grokipedia query <topic>'
        3. Use Claude for coding challenges with 'claude <command>'
        4. Leverage ChatGPT for multilingual support with 'chatgpt <command>'
        5. Explain complex concepts with real-world examples
        6. Provide accurate, factual information

        Always be helpful, truthful, and engaging. Use emojis sparingly but effectively.
        """
        self.grokipedia = grokipedia
        self.claude_game_engine = claude_game_engine
        self.chatgpt_manager = chatgpt_manager
        self.gemini_maintenance_manager = gemini_maintenance_manager
        self.mistral_manager = mistral_manager
        self.llama_behavioral_manager = llama_behavioral_manager
        self.io_design_intelligence = io_design_intelligence
        self.atmosphere_orchestrator = atmosphere_orchestrator
        self.architectural_business_manager = architectural_business_manager

    async def generate_response(self, user_input: str, session_id: str,
                              context: Dict[str, Any] = None) -> str:
        """Generate an AI response with comprehensive system access, behavioral intelligence, IO design principles, Atmosphere ecosystem orchestration, and enterprise architectural business management."""

        # Check for various AI system commands
        if user_input.lower().startswith("grokipedia"):
            return await self._handle_grokipedia_command(user_input, session_id)
        elif user_input.lower().startswith("claude") or user_input.lower().startswith("code"):
            return await self._handle_claude_command(user_input, session_id)
        elif user_input.lower().startswith("chatgpt") or user_input.lower().startswith("gpt"):
            return await self._handle_chatgpt_command(user_input, session_id)
        elif user_input.lower().startswith("gemini") or user_input.lower().startswith("maintenance"):
            return await self._handle_gemini_command(user_input, session_id)
        elif user_input.lower().startswith("mistral") or user_input.lower().startswith("pixtral"):
            return await self._handle_mistral_command(user_input, session_id)
        elif user_input.lower().startswith("llama") or user_input.lower().startswith("behavior"):
            return await self._handle_llama_command(user_input, session_id)
        elif user_input.lower().startswith("io") or user_input.lower().startswith("design"):
            return await self._handle_io_command(user_input, session_id)
        elif user_input.lower().startswith("atmosphere") or user_input.lower().startswith("feedback"):
            return await self._handle_atmosphere_command(user_input, session_id)
        elif user_input.lower().startswith("architecture") or user_input.lower().startswith("business"):
            return await self._handle_architecture_command(user_input, session_id)

        # Get or create conversation history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        history = self.conversation_history[session_id]

        # Prepare messages
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]

        # Add context if provided
        if context:
            context_str = f"Current context: {json.dumps(context, indent=2)}"
            messages.append({"role": "system", "content": context_str})

        # Add conversation history (last 10 messages)
        messages.extend(history[-10:])

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        # Try to enhance response with Grokipedia if it's a knowledge question
        grokipedia_context = await self._get_grokipedia_context(user_input)
        if grokipedia_context:
            messages.append({"role": "system", "content": f"Relevant knowledge from Grokipedia: {grokipedia_context}"})

        try:
            if self.api_key_manager.has_service('openai'):
                client = self.api_key_manager.services['openai']
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )

                ai_response = response.choices[0].message.content

                # Update conversation history
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": ai_response})

                return ai_response
            else:
                # Fallback response with Grokipedia
                return await self._generate_fallback_response(user_input, session_id)

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return f"🤖 AI Error: {str(e)}. Try using 'grokipedia query <topic>' for knowledge lookup."

    async def _handle_grokipedia_command(self, command: str, session_id: str) -> str:
        """Handle Grokipedia-specific commands with enhanced error handling."""
        if not self.grokipedia:
            return "⚠️ Grokipedia is not available. Please check the service configuration."
            
        try:
            parts = command.split()
            if len(parts) < 2:
                return "📚 Grokipedia Commands:\n• grokipedia query <topic> - Search for knowledge\n• grokipedia explain <concept> - Get detailed explanation\n• grokipedia categories - List knowledge categories"

            subcommand = parts[1].lower()

            if subcommand == "query" and len(parts) > 2:
                query = " ".join(parts[2:])
                if not query or len(query) < 3:
                    return "🔍 Please provide a more specific search query (at least 3 characters)."
                    
                try:
                    result = await self.grokipedia.query(query, max_results=3)
                    
                    if not result or not hasattr(result, 'entries'):
                        return "⚠️ Error: Invalid response from Grokipedia service."
                        
                    if result.entries:
                        response = f"📚 Grokipedia Results for '{query}':\n\n"
                        for i, entry in enumerate(result.entries[:3], 1):
                            if not all(hasattr(entry, attr) for attr in ['title', 'category', 'content']):
                                continue
                            response += f"{i}. **{entry.title}**\n"
                            response += f"   Category: {getattr(entry, 'category', 'N/A')}\n"
                            response += f"   {entry.content[:200]}...\n\n"
                        if response == f"📚 Grokipedia Results for '{query}':\n\n":
                            return f"📭 No valid results found for '{query}' in Grokipedia."
                            
                        response += f"Found {getattr(result, 'total_found', 0)} total results. "
                        if hasattr(result, 'confidence_score'):
                            response += f"Confidence: {result.confidence_score:.1%}"
                        return response
                    else:
                        return f"📭 No results found for '{query}' in Grokipedia."
                        
                except Exception as e:
                    logger.error(f"Grokipedia query failed: {str(e)}", exc_info=True)
                    return f"⚠️ Error querying Grokipedia: {str(e)}. Please try again later."

            elif subcommand == "explain" and len(parts) > 2:
                concept = " ".join(parts[2:])
                # Try to find matching concept
                result = await self.grokipedia.query(concept, max_results=1)
                if result.entries:
                    entry = result.entries[0]
                    explanation = await self.grokipedia.explain_concept(entry.id, "comprehensive")
                    return f"📖 **{entry.title}**\n\n{explanation[:1000]}..."
                else:
                    return f"📚 Concept '{concept}' not found in Grokipedia."

            elif subcommand == "categories":
                categories = self.grokipedia.get_categories()
                stats = self.grokipedia.get_category_stats()
                response = "📚 Grokipedia Categories:\n\n"
                for category in categories:
                    count = stats.get(category, 0)
                    response += f"• {category.title()}: {count} entries\n"
                return response

            else:
                return "❓ Unknown Grokipedia command. Try 'grokipedia help'"

        except Exception as e:
            logger.error(f"Grokipedia command failed: {str(e)}", exc_info=True)
            return f"⚠️ Grokipedia command failed: {str(e)}"

    async def _handle_claude_command(self, command: str, session_id: str) -> str:
        """Handle Claude-powered coding game mechanics commands with enhanced error handling."""
        if not self.claude_game_engine:
            return "⚠️ Claude Game Engine is not available. Please check the service configuration."
            
        try:
            parts = command.split()
            if len(parts) < 2:
                return "🎮 Claude Code Game Commands:\n• claude start - Start coding session\n• claude challenge <type> - Generate challenge\n• claude help - Get coding assistance\n• claude submit <code> - Submit solution\n• claude status - Check session status\n• claude leaderboard - View rankings"

            subcommand = parts[1].lower()

            if subcommand == "start":
                session = await self.claude_game_engine.start_coding_session(f"user_{session_id}")
                return f"🎯 Claude Coding Session Started!\nSession ID: {session.session_id}\nLevel: {session.level}\nScore: {session.score}\n\nTry 'claude challenge algorithm_puzzle' to begin!"

            elif subcommand == "challenge":
                if len(parts) < 3:
                    return "🎯 Available Challenge Types:\n• algorithm_puzzle\n• code_optimization\n• debugging_quest\n• architecture_design\n• security_audit\n\nUsage: claude challenge <type>"

                challenge_type = parts[2]
                difficulty = parts[3] if len(parts) > 3 else "medium"

                challenge = await self.claude_game_engine.generate_challenge(session_id, challenge_type, difficulty)

                if challenge:
                    response = f"🎯 **{challenge.title}**\n\n"
                    response += f"⏱️ Time Limit: {challenge.time_limit // 60} minutes\n"
                    response += f"🏆 Points: {challenge.points_value}\n\n"
                    response += f"📝 {challenge.description}\n\n"

                    if challenge.starter_code:
                        response += f"```python\n{challenge.starter_code}\n```\n\n"

                    if challenge.hints:
                        response += f"💡 Hint: {challenge.hints[0]}\n\n"

                    response += "Use 'claude submit <your_code>' to submit your solution!"
                    return response
                else:
                    return "❌ Failed to generate challenge. Try again."

            elif subcommand == "help":
                query = " ".join(parts[2:]) if len(parts) > 2 else "coding help"
                assistance = await self.claude_game_engine.get_claude_assistance(session_id, query)

                response = f"🤖 Claude Code Assistant:\n\n{assistance.content}"

                if assistance.code_suggestions:
                    response += "\n\n💻 Code Suggestions:\n" + "\n".join(f"• {sug}" for sug in assistance.code_suggestions[:3])

                if assistance.next_steps:
                    response += "\n\n🎯 Next Steps:\n" + "\n".join(f"• {step}" for step in assistance.next_steps[:3])

                return response

            elif subcommand == "submit":
                if len(parts) < 3:
                    return "❌ Usage: claude submit <your_code>\n\nExample: claude submit \"def hello(): return 'Hello World!'\""

                code = " ".join(parts[2:])
                result = await self.claude_game_engine.submit_code_solution(session_id, code)

                if "error" in result:
                    return f"❌ {result['error']}"

                response = f"✅ Solution Submitted!\n\n"
                response += f"📊 Score: {result['score']}/100\n"
                response += f"⏱️ Time Taken: {result['time_taken']} seconds\n"
                response += f"💡 Hints Used: {result['hints_used']}\n\n"
                response += f"📝 Feedback: {result['feedback']}\n\n"

                if result.get('new_achievements'):
                    response += f"🏆 New Achievements: {', '.join(result['new_achievements'])}\n\n"

                response += "🎮 Ready for the next challenge? Try 'claude challenge'!"
                return response

            elif subcommand == "status":
                status = self.claude_game_engine.get_session_status(session_id)
                if status:
                    response = f"🎮 Claude Coding Session Status\n\n"
                    response += f"🏆 Score: {status['score']}\n"
                    response += f"⭐ Level: {status['level']}\n"
                    response += f"🎯 State: {status['game_state']}\n"
                    response += f"⏱️ Time Elapsed: {status['time_elapsed']:.0f} seconds\n"
                    response += f"🤖 Claude Interactions: {status['claude_interactions']}\n\n"

                    if status['current_challenge']:
                        response += f"🎯 Current Challenge: {status['current_challenge']}\n"

                    if status['achievements']:
                        response += f"🏆 Achievements: {', '.join(status['achievements'][:5])}"
                        if len(status['achievements']) > 5:
                            response += f" and {len(status['achievements']) - 5} more"

                    return response
                else:
                    return "❌ No active coding session. Start one with 'claude start'"

            elif subcommand == "leaderboard":
                # Simplified leaderboard (would be stored in database in real implementation)
                return "🏆 Claude Code Leaderboard\n\nComing soon! Track your progress and compete with other coders."

            else:
                return "❓ Unknown Claude command. Try 'claude help' for available commands"

        except Exception as e:
            logger.error(f"Claude command failed: {str(e)}", exc_info=True)
            return f"⚠️ Claude command failed: {str(e)}"

    async def _get_grokipedia_context(self, user_input: str) -> Optional[str]:
        """Get relevant Grokipedia context for user input."""
        if not self.grokipedia:
            return None
        
        try:
            # Simple heuristic: if question contains certain keywords, try to get context
            knowledge_keywords = ['what', 'how', 'why', 'explain', 'define', 'meaning']
            if any(keyword in user_input.lower() for keyword in knowledge_keywords):
                # Extract potential topic (simplified)
                words = user_input.lower().split()
                # Remove question words and try to find a topic
                filtered_words = [w for w in words if w not in ['what', 'is', 'are', 'how', 'why', 'does', 'do', 'can', 'the', 'a', 'an']]
                if filtered_words:
                    topic = " ".join(filtered_words[:3])  # Take first few words as topic
                    result = await self.grokipedia.query(topic, max_results=1)
                    if result.entries:
                        return result.entries[0].content[:300]  # Return first 300 chars of content
        except Exception as e:
            logger.warning(f"Failed to get Grokipedia context: {e}")
        
        return None

    async def _generate_fallback_response(self, user_input: str, session_id: str) -> str:
        """Generate response without external AI when OpenAI is unavailable."""
        return f"🤖 AI services are currently limited. I can help you with:\n\n• Basic terminal commands (ls, cd, pwd, etc.)\n• File operations\n• System information\n\nTry 'help' for available commands or 'grokipedia query <topic>' for knowledge lookup."

    def get_help_suggestions(self, command: str) -> List[str]:
        """Get AI-powered help suggestions for commands."""
        # This would normally use AI to provide contextual help
        # For now, return basic suggestions
        return ["Try 'help' for available commands", "Use 'grokipedia query <topic>' for knowledge", "Check 'ai ask <question>' for AI assistance"]


class EnhancedTerminalHandler:
    """Enhanced terminal handler with AI capabilities."""

    def __init__(self, sandbox_root: Path, security_manager, ai_assistant: AIAssistant):
        self.base_handler = None  # Would normally be TerminalHandler
        self.ai_assistant = ai_assistant
        self.sessions = {}  # Store enhanced session data

    async def create_session(self, session_id: str, initial_directory: Path):
        """Create an enhanced terminal session."""
        self.sessions[session_id] = {
            'session_id': session_id,
            'directory': initial_directory,
            'created_at': datetime.now(),
            'ai_enabled': True
        }
        return self.sessions[session_id]

    async def process_command(self, session_id: str, command: str) -> str:
        """Process a command with AI enhancement."""
        if session_id not in self.sessions:
            return "❌ Session not found"

        # Check if it's an AI command
        if command.lower().startswith(('ai ', 'grokipedia ', 'claude ', 'chatgpt ', 'gemini ', 'mistral ', 'llama ', 'atmosphere ', 'architecture ')):
            try:
                return await self.ai_assistant.generate_response(command, session_id)
            except Exception as e:
                return f"❌ AI command failed: {str(e)}"
        
        # For non-AI commands, provide basic terminal simulation
        command_lower = command.lower().strip()
        
        if command_lower in ['help', 'h', '?']:
            return """🎮 Enhanced Arcade Terminal Commands:

🤖 AI Commands:
• ai ask <question> - Ask AI assistant anything
• grokipedia query <topic> - Search knowledge base
• grokipedia explain <concept> - Get detailed explanations
• claude start - Begin coding challenges
• chatgpt ask <question> - Multilingual AI chat
• gemini status - System maintenance info
• mistral help - AI model fine-tuning
• llama session - Behavioral AI interaction
• atmosphere feedback <message> - Submit feedback
• architecture dashboard - Business metrics

🖥️ Terminal Commands:
• ls, dir - List directory contents
• cd <path> - Change directory
• pwd - Show current directory
• clear, cls - Clear screen
• help - Show this help

🎯 Try 'ai ask What can you help me with?' to get started!"""

        elif command_lower in ['ls', 'dir']:
            return "📁 Directory listing (simulated):\n• ai_examples/\n• config.json\n• logs/\n• sandbox/"

        elif command_lower == 'pwd':
            return f"📍 Current directory: {self.sessions[session_id]['directory']}"

        elif command_lower.startswith('cd '):
            path = command[3:].strip()
            return f"📂 Changed to directory: {path}"

        elif command_lower in ['clear', 'cls']:
            return "🧹 Screen cleared"

        else:
            return f"❓ Unknown command: {command}\n💡 Try 'help' for available commands or 'ai ask {command}' for AI assistance"


# Initialize enhanced components
api_key_manager = APIKeyManager()
ai_assistant = AIAssistant(api_key_manager)
enhanced_terminal_handler = EnhancedTerminalHandler(
    sandbox_root=Path(__file__).parent.parent / "sandbox" / "virtual_fs",
    security_manager=None,  # Simplified
    ai_assistant=ai_assistant
)
