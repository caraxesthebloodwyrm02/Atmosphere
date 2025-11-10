# 💻 Command Line Interface Reference

## Overview

Network Visualizer provides a comprehensive command-line interface (CLI) for network analysis, visualization, and data processing. The CLI supports batch operations, automation, and integration with shell scripts.

## 🚀 Basic Usage

```bash
# Show help
network-visualizer --help

# Show version
network-visualizer --version
```

## 📊 Commands

### `analyze` - Network Analysis

Perform comprehensive network analysis with customizable metrics.

```bash
network-visualizer analyze [OPTIONS]
```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--input`, `-i` | | FILE | Input network file (required) | |
| `--output`, `-o` | | FILE | Output analysis file (JSON) | |
| `--metrics` | | LIST | Metrics to compute | degree,betweenness,closeness |
| `--communities` | | FLAG | Detect communities | False |
| `--format` | | CHOICE | Output format: json, csv, text | json |
| `--debug` | | FLAG | Enable debug output | False |

#### Available Metrics

- `degree` - Degree centrality
- `betweenness` - Betweenness centrality
- `closeness` - Closeness centrality
- `eigenvector` - Eigenvector centrality
- `pagerank` - PageRank centrality
- `katz` - Katz centrality
- `clustering` - Local clustering coefficient

#### Examples

```bash
# Basic analysis
network-visualizer analyze -i karate_club.graphml

# Custom metrics
network-visualizer analyze -i network.json --metrics degree betweenness eigenvector

# With community detection
network-visualizer analyze -i network.graphml --communities --output analysis.json

# CSV output for spreadsheet analysis
network-visualizer analyze -i network.csv --format csv --output metrics.csv
```

### `visualize` - Network Visualization

Generate static or interactive network visualizations.

```bash
network-visualizer visualize [OPTIONS]
```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--input`, `-i` | | FILE | Input network file (required) | |
| `--output`, `-o` | | FILE | Output visualization file | |
| `--layout` | | CHOICE | Layout algorithm | spring |
| `--backend` | | CHOICE | Rendering backend | matplotlib |
| `--size` | | INT INT | Figure size (width height) | 12 8 |
| `--dpi` | | INT | Resolution for raster output | 300 |
| `--labels` | | FLAG | Show node labels | False |
| `--debug` | | FLAG | Enable debug output | False |

#### Layout Algorithms

- `spring` - Force-directed spring layout
- `circular` - Circular node arrangement
- `random` - Random node positioning
- `shell` - Concentric shell layout
- `spectral` - Spectral layout using eigenvalues
- `kamada_kawai` - Kamada-Kawai force-directed
- `fruchterman_reingold` - Fruchterman-Reingold force-directed
- `hierarchical` - Hierarchical tree layout

#### Rendering Backends

- `matplotlib` - Static plots (PNG, PDF, SVG, EPS)
- `plotly` - Interactive plots (HTML, PNG, SVG)
- `graphviz` - Graphviz-based layouts (PNG, SVG, PDF)

#### Examples

```bash
# Basic visualization
network-visualizer visualize -i network.graphml

# High-resolution PDF for publication
network-visualizer visualize -i network.json --backend matplotlib --output publication.pdf --dpi 600

# Interactive web visualization
network-visualizer visualize -i network.csv --backend plotly --output interactive.html

# Large network with custom layout
network-visualizer visualize -i large_network.graphml --layout spectral --size 20 20 --output large_viz.png
```

### `convert` - Format Conversion

Convert between different network file formats.

```bash
network-visualizer convert [OPTIONS]
```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--input`, `-i` | | FILE | Input file (required) | |
| `--output`, `-o` | | FILE | Output file (required) | |
| `--input-format` | | STR | Input format (auto-detected) | auto |
| `--output-format` | | STR | Output format (auto-detected) | auto |
| `--debug` | | FLAG | Enable debug output | False |

#### Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| GraphML | .graphml | XML-based standard format |
| GML | .gml | Graph Modelling Language |
| JSON | .json | Node-link JSON format |
| CSV | .csv | Comma-separated values |
| Edge List | .txt, .edgelist | Simple edge list format |
| Adjacency Matrix | .adj, .mat | Matrix format |

#### Examples

```bash
# Convert CSV to GraphML
network-visualizer convert -i network.csv -o network.graphml

