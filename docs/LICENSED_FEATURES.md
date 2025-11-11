# Licensed Advanced Features Guide

This guide provides comprehensive documentation for the licensed advanced tools and features implemented in the Atmosphere Arcade system.

## 🎯 Overview

The Atmosphere Arcade integrates licensed APIs and libraries to provide advanced AI, audio processing, and network analysis capabilities. All licensed features include graceful fallback mechanisms to ensure functionality even when API keys or licenses are unavailable.

## 🤖 AI Assistant (OpenAI/Anthropic Integration)

### Features
- **Conversational AI**: Natural language chat powered by GPT-4 or Claude
- **Code Analysis**: Intelligent code review and improvement suggestions
- **Code Generation**: Automated code creation based on descriptions
- **Multi-Provider Support**: Automatic fallback between OpenAI and Anthropic
- **Demo Mode**: Functional responses when APIs are unavailable

### Setup
```bash
# Set API keys (optional - demo mode works without them)
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### Usage Examples

#### CLI Usage
```bash
# Interactive chat
python Arcade/ui_cli.py ai chat --message "Explain quantum computing"

# Code analysis
python Arcade/ui_cli.py ai analyze --code "def fibonacci(n): return n if n < 2 else fibonacci(n-1) + fibonacci(n-2)" --language python

# Code generation
python Arcade/ui_cli.py ai generate --description "Create a FastAPI endpoint for user management" --language python
```

#### Programmatic Usage
```python
from Arcade.tools.ai_assistant import AIAssistant

assistant = AIAssistant()

# Check provider status
info = assistant.get_provider_info()
print(f"Using: {info['provider']}, Key available: {info['has_key']}")

# Chat
response = assistant.chat("What are the benefits of microservices?")
print(response['response'])

# Code analysis
analysis = assistant.analyze_code("""
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
""", "python")
print(analysis['analysis'])

# Code generation
code = assistant.generate_code("Create a class for managing user sessions", "python")
print(code['code'])
```

### API Response Format
```python
{
    'success': True,
    'response': 'AI-generated response text',
    'demo': False  # True if using demo mode
}
```

## 🎵 Advanced Audio Analysis (NumPy/SciPy)

### Features
- **FFT Spectral Analysis**: Professional frequency domain analysis
- **Spectral Centroid**: Measure of spectral brightness
- **Spectral Rolloff**: Frequency below which 85% of energy resides
- **Band Power Analysis**: Bass, mid, treble frequency ranges
- **Real-time Processing**: Live audio file analysis
- **Multiple Analysis Types**: 808 bass, delay effects, sound processing

### Supported File Formats
- WAV files (recommended for analysis)
- Automatic mono/stereo conversion
- 16-bit/24-bit depth support

### Usage Examples

#### Spectral Analysis
```bash
# CLI spectral analysis
python Arcade/ui_cli.py analyze spectral --file test_audio/high_quality.wav
```

#### Programmatic Usage
```python
from Arcade.tools.audio_analyzer import AudioAnalyzer

analyzer = AudioAnalyzer()

# Advanced spectral analysis
result = analyzer.advanced_spectral_analysis("audio.wav")
print(f"Sample Rate: {result['sample_rate']} Hz")
print(f"Spectral Centroid: {result['centroid']:.1f} Hz")
print(f"Bass Power: {result['bass_power']:.1f} dB")
print(f"Mid Power: {result['mid_power']:.1f} dB")
print(f"Treble Power: {result['treble_power']:.1f} dB")

# Traditional analysis
bass_result = analyzer.analyze_808_bass("audio.wav")
delay_result = analyzer.analyze_bass_vs_delay("audio.wav")
effects_result = analyzer.analyze_sound_effects("reverb")
```

### Analysis Output
```python
{
    'success': True,
    'sample_rate': 44100,
    'duration': 5.0,
    'centroid': 1200.5,  # Hz
    'rolloff': 8500.0,   # Hz (85% energy)
    'bass_power': -15.2, # dB
    'mid_power': -8.7,   # dB
    'treble_power': -22.1 # dB
}
```

## 🎨 Spatial Audio Visualization

### Features
- **3D Spatial Rendering**: Source-listener position visualization
- **Distance Calculation**: Real-time spatial distance computation
- **ASCII Visualization**: Terminal-based spatial representation
- **Comprehensive Analysis**: 6-panel spatial audio examination
- **Doppler Effect Simulation**: Movement-based frequency shifting
- **HRTF Processing**: Head-related transfer function modeling

### Usage Examples

#### CLI Usage
```bash
# 3D spatial visualization
python Arcade/ui_cli.py visualize 3d --source 5.0 0.0 2.0 --listener 0.0 0.0 0.0 --save

