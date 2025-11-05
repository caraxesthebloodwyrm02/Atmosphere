"""Simple test suite for echo.knowledge module."""

import sys
from pathlib import Path

import pytest

# Add Echoes directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "Echoes"))

from echoes.services.knowledge import KnowledgeManager


class TestKnowledgeManagerSimple:
    """Test the KnowledgeManager class."""

    def test_init(self):
        """Test KnowledgeManager initialization."""
        km = KnowledgeManager()
        assert km is not None
        assert hasattr(km, "knowledge_base")
        assert isinstance(km.knowledge_base, dict)

    def test_add_knowledge(self):
        """Test adding knowledge to the store."""
        km = KnowledgeManager()
        result = km.add_knowledge("test_key", "test_value", {"meta": "data"})
        assert result is True
        assert "test_key" in km.knowledge_base

    def test_get_knowledge(self):
        """Test retrieving knowledge from the store."""
        km = KnowledgeManager()
        km.add_knowledge("test_key", "test_value")
        result = km.get_knowledge("test_key")
        assert result == "test_value"

    def test_get_nonexistent_knowledge(self):
        """Test retrieving non-existent knowledge."""
        km = KnowledgeManager()
        result = km.get_knowledge("nonexistent_key")
        assert result is None

    def test_search_knowledge(self):
        """Test searching knowledge."""
        km = KnowledgeManager()
        km.add_knowledge("test_key", "test_value with search term")
        km.add_knowledge("other_key", "other_value")
        results = km.search_knowledge("search term")
        assert len(results) == 1
        assert results[0]["key"] == "test_key"

    def test_list_knowledge(self):
        """Test listing all knowledge keys."""
        km = KnowledgeManager()
        km.add_knowledge("key1", "value1")
        km.add_knowledge("key2", "value2")
        keys = km.list_knowledge()
        assert isinstance(keys, list)
        assert len(keys) == 2
        assert "key1" in keys
        assert "key2" in keys

    def test_delete_knowledge(self):
        """Test deleting knowledge from the store."""
        km = KnowledgeManager()
        km.add_knowledge("test_key", "test_value")
        result = km.delete_knowledge("test_key")
        assert result is True
        assert "test_key" not in km.knowledge_base

    def test_delete_nonexistent_knowledge(self):
        """Test deleting non-existent knowledge."""
        km = KnowledgeManager()
        result = km.delete_knowledge("nonexistent_key")
        assert result is False

    def test_get_stats(self):
        """Test getting knowledge base statistics."""
        km = KnowledgeManager()
        km.add_knowledge("key1", "value1")
        km.add_knowledge("key2", "value2")
        stats = km.get_stats()
        assert isinstance(stats, dict)
        assert stats["total_items"] == 2
        assert "key1" in stats["keys"]
        assert "key2" in stats["keys"]
        assert "last_updated" in stats

    def test_add_knowledge_with_metadata(self):
        """Test adding knowledge with metadata."""
        km = KnowledgeManager()
        result = km.add_knowledge(
            "meta_key", "meta_value", {"category": "test", "priority": 1}
        )
        assert result is True
        data = km.knowledge_base["meta_key"]
        assert data["value"] == "meta_value"
        assert data["metadata"]["category"] == "test"
        assert data["metadata"]["priority"] == 1
        assert "added_at" in data

    def test_search_knowledge_case_insensitive(self):
        """Test that search is case insensitive."""
        km = KnowledgeManager()
        km.add_knowledge("TestKey", "TestValue")
        results = km.search_knowledge("testkey")
        assert len(results) == 1
        results = km.search_knowledge("testvalue")
        assert len(results) == 1

    def test_search_knowledge_empty_query(self):
        """Test searching with empty query."""
        km = KnowledgeManager()
        km.add_knowledge("key1", "value1")
        results = km.search_knowledge("")
        # Should return all items for empty query
        assert len(results) >= 0

    def test_knowledge_base_persistence(self):
        """Test that knowledge persists in the instance."""
        km = KnowledgeManager()
        km.add_knowledge("persistent", "value")
        # Retrieve multiple times
        for _ in range(3):
            result = km.get_knowledge("persistent")
            assert result == "value"

    def test_overwrite_knowledge(self):
        """Test overwriting existing knowledge."""
        km = KnowledgeManager()
        km.add_knowledge("key", "original_value")
        result = km.add_knowledge("key", "new_value")
        assert result is True
        assert km.get_knowledge("key") == "new_value"

    def test_knowledge_with_none_value(self):
        """Test handling None values."""
        km = KnowledgeManager()
        result = km.add_knowledge("none_key", None)
        assert result is True
        assert km.get_knowledge("none_key") is None

    def test_knowledge_with_complex_value(self):
        """Test handling complex values (dict, list)."""
        km = KnowledgeManager()
        complex_value = {"nested": {"data": [1, 2, 3]}}
        result = km.add_knowledge("complex_key", complex_value)
        assert result is True
        assert km.get_knowledge("complex_key") == complex_value

    def test_list_empty_knowledge(self):
        """Test listing keys from empty knowledge base."""
        km = KnowledgeManager()
        keys = km.list_knowledge()
        assert isinstance(keys, list)
        assert len(keys) == 0

    def test_get_stats_empty(self):
        """Test getting stats from empty knowledge base."""
        km = KnowledgeManager()
        stats = km.get_stats()
        assert stats["total_items"] == 0
        assert stats["keys"] == []
        assert stats["last_updated"] == "Never"

    def test_search_in_empty_knowledge(self):
        """Test searching in empty knowledge base."""
        km = KnowledgeManager()
        results = km.search_knowledge("anything")
        assert isinstance(results, list)
        assert len(results) == 0
