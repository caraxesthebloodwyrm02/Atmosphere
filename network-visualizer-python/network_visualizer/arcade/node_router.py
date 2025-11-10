"""
Node Router for Arcade Integration

Routes all moving network nodes to Arcade's dispatcher system.
Tracks node positions, velocities, and states for dynamic routing.
"""
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import asyncio


@dataclass
class NodeState:
    """State snapshot of a moving node."""
    id: str
    x: float
    y: float
    vx: float
    vy: float
    degree: float
    betweenness: float
    eigenvector: float
    nodeScore: float
    habitat: str
    habitatColor: str
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class NodeMovementEvent:
    """Event representing node movement."""
    node_id: str
    previous_state: NodeState
    current_state: NodeState
    displacement: float
    velocity_magnitude: float
    timestamp: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'node_id': self.node_id,
            'previous_state': self.previous_state.to_dict(),
            'current_state': self.current_state.to_dict(),
            'displacement': self.displacement,
            'velocity_magnitude': self.velocity_magnitude,
            'timestamp': self.timestamp
        }


class NodeRouter:
    """
    Routes network node movements to Arcade dispatcher.
    
    Tracks all moving objects and generates routing events for Arcade zones.
    """
    
    def __init__(self, arcade_root: Path, incoming_dir: Optional[Path] = None):
        """
        Initialize node router.
        
        Args:
            arcade_root: Path to Arcade root directory
            incoming_dir: Optional custom incoming directory (defaults to arcade_root/incoming)
        """
        self.arcade_root = Path(arcade_root)
        self.incoming_dir = incoming_dir or (self.arcade_root / "incoming")
        self.incoming_dir.mkdir(parents=True, exist_ok=True)
        
        self.node_states: Dict[str, NodeState] = {}
        self.movement_history: List[NodeMovementEvent] = []
        self.max_history = 1000  # Keep last 1000 events
        
    def register_node(
        self, 
        node_id: str,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = 0.0,
        **kwargs
    ) -> None:
        """
        Register a node with the router.
        
        Args:
            node_id: Unique node identifier
            x, y: Current position
            vx, vy: Current velocity
            **kwargs: Additional node properties (degree, betweenness, etc.)
        """
        state = NodeState(
            id=node_id,
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            degree=kwargs.get('degree', 0.0),
            betweenness=kwargs.get('betweenness', 0.0),
            eigenvector=kwargs.get('eigenvector', 0.0),
            nodeScore=kwargs.get('nodeScore', 0.0),
            habitat=kwargs.get('habitat', 'unknown'),
            habitatColor=kwargs.get('habitatColor', '#999'),
            timestamp=time.time()
        )
        self.node_states[node_id] = state
    
    def update_node(
        self,
        node_id: str,
        x: float,
        y: float,
        vx: float = 0.0,
        vy: float = 0.0,
        **kwargs
    ) -> Optional[NodeMovementEvent]:
        """
        Update node position and generate movement event.
        
        Args:
            node_id: Node to update
            x, y: New position
            vx, vy: New velocity
            **kwargs: Updated properties
            
        Returns:
            NodeMovementEvent if node moved significantly, None otherwise
        """
        if node_id not in self.node_states:
            self.register_node(node_id, x, y, vx, vy, **kwargs)
            return None
        
        previous = self.node_states[node_id]
        
        # Calculate displacement
        dx = x - previous.x
        dy = y - previous.y
        displacement = (dx**2 + dy**2)**0.5
        
        # Calculate velocity magnitude
        velocity_mag = (vx**2 + vy**2)**0.5
        
        # Create new state
        current = NodeState(
            id=node_id,
            x=x,
            y=y,
            vx=vx,
            vy=vy,
            degree=kwargs.get('degree', previous.degree),
            betweenness=kwargs.get('betweenness', previous.betweenness),
            eigenvector=kwargs.get('eigenvector', previous.eigenvector),
            nodeScore=kwargs.get('nodeScore', previous.nodeScore),
            habitat=kwargs.get('habitat', previous.habitat),
            habitatColor=kwargs.get('habitatColor', previous.habitatColor),
            timestamp=time.time()
        )
        
        self.node_states[node_id] = current
        
        # Generate event only if significant movement (threshold: 0.1 pixels)
        if displacement > 0.1 or velocity_mag > 0.01:
            event = NodeMovementEvent(
                node_id=node_id,
                previous_state=previous,
                current_state=current,
                displacement=displacement,
                velocity_magnitude=velocity_mag,
                timestamp=time.time()
            )
            
            self.movement_history.append(event)
            
            # Trim history if needed
            if len(self.movement_history) > self.max_history:
                self.movement_history = self.movement_history[-self.max_history:]
            
            return event
        
        return None
    
    def route_to_arcade(
        self,
        tool_name: str = "network_visualizer",
        zone: str = "visual",
        events: Optional[List[NodeMovementEvent]] = None
    ) -> Path:
        """
        Route node events to Arcade dispatcher.
        
        Args:
            tool_name: Name of the tool generating events
            zone: Target zone for routing
            events: Specific events to route (defaults to recent history)
            
        Returns:
            Path to created routing file
        """
        if events is None:
            # Use last 100 events from history
            events = self.movement_history[-100:]
        
        # Create routing payload
        payload = {
            'tool': tool_name,
            'zone': zone,
            'timestamp': time.time(),
            'node_count': len(self.node_states),
            'event_count': len(events),
            'node_states': {
                node_id: state.to_dict()
                for node_id, state in self.node_states.items()
            },
            'movement_events': [event.to_dict() for event in events]
        }
        
        # Write to incoming directory
        filename = f"{tool_name}_{int(time.time() * 1000)}.json"
        filepath = self.incoming_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(payload, f, indent=2)
        
        return filepath
    
    def get_active_nodes(self) -> List[str]:
        """Get list of all registered node IDs."""
        return list(self.node_states.keys())
    
    def get_node_state(self, node_id: str) -> Optional[NodeState]:
        """Get current state of a specific node."""
        return self.node_states.get(node_id)
    
    def get_movement_summary(self) -> Dict[str, Any]:
        """Get summary of recent movement activity."""
        if not self.movement_history:
            return {
                'total_events': 0,
                'active_nodes': 0,
                'avg_displacement': 0.0,
                'avg_velocity': 0.0
            }
        
        recent_events = self.movement_history[-100:]
        
        total_displacement = sum(e.displacement for e in recent_events)
        total_velocity = sum(e.velocity_magnitude for e in recent_events)
        
        active_nodes = len(set(e.node_id for e in recent_events))
        
        return {
            'total_events': len(recent_events),
            'active_nodes': active_nodes,
            'avg_displacement': total_displacement / len(recent_events),
            'avg_velocity': total_velocity / len(recent_events),
            'timestamp': time.time()
        }
    
    def clear_history(self) -> None:
        """Clear movement history."""
        self.movement_history.clear()
    
    def clear_all(self) -> None:
        """Clear all node states and history."""
        self.node_states.clear()
        self.movement_history.clear()


