# Network Visualizer → Arcade Integration

Complete integration guide for routing network node movements to Arcade zones.

## Overview

The Network Visualizer now routes all moving objects (nodes) to Arcade's dispatcher system, enabling dynamic processing of network topology changes, node movements, and interaction events.

## Architecture

```
Network Visualizer (Python)
    ↓ Node Movement Events
NodeRouter (network_visualizer/arcade/node_router.py)
    ↓ JSON Payloads
Arcade Incoming Directory (Arcade/incoming/)
    ↓ File System Events
Arcade Dispatcher (Arcade/dispatcher.py)
    ↓ Routed to Zones
Network Node Processor (Arcade/tools/network_node_processor.py)
    ↓ Processing Results
Arcade Visual Zone (Arcade/zones/visual/)
```

## Components

### 1. NodeRouter (Network Visualizer Side)
**Location:** `network_visualizer/arcade/node_router.py`

Tracks all moving nodes and generates routing events:
- **NodeState**: Snapshot of node position, velocity, metrics
- **NodeMovementEvent**: Displacement and velocity changes
- **NodeRouter**: Main routing engine
- **ArcadeIntegration**: High-level integration API

### 2. Routing Configuration (Arcade Side)
**Location:** `Arcade/config/routing.yaml`

Maps network tools to zones:
```yaml
# Network Visualizer - Moving Object Routing
network_visualizer: visual
network_nodes: visual
node_tracker: visual
node_movement: visual
network_ecosystem: visual

# Node-specific routing (by habitat)
core_nexus_nodes: visual
hub_zone_nodes: visual
bridge_territory_nodes: visual
peripheral_expanse_nodes: visual

# Integration points routing
integration_points: visual
compass_instrumentation: visual
```

### 3. Node Processor (Arcade Side)
**Location:** `Arcade/tools/network_node_processor.py`

Processes routed node events:
- Movement pattern analysis
- Node activity classification
- Habitat distribution analysis
- Output generation for visual zone

## Usage

### Basic Integration

```python
from network_visualizer.arcade import ArcadeIntegration
from pathlib import Path

# Initialize integration
arcade_root = Path("e:/Projects/Atmosphere/Arcade")
integration = ArcadeIntegration(arcade_root)

# Enable automatic routing (every 5 seconds)
integration.enable_auto_routing(interval=5.0)

# Update nodes (typically in animation loop)
node_data = [
    {
        'id': 'Node1',
        'x': 400.0,
        'y': 300.0,
        'vx': 0.5,
        'vy': -0.3,
        'degree': 0.85,
        'betweenness': 0.32,
        'eigenvector': 0.91,
        'nodeScore': 0.6933,
        'habitat': 'Core Nexus',
        'habitatColor': '#ff6b9d'
    },
    # ... more nodes
]

integration.update(node_data)

# Manual snapshot routing
integration.route_snapshot(zone='visual')
```

### Advanced Routing

```python
from network_visualizer.arcade import NodeRouter
from pathlib import Path

# Create router
router = NodeRouter(arcade_root=Path("e:/Projects/Atmosphere/Arcade"))

# Register nodes
router.register_node(
    node_id='Node1',
    x=400.0,
    y=300.0,
    vx=0.5,
    vy=-0.3,
    degree=0.85,
    betweenness=0.32,
    eigenvector=0.91,
    nodeScore=0.6933,
    habitat='Core Nexus',
    habitatColor='#ff6b9d'
)

# Update and track movement
event = router.update_node(
    node_id='Node1',
    x=401.5,
    y=299.7,
    vx=0.48,
    vy=-0.25
)

if event:
    print(f"Node moved: displacement={event.displacement:.4f}")

# Route to Arcade
filepath = router.route_to_arcade(
    tool_name='network_visualizer',
    zone='visual'
)
print(f"Routed to: {filepath}")
```

## Payload Format

JSON payloads sent to Arcade:

```json
{
  "tool": "network_visualizer",
  "zone": "visual",
  "timestamp": 1699464123.456,
  "node_count": 14,
  "event_count": 42,
  "node_states": {
    "Node1": {
      "id": "Node1",
      "x": 400.0,
      "y": 300.0,
      "vx": 0.5,
      "vy": -0.3,
      "degree": 0.85,
      "betweenness": 0.32,
      "eigenvector": 0.91,
      "nodeScore": 0.6933,
      "habitat": "Core Nexus",
      "habitatColor": "#ff6b9d",
      "timestamp": 1699464123.456
    }
  },
  "movement_events": [
    {
      "node_id": "Node1",
      "previous_state": { ... },
      "current_state": { ... },
      "displacement": 1.5,
      "velocity_magnitude": 0.58,
      "timestamp": 1699464123.456
    }
  ]
}
```

## Processing Output

Processor generates analysis in `zones/visual/outputs/`:

