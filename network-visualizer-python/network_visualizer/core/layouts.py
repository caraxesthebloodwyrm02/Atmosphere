"""
Network Layout Algorithms

Collection of layout algorithms for positioning nodes in network visualizations,
including force-directed, hierarchical, and specialized layouts.
"""

import networkx as nx
from typing import Dict, Any, Optional, Tuple
import numpy as np
from scipy.spatial.distance import pdist, squareform


class LayoutManager:
    """
    Network layout computation and management.

    Provides various algorithms for computing node positions in network visualizations,
    including force-directed, circular, hierarchical, and spectral layouts.
    """

    def __init__(self):
        """Initialize the layout manager."""
        self.layout_methods = {
            'spring': self._spring_layout,
            'force_directed': self._force_directed_layout,
            'circular': self._circular_layout,
            'random': self._random_layout,
            'shell': self._shell_layout,
            'spectral': self._spectral_layout,
            'kamada_kawai': self._kamada_kawai_layout,
            'fruchterman_reingold': self._fruchterman_reingold_layout,
            'hierarchical': self._hierarchical_layout,
            'radial': self._radial_layout,
        }

    def compute_layout(self, G: nx.Graph, method: str = 'spring', **kwargs) -> Dict[Any, Tuple[float, float]]:
        """
        Compute node positions using specified layout algorithm.

        Args:
            G: NetworkX graph
            method: Layout method to use
            **kwargs: Method-specific parameters

        Returns:
            Dictionary mapping nodes to (x, y) positions
        """
        if method not in self.layout_methods:
            available = list(self.layout_methods.keys())
            raise ValueError(f"Unknown layout method '{method}'. Available: {available}")

        return self.layout_methods[method](G, **kwargs)

    def _spring_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute spring (force-directed) layout."""
        pos = nx.spring_layout(G, **kwargs)
        return {node: tuple(coord) for node, coord in pos.items()}

    def _force_directed_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute force-directed layout (alias for spring)."""
        return self._spring_layout(G, **kwargs)

    def _circular_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute circular layout."""
        pos = nx.circular_layout(G, **kwargs)
        return {node: tuple(coord) for node, coord in pos.items()}

    def _random_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute random layout."""
        pos = nx.random_layout(G, **kwargs)
        return {node: tuple(coord) for node, coord in pos.items()}

    def _shell_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute shell layout."""
        pos = nx.shell_layout(G, **kwargs)
        return {node: tuple(coord) for node, coord in pos.items()}

    def _spectral_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute spectral layout."""
        pos = nx.spectral_layout(G, **kwargs)
        return {node: tuple(coord) for node, coord in pos.items()}

    def _kamada_kawai_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute Kamada-Kawai layout."""
        pos = nx.kamada_kawai_layout(G, **kwargs)
        return {node: tuple(coord) for node, coord in pos.items()}

    def _fruchterman_reingold_layout(self, G: nx.Graph, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Compute Fruchterman-Reingold force-directed layout."""
        pos = nx.fruchterman_reingold_layout(G, **kwargs)
        return {node: tuple(coord) for node, coord in pos.items()}

    def _hierarchical_layout(self, G: nx.Graph, root: Any = None, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """
        Compute hierarchical layout.

        Args:
            G: NetworkX graph
            root: Root node for hierarchy (auto-detected if None)
            **kwargs: Additional parameters
        """
        if root is None:
            # Find node with minimum degree as potential root
            degrees = dict(G.degree())
            root = min(degrees, key=degrees.get)

        # Compute levels using BFS
        levels = {}
        visited = set()
        queue = [(root, 0)]
        visited.add(root)
        levels[root] = 0

        while queue:
            node, level = queue.pop(0)
            for neighbor in G.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    levels[neighbor] = level + 1
                    queue.append((neighbor, level + 1))

        # Position nodes by level
        max_level = max(levels.values()) if levels else 0
        level_counts = {}
        positions = {}

        for node, level in levels.items():
            if level not in level_counts:
                level_counts[level] = 0
            else:
                level_counts[level] += 1

            # Calculate x position within level
            level_size = sum(1 for n, l in levels.items() if l == level)
            x = (level_counts[level] - level_size / 2) * 2.0

            # Y position based on level
            y = -level * 2.0

            positions[node] = (x, y)

        return positions

    def _radial_layout(self, G: nx.Graph, center: Any = None, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """
        Compute radial layout from center node.

        Args:
            G: NetworkX graph
            center: Center node (auto-detected if None)
            **kwargs: Additional parameters
        """
        if center is None:
            # Use highest degree node as center
            degrees = dict(G.degree())
            center = max(degrees, key=degrees.get)

        # Compute distances from center
        distances = nx.shortest_path_length(G, center)

        # Group nodes by distance
        distance_groups = {}
        for node, dist in distances.items():
            if dist not in distance_groups:
                distance_groups[dist] = []
            distance_groups[dist].append(node)

        positions = {}

        # Position center
        positions[center] = (0.0, 0.0)

        # Position other nodes radially
        for distance, nodes in distance_groups.items():
            if distance == 0:
                continue

            angle_step = 2 * np.pi / len(nodes)
            radius = distance * 1.5  # Scale radius by distance

            for i, node in enumerate(nodes):
                angle = i * angle_step
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                positions[node] = (x, y)

        return positions

    def optimize_layout(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                       method: str = 'force_directed', iterations: int = 50,
                       **kwargs) -> Dict[Any, Tuple[float, float]]:
        """
        Optimize existing layout to reduce edge crossings and improve aesthetics.

        Args:
            G: NetworkX graph
            pos: Initial positions
            method: Optimization method
            iterations: Number of optimization iterations
            **kwargs: Method-specific parameters

        Returns:
            Optimized positions
        """
        if method == 'force_directed':
            return self._optimize_force_directed(G, pos, iterations, **kwargs)
        elif method == 'stress':
            return self._optimize_stress(G, pos, iterations, **kwargs)
        else:
            return pos

    def _optimize_force_directed(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                                iterations: int, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Optimize layout using force-directed algorithm."""
        # Simple force-directed optimization
        k = kwargs.get('k', 1.0)  # Spring constant
        repulsive_force = kwargs.get('repulsive', 0.1)
        attractive_force = kwargs.get('attractive', 0.01)

        positions = dict(pos)

        for _ in range(iterations):
            forces = {node: np.array([0.0, 0.0]) for node in G.nodes}

            # Calculate repulsive forces
            for i, node1 in enumerate(G.nodes):
                for j, node2 in enumerate(G.nodes):
                    if i != j:
                        pos1 = np.array(positions[node1])
                        pos2 = np.array(positions[node2])
                        diff = pos1 - pos2
                        distance = np.linalg.norm(diff)

                        if distance > 0:
                            force = repulsive_force / (distance * distance)
                            forces[node1] += force * (diff / distance)

            # Calculate attractive forces
            for edge in G.edges:
                node1, node2 = edge
                pos1 = np.array(positions[node1])
                pos2 = np.array(positions[node2])
                diff = pos1 - pos2
                distance = np.linalg.norm(diff)

                if distance > 0:
                    force = attractive_force * distance / k
                    forces[node1] -= force * (diff / distance)
                    forces[node2] += force * (diff / distance)

            # Update positions
            for node in G.nodes:
                positions[node] = tuple(np.array(positions[node]) + forces[node] * 0.01)

        return positions

    def _optimize_stress(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                        iterations: int, **kwargs) -> Dict[Any, Tuple[float, float]]:
        """Optimize layout using stress minimization."""
        # Stress majorization algorithm
        positions = dict(pos)

        for _ in range(iterations):
            new_positions = {}

            for node in G.nodes:
                weighted_sum = np.array([0.0, 0.0])
                total_weight = 0.0

                for neighbor in G.neighbors(node):
                    pos_node = np.array(positions[node])
                    pos_neighbor = np.array(positions[neighbor])

                    # Graph distance (always 1 for unweighted graphs)
                    graph_dist = 1.0

                    # Euclidean distance
                    euclid_dist = np.linalg.norm(pos_node - pos_neighbor)

                    if euclid_dist > 0:
                        weight = 1.0 / (euclid_dist * euclid_dist)
                        direction = (pos_neighbor - pos_node) / euclid_dist
                        weighted_sum += weight * (graph_dist * direction + pos_neighbor)
                        total_weight += weight

                if total_weight > 0:
                    new_positions[node] = tuple(weighted_sum / total_weight)
                else:
                    new_positions[node] = positions[node]

            positions = new_positions

        return positions

    def get_layout_properties(self, method: str) -> Dict[str, Any]:
        """
        Get properties and characteristics of a layout method.

        Args:
            method: Layout method name

        Returns:
            Dictionary of layout properties
        """
        properties = {
            'spring': {
                'type': 'force_directed',
                'complexity': 'O(N²)',
                'quality': 'high',
                'speed': 'medium',
                'use_case': 'general_networks'
            },
            'circular': {
                'type': 'geometric',
                'complexity': 'O(N)',
                'quality': 'medium',
                'speed': 'fast',
                'use_case': 'regular_structures'
            },
            'hierarchical': {
                'type': 'tree',
                'complexity': 'O(N)',
                'quality': 'high',
                'speed': 'fast',
                'use_case': 'tree_structures'
            },
            'spectral': {
                'type': 'mathematical',
                'complexity': 'O(N³)',
                'quality': 'high',
                'speed': 'slow',
                'use_case': 'complex_networks'
            }
        }

        return properties.get(method, {})
