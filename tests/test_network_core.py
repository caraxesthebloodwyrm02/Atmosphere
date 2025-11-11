"""
Tests for atmosphere_audio.core.network module.

This module tests the network presence and device discovery functionality.
"""

import json
import socket
import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from atmosphere_audio.core.network import DeviceInfo, NetworkPresence


class TestDeviceInfo:
    """Tests for DeviceInfo dataclass."""

    def test_device_info_creation(self):
        """Test creating a DeviceInfo instance."""
        metadata = {"hostname": "test-device", "version": "1.0"}
        device = DeviceInfo(
            address="192.168.1.100",
            port=8080,
            last_seen=1234567890.0,
            metadata=metadata
        )

        assert device.address == "192.168.1.100"
        assert device.port == 8080
        assert device.last_seen == 1234567890.0
        assert device.metadata == metadata

    def test_device_info_equality(self):
        """Test DeviceInfo equality comparison."""
        device1 = DeviceInfo("192.168.1.100", 8080, 1234567890.0, {"test": "value"})
        device2 = DeviceInfo("192.168.1.100", 8080, 1234567890.0, {"test": "value"})
        device3 = DeviceInfo("192.168.1.101", 8080, 1234567890.0, {"test": "value"})

        assert device1 == device2
        assert device1 != device3


