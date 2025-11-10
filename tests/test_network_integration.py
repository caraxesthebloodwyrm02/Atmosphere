"""
Comprehensive tests for network_integration module - APOLLO 11 STYLE! 🚀
Testing AtmosphereNetworkCoordinator and AtmosphereDevice.
"""

import time
from unittest.mock import MagicMock, Mock, patch
import pytest

from src.network_integration import AtmosphereDevice, AtmosphereNetworkCoordinator


class TestAtmosphereDevice:
    """Test AtmosphereDevice dataclass - IGNITION SEQUENCE START!"""

    def test_device_creation_minimal(self):
        """T-10: Test minimal device creation."""
        device = AtmosphereDevice(
            device_id="apollo-11",
            address="192.168.1.100",
            port=37021,
            last_seen=time.time()
        )
        
        assert device.device_id == "apollo-11"
        assert device.address == "192.168.1.100"
        assert device.port == 37021
        assert device.device_type == "unknown"
        assert device.capabilities == []
        assert device.services == {}
        assert device.metadata == {}

    def test_device_creation_full(self):
        """T-9: Test full device creation."""
        capabilities = ["monitoring", "audio", "routing"]
        services = {"http": 8080, "ws": 8081}
        metadata = {"version": "1.0", "location": "Houston"}
        
        device = AtmosphereDevice(
            device_id="lunar-module",
            address="10.0.0.50",
            port=5000,
            last_seen=time.time(),
            device_type="atmosphere",
            capabilities=capabilities,
            ecosystem_version="2.0.0",
            services=services,
            metadata=metadata
        )
        
        assert device.device_id == "lunar-module"
        assert device.device_type == "atmosphere"
        assert device.capabilities == capabilities
        assert device.ecosystem_version == "2.0.0"
        assert device.services == services
        assert device.metadata == metadata

    def test_device_post_init_defaults(self):
        """T-8: Test __post_init__ sets defaults."""
        device = AtmosphereDevice(
            device_id="test",
            address="1.1.1.1",
            port=1,
            last_seen=time.time(),
            capabilities=None,
            services=None,
            metadata=None
        )
        
        # Should initialize to empty collections
        assert isinstance(device.capabilities, list)
        assert isinstance(device.services, dict)
        assert isinstance(device.metadata, dict)

    def test_device_types(self):
        """T-7: Test various device types."""
        types = ["atmosphere", "monitor", "client", "router", "server"]
        
        for device_type in types:
            device = AtmosphereDevice(
                device_id=f"{device_type}-device",
                address="127.0.0.1",
                port=8000,
                last_seen=time.time(),
                device_type=device_type
            )
            assert device.device_type == device_type


