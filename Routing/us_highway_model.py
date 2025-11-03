"""
U.S. Highway Network Model
===========================

Simplified representation of major U.S. highways as acoustic topology.
Includes key interstates and major routes with realistic distances and characteristics.
"""

from typing import Dict
from acoustic_routing import AcousticRoutingNetwork


def build_us_highway_network() -> AcousticRoutingNetwork:
    """
    Construct a simplified U.S. highway network with acoustic properties.

    Focuses on major interstates and routes that demonstrate:
    - Dense urban interconnectivity (reverb)
    - Long-haul feedback loops (echo)
    - Regional delay patterns (delay)
    """

    network = AcousticRoutingNetwork()

    # Major project components and their conceptual positions (simplified)
    # In a real implementation, these would use actual conceptual coordinates
    project_components = {
        # Delay Component (East Coast - trajectory optimization)
        'Delay': 'Delay Processing Hub',
        'Trajectory': 'Decision Trajectory',
        'Feedback': 'Signal Feedback Loop',
        'Processing': 'AI Processing Core',
        'Endpoint': 'Final Destination',

        # Reverb Component (Midwest - spatial audio)
        'Reverb': 'Spatial Audio Hub',
        'Spatial': '3D Positioning Engine',
        'Audio': 'Sound Processing Unit',
        'HRTF': 'Head-Related Transfer',

        # Echoes Component (South - multimodal AI)
        'Echoes': 'Multimodal AI Platform',
        'Multimodal': 'Cross-Modal Integration',
        'Orchestration': 'System Orchestrator',
        'Agent': 'AI Agent Framework',
        'Nexus': 'Connection Nexus',

        # Routing Component (West Coast - navigation)
        'Routing': 'Navigation System',
        'Connection': 'Network Connections',
        'Network': 'System Architecture',
        'Graph': 'Data Graph Engine',

        # Platform Core (Mountain West - foundational)
        'Platform': 'Core Platform',
        'Dimension': 'Multi-Dimensional Space',
        'Resonance': 'Signal Resonance',
        'Simulation': 'Virtual Environment',

        # Integration Points (Key Junctions)
        'Interface': 'User Interface Layer',
        'Bridge': 'Component Bridge',
        'Gateway': 'System Gateway'
    }

    # Define major highway segments with realistic distances
    # Format: (start, end, distance_miles, speed_limit, interconnectivity, feedback_loops)

    # Component-to-Component Routes (Dense interconnectivity - HIGH REVERB)
    delay_segments = [
        ('Trajectory', 'Delay', 215, 65, 0.9, 0.8),  # High interconnectivity
        ('Delay', 'Feedback', 90, 65, 0.95, 1.0),  # Dense processing
        ('Feedback', 'Processing', 140, 65, 0.9, 0.9),
        ('Processing', 'Echoes', 665, 70, 0.6, 0.5),  # Mix of processing/AI
    ]

    # Cross-Platform Routes (Long-haul with detours - HIGH ECHO)
    platform_segments = [
        ('Routing', 'Resonance', 370, 75, 0.4, 0.7),  # System detours
        ('Resonance', 'Agent', 1015, 75, 0.3, 0.8),  # Long integration stretches
        ('Agent', 'Orchestration', 550, 70, 0.5, 0.6),
        ('Orchestration', 'Echoes', 470, 65, 0.4, 0.5),
        ('Echoes', 'Endpoint', 665, 70, 0.6, 0.4),
    ]

    # Core Architecture Routes (Balanced mix)
    core_segments = [
        ('Routing', 'Platform', 1020, 75, 0.3, 0.6),  # Architecture passes
        ('Platform', 'Bridge', 650, 75, 0.4, 0.5),
        ('Bridge', 'Interface', 250, 70, 0.5, 0.4),
        ('Interface', 'Reverb', 300, 70, 0.6, 0.5),
    ]

    # Navigation System Routes (High density urban corridors - REVERB)
    routing_segments = [
        ('Network', 'Graph', 175, 60, 0.8, 0.7),  # Navigation density
        ('Graph', 'Connection', 635, 65, 0.6, 0.6),
        ('Connection', 'Routing', 380, 70, 0.7, 0.8),
    ]

    # Integration Routes (Industrial heartland)
    integration_segments = [
        ('Connection', 'Dimension', 750, 75, 0.3, 0.5),
        ('Dimension', 'Platform', 520, 75, 0.4, 0.6),
        ('Platform', 'Gateway', 540, 75, 0.3, 0.4),
        ('Gateway', 'Reverb', 470, 70, 0.5, 0.5),
        ('Reverb', 'Spatial', 340, 70, 0.7, 0.6),
        ('Spatial', 'Delay', 460, 65, 0.6, 0.7),
    ]

    # Multimodal Routes (Southwestern Route)
    multimodal_segments = [
        ('Routing', 'Simulation', 890, 75, 0.3, 0.6),
        ('Simulation', 'Agent', 640, 75, 0.4, 0.5),
        ('Agent', 'Multimodal', 660, 70, 0.5, 0.6),
        ('Multimodal', 'Echoes', 150, 65, 0.6, 0.4),
    ]

    # Extended Architecture Routes (Northern Tier)
    extended_segments = [
        ('Network', 'HRTF', 2070, 75, 0.3, 0.7),  # Very long system
        ('HRTF', 'Reverb', 90, 65, 0.8, 0.5),
        ('Reverb', 'Spatial', 280, 70, 0.6, 0.5),
        ('Spatial', 'Audio', 170, 65, 0.7, 0.6),
    ]

    # Combine all segments
    all_segments = (delay_segments + platform_segments + core_segments +
                   routing_segments + integration_segments + multimodal_segments +
                   extended_segments)

    # Add all segments to network
    for start, end, distance, speed, interconnectivity, feedback in all_segments:
        network.add_highway_segment(
            start, end, distance, speed, interconnectivity, feedback
        )

    # Add cross-component connections (integration bridges)
    # These create additional feedback loops and reverb chambers

    cross_connects = [
        # Reverb hub connections (high spatial interconnectivity)
        ('Reverb', 'HRTF', 90, 65, 0.8, 0.6),
        ('Reverb', 'Spatial', 280, 70, 0.7, 0.5),

        # Echoes connections (multimodal integration)
        ('Agent', 'Nexus', 240, 70, 0.6, 0.4),
        ('Nexus', 'Orchestration', 350, 65, 0.5, 0.5),

        # Platform core connections
        ('Platform', 'Dimension', 520, 75, 0.4, 0.5),
        ('Dimension', 'Simulation', 420, 75, 0.3, 0.4),
        ('Simulation', 'Routing', 270, 70, 0.5, 0.6),

        # Processing alternatives (parallel pathways)
        ('Processing', 'Feedback', 140, 65, 0.9, 0.7),  # Parallel route
        ('Feedback', 'Trajectory', 310, 65, 0.7, 0.6),  # Alternative to main path
    ]

    for start, end, distance, speed, interconnectivity, feedback in cross_connects:
        network.add_highway_segment(
            start, end, distance, speed, interconnectivity, feedback
        )

    return network


