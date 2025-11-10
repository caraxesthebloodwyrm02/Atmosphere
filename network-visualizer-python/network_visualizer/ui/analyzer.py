"""
Network Analyzer - Cable-style Assistant for Network Analysis

A type-safe network analysis interface using Pydantic models for request/response handling.
Provides a clean, maintainable API for network visualization and analysis.
"""
import os
import tempfile
import base64
from pathlib import Path
from typing import List, Dict, Optional, Any, Union, Generator
import networkx as nx

from .models import (
    NetworkNode, NetworkEdge, NetworkStatistics, CentralityScores,
    NetworkInfo, NetworkVisualization, NetworkLayout, VisualizationBackend,
    CentralityMetric, LoadNetworkRequest, AnalyzeNetworkRequest, 
    VisualizeNetworkRequest, SampleNetworkRequest
)
from ..core import NetworkVisualizer


class NetworkAnalyzer:
    """
    Handles network analysis and visualization operations using Pydantic models.
    
    Follows the Cable assistant pattern for clean, type-safe operations.
    """

    def __init__(self, visualizer: Optional[NetworkVisualizer] = None):
        """Initialize the network analyzer.
        
        Args:
            visualizer: Optional NetworkVisualizer instance
        """
        self.visualizer = visualizer or NetworkVisualizer()
        self.current_network: Optional[nx.Graph] = None
        self.current_layout: Optional[Dict[str, tuple]] = None
        self.current_analysis: Optional[Dict[str, Any]] = None

    def load_network(
        self, 
        request: LoadNetworkRequest,
        file_content: Optional[bytes] = None
    ) -> NetworkInfo:
        """Load network from file or content.
        
        Args:
            request: Load network request
            file_content: Optional file content as bytes
            
        Returns:
            NetworkInfo with basic network information
            
        Raises:
            ValueError: If file cannot be loaded
            RuntimeError: If network loading fails
        """
        try:
            if file_content and request.file_type:
                # Load from file content
                with tempfile.NamedTemporaryFile(
                    suffix=f".{request.file_type}", 
                    delete=False
                ) as tmp:
                    tmp.write(file_content)
                    tmp_path = tmp.name
                
                try:
                    G = self.visualizer.load_network(tmp_path)
                    self.current_network = G
                finally:
                    os.unlink(tmp_path)
                    
            elif request.file_path:
                # Load from file path
                G = self.visualizer.load_network(request.file_path)
                self.current_network = G
            else:
                raise ValueError("Either file_path or file_content must be provided")
            
            # Compute basic statistics
            stats = self.visualizer.compute_statistics(G)
            
            return NetworkInfo(
                nodes=len(G.nodes),
                edges=len(G.edges),
                density=stats['density'],
                filename=Path(request.file_path or "uploaded_file").name
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to load network: {str(e)}") from e

    def load_sample_network(self, request: SampleNetworkRequest) -> NetworkInfo:
        """Load a sample network.
        
        Args:
            request: Sample network request
            
        Returns:
            NetworkInfo with sample network information
            
        Raises:
            ValueError: If sample name is invalid
            RuntimeError: If sample loading fails
        """
        try:
            G = self.visualizer.load_sample_graph(request.name)
            self.current_network = G
            
            stats = self.visualizer.compute_statistics(G)
            
            return NetworkInfo(
                nodes=len(G.nodes),
                edges=len(G.edges),
                density=stats['density'],
                name=request.name
            )
            
        except Exception as e:
            raise RuntimeError(f"Failed to load sample network '{request.name}': {str(e)}") from e

    def analyze_network(self, request: AnalyzeNetworkRequest) -> Dict[str, Any]:
        """Analyze current network.
        
        Args:
            request: Analysis request
            
        Returns:
            Analysis results including statistics and centrality metrics
            
        Raises:
            ValueError: If no network is loaded
            RuntimeError: If analysis fails
        """
        if self.current_network is None:
            raise ValueError("No network loaded for analysis")
        
        try:
            analysis = {}
            
            # Compute statistics if requested
            if request.include_statistics:
                stats = self.visualizer.compute_statistics(self.current_network)
                analysis['statistics'] = NetworkStatistics(
                    nodes=stats['nodes'],
                    edges=stats['edges'],
                    density=stats['density'],
                    average_degree=stats.get('average_degree'),
                    is_connected=stats.get('is_connected'),
                    num_components=stats.get('num_components')
                )
            
            # Compute centrality metrics
            if request.metrics:
                centrality_results = []
                metric_names = [m.value for m in request.metrics]
                centrality_data = self.visualizer.analyze_network(
                    self.current_network, 
                    metric_names
                )
                
                for metric_name, scores in centrality_data.items():
                    centrality_results.append(
                        CentralityScores(metric=metric_name, scores=scores)
                    )
                
                analysis['centrality'] = centrality_results
                self.current_analysis = centrality_data
            
            return analysis
            
        except Exception as e:
            raise RuntimeError(f"Network analysis failed: {str(e)}") from e

    def generate_visualization(self, request: VisualizeNetworkRequest) -> NetworkVisualization:
        """Generate network visualization.
        
        Args:
            request: Visualization request
            
        Returns:
            NetworkVisualization with node and edge data
            
        Raises:
            ValueError: If no network is loaded
            RuntimeError: If visualization generation fails
        """
        if self.current_network is None:
            raise ValueError("No network loaded for visualization")
        
        try:
            # Compute layout
            pos = self.visualizer.compute_layout(
                self.current_network, 
                request.layout.value
            )
            self.current_layout = pos
            
            # Prepare nodes
            nodes = []
            for node in self.current_network.nodes():
                x, y = pos[node]
                node_data = {
                    'id': str(node),
                    'x': x,
                    'y': y,
                    'degree': self.current_network.degree(node)
                }
                
                # Add metrics if available
                if self.current_analysis and str(node) in self.current_analysis.get('degree', {}):
                    node_data['metrics'] = {
                        metric: scores.get(str(node), 0.0)
                        for metric, scores in self.current_analysis.items()
                    }
                
                nodes.append(NetworkNode(**node_data))
            
            # Prepare edges
            edges = []
            for source, target, data in self.current_network.edges(data=True):
                x0, y0 = pos[source]
                x1, y1 = pos[target]
                
                edge_data = {
                    'source': str(source),
                    'target': str(target),
                    'x0': x0, 'y0': y0,
                    'x1': x1, 'y1': y1
                }
                
                # Add weight if available
                if 'weight' in data:
                    edge_data['weight'] = data['weight']
                
                edges.append(NetworkEdge(**edge_data))
            
            return NetworkVisualization(
                nodes=nodes,
                edges=edges,
                layout=request.layout,
                backend=request.backend
            )
            
        except Exception as e:
            raise RuntimeError(f"Visualization generation failed: {str(e)}") from e

    def generate_static_image(
        self, 
        request: VisualizeNetworkRequest,
        format: str = "png"
    ) -> str:
        """Generate static network image.
        
        Args:
            request: Visualization request
            format: Image format (png, svg, pdf)
            
        Returns:
            Base64 encoded image string
            
        Raises:
            ValueError: If no network is loaded
            RuntimeError: If image generation fails
        """
        if self.current_network is None:
            raise ValueError("No network loaded for visualization")
        
        try:
            with tempfile.NamedTemporaryFile(
                suffix=f".{format}", 
                delete=False
            ) as tmp:
                output_path = tmp.name
            
            # Generate static visualization
            self.visualizer.visualize_static(
                self.current_network,
                output_file=output_path,
                backend=request.backend.value,
                layout=request.layout.value,
                show_labels=request.show_labels
            )
            
            # Convert to base64
            with open(output_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Clean up
            os.unlink(output_path)
            
            return f"data:image/{format};base64,{image_data}"
            
        except Exception as e:
            raise RuntimeError(f"Static image generation failed: {str(e)}") from e

    def get_available_samples(self) -> List[str]:
        """Get list of available sample networks.
        
        Returns:
            List of sample network names
        """
        return [
            'karate_club',
            'davis_southern_women',
            'florentine_families',
            'les_miserables',
            'football'
        ]

    def get_network_statistics(self) -> NetworkStatistics:
        """Get current network statistics.
        
        Returns:
            NetworkStatistics for current network
            
        Raises:
            ValueError: If no network is loaded
        """
        if self.current_network is None:
            raise ValueError("No network loaded")
        
        stats = self.visualizer.compute_statistics(self.current_network)
        return NetworkStatistics(
            nodes=stats['nodes'],
            edges=stats['edges'],
            density=stats['density'],
            average_degree=stats.get('average_degree'),
            is_connected=stats.get('is_connected'),
            num_components=stats.get('num_components')
        )

    def clear_network(self) -> None:
        """Clear current network and related data."""
        self.current_network = None
        self.current_layout = None
        self.current_analysis = None

    def has_network(self) -> bool:
        """Check if a network is currently loaded.
        
        Returns:
            True if network is loaded, False otherwise
        """
        return self.current_network is not None
