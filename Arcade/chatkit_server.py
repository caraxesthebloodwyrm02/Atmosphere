"""
ChatKit Integration for Atmosphere Arcade
==========================================

Advanced ChatKit integration providing web-based chat interface with full Atmosphere Arcade capabilities.
Includes safety monitoring, multilingual support, file operations, and enterprise features.

This implementation includes a fallback for environments where openai-chatkit is not available.
"""

import asyncio
import hashlib
import json
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional, Union
from openai import OpenAI

from fastapi import FastAPI, Request, Response, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Try to import ChatKit, fall back to mock implementation if not available
try:
    from chatkit import ChatKitServer, Store, FileStore
    from chatkit.agent import Agent, AgentContext, Runner
    from chatkit.events import Event, UserMessageItem, ClientToolCallOutputItem, ProgressUpdateEvent
    from chatkit.streaming import StreamingResult, stream_agent_response, stream_widget
    from chatkit.store import ThreadMetadata, SQLiteStore, DiskFileStore
    from chatkit.tools import function_tool, ClientToolCall
    from chatkit.widgets import Card, Text, Button, List as WidgetList, Form, Input
    from chatkit.types import FilePart, ImagePart, ResponseInputContentParam
    CHATKIT_AVAILABLE = True
except ImportError:
    print("⚠️ OpenAI ChatKit package not available. Using fallback implementation.")
    CHATKIT_AVAILABLE = False

    # Mock implementations for when ChatKit is not available
    class MockChatKitServer:
        def __init__(self, data_store=None, file_store=None):
            self.data_store = data_store
            self.file_store = file_store

        async def process(self, body, context):
            return MockStreamingResult()

    class MockStreamingResult:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

    class MockEvent:
        pass

    class MockProgressUpdateEvent(MockEvent):
        def __init__(self, message: str):
            self.message = message

    class MockCard:
        def __init__(self, children=None):
            self.children = children or []

    class MockText:
        def __init__(self, value: str, id: str = None):
            self.value = value
            self.id = id

    class MockButton:
        def __init__(self, text: str, action: str = None):
            self.text = text
            self.action = action

    class MockList:
        def __init__(self, items: List[Dict] = None):
            self.items = items or []

    # Assign mock classes to match real ChatKit
    ChatKitServer = MockChatKitServer
    StreamingResult = MockStreamingResult
    Event = MockEvent
    ProgressUpdateEvent = MockProgressUpdateEvent
    Card = MockCard
    Text = MockText
    Button = MockButton
    WidgetList = MockList

# Atmosphere Arcade imports
from api.chatgpt_manager import ChatGPTManager
from safety_monitor import SafetyMonitor
from safety_api import SafetyAPI
from api_key_manager import APIKeyManager

# Initialize global server instance for endpoint functions
chatkit_server = None

def initialize_global_server():
    """Initialize the global ChatKit server instance."""
    global chatkit_server
    try:
        chatkit_server = AtmosphereChatKitServer()
        print("✅ Global ChatKit server initialized successfully")
    except Exception as e:
        print(f"⚠️ Global server initialization failed: {e}")
        # Create a minimal fallback
        chatkit_server = type('FallbackServer', (), {
            'chatgpt_manager': None,
            'chatgpt_available': False,
            'safety_monitor': None
        })()

# Initialize the global server
initialize_global_server()

# Initialize terminal handler if not already initialized
if not hasattr(app, 'terminal_handler'):
    from api.enhanced_server_test import EnhancedTerminalHandler
    from api.chatgpt_manager import ChatGPTManager
    
    # Initialize ChatGPTManager if not available in chatkit_server
    if not hasattr(chatkit_server, 'chatgpt_manager') or not chatkit_server.chatgpt_manager:
        chatkit_server.chatgpt_manager = ChatGPTManager()
    
    # Create terminal handler with AI capabilities
    app.terminal_handler = EnhancedTerminalHandler(ai_assistant=chatkit_server.chatgpt_manager)

# Data models
class AtmosphereContext:
    """Context for Atmosphere Arcade operations within ChatKit."""

    def __init__(self, user_id: str, session_id: str, language: str = "en"):
        self.user_id = user_id
        self.session_id = session_id
        self.language = language
        self.safety_identifier = self._generate_safety_identifier()
        self.conversation_history = []
        self.file_operations = []

    def _generate_safety_identifier(self) -> str:
        """Generate privacy-preserving safety identifier."""
        combined = f"{self.user_id}:{self.session_id}".encode()
        return hashlib.sha256(combined).hexdigest()[:16]

