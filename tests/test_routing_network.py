"""
Unit tests for atmosphere_audio.routing.core.network module
"""

import numpy as np
import pytest

from atmosphere_audio.routing.core.network import (
    AcousticParameters, Pulse, AcousticRoutingNetwork
)


class TestAcousticParameters:
    """Test AcousticParameters dataclass"""

    def test_creation(self):
        params = AcousticParameters(
            delay_time=15.0,
            feedback=0.2,
            decay=0.8,
            reverb_density=0.6
        )
        assert params.delay_time == 15.0
        assert params.feedback == 0.2
        assert params.decay == 0.8
        assert params.reverb_density == 0.6

    def test_defaults_not_applicable(self):
        # No defaults in dataclass, all fields required
        pass


class TestPulse:
    """Test Pulse dataclass"""

    def test_creation(self):
        pulse = Pulse(
            origin="A",
            current_position="B",
            amplitude=0.8,
            path_history=["A", "B"]
        )
        assert pulse.origin == "A"
        assert pulse.current_position == "B"
        assert pulse.amplitude == 0.8
        assert pulse.path_history == ["A", "B"]

    def test_empty_path_history(self):
        pulse = Pulse(
            origin="A",
            current_position="A",
            amplitude=1.0,
            path_history=[]
        )
        assert pulse.path_history == []


class TestAcousticRoutingNetwork:
    """Test AcousticRoutingNetwork functionality"""

    def test_init(self):
        network = AcousticRoutingNetwork()
        assert len(network.graph.nodes) == 0
        assert len(network.graph.edges) == 0
        assert network.acoustic_params == {}
        assert network.node_positions == {}

    def test_add_node(self):
        network = AcousticRoutingNetwork()
        network.add_node("A", 10.0, 20.0)

        assert "A" in network.graph.nodes
        assert network.node_positions["A"] == (10.0, 20.0)

    def test_add_connection(self):
        network = AcousticRoutingNetwork()
        network.add_node("A", 0, 0)
        network.add_node("B", 1, 1)
        network.add_connection("A", "B")

        assert ("A", "B") in network.graph.edges
        assert ("A", "B") in network.acoustic_params

        params = network.acoustic_params[("A", "B")]
        assert params.delay_time == 10.0  # Default
        assert params.feedback == 0.1
        assert params.decay == 0.9
        assert params.reverb_density == 0.5

    def test_add_connection_without_nodes(self):
        # Should work even if nodes not explicitly added
        network = AcousticRoutingNetwork()
        network.add_connection("A", "B")

        assert "A" in network.graph.nodes
        assert "B" in network.graph.nodes
        assert ("A", "B") in network.graph.edges

    def test_find_path_existing(self):
        network = AcousticRoutingNetwork()
        network.add_connection("A", "B")
        network.add_connection("B", "C")

        path = network.find_path("A", "C")
        assert path == ["A", "B", "C"]

    def test_find_path_nonexistent(self):
        network = AcousticRoutingNetwork()
        network.add_connection("A", "B")
        network.add_connection("C", "D")  # Separate component

        path = network.find_path("A", "D")
        assert path == []  # No path

    def test_find_path_same_node(self):
        network = AcousticRoutingNetwork()
        network.add_node("A", 0, 0)

        path = network.find_path("A", "A")
        assert path == ["A"]

    def test_add_highway_segment(self):
        network = AcousticRoutingNetwork()
        network.add_highway_segment(
            "CityA", "CityB",
            distance_miles=100.0,
            speed_limit_mph=60,
            interconnectivity=0.4,
            feedback_loops=1.0
        )

        # Check edge added
        assert ("CityA", "CityB") in network.graph.edges

        # Check acoustic parameters calculated
        params = network.acoustic_params[("CityA", "CityB")]
        assert params.delay_time > 0  # Should be calculated from distance/speed
        assert params.feedback == 0.2  # feedback_loops / 5.0
        assert params.decay < 1.0  # Should be less than 1 for distance > 0
        assert params.reverb_density == 0.4

        # Check positions generated
        assert "CityA" in network.node_positions
        assert "CityB" in network.node_positions

    def test_add_highway_segment_long_distance(self):
        network = AcousticRoutingNetwork()
        network.add_highway_segment(
            "A", "B",
            distance_miles=4000.0,  # Very long distance
            speed_limit_mph=65
        )

        params = network.acoustic_params[("A", "B")]
        assert params.decay >= 0.1  # Minimum decay
        assert params.decay < 1.0

    def test_add_highway_segment_high_feedback(self):
        network = AcousticRoutingNetwork()
        network.add_highway_segment(
            "A", "B",
            distance_miles=10.0,
            feedback_loops=10.0  # High feedback
        )

        params = network.acoustic_params[("A", "B")]
        assert params.feedback == 1.0  # Capped at 1.0

    def test_generate_position(self):
        network = AcousticRoutingNetwork()

        # Test position generation (deterministic seed for test)
        np.random.seed(42)
        pos1 = network._generate_position()
        assert -100 <= pos1[0] <= 100
        assert -50 <= pos1[1] <= 50

        np.random.seed(42)
        pos2 = network._generate_position()
        assert pos1 == pos2  # Same seed should give same result

    def test_multiple_connections(self):
        network = AcousticRoutingNetwork()
        network.add_connection("A", "B")
        network.add_connection("A", "C")
        network.add_connection("B", "D")

        assert len(network.graph.edges) == 3
        assert len(network.acoustic_params) == 3

        # All should have default parameters
        for edge in [("A", "B"), ("A", "C"), ("B", "D")]:
            assert edge in network.acoustic_params
            params = network.acoustic_params[edge]
            assert params.delay_time == 10.0

    def test_node_position_preservation(self):
        network = AcousticRoutingNetwork()
        network.add_node("A", 5.0, 10.0)

        # Adding connection shouldn't overwrite position
        network.add_connection("A", "B")
        assert network.node_positions["A"] == (5.0, 10.0)
        assert "B" in network.node_positions  # Should be generated

    def test_shortest_path_weighted(self):
        network = AcousticRoutingNetwork()
        network.add_highway_segment("A", "B", 10.0)
        network.add_highway_segment("A", "C", 5.0)
        network.add_highway_segment("C", "B", 6.0)

        # Shortest path should be A -> C -> B (5 + 6 = 11) vs A -> B (10)
        path = network.find_path("A", "B")
        assert path == ["A", "C", "B"]
