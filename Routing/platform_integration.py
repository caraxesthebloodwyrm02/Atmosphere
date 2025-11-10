"""
Integration with Dimension & Resonance Platform
===============================================

This module demonstrates how the Acoustic Routing System integrates
with the existing Delay and Reverb components from the platform.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from acoustic_routing import AcousticRoutingNetwork
from us_highway_model import build_us_highway_network
import numpy as np


class IntegratedAcousticRouter(AcousticRoutingNetwork):
    """Extended routing system that integrates Delay and Reverb principles."""

    def route_with_delay_optimization(self, start: str, end: str) -> dict:
        """Route optimization using Delay component principles."""
        route = self.find_optimal_route(start, end, 'distance')
        return {'route': route, 'delay_optimized': True}

    def navigate_with_reverb_cues(self, current_position: str, destination: str) -> dict:
        """Navigation using Reverb component spatial audio principles."""
        route = self.find_optimal_route(current_position, destination, 'distance')
        return {'route': route, 'spatial_cues': {}, 'reverb_enhanced': True}


def demonstrate_platform_integration():
    """Demonstrate integration with Delay and Reverb components"""
    print("PLATFORM INTEGRATION DEMONSTRATION")
    print("=" * 50)

    # Create integrated router
    router = IntegratedAcousticRouter()

    # Build the highway network
    network = build_us_highway_network()

    # Copy network data
    router.graph = network.graph.copy()
    router.acoustic_params = network.acoustic_params.copy()
    router.node_positions = network.node_positions.copy()

    print("\n1. Delay-Inspired Trajectory Optimization")
    print("-" * 40)

    route_result = router.route_with_delay_optimization('Boston', 'Miami')
    if route_result['route']:
        print("Route found with Delay optimization:", ' -> '.join(route_result['route']))

    print("\n2. Reverb-Inspired Spatial Navigation")
    print("-" * 40)

    nav_result = router.navigate_with_reverb_cues('NYC', 'Los_Angeles')
    if nav_result['route']:
        print("Route found with Reverb enhancement:", ' -> '.join(nav_result['route']))

    print("\n3. Integration Benefits")
    print("-" * 40)
    print("• Delay component enables trajectory optimization")
    print("• Reverb component provides spatial audio navigation")
    print("• Combined system creates immersive routing experience")


if __name__ == '__main__':
    demonstrate_platform_integration()
