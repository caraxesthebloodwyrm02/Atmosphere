# Delay Module API

## Overview

The Delay module provides time-based audio processing capabilities including echo effects, feedback processing, and AI trajectory optimization.

## Classes

### Delay

Advanced audio delay effect with comprehensive parameters for AI trajectory optimization.

#### Constructor

```python
Delay(
    time_ms=250,
    feedback=0.3,
    level=0.5,
    dry_wet=0.5,
    delay_type='digital',
    rate=None,
    pre_delay=0,
    filter_type=None,
    filter_freq=1000,
    modulation=0,
    persistent_theme=None
)
```

#### Parameters

- `time_ms` (float): Delay time in milliseconds (0-2000ms typical)
- `feedback` (float): Fraction of delayed signal fed back (0-1)
- `level` (float): Amplitude of delayed signal (0-1)
- `dry_wet` (float): Mix balance (0=all dry, 1=all wet)
- `delay_type` (str): Effect type ('digital', 'analog', 'tape', 'ping_pong', 'slapback', 'doubling', 'multi_tap')
- `rate` (str): Tempo-synced rate ('1/1', '1/2', '1/4', etc.)
- `pre_delay` (float): Time before first echo in milliseconds
- `filter_type` (str): Filter on feedback ('lowpass', 'highpass', 'bandpass')
- `filter_freq` (float): Filter cutoff frequency in Hz
- `modulation` (float): Modulation depth for chorus-like effects (0-1)
- `persistent_theme` (str): Thematic fixation inspired by Claude's Golden Gate Bridge obsession

#### Methods

- `process(signal)`: Apply delay effect to audio signal
- `set_parameters(**kwargs)`: Update delay parameters
- `reset()`: Reset delay line state

### EchoesPlatform

Simplified representation of Echoes architecture for AI orchestration.

#### Constructor

```python
EchoesPlatform()
```

#### Methods

- `process_input(query)`: Process through effects chain
- `_apply_delay(query)`: Apply delay processing
- `_apply_echo(delayed)`: Apply echo processing
- `_apply_reverb(echoed)`: Apply reverb processing
- `_apply_master_controls(reverberated)`: Apply final processing

## Usage Examples

```python
from delay import Delay, EchoesPlatform

# Create delay effect
delay = Delay(time_ms=500, feedback=0.4, level=0.6)
processed_audio = delay.process(audio_signal)

# Use Echoes platform
platform = EchoesPlatform()
result = platform.process_input("user query")
```
