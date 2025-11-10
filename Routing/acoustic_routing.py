"""
Acoustic Routing System - Inspired by U.S. Highway Network and Audio Effects
===========================================================================

This module implements a routing system that models the U.S. highway network
using acoustic principles from Reverb, Echo, and Delay components.

Key Concepts:
- Reverb: Dense interconnectivity (urban clusters, high-traffic networks)
- Echo: Large-scale feedback loops (interstate loops, regional routes)
- Delay: Routing latency (travel time, controlled postponements)

The system simulates pulse propagation through an acoustic topology where
highways become conduits for signal flow, revealing spatial and temporal patterns.
"""

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import time


@dataclass
class AcousticParameters:
    """Acoustic properties for routing edges"""
    delay_time: float  # Travel time or physical distance (ms)
    feedback: float    # Number of alternate routes/detours (0-1)
    decay: float       # Traffic dissipation/energy loss (0-1)
    reverb_density: float  # Local interconnectivity (0-1)


@dataclass
class Pulse:
    """Represents a propagating signal through the network"""
    origin: str
    current_position: str
    amplitude: float
    path_history: List[str]
    accumulated_delay: float
    reflections: List[Tuple[str, float]]  # (node, reflection_time)


class AcousticRoutingNetwork:
    """
    Main class for acoustic routing system.
    Models U.S. highway network as acoustic topology.
    """

    def __init__(self):
        self.graph = nx.DiGraph()  # Directed graph for highway segments
        self.acoustic_params: Dict[Tuple[str, str], AcousticParameters] = {}
        self.node_positions: Dict[str, Tuple[float, float]] = {}  # For visualization

    def add_highway_segment(self, start: str, end: str,
                           distance_miles: float,
                           speed_limit_mph: float = 65,
                           interconnectivity: float = 0.3,
                           feedback_loops: float = 0.2):
        """
        Add a highway segment with acoustic properties.

        Args:
            start: Starting city/node
            end: Ending city/node
            distance_miles: Physical distance
            speed_limit_mph: Speed limit for travel time calculation
            interconnectivity: Local density (reverb analog)
            feedback_loops: Number of detour options (echo analog)
        """

        # Calculate acoustic parameters
        travel_time_hours = distance_miles / speed_limit_mph
        delay_ms = travel_time_hours * 3600 * 1000  # Convert to milliseconds

        # Normalize feedback (0-1 scale based on typical detour count)
        feedback = min(feedback_loops / 5.0, 1.0)

        # Calculate decay based on distance (longer = more dissipation)
        decay = max(0.1, 1.0 - (distance_miles / 3000))  # Assume 3000 miles max

        params = AcousticParameters(
            delay_time=delay_ms,
            feedback=feedback,
            decay=decay,
            reverb_density=interconnectivity
        )

        # Add to graph
        self.graph.add_edge(start, end, weight=distance_miles)
        self.acoustic_params[(start, end)] = params

        # Add nodes if not exist
        if start not in self.node_positions:
            self.node_positions[start] = self._generate_position()
        if end not in self.node_positions:
            self.node_positions[end] = self._generate_position()

    def _generate_position(self) -> Tuple[float, float]:
        """Generate random position for visualization (simplified)"""
        return (np.random.uniform(-100, 100), np.random.uniform(-50, 50))

    def propagate_pulse(self, start_node: str, max_steps: int = 50,
                       initial_amplitude: float = 1.0) -> List[Pulse]:
        """
        Simulate pulse propagation through the acoustic network.

        Returns list of pulses at each step, showing how the signal
        spreads and accumulates acoustic effects.
        """

        pulses = [Pulse(start_node, start_node, initial_amplitude,
                       [start_node], 0.0, [])]

        propagation_history = [pulses.copy()]

        for step in range(max_steps):
            new_pulses = []

            for pulse in pulses:
                current_node = pulse.current_position

                # Get all outgoing edges
                neighbors = list(self.graph.successors(current_node))

                if not neighbors:
                    # Dead end - pulse decays
                    decayed_pulse = Pulse(
                        pulse.origin, current_node,
                        pulse.amplitude * 0.1,  # Rapid decay at dead end
                        pulse.path_history + [current_node],
                        pulse.accumulated_delay,
                        pulse.reflections + [(current_node, pulse.accumulated_delay)]
                    )
                    new_pulses.append(decayed_pulse)
                    continue

                # Distribute pulse among neighbors
                for neighbor in neighbors:
                    edge_params = self.acoustic_params.get((current_node, neighbor))
                    if not edge_params:
                        continue

                    # Calculate new amplitude with acoustic effects
                    distance_factor = edge_params.decay
                    reverb_boost = 1 + (edge_params.reverb_density * 0.5)  # Local density boost
                    feedback_echo = edge_params.feedback * 0.3  # Echo contribution

                    new_amplitude = pulse.amplitude * distance_factor * reverb_boost + feedback_echo

                    # Add delay
                    new_delay = pulse.accumulated_delay + edge_params.delay_time

                    # Create reflection if feedback is significant
                    reflections = pulse.reflections.copy()
                    if edge_params.feedback > 0.5:
                        reflections.append((neighbor, new_delay))

                    new_pulse = Pulse(
                        pulse.origin, neighbor, new_amplitude,
                        pulse.path_history + [neighbor],
                        new_delay, reflections
                    )

                    new_pulses.append(new_pulse)

            pulses = new_pulses
            propagation_history.append(pulses.copy())

            # Stop if all pulses have decayed
            if all(p.amplitude < 0.01 for p in pulses):
                break

        return propagation_history

    def analyze_network_acoustics(self) -> Dict[str, Any]:
        """
        Analyze the acoustic properties of the entire network.
        Returns metrics about reverb density, delay distribution, etc.
        """

        if not self.graph.edges():
            return {}

        delays = [params.delay_time for params in self.acoustic_params.values()]
        feedbacks = [params.feedback for params in self.acoustic_params.values()]
        decays = [params.decay for params in self.acoustic_params.values()]
        densities = [params.reverb_density for params in self.acoustic_params.values()]

        return {
            'total_segments': len(self.graph.edges()),
            'total_nodes': len(self.graph.nodes()),
            'avg_delay_ms': np.mean(delays),
            'max_delay_ms': np.max(delays),
            'avg_feedback': np.mean(feedbacks),
            'avg_decay': np.mean(decays),
            'avg_reverb_density': np.mean(densities),
            'delay_distribution': {
                'short': len([d for d in delays if d < 1000]),  # < 1 sec
                'medium': len([d for d in delays if 1000 <= d < 10000]),  # 1-10 sec
                'long': len([d for d in delays if d >= 10000])  # > 10 sec
            }
        }

    def visualize_network(self, propagation_history: Optional[List[List[Pulse]]] = None,
                         save_path: Optional[str] = None):
        """
        Visualize the acoustic routing network with 3D depth and dimension.
        Optionally show pulse propagation animation.
        """

        # Create figure with enhanced 3D-like depth effects
        fig, ax = plt.subplots(figsize=(14, 10), facecolor='#0a0a0a')

        # Create gradient background for depth illusion
        gradient = np.linspace(0, 1, 100).reshape(1, -1)
        gradient = np.vstack((gradient, gradient))
        ax.imshow(gradient, extent=[-150, 150, -100, 100], aspect='auto',
                 cmap='Blues', alpha=0.1, zorder=-1)

        # Add multiple depth layers with subtle grids
        for depth_level in [0.8, 0.6, 0.4]:
            ax.grid(True, which='both', color='#404040', linestyle='-',
                   linewidth=0.3, alpha=depth_level * 0.2, zorder=depth_level)

        # Calculate 3D-like positioning based on acoustic parameters
        pos = self.node_positions.copy()

        # Add depth dimension based on connectivity and acoustic properties
        node_depths = {}
        node_sizes = {}
        node_alphas = {}

        for node in self.graph.nodes():
            # Calculate node's "depth" based on its connections and acoustic properties
            connected_params = []
            for neighbor in self.graph.neighbors(node):
                edge_key = (node, neighbor) if (node, neighbor) in self.acoustic_params else (neighbor, node)
                if edge_key in self.acoustic_params:
                    connected_params.append(self.acoustic_params[edge_key])

            if connected_params:
                # Average acoustic properties determine depth
                avg_density = np.mean([p.reverb_density for p in connected_params])
                avg_delay = np.mean([p.delay_time for p in connected_params])
                avg_feedback = np.mean([p.feedback for p in connected_params])

                # Depth calculation: higher density = closer to viewer (larger, more opaque)
                depth_factor = (avg_density * 0.6 + (1 - avg_delay/10000) * 0.3 + avg_feedback * 0.1)
                node_depths[node] = max(0.3, min(1.0, depth_factor))
            else:
                node_depths[node] = 0.5

            # Size and alpha based on depth (perspective effect)
            base_size = 500
            depth_size = base_size * (0.8 + node_depths[node] * 0.4)  # Closer = larger
            node_sizes[node] = depth_size

            depth_alpha = 0.7 + node_depths[node] * 0.3  # Closer = more opaque
            node_alphas[node] = depth_alpha

        # Create dynamic edge colors based on acoustic parameters
        edge_colors = []
        edge_widths = []
        edge_alphas = []

        # Get acoustic parameter ranges for normalization
        delays = [params.delay_time for params in self.acoustic_params.values()]
        feedbacks = [params.feedback for params in self.acoustic_params.values()]
        decays = [params.decay for params in self.acoustic_params.values()]
        densities = [params.reverb_density for params in self.acoustic_params.values()]

        delay_min, delay_max = min(delays), max(delays)
        feedback_min, feedback_max = min(feedbacks), max(feedbacks)
        density_min, density_max = min(densities), max(densities)

        # Create color mapping based on combined acoustic properties
        for (u, v) in self.graph.edges():
            if (u, v) in self.acoustic_params:
                params = self.acoustic_params[(u, v)]

                # Normalize parameters to 0-1 range
                delay_norm = (params.delay_time - delay_min) / (delay_max - delay_min) if delay_max > delay_min else 0.5
                feedback_norm = (params.feedback - feedback_min) / (feedback_max - feedback_min) if feedback_max > feedback_min else 0.5
                density_norm = (params.reverb_density - density_min) / (density_max - density_min) if density_max > density_min else 0.5

                # Create gradient color based on input/output principle
                # Low delay + high density = "input" flows (cool colors)
                # High delay + low density = "output" flows (warm colors)
                # Feedback creates saturation variation

                if density_norm > 0.6:  # High connectivity (input-like)
                    # Cool colors for input flows
                    r = int(100 + (delay_norm * 100))  # Red increases with delay
                    g = int(150 + (feedback_norm * 100))  # Green increases with feedback
                    b = int(200 + (density_norm * 55))  # Blue high for connectivity
                else:  # Low connectivity (output-like)
                    # Warm colors for output flows
                    r = int(200 + (delay_norm * 55))  # Red high for delay
                    g = int(100 + (feedback_norm * 100))  # Green varies with feedback
                    b = int(100 + (density_norm * 100))  # Blue low for sparse connections

                # Ensure RGB values are within 0-255
                r, g, b = max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))

                # Create hex color
                color = f'#{r:02x}{g:02x}{b:02x}'
                edge_colors.append(color)

                # Dynamic width based on feedback (more feedback = thicker lines)
                width = 1.5 + (params.feedback * 3)
                edge_widths.append(width)

                # Alpha based on decay (less decay = more opaque)
                alpha = 0.6 + (params.decay * 0.4)
                edge_alphas.append(alpha)
            else:
                # Default fallback
                edge_colors.append('#cccccc')
                edge_widths.append(2)
                edge_alphas.append(0.8)

        # Draw nodes with depth-based sizing and shadow effects
        # First draw shadows for depth illusion
        for node in self.graph.nodes():
            x, y = pos[node]
            shadow_offset = (1 - node_depths.get(node, 0.5)) * 3  # Further back = larger shadow
            shadow_alpha = node_alphas.get(node, 0.8) * 0.3

            # Draw shadow circle
            shadow_circle = plt.Circle((x + shadow_offset, y - shadow_offset),
                                     node_sizes.get(node, 500) * 0.08,
                                     color='#000000', alpha=shadow_alpha, zorder=1)
            ax.add_patch(shadow_circle)

        # Draw main nodes with depth-based properties
        node_colors = []
        node_sizes_list = []
        node_alphas_list = []

        for node in self.graph.nodes():
            node_colors.append('#4a90e2')
            node_sizes_list.append(node_sizes.get(node, 500))
            node_alphas_list.append(node_alphas.get(node, 0.8))

        # Draw nodes with depth-based properties
        nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors,
                              node_size=node_sizes_list, alpha=node_alphas_list,
                              ax=ax)

        # Draw edges with individual colors and properties
        for i, (u, v) in enumerate(self.graph.edges()):
            color = edge_colors[i] if i < len(edge_colors) else '#cccccc'
            width = edge_widths[i] if i < len(edge_widths) else 2
            alpha = edge_alphas[i] if i < len(edge_alphas) else 0.8

            nx.draw_networkx_edges(self.graph, pos, edgelist=[(u, v)],
                                 edge_color=color, width=width, alpha=alpha,
                                 arrows=True, arrowsize=20, ax=ax)

        # Draw node labels with depth-based properties
        label_colors = []
        label_sizes = []
        for node in self.graph.nodes():
            depth = node_depths.get(node, 0.5)
            # Labels for closer nodes are more visible
            label_colors.append(('white', depth * 0.8 + 0.2))
            label_sizes.append(8 + depth * 4)  # Closer = larger labels

        # Draw labels individually with depth properties
        for i, node in enumerate(self.graph.nodes()):
            color, alpha = label_colors[i]
            fontsize = label_sizes[i]
            plt.annotate(node, pos[node], xytext=(0, 0), textcoords='offset points',
                        ha='center', va='center', fontsize=fontsize,
                        color=color, alpha=alpha, fontweight='bold', zorder=3)

        # Enhanced title with depth context
        ax.set_title('Dimension & Resonance Acoustic Network\n(Component Interconnectivity with 3D Depth)',
                    fontsize=16, fontweight='bold', color='white',
                    pad=20, bbox=dict(boxstyle="round,pad=0.7",
                                    facecolor='#2a2a2a',
                                    edgecolor='#404040',
                                    alpha=0.9))

        # Set axis limits to show full depth range
        all_x = [pos[node][0] for node in pos]
        all_y = [pos[node][1] for node in pos]
        margin = 20
        ax.set_xlim(min(all_x) - margin, max(all_x) + margin)
        ax.set_ylim(min(all_y) - margin, max(all_y) + margin)

        # Remove axis ticks for cleaner look
        ax.set_xticks([])
        ax.set_yticks([])

        # Add depth legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4a90e2',
                      markersize=15, alpha=0.9, label='High Connectivity (Close)'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4a90e2',
                      markersize=10, alpha=0.6, label='Medium Connectivity'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4a90e2',
                      markersize=8, alpha=0.4, label='Low Connectivity (Far)')
        ]
        ax.legend(handles=legend_elements, loc='upper right',
                 facecolor='#2a2a2a', edgecolor='#404040',
                 labelcolor='white', fontsize=8)

        # Add subtle border with depth effect
        for spine in ax.spines.values():
            spine.set_edgecolor('#404040')
            spine.set_linewidth(2)
            spine.set_alpha(0.5)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight',
                       facecolor=fig.get_facecolor(), edgecolor='none')

        plt.show()

    def calculate_route_metrics(self, route: List[str]) -> Dict[str, float]:
        """
        Calculate comprehensive metrics for a route including enhanced optimization criteria.
        """
        if len(route) < 2:
            return {
                'total_distance': 0,
                'total_delay': 0,
                'avg_reverb_density': 0,
                'path_efficiency': 0,
                'connectivity_score': 0,
                'navigation_smoothness': 0,
                'route_reliability': 0
            }

        total_distance = 0
        total_delay = 0
        total_reverb = 0
        feedback_sum = 0
        decay_sum = 0
        edge_count = 0

        for i in range(len(route) - 1):
            edge = (route[i], route[i + 1])
            if edge in self.acoustic_params:
                params = self.acoustic_params[edge]
                total_distance += self.graph[edge[0]][edge[1]]['weight']
                total_delay += params.delay_time
                total_reverb += params.reverb_density
                feedback_sum += params.feedback
                decay_sum += params.decay
                edge_count += 1

        if edge_count == 0:
            return self.calculate_route_metrics([])

        avg_reverb_density = total_reverb / edge_count
        avg_feedback = feedback_sum / edge_count
        avg_decay = decay_sum / edge_count

        # Enhanced metrics for seamless navigation
        path_efficiency = 1.0 / (1.0 + total_delay / 1000.0)  # Normalize delay impact
        connectivity_score = avg_feedback * avg_reverb_density  # Combined connectivity
        navigation_smoothness = self.calculate_navigation_smoothness(route)
        route_reliability = avg_decay * (1.0 - avg_feedback * 0.1)  # Reliability considering detours

        return {
            'total_distance': total_distance,
            'total_delay': total_delay,
            'avg_reverb_density': avg_reverb_density,
            'path_efficiency': path_efficiency,
            'connectivity_score': connectivity_score,
            'navigation_smoothness': navigation_smoothness,
            'route_reliability': route_reliability,
            'avg_feedback_factor': avg_feedback,
            'avg_decay_factor': avg_decay
        }

    def calculate_navigation_smoothness(self, route: List[str]) -> float:
        """
        Calculate navigation smoothness based on route continuity and flow.
        Returns value between 0 (very rough) and 1 (very smooth).
        """
        if len(route) < 3:
            return 1.0  # Short routes are inherently smooth

        smoothness_score = 0
        valid_segments = 0

        for i in range(len(route) - 2):
            segment_a = (route[i], route[i + 1])
            segment_b = (route[i + 1], route[i + 2])

            # Check if both segments exist
            if segment_a in self.acoustic_params and segment_b in self.acoustic_params:
                params_a = self.acoustic_params[segment_a]
                params_b = self.acoustic_params[segment_b]

                # Calculate transition smoothness based on acoustic continuity
                delay_continuity = 1.0 - abs(params_a.delay_time - params_b.delay_time) / max(params_a.delay_time, params_b.delay_time, 1)
                reverb_continuity = 1.0 - abs(params_a.reverb_density - params_b.reverb_density)

                segment_smoothness = (delay_continuity + reverb_continuity) / 2.0
                smoothness_score += segment_smoothness
                valid_segments += 1

        return smoothness_score / valid_segments if valid_segments > 0 else 0.5

    def find_multi_criteria_route(self, start: str, end: str,
                                criteria_weights: Dict[str, float] = None) -> List[str]:
        """
        Find optimal route considering multiple criteria simultaneously.

        Args:
            criteria_weights: Dict with keys 'distance', 'delay', 'reverb', 'smoothness'
                            Values should sum to 1.0
        """
        if criteria_weights is None:
            criteria_weights = {'distance': 0.4, 'delay': 0.3, 'reverb': 0.2, 'smoothness': 0.1}

        # Normalize weights
        total_weight = sum(criteria_weights.values())
        normalized_weights = {k: v / total_weight for k, v in criteria_weights.items()}

        # Find candidate routes using different optimization criteria
        candidate_routes = []
        criteria = ['distance', 'delay', 'reverb']

        for criterion in criteria:
            route = self.find_optimal_route(start, end, criterion)
            if route:
                metrics = self.calculate_route_metrics(route)
                candidate_routes.append((route, metrics))

        if not candidate_routes:
            return []

        # Score each route based on weighted criteria
        best_route = None
        best_score = -float('inf')

        for route, metrics in candidate_routes:
            score = 0

            # Distance score (lower is better, so invert)
            if metrics['total_distance'] > 0:
                distance_score = 1.0 / metrics['total_distance']
            else:
                distance_score = 1.0
            score += normalized_weights.get('distance', 0) * distance_score

            # Delay score (lower is better)
            if metrics['total_delay'] > 0:
                delay_score = 1.0 / metrics['total_delay']
            else:
                delay_score = 1.0
            score += normalized_weights.get('delay', 0) * delay_score

            # Reverb score (higher density is better)
            reverb_score = metrics['avg_reverb_density']
            score += normalized_weights.get('reverb', 0) * reverb_score

            # Smoothness score
            smoothness_score = metrics['navigation_smoothness']
            score += normalized_weights.get('smoothness', 0) * smoothness_score

            if score > best_score:
                best_score = score
                best_route = route

        return best_route if best_route else []

    def optimize_route_for_navigation(self, start: str, end: str,
                                    preferences: Dict[str, str] = None) -> Tuple[List[str], Dict]:
        """
        Find route optimized for seamless navigation with user preferences.

        Args:
            preferences: Dict with navigation preferences like:
                       'speed_priority': 'fastest'/'balanced'/'scenic'
                       'traffic_avoidance': 'high'/'medium'/'low'
                       'route_type': 'direct'/'scenic'/'efficient'

        Returns:
            Tuple of (optimal_route, detailed_metrics)
        """
        if preferences is None:
            preferences = {}

        # Set default criteria weights based on preferences
        speed_priority = preferences.get('speed_priority', 'balanced')
        traffic_avoidance = preferences.get('traffic_avoidance', 'medium')
        route_type = preferences.get('route_type', 'efficient')

        # Define criteria weights based on preferences
        if speed_priority == 'fastest':
            criteria_weights = {'distance': 0.1, 'delay': 0.7, 'reverb': 0.1, 'smoothness': 0.1}
        elif speed_priority == 'scenic':
            criteria_weights = {'distance': 0.2, 'delay': 0.2, 'reverb': 0.5, 'smoothness': 0.1}
        else:  # balanced
            criteria_weights = {'distance': 0.3, 'delay': 0.3, 'reverb': 0.2, 'smoothness': 0.2}

        # Adjust for traffic avoidance
        if traffic_avoidance == 'high':
            criteria_weights['reverb'] *= 0.5  # Avoid dense areas
            criteria_weights['distance'] *= 1.2  # Prefer longer but less congested routes
        elif traffic_avoidance == 'low':
            criteria_weights['reverb'] *= 1.5  # Okay with denser routes

        # Adjust for route type
        if route_type == 'direct':
            criteria_weights['distance'] *= 1.5
            criteria_weights['delay'] *= 1.2
        elif route_type == 'scenic':
            criteria_weights['reverb'] *= 1.5
            criteria_weights['smoothness'] *= 1.3

        # Find optimal route
        optimal_route = self.find_multi_criteria_route(start, end, criteria_weights)

        if optimal_route:
            detailed_metrics = self.calculate_route_metrics(optimal_route)
            detailed_metrics.update({
                'preferences_applied': preferences,
                'criteria_weights_used': criteria_weights,
                'optimization_score': sum(
                    criteria_weights[k] * detailed_metrics.get(k, 0)
                    for k in ['distance', 'delay', 'reverb', 'smoothness']
                    if k in criteria_weights
                )
            })
        else:
            detailed_metrics = {}

        return optimal_route, detailed_metrics

    def find_optimal_route(self, start: str, end: str,
                          criteria: str = 'distance') -> List[str]:
        """
        Find optimal route using different acoustic criteria.

        Args:
            criteria: 'distance', 'delay', 'reverb' (minimize/maximize density)
        """

        if criteria == 'distance':
            # Standard shortest path
            try:
                return nx.shortest_path(self.graph, start, end, weight='weight')
            except nx.NetworkXNoPath:
                return []

        elif criteria == 'delay':
            # Path with minimal accumulated delay
            delay_weights = {edge: params.delay_time
                           for edge, params in self.acoustic_params.items()}
            nx.set_edge_attributes(self.graph, delay_weights, 'delay_weight')

            try:
                return nx.shortest_path(self.graph, start, end, weight='delay_weight')
            except nx.NetworkXNoPath:
                return []

        elif criteria == 'reverb':
            # Path maximizing reverb density (urban feel)
            density_weights = {edge: 1.0 / (params.reverb_density + 0.1)  # Inverse for maximization
                             for edge, params in self.acoustic_params.items()}
            nx.set_edge_attributes(self.graph, density_weights, 'density_weight')

            try:
                return nx.shortest_path(self.graph, start, end, weight='density_weight')
            except nx.NetworkXNoPath:
                return []

        return []