# Convert GraphML to JSON
network-visualizer convert -i network.graphml -o network.json

# Explicit format specification
network-visualizer convert -i data.txt -o data.graphml --input-format edge_list
```

### `stats` - Network Statistics

Display basic network statistics and properties.

```bash
network-visualizer stats [OPTIONS]
```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--input`, `-i` | | FILE | Input network file (required) | |
| `--detailed` | | FLAG | Show detailed statistics | False |
| `--debug` | | FLAG | Enable debug output | False |

#### Displayed Statistics

**Basic Statistics:**
- Number of nodes and edges
- Network density
- Average degree
- Degree distribution summary

**Detailed Statistics (with --detailed):**
- Diameter (if computable)
- Average path length
- Clustering coefficients
- Connected components
- Degree centrality summary

#### Examples

```bash
# Basic statistics
network-visualizer stats -i network.graphml

# Detailed analysis
network-visualizer stats -i network.json --detailed
```

### `compare` - Network Comparison

Compare multiple networks using various metrics.

```bash
network-visualizer compare [OPTIONS]
```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--inputs`, `-i` | | FILE LIST | Input network files (required, min 2) | |
| `--output`, `-o` | | FILE | Output comparison file | |
| `--metrics` | | LIST | Metrics to compare | density,average_degree,diameter |
| `--debug` | | FLAG | Enable debug output | False |

#### Comparison Metrics

- `density` - Network density
- `average_degree` - Average node degree
- `diameter` - Network diameter
- `average_path_length` - Average shortest path
- `clustering_coefficient` - Global clustering
- `connected_components` - Number of components

#### Examples

```bash
# Compare two networks
network-visualizer compare -i network1.graphml network2.graphml

# Compare multiple networks with custom metrics
network-visualizer compare -i net1.json net2.json net3.csv --metrics density clustering_coefficient

# Save comparison results
network-visualizer compare -i *.graphml --output comparison.json
```

### `batch` - Batch Processing

Execute batch processing jobs defined in a configuration file.

```bash
network-visualizer batch [OPTIONS]
```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--config`, `-c` | | FILE | Batch configuration file (required) | |
| `--dry-run` | | FLAG | Show what would be done | False |
| `--debug` | | FLAG | Enable debug output | False |

#### Configuration File Format

```json
{
  "tasks": [
    {
      "type": "analyze",
      "input": "network1.graphml",
      "output": "analysis1.json",
      "metrics": ["degree", "betweenness"]
    },
    {
      "type": "visualize",
      "input": "network2.json",
      "output": "viz2.png",
      "layout": "spring",
      "backend": "matplotlib"
    },
    {
      "type": "convert",
      "input": "network3.csv",
      "output": "network3.graphml"
    }
  ]
}
```

#### Examples

```bash
# Execute batch job
network-visualizer batch -c batch_config.json

# Dry run to preview tasks
network-visualizer batch -c batch_config.json --dry-run
```

## 🌐 Web Interface

Launch the interactive web application.

```bash
network-visualizer --web [OPTIONS]
```

#### Options

| Option | Short | Type | Description | Default |
|--------|-------|------|-------------|---------|
| `--host` | | STR | Server host | localhost |
| `--port` | | INT | Server port | 5000 |
| `--debug` | | FLAG | Enable debug mode | False |

#### Examples

```bash
# Start web interface
network-visualizer --web

# Custom host/port
network-visualizer --web --host 0.0.0.0 --port 8080

# Debug mode for development
network-visualizer --web --debug
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NETWORK_VIZ_BACKEND` | Default rendering backend | matplotlib |
| `NETWORK_VIZ_LAYOUT` | Default layout algorithm | spring |
| `NETWORK_VIZ_DEBUG` | Enable debug logging | False |
| `NETWORK_VIZ_CACHE_DIR` | Cache directory for temporary files | ~/.network_visualizer/cache |

### Configuration File

Create `~/.network_visualizer/config.json`:

```json
{
  "default_backend": "plotly",
  "default_layout": "spring",
  "figure_size": [12, 8],
  "dpi": 300,
  "cache_enabled": true,
  "parallel_processing": true
}
```

## 🔧 Advanced Usage

### Piping and Redirection

