# 📊 Network Analysis Guide

## Overview

Network Visualizer provides comprehensive network analysis capabilities, implementing state-of-the-art algorithms for centrality measures, community detection, robustness analysis, and structural metrics.

---

## 🔬 Centrality Measures

Centrality measures identify the most important nodes in a network.

### Degree Centrality

**Formula:** `C_D(v) = deg(v) / (n-1)`

Degree centrality measures how connected a node is. Nodes with high degree centrality are hubs that connect many other nodes.

```python
from network_visualizer import NetworkVisualizer

viz = NetworkVisualizer()
G = viz.load_sample_graph('karate_club')

# Compute degree centrality
degree_cent = viz.compute_centrality(G, 'degree')

# Most central node
most_central = max(degree_cent.items(), key=lambda x: x[1])
print(f"Most central node: {most_central[0]} (centrality: {most_central[1]:.3f})")
```

### Betweenness Centrality

**Formula:** `C_B(v) = Σ_{s≠v≠t} σ_{st}(v) / σ_{st}`

Betweenness centrality measures how often a node lies on shortest paths between other nodes. High betweenness nodes are bridges or brokers.

```python
# Compute betweenness centrality (more expensive)
betweenness_cent = viz.compute_centrality(G, 'betweenness')

# Bridge nodes
bridges = [(node, cent) for node, cent in betweenness_cent.items() if cent > 0.1]
print(f"Bridge nodes: {bridges}")
```

### Closeness Centrality

**Formula:** `C_C(v) = 1 / Σ_{u≠v} d(v,u)`

Closeness centrality measures how close a node is to all other nodes. High closeness nodes can quickly reach others.

```python
closeness_cent = viz.compute_centrality(G, 'closeness')

# Most reachable nodes
reachable = sorted(closeness_cent.items(), key=lambda x: x[1], reverse=True)[:3]
print("Top 3 most reachable nodes:")
for node, cent in reachable:
    print(f"  Node {node}: {cent:.3f}")
```

### Eigenvector Centrality

**Formula:** `C_E(v) = λ⁻¹ Σ_{u∈N(v)} C_E(u)`

Eigenvector centrality measures influence through connections to influential nodes. It's the eigenvector of the adjacency matrix.

```python
eigen_cent = viz.compute_centrality(G, 'eigenvector')

# Influential nodes
influential = [(node, cent) for node, cent in eigen_cent.items() if cent > 0.15]
print(f"Influential nodes: {influential}")
```

### PageRank Centrality

**Formula:** `PR(v) = (1-d)/N + d Σ_{u∈N(v)} PR(u)/deg(u)`

PageRank measures importance through recursive relationships, similar to Google's PageRank algorithm.

```python
pagerank_cent = viz.compute_centrality(G, 'pagerank')

# Important nodes
important = sorted(pagerank_cent.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top 5 important nodes by PageRank:")
for node, pr in important:
    print(f"  Node {node}: {pr:.3f}")
```

### Katz Centrality

**Formula:** `C_K(v) = Σ_{k=1}^∞ α^k |paths_{v←k}|`

Katz centrality measures influence through all paths, decaying with path length.

```python
katz_cent = viz.compute_centrality(G, 'katz')

# Nodes with broad influence
broad_influence = [(node, cent) for node, cent in katz_cent.items() if cent > 0.2]
print(f"Nodes with broad influence: {broad_influence}")
```

---

## 👥 Community Detection

Community detection finds groups of densely connected nodes.

### Louvain Method

The Louvain method maximizes modularity through hierarchical optimization.

```python
from network_visualizer.core.algorithms import NetworkAnalyzer

analyzer = NetworkAnalyzer()

# Detect communities
communities = analyzer.detect_communities(G, 'louvain')

# Count community sizes
from collections import Counter
sizes = Counter(communities.values())
print(f"Found {len(sizes)} communities:")
for comm_id, size in sizes.items():
    print(f"  Community {comm_id}: {size} nodes")

# Modularity score
modularity = analyzer.compute_modularity(G, communities)
print(f"Modularity: {modularity:.3f}")
```

