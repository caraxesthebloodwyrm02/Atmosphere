"""
Network Visualizer Core Implementation

Main visualization engine for network analysis and visualization,
inspired by Gephi but built with modern Python libraries.
"""

import networkx as nx
import matplotlib.pyplot as plt
import plotly.graph_objects as go
from pathlib import Path
import json
from typing import Dict, List, Tuple, Optional, Union, Any
import numpy as np
import pandas as pd
from collections import defaultdict

from .algorithms import NetworkAnalyzer
from .layouts import LayoutManager
from .renderers import RendererManager


class NetworkVisualizer:
    """
    Advanced network visualization and analysis toolkit.

    Provides comprehensive network analysis, visualization, and export capabilities
    with multiple backends and algorithms inspired by Gephi.
    """

    def __init__(self,
                 backend: str = 'matplotlib',
                 layout_method: str = 'spring',
                 figsize: Tuple[int, int] = (12, 8)):
        """
        Initialize the Network Visualizer.

        Args:
            backend: Default rendering backend ('matplotlib', 'plotly', 'graphviz')
            layout_method: Default layout algorithm
            figsize: Default figure size for static plots
        """
        self.backend = backend
        self.layout_method = layout_method
        self.figsize = figsize

        # Initialize components
        self.analyzer = NetworkAnalyzer()
        self.layout_manager = LayoutManager()
        self.renderer = RendererManager()

        # Configuration
        self.config = {
            'node_size_range': (100, 1000),
            'edge_width_range': (0.5, 5.0),
            'color_map': 'viridis',
            'dpi': 300,
            'font_size': 8,
        }

    def load_network(self, filepath: Union[str, Path]) -> nx.Graph:
        """
        Load network from file.

        Supports GraphML, GML, JSON, CSV, and edge list formats.

        Args:
            filepath: Path to network file

        Returns:
            NetworkX graph object
        """
        filepath = Path(filepath)

        if filepath.suffix.lower() in ['.graphml', '.xml']:
            return nx.read_graphml(filepath)
        elif filepath.suffix.lower() == '.gml':
            return nx.read_gml(filepath)
        elif filepath.suffix.lower() == '.json':
            with open(filepath, 'r') as f:
                data = json.load(f)
            return nx.node_link_graph(data)
        elif filepath.suffix.lower() in ['.csv', '.txt']:
            return self._load_edge_list(filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    def save_network(self, G: nx.Graph, filepath: Union[str, Path]) -> None:
        """
        Save network to file.

        Args:
            G: NetworkX graph
            filepath: Output file path
        """
        filepath = Path(filepath)

        if filepath.suffix.lower() in ['.graphml', '.xml']:
            nx.write_graphml(G, filepath)
        elif filepath.suffix.lower() == '.gml':
            nx.write_gml(G, filepath)
        elif filepath.suffix.lower() == '.json':
            data = nx.node_link_data(G)
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif filepath.suffix.lower() in ['.csv', '.txt']:
            self._save_edge_list(G, filepath)
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")

    def load_sample_graph(self, name: str) -> nx.Graph:
        """
        Load a sample network for testing and demonstration.

        Args:
            name: Sample network name

        Returns:
            NetworkX graph object
        """
        samples = {
            'karate_club': nx.karate_club_graph,
            'davis_southern_women': nx.davis_southern_women_graph,
            'florentine_families': nx.florentine_families_graph,
            'les_miserables': lambda: nx.les_miserables_graph(),
            'football': nx.football_network,
        }

        if name not in samples:
            available = list(samples.keys())
            raise ValueError(f"Unknown sample '{name}'. Available: {available}")

        return samples[name]()

    def generate_sample(self, type_name: str, **kwargs) -> nx.Graph:
        """
        Generate synthetic network for testing.

        Args:
            type_name: Type of network to generate
            **kwargs: Network generation parameters

        Returns:
            Generated network
        """
        generators = {
            'erdos_renyi': lambda: nx.erdos_renyi_graph(
                kwargs.get('n', 100), kwargs.get('p', 0.1)
            ),
            'barabasi_albert': lambda: nx.barabasi_albert_graph(
                kwargs.get('n', 100), kwargs.get('m', 3)
            ),
            'watts_strogatz': lambda: nx.watts_strogatz_graph(
                kwargs.get('n', 100), kwargs.get('k', 4), kwargs.get('p', 0.1)
            ),
            'karate': lambda: nx.karate_club_graph(),
        }

        if type_name not in generators:
            available = list(generators.keys())
            raise ValueError(f"Unknown generator '{type_name}'. Available: {available}")

        return generators[type_name]()

    def compute_layout(self, G: nx.Graph, method: str = None, **kwargs) -> Dict:
        """
        Compute node positions using layout algorithm.

        Args:
            G: Network graph
            method: Layout method (uses default if None)
            **kwargs: Layout-specific parameters

        Returns:
            Dictionary of node positions
        """
        if method is None:
            method = self.layout_method

        return self.layout_manager.compute_layout(G, method, **kwargs)

    def compute_centrality(self, G: nx.Graph, method: str = 'degree') -> Dict:
        """
        Compute centrality metrics for network.

        Args:
            G: Network graph
            method: Centrality method

        Returns:
            Dictionary of centrality values
        """
        return self.analyzer.compute_centrality(G, method)

    def compute_statistics(self, G: nx.Graph) -> Dict:
        """
        Compute comprehensive network statistics.

        Args:
            G: Network graph

        Returns:
            Dictionary of network statistics
        """
        return self.analyzer.compute_statistics(G)

    def visualize_static(self,
                        G: nx.Graph,
                        pos: Dict = None,
                        output_file: str = None,
                        backend: str = None,
                        show_labels: bool = False,
                        node_colors: Dict = None,
                        node_sizes: Dict = None,
                        **kwargs) -> None:
        """
        Generate static network visualization.

        Args:
            G: Network graph
            pos: Node positions (computed if None)
            output_file: Output file path
            backend: Rendering backend
            show_labels: Whether to show node labels
            node_colors: Node color mapping
            node_sizes: Node size mapping
            **kwargs: Additional visualization parameters
        """
        if backend is None:
            backend = self.backend

        if pos is None:
            pos = self.compute_layout(G)

        # Prepare visualization data
        node_colors = node_colors or {}
        node_sizes = node_sizes or {}

        self.renderer.render_static(
            G, pos, output_file, backend, show_labels,
            node_colors, node_sizes, self.config, **kwargs
        )

    def visualize_interactive(self,
                             G: nx.Graph,
                             pos: Dict = None,
                             node_attributes: Dict = None,
                             **kwargs) -> None:
        """
        Launch interactive network visualization.

        Args:
            G: Network graph
            pos: Node positions
            node_attributes: Additional node attributes for tooltips
            **kwargs: Additional parameters
        """
        if pos is None:
            pos = self.compute_layout(G)

        self.renderer.render_interactive(G, pos, node_attributes, **kwargs)

    def analyze_network(self, G: nx.Graph, metrics: List[str] = None) -> Dict:
        """
        Perform comprehensive network analysis.

        Args:
            G: Network graph
            metrics: List of metrics to compute

        Returns:
            Dictionary of analysis results
        """
        if metrics is None:
            metrics = ['degree', 'betweenness', 'closeness', 'eigenvector']

        results = {
            'statistics': self.compute_statistics(G),
            'centrality': {},
            'communities': None,
            'paths': None,
        }

        # Compute centrality metrics
        for metric in metrics:
            results['centrality'][metric] = self.compute_centrality(G, metric)

        # Detect communities
        results['communities'] = self.analyzer.detect_communities(G)

        # Compute shortest paths
        results['paths'] = self.analyzer.compute_shortest_paths(G)

        return results

    def export_analysis(self, analysis: Dict, filepath: Union[str, Path]) -> None:
        """
        Export analysis results to file.

        Args:
            analysis: Analysis results dictionary
            filepath: Output file path
        """
        filepath = Path(filepath)

        if filepath.suffix.lower() == '.json':
            with open(filepath, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
        elif filepath.suffix.lower() == '.csv':
            self._export_analysis_csv(analysis, filepath)
        else:
            raise ValueError(f"Unsupported export format: {filepath.suffix}")

    def save_analysis(self, analysis: Dict, filepath: Union[str, Path]) -> None:
        """
        Alias for export_analysis for backward compatibility.
        """
        self.export_analysis(analysis, filepath)

    def _load_edge_list(self, filepath: Path) -> nx.Graph:
        """Load network from edge list format."""
        try:
            # Try weighted edge list first
            G = nx.read_weighted_edgelist(filepath, delimiter=',')
        except:
            try:
                # Try unweighted edge list
                G = nx.read_edgelist(filepath, delimiter=',')
            except:
                # Try space-delimited
                G = nx.read_edgelist(filepath)
        return G

    def _save_edge_list(self, G: nx.Graph, filepath: Path) -> None:
        """Save network as edge list."""
        if any('weight' in G[u][v] for u, v in G.edges()):
            nx.write_weighted_edgelist(G, filepath)
        else:
            nx.write_edgelist(G, filepath, delimiter=',')

    def _export_analysis_csv(self, analysis: Dict, filepath: Path) -> None:
        """Export analysis results to CSV format."""
        # Create node-level metrics DataFrame
        centrality_data = analysis.get('centrality', {})
        if centrality_data:
            df_data = {}
            for metric, values in centrality_data.items():
                df_data[metric] = values

            df = pd.DataFrame(df_data)
            df.to_csv(filepath)
