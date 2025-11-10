# Atmosphere Audio

[![CI](https://github.com/caraxesthebloodwyrm02/Atmosphere/actions/workflows/ci.yml/badge.svg)](https://github.com/caraxesthebloodwyrm02/Atmosphere/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/caraxesthebloodwyrm02/Atmosphere/branch/main/graph/badge.svg?token=edb3e568-c331-4bf2-aca4-13b658d855b5)](https://codecov.io/gh/caraxesthebloodwyrm02/Atmosphere)
[![PyPI version](https://badge.fury.io/py/atmosphere-audio.svg)](https://badge.fury.io/py/atmosphere-audio)

A comprehensive audio processing and routing system for creating immersive audio experiences through advanced signal processing, spatial audio, and network routing. This system integrates multiple audio processing modules with intelligent cross-referencing and performance optimization.

## 🎵 Core Features

### Audio Processing Modules
- **🎛️ [Delay Module](./docs/delay/)**: Time-based audio processing with echo effects and AI trajectory optimization
- **🌊 [Echo Module](./docs/echo/)**: Signal reflection and feedback processing with knowledge graphs
- **🏛️ [Reverb Module](./docs/reverb/)**: Acoustic environment simulation with spatial audio processing
- **🛣️ [Routing Module](./docs/routing/)**: Network routing and acoustic topology modeling
- **⚙️ [Core Module](./docs/core/)**: Network presence detection and device discovery

### Advanced Capabilities
- **🔄 Cross-Module Integration**: Seamless interaction between audio processing components
- **📊 Performance Monitoring**: Real-time analytics and optimization insights
- **🛡️ Resilience Patterns**: Circuit breakers and fallback strategies for reliability
- **🎯 Selective Attention**: Intelligent signal filtering for optimal processing
- **📈 Quality Assessment**: Audio quality metrics and analysis tools

## 🚀 Installation

### Install from PyPI
```bash
pip install atmosphere-audio
```

### Install from source
```bash
git clone https://github.com/caraxesthebloodwyrm02/Atmosphere.git
cd Atmosphere
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## 📖 Usage

### Basic Usage

```python
# Import the package
import atmosphere_audio

# Import specific modules with cross-referencing support
from atmosphere_audio.delay import Delay
from atmosphere_audio.reverb import SpatialAudioVisualizer
from atmosphere_audio.routing import AcousticParameters, AcousticRoutingNetwork
from atmosphere_audio.core.network import NetworkPresence, DeviceInfo

# Create interconnected audio processing chain
delay = Delay(time_ms=500, feedback=0.3, level=0.5, dry_wet=0.4)
print(f"Delay time: {delay.time_ms}ms")

# Integrate with spatial audio processing (cross-reference: Reverb Module)
visualizer = SpatialAudioVisualizer()
signal, t = visualizer.generate_signal(frequency=440, duration=1.0)

# Connect to acoustic routing network (cross-reference: Routing Module)
params = AcousticParameters(
    delay_time=100,
    feedback=0.5,
    decay=0.3,
    reverb_density=0.7
)

# Initialize network presence detection (cross-reference: Core Module)
presence = NetworkPresence(device_id="my_device")
```

### Advanced Integration Example

```python
# Comprehensive audio processing pipeline with cross-module references
from atmosphere_audio.delay import Delay
from atmosphere_audio.echo import EchoProcessor  # Cross-reference: Echo Module
from atmosphere_audio.reverb import ReverbPlatform  # Cross-reference: Reverb Module
from atmosphere_audio.routing import AcousticRoutingNetwork  # Cross-reference: Routing Module

class AtmosphereAudioPipeline:
    \"\"\"Complete audio processing pipeline with cross-module integration\"\"\"

    def __init__(self):
        # Initialize all modules with cross-references
        self.delay = Delay()  # See: Delay Module documentation
        self.echo = EchoProcessor()  # See: Echo Module documentation
        self.reverb = ReverbPlatform()  # See: Reverb Module documentation
        self.routing = AcousticRoutingNetwork()  # See: Routing Module documentation

    def process_audio(self, audio_signal):
        \"\"\"Process audio through complete pipeline with cross-module optimization\"\"\"
        # Stage 1: Delay processing (cross-reference: Delay → Echo integration)
        delayed = self.delay.process(audio_signal)

        # Stage 2: Echo enhancement (cross-reference: Echo → Reverb integration)
        echoed = self.echo.enhance(delayed)

        # Stage 3: Spatial processing (cross-reference: Reverb → Routing integration)
        spatial = self.reverb.spatialize_signal(echoed)

        # Stage 4: Network routing (cross-reference: Routing → Core integration)
        routed = self.routing.route_audio(spatial)

        return routed

# Usage with performance monitoring
pipeline = AtmosphereAudioPipeline()
processed_audio = pipeline.process_audio(input_signal)
```

### Command Line Interface

```bash
# Show version
atmosphere --version

# Show help
atmosphere --help

# Run audio quality analysis (cross-reference: Audio Analysis Tools)
atmosphere analyze --input audio_file.wav --output report.html

# Monitor system performance (cross-reference: Performance Monitoring)
atmosphere monitor --metrics cpu,memory,latency
```

## 📦 Enhanced Package Structure

```
atmosphere_audio/
├── __init__.py                 # Main package initialization
├── cli.py                      # Enhanced CLI with cross-module commands
├── delay/                      # Time-based audio effects
│   ├── __init__.py            # Cross-references to Echo Module
│   └── core/
│       ├── delay_essence.py   # Core delay algorithms
│       ├── echoes_essence.py  # Cross-reference: Echo Module
│       └── knowledge_graph.py # AI trajectory optimization
├── echo/                       # Echo and feedback processing
│   ├── __init__.py            # Cross-references to Delay/Reverb
│   └── core/                  # Echo algorithms with knowledge graphs
├── reverb/                     # Reverb and spatial audio
│   ├── __init__.py            # Cross-references to Routing Module
│   └── core/
│       ├── spatial_audio_visualizer.py
│       └── platform.py        # Spatial processing platform
├── routing/                    # Network routing
│   ├── __init__.py            # Cross-references to Core Module
│   └── core/
│       ├── network.py         # Network algorithms
│       └── visualization.py   # Routing visualization
├── core/                       # Core functionality
│   ├── __init__.py            # Cross-references to all modules
│   ├── network.py             # Network presence detection
│   ├── network_integration.py # Cross-module integration
│   └── security.py            # Security and authentication
├── analysis/                   # Audio quality analysis tools
│   ├── __init__.py            # Quality assessment utilities
│   ├── quality_metrics.py     # Audio quality scoring
│   └── reporting.py           # HTML/PDF report generation
└── monitoring/                 # Performance monitoring
    ├── __init__.py            # System monitoring tools
    ├── metrics.py             # Performance metrics collection
    └── dashboard.py           # Real-time monitoring dashboard
```

## 🔄 Cross-Module Integration

### Module Interdependencies

| Source Module | Target Module | Integration Type | Reference |
|---------------|---------------|------------------|-----------|
| **Delay** | Echo | Signal chaining | [Delay→Echo Integration](./docs/integration/delay_echo.md) |
| **Delay** | Reverb | Temporal-spatial processing | [Delay→Reverb Integration](./docs/integration/delay_reverb.md) |
| **Echo** | Routing | Feedback routing | [Echo→Routing Integration](./docs/integration/echo_routing.md) |
| **Reverb** | Routing | Spatial-acoustic mapping | [Reverb→Routing Integration](./docs/integration/reverb_routing.md) |
| **Routing** | Core | Network presence | [Routing→Core Integration](./docs/integration/routing_core.md) |
| **Core** | All Modules | Authentication & monitoring | [Core Integration](./docs/integration/core_modules.md) |

### Integration Patterns

#### 1. Signal Processing Chain
```python
# Cross-reference: Complete Processing Pipeline
# See also: Delay Module, Echo Module, Reverb Module, Routing Module
audio_chain = (
    Delay() >>          # Time-based processing
    EchoProcessor() >>  # Feedback enhancement
    ReverbPlatform() >> # Spatial processing
    RoutingNetwork()    # Network distribution
)
```

#### 2. Quality Monitoring Integration
```python
# Cross-reference: Audio Quality Assessment
# See also: Analysis Module, Monitoring Module
from atmosphere_audio.analysis import QualityAnalyzer
from atmosphere_audio.monitoring import PerformanceMonitor

analyzer = QualityAnalyzer()
monitor = PerformanceMonitor()

# Integrated quality monitoring
quality_report = analyzer.analyze_with_monitoring(
    audio_signal,
    monitor=monitor,
    metrics=['snr', 'thd', 'frequency_response']
)
```

#### 3. Network-Aware Processing
```python
# Cross-reference: Network Integration
# See also: Core Module, Routing Module
from atmosphere_audio.core import NetworkPresence
from atmosphere_audio.routing import AcousticRoutingNetwork

# Network-aware audio processing
presence = NetworkPresence()
routing = AcousticRoutingNetwork()

# Adaptive processing based on network conditions
network_status = presence.get_status()
routing_config = routing.optimize_for_network(network_status)
```

## 🎯 Advanced Features

### Intelligent Audio Processing
- **Selective Attention**: Automatic signal prioritization using AI algorithms
- **Adaptive Processing**: Dynamic parameter adjustment based on audio characteristics
- **Quality Optimization**: Real-time quality assessment and enhancement
- **Network Resilience**: Automatic failover and load balancing

### Performance Optimization
- **Circuit Breakers**: Prevent cascade failures in audio processing chains
- **Fallback Strategies**: Graceful degradation during system stress
- **Resource Monitoring**: Real-time CPU, memory, and I/O tracking
- **Performance Analytics**: Historical analysis and trend prediction

### Developer Experience
- **Cross-Referenced Documentation**: Intelligent linking between related concepts
- **Interactive Examples**: Executable code samples with live validation
- **Performance Profiling**: Built-in benchmarking and optimization tools
- **API Discovery**: Intelligent module and function recommendations

## 🧪 Testing & Quality Assurance

Run the comprehensive test suite with cross-module integration testing:

```bash
pytest
```

Run with coverage and cross-reference validation:

```bash
pytest --cov=src --cov-report=html --cov-fail-under=80
```

### Quality Metrics
- **Overall Target**: 80% minimum code coverage
- **Cross-Reference Validation**: All documentation links verified
- **Integration Testing**: Module interdependencies tested
- **Performance Benchmarking**: Audio processing latency monitored

## 📚 Documentation & Cross-References

### 📖 Primary Documentation
- **[API Reference](./docs/API.md)**: Complete API documentation with cross-references
- **[Integration Guide](./docs/integration/)**: Cross-module integration patterns
- **[Performance Guide](./GUIDEBOOK.md)**: Optimization and resilience patterns
- **[Audio Analysis](./docs/analysis/)**: Quality assessment and reporting tools

### 🔗 Cross-Reference Examples

#### 1. Delay Module References
```
📍 Current: Delay Module → Echo Enhancement
   See also: [Echo Module](./docs/echo/), [Signal Chaining](./docs/integration/delay_echo.md)

📍 Current: Delay Module → Reverb Integration
   See also: [Reverb Module](./docs/reverb/), [Temporal Processing](./docs/integration/delay_reverb.md)

📍 Current: Delay Module → Quality Analysis
   See also: [Analysis Module](./docs/analysis/), [Quality Metrics](./docs/analysis/quality_metrics.md)
```

#### 2. Reverb Module References
```
📍 Current: Reverb Module → Spatial Processing
   See also: [Routing Module](./docs/routing/), [3D Audio](./docs/integration/reverb_routing.md)

📍 Current: Reverb Module → Performance Monitoring
   See also: [Monitoring Module](./monitoring/), [Spatial Metrics](./docs/monitoring/spatial_metrics.md)
```

#### 3. Routing Module References
```
📍 Current: Routing Module → Network Integration
   See also: [Core Module](./docs/core/), [Presence Detection](./docs/integration/routing_core.md)

📍 Current: Routing Module → Quality Assurance
   See also: [Analysis Module](./docs/analysis/), [Network Quality](./docs/analysis/network_quality.md)
```

#### 4. Core Module References
```
📍 Current: Core Module → System Monitoring
   See also: [Monitoring Module](./monitoring/), [Health Checks](./docs/monitoring/health_checks.md)

📍 Current: Core Module → Security Integration
   See also: [Security Module](./docs/security/), [Authentication](./docs/security/auth_patterns.md)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original audio processing algorithms and research
- Network routing and acoustic modeling implementations
- Spatial audio and 3D processing research community
- Open source audio processing ecosystem
- Cross-referencing and documentation optimization techniques
