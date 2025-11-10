# Network Visualizer Routing to Arcade

Complete guide for routing network node movements from Network Visualizer to Arcade zones.

## Quick Start

### 1. Install Dependencies
```bash
cd e:/Projects/Atmosphere/network-visualizer-python
pip install -r requirements-fastapi.txt

cd e:/Projects/Atmosphere/Arcade
pip install -r requirements.txt
```

### 2. Start Arcade Dispatcher
```bash
cd e:/Projects/Atmosphere/Arcade
python dispatcher.py
```

### 3. Run Routing Demo
```bash
cd e:/Projects/Atmosphere/network-visualizer-python
python examples/arcade_routing_demo.py
```

## What Gets Routed

All **moving objects** (nodes) in the network visualization are tracked and routed:

- **Node Position** (x, y coordinates)
- **Node Velocity** (vx, vy velocity vectors)
- **Node Metrics** (degree, betweenness, eigenvector centrality)
- **NodeScore** (composite metric: average of three centralities)
- **Habitat** (Core Nexus, Hub Zone, Bridge Territory, Peripheral Expanse)
- **Movement Events** (displacement, velocity changes)

## Routing Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Network Visualizer                                          │
│ ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│ │   Node1    │───▶│   Node2    │───▶│   Node3    │        │
│ │  Moving ⚡ │    │  Moving ⚡ │    │  Moving ⚡ │        │
│ └────────────┘    └────────────┘    └────────────┘        │
│         │                 │                 │               │
│         └─────────────────┴─────────────────┘               │
│                           │                                 │
│                           ▼                                 │
│                   ┌──────────────┐                         │
│                   │  NodeRouter  │                         │
│                   └──────────────┘                         │
└─────────────────────────│───────────────────────────────────┘
                          │
                          │ JSON Payloads
                          ▼
┌─────────────────────────────────────────────────────────────┐
│ Arcade System                                               │
│ ┌────────────────────────────────────────────────────────┐ │
│ │ incoming/                                              │ │
│ │   network_visualizer_1699464123456.json               │ │
│ └────────────────────────────────────────────────────────┘ │
│                           │                                 │
│                           ▼                                 │
│                   ┌──────────────┐                         │
│                   │  Dispatcher  │                         │
│                   └──────────────┘                         │
│                           │                                 │
│               ┌───────────┴───────────┐                    │
│               ▼                       ▼                    │
│       ┌──────────────┐        ┌──────────────┐            │
│       │ Visual Zone  │        │  Audio Zone  │            │
│       └──────────────┘        └──────────────┘            │
│               │                                             │
│               ▼                                             │
│       ┌──────────────────────┐                            │
│       │ Node Processor       │                            │
│       │ - Movement Analysis  │                            │
│       │ - Classification     │                            │
│       │ - Habitat Report     │                            │
│       └──────────────────────┘                            │
│               │                                             │
│               ▼                                             │
│       ┌──────────────────────┐                            │
│       │ zones/visual/outputs/│                            │
│       │   latest_analysis    │                            │
│       └──────────────────────┘                            │
└─────────────────────────────────────────────────────────────┘
```

## Routing Configuration

**File:** `Arcade/config/routing.yaml`

```yaml
# Network Visualizer - Moving Object Routing
network_visualizer: visual        # Main visualizer
network_nodes: visual             # All network nodes
node_tracker: visual              # Node tracking
node_movement: visual             # Movement events
network_ecosystem: visual         # Ecosystem view

# Node-specific routing (by habitat)
core_nexus_nodes: visual         # Core nodes
hub_zone_nodes: visual           # Hub nodes
bridge_territory_nodes: visual   # Bridge nodes
peripheral_expanse_nodes: visual # Peripheral nodes

