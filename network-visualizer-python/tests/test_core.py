"""
Test suite for Network Visualizer

Comprehensive tests covering core functionality, algorithms, layouts,
renderers, and I/O operations.
"""

import pytest
import networkx as nx
import numpy as np
from pathlib import Path
import tempfile
import json

from network_visualizer.core import NetworkVisualizer
from network_visualizer.core.algorithms import NetworkAnalyzer
from network_visualizer.core.layouts import LayoutManager
from network_visualizer.io import loader, exporter


class TestNetworkVisualizer:
    """Test NetworkVisualizer core functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.visualizer = NetworkVisualizer()

    def test_initialization(self):
        """Test visualizer initialization."""
        assert self.visualizer.backend == 'matplotlib'
        assert self.visualizer.layout_method == 'spring'
        assert isinstance(self.visualizer.analyzer, NetworkAnalyzer)
        assert isinstance(self.visualizer.layout_manager, LayoutManager)

    def test_load_sample_graph(self):
        """Test loading sample graphs."""
        G = self.visualizer.load_sample_graph('karate_club')
        assert isinstance(G, nx.Graph)
        assert len(G.nodes) > 0
        assert len(G.edges) > 0

    def test_compute_layout(self):
        """Test layout computation."""
        G = nx.karate_club_graph()
        pos = self.visualizer.compute_layout(G, 'spring')

        assert len(pos) == len(G.nodes)
        assert all(isinstance(coord, tuple) and len(coord) == 2 for coord in pos.values())
        assert all(isinstance(x, (int, float)) and isinstance(y, (int, float))
                  for coord in pos.values() for x, y in [coord])

    def test_compute_centrality(self):
        """Test centrality computation."""
        G = nx.karate_club_graph()
        centrality = self.visualizer.compute_centrality(G, 'degree')

        assert len(centrality) == len(G.nodes)
        assert all(isinstance(v, (int, float)) for v in centrality.values())
        assert all(0 <= v <= 1 for v in centrality.values())  # Normalized

    def test_compute_statistics(self):
        """Test network statistics computation."""
        G = nx.karate_club_graph()
        stats = self.visualizer.compute_statistics(G)

        required_keys = ['num_nodes', 'num_edges', 'density', 'average_degree']
        assert all(key in stats for key in required_keys)
        assert stats['num_nodes'] == len(G.nodes)
        assert stats['num_edges'] == len(G.edges)
        assert 0 <= stats['density'] <= 1

    def test_analyze_network(self):
        """Test comprehensive network analysis."""
        G = nx.karate_club_graph()
        analysis = self.visualizer.analyze_network(G, ['degree', 'betweenness'])

        assert 'statistics' in analysis
        assert 'centrality' in analysis
        assert 'degree' in analysis['centrality']
        assert 'betweenness' in analysis['centrality']
        assert len(analysis['centrality']['degree']) == len(G.nodes)


class TestNetworkAnalyzer:
    """Test NetworkAnalyzer algorithms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = NetworkAnalyzer()

    def test_centrality_methods(self):
        """Test all centrality computation methods."""
        G = nx.karate_club_graph()

        methods = ['degree', 'betweenness', 'closeness', 'eigenvector']
        for method in methods:
            centrality = self.analyzer.compute_centrality(G, method)
            assert len(centrality) == len(G.nodes)
            assert all(isinstance(v, (int, float)) for v in centrality.values())

    def test_statistics_computation(self):
        """Test statistics computation."""
        G = nx.karate_club_graph()
        stats = self.analyzer.compute_statistics(G)

        assert stats['num_nodes'] == 34
        assert stats['num_edges'] == 78
        assert isinstance(stats['density'], (int, float))
        assert isinstance(stats['average_degree'], (int, float))

    def test_community_detection(self):
        """Test community detection algorithms."""
        G = nx.karate_club_graph()

        # Test Louvain method (may not be available)
        try:
            communities = self.analyzer.detect_communities(G, 'louvain')
            assert len(communities) == len(G.nodes)
            assert all(isinstance(v, int) for v in communities.values())
        except ImportError:
            pass  # Skip if python-louvain not available

        # Test Girvan-Newman
        communities = self.analyzer.detect_communities(G, 'girvan_newman')
        assert len(communities) == len(G.nodes)
        assert all(isinstance(v, int) for v in communities.values())

    def test_shortest_paths(self):
        """Test shortest path computation."""
        G = nx.karate_club_graph()

        # Single pair
        result = self.analyzer.compute_shortest_paths(G, 0, 1)
        assert 'path' in result
        assert 'length' in result
        assert isinstance(result['path'], list)
        assert isinstance(result['length'], int)

        # Single source
        result = self.analyzer.compute_shortest_paths(G, 0)
        assert 'paths' in result
        assert 'lengths' in result
        assert len(result['paths']) > 0

    def test_network_robustness(self):
        """Test network robustness analysis."""
        G = nx.karate_club_graph()
        robustness = self.analyzer.compute_network_robustness(G, 'random', [0.1, 0.2])

        assert 'remaining_fractions' in robustness
        assert 'largest_component_sizes' in robustness
        assert len(robustness['remaining_fractions']) == 2
        assert len(robustness['largest_component_sizes']) == 2


