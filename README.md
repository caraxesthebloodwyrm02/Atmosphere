# Atmosphere

[![CI](https://github.com/caraxesthebloodwyrm02/Atmosphere/actions/workflows/ci.yml/badge.svg)](https://github.com/caraxesthebloodwyrm02/Atmosphere/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/caraxesthebloodwyrm02/Atmosphere/branch/main/graph/badge.svg)](https://codecov.io/gh/caraxesthebloodwyrm02/Atmosphere)

A comprehensive audio processing and routing system for creating immersive audio experiences through advanced signal processing, spatial audio, and network routing.

## 🎵 Features

- **Delay Module**: Time-based audio processing with echo effects and AI trajectory optimization
- **Echo Module**: Signal reflection and feedback processing with knowledge graphs
- **Reverb Module**: Acoustic environment simulation with spatial audio processing
- **Routing Module**: Network routing and acoustic topology modeling

## 🚀 Installation

### Prerequisites
- Python 3.8+
- pip

### Install from source
```bash
git clone https://github.com/yourusername/atmosphere.git
cd atmosphere
pip install -e .
```

### Development Installation
```bash
pip install -e ".[dev]"
```

## 📖 Usage

### Basic Usage

```python
# Import modules
from delay import Delay, EchoesPlatform
from reverb import ReverbPlatform
from routing import AcousticRoutingNetwork

# Create instances
delay = Delay(time_ms=500, feedback=0.3)
reverb = ReverbPlatform()
network = AcousticRoutingNetwork()

# Use functionality
delayed_signal = delay.process(audio_signal)
reverberated = reverb.process_signal(audio_signal)
network.add_highway_segment("A", "B", distance_miles=10)
```

### Delay Module

```python
from delay import Delay

# Create delay effect
delay = Delay(
    time_ms=300,      # Delay time in milliseconds
    feedback=0.4,     # Feedback amount (0-1)
    level=0.6,        # Echo volume (0-1)
    dry_wet=0.5       # Mix balance (0-1)
)

# Apply to audio signal
processed_audio = delay.process(audio_signal)
```

### Reverb Module

```python
from reverb import ReverbPlatform

# Create reverb processor
reverb = ReverbPlatform()

# Process audio with spatial effects
spatial_audio = reverb.spatialize_signal(
    audio_signal,
    source_pos=(1, 0, 0),      # Source position (x, y, z)
    listener_pos=(0, 0, 0),    # Listener position
    velocity=(0, 0, 0)         # Source velocity
)

# Apply reverb preset
hall_reverb = reverb.apply_reverb_preset("hall")
```

### Routing Module

```python
from routing import AcousticRoutingNetwork

# Create acoustic routing network
network = AcousticRoutingNetwork()

# Add network segments with acoustic properties
network.add_highway_segment(
    start="CityA",
    end="CityB",
    distance_miles=50,
    speed_limit_mph=70,
    interconnectivity=0.3
)

# Find optimal acoustic route
route = network.find_optimal_route("CityA", "CityC")
```

## 🏗️ Architecture

### Module Structure

```
src/
├── delay/              # Time-based audio effects
│   ├── core/           # Core delay algorithms
│   ├── api/            # REST API endpoints
│   └── models/         # Data models
├── echo/               # Echo and feedback processing
│   ├── core/           # Echo algorithms
│   ├── api/            # API endpoints
│   └── models/         # Data models
├── reverb/             # Reverb and spatial audio
│   ├── core/           # Reverb algorithms
│   ├── api/            # API endpoints
│   ├── models/         # Signal models
│   └── services/       # Processing services
└── routing/            # Network routing
    ├── acoustic_routing/ # Routing algorithms
    ├── api/            # API endpoints
    ├── core/           # Core routing logic
    └── models/         # Network models
```

### Audio Processing Chain

```
Input → Delay → Echo → Reverb → Spatial → Output
```

## 🧪 Testing

Run the test suite:

```bash
pytest
```

Run with coverage (requires 80% minimum coverage):

```bash
pytest --cov=src --cov-report=html --cov-fail-under=80
```

View coverage report in `htmlcov/index.html`.

### Coverage Requirements
- **Overall Target**: 80% minimum code coverage
- **Source Files**: Only `src/` directory tracked
- **Exclusions**: Test files, generated code, and boilerplate
- **CI Enforcement**: Builds fail if coverage drops below 80%

## 📚 API Documentation

### Delay Module

#### `Delay` Class
Advanced audio delay effect with comprehensive parameters.

**Parameters:**
- `time_ms` (float): Delay time in milliseconds (default: 250)
- `feedback` (float): Feedback amount 0-1 (default: 0.3)
- `level` (float): Echo volume 0-1 (default: 0.5)
- `dry_wet` (float): Mix balance 0-1 (default: 0.5)

### Reverb Module

#### `ReverbPlatform` Class
Main platform for processing audio through complete effects chain.

**Methods:**
- `process_signal(signal)`: Process through full effects chain
- `spatialize_signal(signal, source_pos, listener_pos, velocity)`: Apply 3D spatialization
- `apply_reverb_preset(preset_name)`: Apply preset ("hall", "room", "plate")

### Routing Module

#### `AcousticRoutingNetwork` Class
Network modeling with acoustic properties.

**Methods:**
- `add_highway_segment(start, end, distance, speed_limit, interconnectivity)`
- `find_optimal_route(start, end)`
- `visualize_network(save_path=None)`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Original audio processing algorithms
- Network routing implementations
- Spatial audio research community
