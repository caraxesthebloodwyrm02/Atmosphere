# 📚 Basic Tutorial

## 🎯 Welcome to Network Visualizer!

This tutorial will guide you through the core features of Network Visualizer, from basic usage to advanced analysis. By the end, you'll be able to load networks, compute metrics, and create stunning visualizations.

---

## 🚀 Quick Start (5 minutes)

### 1. Import and Initialize

```python
from network_visualizer import NetworkVisualizer

# Create visualizer instance
viz = NetworkVisualizer()
```

### 2. Load a Sample Network

```python
# Load the famous Zachary's Karate Club network
G = viz.load_sample_graph('karate_club')
print(f"Network loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")
```

**Output:**
```
Network loaded: 34 nodes, 78 edges
```

### 3. Analyze the Network

```python
# Compute basic statistics
stats = viz.compute_statistics(G)
print(f"Density: {stats['density']:.3f}")
print(f"Average degree: {stats['average_degree']:.2f}")
```

### 4. Visualize the Network

```python
# Generate a beautiful visualization
viz.visualize_static(G, output_file='karate_club.png')
print("Visualization saved as karate_club.png")
```

**Result**: A publication-quality network visualization saved to your directory!

---

## 📊 Network Analysis Deep Dive

### Understanding Network Structure

Networks consist of **nodes** (entities) connected by **edges** (relationships). Let's explore the Karate Club network:

```python
# Get basic network information
print(f"Number of nodes: {len(G.nodes)}")
print(f"Number of edges: {len(G.edges)}")

# Check if network is directed
print(f"Directed: {G.is_directed()}")

# Get node degrees (connections)
degrees = dict(G.degree())
print(f"Most connected node: {max(degrees, key=degrees.get)} (degree: {max(degrees.values())})")
```

### Centrality Measures

Centrality tells us which nodes are most important:

```python
# Degree centrality - how connected is each node?
degree_cent = viz.compute_centrality(G, 'degree')
top_degree = sorted(degree_cent.items(), key=lambda x: x[1], reverse=True)[:3]

print("Top 3 nodes by degree centrality:")
for node, centrality in top_degree:
    print(f"  Node {node}: {centrality:.3f}")

# Betweenness centrality - how important for information flow?
betweenness_cent = viz.compute_centrality(G, 'betweenness')
top_betweenness = sorted(betweenness_cent.items(), key=lambda x: x[1], reverse=True)[:3]

print("\\nTop 3 nodes by betweenness centrality:")
for node, centrality in top_betweenness:
    print(f"  Node {node}: {centrality:.3f}")
```

### Community Detection

Discover natural groupings in the network:

```python
# Detect communities using Louvain method
communities = viz.analyzer.detect_communities(G, 'louvain')

# Count community sizes
from collections import Counter
community_sizes = Counter(communities.values())
print(f"Found {len(community_sizes)} communities:")
for comm_id, size in community_sizes.items():
    print(f"  Community {comm_id}: {size} members")
```

---

## 🎨 Advanced Visualization

### Different Layout Algorithms

```python
layouts = ['spring', 'circular', 'random', 'shell']

for layout in layouts:
    filename = f'karate_club_{layout}.png'
    viz.visualize_static(G,
                        layout=layout,
                        output_file=filename,
                        show_labels=False)  # Less cluttered
    print(f"Created {layout} layout: {filename}")
```

### Customizing Visualizations

```python
# Advanced visualization with customization
viz.visualize_static(G,
                    layout='spring',
                    output_file='custom_viz.png',
                    figsize=(12, 8),           # Figure size
                    node_size='degree',       # Size nodes by degree
                    node_color='community',   # Color by community
                    edge_width=0.5,           # Thinner edges
                    show_labels=True,         # Show node labels
                    title='Karate Club Network Analysis')
```

### Interactive Web Visualization

