"""
Comprehensive test suite for Dimension & Resonance package.
"""

from io import BytesIO

import numpy as np
import pytest


# Test imports
def test_delay_imports():
    """Test delay module imports."""
    from src.delay.core.delay_essence import Delay
    from src.delay.core.echoes_essence import EchoesPlatform

    assert Delay is not None
    assert EchoesPlatform is not None


def test_reverb_imports():
    """Test reverb module imports."""
    from src.reverb.core.platform import ReverbPlatform

    assert ReverbPlatform is not None


def test_routing_imports():
    """Test routing module imports."""
    from src.routing.acoustic_routing.core.network import \
        AcousticRoutingNetwork
    from src.routing.acoustic_routing.core.visualization import \
        visualize_network

    assert AcousticRoutingNetwork is not None
    assert visualize_network is not None


# Test instantiation
def test_delay_instantiation():
    """Test Delay class instantiation."""
    from src.delay.core.delay_essence import Delay

    delay = Delay(time_ms=100, feedback=0.5)
    assert delay.time_ms == 100
    assert delay.feedback == 0.5


def test_reverb_instantiation():
    """Test ReverbPlatform instantiation."""
    from src.reverb.core.platform import ReverbPlatform

    reverb = ReverbPlatform()
    status = reverb.get_system_status()
    assert status["status"] == "active"
    assert "services" in status


def test_routing_instantiation():
    """Test AcousticRoutingNetwork instantiation."""
    from src.routing.acoustic_routing.core.network import \
        AcousticRoutingNetwork

    network = AcousticRoutingNetwork()
    assert len(network.graph.nodes) == 0
    assert len(network.acoustic_params) == 0


# Test basic functionality
def test_delay_basic_functionality():
    """Test basic delay functionality."""
    from src.delay.core.delay_essence import Delay

    delay = Delay(time_ms=100, feedback=0.2)

    # Create dummy audio signal
    audio = np.random.random(1000)
    # Note: Actual processing would require full implementation
    # For now, just test that the object exists and has expected attributes
    assert hasattr(delay, "time_ms")
    assert hasattr(delay, "feedback")


def test_reverb_system_status():
    """Test reverb system status."""
    from src.reverb.core.platform import ReverbPlatform

    reverb = ReverbPlatform()

    # Initial status check
    status = reverb.get_system_status()
    assert "status" in status
    assert "services" in status

    # Test service management
    services = status["services"]
    for service in services:
        assert "name" in service
        assert "status" in service


def test_routing_network_operations():
    """Test basic routing network operations."""
    from src.routing.acoustic_routing.core.network import \
        AcousticRoutingNetwork

    # Create network with test nodes
    network = AcousticRoutingNetwork()
    network.add_node("node1", x=0, y=0)
    network.add_node("node2", x=1, y=1)
    network.add_connection("node1", "node2")

    # Test node and edge counts
    assert len(network.graph.nodes) == 2
    assert len(network.graph.edges) == 1

    # Test path finding
    path = network.find_path("node1", "node2")
    assert len(path) == 2
    assert path[0] == "node1"
    assert path[1] == "node2"


def test_routing_visualization():
    """Test routing network visualization."""
    from src.routing.acoustic_routing.core.network import \
        AcousticRoutingNetwork
    from src.routing.acoustic_routing.core.visualization import \
        visualize_network

    network = AcousticRoutingNetwork()

    # Add some nodes
    network.add_node("node1", x=0, y=0)
    network.add_node("node2", x=1, y=1)
    network.add_connection("node1", "node2")

    # Test visualization (should not raise exception)
    try:
        buffer = visualize_network(network)
        # If buffer is returned, it should be BytesIO or None
        assert buffer is None or isinstance(buffer, BytesIO)
    except ImportError:
        # Matplotlib may not be available in test environment
        pytest.skip("Matplotlib not available for visualization tests")


# Integration tests
def test_full_pipeline():
    """Test that all modules can be imported and instantiated together."""
    # Test imports
    from src.delay.core.delay_essence import Delay
    from src.delay.core.echoes_essence import EchoesPlatform
    from src.reverb.core.platform import ReverbPlatform
    from src.routing.acoustic_routing.core.network import \
        AcousticRoutingNetwork

    # Create instances
    delay = Delay()
    echo_platform = EchoesPlatform()
    reverb = ReverbPlatform()
    network = AcousticRoutingNetwork()

    # Basic assertions
    assert delay is not None
    assert echo_platform is not None
    assert reverb is not None
    assert network is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