# Integration points routing
integration_points: visual       # IPs between core/peripheral
compass_instrumentation: visual  # Compass data
```

## Example Payload

When nodes move, payloads like this are sent to Arcade:

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
      "x": 400.5,
      "y": 300.2,
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
      "displacement": 1.5,
      "velocity_magnitude": 0.58,
      "timestamp": 1699464123.456
    }
  ]
}
```

## Processing Output

**Location:** `Arcade/zones/visual/outputs/latest_analysis.json`

```json
{
  "timestamp": 1699464123.456,
  "movement_analysis": {
    "total_events": 42,
    "avg_displacement": 0.8234,
    "avg_velocity": 0.4521,
    "active_nodes": 12
  },
  "node_classification": {
    "static": [],
    "slow": ["Node10", "Node11"],
    "active": ["Node1", "Node2", "Node3"],
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
    }
  }
}
```

## Monitoring

### Watch Incoming Files
```bash
watch -n 1 "ls -lh e:/Projects/Atmosphere/Arcade/incoming/"
```

### View Processing Logs
```bash
tail -f e:/Projects/Atmosphere/Arcade/zones/visual/network_visualizer.log
```

### Check Latest Analysis
```bash
cat e:/Projects/Atmosphere/Arcade/zones/visual/outputs/latest_analysis.json | jq
```

## Integration with Web Report

The generated HTML report now tracks node movements in real-time. To enable routing:

```html
<!-- Add to report.html.j2 -->
<script>
// Initialize Arcade routing (if running in integrated environment)
if (window.arcadeIntegration) {
  window.arcadeIntegration.enableAutoRouting(5.0);
  
  // Update on each animation frame
  function updateArcade() {
    const nodeData = nodePositions.map(n => ({
      id: n.id,
      x: n.x,
      y: n.y,
      vx: n.vx,
      vy: n.vy,
      degree: n.degree,
      betweenness: n.betweenness,
      eigenvector: n.eigenvector,
      nodeScore: n.nodeScore,
      habitat: n.habitat,
      habitatColor: n.habitatColor
    }));
    
    window.arcadeIntegration.update(nodeData);
  }
}
</script>
```

## Advanced Usage

### Route Specific Habitats
```python
from network_visualizer.arcade import NodeRouter

router = NodeRouter(arcade_root)

# Route only Core Nexus nodes
core_events = [
    e for e in router.movement_history
    if router.get_node_state(e.node_id).habitat == 'Core Nexus'
]
router.route_to_arcade(
    tool_name='core_nexus_nodes',
    zone='visual',
    events=core_events
)
```

### Custom Processing
```python
# Create custom processor
class CustomNodeProcessor:
    def process(self, payload):
        # Your custom processing logic
        pass

# Route to custom processor
router.route_to_arcade(
    tool_name='custom_processor',
    zone='custom'
)
```

## Troubleshooting

**Q: Payloads not appearing in incoming/**  
A: Check that Arcade root path is correct and `incoming/` directory exists.

**Q: Dispatcher not processing files**  
A: Ensure dispatcher is running and routing.yaml has correct mappings.

**Q: Processor errors**  
A: Check `zones/visual/network_visualizer.log` for error details.

**Q: No movement events generated**  
A: Verify nodes are actually moving (displacement > 0.1 pixels).

## Files Created

```
network-visualizer-python/
├── network_visualizer/
│   └── arcade/
│       ├── __init__.py
│       └── node_router.py
└── examples/
    └── arcade_routing_demo.py

Arcade/
├── config/
│   └── routing.yaml (updated)
├── tools/
│   └── network_node_processor.py
├── dispatcher.py (updated)
├── NETWORK_INTEGRATION.md
└── README_NETWORK_ROUTING.md (this file)
```

## Next Steps

1. Run the demo to see routing in action
2. Start the Arcade dispatcher to process payloads
3. Monitor the visual zone outputs
4. Integrate with your custom processors
5. Build dashboards to visualize routing data

---

**Status:** ✅ Operational  
**Version:** 1.0.0  
**Last Updated:** 2025-11-08