```python
# Launch interactive web interface
from network_visualizer.ui import WebApp

app = WebApp()
app.run(host='localhost', port=5000, debug=True)
```

Then open http://localhost:5000 in your browser!

---

## 💾 Working with Your Own Data

### Loading Different Formats

```python
# CSV format (node1,node2,weight)
G_csv = viz.load_network('my_network.csv')

# GraphML format (standard network format)
G_graphml = viz.load_network('my_network.graphml')

# JSON format (custom node-link format)
G_json = viz.load_network('my_network.json')

# Edge list format
G_edgelist = viz.load_network('my_network.txt')
```

### CSV Format Example

Create a file `my_network.csv`:
```csv
source,target,weight
Alice,Bob,0.8
Alice,Charlie,0.6
Bob,Charlie,0.9
Bob,David,0.7
Charlie,David,0.5
```

```python
# Load and analyze
G = viz.load_network('my_network.csv')
viz.visualize_static(G, output_file='my_network.png')
```

### Converting Between Formats

```python
# Load CSV and save as GraphML
G = viz.load_network('network.csv')
viz.save_network(G, 'network.graphml')

# Load GraphML and save as JSON
G = viz.load_network('network.graphml')
viz.save_network(G, 'network.json')
```

---

## 🔬 Advanced Analysis

### Comprehensive Network Analysis

```python
# Perform complete analysis
analysis = viz.analyze_network(G, metrics=[
    'degree', 'betweenness', 'closeness',
    'eigenvector', 'pagerank', 'katz'
])

# Save analysis results
viz.save_analysis(analysis, 'network_analysis.json')

# Key insights
stats = analysis['statistics']
print(f"Network density: {stats['density']:.3f}")
print(f"Average clustering: {stats['average_clustering']:.3f}")

centrality = analysis['centrality']
print(f"Most central node by betweenness: {max(centrality['betweenness'], key=centrality['betweenness'].get)}")
```

### Robustness Analysis

```python
# Test network resilience
robustness = viz.analyzer.compute_network_robustness(G, 'random', [0.1, 0.2, 0.3])

print("Network robustness under random node removal:")
for fraction, remaining in zip([0.1, 0.2, 0.3], robustness['largest_component_sizes']):
    print(f"  Remove {fraction*100:.0f}%: {remaining:.3f} of network remains")
```

### Shortest Path Analysis

```python
# Find shortest paths
paths = viz.analyzer.compute_shortest_paths(G, source=0)

print(f"Shortest paths from node 0:")
print(f"  Average distance: {paths['average_distance']:.2f}")
print(f"  Maximum distance: {paths['max_distance']}")

# Path between specific nodes
path_info = viz.analyzer.compute_shortest_paths(G, source=0, target=10)
print(f"Path from 0 to 10: {path_info['path']} (length: {path_info['length']})")
```

---

## ⚡ Command Line Interface

Network Visualizer also provides powerful command-line tools:

```bash
# Analyze a network
network-visualizer analyze --input my_network.graphml --metrics degree betweenness

# Create visualization
network-visualizer visualize --input my_network.json --layout spring --output viz.png

# Convert formats
network-visualizer convert --input network.csv --output network.graphml

# Show statistics
network-visualizer stats --input my_network.gml

# Batch processing
network-visualizer batch --config batch_jobs.json
```

---

## 🧪 Testing and Validation

### Running the Test Suite

```python
# Import test utilities
from network_visualizer.tests.test_core import TestNetworkVisualizer
import unittest

# Run specific tests
suite = unittest.TestLoader().loadTestsFromTestCase(TestNetworkVisualizer)
runner = unittest.TextTestRunner(verbosity=2)
runner.run(suite)
```

### Performance Benchmarking

```python
import time

# Benchmark analysis performance
start_time = time.time()
analysis = viz.analyze_network(G)
analysis_time = time.time() - start_time

print(f"Analysis completed in {analysis_time:.2f} seconds")

# Benchmark visualization
start_time = time.time()
viz.visualize_static(G, output_file='benchmark.png')
viz_time = time.time() - start_time

print(f"Visualization completed in {viz_time:.2f} seconds")
```

