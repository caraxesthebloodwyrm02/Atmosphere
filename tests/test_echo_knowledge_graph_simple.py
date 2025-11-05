"""Simple test suite for echo.knowledge_graph module."""

import sys
from pathlib import Path

import pytest

# Add Echoes directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "Echoes"))

from echoes.services.knowledge_graph import KnowledgeGraph


class TestKnowledgeGraphSimple:
    """Test the KnowledgeGraph class."""

    def test_init(self):
        """Test KnowledgeGraph initialization."""
        kg = KnowledgeGraph()
        assert kg is not None
        assert hasattr(kg, "nodes")
        assert hasattr(kg, "edges")
        assert hasattr(kg, "adjacency")
        assert isinstance(kg.nodes, dict)
        assert isinstance(kg.edges, dict)
        assert isinstance(kg.adjacency, dict)

    def test_add_node(self):
        """Test adding a node to the graph."""
        kg = KnowledgeGraph()
        result = kg.add_node("test_node", "concept", {"value": "test"})
        assert result is True
        assert "test_node" in kg.nodes
        assert kg.nodes["test_node"]["id"] == "test_node"
        assert kg.nodes["test_node"]["type"] == "concept"
        assert kg.nodes["test_node"]["properties"]["value"] == "test"
        assert "test_node" in kg.adjacency

    def test_add_edge(self):
        """Test adding an edge to the graph."""
        kg = KnowledgeGraph()
        # Add nodes first
        kg.add_node("node1", "concept")
        kg.add_node("node2", "concept")
        # Add edge
        result = kg.add_edge(
            "edge1", "node1", "node2", "related_to", {"weight": 0.5}
        )
        assert result is True
        assert "edge1" in kg.edges
        assert kg.edges["edge1"]["source"] == "node1"
        assert kg.edges["edge1"]["target"] == "node2"
        assert kg.edges["edge1"]["relationship"] == "related_to"
        assert "node2" in kg.adjacency["node1"]
        assert "node1" in kg.adjacency["node2"]

    def test_add_edge_without_nodes(self):
        """Test adding edge without existing nodes."""
        kg = KnowledgeGraph()
        result = kg.add_edge("edge1", "nonexistent1", "nonexistent2")
        assert result is False

    def test_get_node(self):
        """Test retrieving a node from the graph."""
        kg = KnowledgeGraph()
        kg.add_node("test_node", "concept", {"value": "test"})
        node = kg.get_node("test_node")
        assert node is not None
        assert node["id"] == "test_node"
        assert node["type"] == "concept"

    def test_get_nonexistent_node(self):
        """Test retrieving a non-existent node."""
        kg = KnowledgeGraph()
        node = kg.get_node("nonexistent")
        assert node is None

    def test_get_edge(self):
        """Test retrieving an edge from the graph."""
        kg = KnowledgeGraph()
        kg.add_node("node1", "concept")
        kg.add_node("node2", "concept")
        kg.add_edge("edge1", "node1", "node2", "related_to")
        edge = kg.get_edge("edge1")
        assert edge is not None
        assert edge["id"] == "edge1"
        assert edge["source"] == "node1"
        assert edge["target"] == "node2"

    def test_get_nonexistent_edge(self):
        """Test retrieving a non-existent edge."""
        kg = KnowledgeGraph()
        edge = kg.get_edge("nonexistent")
        assert edge is None

    def test_find_neighbors(self):
        """Test finding neighbors of a node."""
        kg = KnowledgeGraph()
        kg.add_node("center", "concept")
        kg.add_node("neighbor1", "concept")
        kg.add_node("neighbor2", "concept")
        kg.add_node("distant", "concept")
        kg.add_edge("edge1", "center", "neighbor1")
        kg.add_edge("edge2", "center", "neighbor2")
        kg.add_edge("edge3", "neighbor1", "distant")

        neighbors = kg.find_neighbors("center")
        assert isinstance(neighbors, list)
        # find_neighbors returns all nodes reachable within the depth
        assert len(neighbors) == 3
        assert "neighbor1" in neighbors
        assert "neighbor2" in neighbors
        assert "distant" in neighbors

    def test_find_neighbors_depth(self):
        """Test finding neighbors within a specific depth."""
        kg = KnowledgeGraph()
        kg.add_node("center", "concept")
        kg.add_node("depth1", "concept")
        kg.add_node("depth2", "concept")
        kg.add_edge("edge1", "center", "depth1")
        kg.add_edge("edge2", "depth1", "depth2")

        # Depth 1 finds all nodes reachable within depth 1
        neighbors = kg.find_neighbors("center", depth=1)
        assert len(neighbors) == 2
        assert "depth1" in neighbors
        assert "depth2" in neighbors

        # Default depth (1) finds the same as explicit depth 1
        neighbors_default = kg.find_neighbors("center")
        assert neighbors_default == neighbors

    def test_find_neighbors_nonexistent(self):
        """Test finding neighbors of non-existent node."""
        kg = KnowledgeGraph()
        neighbors = kg.find_neighbors("nonexistent")
        assert neighbors == []

    def test_search_nodes(self):
        """Test searching for nodes by query."""
        kg = KnowledgeGraph()
        kg.add_node("test_node", "concept", {"value": "search_term"})
        kg.add_node("other_node", "entity", {"value": "other"})
        kg.add_node("match_type", "concept", {"value": "no_match"})

        # Search by query
        results = kg.search_nodes("search_term")
        assert len(results) == 1
        assert results[0]["id"] == "test_node"

        # Search by type
        results = kg.search_nodes("", node_type="concept")
        assert len(results) == 2
        assert all(r["type"] == "concept" for r in results)

        # Search by both
        results = kg.search_nodes("match", node_type="concept")
        assert len(results) == 1
        assert results[0]["id"] == "match_type"

    def test_get_graph_stats(self):
        """Test getting graph statistics."""
        kg = KnowledgeGraph()
        kg.add_node("node1", "concept")
        kg.add_node("node2", "entity")
        kg.add_edge("edge1", "node1", "node2", "related_to")

        stats = kg.get_graph_stats()
        assert isinstance(stats, dict)
        assert stats["total_nodes"] == 2
        assert stats["total_edges"] == 1
        assert "concept" in stats["node_types"]
        assert "entity" in stats["node_types"]
        assert "related_to" in stats["edge_types"]
        assert stats["connected_components"] == 1

    def test_export_graph(self):
        """Test exporting the graph."""
        kg = KnowledgeGraph()
        kg.add_node("node1", "concept")
        kg.add_node("node2", "concept")
        kg.add_edge("edge1", "node1", "node2", "related_to")

        exported = kg.export_graph()
        assert isinstance(exported, dict)
        assert "nodes" in exported
        assert "edges" in exported
        assert len(exported["nodes"]) == 2
        assert len(exported["edges"]) == 1

    def test_export_graph_unsupported_format(self):
        """Test exporting with unsupported format."""
        kg = KnowledgeGraph()
        with pytest.raises(ValueError):
            kg.export_graph(format="unsupported")

    def test_multiple_edges_between_nodes(self):
        """Test multiple edges between the same nodes."""
        kg = KnowledgeGraph()
        kg.add_node("node1", "concept")
        kg.add_node("node2", "concept")
        kg.add_edge("edge1", "node1", "node2", "relation1")
        kg.add_edge("edge2", "node1", "node2", "relation2")

        assert len(kg.edges) == 2
        neighbors = kg.find_neighbors("node1")
        assert len(neighbors) == 1  # Still only one unique neighbor

    def test_self_loop_edge(self):
        """Test adding an edge from a node to itself."""
        kg = KnowledgeGraph()
        kg.add_node("self_node", "concept")
        result = kg.add_edge(
            "self_edge", "self_node", "self_node", "self_relation"
        )
        assert result is True
        assert "self_edge" in kg.edges
        # Self loop should not create duplicate in adjacency
        assert "self_node" in kg.adjacency["self_node"]

    def test_duplicate_nodes(self):
        """Test adding duplicate nodes."""
        kg = KnowledgeGraph()
        kg.add_node("duplicate", "concept", {"v": 1})
        result = kg.add_node("duplicate", "concept", {"v": 2})
        assert result is True
        # Node should be overwritten
        assert kg.nodes["duplicate"]["properties"]["v"] == 2

    def test_duplicate_edges(self):
        """Test adding duplicate edges."""
        kg = KnowledgeGraph()
        kg.add_node("node1", "concept")
        kg.add_node("node2", "concept")
        kg.add_edge("edge1", "node1", "node2", "relation1")
        result = kg.add_edge("edge1", "node1", "node2", "relation2")
        assert result is True
        # Edge should be overwritten
        assert kg.edges["edge1"]["relationship"] == "relation2"

    def test_empty_graph_stats(self):
        """Test statistics of empty graph."""
        kg = KnowledgeGraph()
        stats = kg.get_graph_stats()
        assert stats["total_nodes"] == 0
        assert stats["total_edges"] == 0
        assert stats["node_types"] == []
        assert stats["edge_types"] == []
        assert stats["connected_components"] == 0

    def test_disconnected_components(self):
        """Test counting disconnected components."""
        kg = KnowledgeGraph()
        # Component 1
        kg.add_node("comp1_a", "concept")
        kg.add_node("comp1_b", "concept")
        kg.add_edge("edge1", "comp1_a", "comp1_b")
        # Component 2 (disconnected)
        kg.add_node("comp2_a", "concept")
        kg.add_node("comp2_b", "concept")
        kg.add_edge("edge2", "comp2_a", "comp2_b")

        stats = kg.get_graph_stats()
        assert stats["connected_components"] == 2