class TestAtmosphereNetworkCoordinatorInit:
    """Test coordinator initialization - MAIN ENGINE START!"""

    def test_coordinator_default_init(self):
        """T-6: Test default initialization."""
        coordinator = AtmosphereNetworkCoordinator("houston-control")
        
        assert coordinator.device_id == "houston-control"
        assert coordinator.device_type == "atmosphere"
        assert coordinator.capabilities == ["monitoring"]
        assert coordinator.ecosystem_version == "1.0.0"
        assert coordinator.atmosphere_devices == {}
        assert coordinator._running is False

    def test_coordinator_custom_init(self):
        """T-5: Test custom initialization."""
        capabilities = ["audio", "routing", "monitoring"]
        coordinator = AtmosphereNetworkCoordinator(
            device_id="mission-control",
            device_type="server",
            capabilities=capabilities
        )
        
        assert coordinator.device_id == "mission-control"
        assert coordinator.device_type == "server"
        assert coordinator.capabilities == capabilities

    def test_coordinator_creates_network_presence(self):
        """T-4: Test NetworkPresence initialization."""
        coordinator = AtmosphereNetworkCoordinator("test-device")
        
        assert hasattr(coordinator, "network_presence")
        assert coordinator.network_presence is not None
        assert coordinator.network_presence.device_id == "test-device"

    def test_coordinator_creates_lock(self):
        """T-3: Test threading lock creation."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        assert hasattr(coordinator, "_device_lock")
        assert coordinator._device_lock is not None


class TestAtmosphereNetworkCoordinatorStartStop:
    """Test start/stop operations - LIFTOFF SEQUENCE!"""

    def test_start_activates_coordinator(self):
        """T-2: Test start() activates coordinator."""
        coordinator = AtmosphereNetworkCoordinator("apollo-11")
        
        with patch.object(coordinator.network_presence, "start"):
            with patch.object(coordinator, "_monitor_devices"):
                coordinator.start()
                
                assert coordinator._running is True
                assert coordinator._monitor_thread is not None
                coordinator.network_presence.start.assert_called_once()

    def test_start_idempotent(self):
        """T-1: Test start() is idempotent."""
        coordinator = AtmosphereNetworkCoordinator("apollo-11")
        
        with patch.object(coordinator.network_presence, "start"):
            with patch.object(coordinator, "_monitor_devices"):
                coordinator.start()
                first_thread = coordinator._monitor_thread
                
                coordinator.start()  # Second call
                assert coordinator._monitor_thread == first_thread

    def test_stop_deactivates_coordinator(self):
        """LIFTOFF! Test stop() deactivates coordinator."""
        coordinator = AtmosphereNetworkCoordinator("apollo-11")
        
        with patch.object(coordinator.network_presence, "start"):
            with patch.object(coordinator.network_presence, "stop"):
                with patch.object(coordinator, "_monitor_devices"):
                    coordinator.start()
                    assert coordinator._running is True
                    
                    coordinator.stop()
                    assert coordinator._running is False
                    coordinator.network_presence.stop.assert_called_once()


class TestAtmosphereDeviceTracking:
    """Test device tracking - WE HAVE LIFTOFF!"""

    def test_get_devices_empty(self):
        """Test get_atmosphere_devices() with no devices."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        devices = coordinator.get_atmosphere_devices()
        assert devices == {}

    def test_get_devices_returns_all(self):
        """Test get_atmosphere_devices() returns all devices."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        # Add devices of different types
        coordinator.atmosphere_devices["dev1"] = AtmosphereDevice(
            device_id="dev1",
            address="1.1.1.1",
            port=1,
            last_seen=time.time(),
            device_type="atmosphere"
        )
        coordinator.atmosphere_devices["dev2"] = AtmosphereDevice(
            device_id="dev2",
            address="2.2.2.2",
            port=2,
            last_seen=time.time(),
            device_type="monitor"
        )
        
        # Get all devices
        devices = coordinator.get_atmosphere_devices()
        assert len(devices) == 2
        assert "dev1" in devices
        assert "dev2" in devices

    def test_get_device_from_dict(self):
        """Test accessing devices from atmosphere_devices dict."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        test_device = AtmosphereDevice(
            device_id="lunar-module",
            address="192.168.1.100",
            port=5000,
            last_seen=time.time()
        )
        coordinator.atmosphere_devices["lunar-module"] = test_device
        
        retrieved = coordinator.atmosphere_devices.get("lunar-module")
        assert retrieved is not None
        assert retrieved.device_id == "lunar-module"
        assert retrieved.address == "192.168.1.100"

    def test_get_device_not_found(self):
        """Test accessing nonexistent device."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        result = coordinator.atmosphere_devices.get("nonexistent")
        assert result is None


class TestServiceCallbacks:
    """Test service discovery callbacks - HOUSTON, WE HAVE A SIGNAL!"""

    def test_register_service_callback(self):
        """Test registering service discovery callback."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        callback = Mock()
        coordinator.register_service_callback("audio", callback)
        
        assert "audio" in coordinator._service_callbacks
        assert callback in coordinator._service_callbacks["audio"]

    def test_register_multiple_callbacks_same_service(self):
        """Test multiple callbacks for same service."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        callback1 = Mock()
        callback2 = Mock()
        
        coordinator.register_service_callback("audio", callback1)
        coordinator.register_service_callback("audio", callback2)
        
        assert len(coordinator._service_callbacks["audio"]) == 2


class TestDeviceCapabilities:
    """Test device capabilities - ALL SYSTEMS GO!"""

    def test_get_devices_by_capability(self):
        """Test filtering devices by capability."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        # Add devices with different capabilities
        coordinator.atmosphere_devices["dev1"] = AtmosphereDevice(
            device_id="dev1",
            address="1.1.1.1",
            port=1,
            last_seen=time.time(),
            capabilities=["audio", "monitoring"]
        )
        coordinator.atmosphere_devices["dev2"] = AtmosphereDevice(
            device_id="dev2",
            address="2.2.2.2",
            port=2,
            last_seen=time.time(),
            capabilities=["routing", "monitoring"]
        )
        
        # Get devices with audio capability
        devices = coordinator.get_devices_by_capability("audio")
        assert len(devices) == 1
        assert "dev1" in devices

    def test_get_devices_by_multiple_capabilities(self):
        """Test filtering by multiple capabilities."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        coordinator.atmosphere_devices["dev1"] = AtmosphereDevice(
            device_id="dev1",
            address="1.1.1.1",
            port=1,
            last_seen=time.time(),
            capabilities=["audio", "routing", "monitoring"]
        )
        
        # Device has all required capabilities
        devices = coordinator.get_devices_by_capability("audio")
        assert len(devices) == 1
        
        devices = coordinator.get_devices_by_capability("routing")
        assert len(devices) == 1


class TestIntegration:
    """Integration tests - ROGER, GO FOR ORBIT!"""

    def test_full_lifecycle(self):
        """Test complete start/stop lifecycle."""
        coordinator = AtmosphereNetworkCoordinator("mission-control")
        
        with patch.object(coordinator.network_presence, "start"):
            with patch.object(coordinator.network_presence, "stop"):
                with patch.object(coordinator, "_monitor_devices"):
                    # Start
                    coordinator.start()
                    assert coordinator._running is True
                    
                    # Stop
                    coordinator.stop()
                    assert coordinator._running is False

    def test_multiple_devices_tracking(self):
        """Test tracking multiple devices."""
        coordinator = AtmosphereNetworkCoordinator("houston")
        
        # Add fleet of devices
        for i in range(5):
            device = AtmosphereDevice(
                device_id=f"apollo-{i}",
                address=f"192.168.1.{100+i}",
                port=37021 + i,
                last_seen=time.time(),
                device_type="atmosphere",
                capabilities=["monitoring", "audio"]
            )
            coordinator.atmosphere_devices[f"apollo-{i}"] = device
        
        devices = coordinator.get_atmosphere_devices()
        assert len(devices) == 5

    def test_ecosystem_version_tracking(self):
        """Test ecosystem version tracking."""
        coordinator = AtmosphereNetworkCoordinator("test")
        
        assert coordinator.ecosystem_version == "1.0.0"
        
        # Add devices with various versions
        for i, version in enumerate(["1.0.0", "1.1.0", "2.0.0"]):
            device = AtmosphereDevice(
                device_id=f"dev-{i}",
                address=f"1.1.1.{i}",
                port=8000+i,
                last_seen=time.time(),
                ecosystem_version=version
            )
            coordinator.atmosphere_devices[f"dev-{i}"] = device
        
        devices = coordinator.get_atmosphere_devices()
        assert len(devices) == 3


# TOUCHDOWN! 🎯
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
