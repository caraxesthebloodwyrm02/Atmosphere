# API Documentation

## atmosphere_audio

The main package that provides access to all audio processing modules.

### Attributes

- **__version__** (str): The current version of the package

### Example

```python
import atmosphere_audio
print(atmosphere_audio.__version__)  # Output: 0.1.0
```

## atmosphere_audio.delay

### Delay

A class for creating delay effects with various parameters.

#### Parameters

- **time_ms** (float, optional): Delay time in milliseconds. Default: 250
- **feedback** (float, optional): Fraction of delayed signal fed back (0-1). Default: 0.3
- **level** (float, optional): Amplitude of delayed signal (0-1). Default: 0.5
- **dry_wet** (float, optional): Mix balance (0-1). Default: 0.5
- **delay_type** (str, optional): Effect type. Default: 'digital'
- **rate** (str, optional): Tempo-synced rate. Default: None
- **pre_delay** (float, optional): Time before first echo in milliseconds. Default: 0
- **filter_type** (str, optional): Filter on feedback. Default: None
- **filter_freq** (float, optional): Filter cutoff frequency in Hz. Default: 1000
- **modulation** (float, optional): Modulation depth (0-1). Default: 0
- **persistent_theme** (str, optional): Thematic fixation. Default: None

#### Methods

- **process**(signal): Apply delay effect to an audio signal

### Example

```python
from atmosphere_audio.delay import Delay

delay = Delay(time_ms=500, feedback=0.4, level=0.6)
# delay.process(audio_signal)
```

## atmosphere_audio.reverb

### SpatialAudioVisualizer

A class for visualizing spatial audio processing concepts.

#### Attributes

- **sample_rate** (int): Audio sample rate. Default: 44100
- **sound_speed** (int): Speed of sound in m/s. Default: 343

#### Methods

- **generate_signal**(frequency=440, duration=1.0): Generate a mono audio signal
- **apply_doppler**(signal, velocity, t): Apply Doppler effect
- **apply_distance_attenuation**(signal, distance): Apply inverse square law attenuation
- **apply_hrtf**(signal, azimuth_deg): Apply simplified HRTF processing
- **create_comprehensive_visualization**(): Create visualization of all effects
- **demonstrate_doppler**(): Demonstrate Doppler effect
- **demonstrate_distance**(): Demonstrate distance attenuation
- **demonstrate_hrtf**(): Demonstrate HRTF directional analysis

### Example

```python
from atmosphere_audio.reverb import SpatialAudioVisualizer

visualizer = SpatialAudioVisualizer()
signal, t = visualizer.generate_signal(frequency=440, duration=1.0)
```

## atmosphere_audio.routing

### AcousticParameters

Dataclass for acoustic properties of routing edges.

#### Fields

- **delay_time** (float): Travel time or physical distance in milliseconds
- **feedback** (float): Number of alternate routes/detours (0-1)
- **decay** (float): Traffic dissipation/energy loss (0-1)
- **reverb_density** (float): Local interconnectivity (0-1)

### AcousticRoutingNetwork

A class for modeling acoustic propagation through network topologies.

#### Methods

- **add_node**(node_id, **kwargs): Add a node to the network
- **add_edge**(source, target, acoustic_params): Add an edge with acoustic parameters
- **calculate_path**(source, target): Calculate optimal acoustic path
- **visualize_network**(): Visualize the network topology

### Example

```python
from atmosphere_audio.routing import AcousticParameters, AcousticRoutingNetwork

params = AcousticParameters(delay_time=100, feedback=0.5, decay=0.3, reverb_density=0.7)
network = AcousticRoutingNetwork()
network.add_node("room1")
network.add_node("room2")
network.add_edge("room1", "room2", params)
```

## atmosphere_audio.core.network

### DeviceInfo

Dataclass for device information in network presence.

#### Fields

- **address** (str): IP address of the device
- **port** (int): Port number
- **last_seen** (float): Timestamp when device was last seen
- **metadata** (Dict[str, Any]): Additional device information

### NetworkPresence

Handles network presence announcement and device discovery.

#### Parameters

- **device_id** (str): Unique identifier for this device
- **broadcast_port** (int, optional): UDP port for presence announcements. Default: 37020
- **presence_interval** (int, optional): How often to announce presence in seconds. Default: 30

#### Methods

- **start**(): Start the presence announcement and discovery service
- **stop**(): Stop the service
- **announce_presence**(): Send a presence announcement
- **discover_devices**(): Discover devices on the network
- **get_known_devices**(): Get list of known devices

### Example

```python
from atmosphere_audio.core.network import NetworkPresence, DeviceInfo
import time

presence = NetworkPresence(device_id="my_device")
presence.start()

# Device info structure
device = DeviceInfo(
    address="192.168.1.100",
    port=8080,
    last_seen=time.time(),
    metadata={"name": "My Device", "capabilities": ["delay", "reverb"]}
)
```

## atmosphere_audio.cli

Command-line interface for Atmosphere Audio.

### Commands

- **--version**: Show package version
- **--verbose**: Enable verbose output
- **--help**: Show help message

### Example

```bash
atmosphere --version
atmosphere --verbose
```
