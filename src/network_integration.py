<<<<<<< HEAD
"""
Network integration module for Atmosphere
Provides device discovery and network coordination functionality
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import time
=======
#!/usr/bin/env python3
"""
Atmosphere Network Integration Module

Integrates NetworkPresence device discovery with the broader Atmosphere platform,
including security monitoring, service coordination, and distributed operations.
"""

import json
import logging
import socket
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from .network import DeviceInfo, NetworkPresence
from .security import security_logger

logger = logging.getLogger(__name__)
>>>>>>> 94e7240e4017e5ff163804c12cc582d2f8092628


@dataclass
class AtmosphereDevice:
<<<<<<< HEAD
    """Represents a device in the Atmosphere network"""
=======
    """Extended device information for Atmosphere ecosystem."""

>>>>>>> 94e7240e4017e5ff163804c12cc582d2f8092628
    device_id: str
    address: str
    port: int
    last_seen: float
<<<<<<< HEAD
    device_type: str = "unknown"
    capabilities: List[str] = None
    services: Dict[str, str] = None
    ecosystem_version: str = "1.0.0"
    metadata: dict = None
    version: str = "1.0.0"
    ecosystem_id: str = ""
=======
    device_type: str = "unknown"  # atmosphere, monitor, client, etc.
    capabilities: List[str] = None  # services offered
    ecosystem_version: str = "unknown"
    services: Dict[str, Any] = None
    metadata: Dict[str, Any] = None
>>>>>>> 94e7240e4017e5ff163804c12cc582d2f8092628

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []
        if self.services is None:
            self.services = {}
        if self.metadata is None:
            self.metadata = {}

<<<<<<< HEAD
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
=======

class AtmosphereNetworkCoordinator:
    """Coordinates network presence across the Atmosphere ecosystem."""

    def __init__(
        self,
        device_id: str,
        device_type: str = "atmosphere",
        capabilities: List[str] = None,
    ):
        self.device_id = device_id
        self.device_type = device_type
        self.capabilities = capabilities or ["monitoring"]
        self.ecosystem_version = "1.0.0"

        # Initialize network presence
        self.network_presence = NetworkPresence(
            device_id=device_id, broadcast_port=37020, presence_interval=30
        )

        # Enhanced device tracking
        self.atmosphere_devices: Dict[str, AtmosphereDevice] = {}
        self._device_lock = threading.Lock()

        # Service discovery callbacks
        self._service_callbacks: Dict[str, List[Callable]] = {}

        # Start monitoring thread
        self._running = False
        self._monitor_thread = None

        logger.info(
            f"Atmosphere Network Coordinator initialized: {device_id} ({device_type})"
        )

    def start(self):
        """Start the network coordinator."""
        if self._running:
            return

        self._running = True
        self.network_presence.start()

        # Start device monitoring thread
        self._monitor_thread = threading.Thread(
            target=self._monitor_devices, daemon=True, name="AtmosphereNetwork-Monitor"
        )
        self._monitor_thread.start()

        logger.info("Atmosphere Network Coordinator started")

    def stop(self):
        """Stop the network coordinator."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2.0)
        self.network_presence.stop()
        logger.info("Atmosphere Network Coordinator stopped")

    def _monitor_devices(self):
        """Monitor and enhance device information."""
        while self._running:
            try:
                # Get basic device info from NetworkPresence
                basic_devices = self.network_presence.get_devices()

                with self._device_lock:
                    # Update our enhanced device tracking
                    for device_id, info in basic_devices.items():
                        if device_id not in self.atmosphere_devices:
                            # New device discovered
                            self._enhance_device_info(device_id, info)
                        else:
                            # Update existing device
                            self._update_device_info(device_id, info)

                    # Check for service callbacks
                    self._trigger_service_callbacks()

                    # Clean up old devices
                    self._cleanup_old_devices()

            except Exception as e:
                logger.error(f"Error in device monitoring: {e}")

            time.sleep(5)  # Check every 5 seconds

    def _enhance_device_info(self, device_id: str, basic_info: Dict[str, Any]):
        """Enhance basic device info with Atmosphere-specific details."""
        # Try to connect and get more information
        device = AtmosphereDevice(
            device_id=device_id,
            address=basic_info["address"],
            port=basic_info["port"],
            last_seen=basic_info["last_seen"],
            metadata=basic_info,
        )

        # Attempt to query device for Atmosphere-specific information
        enhanced_info = self._query_device_capabilities(device)
        if enhanced_info:
            device.device_type = enhanced_info.get("device_type", "unknown")
            device.capabilities = enhanced_info.get("capabilities", [])
            device.ecosystem_version = enhanced_info.get("version", "unknown")
            device.services = enhanced_info.get("services", {})

        self.atmosphere_devices[device_id] = device
        logger.info(f"Enhanced device info: {device_id} ({device.device_type})")

    def _query_device_capabilities(
        self, device: AtmosphereDevice
    ) -> Optional[Dict[str, Any]]:
        """Query a device for Atmosphere-specific capabilities."""
        try:
            # Attempt to connect to device's info endpoint
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2.0)

            sock.connect((device.address, device.port))
            sock.send(b"GET /api/info HTTP/1.0\r\nHost: localhost\r\n\r\n")

            response = sock.recv(4096).decode("utf-8")
            sock.close()

            # Parse response (simplified)
            if "HTTP/1." in response and "200 OK" in response:
                # Extract JSON from response body
                body_start = response.find("\r\n\r\n")
                if body_start > 0:
                    body = response[body_start + 4 :]
                    try:
                        return json.loads(body)
                    except json.JSONDecodeError:
                        pass

        except (socket.error, OSError, ValueError) as e:
            logger.debug(f"Could not query device {device.device_id}: {e}")

        return None

    def _update_device_info(self, device_id: str, basic_info: Dict[str, Any]):
        """Update existing device information."""
        if device_id in self.atmosphere_devices:
            device = self.atmosphere_devices[device_id]
            device.last_seen = basic_info["last_seen"]
            device.metadata.update(basic_info)

    def _trigger_service_callbacks(self):
        """Trigger callbacks for discovered services."""
        for service_type, callbacks in self._service_callbacks.items():
            available_devices = [
                device
                for device in self.atmosphere_devices.values()
                if service_type in device.capabilities
            ]

            for callback in callbacks:
                try:
                    callback(available_devices)
                except Exception as e:
                    logger.error(f"Error in service callback for {service_type}: {e}")

    def _cleanup_old_devices(self, timeout: float = 300.0):  # 5 minutes
        """Remove devices we haven't heard from recently."""
        now = time.time()
        old_devices = []

        with self._device_lock:
            for device_id, device in self.atmosphere_devices.items():
                if now - device.last_seen > timeout:
                    old_devices.append(device_id)

            for device_id in old_devices:
                del self.atmosphere_devices[device_id]
                logger.info(f"Removed stale device: {device_id}")

    def register_service_callback(self, service_type: str, callback: Callable):
        """Register a callback for when devices with specific services are discovered."""
        if service_type not in self._service_callbacks:
            self._service_callbacks[service_type] = []
        self._service_callbacks[service_type].append(callback)
        logger.info(f"Registered callback for service: {service_type}")

    def get_atmosphere_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all discovered Atmosphere devices."""
        with self._device_lock:
            return {
                dev_id: asdict(device)
                for dev_id, device in self.atmosphere_devices.items()
            }

    def get_devices_by_capability(self, capability: str) -> List[AtmosphereDevice]:
        """Get devices that have a specific capability."""
        with self._device_lock:
            return [
                device
                for device in self.atmosphere_devices.values()
                if capability in device.capabilities
            ]

    def get_service_endpoints(self, service_name: str) -> List[Dict[str, Any]]:
        """Get endpoints for a specific service across all devices."""
        endpoints = []
        with self._device_lock:
            for device in self.atmosphere_devices.values():
                if service_name in device.services:
                    service_info = device.services[service_name]
                    endpoints.append(
                        {
                            "device_id": device.device_id,
                            "address": device.address,
                            "port": service_info.get("port", device.port),
                            "endpoint": service_info.get(
                                "endpoint", f"/{service_name}"
                            ),
                            "capabilities": service_info.get("capabilities", []),
                        }
                    )
        return endpoints

    def broadcast_service_request(
        self, service_type: str, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Broadcast a service request to all capable devices."""
        capable_devices = self.get_devices_by_capability(service_type)

        if not capable_devices:
            return {"error": f"No devices found with capability: {service_type}"}

        # For now, return information about available devices
        # In a full implementation, this would coordinate the request
        return {
            "service_type": service_type,
            "available_devices": len(capable_devices),
            "devices": [
                {"id": d.device_id, "address": d.address, "port": d.port}
                for d in capable_devices
            ],
            "request_data": request_data,
        }