class TestNetworkPresence:
    """Tests for NetworkPresence class."""

    def test_initialization(self):
        """Test NetworkPresence initialization."""
        presence = NetworkPresence("test-device")

        assert presence.device_id == "test-device"
        assert presence.broadcast_port == 37020
        assert presence.presence_interval == 30
        assert presence.known_devices == {}
        assert presence.running is False
        assert isinstance(presence._lock, type(threading.Lock()))

    def test_initialization_custom_params(self):
        """Test NetworkPresence initialization with custom parameters."""
        presence = NetworkPresence("test-device", broadcast_port=12345, presence_interval=60)

        assert presence.device_id == "test-device"
        assert presence.broadcast_port == 12345
        assert presence.presence_interval == 60

    @patch('atmosphere_audio.core.network.socket.socket')
    @patch('atmosphere_audio.core.network.threading.Thread')
    def test_start_service(self, mock_thread, mock_socket):
        """Test starting the network presence service."""
        mock_socket.return_value = MagicMock()
        mock_thread.return_value = MagicMock()

        presence = NetworkPresence("test-device")
        presence.start()

        assert presence.running is True
        assert mock_thread.call_count == 2  # announce and listen threads

        # Check thread creation calls
        calls = mock_thread.call_args_list
        assert calls[0][1]['target'] == presence._announce_loop
        assert calls[1][1]['target'] == presence._listen_loop

    @patch('atmosphere_audio.core.network.socket.socket')
    @patch('atmosphere_audio.core.network.threading.Thread')
    def test_stop_service(self, mock_thread, mock_socket):
        """Test stopping the network presence service."""
        mock_socket.return_value = MagicMock()
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        presence = NetworkPresence("test-device")
        presence.start()
        assert presence.running is True

        presence.stop()
        assert presence.running is False

        # Check that threads were joined
        assert mock_thread_instance.join.call_count == 2

    def test_get_devices_empty(self):
        """Test get_devices with no known devices."""
        presence = NetworkPresence("test-device")
        devices = presence.get_devices()

        assert devices == {}

    def test_get_devices_with_known_devices(self):
        """Test get_devices with known devices."""
        presence = NetworkPresence("test-device")

        # Add some test devices
        device1 = DeviceInfo("192.168.1.100", 8080, time.time(), {"hostname": "device1"})
        device2 = DeviceInfo("192.168.1.101", 8081, time.time(), {"hostname": "device2"})

        presence.known_devices = {
            "device1": device1,
            "device2": device2
        }

        devices = presence.get_devices()

        assert len(devices) == 2
        assert devices["device1"]["address"] == "192.168.1.100"
        assert devices["device1"]["port"] == 8080
        assert devices["device1"]["hostname"] == "device1"
        assert devices["device2"]["hostname"] == "device2"

    @patch('atmosphere_audio.core.network.socket.socket')
    @patch('atmosphere_audio.core.network.socket.gethostname')
    def test_announce_presence_success(self, mock_gethostname, mock_socket_class):
        """Test successful presence announcement."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_gethostname.return_value = "test-host"

        presence = NetworkPresence("test-device")
        presence._announce_presence()

        # Verify socket was created and configured
        mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_sock.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        # Verify message was sent
        mock_sock.sendto.assert_called_once()
        args, kwargs = mock_sock.sendto.call_args

        # Parse the sent message
        message_data = json.loads(args[0].decode('utf-8'))
        assert message_data["type"] == "PRESENCE"
        assert message_data["device_id"] == "test-device"
        assert message_data["port"] == 37021  # broadcast_port + 1
        assert message_data["metadata"]["hostname"] == "test-host"

        # Verify broadcast address
        assert args[1] == ("<broadcast>", 37020)

        # Verify socket was closed
        mock_sock.close.assert_called_once()

    @patch('atmosphere_audio.core.network.socket.socket')
    def test_announce_presence_socket_error(self, mock_socket_class):
        """Test presence announcement with socket error."""
        mock_sock = MagicMock()
        mock_sock.sendto.side_effect = socket.error("Network unreachable")
        mock_socket_class.return_value = mock_sock

        presence = NetworkPresence("test-device")

        # Should not raise exception, just log error
        presence._announce_presence()

        mock_sock.close.assert_called_once()

    def test_handle_presence_valid_message(self):
        """Test handling a valid presence message."""
        presence = NetworkPresence("test-device")

        message = {
            "type": "PRESENCE",
            "device_id": "remote-device",
            "port": 8080,
            "metadata": {"hostname": "remote-host"}
        }
        data = json.dumps(message).encode('utf-8')
        address = "192.168.1.100"

        presence._handle_presence(address, data)

        assert "remote-device" in presence.known_devices
        device_info = presence.known_devices["remote-device"]
        assert device_info.address == address
        assert device_info.port == 8080
        assert device_info.metadata["hostname"] == "remote-host"

    def test_handle_presence_own_message(self):
        """Test handling our own presence message (should be ignored)."""
        presence = NetworkPresence("test-device")

        message = {
            "type": "PRESENCE",
            "device_id": "test-device",  # Same as our device ID
            "port": 8080,
            "metadata": {"hostname": "test-host"}
        }
        data = json.dumps(message).encode('utf-8')
        address = "192.168.1.100"

        presence._handle_presence(address, data)

        # Should not add our own device
        assert len(presence.known_devices) == 0

    def test_handle_presence_invalid_json(self):
        """Test handling invalid JSON in presence message."""
        presence = NetworkPresence("test-device")

        # Send invalid JSON
        data = b"invalid json data"
        address = "192.168.1.100"

        presence._handle_presence(address, data)

        # Should not crash, no devices should be added
        assert len(presence.known_devices) == 0

    def test_handle_presence_wrong_message_type(self):
        """Test handling non-presence message type."""
        presence = NetworkPresence("test-device")

        message = {
            "type": "NOT_PRESENCE",
            "device_id": "remote-device",
            "port": 8080
        }
        data = json.dumps(message).encode('utf-8')
        address = "192.168.1.100"

        presence._handle_presence(address, data)

        # Should ignore non-presence messages
        assert len(presence.known_devices) == 0

    def test_cleanup_old_devices(self):
        """Test cleanup of old/stale devices."""
        presence = NetworkPresence("test-device")

        # Add devices with different last_seen times
        current_time = time.time()
        presence.known_devices = {
            "recent": DeviceInfo("192.168.1.100", 8080, current_time - 10, {}),
            "old": DeviceInfo("192.168.1.101", 8081, current_time - 100, {}),  # Old
        }

        presence._cleanup_old_devices(timeout=50)  # 50 second timeout

        # Only recent device should remain
        assert len(presence.known_devices) == 1
        assert "recent" in presence.known_devices
        assert "old" not in presence.known_devices

    def test_cleanup_old_devices_default_timeout(self):
        """Test cleanup with default timeout (3x presence_interval)."""
        presence = NetworkPresence("test-device", presence_interval=10)

        current_time = time.time()
        presence.known_devices = {
            "recent": DeviceInfo("192.168.1.100", 8080, current_time - 10, {}),
            "old": DeviceInfo("192.168.1.101", 8081, current_time - 40, {}),  # Older than 30 seconds
        }

        presence._cleanup_old_devices()  # Default timeout = 30 seconds

        # Only recent device should remain
        assert len(presence.known_devices) == 1
        assert "recent" in presence.known_devices

    @patch('atmosphere_audio.core.network.time.sleep')
    def test_announce_loop_error_handling(self, mock_sleep):
        """Test error handling in announce loop."""
        presence = NetworkPresence("test-device")

        # Mock _announce_presence to raise an exception
        original_announce = presence._announce_presence
        presence._announce_presence = MagicMock(side_effect=socket.error("Network error"))

        # Set running to True, then False to exit loop quickly
        presence.running = True

        # Mock time.sleep to avoid long waits
        def side_effect(seconds):
            if seconds == 0.5:
                presence.running = False  # Exit after first sleep
        mock_sleep.side_effect = side_effect

        presence._announce_loop()

        # Should have attempted to announce presence
        presence._announce_presence.assert_called_once()

        # Restore original method
        presence._announce_presence = original_announce

    @patch('atmosphere_audio.core.network.socket.socket')
    def test_listen_loop_socket_creation(self, mock_socket_class):
        """Test socket creation in listen loop."""
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock

        presence = NetworkPresence("test-device")

        # Mock running to False to exit immediately
        presence.running = False

        presence._listen_loop()

        # Verify socket was created and configured
        mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
        mock_sock.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mock_sock.bind.assert_called_once_with(("0.0.0.0", 37020))
        mock_sock.settimeout.assert_called_once_with(1.0)
        mock_sock.close.assert_called_once()
