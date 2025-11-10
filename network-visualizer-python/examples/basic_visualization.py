#!/usr/bin/env python
"""
Basic Network Visualization Example

This example demonstrates the core functionality of the Network Visualizer,
including loading networks, computing analysis, and generating visualizations.
"""

import networkx as nx
from network_visualizer import NetworkVisualizer


def main():
    """Run the basic visualization example."""
    print("🌐 Network Visualizer - Basic Example")
    print("=" * 50)

    # Initialize the visualizer
    visualizer = NetworkVisualizer()

    # 1. Load a sample network
    print("\n📊 Loading sample network...")
    G = visualizer.load_sample_graph('karate_club')
    print(f"✅ Loaded Karate Club network: {len(G.nodes)} nodes, {len(G.edges)} edges")

    # 2. Compute basic statistics
    print("\n📈 Computing network statistics...")
    stats = visualizer.compute_statistics(G)
    print("Network Statistics:"    print(f"  • Nodes: {stats['num_nodes']}")
    print(f"  • Edges: {stats['num_edges']}")
    print(f"  • Density: {stats['density']:.4f}")
    print(f"  • Average Degree: {stats['average_degree']:.2f}")

    if stats.get('diameter'):
        print(f"  • Diameter: {stats['diameter']}")
    if stats.get('average_path_length'):
        print(".2f"
    # 3. Compute centrality measures
    print("\n🎯 Computing centrality measures...")
    degree_centrality = visualizer.compute_centrality(G, 'degree')
    betweenness_centrality = visualizer.compute_centrality(G, 'betweenness')

    # Find most central nodes
    top_degree = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:5]
    top_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:5]

    print("Top 5 nodes by degree centrality:"    for node, centrality in top_degree:
        print(".3f"
    print("\nTop 5 nodes by betweenness centrality:"    for node, centrality in top_betweenness:
        print(".3f"
    # 4. Compute network layout
    print("\n📐 Computing network layout...")
    pos = visualizer.compute_layout(G, method='spring')
    print("✅ Layout computed for all nodes")

    # 5. Generate visualization
    print("\n🎨 Generating network visualization...")
    output_file = "karate_club_visualization.png"
    visualizer.visualize_static(
        G,
        pos=pos,
        output_file=output_file,
        backend='matplotlib',
        show_labels=True
    )
    print(f"✅ Visualization saved as: {output_file}")

    # 6. Perform comprehensive analysis
    print("\n🔬 Performing comprehensive network analysis...")
    analysis = visualizer.analyze_network(G, metrics=['degree', 'betweenness', 'closeness'])

    print("Analysis Results:"    print(f"  • Centrality metrics computed: {len(analysis['centrality'])}")
    print(f"  • Communities detected: {len(set(analysis['communities'].values()))}")
    print(f"  • Shortest paths computed: {len(analysis['paths'])} samples")

    # 7. Export analysis results
    print("\n💾 Exporting analysis results...")
    analysis_file = "karate_club_analysis.json"
    visualizer.save_analysis(analysis, analysis_file)
    print(f"✅ Analysis results saved as: {analysis_file}")

    # 8. Demonstrate different layouts
    print("\n🔄 Demonstrating different layout algorithms...")

    layouts = ['circular', 'random', 'shell']
    for layout_name in layouts:
        print(f"  Computing {layout_name} layout...")
        layout_pos = visualizer.compute_layout(G, method=layout_name)

        layout_file = f"karate_club_{layout_name}.png"
        visualizer.visualize_static(
            G,
            pos=layout_pos,
            output_file=layout_file,
            backend='matplotlib',
            show_labels=False  # Less cluttered without labels
        )
        print(f"    ✅ Saved as: {layout_file}")

    print("\n🎉 Example completed successfully!")
    print("\nGenerated files:")
    print("  • karate_club_visualization.png (spring layout)")
    print("  • karate_club_circular.png (circular layout)")
    print("  • karate_club_random.png (random layout)")
    print("  • karate_club_shell.png (shell layout)")
    print("  • karate_club_analysis.json (analysis results)")

    print("\n💡 Tips:")
    print("  • Try different centrality metrics: 'eigenvector', 'pagerank', 'katz'")
    print("  • Experiment with layout algorithms: 'spectral', 'kamada_kawai'")
    print("  • Use the web interface: network-visualizer --web")
    print("  • Load your own networks in various formats")


if __name__ == '__main__':
    main()
