#!/usr/bin/env python
"""
spatial_audio_api_demo.py

Demonstration of spatial audio API functionality.
This shows how the API would work, generating visualizations programmatically.

Usage:
    python spatial_audio_api_demo.py

This demonstrates the core API functionality without requiring Flask server setup.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')  # Server-compatible backend
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401
from io import BytesIO
import json
import base64
from typing import Tuple, Dict, Any

def find_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return Euclidean distance |a-b|."""
    return float(np.linalg.norm(a - b))

def generate_spatial_plot(source_pos: Tuple[float, float, float], listener_pos: Tuple[float, float, float]) -> BytesIO:
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

def simulate_api_request(json_payload: str) -> Dict[str, Any]:
    """
    Simulate processing an API request.

    Args:
        json_payload: JSON string with source_pos and listener_pos

    Returns:
        dict: API response with base64-encoded image
    """
    try:
        data = json.loads(json_payload)

        if 'source_pos' not in data or 'listener_pos' not in data:
            return {
                'error': 'Missing required fields: source_pos and listener_pos',
                'status': 400
            }

        source_pos = tuple(data['source_pos'])
        listener_pos = tuple(data['listener_pos'])

        if len(source_pos) != 3 or len(listener_pos) != 3:
            return {
                'error': 'Positions must be 3D coordinates [x, y, z]',
                'status': 400
            }

        # Generate visualization
        img_buffer = generate_spatial_plot(source_pos, listener_pos)

        # Convert to base64 for JSON response
        img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')

        return {
            'status': 200,
            'message': 'Visualization generated successfully',
            'image_data': img_base64,
            'image_format': 'png',
            'metadata': {
                'source_pos': source_pos,
                'listener_pos': listener_pos,
                'distance': find_distance(np.array(source_pos), np.array(listener_pos))
            }
        }

    except json.JSONDecodeError:
        return {
            'error': 'Invalid JSON payload',
            'status': 400
        }
    except Exception as e:
        return {
            'error': f'Visualization generation failed: {str(e)}',
            'status': 500
        }

def demo_api_calls():
    """Demonstrate various API call scenarios."""
    print("🚀 Spatial Audio API Demo")
    print("=" * 50)

    # Test cases
    test_cases = [
        {
            'name': 'Default positions',
            'payload': '{"source_pos": [5.0, 0.0, 2.0], "listener_pos": [0.0, 0.0, 0.0]}'
        },
        {
            'name': 'Close proximity',
            'payload': '{"source_pos": [1.0, 0.0, 0.0], "listener_pos": [0.0, 0.0, 0.0]}'
        },
        {
            'name': 'Elevated source',
            'payload': '{"source_pos": [3.0, 2.0, 5.0], "listener_pos": [0.0, 0.0, 1.0]}'
        },
        {
            'name': 'Invalid payload (missing field)',
            'payload': '{"source_pos": [1.0, 2.0, 3.0]}'
        },
        {
            'name': 'Invalid payload (wrong dimensions)',
            'payload': '{"source_pos": [1.0, 2.0], "listener_pos": [0.0, 0.0, 0.0]}'
        }
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. {test_case['name']}")
        print("-" * 30)

        response = simulate_api_request(test_case['payload'])

        if response['status'] == 200:
            print("✅ Success!")
            metadata = response['metadata']
            print(f"   Distance: {metadata['distance']:.2f} m")
            print(f"   Image size: {len(response['image_data'])} bytes (base64)")

            # Save the actual image for this test case
            img_data = base64.b64decode(response['image_data'])
            filename = f"api_demo_{i}.png"
            with open(filename, 'wb') as f:
                f.write(img_data)
            print(f"   Saved as: {filename}")

        else:
            print(f"❌ Error ({response['status']}): {response['error']}")

def create_flask_setup_instructions():
    """Provide instructions for setting up Flask API."""
    print("\n" + "=" * 50)
    print("🔧 Flask API Setup Instructions")
    print("=" * 50)
    print("""
To set up the full Flask API server:

1. Install Flask:
   pip install flask

2. Run the API server:
   python spatial_audio_api.py

3. Test the API:
   curl -X POST http://localhost:5000/render \\
        -H "Content-Type: application/json" \\
        -d '{"source_pos": [5.0, 0.0, 2.0], "listener_pos": [0.0, 0.0, 0.0]}' \\
        --output visualization.png

4. API Endpoints:
   - POST /render: Generate visualization
   - GET /health: Health check
   - GET /: API documentation

The API accepts JSON with source_pos and listener_pos arrays,
returns PNG images for 3D spatial audio visualization.
""")

if __name__ == "__main__":
    demo_api_calls()
    create_flask_setup_instructions()
