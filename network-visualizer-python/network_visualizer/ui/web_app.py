"""
Web Application Interface for Network Visualizer

Provides a web-based interface for interactive network visualization,
analysis, and exploration using Flask and modern web technologies.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import tempfile
import base64
import io

try:
    from flask import Flask, render_template, request, jsonify, send_file
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from ..core import NetworkVisualizer


class WebApp:
    """
    Web application for interactive network visualization.

    Provides a modern web interface for network analysis, visualization,
    and exploration with real-time updates and interactive features.
    """

    def __init__(self,
                 host: str = 'localhost',
                 port: int = 5000,
                 debug: bool = False):
        """
        Initialize the web application.

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
        self.visualizer = NetworkVisualizer()
        self.app = None
        self.current_network = None

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

        # Register routes
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

        print("🚀 Starting Network Visualizer Web App")
        print(f"📱 URL: http://{self.host}:{self.port}")
        print("📊 Open your browser to start exploring networks!")

        self.app.run(**run_kwargs)

    def _register_routes(self, app: Flask) -> None:
        """Register Flask routes."""

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

                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
                    file.save(tmp.name)
                    tmp_path = tmp.name

                try:
                    # Load network
                    G = self.visualizer.load_network(tmp_path)
                    self.current_network = G

                    # Get basic info
                    info = {
                        'nodes': len(G.nodes),
                        'edges': len(G.edges),
                        'density': self.visualizer.compute_statistics(G)['density'],
                        'filename': file.filename
                    }

                    return jsonify({
                        'success': True,
                        'network_info': info
                    })

                finally:
                    # Clean up temporary file
                    os.unlink(tmp_path)

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/analyze', methods=['POST'])
        def analyze_network():
            """Analyze current network."""
            try:
                if self.current_network is None:
                    return jsonify({'error': 'No network loaded'}), 400

                data = request.get_json() or {}
                metrics = data.get('metrics', ['degree', 'betweenness', 'closeness'])

                # Perform analysis
                analysis = self.visualizer.analyze_network(self.current_network, metrics)

                return jsonify({
                    'success': True,
                    'analysis': analysis
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/visualize', methods=['POST'])
        def visualize_network():
            """Generate network visualization."""
            try:
                if self.current_network is None:
                    return jsonify({'error': 'No network loaded'}), 400

                data = request.get_json() or {}
                layout = data.get('layout', 'spring')
                backend = data.get('backend', 'plotly')
                show_labels = data.get('show_labels', False)

                # Generate visualization
                if backend == 'plotly':
                    # Return interactive visualization data
                    pos = self.visualizer.compute_layout(self.current_network, layout)

                    # Prepare data for frontend
                    nodes = []
                    for node in self.current_network.nodes():
                        x, y = pos[node]
                        nodes.append({
                            'id': str(node),
                            'x': x,
                            'y': y,
                            'degree': self.current_network.degree(node)
                        })

                    edges = []
                    for source, target in self.current_network.edges():
                        x0, y0 = pos[source]
                        x1, y1 = pos[target]
                        edges.append({
                            'source': str(source),
                            'target': str(target),
                            'x0': x0, 'y0': y0,
                            'x1': x1, 'y1': y1
                        })

                    return jsonify({
                        'success': True,
                        'visualization': {
                            'nodes': nodes,
                            'edges': edges,
                            'layout': layout
                        }
                    })

                else:
                    # Generate static image
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                        output_path = tmp.name

                    self.visualizer.visualize_static(
                        self.current_network,
                        output_file=output_path,
                        backend=backend,
                        layout=layout,
                        show_labels=show_labels
                    )

                    # Convert to base64 for response
                    with open(output_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode()

                    # Clean up
                    os.unlink(output_path)

                    return jsonify({
                        'success': True,
                        'image': f"data:image/png;base64,{image_data}"
                    })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/sample/<name>', methods=['GET'])
        def load_sample(name: str):
            """Load a sample network."""
            try:
                G = self.visualizer.load_sample_graph(name)
                self.current_network = G

                info = {
                    'nodes': len(G.nodes),
                    'edges': len(G.edges),
                    'density': self.visualizer.compute_statistics(G)['density'],
                    'name': name
                }

                return jsonify({
                    'success': True,
                    'network_info': info
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/network/stats', methods=['GET'])
        def get_stats():
            """Get current network statistics."""
            try:
                if self.current_network is None:
                    return jsonify({'error': 'No network loaded'}), 400

                stats = self.visualizer.compute_statistics(self.current_network)

                return jsonify({
                    'success': True,
                    'statistics': stats
                })

            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/api/samples', methods=['GET'])
        def get_samples():
            """Get list of available sample networks."""
            samples = [
                'karate_club',
                'davis_southern_women',
                'florentine_families',
                'les_miserables',
                'football'
            ]

            return jsonify({
                'samples': samples
            })

    def _get_template_dir(self) -> str:
        """Get template directory path."""
        # For now, return current directory - templates would be added separately
        return str(Path(__file__).parent / 'templates')

    def _get_static_dir(self) -> str:
        """Get static files directory path."""
        # For now, return current directory - static files would be added separately
        return str(Path(__file__).parent / 'static')

    def create_basic_templates(self) -> None:
        """Create basic HTML templates for the web interface."""
        template_dir = Path(self._get_template_dir())
        template_dir.mkdir(exist_ok=True)

        # Create basic index.html
        index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Network Visualizer</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .controls {
            display: flex;
            gap: 20px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .control-group {
            display: flex;
            flex-direction: column;
            min-width: 200px;
        }
        label {
            margin-bottom: 5px;
            font-weight: bold;
        }
        select, button, input {
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        button {
            background: #007bff;
            color: white;
            cursor: pointer;
        }
        button:hover {
            background: #0056b3;
        }
        #network-plot {
            width: 100%;
            height: 600px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }
        .stats {
            margin-top: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Network Visualizer</h1>
            <p>Interactive network analysis and visualization</p>
        </div>

        <div class="controls">
            <div class="control-group">
                <label for="sample-select">Load Sample Network:</label>
                <select id="sample-select">
                    <option value="">Choose a sample...</option>
                </select>
            </div>

            <div class="control-group">
                <label for="file-input">Upload Network File:</label>
                <input type="file" id="file-input" accept=".json,.csv,.graphml,.gml">
            </div>

            <div class="control-group">
                <label for="layout-select">Layout:</label>
                <select id="layout-select">
                    <option value="spring">Spring</option>
                    <option value="circular">Circular</option>
                    <option value="random">Random</option>
                    <option value="shell">Shell</option>
                </select>
            </div>

            <div class="control-group">
                <button id="visualize-btn">Visualize Network</button>
                <button id="analyze-btn">Analyze Network</button>
            </div>
        </div>

        <div id="network-plot"></div>

        <div id="stats-container" class="stats" style="display: none;">
            <h3>Network Statistics</h3>
            <div id="stats-content"></div>
        </div>
    </div>

    <script>
        let currentNetwork = null;

        // Load available samples
        fetch('/api/samples')
            .then(response => response.json())
            .then(data => {
                const select = document.getElementById('sample-select');
                data.samples.forEach(sample => {
                    const option = document.createElement('option');
                    option.value = sample;
                    option.textContent = sample.replace('_', ' ').replace(/\\b\\w/g, l => l.toUpperCase());
                    select.appendChild(option);
                });
            });

        // Handle sample selection
        document.getElementById('sample-select').addEventListener('change', function(e) {
            if (e.target.value) {
                loadSampleNetwork(e.target.value);
            }
        });

        // Handle file upload
        document.getElementById('file-input').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                loadNetworkFile(file);
            }
        });

        // Handle visualize button
        document.getElementById('visualize-btn').addEventListener('click', function() {
            if (currentNetwork) {
                visualizeNetwork();
            } else {
                alert('Please load a network first');
            }
        });

        // Handle analyze button
        document.getElementById('analyze-btn').addEventListener('click', function() {
            if (currentNetwork) {
                analyzeNetwork();
            } else {
                alert('Please load a network first');
            }
        });

        async function loadSampleNetwork(name) {
            try {
                const response = await fetch(`/api/network/sample/${name}`);
                const data = await response.json();

                if (data.success) {
                    currentNetwork = data.network_info;
                    updateStats(data.network_info);
                    alert(`Loaded sample network: ${name}`);
                } else {
                    alert('Error loading sample: ' + data.error);
                }
            } catch (error) {
                alert('Error loading sample: ' + error.message);
            }
        }

        async function loadNetworkFile(file) {
            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/network/load', {
                    method: 'POST',
                    body: formData
                });
                const data = await response.json();

                if (data.success) {
                    currentNetwork = data.network_info;
                    updateStats(data.network_info);
                    alert(`Loaded network: ${file.name}`);
                } else {
                    alert('Error loading file: ' + data.error);
                }
            } catch (error) {
                alert('Error loading file: ' + error.message);
            }
        }

        async function visualizeNetwork() {
            const layout = document.getElementById('layout-select').value;

            try {
                const response = await fetch('/api/network/visualize', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        layout: layout,
                        backend: 'plotly'
                    })
                });
                const data = await response.json();

                if (data.success) {
                    renderPlotlyVisualization(data.visualization);
                } else {
                    alert('Error visualizing network: ' + data.error);
                }
            } catch (error) {
                alert('Error visualizing network: ' + error.message);
            }
        }

        async function analyzeNetwork() {
            try {
                const response = await fetch('/api/network/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        metrics: ['degree', 'betweenness', 'closeness']
                    })
                });
                const data = await response.json();

                if (data.success) {
                    showAnalysis(data.analysis);
                } else {
                    alert('Error analyzing network: ' + data.error);
                }
            } catch (error) {
                alert('Error analyzing network: ' + error.message);
            }
        }

        function renderPlotlyVisualization(vizData) {
            const plotDiv = document.getElementById('network-plot');

            const edgeTrace = {
                x: [],
                y: [],
                mode: 'lines',
                line: {width: 0.5, color: '#888'},
                hoverinfo: 'none'
            };

            vizData.edges.forEach(edge => {
                edgeTrace.x.push(edge.x0, edge.x1, null);
                edgeTrace.y.push(edge.y0, edge.y1, null);
            });

            const nodeTrace = {
                x: vizData.nodes.map(n => n.x),
                y: vizData.nodes.map(n => n.y),
                mode: 'markers+text',
                text: vizData.nodes.map(n => n.id),
                textposition: 'top center',
                marker: {
                    size: vizData.nodes.map(n => Math.max(10, Math.min(50, n.degree * 2))),
                    color: vizData.nodes.map(n => n.degree),
                    colorscale: 'YlGnBu',
                    showscale: true,
                    colorbar: {
                        title: 'Node Degree',
                        thickness: 15
                    }
                },
                hovertemplate: 'Node: %{text}<br>Degree: %{marker.color}<extra></extra>'
            };

            const layout = {
                showlegend: false,
                hovermode: 'closest',
                margin: {b: 20, l: 5, r: 5, t: 40},
                xaxis: {showgrid: false, zeroline: false, showticklabels: false},
                yaxis: {showgrid: false, zeroline: false, showticklabels: false},
                plot_bgcolor: 'white'
            };

            Plotly.newPlot(plotDiv, [edgeTrace, nodeTrace], layout);
        }

        function updateStats(info) {
            const statsDiv = document.getElementById('stats-container');
            const contentDiv = document.getElementById('stats-content');

            contentDiv.innerHTML = `
                <p><strong>Nodes:</strong> ${info.nodes}</p>
                <p><strong>Edges:</strong> ${info.edges}</p>
                <p><strong>Density:</strong> ${info.density.toFixed(4)}</p>
            `;

            statsDiv.style.display = 'block';
        }

        function showAnalysis(analysis) {
            const stats = analysis.statistics;
            alert(`Analysis Complete!\\nNodes: ${stats.num_nodes}\\nEdges: ${stats.num_edges}\\nDensity: ${stats.density.toFixed(4)}`);
        }
    </script>
</body>
</html>"""

        with open(template_dir / 'index.html', 'w') as f:
            f.write(index_html)
