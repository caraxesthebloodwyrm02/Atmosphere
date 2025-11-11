# Comprehensive Test Suite for Atmosphere Arcade
# =============================================

import pytest
import asyncio
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import sys

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.chatgpt_manager import ChatGPTManager
from api.enhanced_server_test import EnhancedTerminalHandler
from start_arcade import ArcadeQuickStart


class TestChatGPTManager:
    """Test cases for ChatGPT Manager multilingual functionality."""

    @pytest.fixture
    def mock_openai(self):
        """Mock OpenAI client for testing."""
        with patch('openai.OpenAI') as mock_client:
            mock_instance = Mock()
            mock_client.return_value = mock_instance

            # Mock the chat completions
            mock_completion = Mock()
            mock_completion.choices = [Mock()]
            mock_completion.choices[0].message.content = "Hello! How can I help you today?"
            mock_instance.chat.completions.create = AsyncMock(return_value=mock_completion)

            yield mock_instance

    @pytest.fixture
    def chatgpt_manager(self, mock_openai):
        """Create ChatGPT manager instance with mocked OpenAI."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            manager = ChatGPTManager()
            return manager

    @pytest.mark.asyncio
    async def test_initialization(self, chatgpt_manager):
        """Test ChatGPT manager initializes correctly."""
        assert chatgpt_manager.api_key == 'test_key'
        assert chatgpt_manager.conversation_history == {}

    @pytest.mark.asyncio
    async def test_process_multilingual_message(self, chatgpt_manager):
        """Test multilingual message processing."""
        conversation_id = "test_conversation"
        message = "Hello, how are you?"

        result = await chatgpt_manager.process_multilingual_message(conversation_id, message)

        assert result is not None
        assert "content" in result
        assert conversation_id in chatgpt_manager.conversation_history

    @pytest.mark.asyncio
    async def test_translate_text(self, chatgpt_manager):
        """Test text translation functionality."""
        text = "Hello world"
        target_lang = "es"

        with patch.object(chatgpt_manager, 'process_multilingual_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {"content": "Hola mundo"}

            result = await chatgpt_manager.translate_text(text, target_lang)

            assert result == "Hola mundo"
            mock_process.assert_called_once()

    @pytest.mark.asyncio
    async def test_detect_language(self, chatgpt_manager):
        """Test language detection."""
        text = "Bonjour le monde"

        with patch.object(chatgpt_manager, 'process_multilingual_message', new_callable=AsyncMock) as mock_process:
            mock_process.return_value = {"detected_language": "fr"}

            result = await chatgpt_manager.detect_language(text)

            assert result == "fr"
            mock_process.assert_called_once()

    def test_get_supported_languages(self, chatgpt_manager):
        """Test supported languages retrieval."""
        languages = chatgpt_manager.get_supported_languages()

        assert isinstance(languages, list)
        assert len(languages) > 0
        # Should include common languages
        assert any(lang['code'] == 'en' for lang in languages)

    def test_clear_conversation_history(self, chatgpt_manager):
        """Test conversation history clearing."""
        conversation_id = "test_conversation"
        chatgpt_manager.conversation_history[conversation_id] = [{"role": "user", "content": "test"}]

        chatgpt_manager.clear_conversation_history(conversation_id)

        assert conversation_id not in chatgpt_manager.conversation_history

    def test_get_conversation_stats(self, chatgpt_manager):
        """Test conversation statistics retrieval."""
        conversation_id = "test_conversation"
        chatgpt_manager.conversation_history[conversation_id] = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"}
        ]

        stats = chatgpt_manager.get_conversation_stats()

        assert "total_conversations" in stats
        assert "total_messages" in stats
        assert stats["total_conversations"] >= 1


class TestEnhancedTerminalHandler:
    """Test cases for Enhanced Terminal Handler."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for file operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def terminal_handler(self, temp_dir):
        """Create terminal handler with mocked AI assistant."""
        with patch('api.enhanced_server_test.AIAssistant') as mock_ai:
            mock_ai_instance = Mock()
            mock_ai_instance.generate_response = AsyncMock(return_value="Test response")
            mock_ai.return_value = mock_ai_instance

            handler = EnhancedTerminalHandler()
            handler.current_directory = temp_dir
            yield handler

    @pytest.mark.asyncio
    async def test_process_command_natural_language(self, terminal_handler):
        """Test natural language command processing."""
        command = "What can you do?"

        result = await terminal_handler.process_command(command)

        assert "Test response" in result

    @pytest.mark.asyncio
    async def test_file_operations_list(self, terminal_handler, temp_dir):
        """Test file listing operations."""
        # Create test files
        (temp_dir / "test1.txt").write_text("test content")
        (temp_dir / "test2.py").write_text("print('hello')")

        command = "show me the files"
        result = await terminal_handler.process_command(command)

        assert "test1.txt" in result
        assert "test2.py" in result

    @pytest.mark.asyncio
    async def test_file_operations_read(self, terminal_handler, temp_dir):
        """Test file reading operations."""
        test_file = temp_dir / "test.txt"
        test_content = "This is test content"
        test_file.write_text(test_content)

        command = f"read {test_file.name}"
        result = await terminal_handler.process_command(command)

        assert test_content in result

    @pytest.mark.asyncio
    async def test_file_operations_create(self, terminal_handler, temp_dir):
        """Test file creation operations."""
        command = "create a file called new_test.txt with content 'Hello World'"
        result = await terminal_handler.process_command(command)

        new_file = temp_dir / "new_test.txt"
        assert new_file.exists()
        assert new_file.read_text() == "Hello World"

    @pytest.mark.asyncio
    async def test_directory_navigation(self, terminal_handler, temp_dir):
        """Test directory navigation."""
        # Create subdirectory
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        command = f"go to {subdir.name}"
        result = await terminal_handler.process_command(command)

        assert str(subdir) in result
        assert terminal_handler.current_directory == subdir

    @pytest.mark.asyncio
    async def test_multilingual_commands(self, terminal_handler):
        """Test multilingual command processing."""
        test_cases = [
            ("¿Qué puedes hacer?", "Spanish question"),
            ("Qu'est-ce que tu peux faire?", "French question"),
            ("क्या आप क्या कर सकते हैं?", "Hindi question"),
            ("Was können Sie tun?", "German question"),
        ]

        for command, description in test_cases:
            result = await terminal_handler.process_command(command)
            assert isinstance(result, str), f"Failed for {description}"