def get_highway_characteristics() -> Dict[str, str]:
    """
    Return descriptions of highway characteristics for acoustic analogy.
    """

    return {
        'Delay_Routes': 'Trajectory processing corridor - HIGH REVERB (decision optimization)',
        'Platform_Routes': 'Cross-system integration - HIGH ECHO (component detours, long chains)',
        'Core_Routes': 'Architecture foundation - BALANCED (platform to interface)',
        'Routing_Routes': 'Navigation spine - HIGH REVERB (connection density)',
        'Integration_Routes': 'System heartland - MEDIUM ECHO (data flow, processing)',
        'Multimodal_Routes': 'AI integration path - BALANCED (agent to multimodal)',
        'Extended_Routes': 'Architecture extension - HIGH DELAY (long system chains)',
        'Cross_Connects': 'Integration bridges - LOCAL REVERB (component coupling)'
    }


# Example usage
if __name__ == '__main__':
    network = build_us_highway_network()
    analysis = network.analyze_network_acoustics()

    print("U.S. Highway Acoustic Network Analysis:")
    print(f"Total segments: {analysis['total_segments']}")
    print(f"Total cities: {analysis['total_nodes']}")
    print(f"Average delay: {analysis['avg_delay_ms']:.1f}ms")
    print(f"Average feedback: {analysis['avg_feedback']:.3f}")
    print(f"Average reverb density: {analysis['avg_reverb_density']:.3f}")
    print(f"Delay distribution: {analysis['delay_distribution']}")

    print("\nHighway Characteristics:")
    for highway, desc in get_highway_characteristics().items():
        print(f"- {highway}: {desc}")
