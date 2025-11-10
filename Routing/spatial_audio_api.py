#!/usr/bin/env python
"""
spatial_audio_api.py

Flask API service for the spatial audio visualizer.
Provides HTTP endpoints for generating 3D spatial audio visualizations.

Endpoints:
- POST /render: Generate PNG visualization from source/listener positions
- GET /health: Health check endpoint

Usage:
    python spatial_audio_api.py
    curl -X POST http://localhost:5000/render \
         -H "Content-Type: application/json" \
         -d '{"source_pos": [5.0, 0.0, 2.0], "listener_pos": [0.0, 0.0, 0.0]}' \
         --output visualization.png
"""

import numpy as np
from flask import Flask, request, jsonify, send_file
from io import BytesIO
import matplotlib
matplotlib.use('Agg')  # Server-compatible backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

app = Flask(__name__)

def find_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return Euclidean distance |a-b|."""
    return float(np.linalg.norm(a - b))

def generate_spatial_plot(source_pos, listener_pos):
    """
    Generate 3D spatial audio visualization.

    Args:
        source_pos: tuple of (x, y, z) coordinates
        listener_pos: tuple of (x, y, z) coordinates

    Returns:
        BytesIO buffer containing PNG image
    """
    # Convert to numpy arrays
    src = np.array(source_pos, dtype=float)
    lst = np.array(listener_pos, dtype=float)

    # Calculate distance
    dist = find_distance(src, lst)

    # Create plot
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Plot elements
    ax.scatter(*lst, color="blue", s=120, label="Listener")
    ax.scatter(*src, color="red", s=120, label="Sound Source")

    # Distance bar
    ax.plot(
        [lst[0], src[0]],
        [lst[1], src[1]],
        [lst[2], src[2]],
        color="green",
        linewidth=3,
        label=f"Distance = {dist:.2f} m",
    )

    # Labels and styling
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title("3-D Spatial Audio Setup")
    ax.legend()

    # Optimal viewing angle
    ax.view_init(elev=20, azim=120)

    # Save to buffer
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    plt.close(fig)  # Clean up memory

    return buf

@app.route('/render', methods=['POST'])
def render():
    """
    Generate and return spatial audio visualization.

    Expected JSON payload:
    {
        "source_pos": [x, y, z],
        "listener_pos": [x, y, z]
    }
    """
    try:
        data = request.get_json()

        if not data or 'source_pos' not in data or 'listener_pos' not in data:
            return jsonify({
                'error': 'Missing required fields: source_pos and listener_pos'
            }), 400

        source_pos = tuple(data['source_pos'])
        listener_pos = tuple(data['listener_pos'])

        # Validate coordinates (should be 3D)
        if len(source_pos) != 3 or len(listener_pos) != 3:
            return jsonify({
                'error': 'Positions must be 3D coordinates [x, y, z]'
            }), 400

        # Generate visualization
        img_buffer = generate_spatial_plot(source_pos, listener_pos)

        return send_file(
            img_buffer,
            mimetype='image/png',
            as_attachment=True,
            download_name='spatial_audio_visualization.png'
        )

    except Exception as e:
        return jsonify({
            'error': f'Visualization generation failed: {str(e)}'
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'spatial_audio_visualizer_api',
        'version': '1.0.0'
    })

@app.route('/', methods=['GET'])
def index():
    """API documentation endpoint."""
    return jsonify({
        'service': 'Spatial Audio Visualizer API',
        'version': '1.0.0',
        'endpoints': {
            'POST /render': 'Generate 3D spatial audio visualization',
            'GET /health': 'Health check',
            'GET /': 'This documentation'
        },
        'example_request': {
            'method': 'POST',
            'url': '/render',
            'headers': {'Content-Type': 'application/json'},
            'body': {
                'source_pos': [5.0, 0.0, 2.0],
                'listener_pos': [0.0, 0.0, 0.0]
            }
        }
    })

if __name__ == "__main__":
    print("🚀 Spatial Audio Visualizer API")
    print("📡 Starting Flask server on http://localhost:5000")
    print("📖 API docs available at http://localhost:5000")
    print("💡 Example: curl -X POST http://localhost:5000/render -H 'Content-Type: application/json' -d '{\"source_pos\": [5,0,2], \"listener_pos\": [0,0,0]}' --output viz.png")

    app.run(host="0.0.0.0", port=5000, debug=True)