### Girvan-Newman Algorithm

Girvan-Newman removes edges with high betweenness to find communities.

```python
# Hierarchical community detection
communities_gn = analyzer.detect_communities(G, 'girvan_newman')

# Get community hierarchy
hierarchy = analyzer.girvan_newman_hierarchy(G)
print(f"Community hierarchy levels: {len(hierarchy)}")
```

### Label Propagation

Label propagation assigns communities through local voting.

```python
# Fast community detection
communities_lp = analyzer.detect_communities(G, 'label_propagation')

# Community stability
stability = analyzer.compute_community_stability(G, communities_lp)
print(f"Community stability: {stability:.3f}")
```

---

## 📈 Structural Metrics

### Basic Network Statistics

```python
stats = viz.compute_statistics(G)

print("Network Statistics:")
print(f"  Nodes: {stats['num_nodes']}")
print(f"  Edges: {stats['num_edges']}")
print(f"  Density: {stats['density']:.3f}")
print(f"  Average Degree: {stats['average_degree']:.2f}")

if 'diameter' in stats:
    print(f"  Diameter: {stats['diameter']}")
if 'average_path_length' in stats:
    print(f"  Average Path Length: {stats['average_path_length']:.2f}")
```

### Clustering Coefficients

Clustering measures local density around nodes.

```python
# Global clustering coefficient
global_clustering = analyzer.compute_clustering_coefficient(G)

# Local clustering coefficients
local_clustering = nx.clustering(G)

# Average clustering
avg_clustering = sum(local_clustering.values()) / len(local_clustering)
print(f"Global clustering: {global_clustering:.3f}")
print(f"Average local clustering: {avg_clustering:.3f}")

# Highly clustered nodes
clustered_nodes = [(n, c) for n, c in local_clustering.items() if c > 0.6]
print(f"Highly clustered nodes: {clustered_nodes}")
```

### Connected Components

```python
# Find connected components
components = list(nx.connected_components(G))
print(f"Number of components: {len(components)}")

# Largest component
largest = max(components, key=len)
print(f"Largest component size: {len(largest)}")

# Component analysis
component_sizes = [len(comp) for comp in components]
print(f"Component sizes: {sorted(component_sizes, reverse=True)}")

# Giant component ratio
giant_ratio = len(largest) / len(G.nodes)
print(f"Giant component ratio: {giant_ratio:.3f}")
```

---

## 🔄 Path Analysis

### Shortest Paths

```python
# Shortest paths from a source node
paths = analyzer.compute_shortest_paths(G, source=0)

print(f"Shortest paths from node 0:")
print(f"  Average distance: {paths['average_distance']:.2f}")
print(f"  Maximum distance: {paths['max_distance']}")

# Path to specific target
path_info = analyzer.compute_shortest_paths(G, source=0, target=10)
print(f"Path from 0 to 10: {path_info['path']} (length: {path_info['length']})")

# All pairs shortest paths (expensive for large networks)
if len(G.nodes) < 100:
    all_paths = dict(nx.all_pairs_shortest_path_length(G))
    print(f"Average shortest path length: {nx.average_shortest_path_length(G):.2f}")
```

### Network Efficiency

```python
# Global efficiency
global_efficiency = analyzer.compute_global_efficiency(G)
print(f"Global efficiency: {global_efficiency:.3f}")

# Local efficiency
local_efficiency = analyzer.compute_local_efficiency(G)
avg_local_eff = sum(local_efficiency.values()) / len(local_efficiency)
print(f"Average local efficiency: {avg_local_eff:.3f}")
```

---

## 🛡️ Robustness Analysis

### Attack Tolerance

```python
# Random attack
robustness_random = analyzer.compute_network_robustness(G, 'random', [0.1, 0.2, 0.3])

print("Random attack robustness:")
for frac, remaining in zip([0.1, 0.2, 0.3], robustness_random['largest_component_sizes']):
    ratio = remaining / len(G.nodes)
    print(f"  Remove {frac*100:.0f}%: {ratio:.3f} remaining")

# Targeted attack (high degree nodes first)
robustness_degree = analyzer.compute_network_robustness(G, 'degree', [0.1, 0.2, 0.3])

print("\\nTargeted attack robustness:")
for frac, remaining in zip([0.1, 0.2, 0.3], robustness_degree['largest_component_sizes']):
    ratio = remaining / len(G.nodes)
    print(f"  Remove {frac*100:.0f}%: {ratio:.3f} remaining")
```

