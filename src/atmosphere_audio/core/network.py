"""
Minimal network presence and discovery module.

This module provides basic device discovery and presence announcement
functionality using UDP broadcast. It's designed to be simple, reliable,
and non-intrusive to existing code.
"""

from __future__ import annotations

import json
import logging
import socket
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Package imports
from atmosphere_audio import __version__

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DeviceInfo:
    """Container for device information."""

    address: str
    port: int
    last_seen: float
    metadata: Dict[str, Any]


class NetworkPresence:
    """Handles network presence announcement and device discovery.

    This class provides a simple way for devices to announce their presence
    on the local network and discover other devices.
    """

    def __init__(
        self, device_id: str, broadcast_port: int = 37020, presence_interval: int = 30
    ):
        """Initialize the network presence handler.

        Args:
            device_id: Unique identifier for this device
            broadcast_port: UDP port for presence announcements
            presence_interval: How often to announce presence (seconds)
        """
        self.device_id = device_id
        self.broadcast_port = broadcast_port
        self.presence_interval = presence_interval
        self.known_devices: Dict[str, DeviceInfo] = {}
        self.running = False
        self._lock = threading.Lock()
        self._announce_thread: Optional[threading.Thread] = None
        self._listen_thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the presence announcement and discovery service."""
        if self.running:
            return

        self.running = True

        # Start presence announcement in background
        self._announce_thread = threading.Thread(
            target=self._announce_loop, daemon=True, name="NetworkPresence-Announce"
        )
        self._announce_thread.start()

        # Start listening for other devices
        self._listen_thread = threading.Thread(
            target=self._listen_loop, daemon=True, name="NetworkPresence-Listen"
        )
        self._listen_thread.start()

        logger.info("Network presence started (ID: %s)", self.device_id)

    def stop(self) -> None:
        """Stop the presence and discovery service."""
        self.running = False

        # Wait for threads to finish
        if hasattr(self, "_announce_thread"):
            self._announce_thread.join(timeout=1.0)
        if hasattr(self, "_listen_thread"):
            self._listen_thread.join(timeout=1.0)

        logger.info("Network presence stopped")

    def get_devices(self) -> Dict[str, Dict[str, Any]]:
        """Get information about discovered devices.

        Returns:
            Dictionary mapping device IDs to their information
        """
        self._cleanup_old_devices()
        with self._lock:
            return {
                dev_id: {
                    "address": info.address,
                    "port": info.port,
                    "last_seen": info.last_seen,
                    **info.metadata,
                }
                for dev_id, info in self.known_devices.items()
            }

    def _announce_loop(self) -> None:
        """Background thread that announces our presence periodically.

        This method runs in a loop while the service is active, sending
        presence announcements at regular intervals and handling any errors
        that might occur during the process.
        """
        while self.running:
            try:
                self._announce_presence()
            except (socket.error, OSError) as e:
                logger.error("Network error in announce loop: %s", e)
                time.sleep(1)  # Brief pause after network errors
            except json.JSONEncodeError as e:
                logger.error("Failed to encode presence message: %s", e)
                break  # Stop the loop if we can't encode messages
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Unexpected error in announce loop: %s", e)
                time.sleep(1)  # Brief pause after unexpected errors

            # Sleep most of the interval, but check running flag frequently
            for _ in range(self.presence_interval * 2):
                if not self.running:
                    return
                time.sleep(0.5)

    def _announce_presence(self) -> None:
        """Broadcast our presence on the network.

        This method creates a UDP socket, constructs a presence message,
        and broadcasts it to the local network. The message includes
        the device ID, timestamp, and metadata.
        """
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            current_time = time.time()
            message = {
                "type": "PRESENCE",
                "device_id": self.device_id,
                "timestamp": current_time,
                "port": self.broadcast_port + 1,  # Use next port for direct comms
                "metadata": {
                    "hostname": socket.gethostname(),
                    "start_time": current_time,
                },
            }

            sock.sendto(
                json.dumps(message, ensure_ascii=False).encode("utf-8"),
                ("<broadcast>", self.broadcast_port),
            )

        except (socket.error, OSError) as e:
            logger.error("Network error announcing presence: %s", e)
        except json.JSONEncodeError as e:
            logger.error("Failed to encode presence message: %s", e)
        except (TypeError, ValueError) as e:
            logger.error("Invalid message format: %s", e)
        except UnicodeEncodeError as e:
            logger.error("Encoding error in presence data: %s", e)
        finally:
            if sock:
                try:
                    sock.close()
                except (socket.error, OSError) as e:
                    logger.debug("Error closing socket: %s", e)

    def _listen_loop(self) -> None:
        """Background thread that listens for presence announcements.

        This method runs in a loop, listening for incoming UDP packets
        on the broadcast port. When a valid presence message is received,
        it's passed to _handle_presence for processing.
        """
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(("0.0.0.0", self.broadcast_port))

            # Set timeout to allow checking self.running periodically
            sock.settimeout(1.0)

            while self.running:
                try:
                    data, addr = sock.recvfrom(1024)
                    if not data:
                        continue
                    self._handle_presence(addr[0], data)
                except socket.timeout:
                    continue
                except (socket.error, OSError) as e:
                    logger.error("Network error in listen loop: %s", e)
                    time.sleep(1)
                except Exception as e:  # pylint: disable=broad-except
                    logger.error("Unexpected error in listen loop: %s", e)
                    time.sleep(1)
        except (socket.error, OSError) as e:
            logger.error("Failed to initialize listening socket: %s", e)
        finally:
            if sock:
                try:
                    sock.close()
                except Exception as e:  # pylint: disable=broad-except
                    logger.debug("Error closing socket: %s", e)

    def _handle_presence(self, address: str, data: bytes) -> None:
        """Handle a presence announcement from another device.

        Args:
            address: The IP address of the device sending the announcement
            data: The raw message data received from the network
        """
        try:
            message = json.loads(data.decode("utf-8"))
            if not isinstance(message, dict) or message.get("type") != "PRESENCE":
                return

            device_id = str(message.get("device_id", ""))
            if not device_id:
                logger.warning("Received presence message with empty device_id")
                return

            # Skip our own messages
            if device_id == self.device_id:
                return

            port = int(message.get("port", self.broadcast_port + 1))
            metadata = dict(message.get("metadata", {}))

            with self._lock:
                if device_id not in self.known_devices:
                    logger.info("Discovered new device: %s at %s", device_id, address)

                self.known_devices[device_id] = DeviceInfo(
                    address=address, port=port, last_seen=time.time(), metadata=metadata
                )

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning("Invalid presence message: %s", e)
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error handling presence from %s: %s", address, e)

    def _cleanup_old_devices(self, timeout: float = None) -> None:
        """Remove devices we haven't heard from in a while.

        Args:
            timeout: Maximum time in seconds since last update before a device
                    is considered stale. If None, defaults to 3x the presence interval.
        """
        if timeout is None:
            timeout = self.presence_interval * 3  # 3x the announcement interval

        now = time.time()
        with self._lock:
            old_count = len(self.known_devices)
            self.known_devices = {
                k: v
                for k, v in self.known_devices.items()
                if now - v.last_seen < timeout
            }

            removed = old_count - len(self.known_devices)
            if removed > 0:
                logger.debug("Cleaned up %d old device(s)", removed)
