"""
Example script to generate a network analysis report using the Jinja2 template.
"""
import os
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

def generate_report(output_path: str = "network_report.html"):
    # Set up Jinja2 environment
    template_dir = Path(__file__).parent.parent / "network_visualizer" / "templates"
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    # Ensure tojson filter is available in plain Jinja environments
    env.filters['tojson'] = lambda v: json.dumps(v)
    template = env.get_template("report.html.j2")
    
    # Sample data - replace with your actual network analysis results
    statistics = {
        "num_nodes": 42,
        "num_edges": 150,
        "density": 0.1754
    }
    
    metrics = {
        "degree": {
            "Node1": 0.85,
            "Node2": 0.72,
            "Node3": 0.68,
            "Node4": 0.65,
            "Node5": 0.61,
            "Node6": 0.58,
            "Node7": 0.55,
            "Node8": 0.52,
            "Node9": 0.49,
            "Node10": 0.45,
            "Node11": 0.42
        },
        "betweenness": {
            "Node1": 0.32,
            "Node2": 0.28,
            "Node3": 0.25,
            "Node4": 0.22,
            "Node5": 0.19,
            "Node6": 0.16,
            "Node7": 0.13,
            "Node8": 0.10,
            "Node9": 0.08,
            "Node10": 0.05,
            "Node11": 0.02
        },
        "eigenvector": {
            "Node1": 0.91,
            "Node2": 0.84,
            "Node3": 0.79,
            "Node4": 0.72,
            "Node5": 0.65,
            "Node6": 0.58,
            "Node7": 0.51,
            "Node8": 0.44,
            "Node9": 0.37,
            "Node10": 0.30,
            "Node11": 0.23
        }
    }
    
    # Render template with data
    html_output = template.render(statistics=statistics, metrics=metrics)
    
    # Save to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_output)
    
    print(f"Report generated: {os.path.abspath(output_path)}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate a network analysis report.')
    parser.add_argument('--output', '-o', default='network_report.html',
                       help='Output HTML file path')
    
    args = parser.parse_args()
    generate_report(args.output)