```json
{
  "timestamp": 1699464123.456,
  "tool": "network_visualizer",
  "zone": "visual",
  "node_count": 14,
  "event_count": 42,
  "movement_analysis": {
    "total_events": 42,
    "avg_displacement": 0.8234,
    "avg_velocity": 0.4521,
    "max_displacement": 2.3456,
    "max_velocity": 1.2345,
    "active_nodes": 12
  },
  "node_classification": {
    "static": [],
    "slow": ["Node10", "Node11"],
    "active": ["Node1", "Node2", "Node3", "Node4", "Node5"],
    "hyperactive": []
  },
  "habitat_report": {
    "habitat_counts": {
      "Core Nexus": 3,
      "Hub Zone": 3,
      "Bridge Territory": 3,
      "Peripheral Expanse": 5
    },
    "habitat_avg_scores": {
      "Core Nexus": 0.6933,
      "Hub Zone": 0.4833,
      "Bridge Territory": 0.3533,
      "Peripheral Expanse": 0.2667
    },
    "total_habitats": 4
  }
}
```

## Running the Integration

### 1. Start Arcade Dispatcher

```bash
cd e:/Projects/Atmosphere/Arcade
python dispatcher.py
```

### 2. Generate Network Report with Routing

```bash
cd e:/Projects/Atmosphere/network-visualizer-python
python examples/generate_report.py
```

The report will automatically track node movements and route to Arcade when integrated.

### 3. Monitor Arcade Zones

```bash
# Watch incoming directory
ls e:/Projects/Atmosphere/Arcade/incoming/

# Check visual zone outputs
ls e:/Projects/Atmosphere/Arcade/zones/visual/outputs/

# View latest analysis
cat e:/Projects/Atmosphere/Arcade/zones/visual/outputs/latest_analysis.json
```

## Integration with FastAPI Server

```python
from fastapi import FastAPI
from network_visualizer.ui.fastapi_server import app
from network_visualizer.arcade import ArcadeIntegration
from pathlib import Path

# Initialize Arcade integration
arcade_integration = ArcadeIntegration(
    arcade_root=Path("e:/Projects/Atmosphere/Arcade")
)
arcade_integration.enable_auto_routing(interval=5.0)

# Add endpoint to trigger manual routing
@app.post("/v1/arcade/route")
async def route_to_arcade():
    filepath = arcade_integration.route_snapshot(zone='visual')
    return {
        "success": True,
        "routed_to": str(filepath),
        "summary": arcade_integration.router.get_movement_summary()
    }

# Add endpoint to get routing status
@app.get("/v1/arcade/status")
async def get_arcade_status():
    return {
        "active_nodes": arcade_integration.router.get_active_nodes(),
        "summary": arcade_integration.router.get_movement_summary()
    }
```

## Habitat-Specific Routing

Route nodes by habitat to specialized zones:

```python
# Route only Core Nexus nodes
core_nodes = [
    node for node in node_data 
    if node['habitat'] == 'Core Nexus'
]
router.route_to_arcade(
    tool_name='core_nexus_nodes',
    zone='visual'
)

# Route integration points
integration_point_events = [
    event for event in router.movement_history
    if is_integration_point(event.node_id)
]
router.route_to_arcade(
    tool_name='integration_points',
    zone='visual',
    events=integration_point_events
)
```

## Monitoring and Debugging

### Check Routing Status
```python
summary = router.get_movement_summary()
print(f"Active nodes: {summary['active_nodes']}")
print(f"Avg displacement: {summary['avg_displacement']:.4f}")
print(f"Avg velocity: {summary['avg_velocity']:.4f}")
```

### View Dispatcher Logs
```bash
tail -f e:/Projects/Atmosphere/Arcade/zones/visual/network_visualizer.log
```

### Inspect Processed Files
```bash
ls -la e:/Projects/Atmosphere/Arcade/incoming/*.processed
```

## Troubleshooting

**Problem:** Payloads not routing to Arcade
- Check `incoming_dir` exists: `e:/Projects/Atmosphere/Arcade/incoming/`
- Verify dispatcher is running
- Check routing config has `network_visualizer: visual`

**Problem:** Processor not executing
- Ensure `network_node_processor.py` is executable
- Check Python path in dispatcher
- Verify zone directory permissions

**Problem:** No movement events generated
- Check displacement threshold (default: 0.1 pixels)
- Verify node positions are updating
- Review velocity magnitudes

## Next Steps

1. **Real-time Dashboard**: Create visual dashboard for Arcade zone outputs
2. **Event Filtering**: Add filters for specific node types or movements
3. **Multi-Zone Routing**: Route different node types to different zones
4. **Replay System**: Store and replay historical node movements
5. **Integration Testing**: Automated tests for routing pipeline

---

**Integration Status:** ✅ Active  
**Last Updated:** 2025-11-08  
**Version:** 1.0.0