# Comprehensive analysis
python Arcade/ui_cli.py visualize comprehensive
```

#### Programmatic Usage
```python
from Arcade.tools.spatial_visualizer import SpatialVisualizer

visualizer = SpatialVisualizer()

# 3D spatial visualization
result = visualizer.visualize_3d_spatial(
    source_pos=(5.0, 0.0, 2.0),
    listener_pos=(0.0, 0.0, 0.0),
    save_image=True
)
print(f"Distance: {result['distance']:.2f} units")

# Comprehensive visualization
comprehensive = visualizer.visualize_comprehensive()
print(f"Generated {comprehensive['panels']} analysis panels")
```

## 🕸️ Network Graph Analysis (NetworkX)

### Features
- **Centrality Measures**: Degree, betweenness, closeness, eigenvector, PageRank, Katz
- **Community Detection**: Louvain, Girvan-Newman, label propagation algorithms
- **Network Statistics**: Density, clustering, connectivity analysis
- **Path Analysis**: Shortest paths and network flow computation
- **Real-time Processing**: Live network data analysis

### Supported Algorithms

#### Centrality Measures
- **Degree Centrality**: Node connectivity importance
- **Betweenness Centrality**: Bridge node importance
- **Closeness Centrality**: Average distance to all other nodes
- **Eigenvector Centrality**: Influence based on connections
- **PageRank**: Google-style importance ranking
- **Katz Centrality**: Generalized eigenvector centrality

#### Community Detection
- **Louvain Method**: Modularity optimization
- **Girvan-Newman**: Edge betweenness clustering
- **Label Propagation**: Local community detection

### Usage Examples

```python
import networkx as nx
from network_visualizer.core.algorithms import NetworkAnalyzer

# Create analyzer
analyzer = NetworkAnalyzer()

# Load or create network
G = nx.erdos_renyi_graph(100, 0.1)

# Compute centralities
degree_cent = analyzer.compute_centrality(G, 'degree')
betweenness_cent = analyzer.compute_centrality(G, 'betweenness')
pagerank_cent = analyzer.compute_centrality(G, 'pagerank')

# Community detection
communities = analyzer.detect_communities(G, 'louvain')

# Network statistics
stats = analyzer.compute_statistics(G)
print(f"Nodes: {stats['num_nodes']}")
print(f"Edges: {stats['num_edges']}")
print(f"Density: {stats['density']:.3f}")
print(f"Average Clustering: {stats['clustering_coefficient']:.3f}")
```

## 🎮 Interactive Playground

### Features
- **Demo System**: Showcase all licensed capabilities
- **Interactive Menus**: User-guided exploration
- **Multiple Demo Types**: Audio, spatial, trajectory, preview, random
- **Real-time Feedback**: Live demonstration results
- **Educational Content**: Learn through interactive examples

### Available Demos
- **Audio Analysis**: Bass, delay, and spectral demonstrations
- **Spatial Visualization**: 3D positioning and acoustic field display
- **Trajectory Analysis**: Movement pattern visualization
- **Real-time Preview**: Processing pipeline demonstration
- **Random Demo**: Surprise capability showcase

### Usage Examples

```bash
# CLI usage
python Arcade/ui_cli.py demo audio
python Arcade/ui_cli.py playground

# Programmatic usage
from Arcade.tools.interactive_playground import InteractivePlayground

playground = InteractivePlayground()

# Show menu
playground.show_menu()

