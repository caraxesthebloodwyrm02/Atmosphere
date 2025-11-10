#!/usr/bin/env python3
"""
Custom Spatial Audio Visualizer - Window & Shelf Reference
Creates a 3D visualization showing spatial audio setup with reference objects.
"""

import argparse
import numpy as np

# Optional dependency guard for matplotlib
try:
    import matplotlib
    matplotlib.use('TkAgg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Warning: matplotlib not available. Install with: pip install matplotlib")


def find_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Return Euclidean distance |a-b|."""
    return float(np.linalg.norm(a - b))


def plot_spatial_audio_with_references(
    source_pos: tuple[float, float, float] = (5.0, 0.0, 2.0),
    listener_pos: tuple[float, float, float] = (0.0, 0.0, 1.0),  # Raised listener to 1m height
    save_demo: bool = False,
) -> None:
    """
    Render a 3-D plot showing source, listener, and room references with better spatial context.
    """
    if not MATPLOTLIB_AVAILABLE:
        raise ImportError("matplotlib required for visualization")

    # Convert to NumPy arrays
    src = np.array(source_pos, dtype=float)
    lst = np.array(listener_pos, dtype=float)

    dist = find_distance(src, lst)

    fig = plt.figure(figsize=(14, 10))
    ax = fig.add_subplot(111, projection="3d")

    # Plot main audio elements with larger markers
    ax.scatter(*lst, color="blue", s=200, label="Listener", marker="^", depthshade=False)
    ax.scatter(*src, color="red", s=200, label="Sound Source", marker="o", depthshade=False)

    # Draw distance bar with arrow markers
    ax.plot(
        [lst[0], src[0]],
        [lst[1], src[1]],
        [lst[2], src[2]],
        color="green",
        linewidth=3,
        label=f"Distance = {dist:.2f} m",
        marker='>',
        markersize=10,
        markevery=[1]  # Only show arrow at the end
    )

    # Room dimensions
    room_length = 6.0  # X-axis (depth)
    room_width = 6.0   # Y-axis (width)
    room_height = 3.0  # Z-axis (height)
    wall_thickness = 0.2

    # Add room walls with transparency
    def add_wall(ax, x, y, z, color, alpha=0.1, label=None):
        # Only add label to the first wall to avoid duplicate legend entries
        if label:
            ax.plot_surface(x, y, z, color=color, alpha=alpha, label=label)
        else:
            ax.plot_surface(x, y, z, color=color, alpha=alpha)
        
        # Add wireframe for edges
        ax.plot_wireframe(x, y, z, color=color, alpha=0.3, linewidth=0.5)

    # Floor
    X_floor, Y_floor = np.meshgrid(
        np.linspace(0, room_length, 2),
        np.linspace(-room_width/2, room_width/2, 2)
    )
    Z_floor = np.zeros_like(X_floor)
    add_wall(ax, X_floor, Y_floor, Z_floor, color='lightgray', alpha=0.1, label='Floor')

    # Walls - using proper 3D surfaces
    # Back wall (X = room_length)
    Y_wall, Z_wall = np.meshgrid(
        np.linspace(-room_width/2, room_width/2, 2),
        np.linspace(0, room_height, 2)
    )
    X_wall = np.ones_like(Y_wall) * room_length
    add_wall(ax, X_wall, Y_wall, Z_wall, color='lightblue', alpha=0.1, label='Walls')

    # Left wall (Y = -room_width/2)
    X_wall, Z_wall = np.meshgrid(
        np.linspace(0, room_length, 2),
        np.linspace(0, room_height, 2)
    )
    Y_wall = np.ones_like(X_wall) * (-room_width/2)
    add_wall(ax, X_wall, Y_wall, Z_wall, color='lightblue', alpha=0.1)

    # Right wall (Y = room_width/2)
    Y_wall = np.ones_like(X_wall) * (room_width/2)
    add_wall(ax, X_wall, Y_wall, Z_wall, color='lightblue', alpha=0.1)

    # Ceiling
    X_ceiling, Y_ceiling = np.meshgrid(
        np.linspace(0, room_length, 2),
        np.linspace(-room_width/2, room_width/2, 2)
    )
    Z_ceiling = np.ones_like(X_ceiling) * room_height
    add_wall(ax, X_ceiling, Y_ceiling, Z_ceiling, color='lightgray', alpha=0.1, label='Ceiling')

    # Add WINDOW on the left wall (Y = -room_width/2)
    window_width = 2.0
    window_height = 1.5
    window_bottom = 1.0
    window_left = 2.0
    
    window_x = [window_left, window_left + window_width, window_left + window_width, window_left, window_left]
    window_y = [-room_width/2] * 5
    window_z = [window_bottom, window_bottom, window_bottom + window_height, window_bottom + window_height, window_bottom]
    
    # Fill the window with semi-transparent blue
    ax.plot_surface(
        np.array([[window_left, window_left], [window_left + window_width, window_left + window_width]]),
        np.array([[-room_width/2, -room_width/2], [-room_width/2, -room_width/2]]),
        np.array([[window_bottom, window_bottom + window_height], [window_bottom, window_bottom + window_height]]),
        color='cyan', alpha=0.3, label='Window'
    )
    ax.plot(window_x, window_y, window_z, color='blue', linewidth=2, linestyle='-', label='Window Frame')

    # Add DOOR on the right wall (Y = room_width/2)
    door_width = 1.0
    door_height = 2.1
    door_left = 1.0
    
    door_x = [door_left, door_left + door_width, door_left + door_width, door_left, door_left]
    door_y = [room_width/2] * 5
    door_z = [0, 0, door_height, door_height, 0]
    
    # Fill the door with semi-transparent brown
    ax.plot_surface(
        np.array([[door_left, door_left], [door_left + door_width, door_left + door_width]]),
        np.array([[room_width/2, room_width/2], [room_width/2, room_width/2]]),
        np.array([[0, door_height], [0, door_height]]),
        color='sandybrown', alpha=0.3, label='Door'
    )
    ax.plot(door_x, door_y, door_z, color='saddlebrown', linewidth=2, linestyle='-', label='Door Frame')

    # Add SHELF on the back wall
    shelf_width = 1.5
    shelf_depth = 0.3
    shelf_height = 1.8
    shelf_left = 4.0
    
    # Shelf top
    shelf_x = [shelf_left, shelf_left + shelf_width, shelf_left + shelf_width, shelf_left, shelf_left]
    shelf_y = [room_width/4 - shelf_depth/2] * 5
    shelf_z = [shelf_height] * 5
    ax.plot_surface(
        np.array([[shelf_left, shelf_left], [shelf_left + shelf_width, shelf_left + shelf_width]]),
        np.array([[room_width/4 - shelf_depth/2, room_width/4 + shelf_depth/2], 
                 [room_width/4 - shelf_depth/2, room_width/4 + shelf_depth/2]]),
        np.array([[shelf_height, shelf_height], [shelf_height, shelf_height]]),
        color='peru', alpha=0.5, label='Shelf'
    )
    
    # Shelf supports
    ax.plot([shelf_left, shelf_left], [room_width/4 - shelf_depth/2, room_width/4 - shelf_depth/2], 
            [0, shelf_height], color='sienna', linewidth=2)
    ax.plot([shelf_left + shelf_width, shelf_left + shelf_width], 
            [room_width/4 - shelf_depth/2, room_width/4 - shelf_depth/2], 
            [0, shelf_height], color='sienna', linewidth=2)

    # Add coordinate axes at origin for reference
    axis_length = 1.0
    ax.quiver(0, 0, 0, axis_length, 0, 0, color='r', arrow_length_ratio=0.1, label='X (Front)')
    ax.quiver(0, 0, 0, 0, axis_length, 0, color='g', arrow_length_ratio=0.1, label='Y (Right)')
    ax.quiver(0, 0, 0, 0, 0, axis_length, color='b', arrow_length_ratio=0.1, label='Z (Up)')

    # Labels & title with improved formatting
    ax.set_xlabel("X (m) - Depth (Front to Back)", fontsize=10, labelpad=10)
    ax.set_ylabel("Y (m) - Width (Left to Right)", fontsize=10, labelpad=10)
    ax.set_zlabel("Z (m) - Height", fontsize=10, labelpad=10)
    ax.set_title("3D Spatial Audio Setup - Room with References", fontsize=12, pad=20)

    # Set axis limits with some padding
    padding = 0.5
    ax.set_xlim(0 - padding, room_length + padding)
    ax.set_ylim(-room_width/2 - padding, room_width/2 + padding)
    ax.set_zlim(0 - 0.1, room_height + 0.5)  # Slight extension above ceiling for labels

    # Improved 3D view angle - looking into the room from the front-left
    ax.view_init(elev=25, azim=45)

    # Add text annotations with improved positioning
    text_offset = 0.2
    ax.text(lst[0], lst[1], lst[2] + text_offset, "  Listener", color="blue", 
            fontsize=10, ha='left', va='bottom')
    ax.text(src[0], src[1], src[2] + text_offset, "  Sound Source", color="red", 
            fontsize=10, ha='left', va='bottom')
    
    # Room feature labels
    ax.text(room_length/2, 0, room_height + 0.3, "Back Wall", color='darkblue', 
            ha='center', va='bottom', fontsize=9)
    ax.text(0, -room_width/2 - 0.3, room_height/2, "Left Wall", color='darkblue', 
            ha='center', va='center', rotation=90, fontsize=9)
    ax.text(0, room_width/2 + 0.3, room_height/2, "Right Wall", color='darkblue', 
            ha='center', va='center', rotation=-90, fontsize=9)
    
    # Feature labels
    ax.text(window_left + window_width/2, -room_width/2 - 0.1, window_bottom + window_height/2, 
            "Window", color='darkblue', ha='center', va='center', fontsize=9)
    ax.text(door_left + door_width/2, room_width/2 + 0.1, door_height/2, 
            "Door", color='saddlebrown', ha='center', va='center', fontsize=9)
    ax.text(shelf_left + shelf_width/2, room_width/4 - shelf_depth - 0.1, shelf_height + 0.1, 
            "Shelf", color='sienna', ha='center', va='bottom', fontsize=9)

    # Add a grid for better depth perception
    ax.grid(True, linestyle=':', alpha=0.5)
    
    # Add a legend with better positioning
    leg = ax.legend(loc='upper right', bbox_to_anchor=(1.3, 0.9), fontsize=9)
    leg.set_title('Legend', prop={'weight': 'bold'})

    plt.tight_layout()

    if save_demo:
        plt.savefig('spatial_room_references.png', dpi=150, bbox_inches='tight')
        print("Room reference visualization saved as 'spatial_room_references.png'")
    else:
        plt.show()


def build_arg_parser() -> argparse.ArgumentParser:
    """Return ArgumentParser for optional CLI parsing."""
    parser = argparse.ArgumentParser(
        description="Render a 3D spatial audio scene with room references (window, shelf)."
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
    plot_spatial_audio_with_references(
        source_pos=tuple(args.source),
        listener_pos=tuple(args.listener),
        save_demo=args.save_demo
    )
