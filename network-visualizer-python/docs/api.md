# 🔧 API Reference

## Core Classes

### NetworkVisualizer

The main class for network visualization and analysis.

#### Constructor

```python
NetworkVisualizer(backend: str = 'matplotlib',
                 layout_method: str = 'spring')
```

**Parameters:**
- `backend` (str): Default rendering backend ('matplotlib', 'plotly', 'graphviz')
- `layout_method` (str): Default layout algorithm

#### Methods

##### Network Loading and Saving

```python
def load_network(self, filepath: Union[str, Path]) -> nx.Graph
```
Load network from file. Supports multiple formats with auto-detection.

```python
def save_network(self, G: nx.Graph, filepath: Union[str, Path]) -> None
```
Save network to file in specified format.

```python
def load_sample_graph(self, name: str) -> nx.Graph
```
Load built-in sample network.

**Available samples:**
- `'karate_club'` - Zachary's karate club
- `'davis_southern_women'` - Southern women dataset
- `'florentine_families'` - Florentine families
- `'les_miserables'` - Les Misérables characters
- `'football'` - College football teams

##### Analysis Methods

```python
def analyze_network(self, G: nx.Graph,
                   metrics: List[str] = None) -> Dict[str, Any]
```
Perform comprehensive network analysis.

```python
def compute_statistics(self, G: nx.Graph) -> Dict[str, Any]
```
Compute basic network statistics.

**Returns:**
- `num_nodes`: Number of nodes
- `num_edges`: Number of edges
- `density`: Network density (0-1)
- `average_degree`: Average node degree
- `diameter`: Network diameter (if computable)
- `average_path_length`: Average shortest path length
- `average_clustering`: Average clustering coefficient

```python
def compute_centrality(self, G: nx.Graph,
                      method: str) -> Dict[Any, float]
```
Compute node centrality measures.

**Methods:**
- `'degree'`: Degree centrality
- `'betweenness'`: Betweenness centrality
- `'closeness'`: Closeness centrality
- `'eigenvector'`: Eigenvector centrality
- `'pagerank'`: PageRank centrality
- `'katz'`: Katz centrality

##### Layout Methods

```python
def compute_layout(self, G: nx.Graph,
                  method: str = None,
                  **kwargs) -> Dict[Any, Tuple[float, float]]
```
Compute node positions for visualization.

**Methods:**
- `'spring'`: Force-directed spring layout
- `'circular'`: Circular arrangement
- `'random'`: Random positioning
- `'shell'`: Concentric shells
- `'spectral'`: Spectral layout
- `'kamada_kawai'`: Kamada-Kawai force-directed
- `'fruchterman_reingold'`: Fruchterman-Reingold
- `'hierarchical'`: Hierarchical layout

##### Visualization Methods

```python
def visualize_static(self, G: nx.Graph,
                    pos: Dict = None,
                    output_file: str = None,
                    backend: str = None,
                    layout: str = None,
                    figsize: Tuple[int, int] = (12, 8),
                    dpi: int = 300,
                    show_labels: bool = True,
                    node_size: Union[str, int, List] = 300,
                    node_color: Union[str, str, List] = 'lightblue',
                    edge_width: Union[float, List] = 1.0,
                    title: str = None,
                    **kwargs) -> None
```
Create static network visualization.

**Parameters:**
- `pos`: Node positions (computed if None)
- `output_file`: Output file path (display if None)
- `backend`: Rendering backend
- `layout`: Layout algorithm
- `figsize`: Figure size in inches
- `dpi`: Resolution for raster output
- `show_labels`: Show node labels
- `node_size`: Node size ('degree', int, or list)
- `node_color`: Node color ('community', color, or list)
- `edge_width`: Edge width (float or list)
- `title`: Plot title

```python
def visualize_interactive(self, G: nx.Graph,
                         output_file: str = 'network.html',
                         layout: str = None,
                         **kwargs) -> None
```
Create interactive web-based visualization.

##### Utility Methods

```python
def save_analysis(self, analysis: Dict[str, Any],
                 filepath: Union[str, Path]) -> None
```
Save analysis results to JSON file.

---

## NetworkAnalyzer

