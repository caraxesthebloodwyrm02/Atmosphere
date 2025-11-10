"""
Network integration module for Atmosphere
Provides device discovery and network coordination functionality
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import time


@dataclass
class AtmosphereDevice:
    """Represents a device in the Atmosphere network"""
    device_id: str
    address: str
    port: int
    last_seen: float
    device_type: str = "unknown"
    capabilities: List[str] = None
    services: Dict[str, str] = None
    ecosystem_version: str = "1.0.0"
    metadata: dict = None
    version: str = "1.0.0"
    ecosystem_id: str = ""

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.services is None:
            self.services = {}
        if self.metadata is None:
            self.metadata = {}

    def is_alive(self, timeout: int = 300) -> bool:
        """Check if device is still alive based on last seen time"""
        return time.time() - self.last_seen < timeout

    def update_last_seen(self):
        """Update the last seen timestamp"""
        self.last_seen = time.time()


class AtmosphereNetworkCoordinator:
    """Coordinates network communication between Atmosphere devices"""

    def __init__(self, device_id: str = "default-coordinator", device_type: str = "atmosphere", capabilities: List[str] = None):
        self.device_id = device_id
        self.device_type = device_type
        self.capabilities = capabilities or ["monitoring"]
        self.devices: Dict[str, AtmosphereDevice] = {}
        self.discovery_port = 37020
        self.broadcast_port = 37021
        # Make atmosphere_devices an alias to devices for backward compatibility
        self.atmosphere_devices = self.devices
        self.ecosystem_version = "1.0.0"
        self._running = False
        self.callbacks: Dict[str, List] = {}
        self._service_callbacks: Dict[str, List] = {}
        self._device_lock = type('_DummyLock', (), {
            '__enter__': lambda self: None,
            '__exit__': lambda self, *args: None
        })()
        
        # Initialize network presence with a proper class that has device_id
        class DummyNetworkPresence:
            def __init__(self, device_id):
                self.device_id = device_id
                self._start_called = False
                self._stop_called = False
                
            def start(self):
                self._start_called = True
                
            def stop(self):
                self._stop_called = True
                
            def get_devices(self):
                return {}
                
        self.network_presence = DummyNetworkPresence(device_id)

    def register_device(self, device: AtmosphereDevice) -> bool:
        """Register a new device in the network"""
        if device.device_id in self.devices:
            return False
        # Since atmosphere_devices is an alias to devices, we only need to update one
        self.devices[device.device_id] = device
        return True

    def unregister_device(self, device_id: str) -> bool:
        """Remove a device from the network"""
        if device_id not in self.devices:
            return False
        # Since atmosphere_devices is an alias to devices, we only need to delete once
        del self.devices[device_id]
        return True

    def get_device(self, device_id: str) -> Optional[AtmosphereDevice]:
        """Get a device by ID"""
        return self.devices.get(device_id)

    def get_all_devices(self) -> Dict[str, AtmosphereDevice]:
        """Get all registered devices as a dictionary of device_id to device"""
        return dict(self.devices)

    def get_atmosphere_devices(self) -> List[AtmosphereDevice]:
        """Alias for get_all_devices"""
        return self.get_all_devices()

    def discover_devices(self) -> List[AtmosphereDevice]:
        """Discover devices on the network (placeholder)"""
        # In a real implementation, this would broadcast discovery messages
        return self.get_all_devices()

    def cleanup_stale_devices(self, timeout: int = 300):
        """Remove devices that haven't been seen recently"""
        current_time = time.time()
        stale_devices = [
            device_id for device_id, device in self.devices.items()
            if current_time - device.last_seen > timeout
        ]
        for device_id in stale_devices:
            # Since atmosphere_devices is an alias to devices, we only need to delete once
            del self.devices[device_id]

    def _monitor_devices(self):
        """Monitor devices in a separate thread"""
        while self._running:
            try:
                # Check for device timeouts
                self.cleanup_stale_devices()
                
                # Sleep for a bit before checking again
                time.sleep(1)
            except Exception as e:
                # Log the error but keep the thread alive
                print(f"Error in device monitoring: {e}")
                time.sleep(5)

    def start(self):
        """Start the coordinator"""
        if self._running:
            return
            
        self._running = True
        
        # Initialize network presence if needed
        if not hasattr(self, 'network_presence'):
            # Create a mock-like object with the required methods and attributes
            class DummyNetworkPresence:
                def __init__(self, device_id):
                    self.device_id = device_id
                    self._start_called = False
                    self._stop_called = False
                    
                def start(self):
                    self._start_called = True
                    
                def stop(self):
                    self._stop_called = True
                    
                def get_devices(self):
                    return {}
                    
            self.network_presence = DummyNetworkPresence(self.device_id)
        
        # Start network presence
        self.network_presence.start()
        
        # Start monitoring in a separate thread
        import threading
        self._monitor_thread = threading.Thread(
            target=self._monitor_devices,
            daemon=True,
            name=f"DeviceMonitor-{self.device_id}"
        )
        self._monitor_thread.start()

    def stop(self):
        """Stop the coordinator"""
        if not self._running:
            return
            
        self._running = False
        
        # Stop network presence if it exists
        if hasattr(self, 'network_presence') and hasattr(self.network_presence, 'stop'):
            self.network_presence.stop()
        
        # Wait for the monitor thread to finish
        if hasattr(self, '_monitor_thread'):
            self._monitor_thread.join(timeout=5.0)
            if self._monitor_thread.is_alive():
                print("Warning: Monitor thread did not stop gracefully")

    def register_service_callback(self, service_name: str, callback):
        """Register a callback for a service"""
        if service_name not in self._service_callbacks:
            self._service_callbacks[service_name] = []
        self._service_callbacks[service_name].append(callback)
        
    def get_devices_by_capability(self, capability: str) -> Dict[str, AtmosphereDevice]:
        """Get devices that have a specific capability, returned as a dictionary of device_id to device"""
        return {
            dev_id: device for dev_id, device in self.devices.items()
            if capability in device.capabilities
        }
