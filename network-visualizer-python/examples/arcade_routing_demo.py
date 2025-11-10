"""
Arcade Routing Demo

Demonstrates routing network node movements to Arcade dispatcher.
"""
import sys
import time
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from network_visualizer.arcade import ArcadeIntegration


def simulate_network_nodes():
    """Generate simulated network node data."""
    import math
    
    nodes = []
    for i in range(1, 15):
        angle = (i / 14) * 2 * math.pi
        radius = 100 + (i * 20)
        
        # Calculate position
        x = 400 + math.cos(angle) * radius
        y = 400 + math.sin(angle) * radius
        
        # Calculate velocity (orbital motion)
        vx = -math.sin(angle) * 0.5
        vy = math.cos(angle) * 0.5
        
        # Metrics from report data
        degree = max(0.42, 0.85 - (i * 0.04))
        betweenness = max(0.02, 0.32 - (i * 0.03))
        eigenvector = max(0.23, 0.91 - (i * 0.06))
        nodeScore = (degree + betweenness + eigenvector) / 3
        
        # Habitat assignment
        if i <= 3:
            habitat = 'Core Nexus'
            color = '#ff6b9d'
        elif i <= 6:
            habitat = 'Hub Zone'
            color = '#4ecdc4'
        elif i <= 9:
            habitat = 'Bridge Territory'
            color = '#95e1d3'
        else:
            habitat = 'Peripheral Expanse'
            color = '#f38181'
        
        nodes.append({
            'id': f'Node{i}',
            'x': x,
            'y': y,
            'vx': vx,
            'vy': vy,
            'degree': degree,
            'betweenness': betweenness,
            'eigenvector': eigenvector,
            'nodeScore': nodeScore,
            'habitat': habitat,
            'habitatColor': color
        })
    
    return nodes


def main():
    """Run the Arcade routing demonstration."""
    print("=" * 60)
    print("Network Visualizer → Arcade Routing Demo")
    print("=" * 60)
    
    # Initialize Arcade integration
    arcade_root = Path("e:/Projects/Atmosphere/Arcade")
    
    if not arcade_root.exists():
        print(f"ERROR: Arcade root not found at {arcade_root}")
        print("Please ensure Arcade is installed at the correct path.")
        return
    
    print(f"\n✓ Arcade root: {arcade_root}")
    
    integration = ArcadeIntegration(arcade_root)
    print("✓ Arcade integration initialized")
    
    # Enable auto-routing
    integration.enable_auto_routing(interval=2.0)
    print("✓ Auto-routing enabled (interval: 2.0s)")
    
    print("\n" + "-" * 60)
    print("Simulating network node movements...")
    print("-" * 60)
    
    # Simulate 10 frames of movement
    for frame in range(10):
        print(f"\nFrame {frame + 1}/10:")
        
        # Generate node data
        nodes = simulate_network_nodes()
        
        # Add some randomness to movement
        import random
        for node in nodes:
            node['x'] += random.uniform(-1, 1)
            node['y'] += random.uniform(-1, 1)
            node['vx'] += random.uniform(-0.1, 0.1)
            node['vy'] += random.uniform(-0.1, 0.1)
        
        # Update integration
        integration.update(nodes)
        
        # Get summary
        summary = integration.router.get_movement_summary()
        print(f"  Active nodes: {summary['active_nodes']}")
        print(f"  Avg displacement: {summary['avg_displacement']:.4f}")
        print(f"  Avg velocity: {summary['avg_velocity']:.4f}")
        
        time.sleep(0.5)
    
    print("\n" + "-" * 60)
    print("Manual snapshot routing...")
    print("-" * 60)
    
    # Route final snapshot
    filepath = integration.route_snapshot(zone='visual')
    print(f"✓ Routed to: {filepath}")
    
    # Final summary
    summary = integration.router.get_movement_summary()
    print("\n" + "=" * 60)
    print("ROUTING SUMMARY")
    print("=" * 60)
    print(f"Total events: {summary['total_events']}")
    print(f"Active nodes: {summary['active_nodes']}")
    print(f"Avg displacement: {summary['avg_displacement']:.4f}")
    print(f"Avg velocity: {summary['avg_velocity']:.4f}")
    print(f"\nActive node IDs:")
    for node_id in integration.router.get_active_nodes():
        print(f"  - {node_id}")
    
    print("\n" + "=" * 60)
    print("✓ Demo complete!")
    print("=" * 60)
    print(f"\nCheck Arcade incoming directory:")
    print(f"  {arcade_root / 'incoming'}")
    print(f"\nCheck Arcade visual zone:")
    print(f"  {arcade_root / 'zones' / 'visual'}")
    print("\nTo process routed files, run:")
    print(f"  cd {arcade_root}")
    print(f"  python dispatcher.py")


if __name__ == "__main__":
    main()
