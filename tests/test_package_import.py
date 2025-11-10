"""
Test package imports and basic functionality.
"""

import pytest


def test_package_import():
    """Test that the main package can be imported."""
    import atmosphere_audio
    assert atmosphere_audio.__version__ == "0.1.0"


def test_delay_module_import():
    """Test that the delay module can be imported."""
    from atmosphere_audio.delay import Delay
    
    delay = Delay()
    assert delay.time_ms == 250
    assert delay.feedback == 0.3
    assert delay.level == 0.5
    assert delay.dry_wet == 0.5


def test_reverb_module_import():
    """Test that the reverb module can be imported."""
    from atmosphere_audio.reverb import SpatialAudioVisualizer
    
    visualizer = SpatialAudioVisualizer()
    assert visualizer.sample_rate == 44100
    assert visualizer.sound_speed == 343


def test_routing_module_import():
    """Test that the routing module can be imported."""
    from atmosphere_audio.routing import AcousticParameters
    
    params = AcousticParameters(delay_time=100, feedback=0.5, decay=0.3, reverb_density=0.7)
    assert params.delay_time == 100
    assert params.feedback == 0.5
    assert params.decay == 0.3
    assert params.reverb_density == 0.7


def test_cli_version():
    """Test that the CLI shows the correct version."""
    from atmosphere_audio.cli import main
    
    # Test version flag
    result = main(["--version"])
    assert result == 0


def test_core_network_import():
    """Test that the core network module can be imported."""
    from atmosphere_audio.core.network import DeviceInfo, NetworkPresence
    import time
    
    device = DeviceInfo(
        address="192.168.1.100",
        port=8080,
        last_seen=time.time(),
        metadata={"name": "Test Device", "capabilities": ["delay", "reverb"]}
    )
    assert device.address == "192.168.1.100"
    assert device.port == 8080
    assert device.metadata["name"] == "Test Device"
    assert device.metadata["capabilities"] == ["delay", "reverb"]
    
    # Test NetworkPresence initialization
    presence = NetworkPresence(device_id="test_device")
    assert presence.device_id == "test_device"
    assert presence.broadcast_port == 37020
    assert presence.presence_interval == 30