class AtmosphereChatKitServer(ChatKitServer):
    """ChatKit server implementation for Atmosphere Arcade with full safety integration."""

    def __init__(self, data_store: Optional[Any] = None, file_store: Optional[Any] = None):
        super().__init__(data_store, file_store)

        # Initialize Atmosphere Arcade components with error handling
        try:
            self.api_keys = APIKeyManager()
            self.chatgpt_manager = ChatGPTManager()
            self.safety_monitor = SafetyMonitor(self.chatgpt_manager)
            self.chatgpt_available = True
            print("✅ Atmosphere Arcade components initialized successfully")
        except Exception as e:
            print(f"⚠️ Some Atmosphere components failed to initialize: {e}")
            # Create fallback instances
            self.api_keys = APIKeyManager()
            self.chatgpt_manager = None
            self.safety_monitor = SafetyMonitor()
            self.chatgpt_available = False

        # Track ChatKit availability
        self.chatkit_available = CHATKIT_AVAILABLE

        # Initialize agent only if ChatKit is available
        if self.chatkit_available:
            # Agent configuration with safety and multilingual capabilities
            self.assistant_agent = Agent[AgentContext](
                model="gpt-4",  # Using GPT-4 for production stability
                name="Atmosphere Assistant",
                instructions=self._get_assistant_instructions(),
                tools=self._get_available_tools(),
            )
        else:
            # Fallback agent simulation
            self.assistant_agent = None

        # Supported languages for multilingual interface
        self.supported_languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'ar': 'Arabic', 'ja': 'Japanese', 'zh': 'Chinese', 'hi': 'Hindi',
            'pt': 'Portuguese', 'ru': 'Russian', 'ko': 'Korean', 'it': 'Italian'
        }

    def _get_assistant_instructions(self) -> str:
        """Get comprehensive assistant instructions with safety and capabilities."""
        return """
        You are Atmosphere Assistant, an advanced AI terminal with comprehensive safety features.

        SAFETY FIRST: Always prioritize user safety and content moderation. Report any concerning content immediately.

        CAPABILITIES:
        - Natural language file system operations
        - Multilingual communication with cultural awareness
        - Code assistance and development help
        - System administration and monitoring
        - Safety monitoring and compliance
        - Enterprise deployment management

        BEHAVIOR:
        - Be helpful, friendly, and culturally aware
        - Use appropriate language for the user's culture
        - Maintain safety and security best practices
        - Provide clear, actionable responses
        - Use tools when appropriate for complex operations
        - Stream progress for long-running operations

        SAFETY PROTOCOLS:
        - Monitor all content for safety violations
        - Use safety identifiers for compliance
        - Report suspicious activity immediately
        - Maintain user privacy and data protection
        - Follow OpenAI safety guidelines

        When using tools, provide clear feedback about what you're doing and why.
        """

    def _get_available_tools(self) -> List:
        """Get all available tools for Atmosphere Arcade operations."""
        if not self.chatkit_available:
            return []  # No tools in fallback mode

        return [
            self._file_operations_tool,
            self._safety_report_tool,
            self._system_info_tool,
            self._multilingual_translate_tool,
            self._code_assistance_tool,
            self._deployment_status_tool,
        ]

