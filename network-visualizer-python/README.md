# Network Visualizer (Python Edition)
## Advanced Network Visualization and Analysis Tool

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![NetworkX](https://img.shields.io/badge/NetworkX-3.0+-green.svg)](https://networkx.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive network visualization and analysis toolkit inspired by Gephi, built with Python. This project provides advanced graph visualization, network analysis algorithms, and interactive exploration capabilities for complex network structures.

## 🎯 Features

### Core Visualization Capabilities
- **Interactive Graph Visualization**: Real-time network exploration with zoom, pan, and selection
- **Multiple Layout Algorithms**: Force-directed, circular, hierarchical, and spectral layouts
- **Advanced Rendering**: High-performance rendering with matplotlib, plotly, and graphviz backends
- **Temporal Network Analysis**: Dynamic network evolution over time

### Network Analysis Tools
- **Centrality Metrics**: Degree, betweenness, closeness, and eigenvector centrality
- **Community Detection**: Louvain, Girvan-Newman, and label propagation algorithms
- **Path Analysis**: Shortest paths, network diameter, and connectivity measures
- **Statistical Analysis**: Network density, clustering coefficients, and degree distributions

### Data Integration
- **Multiple Formats**: Support for GraphML, GML, JSON, CSV, and edge lists
- **Database Integration**: PostgreSQL, Neo4j, and MongoDB connectors
- **API Integration**: RESTful APIs for real-time network data streaming
- **Plugin Architecture**: Extensible plugin system for custom data sources

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/network-visualizer-python.git
cd network-visualizer-python

# Install in development mode
pip install -e .

# Or install from PyPI (when available)
pip install network-visualizer
```

### Basic Usage

```python
from network_visualizer import NetworkVisualizer

# Create a network visualizer instance
visualizer = NetworkVisualizer()

# Load a sample network
G = visualizer.load_sample_graph('karate_club')

# Compute centrality metrics
centrality = visualizer.compute_centrality(G, method='betweenness')

# Visualize the network
visualizer.visualize(G, layout='force_directed', show_labels=True)

# Export analysis results
visualizer.export_analysis(G, 'analysis_report.html')
```

### Command Line Interface

```bash
# Launch interactive visualizer
network-visualizer --interactive

# Analyze network file
network-visualizer analyze --input network.graphml --output analysis.json

# Generate visualization
network-visualizer visualize --input network.json --layout spring --output network.png
```

## 📦 Project Structure

```
network-visualizer/
├── pyproject.toml              # Project configuration (PEP 621)
├── setup.py                   # Legacy setup script
├── MANIFEST.in               # Package manifest
├── README.md                 # This file
├── LICENSE                   # MIT License
├── requirements.txt          # Dependencies
├── network_visualizer/       # Main package
│   ├── __init__.py          # Package initialization
│   ├── __main__.py          # CLI entry point
│   ├── core/                # Core visualization engine
│   │   ├── __init__.py
│   │   ├── visualizer.py    # Main visualizer class
│   │   ├── layouts.py       # Layout algorithms
│   │   ├── renderers.py     # Rendering backends
│   │   └── algorithms.py    # Network analysis algorithms
│   ├── io/                  # Data input/output
│   │   ├── __init__.py
│   │   ├── loaders.py       # Data loading utilities
│   │   ├── exporters.py     # Export functionality
│   │   └── formats.py       # Format handlers
│   ├── ui/                  # User interface components
│   │   ├── __init__.py
│   │   ├── web/            # Web-based interface
│   │   ├── desktop/        # Desktop GUI
│   │   └── cli.py          # Command-line interface
│   ├── plugins/            # Plugin system
│   │   ├── __init__.py
│   │   ├── base.py         # Plugin base classes
│   │   └── loaders/        # Plugin discovery
│   └── utils/              # Utility functions
│       ├── __init__.py
│       ├── helpers.py      # General utilities
│       └── validation.py   # Data validation
├── tests/                  # Test suite
│   ├── __init__.py
│   ├── test_core.py        # Core functionality tests
│   ├── test_io.py          # I/O tests
│   ├── test_ui.py          # UI tests
│   ├── test_plugins.py     # Plugin tests
│   └── fixtures/           # Test data
├── docs/                   # Documentation
│   ├── index.md
│   ├── api/
│   ├── tutorials/
│   └── examples/
├── examples/               # Example scripts
│   ├── basic_visualization.py
│   ├── centrality_analysis.py
│   ├── community_detection.py
│   └── custom_layouts.py
├── scripts/                # Development scripts
│   ├── build_docs.py
│   ├── run_tests.py
│   └── generate_sample_data.py
└── .github/                # GitHub configuration
    ├── workflows/
    └── ISSUE_TEMPLATE/
```

## 🏗️ Architecture

### Modular Design
Following the Maven-inspired modular architecture, the project is organized into focused modules:

- **`core`**: Core visualization and analysis engine
- **`io`**: Data input/output and format handling
- **`ui`**: User interface components (web, desktop, CLI)
- **`plugins`**: Extensible plugin system
- **`utils`**: Shared utility functions

### Plugin Architecture
The plugin system allows extending functionality without modifying core code:

```python
from network_visualizer.plugins import Plugin

class CustomLayoutPlugin(Plugin):
    name = "custom_layout"
    version = "1.0.0"

    def execute(self, graph, **kwargs):
        # Custom layout algorithm implementation
        return custom_layout_positions(graph)
```

### Rendering Backends
Multiple rendering backends for different use cases:

- **Matplotlib**: Publication-quality static plots
- **Plotly**: Interactive web-based visualizations
- **Graphviz**: Hierarchical and flow diagrams
- **PyQt**: Native desktop applications
- **WebGL**: High-performance web rendering

## 🔧 Configuration

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "network-visualizer"
version = "0.1.0"
description = "Advanced network visualization toolkit"
authors = [{name = "Your Name", email = "your.email@example.com"}]
dependencies = [
    "networkx>=3.0",
    "matplotlib>=3.5",
    "plotly>=5.0",
    "numpy>=1.21",
    "pandas>=1.3",
    "scipy>=1.7"
]
```

### Environment Variables
```bash
# Set default visualization backend
export NETWORK_VISUALIZER_BACKEND=plotly

# Configure plugin directory
export NETWORK_VISUALIZER_PLUGIN_DIR=/path/to/plugins

# Set logging level
export NETWORK_VISUALIZER_LOG_LEVEL=INFO
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=network_visualizer --cov-report=html

# Run specific test module
pytest tests/test_core.py

# Run with verbose output
pytest -v
```

## 📚 Documentation

- [API Reference](docs/api/)
- [User Guide](docs/user_guide.md)
- [Developer Guide](docs/developer_guide.md)
- [Examples](examples/)
- [Plugin Development](docs/plugins.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run linting and formatting
black network_visualizer/
isort network_visualizer/
flake8 network_visualizer/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original Gephi project for inspiration
- NetworkX library for graph algorithms
- Matplotlib and Plotly for visualization
- Open source network analysis community

## 🔗 Related Projects

- [Gephi](https://gephi.org/) - Original Java-based network visualizer
- [NetworkX](https://networkx.org/) - Python graph library
- [GraphXR](https://graphxr.com/) - Commercial network visualization
- [Cytoscape](https://cytoscape.org/) - Biological network analysis