# Global coordinator instance
_coordinator: Optional[AtmosphereNetworkCoordinator] = None


def initialize_network_coordinator(
    device_id: str, device_type: str = "atmosphere"
) -> AtmosphereNetworkCoordinator:
    """Initialize the global network coordinator."""
    global _coordinator

    if _coordinator is None:
        capabilities = []
        if device_type == "atmosphere":
            capabilities = ["monitoring", "api", "coordination"]
        elif device_type == "monitor":
            capabilities = ["monitoring", "logging"]
        elif device_type == "client":
            capabilities = ["client", "requests"]

        _coordinator = AtmosphereNetworkCoordinator(
            device_id=device_id, device_type=device_type, capabilities=capabilities
        )

    return _coordinator


def get_network_coordinator() -> Optional[AtmosphereNetworkCoordinator]:
    """Get the global network coordinator instance."""
    return _coordinator


def start_network_coordination():
    """Start the global network coordinator."""
    if _coordinator:
        _coordinator.start()


def stop_network_coordination():
    """Stop the global network coordinator."""
    if _coordinator:
        _coordinator.stop()


# Convenience functions
def get_atmosphere_devices():
    """Get all discovered Atmosphere devices."""
    return _coordinator.get_atmosphere_devices() if _coordinator else {}


def get_service_endpoints(service_name: str):
    """Get endpoints for a specific service."""
    return _coordinator.get_service_endpoints(service_name) if _coordinator else []


def broadcast_service_request(service_type: str, request_data: Dict[str, Any]):
    """Broadcast a service request."""
    return (
        _coordinator.broadcast_service_request(service_type, request_data)
        if _coordinator
        else {"error": "No coordinator initialized"}
    )
>>>>>>> 94e7240e4017e5ff163804c12cc582d2f8092628