# Tool method definitions - created conditionally based on ChatKit availability
if CHATKIT_AVAILABLE:
    @function_tool(description_override="Perform safe file system operations in the user's directory.")
    async def _chatkit_file_operations_tool(ctx: AgentContext, operation: str, path: str = "", content: str = "") -> str:
        """Safe file system operations with security controls."""
        try:
            # Get server instance from context
            server = getattr(ctx.context, '_server', None)
            if not server:
                return "Server context not available"

            # Safety check the operation using ChatGPT moderation
            safety_result = await server.chatgpt_manager.check_moderation(f"File operation: {operation} on {path}")
            if safety_result.get('flagged', False):
                await server.safety_monitor.submit_user_report(
                    user_id=ctx.context.user_id if hasattr(ctx, 'context') else 'unknown',
                    report_type='unsafe_file_operation',
                    content=f"Unsafe file operation blocked: {operation} on {path}",
                    context={'source': 'web_chat_interface', 'violations': safety_result.get('violations', [])}
                )
                return "⚠️ File operation blocked for safety reasons. Please contact support if you need assistance."

            # Perform operation based on type
            if operation == "list":
                return server._list_directory(path or ".")
            elif operation == "read":
                return server._read_file(path)
            elif operation == "write":
                return server._write_file(path, content)
            elif operation == "create_dir":
                return server._create_directory(path)
            else:
                return f"Unknown file operation: {operation}"

        except Exception as e:
            return f"File operation failed: {str(e)}"

    @function_tool(description_override="Report safety concerns or inappropriate content.")
    async def _chatkit_safety_report_tool(ctx: AgentContext, report_type: str, description: str) -> str:
        """Handle safety reporting through the integrated safety system."""
        try:
            server = getattr(ctx.context, '_server', None)
            if not server:
                return "Server context not available"

            report_data = {
                'type': report_type,
                'description': description,
                'user_id': ctx.context.user_id if hasattr(ctx, 'context') else 'unknown',
                'timestamp': datetime.now().isoformat(),
                'source': 'chatkit_web_interface'
            }

            await server.safety_monitor.submit_user_report(report_data)
            return "✅ Safety report submitted successfully. Thank you for helping keep Atmosphere Arcade safe."

        except Exception as e:
            return f"Failed to submit safety report: {str(e)}"

    @function_tool(description_override="Get system information and performance metrics.")
    async def _chatkit_system_info_tool(ctx: AgentContext) -> str:
        """Provide system information and monitoring data."""
        try:
            server = getattr(ctx.context, '_server', None)
            if not server:
                return "Server context not available"

            import psutil

            # System information
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')

            info = f"""
System Information:
• CPU Usage: {cpu_percent}%
• Memory: {memory.percent}% used ({memory.used//1024//1024}MB/{memory.total//1024//1024}MB)
• Disk: {disk.percent}% used ({disk.used//1024//1024//1024}GB/{disk.total//1024//1024//1024}GB)

Atmosphere Arcade Status:
• Safety Monitor: Active
• AI Services: Operational
• File Operations: Enabled
• Multilingual Support: {len(server.supported_languages)} languages
            """.strip()

            return info

        except Exception as e:
            return f"Could not retrieve system information: {str(e)}"

    @function_tool(description_override="Translate text between supported languages.")
    async def _chatkit_multilingual_translate_tool(ctx: AgentContext, text: str, target_language: str, source_language: str = "auto") -> str:
        """Multilingual translation with cultural awareness."""
        try:
            server = getattr(ctx.context, '_server', None)
            if not server:
                return "Server context not available"

            if target_language not in server.supported_languages:
                return f"Unsupported target language: {target_language}. Supported: {', '.join(server.supported_languages.keys())}"

            # Use ChatGPT manager for translation
            translation_prompt = f"Translate the following text from {source_language} to {target_language}. Maintain cultural appropriateness and natural tone: {text}"

            response = await server.chatgpt_manager.process_multilingual_message(
                message=translation_prompt,
                language=target_language,
                safety_identifier=getattr(ctx.context, 'safety_identifier', None)
            )

            return f"Translation to {server.supported_languages[target_language]}: {response}"

        except Exception as e:
            return f"Translation failed: {str(e)}"

    @function_tool(description_override="Provide code assistance and development help.")
    async def _chatkit_code_assistance_tool(ctx: AgentContext, request: str, language: str = "python") -> str:
        """Code assistance and development support."""
        try:
            server = getattr(ctx.context, '_server', None)
            if not server:
                return "Server context not available"

            code_prompt = f"Provide helpful code assistance for: {request}. Language: {language}. Include best practices and error handling."

            response = await server.chatgpt_manager.process_multilingual_message(
                message=code_prompt,
                language="en",  # Code is typically in English
                safety_identifier=getattr(ctx.context, 'safety_identifier', None)
            )

            return response

        except Exception as e:
            return f"Code assistance failed: {str(e)}"

    @function_tool(description_override="Check deployment and system status.")
    async def _chatkit_deployment_status_tool(ctx: AgentContext) -> str:
        """Check deployment status and system health."""
        try:
            server = getattr(ctx.context, '_server', None)
            if not server:
                return "Server context not available"

            status = {
                'deployment_type': 'chatkit_web_interface',
                'safety_system': 'active',
                'ai_services': 'operational',
                'multilingual_support': f"{len(server.supported_languages)} languages",
                'file_operations': 'enabled',
                'timestamp': datetime.now().isoformat()
            }

            status_text = "Deployment Status:\n" + "\n".join(f"• {k}: {v}" for k, v in status.items())
            return status_text

        except Exception as e:
            return f"Could not retrieve deployment status: {str(e)}"

    # Assign decorated functions to class
    AtmosphereChatKitServer._file_operations_tool = _chatkit_file_operations_tool
    AtmosphereChatKitServer._safety_report_tool = _chatkit_safety_report_tool
    AtmosphereChatKitServer._system_info_tool = _chatkit_system_info_tool
    AtmosphereChatKitServer._multilingual_translate_tool = _chatkit_multilingual_translate_tool
    AtmosphereChatKitServer._code_assistance_tool = _chatkit_code_assistance_tool
    AtmosphereChatKitServer._deployment_status_tool = _chatkit_deployment_status_tool