Advanced network analysis algorithms.

### Constructor

```python
NetworkAnalyzer()
```

### Centrality Methods

```python
def compute_centrality(self, G: nx.Graph,
                      method: str,
                      normalized: bool = True) -> Dict[Any, float]
```
Compute various centrality measures.

### Community Detection

```python
def detect_communities(self, G: nx.Graph,
                      method: str = 'louvain') -> Dict[Any, int]
```
Detect communities in the network.

**Methods:**
- `'louvain'`: Louvain method (requires python-louvain)
- `'girvan_newman'`: Edge betweenness
- `'label_propagation'`: Label propagation
- `'modularity'`: Modularity optimization

### Path Analysis

```python
def compute_shortest_paths(self, G: nx.Graph,
                          source: Any = None,
                          target: Any = None) -> Dict[str, Any]
```
Compute shortest paths in the network.

### Robustness Analysis

```python
def compute_network_robustness(self, G: nx.Graph,
                              attack_type: str = 'random',
                              fractions: List[float] = [0.1, 0.2, 0.3]) -> Dict[str, Any]
```
Analyze network robustness under attacks.

**Attack types:**
- `'random'`: Random node removal
- `'degree'`: Remove high-degree nodes first
- `'betweenness'`: Remove high-betweenness nodes first

---

## LayoutManager

Manages network layout algorithms.

### Constructor

```python
LayoutManager()
```

### Layout Methods

```python
def compute_layout(self, G: nx.Graph,
                  method: str,
                  **kwargs) -> Dict[Any, Tuple[float, float]]
```
Compute node layout positions.

### Specialized Layouts

```python
def spring_layout(self, G: nx.Graph, **kwargs) -> Dict
def circular_layout(self, G: nx.Graph, **kwargs) -> Dict
def spectral_layout(self, G: nx.Graph, **kwargs) -> Dict
def hierarchical_layout(self, G: nx.Graph, root=None, **kwargs) -> Dict
```

---

## Data I/O Classes

### DataLoader

Handles loading networks from various formats.

```python
from network_visualizer.io import loader

# Load network
G = loader.load('network.graphml')

# Load with specific format
G = loader.load('network.txt', format='edge_list')
```

### DataExporter

Handles saving networks to various formats.

```python
from network_visualizer.io import exporter

# Save network
exporter.export(G, 'network.json')

# Save with specific format
exporter.export(G, 'network.csv', format='csv')
```

### Format Registry

Extensible system for custom formats.

```python
from network_visualizer.io import registry

# Register custom loader
def my_loader(filepath):
    # Custom loading logic
    return G

registry.register_loader('.myformat', my_loader)
```

---

## User Interface Classes

### CLI

Command-line interface for Network Visualizer.

```python
from network_visualizer.ui import CLI

cli = CLI()
exit_code = cli.run(['analyze', '-i', 'network.graphml'])
```

### WebApp

Web-based interactive interface.

```python
from network_visualizer.ui import WebApp

app = WebApp(host='0.0.0.0', port=5000)
app.run()
```

---

## Exception Classes

### NetworkVisualizerError
Base exception for Network Visualizer errors.

### FileFormatError
Raised when file format is not supported or invalid.

### AnalysisError
Raised when network analysis fails.

### VisualizationError
Raised when visualization fails.

### LayoutError
Raised when layout computation fails.

---

## Constants and Defaults

### Default Values

```python
DEFAULT_BACKEND = 'matplotlib'
DEFAULT_LAYOUT = 'spring'
DEFAULT_FIGSIZE = (12, 8)
DEFAULT_DPI = 300
DEFAULT_NODE_SIZE = 300
DEFAULT_NODE_COLOR = 'lightblue'
DEFAULT_EDGE_WIDTH = 1.0
```

### Supported Formats

```python
SUPPORTED_FORMATS = {
    '.graphml': 'GraphML',
    '.gml': 'GML',
    '.json': 'JSON',
    '.csv': 'CSV',
    '.txt': 'Edge List',
    '.edgelist': 'Edge List',
    '.adj': 'Adjacency Matrix',
    '.mat': 'Adjacency Matrix'
}
```

### Available Metrics

