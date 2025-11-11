"""
Unit tests for delay/core/knowledge_graph.py
"""

import pytest
from atmosphere_audio.delay.core.knowledge_graph import KnowledgeGraph


def test_knowledge_graph_add_triple():
    """Test adding triples to the knowledge graph."""
    kg = KnowledgeGraph()
    kg.add_triple("subject", "predicate", "object")
    assert len(kg.triples) == 1
    assert kg.triples[0] == ("subject", "predicate", "object")


def test_knowledge_graph_query_full_match():
    """Test querying with full subject-predicate-object match."""
    kg = KnowledgeGraph()
    kg.add_triple("s1", "p1", "o1")
    kg.add_triple("s2", "p2", "o2")
    
    results = kg.query("s1", "p1", "o1")
    assert len(results) == 1
    assert results[0] == ("s1", "p1", "o1")


def test_knowledge_graph_query_partial_match():
    """Test querying with partial matches."""
    kg = KnowledgeGraph()
    kg.add_triple("s1", "p1", "o1")
    kg.add_triple("s1", "p2", "o2")
    kg.add_triple("s2", "p1", "o1")
    
    # Query by subject only
    results = kg.query(subject="s1")
    assert len(results) == 2
    assert ("s1", "p1", "o1") in results
    assert ("s1", "p2", "o2") in results
    
    # Query by predicate only
    results = kg.query(predicate="p1")
    assert len(results) == 2
    assert ("s1", "p1", "o1") in results
    assert ("s2", "p1", "o1") in results


def test_knowledge_graph_infer_ontology():
    """Test ontology inference."""
    kg = KnowledgeGraph()
    kg.add_triple("concept", "related_to", "other_concept")
    kg.add_triple("concept", "subclass_of", "parent_concept")
    kg.add_triple("unrelated", "property", "value")
    
    results = kg.infer_ontology("concept")
    assert len(results) == 2
    assert ("concept", "related_to", "other_concept") in results
    assert ("concept", "subclass_of", "parent_concept") in results


def test_knowledge_graph_decay_modeling():
    """Test decay modeling returns expected string."""
    kg = KnowledgeGraph()
    assert kg.decay_modeling() == "Ontology-based decay simulated."
