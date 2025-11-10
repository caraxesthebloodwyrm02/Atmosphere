"""
Comprehensive tests for network module.
Tests NetworkPresence and DeviceInfo classes with mocked sockets.
"""

import json
import socket
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

    @patch('time.sleep')
    @patch('threading.Thread')
    def test_stop_waits_for_threads(self, mock_thread_class, mock_sleep):
        """Test stop() waits for threads to finish."""
        # Create a mock thread that will be alive for a few iterations
        class MockThread:
            def __init__(self, target=None, name=None):
                self.target = target
                self.name = name
                self.call_count = 0
                self.is_alive_count = 3  # Will be alive for 3 calls
                self._is_alive = True
                
            def is_alive(self):
                self.call_count += 1
                if self.call_count < self.is_alive_count:
                    return True
                self._is_alive = False
                return False
                
            def join(self, timeout=None):
                if self.target and self._is_alive:
                    self.target()
        
        # Create instance and set up test conditions
        presence = NetworkPresence("device-1")
        presence.running = True
        
        # Create mock threads
        mock_announce_thread = MockThread(target=presence._announce_loop, name=f"NetworkAnnounce-{presence.device_id}")
        mock_listen_thread = MockThread(target=presence._listen_loop, name=f"NetworkListen-{presence.device_id}")
        
        # Set thread daemon to False to match implementation
        mock_announce_thread.daemon = False
        mock_listen_thread.daemon = False
        
        presence._announce_thread = mock_announce_thread
        presence._listen_thread = mock_listen_thread
        
        # Create a mock socket for the listen socket
        mock_listen_socket = MagicMock()
        presence._socket = mock_listen_socket
        
        # Create a mock for the broadcast socket
        mock_broadcast_socket = MagicMock()
        
        # Patch socket.socket to return our mock broadcast socket
        with patch('socket.socket') as mock_socket_class:
            mock_socket_class.return_value = mock_broadcast_socket
            
            # Call stop - this should wait for threads to finish
            presence.stop()
            
            # Verify threads were checked multiple times
            assert mock_announce_thread.call_count > 1
            assert mock_listen_thread.call_count > 1
            
            # Verify the listen socket was closed
            mock_listen_socket.close.assert_called_once()
            
            # Verify the broadcast socket was closed
            mock_broadcast_socket.close.assert_called_once()


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
        assert devices["device-2"]["metadata"] == metadata

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
    @patch('socket.getaddrinfo')
    def test_announce_presence_creates_socket(self, mock_getaddrinfo, mock_hostname, mock_socket_class):
        """Test _announce_presence creates socket."""
        # Mock getaddrinfo to return a dummy address
        mock_getaddrinfo.return_value = [
            (socket.AF_INET, socket.SOCK_DGRAM, 17, '', ('8.8.8.8', 80))
        ]
        
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Mock the socket context manager methods
        mock_socket.__enter__.return_value = mock_socket
        mock_socket.__exit__.return_value = None
        
        # Mock getsockname to return a dummy address
        mock_socket.getsockname.return_value = ('192.168.1.1', 12345)
        
        # Create a separate mock for the broadcast socket
        mock_broadcast_socket = MagicMock()
        mock_broadcast_socket.__enter__.return_value = mock_broadcast_socket
        mock_broadcast_socket.__exit__.return_value = None
        
        # Make the socket constructor return different mocks for different calls
        mock_socket_class.side_effect = [mock_socket, mock_broadcast_socket]
        
        presence = NetworkPresence("device-1")
        presence._announce_presence()
        
        # Verify sockets were created with the correct parameters
        assert mock_socket_class.call_count == 2
        
        # First call is for getting the local IP
        assert mock_socket_class.call_args_list[0][0] == (socket.AF_INET, socket.SOCK_DGRAM)
        
        # Second call is for the broadcast socket
        assert mock_socket_class.call_args_list[1][0] == (socket.AF_INET, socket.SOCK_DGRAM)
        
        # Verify socket options were set correctly on the broadcast socket
        mock_broadcast_socket.setsockopt.assert_called_once_with(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            1
        )
        
        # Verify the broadcast message was sent
        mock_broadcast_socket.sendto.assert_called_once()

    @patch("socket.socket")
    @patch("socket.gethostname")
    @patch('time.time', return_value=1234567890.0)
    def test_announce_presence_sends_message(self, mock_time, mock_hostname, mock_socket_class):
        """Test _announce_presence sends message."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Mock the socket context manager methods
        mock_socket.__enter__.return_value = mock_socket
        mock_socket.__exit__.return_value = None
        
        presence = NetworkPresence("device-1", broadcast_port=37020)
        presence._announce_presence()
        
        # Verify socket was configured correctly
        mock_socket.setsockopt.assert_called_once_with(
            socket.SOL_SOCKET, 
            socket.SO_BROADCAST, 
            1
        )
        
        # Verify sendto was called with the correct arguments
        expected_message = {
            "type": "PRESENCE",
            "device_id": "device-1",
            "timestamp": 1234567890.0,
            "port": 37020,
            "metadata": {}
        }
        
        mock_socket.sendto.assert_called_once()
        
        # Get the actual message that was sent
        call_args = mock_socket.sendto.call_args[0]
        message_bytes = call_args[0]
        message = json.loads(message_bytes.decode('utf-8'))
        
        # Verify the message content
        assert message == expected_message
        
        # Verify the message was sent to the broadcast address
        assert mock_socket.sendto.call_args[0][1] == ('<broadcast>', 37020)
        
        # Verify the socket was closed
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_presence_closes_socket(self, mock_hostname, mock_socket_class):
        """Test _announce_presence closes socket."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Mock the socket context manager methods
        mock_socket.__enter__.return_value = mock_socket
        mock_socket.__exit__.return_value = None
        
        presence = NetworkPresence("device-1")
        presence._announce_presence()
        
        # Verify the socket was properly closed
        mock_socket.close.assert_called_once()
        
        # Verify the socket was used as a context manager
        mock_socket.__enter__.assert_called_once()
        mock_socket.__exit__.assert_called_once()

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_presence_handles_socket_error(self, mock_hostname, mock_socket_class):
        """Test _announce_presence handles socket errors."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Make sendto raise an exception
        mock_socket.sendto.side_effect = OSError("Network error")
        
        # Mock the socket context manager methods
        mock_socket.__enter__.return_value = mock_socket
        mock_socket.__exit__.return_value = None
        
        presence = NetworkPresence("device-1")
        
        # Should not raise exception
        presence._announce_presence()
        
        # Verify the socket was still closed even if there was an error
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    @patch("socket.gethostname")
    def test_announce_presence_sets_broadcast_option(self, mock_hostname, mock_socket_class):
        """Test _announce_presence sets broadcast socket option."""
        mock_hostname.return_value = "test-host"
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        
        # Mock the socket context manager methods
        mock_socket.__enter__.return_value = mock_socket
        mock_socket.__exit__.return_value = None
        
        presence = NetworkPresence("device-1")
        presence._announce_presence()
        
        # Verify setsockopt was called with the correct parameters
        mock_socket.setsockopt.assert_called_once_with(
            socket.SOL_SOCKET,
            socket.SO_BROADCAST,
            1
        )


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

    @patch('src.network.logger')
    @patch('time.sleep')
    def test_announce_loop_handles_errors(self, mock_sleep, mock_logger):
        """Test _announce_loop handles errors gracefully."""
        # Create a side effect that will raise an error on first call,
        # then set running to False on second call to exit the loop
        side_effects = [
            OSError("Network error"),  # First call raises error
            None,                      # Second call allows loop to exit
        ]
        
        # Create a mock for _announce_presence that will use our side effects
        with patch.object(NetworkPresence, '_announce_presence') as mock_announce:
            mock_announce.side_effect = side_effects
            
            # Create instance and set up test conditions
            presence = NetworkPresence("device-1", presence_interval=0.1)
            presence.running = True
            
            # Run the loop (it should exit after the second call)
            presence._announce_loop()
            
            # Verify _announce_presence was called twice
            assert mock_announce.call_count == 2
            
            # Verify the error was logged
            mock_logger.error.assert_called_once_with("Error in announcement loop: Network error")


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
            device_id = f"device-{i}"
            assert device_id in devices
            assert isinstance(devices[device_id], dict)
            assert devices[device_id]['address'] == f"192.168.1.{100+i}"
            assert devices[device_id]['port'] == 37021 + i
            assert devices[device_id]['metadata'] == {"id": i}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
