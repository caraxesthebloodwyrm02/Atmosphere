# Routing Module API

## Overview

The Routing module provides acoustic routing and network analysis capabilities, modeling networks as acoustic topologies where edges affect signal propagation.

## Classes

### AcousticRoutingNetwork

Main class for acoustic routing system modeling networks as acoustic topologies.

#### Constructor

```python
AcousticRoutingNetwork()
```

#### Attributes

- `graph`: NetworkX directed graph representing routing segments
- `acoustic_params`: Dictionary of acoustic parameters for edges
- `node_positions`: Dictionary of node positions for visualization

#### Methods

- `add_highway_segment(start, end, distance_miles, speed_limit_mph=65, interconnectivity=0.3, feedback_loops=0.2)`: Add highway segment with acoustic properties
- `add_node(node_id, position=None)`: Add node to network
- `add_edge(start, end, acoustic_params)`: Add edge with acoustic parameters
- `find_shortest_path(start, end)`: Find shortest path between nodes
- `find_optimal_route(start, end, criteria='distance')`: Find optimal route based on criteria
- `analyze_network()`: Analyze network acoustic properties
- `propagate_pulse(start_node, pulse)`: Propagate signal through network
- `visualize_network(save_path=None)`: Create network visualization

### AcousticParameters

Acoustic properties for routing edges.

#### Constructor

```python
AcousticParameters(
    delay_time=0.0,
    feedback=0.0,
    decay=0.0,
    reverb_density=0.0
)
```

#### Attributes

- `delay_time` (float): Travel time or physical distance (ms)
- `feedback` (float): Number of alternate routes/detours (0-1)
- `decay` (float): Traffic dissipation/energy loss (0-1)
- `reverb_density` (float): Local interconnectivity (0-1)

### Pulse

Represents a propagating signal through the network.

#### Constructor

```python
Pulse(
    origin,
    current_position,
    amplitude=1.0,
    path_history=None
)
```

#### Attributes

- `origin`: Starting node
- `current_position`: Current node position
- `amplitude`: Signal amplitude
- `path_history`: List of nodes visited

## Usage Examples

```python
from routing import AcousticRoutingNetwork, AcousticParameters

# Create network
network = AcousticRoutingNetwork()

# Add highway segments
network.add_highway_segment(
    start="CityA",
    end="CityB",
    distance_miles=50,
    speed_limit_mph=70,
    interconnectivity=0.4,
    feedback_loops=0.2
)

# Add another segment
network.add_highway_segment(
    start="CityB",
    end="CityC",
    distance_miles=75,
    speed_limit_mph=65,
    interconnectivity=0.6,
    feedback_loops=0.3
)

# Find optimal route
route = network.find_optimal_route("CityA", "CityC")
print(f"Optimal route: {route}")

# Visualize network
network.visualize_network(save_path="network_plot.png")

# Analyze network
analysis = network.analyze_network()
print(f"Network analysis: {analysis}")
```
