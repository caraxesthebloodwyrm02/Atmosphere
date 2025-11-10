"""
Flask Adapter for Cable-style Network Analyzer

Provides backward compatibility for existing Flask routes while using the new
Cable-inspired NetworkAnalyzer backend.
"""
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional

try:
    from flask import Flask, render_template, request, jsonify, send_file
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from .analyzer import NetworkAnalyzer
from .models import (
    LoadNetworkRequest, AnalyzeNetworkRequest, VisualizeNetworkRequest,
    SampleNetworkRequest
)


class FlaskWebApp:
    """
    Flask web application using the Cable-style NetworkAnalyzer backend.
    
    Provides backward compatibility while leveraging the new architecture.
    """

    def __init__(self,
                 host: str = 'localhost',
                 port: int = 5000,
                 debug: bool = False):
        """
        Initialize the Flask web application.

        Args:
            host: Server host address
            port: Server port
            debug: Enable debug mode
        """
        if not FLASK_AVAILABLE:
            raise ImportError("Flask is required for web interface. Install with: pip install flask flask-cors")

        self.host = host
        self.port = port
        self.debug = debug
        self.analyzer = NetworkAnalyzer()
        self.app = None

    def create_app(self) -> Flask:
        """
        Create and configure the Flask application.

        Returns:
            Flask application instance
        """
        app = Flask(__name__,
                   template_folder=self._get_template_dir(),
                   static_folder=self._get_static_dir())

        CORS(app)  # Enable CORS for API endpoints

        # Register routes using the new analyzer
        self._register_routes(app)

        self.app = app
        return app

    def run(self, **kwargs) -> None:
        """
        Run the web application.

        Args:
            **kwargs: Additional arguments for app.run()
        """
        if self.app is None:
            self.app = self.create_app()

        # Default kwargs
        run_kwargs = {
            'host': self.host,
            'port': self.port,
            'debug': self.debug
        }
        run_kwargs.update(kwargs)

        print("🚀 Starting Network Visualizer Web App (Cable-style backend)")
        print(f"📱 URL: http://{self.host}:{self.port}")
        print("📊 Open your browser to start exploring networks!")

        self.app.run(**run_kwargs)

    def _register_routes(self, app: Flask) -> None:
        """Register Flask routes using the new NetworkAnalyzer."""

        @app.route('/')
        def index():
            """Main application page."""
            return render_template('index.html')

        @app.route('/api/network/load', methods=['POST'])
        def load_network():
            """Load network from uploaded file."""
            try:
                if 'file' not in request.files:
                    return jsonify({'error': 'No file provided'}), 400

                file = request.files['file']
                if file.filename == '':
                    return jsonify({'error': 'No file selected'}), 400

                # Read file content
                file_content = file.read()
                file_type = Path(file.filename).suffix.lstrip('.')
                
                # Create request for analyzer
                load_request = LoadNetworkRequest(file_type=file_type)
                
                # Load network using new analyzer
                network_info = self.analyzer.load_network(load_request, file_content)

                return jsonify({
                    'success': True,
                    'network_info': network_info.dict()
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/analyze', methods=['POST'])
        def analyze_network():
            """Analyze current network."""
            try:
                if not self.analyzer.has_network():
                    return jsonify({'error': 'No network loaded'}), 400

                data = request.get_json() or {}
                metrics = data.get('metrics', ['degree', 'betweenness', 'closeness'])
                
                # Convert string metrics to enum values
                metric_enums = []
                for metric in metrics:
                    try:
                        from .models import CentralityMetric
                        metric_enums.append(CentralityMetric(metric))
                    except ValueError:
                        # Skip invalid metrics
                        continue

                # Create analysis request
                analyze_request = AnalyzeNetworkRequest(
                    metrics=metric_enums,
                    include_statistics=True
                )

                # Analyze using new analyzer
                analysis = self.analyzer.analyze_network(analyze_request)

                # Convert to legacy format
                result = {'success': True}
                
                if 'statistics' in analysis:
                    result['analysis'] = analysis['statistics'].dict()
                
                if 'centrality' in analysis:
                    centrality_dict = {}
                    for centrality in analysis['centrality']:
                        centrality_dict[centrality.metric] = centrality.scores
                    result['analysis']['centrality'] = centrality_dict

                return jsonify(result)

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/visualize', methods=['POST'])
        def visualize_network():
            """Generate network visualization."""
            try:
                if not self.analyzer.has_network():
                    return jsonify({'error': 'No network loaded'}), 400

                data = request.get_json() or {}
                layout = data.get('layout', 'spring')
                backend = data.get('backend', 'plotly')
                show_labels = data.get('show_labels', False)

                # Create visualization request
                from .models import NetworkLayout, VisualizationBackend
                viz_request = VisualizeNetworkRequest(
                    layout=NetworkLayout(layout),
                    backend=VisualizationBackend(backend),
                    show_labels=show_labels
                )

                # Generate visualization using new analyzer
                if backend == 'plotly':
                    visualization = self.analyzer.generate_visualization(viz_request)

                    # Convert to legacy format
                    legacy_viz = {
                        'nodes': [
                            {
                                'id': node.id,
                                'x': node.x,
                                'y': node.y,
                                'degree': node.degree
                            } for node in visualization.nodes
                        ],
                        'edges': [
                            {
                                'source': edge.source,
                                'target': edge.target,
                                'x0': edge.x0, 'y0': edge.y0,
                                'x1': edge.x1, 'y1': edge.y1
                            } for edge in visualization.edges
                        ],
                        'layout': layout
                    }

                    return jsonify({
                        'success': True,
                        'visualization': legacy_viz
                    })
                else:
                    # Generate static image
                    image_data = self.analyzer.generate_static_image(viz_request)

                    return jsonify({
                        'success': True,
                        'image': image_data
                    })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/sample/<name>', methods=['GET'])
        def load_sample(name: str):
            """Load a sample network."""
            try:
                # Create sample request
                sample_request = SampleNetworkRequest(name=name)

                # Load sample using new analyzer
                network_info = self.analyzer.load_sample_network(sample_request)

                return jsonify({
                    'success': True,
                    'network_info': network_info.dict()
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/stats', methods=['GET'])
        def get_stats():
            """Get current network statistics."""
            try:
                if not self.analyzer.has_network():
                    return jsonify({'error': 'No network loaded'}), 400

                stats = self.analyzer.get_network_statistics()

                return jsonify({
                    'success': True,
                    'statistics': stats.dict()
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/samples', methods=['GET'])
        def get_samples():
            """Get list of available sample networks."""
            try:
                samples = self.analyzer.get_available_samples()

                return jsonify({
                    'samples': samples
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        # New Cable-style endpoints
        @app.route('/api/v1/network/status')
        def get_network_status():
            """Get current network status (new endpoint)."""
            try:
                has_network = self.analyzer.has_network()
                
                status = {
                    "has_network": has_network,
                    "network_loaded": bool(self.analyzer.current_network)
                }
                
                if has_network and self.analyzer.current_network:
                    status.update({
                        "nodes": len(self.analyzer.current_network.nodes),
                        "edges": len(self.analyzer.current_network.edges),
                        "has_layout": self.analyzer.current_layout is not None,
                        "has_analysis": self.analyzer.current_analysis is not None
                    })
                
                return jsonify({
                    "success": True,
                    "status": status
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/v1/network/clear', methods=['DELETE'])
        def clear_network():
            """Clear current network (new endpoint)."""
            try:
                self.analyzer.clear_network()
                
                return jsonify({
                    "success": True,
                    "message": "Network cleared successfully"
                })
                
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    def _get_template_dir(self) -> str:
        """Get template directory path."""
        current_dir = Path(__file__).parent.parent
        template_dir = current_dir / "templates"
        return str(template_dir)

    def _get_static_dir(self) -> str:
        """Get static directory path."""
        current_dir = Path(__file__).parent.parent
        static_dir = current_dir / "static"
        return str(static_dir)


# Backward compatibility alias
WebApp = FlaskWebApp
