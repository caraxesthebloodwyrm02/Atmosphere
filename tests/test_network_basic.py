"""
Comprehensive tests for network module.
Tests NetworkPresence and DeviceInfo classes with mocked sockets.
"""

import json
import time
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.network import DeviceInfo, NetworkPresence


class TestDeviceInfo:
    """Test DeviceInfo dataclass."""

    def test_device_info_creation(self):
        """Test creating DeviceInfo instance."""
        metadata = {"hostname": "test-host", "version": "1.0"}
        device = DeviceInfo(
            address="192.168.1.100",
            port=37021,
            last_seen=time.time(),
            metadata=metadata
        )
        
        assert device.address == "192.168.1.100"
        assert device.port == 37021
        assert device.metadata == metadata

    def test_device_info_with_empty_metadata(self):
        """Test DeviceInfo with empty metadata."""
        device = DeviceInfo(
            address="10.0.0.1",
            port=5000,
            last_seen=time.time(),
            metadata={}
        )
        
        assert device.metadata == {}

    def test_device_info_timestamp(self):
        """Test DeviceInfo stores timestamp."""
        now = time.time()
        device = DeviceInfo(
            address="127.0.0.1",
            port=8000,
            last_seen=now,
            metadata={}
        )
        
        assert device.last_seen == now


