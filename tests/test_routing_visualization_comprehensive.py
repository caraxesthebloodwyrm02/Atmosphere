"""
Tests for atmosphere_audio.routing.core.visualization module - comprehensive coverage.

This module tests the network visualization functionality for routing networks.
"""

from io import BytesIO
from unittest.mock import MagicMock, patch

import pytest

from atmosphere_audio.routing.core.visualization import visualize_network


class TestNetworkVisualization:
    """Tests for network visualization functionality."""

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.Circle')
    @patch('matplotlib.pyplot.annotate')
    @patch('matplotlib.pyplot.legend')
    @patch('matplotlib.pyplot.imshow')
    @patch('matplotlib.pyplot.grid')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.yticks')
    @patch('matplotlib.pyplot.xlim')
    @patch('matplotlib.pyplot.ylim')
    @patch('matplotlib.pyplot.subplots')
    @patch('networkx.draw_networkx_nodes')
    @patch('networkx.draw_networkx_edges')
    def test_visualize_network_basic(self, mock_draw_edges, mock_draw_nodes, mock_subplots,
                                   mock_ylim, mock_xlim, mock_yticks, mock_xticks, mock_title,
                                   mock_grid, mock_imshow, mock_legend, mock_annotate,
                                   mock_circle, mock_tight_layout, mock_savefig):
        """Test basic network visualization."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # Mock network object
        mock_network = MagicMock()
        mock_network.graph = MagicMock()
        mock_network.graph.nodes.return_value = ['node1', 'node2']
        mock_network.graph.edges.return_value = [('node1', 'node2')]
        mock_network.node_positions = {'node1': (0, 0), 'node2': (10, 10)}
        mock_network.acoustic_params = {
            ('node1', 'node2'): MagicMock(
                reverb_density=0.8,
                delay_time=500,
                feedback=0.3,
                decay=0.5
            )
        }

        # Mock network neighbors
        mock_network.graph.neighbors.side_effect = lambda node: {
            'node1': ['node2'],
            'node2': ['node1']
        }.get(node, [])

        result = visualize_network(mock_network)

        # Verify matplotlib calls were made
        mock_subplots.assert_called_once()
        assert isinstance(result, BytesIO)

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.Circle')
    @patch('matplotlib.pyplot.annotate')
    @patch('matplotlib.pyplot.legend')
    @patch('matplotlib.pyplot.imshow')
    @patch('matplotlib.pyplot.grid')
    @patch('matplotlib.pyplot.title')
    @patch('matplotlib.pyplot.xticks')
    @patch('matplotlib.pyplot.yticks')
    @patch('matplotlib.pyplot.xlim')
    @patch('matplotlib.pyplot.ylim')
    @patch('matplotlib.pyplot.subplots')
    @patch('networkx.draw_networkx_nodes')
    @patch('networkx.draw_networkx_edges')
    def test_visualize_network_with_save_path(self, mock_draw_edges, mock_draw_nodes, mock_subplots,
                                             mock_ylim, mock_xlim, mock_yticks, mock_xticks, mock_title,
                                             mock_grid, mock_imshow, mock_legend, mock_annotate,
                                             mock_circle, mock_tight_layout, mock_savefig):
        """Test network visualization with save path."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # Mock network object
        mock_network = MagicMock()
        mock_network.graph = MagicMock()
        mock_network.graph.nodes.return_value = ['node1']
        mock_network.graph.edges.return_value = []
        mock_network.node_positions = {'node1': (0, 0)}
        mock_network.acoustic_params = {}

        mock_network.graph.neighbors.return_value = []

        result = visualize_network(mock_network, save_path="test.png")

        # Should return None when saving to file
        assert result is None
        mock_savefig.assert_called_once_with(
            "test.png",
            dpi=300,
            bbox_inches="tight",
            facecolor=mock_fig.get_facecolor(),
            edgecolor="none",
        )

    def test_node_depth_calculation_high_connectivity(self):
        """Test node depth calculation for high connectivity nodes."""
        with patch('matplotlib.pyplot.savefig'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.Circle'), \
             patch('matplotlib.pyplot.annotate'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.imshow'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.xticks'), \
             patch('matplotlib.pyplot.yticks'), \
             patch('matplotlib.pyplot.xlim'), \
             patch('matplotlib.pyplot.ylim'), \
             patch('matplotlib.pyplot.subplots'), \
             patch('networkx.draw_networkx_nodes'), \
             patch('networkx.draw_networkx_edges'):

            # Mock network with high connectivity node
            mock_network = MagicMock()
            mock_network.graph = MagicMock()
            mock_network.graph.nodes.return_value = ['hub', 'leaf']
            mock_network.graph.edges.return_value = [('hub', 'leaf')]
            mock_network.node_positions = {'hub': (0, 0), 'leaf': (10, 0)}

            # High connectivity parameters
            mock_network.acoustic_params = {
                ('hub', 'leaf'): MagicMock(
                    reverb_density=0.9,  # High density
                    delay_time=200,      # Low delay
                    feedback=0.8,        # High feedback
                    decay=0.3
                )
            }

            mock_network.graph.neighbors.side_effect = lambda node: {
                'hub': ['leaf'],
                'leaf': ['hub']
            }.get(node, [])

            result = visualize_network(mock_network)
            assert isinstance(result, BytesIO)

    def test_edge_color_high_density(self):
        """Test edge color calculation for high density connections."""
        with patch('matplotlib.pyplot.savefig'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.Circle'), \
             patch('matplotlib.pyplot.annotate'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.imshow'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.xticks'), \
             patch('matplotlib.pyplot.yticks'), \
             patch('matplotlib.pyplot.xlim'), \
             patch('matplotlib.pyplot.ylim'), \
             patch('matplotlib.pyplot.subplots'), \
             patch('networkx.draw_networkx_nodes'), \
             patch('networkx.draw_networkx_edges'):

            mock_network = MagicMock()
            mock_network.graph = MagicMock()
            mock_network.graph.nodes.return_value = ['A', 'B']
            mock_network.graph.edges.return_value = [('A', 'B')]
            mock_network.node_positions = {'A': (0, 0), 'B': (10, 0)}

            # High density - should produce cool colors (high blue)
            mock_network.acoustic_params = {
                ('A', 'B'): MagicMock(
                    reverb_density=0.9,  # High density
                    delay_time=300,
                    feedback=0.5,
                    decay=0.7
                )
            }

            mock_network.graph.neighbors.side_effect = lambda node: ['B'] if node == 'A' else ['A']

            result = visualize_network(mock_network)
            assert isinstance(result, BytesIO)

    def test_edge_color_low_density(self):
        """Test edge color calculation for low density connections."""
        with patch('matplotlib.pyplot.savefig'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.Circle'), \
             patch('matplotlib.pyplot.annotate'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.imshow'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.xticks'), \
             patch('matplotlib.pyplot.yticks'), \
             patch('matplotlib.pyplot.xlim'), \
             patch('matplotlib.pyplot.ylim'), \
             patch('matplotlib.pyplot.subplots'), \
             patch('networkx.draw_networkx_nodes'), \
             patch('networkx.draw_networkx_edges'):

            mock_network = MagicMock()
            mock_network.graph = MagicMock()
            mock_network.graph.nodes.return_value = ['A', 'B']
            mock_network.graph.edges.return_value = [('A', 'B')]
            mock_network.node_positions = {'A': (0, 0), 'B': (10, 0)}

            # Low density - should produce warm colors (high red)
            mock_network.acoustic_params = {
                ('A', 'B'): MagicMock(
                    reverb_density=0.2,  # Low density
                    delay_time=800,
                    feedback=0.1,
                    decay=0.9
                )
            }

            mock_network.graph.neighbors.side_effect = lambda node: ['B'] if node == 'A' else ['A']

            result = visualize_network(mock_network)
            assert isinstance(result, BytesIO)

    def test_empty_network_visualization(self):
        """Test visualization with empty network."""
        with patch('matplotlib.pyplot.savefig') as mock_savefig, \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.Circle'), \
             patch('matplotlib.pyplot.annotate'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.imshow'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.xticks'), \
             patch('matplotlib.pyplot.yticks'), \
             patch('matplotlib.pyplot.xlim'), \
             patch('matplotlib.pyplot.ylim'), \
             patch('matplotlib.pyplot.subplots') as mock_subplots, \
             patch('networkx.draw_networkx_nodes'), \
             patch('networkx.draw_networkx_edges'):

            # Mock matplotlib components
            mock_fig = MagicMock()
            mock_ax = MagicMock()
            mock_subplots.return_value = (mock_fig, mock_ax)

            # Mock empty network
            mock_network = MagicMock()
            mock_network.graph = MagicMock()
            mock_network.graph.nodes.return_value = []
            mock_network.graph.edges.return_value = []
            mock_network.node_positions = {}
            mock_network.acoustic_params = {}

            mock_network.graph.neighbors.return_value = []

            result = visualize_network(mock_network)

            # Should still return BytesIO even for empty graph
            assert isinstance(result, BytesIO)

    def test_axis_limits_calculation(self):
        """Test axis limits calculation for different node positions."""
        with patch('matplotlib.pyplot.savefig'), \
             patch('matplotlib.pyplot.tight_layout'), \
             patch('matplotlib.pyplot.Circle'), \
             patch('matplotlib.pyplot.annotate'), \
             patch('matplotlib.pyplot.legend'), \
             patch('matplotlib.pyplot.imshow'), \
             patch('matplotlib.pyplot.grid'), \
             patch('matplotlib.pyplot.title'), \
             patch('matplotlib.pyplot.xticks'), \
             patch('matplotlib.pyplot.yticks'), \
             patch('matplotlib.pyplot.xlim') as mock_xlim, \
             patch('matplotlib.pyplot.ylim') as mock_ylim, \
             patch('matplotlib.pyplot.subplots'), \
             patch('networkx.draw_networkx_nodes'), \
             patch('networkx.draw_networkx_edges'):

            mock_network = MagicMock()
            mock_network.graph = MagicMock()
            mock_network.graph.nodes.return_value = ['node1', 'node2']
            mock_network.graph.edges.return_value = []
            mock_network.node_positions = {'node1': (-50, -30), 'node2': (50, 30)}
            mock_network.acoustic_params = {}

            mock_network.graph.neighbors.return_value = []

            result = visualize_network(mock_network)

            # Check that axis limits were set with margin
            mock_xlim.assert_called_once()
            mock_ylim.assert_called_once()

            # Verify the call includes margin (20) around node positions
            xlim_call = mock_xlim.call_args[0]
            ylim_call = mock_ylim.call_args[0]

            assert xlim_call[0] == -70  # -50 - 20
            assert xlim_call[1] == 70   # 50 + 20
            assert ylim_call[0] == -50  # -30 - 20
            assert ylim_call[1] == 50   # 30 + 20