### Percolation Theory

```python
# Percolation threshold
threshold = analyzer.compute_percolation_threshold(G)
print(f"Percolation threshold: {threshold:.3f}")

# Critical fraction for fragmentation
critical_fraction = analyzer.compute_critical_fraction(G)
print(f"Critical fraction: {critical_fraction:.3f}")
```

---

## 📊 Advanced Analysis

### Assortativity

```python
# Degree assortativity
assortativity = nx.degree_assortativity_coefficient(G)
print(f"Degree assortativity: {assortativity:.3f}")

# Interpret result
if assortativity > 0:
    print("Network is assortative (similar degrees connect)")
elif assortativity < 0:
    print("Network is disassortative (dissimilar degrees connect)")
else:
    print("Network is neutral")
```

### Rich Club Coefficient

```python
# Rich club analysis
rich_club = analyzer.compute_rich_club_coefficient(G)

# Plot rich club curve
degrees = sorted(set(dict(G.degree()).values()))
rich_club_values = [rich_club.get(d, 0) for d in degrees]

plt.plot(degrees, rich_club_values)
plt.xlabel('Degree')
plt.ylabel('Rich Club Coefficient')
plt.title('Rich Club Analysis')
plt.show()
```

### Small World Properties

```python
# Small world analysis
small_world = analyzer.compute_small_world_properties(G)

print("Small world properties:")
print(f"  Clustering coefficient: {small_world['clustering']:.3f}")
print(f"  Average path length: {small_world['path_length']:.3f}")
print(f"  Small world coefficient: {small_world['small_world_coeff']:.3f}")
```

---

## 🔍 Comparative Analysis

### Multi-Network Comparison

```python
networks = [
    ('karate_club', viz.load_sample_graph('karate_club')),
    ('florentine_families', viz.load_sample_graph('florentine_families')),
    ('davis_southern_women', viz.load_sample_graph('davis_southern_women'))
]

comparison = {}

for name, G in networks:
    stats = viz.compute_statistics(G)
    degree_cent = viz.compute_centrality(G, 'degree')
    betweenness_cent = viz.compute_centrality(G, 'betweenness')

    comparison[name] = {
        'nodes': stats['num_nodes'],
        'density': stats['density'],
        'avg_degree_cent': sum(degree_cent.values()) / len(degree_cent),
        'avg_betweenness_cent': sum(betweenness_cent.values()) / len(betweenness_cent)
    }

# Print comparison table
print("Network Comparison:")
print("Name                  | Nodes | Density | Avg Degree Cent | Avg Betweenness")
print("-" * 75)
for name, data in comparison.items():
    print("22")
```

### Temporal Analysis

```python
# For temporal networks (if available)
temporal_metrics = analyzer.compute_temporal_metrics(temporal_graph)

print("Temporal network analysis:")
print(f"  Activity bursts: {len(temporal_metrics['bursts'])}")
print(f"  Temporal efficiency: {temporal_metrics['efficiency']:.3f}")
print(f"  Memory coefficient: {temporal_metrics['memory']:.3f}")
```

---

## 🎯 Custom Analysis

### Creating Custom Metrics

```python
def custom_centrality(G, alpha=0.85):
    """Custom centrality measure combining degree and clustering."""
    degree_cent = viz.compute_centrality(G, 'degree')
    clustering = nx.clustering(G)

    custom_cent = {}
    for node in G.nodes():
        # Combine degree and clustering
        custom_cent[node] = alpha * degree_cent[node] + (1-alpha) * clustering[node]

    return custom_cent

# Use custom metric
custom_cent = custom_centrality(G)
top_custom = sorted(custom_cent.items(), key=lambda x: x[1], reverse=True)[:5]
print("Top nodes by custom centrality:")
for node, cent in top_custom:
    print(f"  Node {node}: {cent:.3f}")
```

