# Delay Essence: Advanced Audio Effect with Emotion Analysis

**Tempo-synced delay with automated filter modulation, quantization, and emotional grounding**

## Features

### 🎼 Core Audio Processing
- **Tempo-Sync**: 1/1 through 1/32 rates + custom ratios (3/8, 3/16, etc.)
- **Filter Modulation**: Automated 240Hz filter with emotion-based adjustments
- **Quantization Grid**: 75% snap-to-grid timing for musical precision
- **Multiple Types**: Digital, Analog, Tape, Ping-Pong, Slapback, Doubling

### 🧠 Emotion-Based Processing
- **Emotional Grounding**: 5 emotion types (calm, tense, joyful, melancholic, aggressive)
- **Dynamic Modulation**: Emotion affects filter response and feedback
- **Tactile Feedback**: Simulated touch sensations based on audio emotion analysis

### 📊 Technical Specifications
- **Sample Rates**: All standard audio rates supported
- **Filter Range**: 20Hz - 20kHz with automated modulation
- **Feedback Control**: 0-100% with emotion-influenced decay
- **Quantization Strength**: Adjustable snap-to-grid (0-100%)

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Delay
```python
from delay_essence import Delay

# Simple tempo-synced delay
delay = Delay(rate='1/8', feedback=0.3, dry_wet=0.5)
result = delay.process_signal("Audio input")
```

### Emotion-Grounded Delay
```python
# Joyful delay with tactile feedback
joyful_delay = Delay(
    rate='1/16',
    emotion_type='joyful',
    tactile_feedback=True,
    filter_freq=240,
    filter_mod=0.6
)
result = joyful_delay.process_signal("Uplifting melody")
```

### Tense Suspense Effect
```python
# Tense delay for suspense scenes
tense_delay = Delay(
    delay_type='tape',
    rate='1/8',
    emotion_type='tense',
    tactile_feedback=True,
    filter_freq=180,
    filter_mod=0.8,
    dry_wet=0.7
)
result = tense_delay.process_signal("Suspenseful score")
```

## Emotion Types

| Emotion | Modulation Effect | Tactile Response |
|---------|------------------|------------------|
| **Calm** | -0.1 mod (softer) | Gentle vibration, soothing resonance |
| **Joyful** | +0.15 mod (brighter) | Warm waves, uplifting harmonics |
| **Tense** | +0.2 mod (sharper) | Sharp pulses, heightened sensitivity |
| **Melancholic** | -0.05 mod (deeper) | Deep bass thrum, introspective echo |
| **Aggressive** | +0.25 mod (intense) | Intense low-end, powerful impact |

## Testing

Run the test suite:
```bash
python -m pytest test_delay_emotion.py -v
```

## Demonstration

Run the emotion analysis demo:
```bash
python demo_delay_emotion.py
```

## Audio Logic Grounding

This implementation is grounded in VTEC Sound & Emotion Analysis principles:

- **Tactile Mapping**: Quantifies how sound waves create physical touch sensations
- **Emotional Intelligence**: Connects audio properties to human emotional responses
- **Scientific Rigor**: Combines physics, biology, and perception research
- **Enhanced Sound Design**: Provides emotionally-aware audio processing

## License

See LICENSE file in the project root.

## Contributing

1. Add emotion types or tactile responses to expand the analysis
2. Implement additional audio processing algorithms
3. Enhance quantization and timing precision
4. Add support for multi-channel processing
