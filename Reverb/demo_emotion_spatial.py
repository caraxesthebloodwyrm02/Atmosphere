#!/usr/bin/env python3
"""
Demonstration of Emotion-Based Spatial Audio Processing

Shows how emotions create immersive 3D audio experiences with environmental depth.
"""

import math
from models.signal import AudioSignal, SpatialParameters
from services.spatial_service import SpatialAudioService, EmotionSpatializer


def create_test_signal(frequency: float = 440.0, duration: float = 1.0, sample_rate: int = 44100) -> AudioSignal:
    """Create a test sine wave signal."""
    num_samples = int(duration * sample_rate)
    data = []
    for i in range(num_samples):
        t = i / sample_rate
        sample = 0.5 * math.sin(2 * math.pi * frequency * t)
        data.append(sample)

    return AudioSignal.create_mono(data=data, sample_rate=sample_rate)


def demonstrate_emotion_spatialization():
    """Demonstrate emotion-based spatial positioning."""
    print("🎭 Emotion-Based Spatial Audio Demonstration")
    print("=" * 50)

    service = SpatialAudioService()
    spatializer = EmotionSpatializer()

    # Create test signal
    signal = create_test_signal(frequency=440.0, duration=0.5)
    print("✓ Created test signal: 440Hz sine wave, 0.5s duration")
    # Demonstrate emotion positioning
    emotions = ['joyful', 'calm', 'tense', 'melancholic', 'aggressive', 'intimate', 'epic']

    print("\n🗺️ Emotion Spatial Positioning:")
    for emotion in emotions:
        position_data = spatializer.get_emotion_position(emotion)
        immersive = spatializer.calculate_immersive_position(emotion, 'small_room')

        print(f"• {emotion.capitalize()}: {position_data['description']}")
        print(f"  Position: {position_data['position']}, Spread: {position_data['spread']}")

    print("\n🎧 Processing Audio with Emotions:")
    for emotion in ['joyful', 'tense', 'calm']:
        spatialized = service.process_emotion_spatial(signal, emotion, 'small_room')
        metadata = spatialized.metadata

        print(f"• {emotion.capitalize()} processing: {metadata['spatial_description']}")
        print(f"  Stereo output: {spatialized.channels} channels, {len(spatialized.data[0])} samples")


def demonstrate_environmental_depth():
    """Demonstrate how environments affect spatial positioning."""
    print("\n🏛️ Environmental Depth Effects:")
    print("=" * 35)

    service = SpatialAudioService()
    spatializer = EmotionSpatializer()
    signal = create_test_signal(frequency=220.0, duration=0.3)

    environments = ['small_room', 'large_hall', 'cathedral', 'outdoor', 'forest', 'alley']

    for env in environments:
        # Process joyful emotion in different environments
        immersive = spatializer.calculate_immersive_position('joyful', env)
        spatialized = service.process_emotion_spatial(signal, 'joyful', env)

        print(f"• {env.replace('_', ' ').title()}: {immersive['description']}")
        print(f"  Scaled position: {tuple(round(coord, 2) for coord in immersive['position'])}")


def demonstrate_immersive_scene():
    """Demonstrate creating immersive 3D scenes."""
    print("\n🌟 Immersive Scene Creation:")
    print("=" * 30)

    service = SpatialAudioService()

    # Create multiple audio elements with emotional connotations
    audio_elements = {
        'joyful_strings': create_test_signal(660.0, 0.8),   # High strings
        'calm_piano': create_test_signal(261.6, 1.0),       # Middle C
        'tense_percussion': create_test_signal(440.0, 0.3),  # A440
        'epic_brass': create_test_signal(146.8, 0.6),       # D3
    }

    # Create immersive scene
    scene = service.create_immersive_scene(audio_elements)

    print("✓ Mixed emotional audio elements into 3D scene:")
    print(f"  Elements: {len(audio_elements)}")
    print(f"  Output: {scene.channels} channels, {len(scene.data[0])} samples")
    print(f"  Sample rate: {scene.sample_rate}Hz")

    # Show spatial metadata for each element
    print("\n  Spatial positioning per element:")
    for element_name, signal in audio_elements.items():
        emotion = element_name.split('_')[0]
        temp_spatialized = service.process_emotion_spatial(signal, emotion)
        desc = temp_spatialized.metadata['spatial_description']
        print(f"  • {element_name}: {desc}")


def demonstrate_technical_features():
    """Show technical features of the enhanced spatial system."""
    print("\n⚙️ Technical Features:")
    print("=" * 22)

    service = SpatialAudioService()

    # Show service status
    status = service.get_status()
    print("✓ Spatial Audio Service Status:")
    print(f"  Features: HRTF ({status['features']['hrtf']}), Doppler ({status['features']['doppler']})")
    print(f"  Emotion spatialization: {status['features']['emotion_spatialization']}")
    print(f"  Immersive scenes: {status['features']['immersive_scenes']}")
    print(f"  Available emotions: {status['emotion_positions']}")
    print(f"  Available environments: {status['environments']}")

    # Show emotion positions
    positions = service.get_emotion_positions()
    print("\n✓ Emotion Position Library:")
    for emotion, data in positions.items():
        pos = data['position']
        spread = data['spread']
        print(f"  • {emotion}: pos{pos}, spread{spread:.1f}")

    # Show environments
    environments = service.get_environments()
    print("\n✓ Environment Library:")
    for env, data in environments.items():
        size = data['size']
        rt60 = data['rt60']
        print(f"  • {env}: {size}m³, RT60={rt60:.1f}s")


if __name__ == "__main__":
    demonstrate_emotion_spatialization()
    demonstrate_environmental_depth()
    demonstrate_immersive_scene()
    demonstrate_technical_features()

    print("\n🎼 Emotion-Based Spatial Audio Complete")
    print("Audio now has emotional depth and environmental space!")
