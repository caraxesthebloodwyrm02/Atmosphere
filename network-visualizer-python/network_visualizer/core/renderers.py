"""
Network Rendering Backends

Multiple rendering backends for network visualization including matplotlib,
plotly, and graphviz support.
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import warnings


class RendererManager:
    """
    Multi-backend rendering system for network visualizations.

    Supports static and interactive visualizations with multiple rendering engines
    including matplotlib, plotly, and graphviz.
    """

    def __init__(self):
        """Initialize the renderer manager."""
        self.backends = {
            'matplotlib': MatplotlibRenderer(),
            'plotly': PlotlyRenderer(),
            'graphviz': GraphvizRenderer(),
        }

    def render_static(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                     output_file: str = None, backend: str = 'matplotlib',
                     show_labels: bool = False, node_colors: Dict = None,
                     node_sizes: Dict = None, config: Dict = None, **kwargs) -> None:
        """
        Render static network visualization.

        Args:
            G: NetworkX graph
            pos: Node positions
            output_file: Output file path
            backend: Rendering backend
            show_labels: Whether to show node labels
            node_colors: Node color mapping
            node_sizes: Node size mapping
            config: Rendering configuration
            **kwargs: Backend-specific parameters
        """
        if backend not in self.backends:
            available = list(self.backends.keys())
            raise ValueError(f"Unknown backend '{backend}'. Available: {available}")

        renderer = self.backends[backend]
        renderer.render_static(G, pos, output_file, show_labels,
                             node_colors, node_sizes, config, **kwargs)

    def render_interactive(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                          node_attributes: Dict = None, backend: str = 'plotly',
                          **kwargs) -> None:
        """
        Render interactive network visualization.

        Args:
            G: NetworkX graph
            pos: Node positions
            node_attributes: Additional node attributes
            backend: Rendering backend
            **kwargs: Backend-specific parameters
        """
        if backend not in self.backends:
            available = list(self.backends.keys())
            raise ValueError(f"Unknown backend '{backend}'. Available: {available}")

        renderer = self.backends[backend]
        renderer.render_interactive(G, pos, node_attributes, **kwargs)


class MatplotlibRenderer:
    """Matplotlib-based static network renderer."""

    def render_static(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                     output_file: str = None, show_labels: bool = False,
                     node_colors: Dict = None, node_sizes: Dict = None,
                     config: Dict = None, **kwargs) -> None:
        """
        Render network using matplotlib.

        Args:
            G: NetworkX graph
            pos: Node positions
            output_file: Output file path
            show_labels: Whether to show node labels
            node_colors: Node color mapping
            node_sizes: Node size mapping
            config: Rendering configuration
            **kwargs: Matplotlib-specific parameters
        """
        # Set up configuration
        config = config or {}
        figsize = kwargs.get('figsize', (12, 8))
        dpi = config.get('dpi', 300)

        # Create figure
        fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
        ax.set_aspect('equal')

        # Draw edges
        nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.3, **kwargs)

        # Prepare node visualization data
        node_list = list(G.nodes)
        node_color_values = self._prepare_node_colors(G, node_colors, config)
        node_size_values = self._prepare_node_sizes(G, node_sizes, config)

        # Draw nodes
        nx.draw_networkx_nodes(G, pos, nodelist=node_list,
                              node_color=node_color_values,
                              node_size=node_size_values,
                              ax=ax, **kwargs)

        # Draw labels if requested
        if show_labels:
            font_size = config.get('font_size', 8)
            nx.draw_networkx_labels(G, pos, ax=ax, font_size=font_size, **kwargs)

        # Configure plot
        ax.axis('off')
        plt.tight_layout()

        # Save or show
        if output_file:
            plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
            plt.close()
        else:
            plt.show()

    def render_interactive(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                          node_attributes: Dict = None, **kwargs) -> None:
        """
        Matplotlib doesn't support interactive rendering natively.
        Fall back to static rendering.
        """
        warnings.warn("Matplotlib backend doesn't support interactive rendering. "
                     "Use plotly backend for interactive visualizations.")
        self.render_static(G, pos, show_labels=True, **kwargs)

    def _prepare_node_colors(self, G: nx.Graph, node_colors: Dict = None,
                           config: Dict = None) -> List:
        """Prepare node colors for visualization."""
        if node_colors:
            return [node_colors.get(node, 'skyblue') for node in G.nodes]
        else:
            # Use degree-based coloring
            degrees = dict(G.degree())
            min_degree = min(degrees.values())
            max_degree = max(degrees.values())

            if max_degree > min_degree:
                # Normalize to 0-1 range
                normalized_degrees = [(d - min_degree) / (max_degree - min_degree)
                                    for d in degrees.values()]
                colormap = config.get('color_map', 'viridis')
                cmap = plt.cm.get_cmap(colormap)
                return [cmap(norm) for norm in normalized_degrees]
            else:
                return ['skyblue'] * len(G.nodes)

    def _prepare_node_sizes(self, G: nx.Graph, node_sizes: Dict = None,
                           config: Dict = None) -> List:
        """Prepare node sizes for visualization."""
        if node_sizes:
            return [node_sizes.get(node, 100) for node in G.nodes]
        else:
            # Use degree-based sizing
            config = config or {}
            min_size, max_size = config.get('node_size_range', (100, 1000))

            degrees = dict(G.degree())
            min_degree = min(degrees.values())
            max_degree = max(degrees.values())

            if max_degree > min_degree:
                sizes = []
                for degree in degrees.values():
                    # Normalize and scale
                    normalized = (degree - min_degree) / (max_degree - min_degree)
                    size = min_size + normalized * (max_size - min_size)
                    sizes.append(size)
                return sizes
            else:
                return [300] * len(G.nodes)


class PlotlyRenderer:
    """Plotly-based interactive network renderer."""

    def render_static(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                     output_file: str = None, show_labels: bool = False,
                     node_colors: Dict = None, node_sizes: Dict = None,
                     config: Dict = None, **kwargs) -> None:
        """
        Render static network using plotly.

        Args:
            G: NetworkX graph
            pos: Node positions
            output_file: Output file path
            show_labels: Whether to show node labels
            node_colors: Node color mapping
            node_sizes: Node size mapping
            config: Rendering configuration
            **kwargs: Plotly-specific parameters
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise ImportError("plotly is required for plotly backend")

        # Prepare data
        edge_x, edge_y = self._prepare_edges(G, pos)
        node_x, node_y, node_colors_list, node_sizes_list, node_text = self._prepare_nodes(
            G, pos, node_colors, node_sizes, show_labels, config
        )

        # Create figure
        fig = go.Figure()

        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))

        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text' if show_labels else 'markers',
            hoverinfo='text',
            text=node_text if show_labels else None,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=node_colors_list,
                size=node_sizes_list,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2
            )
        ))

        # Configure layout
        fig.update_layout(
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )

        # Save or show
        if output_file:
            fig.write_image(output_file)
        else:
            fig.show()

    def render_interactive(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                          node_attributes: Dict = None, **kwargs) -> None:
        """
        Render interactive network using plotly.

        Args:
            G: NetworkX graph
            pos: Node positions
            node_attributes: Additional node attributes for tooltips
            **kwargs: Plotly-specific parameters
        """
        try:
            import plotly.graph_objects as go
        except ImportError:
            raise ImportError("plotly is required for plotly backend")

        # Prepare data
        edge_x, edge_y = self._prepare_edges(G, pos)
        node_x, node_y, node_colors_list, node_sizes_list, node_text = self._prepare_nodes(
            G, pos, None, None, True, None, node_attributes
        )

        # Create figure
        fig = go.Figure()

        # Add edges
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines'
        ))

        # Add nodes
        fig.add_trace(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                reversescale=True,
                color=node_colors_list,
                size=node_sizes_list,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                ),
                line_width=2
            )
        ))

        # Configure layout
        fig.update_layout(
            title="Interactive Network Visualization",
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=5, r=5, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white'
        )

        # Add interactive controls
        fig.update_traces(
            hovertemplate="<b>%{text}</b><br>" +
                         "Position: (%{x:.2f}, %{y:.2f})<br>" +
                         "<extra></extra>"
        )

        fig.show()

    def _prepare_edges(self, G: nx.Graph, pos: Dict) -> Tuple[List, List]:
        """Prepare edge coordinates for plotting."""
        edge_x = []
        edge_y = []

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        return edge_x, edge_y

    def _prepare_nodes(self, G: nx.Graph, pos: Dict, node_colors: Dict = None,
                      node_sizes: Dict = None, show_labels: bool = False,
                      config: Dict = None, node_attributes: Dict = None) -> Tuple:
        """Prepare node data for plotting."""
        node_x = []
        node_y = []
        node_text = []
        node_colors_list = []
        node_sizes_list = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Node text
            if show_labels:
                text = str(node)
                if node_attributes and node in node_attributes:
                    attrs = node_attributes[node]
                    if isinstance(attrs, dict):
                        attr_str = "<br>".join([f"{k}: {v}" for k, v in attrs.items()])
                        text += f"<br>{attr_str}"
                node_text.append(text)
            else:
                node_text.append("")

            # Node colors
            if node_colors and node in node_colors:
                node_colors_list.append(node_colors[node])
            else:
                # Use degree-based coloring
                degree = G.degree[node]
                node_colors_list.append(degree)

            # Node sizes
            if node_sizes and node in node_sizes:
                node_sizes_list.append(node_sizes[node])
            else:
                # Use degree-based sizing
                degree = G.degree[node]
                size = max(10, min(50, degree * 3))
                node_sizes_list.append(size)

        return node_x, node_y, node_colors_list, node_sizes_list, node_text


