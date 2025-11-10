#!/usr/bin/env python
"""
Network Visualizer Command Line Interface

Main entry point for the network-visualizer command-line tool.
"""

import sys
import argparse
from pathlib import Path

from .core import NetworkVisualizer
from .io.savers import save_json_report, save_html_report


def create_parser():
    """Create command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Network Visualizer - Advanced network analysis and visualization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  network-visualizer --interactive
  network-visualizer analyze --input network.graphml --output analysis.json
  network-visualizer visualize --input network.json --layout spring --output network.png
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Interactive mode
    subparsers.add_parser('interactive', help='Launch interactive visualization')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze network file')
    analyze_parser.add_argument('--input', '-i', required=True,
                               help='Input network file')
    analyze_parser.add_argument('--output', '-o',
                               help='Output analysis file (JSON or HTML)')
    analyze_parser.add_argument('--format', choices=['json', 'html'], default='json',
                               help='Output format for the analysis report')
    analyze_parser.add_argument('--metrics', nargs='+',
                               default=['degree', 'betweenness', 'closeness'],
                               help='Metrics to compute')

    # Visualize command
    visualize_parser = subparsers.add_parser('visualize', help='Generate visualization')
    visualize_parser.add_argument('--input', '-i', required=True,
                                 help='Input network file')
    visualize_parser.add_argument('--output', '-o',
                                 help='Output visualization file')
    visualize_parser.add_argument('--layout', '-l',
                                 choices=['spring', 'circular', 'random', 'shell', 'spectral'],
                                 default='spring', help='Layout algorithm')
    visualize_parser.add_argument('--backend', '-b',
                                 choices=['matplotlib', 'plotly', 'graphviz'],
                                 default='matplotlib', help='Visualization backend')
    visualize_parser.add_argument('--show-labels', action='store_true',
                                 help='Show node labels')

    # Sample command
    sample_parser = subparsers.add_parser('sample', help='Generate sample network')
    sample_parser.add_argument('--type', '-t',
                              choices=['karate', 'erdos_renyi', 'barabasi_albert', 'watts_strogatz'],
                              default='karate', help='Sample network type')
    sample_parser.add_argument('--output', '-o',
                              help='Output file for sample network')

    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        visualizer = NetworkVisualizer()

        if args.command == 'interactive':
            return run_interactive(visualizer)

        elif args.command == 'analyze':
            return run_analyze(visualizer, args)

        elif args.command == 'visualize':
            return run_visualize(visualizer, args)

        elif args.command == 'sample':
            return run_sample(visualizer, args)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0


def run_interactive(visualizer):
    """Run interactive visualization mode."""
    print("🚀 Launching Network Visualizer Interactive Mode")
    print("📊 Loading sample network...")

    # Load sample network
    G = visualizer.load_sample_graph('karate_club')

    print(f"📈 Network loaded: {len(G.nodes)} nodes, {len(G.edges)} edges")
    print("🎨 Computing layout...")

    # Compute layout
    pos = visualizer.compute_layout(G, method='spring')

    print("🎯 Computing centrality metrics...")
    centrality = visualizer.compute_centrality(G, method='betweenness')

    print("📊 Launching interactive visualization...")
    visualizer.visualize_interactive(G, pos, centrality)

    print("✅ Interactive visualization complete!")
    return 0


def run_analyze(visualizer, args):
    """Run network analysis."""
    print(f"📊 Analyzing network: {args.input}")

    # Load network
    G = visualizer.load_network(args.input)

    # Compute metrics
    analysis = {}
    for metric in args.metrics:
        print(f"🔢 Computing {metric} centrality...")
        analysis[metric] = visualizer.compute_centrality(G, method=metric)

    # Add network statistics
    analysis['statistics'] = visualizer.compute_statistics(G)

    # Save results
    if args.output:
        if args.format == 'html':
            save_html_report(analysis, args.output)
            print(f"💾 HTML report saved to: {args.output}")
        else:  # Default to json
            save_json_report(analysis, args.output)
            print(f"💾 JSON analysis saved to: {args.output}")
    else:
        # Print summary
        stats = analysis['statistics']
        print("📈 Network Statistics:"        print(f"  Nodes: {stats['num_nodes']}")
        print(f"  Edges: {stats['num_edges']}")
        print(f"  Density: {stats['density']:.3f}")
        print(".3f"        print(".3f"
    return 0


def run_visualize(visualizer, args):
    """Run network visualization."""
    print(f"🎨 Visualizing network: {args.input}")

    # Load network
    G = visualizer.load_network(args.input)

    # Compute layout
    print(f"📐 Computing {args.layout} layout...")
    pos = visualizer.compute_layout(G, method=args.layout)

    # Set default output if not specified
    if not args.output:
        input_path = Path(args.input)
        args.output = str(input_path.with_suffix('.png'))

    # Generate visualization
    print(f"🎨 Generating visualization with {args.backend} backend...")
    visualizer.visualize_static(
        G, pos,
        output_file=args.output,
        backend=args.backend,
        show_labels=args.show_labels
    )

    print(f"💾 Visualization saved to: {args.output}")
    return 0


def run_sample(visualizer, args):
    """Generate and save sample network."""
    print(f"🎲 Generating {args.type} sample network...")

    # Generate sample
    G = visualizer.generate_sample(args.type)

    # Save to file
    if args.output:
        visualizer.save_network(G, args.output)
        print(f"💾 Sample network saved to: {args.output}")
    else:
        # Print basic info
        print("📊 Sample Network Generated:"        print(f"  Nodes: {len(G.nodes)}")
        print(f"  Edges: {len(G.edges)}")
        print(".3f"
    return 0


if __name__ == '__main__':
    sys.exit(main())