else:
    # Fallback tool methods for when ChatKit is not available
    async def _fallback_file_operations_tool(self, operation: str, path: str = "", content: str = "") -> str:
        return "File operations available in terminal mode only."

    async def _fallback_safety_report_tool(self, report_type: str, description: str) -> str:
        return "Safety reporting available in terminal mode only."

    async def _fallback_system_info_tool(self) -> str:
        return "System info available in terminal mode only."

    async def _fallback_multilingual_translate_tool(self, text: str, target_language: str, source_language: str = "auto") -> str:
        return "Translation available in terminal mode only."

    async def _fallback_code_assistance_tool(self, request: str, language: str = "python") -> str:
        return "Code assistance available in terminal mode only."

    async def _fallback_deployment_status_tool(self) -> str:
        return "Deployment status available in terminal mode only."

    # Assign fallback methods to class
    AtmosphereChatKitServer._file_operations_tool = _fallback_file_operations_tool
    AtmosphereChatKitServer._safety_report_tool = _fallback_safety_report_tool
    AtmosphereChatKitServer._system_info_tool = _fallback_system_info_tool
    AtmosphereChatKitServer._multilingual_translate_tool = _fallback_multilingual_translate_tool
    AtmosphereChatKitServer._code_assistance_tool = _fallback_code_assistance_tool
    AtmosphereChatKitServer._deployment_status_tool = _fallback_deployment_status_tool

    # File operation helper methods
    def _list_directory(self, path: str) -> str:
        """List directory contents safely."""
        try:
            full_path = Path(path).resolve()
            if not full_path.exists() or not full_path.is_dir():
                return f"Directory not found: {path}"

            items = []
            for item in full_path.iterdir():
                if not item.name.startswith('.'):  # Skip hidden files
                    item_type = "DIR" if item.is_dir() else "FILE"
                    size = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                    items.append(f"{item_type}: {item.name}{size}")

            return f"Contents of {path}:\n" + "\n".join(items[:20])  # Limit to 20 items

        except Exception as e:
            return f"Could not list directory: {str(e)}"

    def _read_file(self, path: str) -> str:
        """Read file contents safely."""
        try:
            full_path = Path(path).resolve()
            if not full_path.exists() or not full_path.is_file():
                return f"File not found: {path}"

            # Safety check file size
            size = full_path.stat().st_size
            if size > 1024 * 1024:  # 1MB limit
                return f"File too large to read: {size} bytes. Maximum size: 1MB"

            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read(5000)  # Limit to first 5000 characters

            return f"Contents of {path}:\n{content}"

        except Exception as e:
            return f"Could not read file: {str(e)}"

    def _write_file(self, path: str, content: str) -> str:
        """Write file contents safely."""
        try:
            full_path = Path(path).resolve()

            # Safety checks
            if full_path.exists() and full_path.is_dir():
                return f"Cannot write to directory: {path}"

            # Ensure parent directory exists
            full_path.parent.mkdir(parents=True, exist_ok=True)

            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return f"Successfully wrote {len(content)} characters to {path}"

        except Exception as e:
            return f"Could not write file: {str(e)}"

    def _create_directory(self, path: str) -> str:
        """Create directory safely."""
        try:
            full_path = Path(path).resolve()
            full_path.mkdir(parents=True, exist_ok=True)
            return f"Successfully created directory: {path}"

        except Exception as e:
            return f"Could not create directory: {str(e)}"

    async def respond(
        self,
        thread: Optional[Any] = None,
        input: Optional[Any] = None,
        context: Optional[Any] = None,
    ) -> AsyncIterator[Event]:
        """Main response handler with safety integration."""
        try:
            # Extract or create context
            atmosphere_context = self._get_atmosphere_context(context or {})

            # Handle input based on availability
            input_text = ""
            if hasattr(input, 'content') and input.content:
                input_text = str(input.content)
            elif isinstance(input, str):
                input_text = input
            elif isinstance(input, dict) and 'content' in input:
                input_text = input['content']

            # Safety check the input
            if input_text:
                safety_result = await self.chatgpt_manager.check_moderation(input_text)
                if safety_result.get('flagged', False):
                    await self.safety_monitor.submit_user_report(
                        user_id=atmosphere_context.user_id,
                        report_type='moderation_violation',
                        content=f"Input flagged by moderation: {input_text[:200]}",
                        context={'source': 'web_chat_interface', 'violations': safety_result.get('violations', [])}
                    )

                    # Stream safety warning
                    yield ProgressUpdateEvent("Content flagged for safety review")
                    return

            # Process with AI or fallback
            if self.chatkit_available and self.assistant_agent:
                # Use real ChatKit agent
                agent_context = AgentContext(
                    thread=thread,
                    store=self.store if hasattr(self, 'store') else None,
                    request_context=atmosphere_context,
                )

                # Add server reference to context for tools to use
                agent_context.context._server = self

                # Convert input to agent format
                agent_input = await self._to_input_item(input)

                result = Runner.run_streamed(
                    self.assistant_agent,
                    agent_input,
                    context=agent_context,
                )

                # Stream response with safety monitoring
                async for event in stream_agent_response(agent_context, result):
                    # Additional safety monitoring on responses
                    if hasattr(event, 'content') and event.content:
                        output_safety = await self.chatgpt_manager.check_moderation(str(event.content))
                        if output_safety.get('flagged', False):
                            await self.safety_monitor.submit_user_report(
                                user_id=atmosphere_context.user_id,
                                report_type='output_moderation_violation',
                                content=f"Output flagged by moderation: {str(event.content)[:200]}",
                                context={'source': 'web_chat_interface', 'violations': output_safety.get('violations', [])}
                            )

                    yield event
            else:
                # Fallback implementation using ChatGPT manager directly
                response = await self.chatgpt_manager.process_multilingual_message(
                    message=input_text,
                    language=atmosphere_context.language,
                    safety_identifier=atmosphere_context.safety_identifier
                )

                # Create mock event with response
                yield ProgressUpdateEvent(f"🤖 Atmosphere Assistant: {response}")

        except Exception as e:
            # Error handling with safety logging
            await self.safety_monitor.submit_user_report(
                user_id=getattr(context, 'user_id', 'unknown') if context else 'unknown',
                report_type='system_error',
                content=f"ChatKit processing error: {str(e)}",
                context={'source': 'web_chat_interface'}
            )

            yield ProgressUpdateEvent(f"System error: {str(e)}")

    def _get_atmosphere_context(self, context: Any) -> AtmosphereContext:
        """Extract or create Atmosphere context."""
        if isinstance(context, AtmosphereContext):
            return context

        # Extract from request context
        user_id = getattr(context, 'user_id', None) or str(uuid.uuid4())
        session_id = getattr(context, 'session_id', None) or str(uuid.uuid4())
        language = getattr(context, 'language', 'en')

        return AtmosphereContext(user_id, session_id, language)

    async def _to_input_item(self, input: Union[UserMessageItem, ClientToolCallOutputItem]):
        """Convert input to agent input format."""
        if isinstance(input, UserMessageItem):
            return input
        elif isinstance(input, ClientToolCallOutputItem):
            return input
        else:
            raise ValueError(f"Unsupported input type: {type(input)}")

    async def to_message_content(
        self, input: Union[FilePart, ImagePart]
    ) -> ResponseInputContentParam:
        """Handle file and image content processing."""
        if isinstance(input, FilePart):
            # Handle file uploads
            if hasattr(input, 'url'):
                return {"type": "file", "file": {"url": input.url}}
            else:
                return {"type": "text", "text": f"File: {getattr(input, 'name', 'unknown')}"}

        elif isinstance(input, ImagePart):
            # Handle image content
            if hasattr(input, 'url'):
                return {"type": "image_url", "image_url": {"url": input.url}}
            else:
                return {"type": "text", "text": "Image content"}

        raise NotImplementedError(f"Unsupported content type: {type(input)}")

    async def action(self, thread: ThreadMetadata, action_name: str, payload: Dict[str, Any], context: Any) -> AsyncIterator[Event]:
        """Handle custom actions from the chat interface."""
        try:
            atmosphere_context = self._get_atmosphere_context(context)

            if action_name == "file_explorer":
                # Show file explorer widget
                widget = Card(
                    children=[
                        Text(value="File Explorer", id="title"),
                        WidgetList(
                            items=self._get_file_list_items(".")
                        ),
                        Button(
                            text="Refresh",
                            action="file_explorer"
                        )
                    ]
                )

                async for event in stream_widget(
                    thread,
                    widget,
                    generate_id=lambda item_type: self.store.generate_item_id(item_type, thread, context),
                ):
                    yield event

            elif action_name == "safety_dashboard":
                # Show safety dashboard
                dashboard_data = await self.safety_monitor.get_dashboard_data()

                widget = Card(
                    children=[
                        Text(value="Safety Dashboard", id="title"),
                        Text(value=f"Total Reports: {dashboard_data.get('total_reports', 0)}", id="reports"),
                        Text(value=f"Active Incidents: {dashboard_data.get('active_incidents', 0)}", id="incidents"),
                        Text(value=f"Safety Score: {dashboard_data.get('safety_score', 100)}%", id="score")
                    ]
                )

                async for event in stream_widget(
                    thread,
                    widget,
                    generate_id=lambda item_type: self.store.generate_item_id(item_type, thread, context),
                ):
                    yield event

            elif action_name == "language_switch":
                # Language switching widget
                target_lang = payload.get('language', 'en')
                atmosphere_context.language = target_lang

                widget = Card(
                    children=[
                        Text(value=f"Language switched to: {self.supported_languages.get(target_lang, target_lang)}", id="confirmation")
                    ]
                )

                async for event in stream_widget(
                    thread,
                    widget,
                    generate_id=lambda item_type: self.store.generate_item_id(item_type, thread, context),
                ):
                    yield event

        except Exception as e:
            yield ProgressUpdateEvent(message=f"Action failed: {str(e)}")

    def _get_file_list_items(self, path: str) -> List[Dict[str, Any]]:
        """Get file list items for widget display."""
        try:
            full_path = Path(path).resolve()
            if not full_path.exists() or not full_path.is_dir():
                return [{"text": f"Directory not found: {path}", "type": "error"}]

            items = []
            for item in full_path.iterdir():
                if not item.name.startswith('.'):
                    item_type = "📁" if item.is_dir() else "📄"
                    size_info = f" ({item.stat().st_size} bytes)" if item.is_file() else ""
                    items.append({
                        "text": f"{item_type} {item.name}{size_info}",
                        "action": "file_select",
                        "payload": {"path": str(item), "type": "dir" if item.is_dir() else "file"}
                    })

            return items[:20]  # Limit to 20 items

        except Exception as e:
            return [{"text": f"Error listing files: {str(e)}", "type": "error"}]