```python
AVAILABLE_METRICS = [
    'degree',
    'betweenness',
    'closeness',
    'eigenvector',
    'pagerank',
    'katz',
    'clustering'
]
```

### Layout Methods

```python
LAYOUT_METHODS = [
    'spring',
    'circular',
    'random',
    'shell',
    'spectral',
    'kamada_kawai',
    'fruchterman_reingold',
    'hierarchical'
]
```

### Rendering Backends

```python
RENDERING_BACKENDS = [
    'matplotlib',
    'plotly',
    'graphviz'
]
```

---

## Type Hints

Network Visualizer uses comprehensive type hints for better IDE support:

```python
from typing import Union, Dict, List, Tuple, Any, Optional
from pathlib import Path
import networkx as nx

# Common type aliases
Node = Any
Edge = Tuple[Node, Node]
Position = Tuple[float, float]
Positions = Dict[Node, Position]
CentralityDict = Dict[Node, float]
AnalysisResult = Dict[str, Any]
Network = nx.Graph
```

---

## Plugin System

### Plugin Base Class

```python
from network_visualizer.plugins import Plugin

class CustomLayoutPlugin(Plugin):
    name = "custom_layout"
    version = "1.0.0"
    description = "Custom network layout algorithm"

    def execute(self, graph: nx.Graph, **kwargs) -> Dict[Node, Position]:
        # Custom layout implementation
        return positions
```

### Plugin Registration

```python
from network_visualizer.plugins import plugin_manager

# Register plugin
plugin_manager.register(CustomLayoutPlugin())

# Use plugin
positions = plugin_manager.execute('custom_layout', graph=G)
```

---

## Configuration

### Environment Variables

- `NETWORK_VIZ_BACKEND`: Default backend
- `NETWORK_VIZ_LAYOUT`: Default layout
- `NETWORK_VIZ_DEBUG`: Enable debug mode
- `NETWORK_VIZ_CACHE_DIR`: Cache directory

### Configuration File

Location: `~/.network_visualizer/config.json`

```json
{
  "default_backend": "plotly",
  "default_layout": "spring",
  "figure_size": [12, 8],
  "dpi": 300,
  "cache_enabled": true,
  "parallel_processing": true,
  "max_workers": 4
}
```

---

## Performance Considerations

### Memory Usage

- **Small networks** (< 1K nodes): ~10-50MB
- **Medium networks** (1K-10K nodes): ~50-200MB
- **Large networks** (10K-100K nodes): ~200MB-1GB
- **Very large networks** (> 100K nodes): 1GB+

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Layout (spring) | O(N²) | Force-directed |
| Centrality (degree) | O(N + M) | Linear |
| Centrality (betweenness) | O(N³) | Cubic, slow for large N |
| Community detection | O(N²) | Varies by method |
| Shortest paths | O(N + M) | Dijkstra/ Floyd-Warshall |

### Optimization Tips

```python
# Use approximate algorithms for large networks
centrality = viz.compute_centrality(G, 'degree')  # O(N) instead of betweenness O(N³)

# Sample large networks for visualization
if len(G.nodes) > 10000:
    sampler = NetworkSampler()
    G_sample = sampler.sample_nodes(G, 5000)

# Use efficient layouts
pos = viz.compute_layout(G, 'random')  # Fast for large networks
```

---

## Error Handling

### Best Practices

```python
from network_visualizer import NetworkVisualizer, NetworkVisualizerError

viz = NetworkVisualizer()

try:
    G = viz.load_network('network.graphml')
    analysis = viz.analyze_network(G)
    viz.visualize_static(G, output_file='result.png')

except FileNotFoundError:
    print("Network file not found")

except NetworkVisualizerError as e:
    print(f"Network Visualizer error: {e}")

except Exception as e:
    print(f"Unexpected error: {e}")
    # Log for debugging
```

### Error Types

- `FileFormatError`: Invalid or unsupported file format
- `AnalysisError`: Network analysis failed
- `VisualizationError`: Rendering failed
- `LayoutError`: Layout computation failed
- `PluginError`: Plugin execution failed

---

*For more examples and usage patterns, see the [tutorial](tutorial.md) and [examples](../examples/) directory.*
