"""Tests for atmosphere_audio.routing.core.visualization module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from atmosphere_audio.routing.core.visualization import visualize_network, logger


def _make_mock_network(nodes=None, edges=None, acoustic_params=None):
    """Helper to build a mock network with the interface the visualizer expects."""
    if nodes is None:
        nodes = []
    if edges is None:
        edges = []
    if acoustic_params is None:
        acoustic_params = {}

    mock_network = MagicMock()
    mock_network.node_positions = {n: (float(i), 0.0) for i, n in enumerate(nodes)}
    mock_network.graph.nodes.return_value = nodes
    mock_network.graph.edges.return_value = edges
    mock_network.graph.neighbors.return_value = []
    mock_network.acoustic_params = acoustic_params
    return mock_network


class TestRoutingVisualization:
    """Test the routing visualization functions."""

    @patch('atmosphere_audio.routing.core.visualization.plt')
    @patch('atmosphere_audio.routing.core.visualization.nx')
    def test_visualize_network_basic(self, mock_nx, mock_plt):
        """Test basic network visualization."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.Circle.return_value = MagicMock()

        # Mock network object with the proper interface
        mock_network = _make_mock_network(nodes=['node1'])

        # Test the function
        result = visualize_network(mock_network)

        # Verify matplotlib was called
        mock_plt.subplots.assert_called_once()
        assert result is not None

    @patch('atmosphere_audio.routing.core.visualization.plt')
    @patch('atmosphere_audio.routing.core.visualization.nx')
    def test_visualize_network_with_save_path(self, mock_nx, mock_plt):
        """Test network visualization with save path."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)
        mock_plt.Circle.return_value = MagicMock()

        # Mock network object with the proper interface
        mock_network = _make_mock_network(nodes=['node1'])

        # Test with save path
        result = visualize_network(mock_network, save_path="/tmp/test.png")

        # Verify savefig was called
        mock_fig.savefig.assert_called_once_with("/tmp/test.png", dpi=300, bbox_inches="tight")
        assert result is None  # Should return None when saving to file

    def test_logger_configuration(self):
        """Test that logger is properly configured."""
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
