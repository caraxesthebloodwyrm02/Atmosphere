"""
Basic Usage Examples for Atmosphere Audio

This file demonstrates how to use the main components of the atmosphere-audio package.
"""

# Import the main package
import atmosphere_audio

# Import specific modules
from atmosphere_audio.delay import Delay
from atmosphere_audio.reverb import SpatialAudioVisualizer
from atmosphere_audio.routing import AcousticParameters, AcousticRoutingNetwork
from atmosphere_audio.core.network import NetworkPresence, DeviceInfo
import numpy as np
import time


def main():
    """Demonstrate basic usage of the atmosphere-audio package."""
    
    print(f"Atmosphere Audio v{atmosphere_audio.__version__}")
    print("=" * 50)
    
    # 1. Delay Effect Example
    print("\n1. Delay Effect Example:")
    print("-" * 30)
    
    delay = Delay(
        time_ms=500,
        feedback=0.4,
        level=0.6,
        dry_wet=0.3,
        delay_type="digital"
    )
    
    print(f"Created delay effect with:")
    print(f"  - Time: {delay.time_ms}ms")
    print(f"  - Feedback: {delay.feedback}")
    print(f"  - Level: {delay.level}")
    print(f"  - Dry/Wet: {delay.dry_wet}")
    print(f"  - Type: {delay.delay_type}")
    
    # 2. Spatial Audio Visualization Example
    print("\n2. Spatial Audio Visualization Example:")
    print("-" * 40)
    
    visualizer = SpatialAudioVisualizer()
    print(f"Created spatial audio visualizer with:")
    print(f"  - Sample rate: {visualizer.sample_rate} Hz")
    print(f"  - Sound speed: {visualizer.sound_speed} m/s")
    
    # Generate a test signal
    signal, t = visualizer.generate_signal(frequency=440, duration=1.0)
    print(f"Generated test signal:")
    print(f"  - Frequency: 440 Hz")
    print(f"  - Duration: 1.0 second")
    print(f"  - Samples: {len(signal)}")
    
    # 3. Acoustic Routing Example
    print("\n3. Acoustic Routing Example:")
    print("-" * 30)
    
    # Create acoustic parameters
    params = AcousticParameters(
        delay_time=100,
        feedback=0.5,
        decay=0.3,
        reverb_density=0.7
    )
    
    print(f"Created acoustic parameters:")
    print(f"  - Delay time: {params.delay_time}ms")
    print(f"  - Feedback: {params.feedback}")
    print(f"  - Decay: {params.decay}")
    print(f"  - Reverb density: {params.reverb_density}")
    
    # Create routing network
    network = AcousticRoutingNetwork()
    print(f"Created acoustic routing network:")
    print(f"  - Nodes: {len(network.graph.nodes)}")
    print(f"  - Edges: {len(network.graph.edges)}")
    
    # 4. Network Presence Example
    print("\n4. Network Presence Example:")
    print("-" * 30)
    
    # Create network presence handler
    presence = NetworkPresence(
        device_id="demo_device",
        broadcast_port=37020,
        presence_interval=30
    )
    
    print(f"Created network presence handler:")
    print(f"  - Device ID: {presence.device_id}")
    print(f"  - Broadcast port: {presence.broadcast_port}")
    print(f"  - Presence interval: {presence.presence_interval}s")
    
    # Create a device info
    device = DeviceInfo(
        address="192.168.1.100",
        port=8080,
        last_seen=time.time(),
        metadata={
            "name": "Demo Device",
            "capabilities": ["delay", "reverb", "routing"],
            "version": "0.1.0"
        }
    )
    
    print(f"\nCreated device info:")
    print(f"  - Address: {device.address}:{device.port}")
    print(f"  - Name: {device.metadata['name']}")
    print(f"  - Capabilities: {device.metadata['capabilities']}")
    print(f"  - Version: {device.metadata['version']}")
    
    print("\n" + "=" * 50)
    print("All examples completed successfully!")
    print("=" * 50)


if __name__ == "__main__":
    main()