class TestArcadeQuickStart:
    """Test cases for Arcade Quick Start functionality."""

    @pytest.fixture
    def quickstart(self):
        """Create ArcadeQuickStart instance."""
        return ArcadeQuickStart()

    def test_initialization(self, quickstart):
        """Test quickstart initialization."""
        assert quickstart.project_root.exists()
        assert quickstart.config_dir.name == "config"
        assert quickstart.logs_dir.name == "logs"

    def test_check_environment_no_api_key(self, quickstart):
        """Test environment check without API key."""
        with patch.dict(os.environ, {}, clear=True):
            result = quickstart.check_environment()
            assert result is False

    def test_check_environment_with_api_key(self, quickstart):
        """Test environment check with API key."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('start_arcade.ChatGPTManager') as mock_chatgpt:
                mock_chatgpt.return_value = Mock()
                result = quickstart.check_environment()
                assert result is True

    def test_show_welcome(self, quickstart, capsys):
        """Test welcome message display."""
        quickstart.show_welcome()
        captured = capsys.readouterr()

        assert "ATMOSPHERE ARCADE" in captured.out
        assert "MULTILINGUAL SUPPORT" in captured.out
        assert "NATURAL CONVERSATION" in captured.out

    def test_show_help(self, quickstart, capsys):
        """Test help message display."""
        quickstart.show_help()
        captured = capsys.readouterr()

        assert "QUICK START COMMANDS" in captured.out
        assert "Natural Language:" in captured.out
        assert "Multilingual:" in captured.out


class TestIntegration:
    """Integration tests for complete system functionality."""

    @pytest.mark.asyncio
    async def test_full_conversation_flow(self):
        """Test complete conversation flow from start to finish."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('api.enhanced_server_test.AIAssistant') as mock_ai:
                mock_ai_instance = Mock()
                mock_ai_instance.generate_response = AsyncMock(side_effect=[
                    "Hello! I can help you with various tasks.",
                    "Here are the files in your directory: test.txt, script.py",
                    "I've created the file 'notes.txt' for you."
                ])
                mock_ai.return_value = mock_ai_instance

                handler = EnhancedTerminalHandler()

                # Simulate conversation
                responses = []
                commands = [
                    "Hello, what can you do?",
                    "Show me the files here",
                    "Create a file called notes.txt"
                ]

                for command in commands:
                    response = await handler.process_command(command)
                    responses.append(response)

                assert len(responses) == 3
                assert all(isinstance(r, str) for r in responses)

    @pytest.mark.asyncio
    async def test_multilingual_integration(self):
        """Test multilingual functionality integration."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('api.chatgpt_manager.ChatGPTManager') as mock_manager:
                mock_manager_instance = Mock()
                mock_manager_instance.translate_text = AsyncMock(return_value="Hello! How can I help?")
                mock_manager.return_value = mock_manager_instance

                manager = ChatGPTManager()

                # Test various languages
                languages = ['es', 'fr', 'de', 'hi', 'bn']
                for lang in languages:
                    result = await manager.translate_text("Hello", lang)
                    assert isinstance(result, str)

    def test_environment_setup_integration(self):
        """Test complete environment setup."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            quickstart = ArcadeQuickStart()

            # Should pass environment check
            result = quickstart.check_environment()
            assert result is True

            # Should create necessary directories
            assert quickstart.config_dir.exists() or quickstart.config_dir.parent.exists()


# Performance and Load Testing
class TestPerformance:
    """Performance and load testing."""

    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('api.enhanced_server_test.AIAssistant') as mock_ai:
                mock_ai_instance = Mock()
                mock_ai_instance.generate_response = AsyncMock(return_value="Response")
                mock_ai.return_value = mock_ai_instance

                handler = EnhancedTerminalHandler()

                # Simulate concurrent requests
                tasks = []
                for i in range(10):
                    task = handler.process_command(f"Test command {i}")
                    tasks.append(task)

                results = await asyncio.gather(*tasks)

                assert len(results) == 10
                assert all(isinstance(r, str) for r in results)

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage under load."""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            with patch('api.chatgpt_manager.ChatGPTManager') as mock_manager:
                mock_manager_instance = Mock()
                mock_manager_instance.process_multilingual_message = AsyncMock(return_value={"content": "test"})
                mock_manager.return_value = mock_manager_instance

                manager = ChatGPTManager()

                # Perform multiple operations
                for i in range(100):
                    await manager.process_multilingual_message(f"conv_{i}", f"Message {i}")

                final_memory = process.memory_info().rss
                memory_increase = final_memory - initial_memory

                # Memory increase should be reasonable (less than 50MB)
                assert memory_increase < 50 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