class TestNetworkPresenceInitialization:
    """Test NetworkPresence initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        presence = NetworkPresence("device-1")
        
        assert presence.device_id == "device-1"
        assert presence.broadcast_port == 37020
        assert presence.presence_interval == 30
        assert presence.known_devices == {}
        assert presence.running is False

    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        presence = NetworkPresence(
            device_id="custom-device",
            broadcast_port=5000,
            presence_interval=60
        )
        
        assert presence.device_id == "custom-device"
        assert presence.broadcast_port == 5000
        assert presence.presence_interval == 60

    def test_initialization_creates_lock(self):
        """Test initialization creates threading lock."""
        presence = NetworkPresence("device-1")
        
        assert hasattr(presence, "_lock")
        assert presence._lock is not None


class TestNetworkPresenceStartStop:
    """Test start and stop operations."""

    def test_start_sets_running_flag(self):
        """Test start() sets running flag."""
        presence = NetworkPresence("device-1")
        
        with patch.object(presence, "_announce_loop"):
            with patch.object(presence, "_listen_loop"):
                presence.start()
                assert presence.running is True

    def test_start_creates_threads(self):
        """Test start() creates background threads."""
        presence = NetworkPresence("device-1")
        
        with patch.object(presence, "_announce_loop"):
            with patch.object(presence, "_listen_loop"):
                presence.start()
                assert presence._announce_thread is not None
                assert presence._listen_thread is not None

    def test_start_idempotent(self):
        """Test calling start() multiple times is safe."""
        presence = NetworkPresence("device-1")
        
        with patch.object(presence, "_announce_loop"):
            with patch.object(presence, "_listen_loop"):
                presence.start()
                first_announce = presence._announce_thread
                
                presence.start()  # Should not create new threads
                assert presence._announce_thread is first_announce

    def test_stop_clears_running_flag(self):
        """Test stop() clears running flag."""
        presence = NetworkPresence("device-1")
        
        with patch.object(presence, "_announce_loop"):
            with patch.object(presence, "_listen_loop"):
                presence.start()
        
        presence.stop()
        assert presence.running is False

    def test_stop_waits_for_threads(self):
        """Test stop() waits for threads to finish."""
        presence = NetworkPresence("device-1")
        
        mock_thread = MagicMock()
        presence._announce_thread = mock_thread
        presence._listen_thread = mock_thread
        presence.running = True
        
        presence.stop()
        
        # Verify join was called with timeout
        assert mock_thread.join.called


class TestNetworkPresenceGetDevices:
    """Test get_devices method."""

    def test_get_devices_empty(self):
        """Test get_devices returns empty dict initially."""
        presence = NetworkPresence("device-1")
        
        with patch.object(presence, "_cleanup_old_devices"):
            devices = presence.get_devices()
        
        assert devices == {}

    def test_get_devices_with_known_devices(self):
        """Test get_devices returns known devices."""
        presence = NetworkPresence("device-1")
        
        # Add a known device
        metadata = {"hostname": "host-1", "version": "1.0"}
        device_info = DeviceInfo(
            address="192.168.1.100",
            port=37021,
            last_seen=time.time(),
            metadata=metadata
        )
        presence.known_devices["device-2"] = device_info
        
        with patch.object(presence, "_cleanup_old_devices"):
            devices = presence.get_devices()
        
        assert "device-2" in devices
        assert devices["device-2"]["address"] == "192.168.1.100"
        assert devices["device-2"]["port"] == 37021
        assert devices["device-2"]["hostname"] == "host-1"

    def test_get_devices_calls_cleanup(self):
        """Test get_devices calls cleanup."""
        presence = NetworkPresence("device-1")
        
        with patch.object(presence, "_cleanup_old_devices") as mock_cleanup:
            presence.get_devices()
            mock_cleanup.assert_called_once()

    def test_get_devices_thread_safe(self):
        """Test get_devices uses lock."""
        presence = NetworkPresence("device-1")
        
        # Replace lock with a mock
        mock_lock = MagicMock()
        presence._lock = mock_lock
        
        with patch.object(presence, "_cleanup_old_devices"):
            presence.get_devices()
            mock_lock.__enter__.assert_called()
            mock_lock.__exit__.assert_called()


class TestNetworkPresenceAnnounce:
    """Test presence announcement."""

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_presence_creates_socket(self, mock_hostname, mock_socket_class):
        """Test _announce_presence creates socket."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        presence = NetworkPresence("device-1")
        presence._announce_presence()
        
        mock_socket_class.assert_called_once_with(
            __import__("socket").AF_INET,
            __import__("socket").SOCK_DGRAM
        )

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_presence_sends_message(self, mock_hostname, mock_socket_class):
        """Test _announce_presence sends message."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        presence = NetworkPresence("device-1", broadcast_port=37020)
        presence._announce_presence()
        
        # Verify sendto was called
        assert mock_socket.sendto.called
        
        # Get the message that was sent
        call_args = mock_socket.sendto.call_args
        message_bytes = call_args[0][0]
        message = json.loads(message_bytes.decode("utf-8"))
        
        assert message["type"] == "PRESENCE"
        assert message["device_id"] == "device-1"
        assert "timestamp" in message
        assert "port" in message
        assert "metadata" in message

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_presence_closes_socket(self, mock_hostname, mock_socket_class):
        """Test _announce_presence closes socket."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        presence = NetworkPresence("device-1")
        presence._announce_presence()
        
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_announce_presence_handles_socket_error(self, mock_socket_class):
        """Test _announce_presence handles socket errors."""
        mock_socket_class.side_effect = OSError("Network error")
        
        presence = NetworkPresence("device-1")
        
        # Should not raise exception
        presence._announce_presence()

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_presence_sets_broadcast_option(self, mock_hostname, mock_socket_class):
        """Test _announce_presence sets broadcast socket option."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        presence = NetworkPresence("device-1")
        presence._announce_presence()
        
        # Verify setsockopt was called for broadcast
        mock_socket.setsockopt.assert_called()


class TestNetworkPresenceAnnounceLoop:
    """Test announcement loop."""

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_loop_runs_while_active(self, mock_hostname, mock_socket_class):
        """Test _announce_loop runs while running is True."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        presence = NetworkPresence("device-1", presence_interval=1)
        presence.running = True
        
        # Run loop for a short time
        call_count = 0
        original_announce = presence._announce_presence
        
        def counting_announce():
            nonlocal call_count
            call_count += 1
            if call_count >= 2:
                presence.running = False
            original_announce()
        
        presence._announce_presence = counting_announce
        presence._announce_loop()
        
        assert call_count >= 1

    def test_announce_loop_handles_errors(self):
        """Test _announce_loop handles errors gracefully."""
        presence = NetworkPresence("device-1", presence_interval=1)
        presence.running = True
        
        call_count = 0
        
        def failing_announce():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise OSError("Network error")
            presence.running = False
        
        presence._announce_presence = failing_announce
        
        # Should not raise exception
        presence._announce_loop()
        
        assert call_count >= 1


class TestNetworkPresenceIntegration:
    """Integration tests for NetworkPresence."""

    def test_full_lifecycle(self):
        """Test full start/stop lifecycle."""
        presence = NetworkPresence("device-1")
        
        assert presence.running is False
        
        with patch.object(presence, "_announce_loop"):
            with patch.object(presence, "_listen_loop"):
                presence.start()
                assert presence.running is True
                
                presence.stop()
                assert presence.running is False

    def test_multiple_devices(self):
        """Test tracking multiple devices."""
        presence = NetworkPresence("device-1")
        
        # Add multiple devices
        for i in range(3):
            device_info = DeviceInfo(
                address=f"192.168.1.{100+i}",
                port=37021 + i,
                last_seen=time.time(),
                metadata={"id": i}
            )
            presence.known_devices[f"device-{i}"] = device_info
        
        with patch.object(presence, "_cleanup_old_devices"):
            devices = presence.get_devices()
        
        assert len(devices) == 3
        for i in range(3):
            assert f"device-{i}" in devices


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