class ArcadeIntegration:
    """
    High-level integration between Network Visualizer and Arcade.
    
    Provides automatic routing of network events to Arcade zones.
    """
    
    def __init__(self, arcade_root: Path):
        """
        Initialize Arcade integration.
        
        Args:
            arcade_root: Path to Arcade root directory
        """
        self.router = NodeRouter(arcade_root)
        self.auto_route = False
        self.route_interval = 5.0  # Route every 5 seconds
        self.last_route_time = 0.0
    
    def enable_auto_routing(self, interval: float = 5.0) -> None:
        """
        Enable automatic routing to Arcade.
        
        Args:
            interval: Routing interval in seconds
        """
        self.auto_route = True
        self.route_interval = interval
    
    def disable_auto_routing(self) -> None:
        """Disable automatic routing."""
        self.auto_route = False
    
    def update(self, node_data: List[Dict[str, Any]]) -> None:
        """
        Update all nodes and route if needed.
        
        Args:
            node_data: List of node dictionaries with position/velocity data
        """
        events = []
        
        for node in node_data:
            event = self.router.update_node(
                node_id=node['id'],
                x=node['x'],
                y=node['y'],
                vx=node.get('vx', 0.0),
                vy=node.get('vy', 0.0),
                degree=node.get('degree', 0.0),
                betweenness=node.get('betweenness', 0.0),
                eigenvector=node.get('eigenvector', 0.0),
                nodeScore=node.get('nodeScore', 0.0),
                habitat=node.get('habitat', 'unknown'),
                habitatColor=node.get('habitatColor', '#999')
            )
            
            if event:
                events.append(event)
        
        # Auto-route if enabled and interval elapsed
        if self.auto_route:
            current_time = time.time()
            if current_time - self.last_route_time >= self.route_interval:
                if events:
                    self.router.route_to_arcade(events=events)
                    self.last_route_time = current_time
    
    def route_snapshot(self, zone: str = "visual") -> Path:
        """
        Route current snapshot to Arcade.
        
        Args:
            zone: Target zone
            
        Returns:
            Path to routing file
        """
        return self.router.route_to_arcade(zone=zone)