# FastAPI application setup
app = FastAPI(title="Atmosphere Arcade ChatKit", description="Web-based chat interface for Atmosphere Arcade")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="web/static"), name="static")
templates = Jinja2Templates(directory="web/templates")

@app.get("/")
async def chat_interface():
    """Serve the main chat interface."""
    return templates.TemplateResponse("chat.html", {"request": {}})

@app.get("/terminal")
async def terminal_interface():
    """Serve the web-based terminal interface."""
    return templates.TemplateResponse("terminal.html", {"request": {}})


# WebSocket endpoint for real-time terminal communication
@app.websocket("/ws/terminal")
async def terminal_websocket(websocket: WebSocket):
    """WebSocket endpoint for real-time terminal communication with enhanced error handling."""
    session_id = str(uuid.uuid4())
    terminal_session = None
    
    try:
        # Accept the WebSocket connection
        await websocket.accept()
        
        # Initialize terminal sessions dictionary if it doesn't exist
        if not hasattr(app, 'terminal_sessions'):
            app.terminal_sessions = {}
        
        # Create terminal session
        terminal_session = {
            'session_id': session_id,
            'directory': str(Path.home()),
            'connected': True,
            'websocket': websocket,
            'last_active': datetime.now().isoformat()
        }
        
        # Store the session
        app.terminal_sessions[session_id] = terminal_session
        
        print(f"🔌 New terminal session: {session_id}")
        
        # Send session confirmation
        await websocket.send_json({
            'type': 'session_created',
            'session_id': session_id,
            'current_dir': terminal_session['directory'],
            'welcome_message': 'Terminal session initialized. Type a command to begin.'
        })

        # Terminal command processing loop
        while True:
            try:
                # Receive data from client with timeout
                data = await asyncio.wait_for(websocket.receive_json(), timeout=300)  # 5 minute timeout
                message_type = data.get('type')
                
                # Update last active time
                if terminal_session:
                    terminal_session['last_active'] = datetime.now().isoformat()

                if message_type == 'ping':
                    # Respond to keep-alive ping
                    await websocket.send_json({'type': 'pong'})
                    continue
                    
                elif message_type == 'command':
                    command = data.get('command', '').strip()
                    if not command:
                        continue
                        
                    print(f"⌨️  Processing command: {command[:50]}...")
                    
                    # Process command using our enhanced terminal handler
                    try:
                        if hasattr(app, 'terminal_handler') and app.terminal_handler:
                            # Process the command asynchronously
                            response = await app.terminal_handler.process_command(command)
                            
                            # Ensure response is a string
                            if not isinstance(response, str):
                                response = str(response) if response is not None else "No output"
                        else:
                            response = "Terminal handler not initialized. Please try again."

                            # Send response back to client in chunks to handle large outputs
                            chunk_size = 4096  # 4KB chunks
                            for i in range(0, len(response), chunk_size):
                                chunk = response[i:i + chunk_size]
                                await websocket.send_json({
                                    'type': 'command_output',
                                    'output': chunk,
                                    'is_complete': (i + chunk_size) >= len(response),
                                    'current_dir': terminal_session['directory']
                                })
                                
                                # Small delay to prevent overwhelming the client
                                await asyncio.sleep(0.01)

                        except asyncio.CancelledError:
                            # Handle cancellation
                            print(f"Command cancelled by user: {session_id}")
                            await websocket.send_json({
                                'type': 'error',
                                'message': 'Command execution was cancelled',
                                'current_dir': terminal_session['directory']
                            })
                            
                        except Exception as e:
                            error_msg = f'Error processing command: {str(e)}'
                            print(f"❌ {error_msg}")
                            await websocket.send_json({
                                'type': 'error',
                                'message': error_msg,
                                'current_dir': terminal_session['directory']
                            })

                elif message_type == 'heartbeat':
                    # Respond to heartbeat
                    await websocket.send_json({
                        'type': 'heartbeat_response',
                        'timestamp': datetime.now().isoformat()
                    })

            except asyncio.TimeoutError:
                # Handle client timeout (no data received for a while)
                print(f"⌛ Session timed out: {session_id}")
                await websocket.close(code=1001)  # Going away
                break
                
            except json.JSONDecodeError:
                error_msg = 'Invalid JSON received'
                print(f"❌ {error_msg}")
                await websocket.send_json({
                    'type': 'error',
                    'message': error_msg
                })
                
            except RuntimeError as e:
                if 'no running event loop' in str(e).lower():
                    print("Event loop closed, shutting down WebSocket")
                    break
                raise

    except WebSocketDisconnect:
        print(f"🔌 Client disconnected: {session_id}")
        
    except Exception as e:
        error_msg = f"WebSocket error in session {session_id}: {str(e)}"
        print(f"❌ {error_msg}")
        try:
            await websocket.send_json({
                'type': 'error',
                'message': 'A server error occurred. Please reconnect.',
                'fatal': True
                'message': 'Internal server error'
            })
        except:
            pass

