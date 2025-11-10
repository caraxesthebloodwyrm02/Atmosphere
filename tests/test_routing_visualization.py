"""Tests for atmosphere_audio.routing.core.visualization module."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from atmosphere_audio.routing.core.visualization import visualize_network, logger


class TestRoutingVisualization:
    """Test the routing visualization functions."""

    @patch('atmosphere_audio.routing.core.visualization.plt')
    def test_visualize_network_basic(self, mock_plt):
        """Test basic network visualization."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        # Mock network object
        mock_network = Mock()
        mock_network.nodes = [{'id': 'node1', 'position': [0, 0, 0]}]
        mock_network.connections = []

        # Test the function
        result = visualize_network(mock_network)

        # Verify matplotlib was called
        mock_plt.subplots.assert_called_once()
        assert result is not None

    @patch('atmosphere_audio.routing.core.visualization.plt')
    def test_visualize_network_with_save_path(self, mock_plt):
        """Test network visualization with save path."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_plt.subplots.return_value = (mock_fig, mock_ax)

        # Mock network object
        mock_network = Mock()
        mock_network.nodes = [{'id': 'node1', 'position': [0, 0, 0]}]
        mock_network.connections = []

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
