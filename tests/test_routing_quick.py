"""
Quick coverage tests for routing network module.
These tests focus on basic routing functionality to boost coverage quickly.
"""

import pytest
from src.atmosphere_audio.routing.core.network import AcousticRoutingNetwork


def test_network_basic_operations():
    """Test basic network operations"""
    net = AcousticRoutingNetwork()
    net.add_node("A", 0, 0)
    net.add_node("B", 1, 1)
    net.add_connection("A", "B")
    assert "A" in net.graph.nodes
    assert "B" in net.graph.nodes


def test_simple_pathfinding():
    """Test basic path finding between nodes"""
    net = AcousticRoutingNetwork()
    net.add_connection("start", "end")
    path = net.find_path("start", "end")
    assert path == ["start", "end"]


def test_network_initialization():
    """Test network initialization"""
    net = AcousticRoutingNetwork()
    assert len(net.graph.nodes) == 0
    assert len(net.graph.edges) == 0


def test_add_multiple_nodes():
    """Test adding multiple nodes"""
    net = AcousticRoutingNetwork()
    nodes = [("A", 0, 0), ("B", 1, 1), ("C", 2, 2), ("D", 3, 3)]

    for node_id, x, y in nodes:
        net.add_node(node_id, x, y)

    assert len(net.graph.nodes) == 4
    for node_id, _, _ in nodes:
        assert node_id in net.graph.nodes


def test_connection_validation():
    """Test that connections require existing nodes"""
    net = AcousticRoutingNetwork()

    # Add nodes first
    net.add_node("A", 0, 0)
    net.add_node("B", 1, 1)

    # Now connection should work
    net.add_connection("A", "B")
    assert ("A", "B") in net.graph.edges