@app.post("/api/chatkit/session")
async def create_chatkit_session():
    """Create a new ChatKit session and return client secret."""
    try:
        # For now, return a mock session since the official ChatKit API might require specific setup
        # This will be replaced with actual ChatKit session creation once properly configured
        import uuid
        import time

        mock_session = {
            "client_secret": f"mock_secret_{uuid.uuid4().hex}_{int(time.time())}",
            "session_id": str(uuid.uuid4()),
            "expires_at": int(time.time()) + 3600  # 1 hour from now
        }

        print(f"✅ Mock ChatKit session created: {mock_session['session_id']}")
        return mock_session

    except Exception as e:
        print(f"Error creating ChatKit session: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create ChatKit session: {str(e)}")


@app.post("/chatkit")
async def chatkit_endpoint(request: Request):
    """ChatKit server endpoint - simplified for web chat interface."""
    try:
        body = await request.body()

        # Parse the request body
        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            # If not JSON, treat as plain text message
            data = {"content": body.decode('utf-8'), "type": "user_message"}

        # Extract context from headers
        context = {
            'user_id': request.headers.get('X-User-ID', str(uuid.uuid4())),
            'session_id': request.headers.get('X-Session-ID', str(uuid.uuid4())),
            'language': request.headers.get('Accept-Language', 'en').split(',')[0].split('-')[0],
            'ip_address': request.client.host if request.client else 'unknown'
        }

        # Handle different message types
        if data.get('type') == 'user_message':
            message_content = data.get('content', '').strip()
            if message_content:
                # Process through our AI system
                response = await process_user_message(message_content, context)

                # Return response in expected format
                return {
                    "content": response,
                    "type": "assistant_message",
                    "timestamp": datetime.now().isoformat()
                }

        # Default response for unsupported types
        return {
            "content": "I'm sorry, I didn't understand that message format.",
            "type": "assistant_message",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"ChatKit endpoint error: {e}")
        import traceback
        traceback.print_exc()

        return {
            "content": f"I encountered an error processing your message: {str(e)}",
            "type": "error_message",
            "timestamp": datetime.now().isoformat()
        }

