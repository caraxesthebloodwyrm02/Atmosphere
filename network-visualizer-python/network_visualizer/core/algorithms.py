"""
Network Analysis Algorithms

Comprehensive collection of network analysis algorithms including centrality measures,
community detection, and statistical analysis.
"""

import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
import numpy as np
from collections import defaultdict
import community as community_louvain  # python-louvain package


class NetworkAnalyzer:
    """
    Network analysis algorithms and metrics computation.

    Provides comprehensive network analysis capabilities including centrality measures,
    community detection, statistical analysis, and path computation.
    """

    def __init__(self):
        """Initialize the network analyzer."""
        self.config = {
            'centrality_methods': {
                'degree': self._compute_degree_centrality,
                'betweenness': self._compute_betweenness_centrality,
                'closeness': self._compute_closeness_centrality,
                'eigenvector': self._compute_eigenvector_centrality,
                'pagerank': self._compute_pagerank,
                'katz': self._compute_katz_centrality,
            },
            'community_methods': {
                'louvain': self._detect_communities_louvain,
                'girvan_newman': self._detect_communities_girvan_newman,
                'label_propagation': self._detect_communities_label_propagation,
            }
        }

    def compute_centrality(self, G: nx.Graph, method: str = 'degree',
                          normalized: bool = True) -> Dict[Any, float]:
        """
        Compute centrality metric for all nodes.

        Args:
            G: NetworkX graph
            method: Centrality method to use
            normalized: Whether to normalize results

        Returns:
            Dictionary mapping nodes to centrality values
        """
        if method not in self.config['centrality_methods']:
            available = list(self.config['centrality_methods'].keys())
            raise ValueError(f"Unknown centrality method '{method}'. Available: {available}")

        return self.config['centrality_methods'][method](G, normalized)

    def compute_statistics(self, G: nx.Graph) -> Dict[str, Any]:
        """
        Compute comprehensive network statistics.

        Args:
            G: NetworkX graph

        Returns:
            Dictionary of network statistics
        """
        stats = {
            'num_nodes': len(G.nodes),
            'num_edges': len(G.edges),
            'density': nx.density(G),
            'average_degree': sum(dict(G.degree()).values()) / len(G.nodes),
            'degree_assortativity': nx.degree_assortativity_coefficient(G),
        }

        # Connected components
        if nx.is_connected(G):
            stats.update({
                'is_connected': True,
                'diameter': nx.diameter(G),
                'average_path_length': nx.average_shortest_path_length(G),
                'clustering_coefficient': nx.average_clustering(G),
            })
        else:
            stats.update({
                'is_connected': False,
                'num_components': nx.number_connected_components(G),
                'largest_component_size': len(max(nx.connected_components(G), key=len)),
            })

        # Additional metrics
        try:
            stats['transitivity'] = nx.transitivity(G)
            stats['square_clustering'] = nx.square_clustering(G)
        except:
            pass

        return stats

    def detect_communities(self, G: nx.Graph, method: str = 'louvain') -> Dict[Any, int]:
        """
        Detect communities in the network.

        Args:
            G: NetworkX graph
            method: Community detection method

        Returns:
            Dictionary mapping nodes to community IDs
        """
        if method not in self.config['community_methods']:
            available = list(self.config['community_methods'].keys())
            raise ValueError(f"Unknown community method '{method}'. Available: {available}")

        return self.config['community_methods'][method](G)

    def compute_shortest_paths(self, G: nx.Graph, source: Any = None,
                              target: Any = None) -> Dict:
        """
        Compute shortest paths in the network.

        Args:
            G: NetworkX graph
            source: Source node (None for all pairs)
            target: Target node (None for all pairs)

        Returns:
            Dictionary of shortest path results
        """
        if source is not None and target is not None:
            # Single pair shortest path
            try:
                path = nx.shortest_path(G, source, target)
                length = nx.shortest_path_length(G, source, target)
                return {
                    'path': path,
                    'length': length,
                    'type': 'single_pair'
                }
            except nx.NetworkXNoPath:
                return {
                    'error': f'No path exists between {source} and {target}',
                    'type': 'single_pair'
                }

        elif source is not None:
            # Single source shortest paths
            paths = nx.shortest_path(G, source)
            lengths = nx.shortest_path_length(G, source)
            return {
                'paths': paths,
                'lengths': lengths,
                'type': 'single_source'
            }

        else:
            # All pairs shortest paths (sample for large graphs)
            if len(G.nodes) > 100:
                # For large graphs, compute only basic statistics
                return {
                    'average_path_length': nx.average_shortest_path_length(G),
                    'diameter': nx.diameter(G),
                    'type': 'statistics_only',
                    'note': 'Graph too large for full path computation'
                }
            else:
                # Compute full all-pairs shortest paths
                lengths = dict(nx.all_pairs_shortest_path_length(G))
                return {
                    'all_pairs_lengths': lengths,
                    'type': 'all_pairs'
                }

    def analyze_temporal_network(self, graphs: List[nx.Graph]) -> Dict[str, Any]:
        """
        Analyze temporal evolution of network properties.

        Args:
            graphs: List of graphs representing different time steps

        Returns:
            Dictionary of temporal analysis results
        """
        temporal_stats = []

        for i, G in enumerate(graphs):
            stats = self.compute_statistics(G)
            stats['time_step'] = i
            temporal_stats.append(stats)

        # Compute trends
        trends = {}
        metrics = ['num_nodes', 'num_edges', 'density', 'average_degree']

        for metric in metrics:
            values = [stats[metric] for stats in temporal_stats]
            trends[metric] = {
                'values': values,
                'change': values[-1] - values[0] if values else 0,
                'trend': 'increasing' if values and values[-1] > values[0] else 'decreasing'
            }

        return {
            'temporal_statistics': temporal_stats,
            'trends': trends,
            'time_steps': len(graphs)
        }

    def find_critical_nodes(self, G: nx.Graph, method: str = 'betweenness',
                           top_k: int = 10) -> List[Tuple[Any, float]]:
        """
        Find most critical nodes in the network.

        Args:
            G: NetworkX graph
            method: Centrality method for ranking
            top_k: Number of top nodes to return

        Returns:
            List of (node, centrality_score) tuples
        """
        centrality = self.compute_centrality(G, method)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        return sorted_nodes[:top_k]

    def compute_network_robustness(self, G: nx.Graph, attack_method: str = 'random',
                                  fractions: List[float] = None) -> Dict[str, List[float]]:
        """
        Compute network robustness under node removal.

        Args:
            G: NetworkX graph
            attack_method: Method for node removal ('random', 'degree', 'betweenness')
            fractions: Fractions of nodes to remove

        Returns:
            Dictionary of robustness metrics
        """
        if fractions is None:
            fractions = [0.1, 0.2, 0.3, 0.4, 0.5]

        original_size = len(G.nodes)
        remaining_fractions = []
        largest_component_sizes = []

        # Make a copy to avoid modifying original
        H = G.copy()

        for fraction in fractions:
            num_to_remove = int(fraction * original_size)

            if attack_method == 'random':
                nodes_to_remove = np.random.choice(list(H.nodes), num_to_remove, replace=False)
            elif attack_method == 'degree':
                degrees = dict(H.degree())
                nodes_to_remove = sorted(degrees.keys(), key=lambda x: degrees[x], reverse=True)[:num_to_remove]
            elif attack_method == 'betweenness':
                betweenness = nx.betweenness_centrality(H)
                nodes_to_remove = sorted(betweenness.keys(), key=lambda x: betweenness[x], reverse=True)[:num_to_remove]

            H.remove_nodes_from(nodes_to_remove)

            if len(H.nodes) > 0:
                largest_component = len(max(nx.connected_components(H), key=len))
                remaining_fractions.append(len(H.nodes) / original_size)
                largest_component_sizes.append(largest_component / original_size)
            else:
                remaining_fractions.append(0)
                largest_component_sizes.append(0)

        return {
            'remaining_fractions': remaining_fractions,
            'largest_component_sizes': largest_component_sizes,
            'attack_method': attack_method,
            'removal_fractions': fractions
        }

    # Centrality computation methods
    def _compute_degree_centrality(self, G: nx.Graph, normalized: bool = True) -> Dict[Any, float]:
        """Compute degree centrality."""
        return nx.degree_centrality(G)

    def _compute_betweenness_centrality(self, G: nx.Graph, normalized: bool = True) -> Dict[Any, float]:
        """Compute betweenness centrality."""
        return nx.betweenness_centrality(G, normalized=normalized)

    def _compute_closeness_centrality(self, G: nx.Graph, normalized: bool = True) -> Dict[Any, float]:
        """Compute closeness centrality."""
        return nx.closeness_centrality(G)

    def _compute_eigenvector_centrality(self, G: nx.Graph, normalized: bool = True) -> Dict[Any, float]:
        """Compute eigenvector centrality."""
        return nx.eigenvector_centrality(G)

    def _compute_pagerank(self, G: nx.Graph, normalized: bool = True) -> Dict[Any, float]:
        """Compute PageRank centrality."""
        return nx.pagerank(G)

    def _compute_katz_centrality(self, G: nx.Graph, normalized: bool = True) -> Dict[Any, float]:
        """Compute Katz centrality."""
        return nx.katz_centrality(G)

    # Community detection methods
    def _detect_communities_louvain(self, G: nx.Graph) -> Dict[Any, int]:
        """Detect communities using Louvain method."""
        try:
            partition = community_louvain.best_partition(G)
            return partition
        except ImportError:
            raise ImportError("python-louvain package required for Louvain method")

    def _detect_communities_girvan_newman(self, G: nx.Graph) -> Dict[Any, int]:
        """Detect communities using Girvan-Newman method."""
        from networkx.algorithms.community import girvan_newman

        # Get first level of communities
        communities = girvan_newman(G)
        first_partition = next(communities)

        # Convert to node -> community mapping
        partition = {}
        for i, community in enumerate(first_partition):
            for node in community:
                partition[node] = i

        return partition

    def _detect_communities_label_propagation(self, G: nx.Graph) -> Dict[Any, int]:
        """Detect communities using label propagation."""
        from networkx.algorithms.community import label_propagation_communities

        communities = label_propagation_communities(G)

        # Convert to node -> community mapping
        partition = {}
        for i, community in enumerate(communities):
            for node in community:
                partition[node] = i

        return partition
