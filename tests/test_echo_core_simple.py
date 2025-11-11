"""
Tests for atmosphere_audio.echo.core.core module.

This module tests the EchoesAssistantV2 main functionality.
"""

import os
import pytest
from unittest.mock import MagicMock, patch

from atmosphere_audio.echo.core.core import EchoesAssistantV2


class TestEchoesAssistantV2:
    """Tests for EchoesAssistantV2 class."""

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_initialization_basic(self, mock_openai_class):
        """Test basic EchoesAssistantV2 initialization."""
        # Mock OpenAI client
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        assistant = EchoesAssistantV2()

        # Verify basic attributes are set
        assert assistant.api_key == "test-key"
        assert assistant.client == mock_client
        assert assistant.model == "gpt-4"  # From our fallback constants
        assert assistant.session_id is not None

        # Verify subsystems are initialized (they should be mock objects)
        assert hasattr(assistant, 'context_manager')
        assert hasattr(assistant, 'knowledge_manager')
        assert hasattr(assistant, 'fs_tools')
        assert hasattr(assistant, 'agent_workflow')

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    def test_initialization_missing_api_key(self):
        """Test initialization fails without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(RuntimeError, match="OPENAI_API_KEY environment variable is missing"):
                EchoesAssistantV2()

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_custom_session_id(self, mock_openai_class):
        """Test custom session ID initialization."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        assistant = EchoesAssistantV2(session_id="custom-session-123")

        assert assistant.session_id == "custom-session-123"

    def test_chat_to_responses_conversion(self):
        """Test conversion from chat messages to responses format."""
        messages = [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there"}
        ]

        result = EchoesAssistantV2._chat_to_responses(messages)

        assert len(result) == 3

        # System message becomes developer
        assert result[0]["role"] == "developer"
        assert result[0]["type"] == "message"
        assert result[0]["content"] == "You are a helpful assistant"

        # User message stays user
        assert result[1]["role"] == "user"
        assert result[1]["type"] == "message"
        assert result[1]["content"] == "Hello"

        # Assistant message gets content array
        assert result[2]["role"] == "assistant"
        assert result[2]["type"] == "message"
        assert result[2]["content"][0]["type"] == "output_text"
        assert result[2]["content"][0]["text"] == "Hi there"

    def test_responses_to_chat_conversion(self):
        """Test conversion from responses format back to chat messages."""
        # Mock response items
        mock_item = MagicMock()
        mock_output_item = MagicMock()
        mock_output_item.type = "message"
        mock_content_item = MagicMock()
        mock_content_item.type = "output_text"
        mock_content_item.text = "Hello world"
        mock_output_item.content = [mock_content_item]
        mock_item.output = [mock_output_item]

        result = EchoesAssistantV2._responses_to_chat([mock_item])

        assert len(result) == 1
        assert result[0]["role"] == "assistant"
        assert result[0]["content"] == "Hello world"

    def test_sanitize_tool_schemas(self):
        """Test tool schema sanitization."""
        raw_tools = [
            {
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "arg1": {"type": "string"}
                        }
                    }
                }
            }
        ]

        result = EchoesAssistantV2._sanitize_tool_schemas(raw_tools)

        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["function"]["name"] == "test_tool"
        assert result[0]["function"]["description"] == "A test tool"
        assert "parameters" in result[0]["function"]

    def test_tools_to_responses_format(self):
        """Test conversion of tools to responses format."""
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {"type": "object", "properties": {}},
                    "strict": True
                }
            }
        ]

        result = EchoesAssistantV2._tools_to_responses_format(tools)

        assert len(result) == 1
        assert result[0]["type"] == "function"
        assert result[0]["name"] == "test_tool"
        assert result[0]["description"] == "A test tool"
        assert result[0]["strict"] is True

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_rag_context_retrieval_disabled(self, mock_openai_class):
        """Test RAG context retrieval when disabled."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        assistant = EchoesAssistantV2(enable_rag=False)

        result = assistant._retrieve_rag_context("test query")
        assert result == []

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_rag_context_retrieval_with_results(self, mock_openai_class):
        """Test RAG context retrieval with mock results."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock RAG system
        mock_rag = MagicMock()
        mock_rag.search.return_value = {"results": [{"text": "test content"}]}

        assistant = EchoesAssistantV2(enable_rag=True)
        assistant.rag = mock_rag

        result = assistant._retrieve_rag_context("test query")
        assert result == [{"text": "test content"}]
        mock_rag.search.assert_called_once_with("test query", top_k=3)

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'})
    @patch('openai.OpenAI')
    def test_rag_context_retrieval_error(self, mock_openai_class):
        """Test RAG context retrieval with error handling."""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # Mock RAG system that raises exception
        mock_rag = MagicMock()
        mock_rag.search.side_effect = Exception("RAG error")

        assistant = EchoesAssistantV2(enable_rag=True)
        assistant.rag = mock_rag

        result = assistant._retrieve_rag_context("test query")
        assert result == []  # Should return empty list on error