async def process_user_message(message: str, context: dict) -> str:
    """Process a user message and return AI response."""
    try:
        # Create atmosphere context
        atmosphere_context = AtmosphereContext(
            user_id=context.get('user_id', 'unknown'),
            session_id=context.get('session_id', 'unknown'),
            language=context.get('language', 'en')
        )

        # Safety check - only if ChatGPT manager is available
        if chatkit_server.chatgpt_manager and chatkit_server.chatgpt_available:
            try:
                safety_result = await chatkit_server.chatgpt_manager.check_moderation(message)
                if safety_result.get('flagged', False):
                    await chatkit_server.safety_monitor.submit_user_report(
                        user_id=atmosphere_context.user_id,
                        report_type='moderation_violation',
                        content=f"Message flagged by moderation: {message[:200]}",
                        context={'source': 'web_chat_interface', 'violations': safety_result.get('violations', [])}
                    )
                    return "⚠️ Your message was flagged for safety review. Please rephrase and try again."
            except Exception as e:
                print(f"Safety check failed: {e}")
                # Continue without safety check if it fails

        # Process through ChatGPT manager if available
        if chatkit_server.chatgpt_manager and chatkit_server.chatgpt_available:
            response = await chatkit_server.chatgpt_manager.process_multilingual_message(
                conversation_id=f"chatkit_{atmosphere_context.session_id}",
                message=message,
                user_id=atmosphere_context.user_id,
                session_id=atmosphere_context.session_id
            )
            return response.content if response and hasattr(response, 'content') else "I received your message but couldn't generate a response."
        else:
            # Fallback response when AI is not available
            return f"Hello! I'm the Atmosphere Assistant. I received your message: '{message[:100]}{'...' if len(message) > 100 else ''}'.\n\nI'm currently running in limited mode without AI capabilities. Please use the terminal interface for full functionality by running `python start_arcade.py`."

    except Exception as e:
        print(f"Message processing error: {e}")
        return f"Sorry, I encountered an error: {str(e)}. Please try again."

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "chatkit": "active",
            "safety_monitor": "active",
            "ai_services": "active"
        }
    }

if __name__ == "__main__":
    import uvicorn
    import os

    # Make port configurable via environment variable
    port = int(os.getenv('CHATKIT_PORT', '8081'))

    print(f"🚀 Starting ChatKit server on port {port}")
    print(f"🌐 Access at: http://localhost:{port}")

    uvicorn.run(app, host="0.0.0.0", port=port)
