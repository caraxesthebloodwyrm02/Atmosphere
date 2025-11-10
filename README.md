# Atmosphere Audio & Learning System

[![CI](https://github.com/caraxesthebloodwyrm02/Atmosphere/actions/workflows/ci.yml/badge.svg)](https://github.com/caraxesthebloodwyrm02/Atmosphere/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/caraxesthebloodwyrm02/Atmosphere/branch/main/graph/badge.svg?token=edb3e568-c331-4bf2-aca4-13b658d855b5)](https://codecov.io/gh/caraxesthebloodwyrm02/Atmosphere)

A comprehensive audio processing, routing system, and emotionally-adaptive learning companion for creating immersive audio experiences and educational interactions through advanced signal processing, spatial audio, network routing, and AI-powered learning.

## Core Features

### Audio Processing Modules
- **Delay Module**: Time-based audio processing with echo effects and AI trajectory optimization
- **Echo Module**: Signal reflection and feedback processing with knowledge graphs
- **Reverb Module**: Acoustic environment simulation with spatial audio processing
- **Routing Module**: Network routing and acoustic topology modeling
- **Core Module**: Network presence detection and device discovery

### Arcade Terminal & Learning Companion
- **Arcade Terminal**: Retro-style terminal entertainment space with WebSocket communication
- **Emotionally-Adaptive Learning Companion**: AI-powered educational assistant with real-time emotional detection
- **Adaptive Content Delivery**: 5 content types with emotion-based routing (Interactive, Explanatory, Project-based, Assessment, Mindfulness)
- **Intervention System**: 4 automated support mechanisms (Stress relief, Engagement boost, Confusion support, Frustration relief)
- **Progress Analytics**: Real-time skill tracking and behavioral insights

### Advanced Capabilities
- **Cross-Module Integration**: Seamless interaction between audio processing components
- **Performance Monitoring**: Real-time analytics and optimization insights
- **Resilience Patterns**: Circuit breakers and fallback strategies for reliability
- **Selective Attention**: Intelligent signal filtering for optimal processing
- **Quality Assessment**: Audio quality metrics and analysis tools
- **WebSocket Terminal**: Real-time terminal access through modern web interfaces

## Quick Start

### Automated Setup
```bash
# Run the complete setup script
python setup_atmosphere.py
```

### Manual Installation
```bash
# Clone the repository
git clone https://github.com/caraxesthebloodwyrm02/Atmosphere.git
cd Atmosphere

# Install core dependencies
pip install -r config/requirements.txt

# Install development tools (optional)
pip install -r config/requirements.txt -r config/requirements-dev.txt

# Validate configuration
python validate_config.py
```

### Start the System
```bash
# Start the Arcade Terminal & Learning Companion server
python Arcade/api/server.py

# Test the API
python api_test_quick.py

# Access the web interface
# http://localhost:7681
```

## Usage

### Learning Companion API

```python
import httpx
import asyncio

async def use_learning_companion():
    async with httpx.AsyncClient() as client:
        # Start a learning session
        response = await client.post(
            'http://localhost:7681/learning/session/start',
            params={
                'learner_id': 'student_123',
                'topic': 'python_functions'
            }
        )

        session_data = response.json()
        session_id = session_data['data']['session_id']

        # Process learning interactions
        await client.post(
            'http://localhost:7681/learning/session/interact',
            json={
                'session_id': session_id,
                'interaction_type': 'correct_answer',
                'interaction_data': {
                    'response_time': 1.2,
                    'confidence': 0.85
                }
            }
        )

        # Get progress analytics
        progress = await client.get(
            f'http://localhost:7681/learning/progress/student_123'
        )

        print(f"Mastery level: {progress.json()['data']['overall_mastery']:.1%}")

asyncio.run(use_learning_companion())
```

### Audio Processing

```python
# Import audio processing modules
from atmosphere_audio.delay import Delay
from atmosphere_audio.reverb import ReverbPlatform
from atmosphere_audio.routing import AcousticRoutingNetwork

# Create processing chain
delay = Delay(time_ms=300, feedback=0.4, level=0.6)
reverb = ReverbPlatform()
routing = AcousticRoutingNetwork()

# Process audio signal
processed = delay.process(audio_signal)
spatialized = reverb.spatialize_signal(processed)
routed = routing.route_audio(spatialized)
```

### Arcade Terminal

```python
# Connect via WebSocket
import websockets
import asyncio

async def terminal_session():
    async with websockets.connect('ws://localhost:7681/arcade/ws') as ws:
        # Send commands
        await ws.send('{"type": "command", "command": "ls"}')

        # Receive responses
        response = await ws.recv()
        print(f"Terminal output: {response}")

asyncio.run(terminal_session())
```

## Project Structure

```
Atmosphere/
├── Arcade/                    # Terminal & Learning System
│   ├── api/
│   │   ├── server.py          # FastAPI server with WebSocket
│   │   ├── learning_companion_api.py  # AI learning endpoints
│   │   └── terminal_handler.py # Terminal session management
│   └── learning_companion/    # Adaptive learning features
│       ├── emotional_detection.py
│       ├── content_adaptation.py
│       └── intervention_system.py
├── Delay/                     # Time-based audio effects
├── Echoes/                    # Signal reflection processing
├── Reverb/                    # Spatial audio processing
├── Routing/                   # Acoustic network routing
├── config/                    # Configuration files
│   ├── requirements.txt       # Core dependencies
│   ├── requirements-dev.txt   # Development tools
│   ├── pyproject.toml         # Project configuration
│   └── .pylintrc             # Linting rules
├── src/atmosphere_audio/      # Main package
├── docs/                      # Documentation
├── automation/                # Automation scripts
├── data/                      # Data files
├── temp/                      # Temporary files
├── setup_atmosphere.py        # Setup script
├── validate_config.py         # Configuration validator
└── api_test_quick.py          # API testing
```

## Arcade Terminal Features

### Web-Based Terminal
- **Retro Interface**: Classic terminal styling with modern WebSocket communication
- **Multi-Session**: Concurrent terminal sessions with isolated sandboxes
- **Command History**: Persistent command history and auto-completion
- **File System**: Virtual file system with persistent storage

### Learning Companion Integration
- **Emotional Detection**: Real-time analysis of learner emotional state
- **Adaptive Content**: Dynamic content selection based on emotional feedback
- **Progress Tracking**: Comprehensive skill mastery analytics
- **Intervention Support**: Automated assistance for learning difficulties

## Learning Companion Capabilities

### Emotional Intelligence
- **8 Emotional States**: Exploratory, Creative, Analytical, Urgent, Calm, Frustrated, Confused, Engaged
- **Real-Time Detection**: Continuous emotional state monitoring
- **Behavioral Analysis**: Pattern recognition in learning interactions

### Content Adaptation
- **5 Content Types**:
  - **Interactive Exercises**: Hands-on coding challenges
  - **Explanatory Content**: Concept explanations with examples
  - **Project-Based Learning**: Real-world application scenarios
  - **Assessments**: Knowledge verification and progress checks
  - **Mindfulness**: Stress reduction and focus enhancement

### Intervention System
- **4 Support Mechanisms**:
  - **Stress Relief**: Breathing exercises and calming content
  - **Engagement Boost**: Interactive elements and gamification
  - **Confusion Support**: Simplified explanations and visual aids
  - **Frustration Relief**: Encouragement and alternative approaches

### Analytics & Insights
- **Progress Tracking**: Skill mastery levels and learning velocity
- **Behavioral Patterns**: Study habits and interaction preferences
- **Recommendations**: Personalized learning path suggestions

## Development

### Configuration Validation
```bash
# Run configuration validation
python validate_config.py
```

### Code Quality
```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Run tests
pytest --cov=src --cov-report=html
```

### API Testing
```bash
# Test learning companion API
python api_test_quick.py

# Test specific endpoints
curl http://localhost:7681/learning/status
```

## Testing & Quality Assurance

### Test Suite
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-fail-under=80

# Run specific test categories
pytest -m "api"        # API tests only
pytest -m "slow"       # Performance tests
pytest -m "integration" # Cross-module tests
```

### Configuration Validation
```bash
# Validate all configuration files
python validate_config.py

# Check package compatibility
python -c "import atmosphere_audio; print('✅ Package imports successful')"
```

## Documentation

### API Documentation
- **[Learning Companion API](./Arcade/API.md)**: Complete REST API reference
- **[Terminal API](./Arcade/README.md)**: WebSocket communication protocols
- **[Audio Processing API](./docs/API.md)**: Core audio processing interfaces

### Integration Guides
- **[Delay-Echo Integration](./docs/integration/delay_echo.md)**: Signal chaining patterns
- **[Reverb-Routing Integration](./docs/integration/reverb_routing.md)**: Spatial-acoustic mapping
- **[Learning Companion Setup](./Arcade/README.md)**: Educational system configuration

### Technical Documentation
- **[Architecture Overview](./GUIDEBOOK.md)**: System design and patterns
- **[Performance Guide](./docs/COVERAGE.md)**: Optimization techniques
- **[Security Guide](./docs/Security Violation Remediation.md)**: Security best practices

## Contributing

1. **Setup Development Environment**
   ```bash
   git clone https://github.com/caraxesthebloodwyrm02/Atmosphere.git
   cd Atmosphere
   python setup_atmosphere.py
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development Workflow**
   ```bash
   # Make changes
   # Run tests
   pytest

   # Validate configuration
   python validate_config.py

   # Format code
   black . && isort .
   ```

4. **Submit Changes**
   ```bash
   git add .
   git commit -m "Add your feature description"
   git push origin feature/your-feature-name
   ```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Audio Processing Research**: Original algorithms and spatial audio techniques
- **Educational Technology**: Adaptive learning and emotional intelligence research
- **Open Source Community**: WebSocket, FastAPI, and Python ecosystem contributors
- **Terminal Interface Design**: Retro computing and modern web development inspiration

---

**Atmosphere**: Where audio processing meets emotionally-adaptive learning in a retro terminal experience. 🎵🤖🎮✨