# Run specific demo
playground.run_demo("spatial")
playground.run_demo("random")
```

## 🔧 Tool Dispatch System

### Features
- **Automated Routing**: Intelligent tool-to-zone assignment
- **Background Processing**: Asynchronous tool execution
- **Process Monitoring**: Real-time execution tracking
- **Log Management**: Comprehensive execution logging
- **Zone-based Execution**: Isolated processing environments

### Configuration
```yaml
# config/routing.yaml
audio_analyzer: audio
spatial_visualizer: visual
ai_assistant: games
network_visualizer: visual
```

### Usage Examples

```bash
# Start dispatcher
python Arcade/ui_cli.py run --background

# Check status
python Arcade/ui_cli.py status

# View zone logs
python Arcade/ui_cli.py log visual

# List zones
python Arcade/ui_cli.py zones

# Play tool (drop into incoming queue)
python Arcade/ui_cli.py play ai_assistant
```

## 🔐 License Management

### API Key Configuration
```bash
# Environment variables
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

# Or create .env file
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
```

### Fallback Behavior
- **Demo Mode**: All licensed features provide functional demos
- **Graceful Degradation**: System continues working without licenses
- **Error Handling**: Comprehensive error reporting and recovery
- **Logging**: License status and fallback usage tracking

### License Compliance
- **Third-party Notices**: Complete attribution in `ThirdPartyNotices.txt`
- **API Terms**: Respect for OpenAI/Anthropic usage policies
- **Open Source**: Compatible with MIT and BSD licenses
- **Commercial Use**: Ready for commercial deployment

## 🚀 Performance Optimization

### Caching Strategies
- **Response Caching**: AI responses cached for repeated queries
- **Analysis Results**: Spectral analysis cached for same files
- **Visualization Cache**: Generated images cached for reuse

### Resource Management
- **Memory Limits**: Configurable memory usage limits
- **Concurrent Processing**: Controlled parallelism for heavy computations
- **Timeout Handling**: Automatic termination of long-running processes

### Monitoring
```python
from Arcade.tools.ai_assistant import AIAssistant

assistant = AIAssistant()

# Get provider info
info = assistant.get_provider_info()
print(f"Provider: {info['provider']}")
print(f"API Key Available: {info['has_key']}")

# Clear conversation history
assistant.clear_history()
```

## 🐛 Troubleshooting

### Common Issues

#### AI Assistant Not Working
```bash
# Check API keys
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Test connectivity
python -c "import openai; print('OpenAI available')"
python -c "import anthropic; print('Anthropic available')"
```

#### Audio Analysis Errors
```bash
# Check file format
file test_audio/high_quality.wav

# Verify scipy/numpy
python -c "import numpy, scipy.io.wavfile; print('Libraries available')"
```

#### Network Analysis Issues
```bash
# Check networkx
python -c "import networkx as nx; print(f'NetworkX {nx.__version__}')"
```

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug logging for all tools
```

## 📚 API Reference

### AI Assistant Methods
- `chat(message, model="auto")` → Dict[str, Any]
- `analyze_code(code, language="python")` → Dict[str, Any]
- `generate_code(description, language="python")` → Dict[str, Any]
- `get_provider_info()` → Dict[str, Any]
- `clear_history()` → None

### Audio Analyzer Methods
- `analyze_808_bass(file_path=None)` → Dict[str, Any]
- `analyze_bass_vs_delay(file_path=None)` → Dict[str, Any]
- `analyze_sound_effects(effect_type="reverb")` → Dict[str, Any]
- `advanced_spectral_analysis(file_path=None)` → Dict[str, Any]

### Spatial Visualizer Methods
- `visualize_3d_spatial(source_pos, listener_pos, save_image=False)` → Dict[str, Any]
- `visualize_comprehensive()` → Dict[str, Any]

### Network Analyzer Methods
- `compute_centrality(G, method, normalized=True)` → Dict[Any, float]
- `detect_communities(G, method)` → List[List[Any]]
- `compute_statistics(G)` → Dict[str, Any]

---

## 🎯 Best Practices

1. **Always test in demo mode** before deploying with API keys
2. **Implement proper error handling** for API failures
3. **Cache expensive computations** to improve performance
4. **Monitor API usage** to stay within rate limits
5. **Keep licenses updated** and monitor for changes
6. **Document API key requirements** for deployment

The licensed advanced features provide powerful capabilities while maintaining system reliability through comprehensive fallback mechanisms.
