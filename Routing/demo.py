"""
Acoustic Routing System Demonstration
=====================================

This script demonstrates the routing system inspired by the U.S. Highway Network
and acoustic principles from Reverb, Echo, and Delay.

Shows:
1. Network construction with acoustic parameters
2. Pulse propagation simulation
3. Route optimization with different criteria
4. Network analysis and visualization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from acoustic_routing import AcousticRoutingNetwork
from us_highway_model import build_us_highway_network, get_highway_characteristics
import matplotlib.pyplot as plt
import numpy as np


def demonstrate_pulse_propagation(network: AcousticRoutingNetwork):
    """Demonstrate pulse propagation from a starting city"""

    print("\n" + "="*60)
    print("PULSE PROPAGATION DEMONSTRATION")
    print("="*60)

    # Start pulse in Delay hub
    start_city = 'Delay'
    print(f"\nStarting acoustic pulse in {start_city}...")

    propagation_history = network.propagate_pulse(start_city, max_steps=20)

    print("Propagation Results:")
    print(f"Initial pulse amplitude: 1.0")

    for step, pulses in enumerate(propagation_history):
        if step == 0:
            continue  # Skip initial state

        active_pulses = [p for p in pulses if p.amplitude > 0.01]
        if not active_pulses:
            print(f"Step {step}: All pulses decayed")
            break

        total_amplitude = sum(p.amplitude for p in active_pulses)
        cities_reached = len(set(p.current_position for p in active_pulses))

        print(f"Step {step}: {len(active_pulses)} active pulses, "
              f"{cities_reached} components reached, "
              f"total amplitude: {total_amplitude:.3f}")
        # Show some example pulses
        if step <= 5:
            for i, pulse in enumerate(active_pulses[:3]):  # Show first 3
                path_str = ' -> '.join(pulse.path_history[-3:])  # Last 3 components
                print(f"  Pulse {i+1}: {path_str} "
                      f"(amplitude: {pulse.amplitude:.3f})")

    print(f"\nPulse propagation completed after {len(propagation_history)-1} steps")


def demonstrate_route_optimization(network: AcousticRoutingNetwork):
    """Show different routing strategies"""

    print("\n" + "="*60)
    print("ROUTE OPTIMIZATION DEMONSTRATION")
    print("="*60)

    routes = [
        ('Delay', 'Routing'),
        ('Trajectory', 'Endpoint'),
        ('Network', 'Echoes'),
        ('Reverb', 'Orchestration')
    ]

    criteria = ['distance', 'delay', 'reverb']

    for start, end in routes:
        print(f"\nRoutes from {start} to {end}:")

        for criterion in criteria:
            route = network.find_optimal_route(start, end, criterion)

            if route:
                # Calculate total metrics
                total_distance = 0
                total_delay = 0
                avg_reverb = 0

                for i in range(len(route)-1):
                    edge = (route[i], route[i+1])
                    params = network.acoustic_params.get(edge)
                    if params:
                        total_distance += network.graph[edge[0]][edge[1]]['weight']
                        total_delay += params.delay_time
                        avg_reverb += params.reverb_density

                if len(route) > 1:
                    avg_reverb /= (len(route) - 1)

                print(f"  {criterion.upper()}: {' -> '.join(route)}")
                print(f"    Distance: {total_distance:.0f} miles, "
                      f"Delay: {total_delay:.0f}ms, "
                      f"Avg Reverb: {avg_reverb:.3f}")
            else:
                print(f"  {criterion.upper()}: No route found")


def demonstrate_network_analysis(network: AcousticRoutingNetwork):
    """Analyze the acoustic properties of the network"""

    print("\n" + "="*60)
    print("NETWORK ACOUSTIC ANALYSIS")
    print("="*60)

    analysis = network.analyze_network_acoustics()

    print("Network Statistics:")
    print(f"- Total highway segments: {analysis['total_segments']}")
    print(f"- Total cities/nodes: {analysis['total_nodes']}")
    print(f"- Average delay: {analysis['avg_delay_ms']:.1f}ms")
    print(f"- Maximum delay: {analysis['max_delay_ms']:.0f}ms")
    print(f"- Average feedback: {analysis['avg_feedback']:.3f}")
    print(f"- Average decay: {analysis['avg_decay']:.3f}")
    print(f"- Average reverb density: {analysis['avg_reverb_density']:.3f}")

    print("\nDelay Distribution (travel time categories):")
    delay_dist = analysis['delay_distribution']
    print(f"- Short routes (< 1 sec): {delay_dist['short']}")
    print(f"- Medium routes (1-10 sec): {delay_dist['medium']}")
    print(f"- Long routes (> 10 sec): {delay_dist['long']}")

    print("\nAcoustic Analogies:")
    print("- HIGH REVERB areas: Dense component hubs (Delay processing, Routing connections)")
    print("- HIGH ECHO areas: Long integration routes (Platform chains, cross-system paths)")
    print("- HIGH DELAY areas: Complex architectures, extended processing chains")
    print("- LOW DECAY areas: Well-connected, high-throughput pathways")


def demonstrate_highway_characteristics():
    """Show the acoustic characteristics of major highways"""

    print("\n" + "="*60)
    print("COMPONENT ACOUSTIC CHARACTERISTICS")
    print("="*60)

    characteristics = get_highway_characteristics()

    for highway, desc in characteristics.items():
        print(f"{highway}: {desc}")


def create_visualization(network: AcousticRoutingNetwork):
    """Create a visualization of the network"""

    print("\n" + "="*60)
    print("NETWORK VISUALIZATION")
    print("="*60)

    try:
        # Save visualization
        viz_path = os.path.join(os.path.dirname(__file__), 'acoustic_routing_network.png')
        network.visualize_network(save_path=viz_path)
        print(f"Network visualization saved to: {viz_path}")

        # Demonstrate pulse propagation visualization
        print("\nSimulating pulse propagation for visualization...")
        propagation = network.propagate_pulse('Delay', max_steps=10)

        # Create simple animation data
        step_data = []
        for step, pulses in enumerate(propagation):
            cities = list(set(p.current_position for p in pulses if p.amplitude > 0.01))
            amplitudes = [p.amplitude for p in pulses if p.amplitude > 0.01]
            step_data.append((step, cities, amplitudes))

        print(f"Propagation data collected for {len(step_data)} steps")
        print("Components reached over time:")
        for step, cities, amps in step_data[:5]:  # Show first 5 steps
            avg_amp = np.mean(amps) if amps else 0
            print(f"  Step {step}: {len(cities)} components, avg amplitude: {avg_amp:.3f}")
    except ImportError as e:
        print(f"Visualization requires matplotlib. Install with: pip install matplotlib")
        print(f"Error: {e}")


def main():
    """Main demonstration function"""

    print("ACOUSTIC ROUTING SYSTEM DEMONSTRATION")
    print("Dimension & Resonance Component Network")
    print("="*60)

    # Build the network
    print("\nBuilding Dimension & Resonance Component Network with acoustic properties...")
    network = build_us_highway_network()
    print("Component network constructed successfully!")

    # Run demonstrations
    demonstrate_highway_characteristics()
    demonstrate_network_analysis(network)
    demonstrate_pulse_propagation(network)
    demonstrate_route_optimization(network)
    create_visualization(network)

    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)
    print("\nKey Insights:")
    print("• Components become acoustic conduits where connections = delay")
    print("• Processing hubs create reverb chambers of dense interconnectivity")
    print("• Integration routes generate echo-like feedback loops")
    print("• Route optimization reveals perceptual patterns in system architecture")
    print("• Pulse propagation shows how information flows through component networks")


if __name__ == '__main__':
    main()
