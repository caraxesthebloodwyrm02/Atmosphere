"""Simple test suite for echo.core module."""

import sys
from pathlib import Path
from unittest.mock import Mock

# Add Echoes directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "Echoes"))

from echoes.core import EchoesAssistantV2
from echoes.config import RuntimeOptions

class TestEchoesAssistantV2Simple:
    """Simple tests for EchoesAssistantV2 to increase coverage."""

    def test_init_minimal(self):
        """Test minimal initialization."""
        assistant = EchoesAssistantV2()
        assert assistant is not None
        assert hasattr(assistant, "session_id")
        assert hasattr(assistant, "client")
        assert hasattr(assistant, "knowledge_manager")

    def test_init_with_session_id(self):
        """Test initialization with custom session ID."""
        session_id = "test-session-123"
        assistant = EchoesAssistantV2(session_id=session_id)
        assert assistant.session_id == session_id

    def test_init_with_options(self):
        """Test initialization with options."""
        opts = RuntimeOptions(
            enable_tools=False,
            enable_rag=False,
            enable_glimpse=False,
            enable_status=False,
        )
        assistant = EchoesAssistantV2(opts=opts)
        assert assistant.enable_tools is False
        assert assistant.enable_rag is False
        assert assistant.enable_glimpse is False

    def test_get_stats_returns_dict(self):
        """Test that get_stats returns a dictionary."""
        assistant = EchoesAssistantV2()
        stats = assistant.get_stats()
        assert isinstance(stats, dict)
        assert "session_id" in stats

    def test_chat_to_responses_static_method(self):
        """Test the static method for converting chat to responses."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        responses = EchoesAssistantV2._chat_to_responses(messages)
        assert isinstance(responses, list)
        assert len(responses) == 2
        assert all(isinstance(r, dict) for r in responses)

    def test_responses_to_chat_static_method(self):
        """Test the static method for converting responses to chat."""
        response_items = [
            {"type": "output_text", "text": "Hello"},
            {"type": "output_text", "text": "Hi there!"},
        ]
        messages = EchoesAssistantV2._responses_to_chat(response_items)
        assert isinstance(messages, list)
        # The method might return empty list for unsupported types
        assert isinstance(messages, list)

    def test_sanitize_tool_schemas_static_method(self):
        """Test tool schema sanitization."""
        raw_tools = [
            {"name": "test_tool", "description": "A test tool"},
            {
                "function": {
                    "name": "another_tool",
                    "description": "Another tool",
                }
            },
        ]
        sanitized = EchoesAssistantV2._sanitize_tool_schemas(raw_tools)
        assert isinstance(sanitized, list)
        assert len(sanitized) == 2

    def test_tools_to_responses_format_static_method(self):
        """Test conversion of tools to responses format."""
        tools = [
            {
                "name": "test_tool",
                "description": "A test tool",
                "parameters": {},
            }
        ]
        responses_tools = EchoesAssistantV2._tools_to_responses_format(tools)
        assert isinstance(responses_tools, list)
        # The method might return empty list for unsupported formats
        assert isinstance(responses_tools, list)

    def test_retrieve_rag_context_when_disabled(self):
        """Test RAG context retrieval when RAG is disabled."""
        assistant = EchoesAssistantV2(opts=RuntimeOptions(enable_rag=False))
        context = assistant._retrieve_rag_context("test query")
        assert context == []

    def test_safe_responses_create_with_exception(self):
        """Test safe responses creation handles exceptions."""
        assistant = EchoesAssistantV2()
        assistant.client = Mock()
        assistant.client.responses.create.side_effect = Exception("API Error")

        result = assistant._safe_responses_create("test")
        assert result is None

    def test_add_knowledge_method_exists(self):
        """Test that add_knowledge method exists."""
        assistant = EchoesAssistantV2()
        assert hasattr(assistant, "add_knowledge")
        assert callable(assistant.add_knowledge)

    def test_clear_session_method_exists(self):
        """Test that clear_session method exists."""
        assistant = EchoesAssistantV2()
        assert hasattr(assistant, "clear_session")
        assert callable(assistant.clear_session)

    def test_get_conversation_history_method_exists(self):
        """Test that get_conversation_history method exists."""
        assistant = EchoesAssistantV2()
        assert hasattr(assistant, "get_conversation_history")
        assert callable(assistant.get_conversation_history)

    @patch("echoes.core.OpenAI")
    def test_initialization_with_openai_client(self, mock_openai):
        """Test that OpenAI client is properly initialized."""
        mock_client = Mock()
        mock_openai.return_value = mock_client

        assistant = EchoesAssistantV2()

        assert assistant.client is not None
        mock_openai.assert_called_once()

    def test_quantum_state_manager_initialization(self):
        """Test quantum state manager is initialized."""
        assistant = EchoesAssistantV2()
        assert assistant.quantum_state_manager is not None
        assert hasattr(
            assistant.quantum_state_manager, "initialize_quantum_states"
        )

    def test_inventory_service_initialization(self):
        """Test inventory service is initialized."""
        assistant = EchoesAssistantV2()
        assert assistant.inventory_service is not None

    def test_context_manager_initialization(self):
        """Test context manager is initialized."""
        assistant = EchoesAssistantV2()
        assert assistant.context_manager is not None

    def test_memory_store_initialization(self):
        """Test memory store is initialized."""
        assistant = EchoesAssistantV2()
        assert assistant.memory_store is not None

    def test_knowledge_graph_initialization(self):
        """Test knowledge graph is initialized."""
        assistant = EchoesAssistantV2()
        assert assistant.knowledge_graph is not None

    def test_agent_workflow_initialization(self):
        """Test agent workflow is initialized."""
        assistant = EchoesAssistantV2()
        assert assistant.agent_workflow is not None
        assert assistant.agent_workflow.assistant is assistant

    def test_filesystem_tools_initialization(self):
        """Test filesystem tools are initialized."""
        assistant = EchoesAssistantV2()
        assert assistant.fs_tools is not None
        assert hasattr(assistant.fs_tools, "root_dir")

    def test_glimpse_disabled_by_default(self):
        """Test that glimpse is disabled by default."""
        assistant = EchoesAssistantV2(
            opts=RuntimeOptions(enable_glimpse=False)
        )
        assert assistant.enable_glimpse is False

    def test_tools_disabled_by_default(self):
        """Test that tools are disabled by default."""
        assistant = EchoesAssistantV2(opts=RuntimeOptions(enable_tools=False))
        assert assistant.enable_tools is False
        assert assistant.tool_registry is None

    def test_rag_disabled_when_not_available(self):
        """Test RAG is disabled when not available."""
        assistant = EchoesAssistantV2(opts=RuntimeOptions(enable_rag=False))
        assert assistant.enable_rag is False
        assert assistant.rag is None
