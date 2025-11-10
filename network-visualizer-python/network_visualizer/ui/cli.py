"""
Command Line Interface for Network Visualizer

Provides CLI commands for network analysis, visualization, and data processing.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any, Optional

from ..core import NetworkVisualizer


class CLI:
    """
    Command Line Interface for network visualization and analysis.

    Provides comprehensive CLI tools for network processing, analysis,
    and visualization with support for batch operations and automation.
    """

    def __init__(self):
        """Initialize the CLI."""
        self.visualizer = NetworkVisualizer()
        self.commands = {
            'analyze': self.analyze_command,
            'visualize': self.visualize_command,
            'convert': self.convert_command,
            'stats': self.stats_command,
            'compare': self.compare_command,
            'batch': self.batch_command,
        }

    def run(self, args: Optional[list] = None) -> int:
        """
        Run CLI with command line arguments.

        Args:
            args: Command line arguments (uses sys.argv if None)

        Returns:
            Exit code (0 for success, non-zero for error)
        """
        if args is None:
            args = sys.argv[1:]

        parser = self._create_parser()
        parsed_args = parser.parse_args(args)

        if not hasattr(parsed_args, 'command') or parsed_args.command is None:
            parser.print_help()
            return 1

        try:
            command_func = self.commands.get(parsed_args.command)
            if command_func:
                return command_func(parsed_args)
            else:
                print(f"Unknown command: {parsed_args.command}", file=sys.stderr)
                return 1
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            if parsed_args.debug:
                import traceback
                traceback.print_exc()
            return 1

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            description="Network Visualizer - Advanced network analysis and visualization",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  network-visualizer analyze --input network.graphml --metrics degree betweenness
  network-visualizer visualize --input network.json --layout spring --output plot.png
  network-visualizer convert --input network.csv --output network.graphml
  network-visualizer stats --input network.gml
  network-visualizer batch --config batch_config.json
            """
        )

        parser.add_argument('--debug', action='store_true',
                           help='Enable debug output')

        subparsers = parser.add_subparsers(dest='command', help='Available commands')

        # Analyze command
        analyze_parser = subparsers.add_parser('analyze', help='Analyze network properties')
        analyze_parser.add_argument('-i', '--input', required=True,
                                   help='Input network file')
        analyze_parser.add_argument('-o', '--output',
                                   help='Output analysis file (JSON)')
        analyze_parser.add_argument('--metrics', nargs='+',
                                   default=['degree', 'betweenness', 'closeness'],
                                   help='Metrics to compute')
        analyze_parser.add_argument('--communities', action='store_true',
                                   help='Detect communities')
        analyze_parser.add_argument('--format', choices=['json', 'csv', 'text'],
                                   default='json', help='Output format')

        # Visualize command
        viz_parser = subparsers.add_parser('visualize', help='Generate network visualization')
        viz_parser.add_argument('-i', '--input', required=True,
                               help='Input network file')
        viz_parser.add_argument('-o', '--output',
                               help='Output visualization file')
        viz_parser.add_argument('--layout', choices=['spring', 'circular', 'random', 'shell'],
                               default='spring', help='Layout algorithm')
        viz_parser.add_argument('--backend', choices=['matplotlib', 'plotly', 'graphviz'],
                               default='matplotlib', help='Rendering backend')
        viz_parser.add_argument('--size', nargs=2, type=int, default=[12, 8],
                               help='Figure size (width height)')
        viz_parser.add_argument('--dpi', type=int, default=300,
                               help='Resolution for raster output')
        viz_parser.add_argument('--labels', action='store_true',
                               help='Show node labels')

        # Convert command
        convert_parser = subparsers.add_parser('convert', help='Convert between formats')
        convert_parser.add_argument('-i', '--input', required=True,
                                   help='Input file')
        convert_parser.add_argument('-o', '--output', required=True,
                                   help='Output file')
        convert_parser.add_argument('--input-format',
                                   help='Input format (auto-detected if not specified)')
        convert_parser.add_argument('--output-format',
                                   help='Output format (auto-detected if not specified)')

        # Stats command
        stats_parser = subparsers.add_parser('stats', help='Show network statistics')
        stats_parser.add_argument('-i', '--input', required=True,
                                 help='Input network file')
        stats_parser.add_argument('--detailed', action='store_true',
                                 help='Show detailed statistics')

        # Compare command
        compare_parser = subparsers.add_parser('compare', help='Compare multiple networks')
        compare_parser.add_argument('-i', '--inputs', nargs='+', required=True,
                                   help='Input network files to compare')
        compare_parser.add_argument('-o', '--output',
                                   help='Output comparison file')
        compare_parser.add_argument('--metrics', nargs='+',
                                   default=['density', 'average_degree', 'diameter'],
                                   help='Metrics to compare')

        # Batch command
        batch_parser = subparsers.add_parser('batch', help='Run batch processing')
        batch_parser.add_argument('-c', '--config', required=True,
                                 help='Batch configuration file (JSON)')
        batch_parser.add_argument('--dry-run', action='store_true',
                                 help='Show what would be done without executing')

        return parser

    def analyze_command(self, args) -> int:
        """Handle analyze command."""
        print(f"📊 Analyzing network: {args.input}")

        try:
            # Load network
            G = self.visualizer.load_network(args.input)

            # Perform analysis
            analysis = self.visualizer.analyze_network(G, args.metrics)

            if args.communities:
                analysis['communities'] = self.visualizer.analyzer.detect_communities(G)

            # Output results
            if args.output:
                if args.format == 'json':
                    self.visualizer.save_analysis(analysis, args.output)
                elif args.format == 'csv':
                    self._export_analysis_csv(analysis, args.output)
                print(f"💾 Analysis saved to: {args.output}")
            else:
                self._print_analysis_summary(analysis)

            return 0

        except Exception as e:
            print(f"Analysis failed: {e}", file=sys.stderr)
            return 1

    def visualize_command(self, args) -> int:
        """Handle visualize command."""
        print(f"🎨 Visualizing network: {args.input}")

        try:
            # Load network
            G = self.visualizer.load_network(args.input)

            # Set up visualization config
            config = {
                'figsize': tuple(args.size),
                'dpi': args.dpi,
            }

            # Generate visualization
            output_file = args.output or f"{Path(args.input).stem}_visualization.png"

            self.visualizer.visualize_static(
                G,
                output_file=output_file,
                backend=args.backend,
                show_labels=args.labels,
                config=config
            )

            print(f"💾 Visualization saved to: {output_file}")
            return 0

        except Exception as e:
            print(f"Visualization failed: {e}", file=sys.stderr)
            return 1

    def convert_command(self, args) -> int:
        """Handle convert command."""
        print(f"🔄 Converting {args.input} → {args.output}")

        try:
            # Load network
            G = self.visualizer.load_network(args.input)

            # Save in new format
            self.visualizer.save_network(G, args.output)

            print(f"✅ Conversion complete")
            return 0

        except Exception as e:
            print(f"Conversion failed: {e}", file=sys.stderr)
            return 1

    def stats_command(self, args) -> int:
        """Handle stats command."""
        print(f"📈 Computing statistics for: {args.input}")

        try:
            # Load network
            G = self.visualizer.load_network(args.input)

            # Get statistics
            stats = self.visualizer.compute_statistics(G)

            if args.detailed:
                print("\nDetailed Statistics:")
                for key, value in stats.items():
                    if isinstance(value, float):
                        print(f"  {key}: {value:.4f}")
                    else:
                        print(f"  {key}: {value}")
            else:
                print(f"  Nodes: {stats['num_nodes']}")
                print(f"  Edges: {stats['num_edges']}")
                print(f"  Density: {stats['density']:.4f}")
                print(f"  Average Degree: {stats['average_degree']:.2f}")
                if stats.get('diameter'):
                    print(f"  Diameter: {stats['diameter']}")
                if stats.get('average_path_length'):
                    print(f"  Avg Path Length: {stats['average_path_length']:.2f}")

            return 0

        except Exception as e:
            print(f"Statistics computation failed: {e}", file=sys.stderr)
            return 1

    def compare_command(self, args) -> int:
        """Handle compare command."""
        print(f"🔍 Comparing {len(args.inputs)} networks")

        try:
            networks = []
            for filepath in args.inputs:
                G = self.visualizer.load_network(filepath)
                stats = self.visualizer.compute_statistics(G)
                networks.append({
                    'file': filepath,
                    'graph': G,
                    'stats': stats
                })

            # Generate comparison
            comparison = self._compare_networks(networks, args.metrics)

            if args.output:
                with open(args.output, 'w') as f:
                    import json
                    json.dump(comparison, f, indent=2)
                print(f"💾 Comparison saved to: {args.output}")
            else:
                self._print_comparison(comparison)

            return 0

        except Exception as e:
            print(f"Comparison failed: {e}", file=sys.stderr)
            return 1

    def batch_command(self, args) -> int:
        """Handle batch command."""
        print(f"📦 Running batch processing: {args.config}")

        try:
            # Load configuration
            with open(args.config, 'r') as f:
                config = json.load(f)

            if args.dry_run:
                print("🔍 Dry run - would process:")
                for task in config.get('tasks', []):
                    print(f"  {task.get('type', 'unknown')}: {task.get('input', 'unknown')}")
                return 0

            # Execute batch processing
            results = self._execute_batch(config)

            print(f"✅ Batch processing complete: {len(results)} tasks executed")
            return 0

        except Exception as e:
            print(f"Batch processing failed: {e}", file=sys.stderr)
            return 1

    def _print_analysis_summary(self, analysis: Dict) -> None:
        """Print analysis summary to console."""
        stats = analysis.get('statistics', {})

        print("\n📊 Network Analysis Summary")
        print("=" * 40)
        print(f"Nodes: {stats.get('num_nodes', 'N/A')}")
        print(f"Edges: {stats.get('num_edges', 'N/A')}")
        print(f"Density: {stats.get('density', 'N/A'):.4f}")
        print(f"Average Degree: {stats.get('average_degree', 'N/A'):.2f}")

        if 'centrality' in analysis:
            centrality = analysis['centrality']
            print(f"\nCentrality Metrics Computed: {len(centrality)}")

        if 'communities' in analysis:
            communities = analysis['communities']
            unique_communities = len(set(communities.values()))
            print(f"Communities Detected: {unique_communities}")

    def _export_analysis_csv(self, analysis: Dict, filepath: str) -> None:
        """Export analysis results to CSV."""
        import csv

        with open(filepath, 'w', newline='') as f:
            writer = csv.writer(f)

            # Write statistics
            if 'statistics' in analysis:
                writer.writerow(['Statistic', 'Value'])
                for key, value in analysis['statistics'].items():
                    writer.writerow([key, value])
                writer.writerow([])

            # Write centrality measures
            if 'centrality' in analysis:
                writer.writerow(['Node', 'Metric', 'Value'])
                for metric, values in analysis['centrality'].items():
                    for node, value in values.items():
                        writer.writerow([node, metric, value])
                writer.writerow([])

    def _compare_networks(self, networks: list, metrics: list) -> Dict:
        """Compare multiple networks."""
        comparison = {
            'networks': [],
            'metrics_comparison': {},
            'summary': {}
        }

        for network in networks:
            net_info = {
                'file': network['file'],
                'statistics': network['stats']
            }
            comparison['networks'].append(net_info)

        # Compare metrics across networks
        for metric in metrics:
            comparison['metrics_comparison'][metric] = [
                net['stats'].get(metric, 'N/A') for net in networks
            ]

        return comparison

    def _print_comparison(self, comparison: Dict) -> None:
        """Print network comparison to console."""
        print("\n🔍 Network Comparison")
        print("=" * 40)

        for i, network in enumerate(comparison['networks']):
            print(f"\nNetwork {i+1}: {network['file']}")
            stats = network['statistics']
            print(f"  Nodes: {stats.get('num_nodes', 'N/A')}")
            print(f"  Edges: {stats.get('num_edges', 'N/A')}")
            print(f"  Density: {stats.get('density', 'N/A'):.4f}")

        print(f"\n📊 Metrics Comparison:")
        for metric, values in comparison.get('metrics_comparison', {}).items():
            print(f"  {metric}: {values}")

    def _execute_batch(self, config: Dict) -> list:
        """Execute batch processing tasks."""
        results = []

        for task in config.get('tasks', []):
            task_type = task.get('type')

            if task_type == 'analyze':
                # Analyze network
                G = self.visualizer.load_network(task['input'])
                analysis = self.visualizer.analyze_network(G, task.get('metrics', []))
                if task.get('output'):
                    self.visualizer.save_analysis(analysis, task['output'])
                results.append({'task': task, 'status': 'completed'})

            elif task_type == 'visualize':
                # Generate visualization
                G = self.visualizer.load_network(task['input'])
                self.visualizer.visualize_static(
                    G,
                    output_file=task['output'],
                    backend=task.get('backend', 'matplotlib')
                )
                results.append({'task': task, 'status': 'completed'})

            elif task_type == 'convert':
                # Convert format
                G = self.visualizer.load_network(task['input'])
                self.visualizer.save_network(G, task['output'])
                results.append({'task': task, 'status': 'completed'})

        return results
