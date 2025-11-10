# 🛠️ Installation Guide

## Prerequisites

Network Visualizer requires **Python 3.8 or higher**. We recommend using Python 3.9+ for optimal performance.

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **Python** | 3.8.0 | 3.9.0+ |
| **RAM** | 4GB | 8GB+ |
| **Disk Space** | 500MB | 1GB+ |
| **OS** | Windows 10+ / macOS 10.15+ / Linux | Any modern OS |

### Optional Dependencies

For full functionality, install these optional packages:

- **Graphviz**: For graphviz backend rendering
- **PyTorch**: For advanced ML-based algorithms (future)
- **CUDA**: For GPU acceleration (future)

---

## 🚀 Quick Installation

### From PyPI (Recommended)

```bash
# Install core package
pip install network-visualizer

# Install with all optional dependencies
pip install network-visualizer[all]

# Install with web interface
pip install network-visualizer[web]

# Install with development tools
pip install network-visualizer[dev]
```

### From Source

```bash
# Clone repository
git clone https://github.com/your-org/network-visualizer.git
cd network-visualizer

# Install in development mode
pip install -e .

# Install with optional dependencies
pip install -e ".[all,web,dev]"
```

### Using Conda

```bash
# Create new environment
conda create -n network-viz python=3.9
conda activate network-viz

# Install package
pip install network-visualizer[all]
```

---

## 🔧 Detailed Installation

### Core Dependencies

The following packages are automatically installed:

```toml
# From pyproject.toml
dependencies = [
    "networkx>=3.0",
    "numpy>=1.21.0",
    "scipy>=1.7.0",
    "matplotlib>=3.5.0",
    "pandas>=1.3.0",
]
```

### Optional Feature Groups

#### Web Interface
```bash
pip install network-visualizer[web]
```
Includes:
- Flask>=2.0.0
- flask-cors>=3.0.0
- plotly>=5.0.0

#### Graphviz Backend
```bash
pip install network-visualizer[graphviz]
```
Includes:
- graphviz>=0.19.0
- pygraphviz>=1.9 (if available)

#### Development Tools
```bash
pip install network-visualizer[dev]
```
Includes:
- pytest>=7.0.0
- pytest-cov>=4.0.0
- black>=22.0.0
- mypy>=0.950
- flake8>=5.0.0
- sphinx>=5.0.0

#### All Features
```bash
pip install network-visualizer[all]
```
Includes all optional dependencies for complete functionality.

---

## 🖥️ Platform-Specific Instructions

### Windows

#### Using pip
```bash
# Install Microsoft Visual C++ Build Tools if needed
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

pip install network-visualizer[all]
```

#### Using Anaconda
```bash
conda create -n network-viz python=3.9
conda activate network-viz
conda install -c conda-forge networkx matplotlib scipy pandas
pip install network-visualizer
```

### macOS

```bash
# Using Homebrew (recommended)
brew install python@3.9 graphviz

# Install package
pip install network-visualizer[all]
```

### Linux (Ubuntu/Debian)

```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev python3-pip graphviz graphviz-dev

# Install package
pip install network-visualizer[all]
```

### Linux (CentOS/RHEL)

```bash
# Install system dependencies
sudo yum install python3-devel graphviz graphviz-devel

# Install package
pip install network-visualizer[all]
```

---

## 🔍 Verification

After installation, verify Network Visualizer is working:

```python
# Test basic import
import network_visualizer
print(f"Network Visualizer v{network_visualizer.__version__}")

# Test core functionality
from network_visualizer import NetworkVisualizer
viz = NetworkVisualizer()
G = viz.load_sample_graph('karate_club')
print(f"Loaded network with {len(G.nodes)} nodes and {len(G.edges)} edges")

# Test visualization
viz.visualize_static(G, output_file='test.png')
print("Visualization saved as test.png")
```

### Expected Output
```
Network Visualizer v0.1.0
Loaded network with 34 nodes and 78 edges
Visualization saved as test.png
```

---

## 🐛 Troubleshooting

### Common Issues

#### Import Error: "No module named 'network_visualizer'"

**Solution**: Ensure the package is installed in the correct Python environment.

```bash
# Check which Python/pip you're using
which python
which pip

# Install in the correct environment
pip install network-visualizer

# Or use python -m pip
python -m pip install network-visualizer
```

#### Graphviz Backend Not Available

**Error**: "graphviz backend not available"

**Solution**: Install graphviz system library and Python package.

```bash
# Install system library
# Ubuntu/Debian:
sudo apt-get install graphviz graphviz-dev

# macOS:
brew install graphviz

# Windows: Download from https://graphviz.org/download/

# Install Python package
pip install graphviz
pip install network-visualizer[graphviz]
```

#### Web Interface Issues

**Error**: "Flask not found"

**Solution**: Install web dependencies.

```bash
pip install network-visualizer[web]
```

#### Permission Errors

**Solution**: Use virtual environment or user installation.

```bash
# Create virtual environment
python -m venv network_viz_env
source network_viz_env/bin/activate  # On Windows: network_viz_env\Scripts\activate

# Install package
pip install network-visualizer[all]
```

#### Memory Issues with Large Networks

**Solution**: Increase system memory or use sampling.

```python
# For large networks, use sampling
from network_visualizer.core.algorithms import NetworkSampler

sampler = NetworkSampler()
sampled_graph = sampler.sample_nodes(large_graph, sample_size=5000)
```

---

## 📦 Offline Installation

For systems without internet access:

```bash
# Download wheel on connected machine
pip download --dest=./packages network-visualizer[all]

# Transfer packages to offline machine
# Copy packages directory to offline machine

# Install on offline machine
pip install --no-index --find-links=./packages network-visualizer
```

---

## 🔄 Upgrading

### From PyPI
```bash
# Upgrade to latest version
pip install --upgrade network-visualizer

# Upgrade with all extras
pip install --upgrade network-visualizer[all]
```

### From Source
```bash
cd network-visualizer
git pull origin main
pip install -e ".[all]"
```

### Checking Version
```python
import network_visualizer
print(f"Current version: {network_visualizer.__version__}")
```

---

## 🧪 Testing Installation

Run the test suite to verify installation:

```bash
# Install test dependencies
pip install network-visualizer[dev]

# Run basic tests
python -m pytest tests/test_core.py -v

# Run full test suite
python -m pytest tests/ --cov=network_visualizer

# Run performance tests
python -m pytest tests/ -k "performance" -v
```

### Expected Test Results
```
========================= test session starts =========================
collected 25 items

tests/test_core.py::TestNetworkVisualizer::test_initialization PASSED
tests/test_core.py::TestNetworkVisualizer::test_load_sample_graph PASSED
tests/test_core.py::TestNetworkAnalyzer::test_centrality_methods PASSED
...
========================= 25 passed, 0 failed in 5.23s ========================
```

---

## 🎯 Next Steps

After successful installation:

1. **📖 Read the Tutorial**: [tutorial.md](tutorial.md)
2. **🎮 Try the Examples**: [examples/](../examples/)
3. **🌐 Start Web Interface**: `network-visualizer --web`
4. **📊 Analyze Your Data**: Load your own network data
5. **🔧 Customize**: Explore plugins and extensions

---

## 📞 Support

If you encounter issues:

1. **Check this guide** for common solutions
2. **Search existing issues** on GitHub
3. **Create a new issue** with:
   - Python version: `python --version`
   - Installation method
   - Error message and traceback
   - System information

Happy network visualizing! 🌐✨
