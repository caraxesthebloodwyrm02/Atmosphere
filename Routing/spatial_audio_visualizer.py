"""
spatial_audio_visualizer.py

Standalone 3D spatial audio visualizer for the Dimension & Resonance platform.
Creates static visualizations of sound source-listener relationships in 3D space.

Features:
* Interactive 3D plotting with source (red), listener (blue), and distance bar (green)
* Command-line interface with customizable positions
* Demo image generation for documentation
* Graceful matplotlib dependency handling
* TkAgg backend for Windows IDE compatibility

Command-line usage:
  python spatial_audio_visualizer.py [--source x y z] [--listener x y z] [--save-demo]

Examples:
  python spatial_audio_visualizer.py  # Default positions
  python spatial_audio_visualizer.py --source 4 1 2 --listener -1 0 0  # Custom positions
  python spatial_audio_visualizer.py --save-demo  # Save PNG without displaying
"""

import argparse

# Optional dependency guard for matplotlib
try:
    import matplotlib
    # Explicitly set backend before importing pyplot
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401  (imported for side‑effect)
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


def find_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return Euclidean distance |a‑b|."""
    return float(np.linalg.norm(a - b))


def plot_spatial_audio(
    source_pos: tuple[float, float, float] = (5.0, 0.0, 2.0),
    listener_pos: tuple[float, float, float] = (0.0, 0.0, 0.0),
    save_demo: bool = False,
) -> None:
    """
    Render a 3‑D plot showing source, listener, and distance bar.

    Parameters
    ----------
    source_pos : tuple[float, float, float]
        (x, y, z) coordinates of the sound source.
    listener_pos : tuple[float, float, float]
        (x, y, z) coordinates of the listener.
    save_demo : bool
        If True, save a demo image instead of showing interactive plot.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib required for visualization")

    # Convert to NumPy arrays for distance calculation
    src = np.array(source_pos, dtype=float)
    lst = np.array(listener_pos, dtype=float)

    dist = find_distance(src, lst)

    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection="3d")

    # Plot nodes
    ax.scatter(*lst, color="blue", s=120, label="Listener")
    ax.scatter(*src, color="red", s=120, label="Sound Source")

    # Draw distance bar
    ax.plot(
        [lst[0], src[0]],
        [lst[1], src[1]],
        [lst[2], src[2]],
        color="green",
        linewidth=3,
        label=f"Distance = {dist:.2f} m",
    )

    # Labels & title
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.set_zlabel("Z (m)")
    ax.set_title("3‑D Spatial Audio Setup")
    ax.legend()

    # 3‑D view angle tweaks (optional)
    ax.view_init(elev=20, azim=120)

    if save_demo:
        # Save demo image for sharing without GUI
        plt.savefig('spatial_demo.png', dpi=150, bbox_inches='tight')
        print("Demo image saved as 'spatial_demo.png'")
    else:
        plt.show()


def build_arg_parser() -> argparse.ArgumentParser:
    """Return ArgumentParser for optional CLI parsing."""
    parser = argparse.ArgumentParser(
        description="Render a basic 3‑D spatial audio scene."
    )
    sub = parser.add_argument_group("source")
    sub.add_argument(
        "--source",
        nargs=3,
        type=float,
        metavar=("X", "Y", "Z"),
        default=(5.0, 0.0, 2.0),
        help="Coordinates of the sound source (default: 5 0 2)",
    )
    sub = parser.add_argument_group("listener")
    sub.add_argument(
        "--listener",
        nargs=3,
        type=float,
        metavar=("X", "Y", "Z"),
        default=(0.0, 0.0, 0.0),
        help="Coordinates of the listener (default: 0 0 0)",
    )
    parser.add_argument(
        "--save-demo",
        action="store_true",
        help="Save demo image instead of showing interactive plot",
    )
    return parser


if __name__ == "__main__":
    args = build_arg_parser().parse_args()
    plot_spatial_audio(
        source_pos=tuple(args.source),
        listener_pos=tuple(args.listener),
        save_demo=args.save_demo
    )