### Plugin-Based Analysis

```python
from network_visualizer.plugins import Plugin

class CustomAnalysisPlugin(Plugin):
    name = "custom_analysis"
    description = "Custom network analysis plugin"

    def execute(self, graph, **kwargs):
        # Custom analysis logic
        result = {
            'custom_metric': self.compute_custom_metric(graph),
            'special_nodes': self.find_special_nodes(graph)
        }
        return result

    def compute_custom_metric(self, G):
        # Implementation
        return sum(dict(G.degree()).values()) / len(G.nodes)

    def find_special_nodes(self, G):
        # Implementation
        return [n for n in G.nodes() if G.degree(n) > 5]

# Register and use plugin
plugin_manager.register(CustomAnalysisPlugin())
result = plugin_manager.execute('custom_analysis', graph=G)
```

---

## 📈 Performance Optimization

### Scaling Analysis

```python
import time

def benchmark_analysis(G, methods):
    """Benchmark different analysis methods."""
    results = {}

    for method in methods:
        start_time = time.time()
        if method == 'statistics':
            result = viz.compute_statistics(G)
        elif method in ['degree', 'betweenness', 'closeness']:
            result = viz.compute_centrality(G, method)
        elif method == 'communities':
            result = analyzer.detect_communities(G)
        else:
            continue

        elapsed = time.time() - start_time
        results[method] = elapsed
        print(f"{method}: {elapsed:.3f}s")

    return results

# Benchmark on different network sizes
sizes = [100, 500, 1000]
methods = ['statistics', 'degree', 'betweenness', 'communities']

for n in sizes:
    print(f"\\nBenchmarking {n} nodes:")
    G_test = nx.erdos_renyi_graph(n, 0.1)
    benchmark_analysis(G_test, methods)
```

### Memory-Efficient Analysis

```python
# For very large networks
def analyze_large_network(G):
    """Memory-efficient analysis for large networks."""

    # Sample for expensive computations
    if len(G.nodes) > 10000:
        sample_size = min(5000, len(G.nodes) // 2)
        sampler = NetworkSampler()
        G_sample = sampler.sample_nodes(G, sample_size)
    else:
        G_sample = G

    # Fast computations on sample
    stats = viz.compute_statistics(G_sample)
    degree_cent = viz.compute_centrality(G_sample, 'degree')

    # Expensive computations on full network (if feasible)
    if len(G.nodes) < 5000:
        betweenness_cent = viz.compute_centrality(G, 'betweenness')
        communities = analyzer.detect_communities(G)
    else:
        betweenness_cent = None
        communities = None

    return {
        'statistics': stats,
        'degree_centrality': degree_cent,
        'betweenness_centrality': betweenness_cent,
        'communities': communities,
        'sampled': len(G.nodes) > 10000
    }

# Analyze large network efficiently
result = analyze_large_network(large_graph)
```

---

## 📚 Further Reading

### Key Papers

1. **Centrality Measures**
   - Freeman, L.C. (1978). Centrality in social networks
   - Brandes, U. (2001). A faster algorithm for betweenness centrality

2. **Community Detection**
   - Blondel et al. (2008). Fast unfolding of communities in large networks
   - Girvan & Newman (2002). Community structure in social and biological networks

3. **Network Robustness**
   - Albert et al. (2000). Error and attack tolerance of complex networks
   - Cohen et al. (2001). Breakdown of the internet under intentional attack

### Recommended Books

- **"Networks: An Introduction"** by Mark Newman
- **"Complex Networks: Structure and Dynamics"** by Santo Fortunato
- **"Network Science"** by Albert-László Barabási

### Online Resources

- **NetworkX Documentation**: https://networkx.org/documentation/
- **Stanford Network Analysis Platform**: https://snap.stanford.edu/
- **igraph Library**: https://igraph.org/

---

*For practical examples, see the [examples](../examples/) directory and [tutorial](tutorial.md).* 📊✨
