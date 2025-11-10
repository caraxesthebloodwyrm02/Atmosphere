"""
Data Input/Output Module

Handles loading and saving network data in multiple formats,
providing unified interface for data exchange.
"""

import networkx as nx
import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional, Union
import csv
import io


class DataLoader:
    """
    Network data loading utilities.

    Supports multiple formats: GraphML, GML, JSON, CSV, edge lists,
    adjacency matrices, and custom formats.
    """

    def __init__(self):
        """Initialize the data loader."""
        self.supported_formats = {
            '.graphml': self._load_graphml,
            '.gml': self._load_gml,
            '.json': self._load_json,
            '.csv': self._load_csv,
            '.txt': self._load_edge_list,
            '.edgelist': self._load_edge_list,
            '.adj': self._load_adjacency_matrix,
            '.mat': self._load_adjacency_matrix,
        }

    def load(self, filepath: Union[str, Path], format: str = None, **kwargs) -> nx.Graph:
        """
        Load network from file.

        Args:
            filepath: Path to data file
            format: Explicit format specification (auto-detected if None)
            **kwargs: Format-specific loading parameters

        Returns:
            NetworkX graph object
        """
        filepath = Path(filepath)

        # Auto-detect format if not specified
        if format is None:
            format = filepath.suffix.lower()

        if format not in self.supported_formats:
            available = list(self.supported_formats.keys())
            raise ValueError(f"Unsupported format '{format}'. Available: {available}")

        return self.supported_formats[format](filepath, **kwargs)

    def _load_graphml(self, filepath: Path, **kwargs) -> nx.Graph:
        """Load GraphML format."""
        return nx.read_graphml(filepath, **kwargs)

    def _load_gml(self, filepath: Path, **kwargs) -> nx.Graph:
        """Load GML format."""
        return nx.read_gml(filepath, **kwargs)

    def _load_json(self, filepath: Path, **kwargs) -> nx.Graph:
        """Load JSON format."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Try different JSON formats
        if 'nodes' in data and 'edges' in data:
            return self._from_node_link_format(data)
        elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
            return self._from_adjacency_list(data)
        else:
            # Try NetworkX node-link format
            try:
                return nx.node_link_graph(data)
            except:
                raise ValueError("Unsupported JSON format")

    def _load_csv(self, filepath: Path, **kwargs) -> nx.Graph:
        """Load CSV format."""
        delimiter = kwargs.get('delimiter', ',')
        has_header = kwargs.get('header', True)
        source_col = kwargs.get('source', 0)
        target_col = kwargs.get('target', 1)
        weight_col = kwargs.get('weight', None)

        # Read CSV
        df = pd.read_csv(filepath, delimiter=delimiter, header=0 if has_header else None)

        # Extract columns
        if has_header:
            source_data = df.iloc[:, source_col]
            target_data = df.iloc[:, target_col]
            weight_data = df.iloc[:, weight_col] if weight_col is not None else None
        else:
            source_data = df.iloc[:, source_col]
            target_data = df.iloc[:, target_col]
            weight_data = df.iloc[:, weight_col] if weight_col is not None and weight_col < len(df.columns) else None

        # Create edge list
        edges = list(zip(source_data, target_data))

        # Create graph
        if weight_data is not None:
            weighted_edges = [(s, t, w) for (s, t), w in zip(edges, weight_data)]
            G = nx.Graph()
            G.add_weighted_edges_from(weighted_edges)
        else:
            G = nx.Graph()
            G.add_edges_from(edges)

        return G

    def _load_edge_list(self, filepath: Path, **kwargs) -> nx.Graph:
        """Load edge list format."""
        delimiter = kwargs.get('delimiter', None)  # Auto-detect
        comments = kwargs.get('comments', '#')

        try:
            # Try weighted edge list
            return nx.read_weighted_edgelist(filepath, delimiter=delimiter, comments=comments)
        except:
            try:
                # Try unweighted edge list
                return nx.read_edgelist(filepath, delimiter=delimiter, comments=comments)
            except Exception as e:
                raise ValueError(f"Failed to load edge list: {e}")

    def _load_adjacency_matrix(self, filepath: Path, **kwargs) -> nx.Graph:
        """Load adjacency matrix format."""
        delimiter = kwargs.get('delimiter', ',')

        # Read matrix
        matrix = []
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    row = [float(x) for x in line.split(delimiter)]
                    matrix.append(row)

        if not matrix:
            raise ValueError("Empty adjacency matrix")

        # Convert to NetworkX graph
        return nx.from_numpy_array(np.array(matrix))

    def _from_node_link_format(self, data: Dict) -> nx.Graph:
        """Create graph from custom node-link format."""
        G = nx.Graph()

        # Add nodes
        for node_data in data.get('nodes', []):
            node_id = node_data['id']
            attrs = {k: v for k, v in node_data.items() if k != 'id'}
            G.add_node(node_id, **attrs)

        # Add edges
        for edge_data in data.get('edges', []):
            source = edge_data['source']
            target = edge_data['target']
            attrs = {k: v for k, v in edge_data.items() if k not in ['source', 'target']}
            G.add_edge(source, target, **attrs)

        return G

    def _from_adjacency_list(self, adj_list: List[List]) -> nx.Graph:
        """Create graph from adjacency list."""
        G = nx.Graph()
        for i, neighbors in enumerate(adj_list):
            for j in neighbors:
                if j > i:  # Avoid duplicate edges
                    G.add_edge(i, j)
        return G


class DataExporter:
    """
    Network data export utilities.

    Supports exporting network data to multiple formats with customizable options.
    """

    def __init__(self):
        """Initialize the data exporter."""
        self.supported_formats = {
            '.graphml': self._export_graphml,
            '.gml': self._export_gml,
            '.json': self._export_json,
            '.csv': self._export_csv,
            '.txt': self._export_edge_list,
            '.edgelist': self._export_edge_list,
            '.adj': self._export_adjacency_matrix,
            '.mat': self._export_adjacency_matrix,
        }

    def export(self, G: nx.Graph, filepath: Union[str, Path], format: str = None, **kwargs) -> None:
        """
        Export network to file.

        Args:
            G: NetworkX graph
            filepath: Output file path
            format: Explicit format specification (auto-detected if None)
            **kwargs: Format-specific export parameters
        """
        filepath = Path(filepath)

        # Auto-detect format if not specified
        if format is None:
            format = filepath.suffix.lower()

        if format not in self.supported_formats:
            available = list(self.supported_formats.keys())
            raise ValueError(f"Unsupported format '{format}'. Available: {available}")

        self.supported_formats[format](G, filepath, **kwargs)

    def _export_graphml(self, G: nx.Graph, filepath: Path, **kwargs) -> None:
        """Export to GraphML format."""
        nx.write_graphml(G, filepath, **kwargs)

    def _export_gml(self, G: nx.Graph, filepath: Path, **kwargs) -> None:
        """Export to GML format."""
        nx.write_gml(G, filepath, **kwargs)

    def _export_json(self, G: nx.Graph, filepath: Path, **kwargs) -> None:
        """Export to JSON format."""
        format_type = kwargs.get('format', 'node_link')

        if format_type == 'node_link':
            data = nx.node_link_data(G)
        elif format_type == 'custom':
            data = self._to_custom_format(G)
        else:
            data = nx.node_link_data(G)

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)

    def _export_csv(self, G: nx.Graph, filepath: Path, **kwargs) -> None:
        """Export to CSV format."""
        delimiter = kwargs.get('delimiter', ',')
        include_weights = kwargs.get('weights', True)

        edges = []
        for u, v, data in G.edges(data=True):
            row = [u, v]
            if include_weights and 'weight' in data:
                row.append(data['weight'])
            edges.append(row)

        # Write CSV
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f, delimiter=delimiter)
            writer.writerows(edges)

    def _export_edge_list(self, G: nx.Graph, filepath: Path, **kwargs) -> None:
        """Export to edge list format."""
        delimiter = kwargs.get('delimiter', '\t')

        if any('weight' in G[u][v] for u, v in G.edges()):
            nx.write_weighted_edgelist(G, filepath, delimiter=delimiter)
        else:
            nx.write_edgelist(G, filepath, delimiter=delimiter)

    def _export_adjacency_matrix(self, G: nx.Graph, filepath: Path, **kwargs) -> None:
        """Export to adjacency matrix format."""
        delimiter = kwargs.get('delimiter', ',')

        # Get adjacency matrix
        adj_matrix = nx.to_numpy_array(G)

        # Write matrix
        with open(filepath, 'w', encoding='utf-8') as f:
            for row in adj_matrix:
                line = delimiter.join(f"{x:g}" for x in row)
                f.write(line + '\n')

    def _to_custom_format(self, G: nx.Graph) -> Dict:
        """Convert graph to custom JSON format."""
        nodes = []
        for node, attrs in G.nodes(data=True):
            node_data = {'id': node}
            node_data.update(attrs)
            nodes.append(node_data)

        edges = []
        for source, target, attrs in G.edges(data=True):
            edge_data = {'source': source, 'target': target}
            edge_data.update(attrs)
            edges.append(edge_data)

        return {'nodes': nodes, 'edges': edges}


class FormatRegistry:
    """
    Registry for custom data formats and loaders.

    Allows extending the I/O system with custom formats and specialized loaders.
    """

    def __init__(self):
        """Initialize the format registry."""
        self.loaders = {}
        self.exporters = {}

    def register_loader(self, format_name: str, loader_func: callable) -> None:
        """
        Register a custom loader function.

        Args:
            format_name: Format identifier (e.g., '.custom')
            loader_func: Function that takes filepath and returns nx.Graph
        """
        self.loaders[format_name.lower()] = loader_func

    def register_exporter(self, format_name: str, exporter_func: callable) -> None:
        """
        Register a custom exporter function.

        Args:
            format_name: Format identifier (e.g., '.custom')
            exporter_func: Function that takes G and filepath
        """
        self.exporters[format_name.lower()] = exporter_func

    def get_loader(self, format_name: str) -> callable:
        """Get registered loader for format."""
        return self.loaders.get(format_name.lower())

    def get_exporter(self, format_name: str) -> callable:
        """Get registered exporter for format."""
        return self.exporters.get(format_name.lower())


# Global instances
loader = DataLoader()
exporter = DataExporter()
registry = FormatRegistry()
