"""
Tests for atmosphere_audio.routing.core.visualization module - comprehensive coverage.

This module tests the network visualization functionality for routing networks.
"""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from atmosphere_audio.routing.core.visualization import visualize_network


def _make_mock_network(nodes, edges, acoustic_params=None, node_positions=None):
    """Helper to create a properly configured mock network."""
    mock_network = MagicMock()
    mock_network.graph = MagicMock()
    mock_network.graph.nodes.return_value = nodes
    mock_network.graph.edges.return_value = edges
    mock_network.node_positions = node_positions or {
        n: (float(i * 10), 0.0) for i, n in enumerate(nodes)
    }
    mock_network.acoustic_params = acoustic_params or {}
    mock_network.graph.neighbors.return_value = []
    return mock_network


def _run_visualize(mock_network, save_path=None):
    """Helper to run visualize_network with all plt/nx functions mocked."""
    mock_fig = MagicMock()
    mock_ax = MagicMock()
    with patch('atmosphere_audio.routing.core.visualization.plt') as mock_plt, \
         patch('atmosphere_audio.routing.core.visualization.nx'):
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.Circle.return_value = MagicMock()
        mock_plt.Line2D.return_value = MagicMock()
        result = visualize_network(mock_network, save_path=save_path)
    return result, mock_fig, mock_ax


class TestNetworkVisualization:
    """Tests for network visualization functionality."""

    def test_visualize_network_basic(self):
        """Test basic network visualization."""
        mock_network = _make_mock_network(
            nodes=['node1', 'node2'],
            edges=[('node1', 'node2')],
            acoustic_params={
                ('node1', 'node2'): MagicMock(
                    reverb_density=0.8, delay_time=500, feedback=0.3, decay=0.5
                )
            }
        )
        mock_network.graph.neighbors.side_effect = lambda node: {
            'node1': ['node2'], 'node2': ['node1']
        }.get(node, [])

        result, _, _ = _run_visualize(mock_network)
        assert isinstance(result, BytesIO)

    def test_visualize_network_with_save_path(self):
        """Test network visualization with save path."""
        mock_network = _make_mock_network(nodes=['node1'], edges=[])

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        with patch('atmosphere_audio.routing.core.visualization.plt') as mock_plt, \
             patch('atmosphere_audio.routing.core.visualization.nx'):
            mock_plt.subplots.return_value = (mock_fig, mock_ax)
            mock_plt.Circle.return_value = MagicMock()
            mock_plt.Line2D.return_value = MagicMock()
            result = visualize_network(mock_network, save_path="test.png")

        # Should return None when saving to file
        assert result is None
        mock_fig.savefig.assert_called_once_with("test.png", dpi=300, bbox_inches="tight")

    def test_node_depth_calculation_high_connectivity(self):
        """Test node depth calculation for high connectivity nodes."""
        mock_network = _make_mock_network(
            nodes=['hub', 'leaf'],
            edges=[('hub', 'leaf')],
            acoustic_params={
                ('hub', 'leaf'): MagicMock(
                    reverb_density=0.9, delay_time=200, feedback=0.8, decay=0.3
                )
            }
        )
        mock_network.graph.neighbors.side_effect = lambda node: {
            'hub': ['leaf'], 'leaf': ['hub']
        }.get(node, [])

        result, _, _ = _run_visualize(mock_network)
        assert isinstance(result, BytesIO)

    def test_edge_color_high_density(self):
        """Test edge color calculation for high density connections."""
        mock_network = _make_mock_network(
            nodes=['A', 'B'],
            edges=[('A', 'B')],
            acoustic_params={
                ('A', 'B'): MagicMock(
                    reverb_density=0.9, delay_time=300, feedback=0.5, decay=0.7
                )
            }
        )
        mock_network.graph.neighbors.side_effect = lambda node: ['B'] if node == 'A' else ['A']

        result, _, _ = _run_visualize(mock_network)
        assert isinstance(result, BytesIO)

    def test_edge_color_low_density(self):
        """Test edge color calculation for low density connections."""
        mock_network = _make_mock_network(
            nodes=['A', 'B'],
            edges=[('A', 'B')],
            acoustic_params={
                ('A', 'B'): MagicMock(
                    reverb_density=0.2, delay_time=800, feedback=0.1, decay=0.9
                )
            }
        )
        mock_network.graph.neighbors.side_effect = lambda node: ['B'] if node == 'A' else ['A']

        result, _, _ = _run_visualize(mock_network)
        assert isinstance(result, BytesIO)

    def test_empty_network_visualization(self):
        """Test visualization with empty network."""
        mock_network = _make_mock_network(nodes=[], edges=[])

        result, _, _ = _run_visualize(mock_network)
        # Should still return BytesIO even for empty graph
        assert isinstance(result, BytesIO)

    def test_axis_limits_calculation(self):
        """Test axis limits calculation for different node positions."""
        mock_network = _make_mock_network(
            nodes=['node1', 'node2'],
            edges=[],
            node_positions={'node1': (-50, -30), 'node2': (50, 30)}
        )

        mock_fig = MagicMock()
        mock_ax = MagicMock()
        with patch('atmosphere_audio.routing.core.visualization.plt') as mock_plt, \
             patch('atmosphere_audio.routing.core.visualization.nx'):
            mock_plt.subplots.return_value = (mock_fig, mock_ax)
            mock_plt.Circle.return_value = MagicMock()
            mock_plt.Line2D.return_value = MagicMock()
            visualize_network(mock_network)

        # Check that axis limits were set with margin via ax.set_xlim / ax.set_ylim
        mock_ax.set_xlim.assert_called_once_with(-70, 70)  # -50-20, 50+20
        mock_ax.set_ylim.assert_called_once_with(-50, 50)  # -30-20, 30+20