class TestLayoutManager:
    """Test LayoutManager algorithms."""

    def setup_method(self):
        """Set up test fixtures."""
        self.layout_manager = LayoutManager()

    def test_layout_computation(self):
        """Test layout computation for different algorithms."""
        G = nx.karate_club_graph()

        layouts = ['spring', 'circular', 'random', 'shell']
        for layout in layouts:
            pos = self.layout_manager.compute_layout(G, layout)
            assert len(pos) == len(G.nodes)
            assert all(isinstance(coord, tuple) and len(coord) == 2 for coord in pos.values())

    def test_spring_layout(self):
        """Test spring layout specifically."""
        G = nx.karate_club_graph()
        pos = self.layout_manager.compute_layout(G, 'spring')

        # Check that positions are reasonable (not all at origin)
        x_coords = [x for x, y in pos.values()]
        y_coords = [y for x, y in pos.values()]

        assert np.std(x_coords) > 0.1  # Some spread in x
        assert np.std(y_coords) > 0.1  # Some spread in y

    def test_circular_layout(self):
        """Test circular layout."""
        G = nx.cycle_graph(10)
        pos = self.layout_manager.compute_layout(G, 'circular')

        # In a circular layout, points should be approximately equally spaced on a circle
        angles = []
        for node in range(10):
            x, y = pos[node]
            angle = np.arctan2(y, x)
            angles.append(angle)

        angles.sort()
        angle_diffs = np.diff(angles + [angles[0] + 2*np.pi])
        avg_diff = np.mean(angle_diffs[:-1])  # Exclude wrap-around

        # Should be close to 2π/10 = 0.628 radians
        expected_diff = 2 * np.pi / 10
        assert abs(avg_diff - expected_diff) < 0.1

    def test_hierarchical_layout(self):
        """Test hierarchical layout."""
        # Create a simple tree
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)])

        pos = self.layout_manager.compute_layout(G, 'hierarchical')

        # Root should be at top
        root_x, root_y = pos[0]

        # Children should be below root
        for child in [1, 2]:
            child_x, child_y = pos[child]
            assert child_y < root_y

    def test_radial_layout(self):
        """Test radial layout."""
        # Create a star graph
        G = nx.star_graph(5)
        pos = self.layout_manager.compute_layout(G, 'radial')

        # Center node should be at origin
        center_x, center_y = pos[0]
        assert abs(center_x) < 1e-10
        assert abs(center_y) < 1e-10

        # Leaf nodes should be at equal distance from center
        distances = []
        for node in range(1, 6):
            x, y = pos[node]
            distance = np.sqrt(x**2 + y**2)
            distances.append(distance)

        # All distances should be approximately equal
        distance_std = np.std(distances)
        assert distance_std < 0.1


class TestDataIO:
    """Test data input/output functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.test_graph = nx.karate_club_graph()

    def test_json_io(self):
        """Test JSON format I/O."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Export to JSON
            exporter.export(self.test_graph, tmp_path, format='json')

            # Import from JSON
            imported_graph = loader.load(tmp_path, format='json')

            # Verify structure
            assert len(imported_graph.nodes) == len(self.test_graph.nodes)
            assert len(imported_graph.edges) == len(self.test_graph.edges)

        finally:
            tmp_path.unlink()

    def test_csv_io(self):
        """Test CSV format I/O."""
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Export to CSV
            exporter.export(self.test_graph, tmp_path, format='csv')

            # Import from CSV
            imported_graph = loader.load(tmp_path, format='csv')

            # Verify structure (may have different node labels)
            assert len(imported_graph.edges) == len(self.test_graph.edges)

        finally:
            tmp_path.unlink()

    def test_edge_list_io(self):
        """Test edge list format I/O."""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Export to edge list
            exporter.export(self.test_graph, tmp_path, format='txt')

            # Import from edge list
            imported_graph = loader.load(tmp_path, format='txt')

            # Verify structure
            assert len(imported_graph.edges) == len(self.test_graph.edges)

        finally:
            tmp_path.unlink()

    def test_format_auto_detection(self):
        """Test automatic format detection."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Export without specifying format
            exporter.export(self.test_graph, tmp_path)

            # Import without specifying format
            imported_graph = loader.load(tmp_path)

            assert len(imported_graph.nodes) == len(self.test_graph.nodes)

        finally:
            tmp_path.unlink()


class TestIntegration:
    """Integration tests for complete workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.visualizer = NetworkVisualizer()

    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow."""
        # Load sample network
        G = self.visualizer.load_sample_graph('karate_club')

        # Compute analysis
        analysis = self.visualizer.analyze_network(G)

        # Verify all components are present
        assert 'statistics' in analysis
        assert 'centrality' in analysis
        assert 'communities' in analysis
        assert 'paths' in analysis

        # Verify statistics are reasonable
        stats = analysis['statistics']
        assert stats['num_nodes'] == 34
        assert stats['num_edges'] == 78
        assert 0 < stats['density'] < 1

    def test_visualization_workflow(self):
        """Test complete visualization workflow."""
        G = self.visualizer.load_sample_graph('karate_club')

        # Compute layout
        pos = self.visualizer.compute_layout(G)

        # Generate static visualization
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            output_path = tmp.name

        try:
            self.visualizer.visualize_static(G, pos, output_file=output_path)
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0

        finally:
            Path(output_path).unlink()

    def test_io_workflow(self):
        """Test complete I/O workflow."""
        original_graph = self.visualizer.load_sample_graph('karate_club')

        # Export to temporary file
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            # Export and re-import
            self.visualizer.save_network(original_graph, tmp_path)
            imported_graph = self.visualizer.load_network(tmp_path)

            # Verify structure preservation
            assert len(imported_graph.nodes) == len(original_graph.nodes)
            assert len(imported_graph.edges) == len(original_graph.edges)

        finally:
            tmp_path.unlink()


if __name__ == '__main__':
    pytest.main([__file__])