---

## 🎯 Best Practices

### Memory Management for Large Networks

```python
# For networks with >10,000 nodes
if len(G.nodes) > 10000:
    # Use sampling for visualization
    from network_visualizer.core.algorithms import NetworkSampler
    sampler = NetworkSampler()
    G_sampled = sampler.sample_nodes(G, sample_size=5000)
    viz.visualize_static(G_sampled, output_file='large_network_sample.png')
```

### Choosing the Right Layout

```python
# Layout selection guide
def choose_layout(G):
    n = len(G.nodes)

    if n < 50:
        return 'spring'  # Force-directed works well for small networks
    elif n < 500:
        return 'circular'  # Good for medium networks
    else:
        return 'random'  # Fast for large networks, may need post-processing

layout = choose_layout(G)
viz.visualize_static(G, layout=layout, output_file='optimized_layout.png')
```

### Error Handling

```python
try:
    G = viz.load_network('potentially_missing_file.graphml')
    analysis = viz.analyze_network(G)
    viz.visualize_static(G, output_file='result.png')
    print("✅ Analysis completed successfully!")

except FileNotFoundError:
    print("❌ File not found. Please check the file path.")

except Exception as e:
    print(f"❌ Error during analysis: {e}")
    # Log error for debugging
    import logging
    logging.error(f"Analysis failed: {e}", exc_info=True)
```

---

## 🔗 Integration Examples

### With Pandas

```python
import pandas as pd

# Convert network to DataFrame
edges_df = pd.DataFrame(G.edges(), columns=['source', 'target'])

# Add centrality measures
degree_cent = viz.compute_centrality(G, 'degree')
betweenness_cent = viz.compute_centrality(G, 'betweenness')

nodes_df = pd.DataFrame({
    'node': list(G.nodes()),
    'degree_centrality': [degree_cent.get(n, 0) for n in G.nodes()],
    'betweenness_centrality': [betweenness_cent.get(n, 0) for n in G.nodes()]
})

# Save to CSV
nodes_df.to_csv('network_metrics.csv', index=False)
```

### With Jupyter Notebooks

```python
# For interactive analysis in Jupyter
import matplotlib.pyplot as plt

# Create subplots for comparison
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

layouts = ['spring', 'circular', 'random']
for i, layout in enumerate(layouts):
    pos = viz.compute_layout(G, layout)
    viz.visualize_static(G, pos=pos, ax=axes[i], show_plot=False)
    axes[i].set_title(f'{layout.title()} Layout')

plt.tight_layout()
plt.savefig('layout_comparison.png', dpi=300, bbox_inches='tight')
```

---

## 🎉 Congratulations!

You've completed the Network Visualizer tutorial! You now know how to:

- ✅ Load and explore networks
- ✅ Compute centrality measures and statistics
- ✅ Detect communities and analyze structure
- ✅ Create beautiful visualizations
- ✅ Work with different data formats
- ✅ Use command-line tools
- ✅ Handle large networks efficiently
- ✅ Integrate with other Python tools

### Next Steps

- **📖 Read the API Reference**: [api.md](api.md) for detailed function documentation
- **🔧 Explore Plugins**: [plugins.md](plugins.md) for extending functionality
- **🎯 Try Use Cases**: [social_networks.md](social_networks.md) for domain-specific examples
- **🚀 Advanced Features**: [performance.md](performance.md) for optimization techniques

Happy network analyzing! 🌐✨

### 📞 Need Help?

- **Documentation**: [Full Documentation Index](index.md)
- **Examples**: [examples/](../examples/) directory
- **Issues**: [GitHub Issues](https://github.com/your-org/network-visualizer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/network-visualizer/discussions)
