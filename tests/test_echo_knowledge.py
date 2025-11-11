"""
Unit tests for echo/core/knowledge.py
"""

import pytest
from unittest.mock import patch
from datetime import datetime
from atmosphere_audio.echo.core.knowledge import KnowledgeManager


@pytest.fixture
def knowledge_manager():
    """Fixture that ensures we get the fallback KnowledgeManager."""
    with patch('atmosphere_audio.echo.core.knowledge.safe_import', return_value=(None, False)):
        # Re-import the module to trigger the fallback
        import importlib
        import atmosphere_audio.echo.core.knowledge
        importlib.reload(atmosphere_audio.echo.core.knowledge)
        yield atmosphere_audio.echo.core.knowledge.KnowledgeManager


def test_knowledge_manager_init(knowledge_manager):
    """Test KnowledgeManager initialization."""
    km = knowledge_manager()
    assert km.knowledge_base == {}


def test_knowledge_manager_add_knowledge(knowledge_manager):
    """Test adding knowledge to the knowledge base."""
    km = knowledge_manager()
    
    # Add knowledge with metadata
    result = km.add_knowledge("test_key", "test_value", {"category": "test"})
    assert result is True
    assert "test_key" in km.knowledge_base
    assert km.knowledge_base["test_key"]["value"] == "test_value"
    assert km.knowledge_base["test_key"]["metadata"] == {"category": "test"}
    
    # Add knowledge without metadata
    result = km.add_knowledge("key2", 42)
    assert result is True
    assert km.knowledge_base["key2"]["value"] == 42
    assert km.knowledge_base["key2"]["metadata"] == {}


def test_knowledge_manager_get_knowledge(knowledge_manager):
    """Test retrieving knowledge by key."""
    km = knowledge_manager()
    km.add_knowledge("existing", "value")
    
    # Get existing knowledge
    result = km.get_knowledge("existing")
    assert result == "value"
    
    # Get non-existing knowledge
    result = km.get_knowledge("nonexistent")
    assert result is None


def test_knowledge_manager_search_knowledge(knowledge_manager):
    """Test searching knowledge base."""
    km = knowledge_manager()
    km.add_knowledge("apple", "fruit", {"color": "red"})
    km.add_knowledge("car", "vehicle", {"wheels": 4})
    km.add_knowledge("pineapple", "fruit", {"color": "yellow"})
    
    # Search by key
    results = km.search_knowledge("apple")
    assert len(results) == 2  # apple and pineapple
    assert results[0]["key"] in ["apple", "pineapple"]
    
    # Search by value
    results = km.search_knowledge("fruit")
    assert len(results) == 2
    assert all(r["value"] == "fruit" for r in results)
    
    # Search with no matches
    results = km.search_knowledge("nonexistent")
    assert len(results) == 0


def test_knowledge_manager_list_knowledge(knowledge_manager):
    """Test listing all knowledge keys."""
    km = knowledge_manager()
    km.add_knowledge("key1", "value1")
    km.add_knowledge("key2", "value2")
    
    keys = km.list_knowledge()
    assert len(keys) == 2
    assert "key1" in keys
    assert "key2" in keys


def test_knowledge_manager_delete_knowledge(knowledge_manager):
    """Test deleting knowledge by key."""
    km = knowledge_manager()
    km.add_knowledge("test_key", "value")
    
    # Delete existing key
    result = km.delete_knowledge("test_key")
    assert result is True
    assert "test_key" not in km.knowledge_base
    
    # Delete non-existing key
    result = km.delete_knowledge("nonexistent")
    assert result is False


def test_knowledge_manager_get_stats(knowledge_manager):
    """Test getting knowledge base statistics."""
    km = knowledge_manager()
    
    # Empty knowledge base
    stats = km.get_stats()
    assert stats["total_items"] == 0
    assert stats["keys"] == []
    assert stats["last_updated"] == "Never"
    
    # After adding items
    km.add_knowledge("key1", "value1")
    km.add_knowledge("key2", "value2")
    
    stats = km.get_stats()
    assert stats["total_items"] == 2
    assert set(stats["keys"]) == {"key1", "key2"}
    assert isinstance(stats["last_updated"], str)
    assert stats["last_updated"] != "Never"


def test_knowledge_manager_add_knowledge_exception(knowledge_manager):
    """Test add_knowledge handles exceptions gracefully."""
    km = knowledge_manager()
    
    # Mock the knowledge_base to raise an exception
    km.knowledge_base = None  # This will cause an exception
    
    result = km.add_knowledge("test", "value")
    assert result is False