```bash
# Pipe analysis output to file
network-visualizer analyze -i network.graphml > analysis.txt

# Chain commands with temporary files
network-visualizer convert -i network.csv -o temp.graphml && \
network-visualizer analyze -i temp.graphml -o analysis.json && \
rm temp.graphml
```

### Batch Processing with Shell Scripts

```bash
#!/bin/bash
# batch_process.sh

INPUT_DIR="networks/"
OUTPUT_DIR="results/"

for file in "$INPUT_DIR"/*.graphml; do
    basename=$(basename "$file" .graphml)
    echo "Processing $basename..."

    # Analyze network
    network-visualizer analyze -i "$file" -o "$OUTPUT_DIR/${basename}_analysis.json"

    # Generate visualization
    network-visualizer visualize -i "$file" -o "$OUTPUT_DIR/${basename}_viz.png"
done

echo "Batch processing complete!"
```

### Parallel Processing

```bash
# Process multiple networks in parallel
ls networks/*.graphml | parallel --no-notice \
    'network-visualizer analyze -i {} -o results/{/.}_analysis.json'
```

### Integration with Other Tools

```bash
# Generate analysis and pipe to jq for JSON processing
network-visualizer analyze -i network.graphml | jq '.statistics'

# Create visualization and optimize with ImageMagick
network-visualizer visualize -i network.graphml -o temp.png && \
convert temp.png -resize 50% -quality 90 final.png && \
rm temp.png
```

## 🐛 Troubleshooting

### Common Issues

#### "Command not found"
```bash
# Ensure package is installed
pip install network-visualizer

# Check if scripts are in PATH
which network-visualizer

# Try python module execution
python -m network_visualizer --help
```

#### "Module not found" errors
```bash
# Install missing optional dependencies
pip install network-visualizer[all]

# Check Python environment
python -c "import network_visualizer; print(network_visualizer.__version__)"
```

#### Memory issues with large networks
```bash
# Use streaming for large files (future feature)
# For now, increase system memory or use sampling

# Check available memory
free -h  # Linux
system_profiler SPHardwareDataType  # macOS
```

#### Permission errors
```bash
# Run with appropriate permissions
sudo network-visualizer ...

# Or install without sudo
pip install --user network-visualizer
```

## 📊 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Command-line parsing error |
| 3 | File not found |
| 4 | Invalid input format |
| 5 | Analysis error |
| 6 | Visualization error |
| 7 | Output error |

## 📈 Performance Tips

### For Large Networks
```bash
# Use efficient layouts
network-visualizer visualize -i large.graphml --layout random

# Reduce output quality for faster rendering
network-visualizer visualize -i network.graphml --dpi 150

# Use batch processing for multiple networks
network-visualizer batch -c large_batch_config.json
```

### Memory Optimization
```bash
# Limit concurrent operations
export NETWORK_VIZ_MAX_WORKERS=2

# Use disk caching for large datasets
export NETWORK_VIZ_CACHE_DIR=/tmp/network_cache
```

## 📚 Examples

### Complete Workflow
```bash
# 1. Convert data format
network-visualizer convert -i raw_data.csv -o network.graphml

# 2. Analyze network
network-visualizer analyze -i network.graphml --communities -o analysis.json

# 3. Generate multiple visualizations
network-visualizer visualize -i network.graphml --layout spring -o spring_layout.png
network-visualizer visualize -i network.graphml --layout circular -o circular_layout.png

# 4. Compare with reference network
network-visualizer compare -i network.graphml reference.graphml -o comparison.json
```

### Research Pipeline
```bash
#!/bin/bash
# research_pipeline.sh

DATASETS=("social" "biological" "transportation")
LAYOUTS=("spring" "spectral" "circular")

for dataset in "${DATASETS[@]}"; do
    echo "Processing $dataset network..."

    # Analyze
    network-visualizer analyze -i "data/${dataset}.graphml" \
        --metrics degree betweenness eigenvector \
        -o "results/${dataset}_analysis.json"

    # Visualize with different layouts
    for layout in "${LAYOUTS[@]}"; do
        network-visualizer visualize -i "data/${dataset}.graphml" \
            --layout $layout \
            --output "results/${dataset}_${layout}.png"
    done
done

echo "Research pipeline complete!"
```

---

*For more information, see the [full documentation](index.md) or visit our [GitHub repository](https://github.com/your-org/network-visualizer).* 🌐✨
