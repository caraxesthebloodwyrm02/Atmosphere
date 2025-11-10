"""
Network Presence Demo

This script demonstrates the basic usage of the NetworkPresence class
for device discovery and presence announcement.
"""

import random
import sys
import time
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))
from src.network import NetworkPresence

def main():
    """Run the network presence demonstration.
    
    This function initializes the NetworkPresence service with a random device ID,
    starts the service, and continuously displays discovered devices on the network.
    """
    # Generate a unique device ID (in a real app, this would be persistent)
    device_id = f"device-{random.randint(1000, 9999)}"

    print(f"Starting network presence as {device_id}")
    print("Press Ctrl+C to exit\n")

    # Create and start the network presence service
    net = NetworkPresence(
        device_id=device_id,
        broadcast_port=37020,
        presence_interval=10  # Announce every 10 seconds
    )

    try:
        net.start()

        while True:
            # Get and display discovered devices
            devices = net.get_devices()

            print("\n" + "=" * 50)
            print(f"{device_id} - Discovered {len(devices)} devices:")
            for dev_id, info in devices.items():
                age = time.time() - info['last_seen']
                print(f"  - {dev_id} at {info['address']}:{info['port']} "
                      f"({age:.1f}s ago)")

            # Wait before next update
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        net.stop()

if __name__ == "__main__":
    main()