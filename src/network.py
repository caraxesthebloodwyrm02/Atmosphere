"""
Network module for Atmosphere
Provides basic network presence and device information functionality
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Union
import time
import socket
import threading
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Information about a network device"""
    address: str  # IP address
    port: int
    hostname: Optional[str] = None
    ip_address: Optional[str] = None  # Alias for address
    device_type: str = "atmosphere_device"
    capabilities: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    last_seen: float = field(default_factory=time.time)

    def __post_init__(self):
        if self.ip_address is None:
            self.ip_address = self.address
        if self.hostname is None:
            self.hostname = f"device_{self.address.replace('.', '_')}"

    def update_last_seen(self):
        """Update the last seen timestamp to now"""
        self.last_seen = time.time()

    def to_dict(self) -> Dict[str, Any]:
        """Convert device info to a dictionary"""
        return {
            'address': self.address,
            'port': self.port,
            'hostname': self.hostname,
            'device_type': self.device_type,
            'capabilities': self.capabilities,
            'metadata': self.metadata,
            'last_seen': self.last_seen
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeviceInfo':
        """Create DeviceInfo from a dictionary"""
        return cls(
            address=data.get('address'),
            port=data.get('port'),
            hostname=data.get('hostname'),
            device_type=data.get('device_type', 'atmosphere_device'),
            capabilities=data.get('capabilities', []),
            metadata=data.get('metadata', {}),
            last_seen=data.get('last_seen', time.time())
        )


class NetworkPresence:
    """
    Manages network presence and device discovery.
    
    This class handles device discovery, presence announcements, and maintains
    a list of known devices on the network.
    """
    
    def __init__(self, device_id: str = None, broadcast_port: int = 37020, presence_interval: int = 30):
        """
        Initialize the NetworkPresence manager.
        
        Args:
            device_id: Unique identifier for this device. If None, one will be generated.
            broadcast_port: UDP port to use for presence announcements.
            presence_interval: How often to send presence announcements (in seconds).
        """
        self.device_id = device_id or f"device_{socket.gethostname()}"
        self.broadcast_port = broadcast_port
        self.presence_interval = presence_interval
        
        # Device storage
        self.known_devices: Dict[str, DeviceInfo] = {}
        self.devices = self.known_devices  # Alias for backward compatibility
        
        # Network info
        self.local_hostname = socket.gethostname()
        self.local_ip = self._get_local_ip()
        
        # Thread control
        self._running = False
        self._announce_thread: Optional[threading.Thread] = None
        self._listen_thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        
        # Socket for sending/receiving announcements
        self._socket: Optional[socket.socket] = None

    def _get_local_ip(self) -> str:
        """
        Get the local IP address that can be used for communication.
        
        Returns:
            The local IP address as a string, or '127.0.0.1' if detection fails.
        """
        try:
            # Try to connect to a public DNS server to determine the best interface
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except Exception as e:
            logger.warning(f"Could not determine local IP address: {e}")
            return "127.0.0.1"

    def register_device(self, device_info: DeviceInfo, device_id: str = None) -> bool:
        """
        Register a device in the network.
        
        Args:
            device_info: The DeviceInfo object to register
            device_id: Optional device ID. If not provided, will be generated.
            
        Returns:
            bool: True if device was registered, False if it already exists
        """
        device_id = device_id or getattr(device_info, 'device_id', None) or f"{device_info.hostname}_{device_info.port}"
        
        with self._lock:
            if device_id in self.known_devices:
                return False
                
            # Ensure the device has the correct ID
            device_info.device_id = device_id
            self.known_devices[device_id] = device_info
            logger.debug(f"Registered device: {device_id}")
            return True

    def unregister_device(self, device_id: str) -> bool:
        """
        Remove a device from the network.
        
        Args:
            device_id: The ID of the device to remove
            
        Returns:
            bool: True if device was removed, False if it didn't exist
        """
        with self._lock:
            if device_id in self.known_devices:
                del self.known_devices[device_id]
                logger.debug(f"Unregistered device: {device_id}")
                return True
            return False

    def get_device(self, device_id: str) -> Optional[DeviceInfo]:
        """
        Get device information by device_id.
        
        Args:
            device_id: The ID of the device to retrieve
            
        Returns:
            Optional[DeviceInfo]: The device info if found, None otherwise
        """
        with self._lock:
            return self.known_devices.get(device_id)

    def get_devices(self) -> Dict[str, Dict]:
        """
        Get all devices as a dictionary of device_id to device info dictionaries.
        
        Returns:
            Dict[str, Dict]: Dictionary mapping device IDs to device info dictionaries
        """
        with self._lock:
            self._cleanup_old_devices()
            # Convert DeviceInfo objects to dictionaries
            return {
                dev_id: {
                    'address': dev_info.address,
                    'port': dev_info.port,
                    'hostname': dev_info.hostname,
                    'ip_address': dev_info.ip_address,
                    'device_type': dev_info.device_type,
                    'capabilities': dev_info.capabilities,
                    'metadata': dev_info.metadata,
                    'last_seen': dev_info.last_seen
                }
                for dev_id, dev_info in self.known_devices.items()
            }
    
    def get_all_devices(self) -> List[DeviceInfo]:
        """
        Get all registered devices as a list.
        
        Returns:
            List[DeviceInfo]: List of all known devices
        """
        with self._lock:
            self._cleanup_old_devices()
            return list(self.known_devices.values())
    
    # Alias for backward compatibility
    get_devices_dict = get_devices

    def _announce_presence(self):
        """
        Broadcast a presence announcement to the network.
        
        This method creates a new socket, sets the broadcast option,
        sends the announcement, and then closes the socket.
        """
        sock = None
        try:
            # Create a new socket for each announcement to avoid issues with socket reuse
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # Enable broadcast
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            
            # Prepare the announcement message
            message = {
                "type": "PRESENCE",
                "device_id": self.device_id,
                "timestamp": time.time(),
                "port": self.broadcast_port,
                "metadata": {}
            }
            
            # Send the message to the broadcast address
            sock.sendto(
                json.dumps(message).encode('utf-8'),
                ('<broadcast>', self.broadcast_port)
            )
            
            logger.debug(f"Sent presence announcement: {message}")
            
        except Exception as e:
            logger.error(f"Error sending presence announcement: {e}")
        finally:
            if sock:
                sock.close()
            return False

    # Alias for backward compatibility
    broadcast_presence = _announce_presence

    def discover_devices(self, timeout: float = 5.0) -> List[DeviceInfo]:
        """
        Discover devices on the network.
        
        Note: This is a placeholder implementation. In a real implementation,
        this would actively scan the network for devices.
        
        Args:
            timeout: Timeout in seconds (not currently used)
            
        Returns:
            List[DeviceInfo]: List of discovered devices
        """
        # Just return the current list of known devices
        return self.get_all_devices()

    def _cleanup_old_devices(self, timeout: int = 300) -> int:
        """
        Remove devices that haven't been seen recently.
        
        Args:
            timeout: Number of seconds after which a device is considered stale
            
        Returns:
            int: Number of devices removed
        """
        if not self._running:
            return 0
            
        now = time.time()
        removed = 0
        
        with self._lock:
            # Find and remove stale devices
            stale_devices = [
                dev_id for dev_id, dev in self.known_devices.items()
                if now - dev.last_seen > timeout
            ]
            
            for dev_id in stale_devices:
                if dev_id in self.known_devices:
                    del self.known_devices[dev_id]
                    removed += 1
                    logger.info(f"Removed stale device: {dev_id}")
        
        return removed
        
    # Alias for backward compatibility
    cleanup_stale_devices = _cleanup_old_devices
        
    def _announce_presence(self):
        """Announce presence to the network (internal method)"""
        return self.broadcast_presence()
        
    def _announce_loop(self):
        """
        Continuously broadcast presence announcements at regular intervals.
        
        This runs in a separate thread started by the start() method.
        """
        logger.info("Starting announcement loop")
        
        while self._running:
            try:
                self._announce_presence()
                self._cleanup_old_devices()
            except Exception as e:
                logger.error(f"Error in announcement loop: {e}")
            
            # Sleep in small increments to be responsive to shutdown
            sleep_interval = 0.1  # 100ms
            total_sleep = 0
            
            while total_sleep < self.presence_interval and self._running:
                time.sleep(sleep_interval)
                total_sleep += sleep_interval
                
            if not self._running:
                logger.info("Announcement loop stopped")
                return
    
    def start(self):
        """
        Start the network presence service.
        
        This will start two background threads:
        1. Announcement thread: Periodically broadcasts our presence
        2. Listen thread: Listens for presence announcements from other devices
        """
        if self._running:
            logger.warning("Network presence service is already running")
            return
            
        logger.info(f"Starting network presence service for device: {self.device_id}")
        self._running = True
        
        try:
            # Create the socket for listening first
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._socket.bind(('0.0.0.0', self.broadcast_port))
            
            # Start announcement thread
            self._announce_thread = threading.Thread(
                target=self._announce_loop,
                daemon=True,
                name=f"NetworkAnnounce-{self.device_id}"
            )
            self._announce_thread.start()
            
            # Start listen thread
            self._listen_thread = threading.Thread(
                target=self._listen_loop,
                daemon=True,
                name=f"NetworkListen-{self.device_id}"
            )
            self._listen_thread.start()
            
            logger.info("Network presence service started")
            
        except Exception as e:
            self._running = False
            if hasattr(self, '_socket') and self._socket:
                try:
                    self._socket.close()
                except Exception as close_error:
                    logger.warning(f"Error closing socket: {close_error}")
                self._socket = None
            logger.error(f"Failed to start network presence service: {e}")
            raise
    
    def _listen_loop(self):
        """
        Main loop for listening to incoming presence announcements.
        
        This runs in a separate thread started by the start() method.
        """
        logger.info("Starting listen loop")
        
        # Create a socket for listening
        try:
            listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            listen_socket.bind(('0.0.0.0', self.broadcast_port))
            listen_socket.settimeout(1.0)  # Allow for periodic checking of self._running
            
            while self._running:
                try:
                    data, addr = listen_socket.recvfrom(1024)
                    self._handle_presence_announcement(data, addr)
                except socket.timeout:
                    continue
                except OSError as e:
                    if self._running:  # Only log if we didn't expect this error
                        logger.error(f"Socket error in listen loop: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error in listen loop: {e}")
        finally:
            if listen_socket:
                listen_socket.close()
                    
        logger.info("Listen loop stopped")

        
        # Create a socket for listening
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            self._socket.bind(('0.0.0.0', self.broadcast_port))
            self._socket.settimeout(1.0)  # Allow for periodic checking of self._running
            
            while self._running:
                try:
                    data, addr = self._socket.recvfrom(1024)
                    self._handle_presence_announcement(data, addr)
                except socket.timeout:
                    continue
                except OSError as e:
                    if self._running:  # Only log if we didn't expect this error
                        logger.error(f"Socket error in listen loop: {e}")
                    break
                except Exception as e:
                    logger.error(f"Error in listen loop: {e}")
        finally:
            if self._socket:
                self._socket.close()
                self._socket = None
                
        logger.info("Listen loop stopped")
    
    def _handle_presence_announcement(self, data: bytes, addr: tuple):
        """
        Process an incoming presence announcement.
        
        Args:
            data: The raw message data received
            addr: Tuple of (ip, port) where the message came from
        """
        try:
            message = json.loads(data.decode('utf-8'))
            
            # Skip if not a presence message or missing required fields
            if message.get('type') != 'PRESENCE' or 'device_id' not in message:
                return
                
            device_id = message['device_id']
            
            # Skip our own announcements
            if device_id == self.device_id:
                return
                
            with self._lock:
                # Get or create the device
                if device_id in self.known_devices:
                    # Update existing device
                    device = self.known_devices[device_id]
                    device.address = message.get('ip_address', addr[0])
                    device.port = message.get('port', addr[1])
                    device.hostname = message.get('hostname', f"device_{device_id}")
                    device.last_seen = time.time()
                else:
                    # Create new device
                    device = DeviceInfo(
                        address=message.get('ip_address', addr[0]),
                        port=message.get('port', addr[1]),
                        hostname=message.get('hostname', f"device_{device_id}"),
                        last_seen=time.time()
                    )
                    self.known_devices[device_id] = device
                    logger.info(f"Discovered new device: {device_id} at {device.address}:{device.port}")
            
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON in presence announcement from {addr}: {e}")
        except Exception as e:
            logger.error(f"Error processing presence announcement: {e}")
