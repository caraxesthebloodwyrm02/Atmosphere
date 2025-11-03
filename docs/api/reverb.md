# Reverb Module API

## Overview

The Reverb module provides acoustic environment simulation with spatial audio processing, implementing a complete effects chain from input to binaural output.

## Classes

### ReverbPlatform

Main platform for processing audio through the complete effects chain: Input → Delay → Echo → Reverb → Spatial → Output.

#### Constructor

```python
ReverbPlatform(
    delay_params=None,
    echo_params=None,
    reverb_params=None,
    spatial_params=None
)
```

#### Parameters

- `delay_params` (DelayParameters): Delay effect parameters
- `echo_params` (EchoParameters): Echo effect parameters
- `reverb_params` (ReverbParameters): Reverb effect parameters
- `spatial_params` (SpatialParameters): Spatial audio parameters

#### Methods

- `get_system_status()`: Get status of all services in the platform
- `process_signal(signal)`: Process through complete effects chain
- `process_with_custom_params(signal, **params)`: Process with custom parameters
- `spatialize_signal(signal, source_pos, listener_pos, velocity)`: Apply 3D spatialization
- `apply_reverb_preset(preset_name)`: Apply reverb preset
- `get_available_presets()`: Get list of available presets
- `process_with_preset(signal, preset_name)`: Process using specific preset

### AudioSignal

Represents an audio signal with metadata.

#### Constructor

```python
AudioSignal(
    data,
    sample_rate=44100,
    channels=2,
    bit_depth=16
)
```

#### Attributes

- `data`: Audio data array
- `sample_rate`: Sample rate in Hz
- `channels`: Number of channels
- `bit_depth`: Bit depth
- `duration`: Duration in seconds (computed)

### SpatialParameters

Parameters for 3D spatial audio processing.

#### Constructor

```python
SpatialParameters(
    source_position=(1, 0, 0),
    listener_position=(0, 0, 0),
    listener_orientation=(0, 0, 1),
    room_dimensions=(10, 10, 3),
    wall_reflectivity=0.7
)
```

## Services

### DelayService

Provides delay effect processing functionality.

### EchoService

Provides echo effect processing functionality.

### ReverbService

Provides advanced reverb processing with algorithmic reverb implementation.

### SpatialAudioService

Provides 3D spatial audio processing including HRTF and binaural rendering.

## Usage Examples

```python
from reverb import ReverbPlatform, AudioSignal

# Create platform
reverb = ReverbPlatform()

# Get system status
status = reverb.get_system_status()
print(f"Platform status: {status['status']}")

# Process audio signal
audio = AudioSignal(data, sample_rate=44100)
processed = reverb.process_signal(audio)

# Apply spatial audio
spatial = reverb.spatialize_signal(
    processed,
    source_pos=(2, 1, 0),
    listener_pos=(0, 0, 0),
    velocity=(0, 0, 0)
)

# Use preset
reverb.apply_reverb_preset("hall")
```