class GraphvizRenderer:
    """Graphviz-based hierarchical network renderer."""

    def render_static(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                     output_file: str = None, show_labels: bool = False,
                     node_colors: Dict = None, node_sizes: Dict = None,
                     config: Dict = None, **kwargs) -> None:
        """
        Render network using graphviz.

        Args:
            G: NetworkX graph
            pos: Node positions (ignored for graphviz)
            output_file: Output file path
            show_labels: Whether to show node labels
            node_colors: Node color mapping (ignored for graphviz)
            node_sizes: Node size mapping (ignored for graphviz)
            config: Rendering configuration
            **kwargs: Graphviz-specific parameters
        """
        try:
            from networkx.drawing.nx_agraph import to_agraph
        except ImportError:
            raise ImportError("pygraphviz is required for graphviz backend")

        # Convert to agraph
        A = to_agraph(G)

        # Configure graph
        A.graph_attr.update({
            'rankdir': kwargs.get('rankdir', 'TB'),
            'size': kwargs.get('size', '12,8'),
            'ratio': kwargs.get('ratio', 'compress'),
        })

        # Configure nodes
        for node in A.nodes():
            node.attr.update({
                'shape': 'circle',
                'style': 'filled',
                'fillcolor': 'lightblue',
            })

        # Configure edges
        for edge in A.edges():
            edge.attr.update({
                'color': 'gray',
                'penwidth': '0.5',
            })

        # Save or show
        if output_file:
            # Determine format from extension
            ext = Path(output_file).suffix.lower()
            if ext in ['.png', '.jpg', '.svg', '.pdf']:
                format_map = {'.png': 'png', '.jpg': 'jpg', '.svg': 'svg', '.pdf': 'pdf'}
                format_type = format_map.get(ext, 'png')
                A.draw(output_file, format=format_type, prog='dot')
            else:
                # Save as dot file
                A.write(output_file)
        else:
            # Display using matplotlib
            plt.figure(figsize=(12, 8))
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
            nx.draw(G, pos, with_labels=True, node_color='lightblue',
                   node_size=500, font_size=8, font_weight='bold')
            plt.show()

    def render_interactive(self, G: nx.Graph, pos: Dict[Any, Tuple[float, float]],
                          node_attributes: Dict = None, **kwargs) -> None:
        """
        Graphviz doesn't support interactive rendering natively.
        Fall back to static rendering.
        """
        warnings.warn("Graphviz backend doesn't support interactive rendering. "
                     "Use plotly backend for interactive visualizations.")
        self.render_static(G, pos, show_labels=True, **kwargs)
