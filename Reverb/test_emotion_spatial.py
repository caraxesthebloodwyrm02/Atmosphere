#!/usr/bin/env python3
"""
Tests for Emotion-Based Spatial Audio Processing
"""

import unittest
import math
from models.signal import AudioSignal, SpatialParameters
from services.spatial_service import SpatialAudioService, EmotionSpatializer


class TestEmotionSpatializer(unittest.TestCase):
    """Test emotion spatializer functionality."""

    def setUp(self):
        """Set up test environment."""
        self.spatializer = EmotionSpatializer()

    def test_emotion_positions_available(self):
        """Test that emotion positions are properly defined."""
        positions = self.spatializer.emotion_positions
        self.assertIn('joyful', positions)
        self.assertIn('calm', positions)
        self.assertIn('tense', positions)
        self.assertIn('melancholic', positions)
        self.assertIn('aggressive', positions)

    def test_get_emotion_position(self):
        """Test retrieving emotion position data."""
        joyful_data = self.spatializer.get_emotion_position('joyful')
        self.assertEqual(joyful_data['description'], 'uplifting, expansive presence')
        self.assertEqual(joyful_data['position'], (0, 2, 1))

    def test_environment_params(self):
        """Test environment parameter retrieval."""
        hall_data = self.spatializer.get_environment_params('large_hall')
        self.assertEqual(hall_data['size'], 500)
        self.assertEqual(hall_data['rt60'], 2.5)

    def test_calculate_immersive_position(self):
        """Test immersive position calculation with environment scaling."""
        immersive = self.spatializer.calculate_immersive_position('joyful', 'large_hall')

        self.assertIn('position', immersive)
        self.assertIn('spread', immersive)
        self.assertIn('environment', immersive)
        self.assertIn('description', immersive)

        # Position should be scaled for large hall
        scale_factor = math.sqrt(500) / 10  # ~7.07
        expected_pos = tuple(coord * scale_factor for coord in (0, 2, 1))
        self.assertEqual(immersive['position'], expected_pos)


class TestSpatialAudioService(unittest.TestCase):
    """Test enhanced spatial audio service."""

    def setUp(self):
        """Set up test environment."""
        self.service = SpatialAudioService()

    def test_emotion_spatial_processing(self):
        """Test emotion-based spatial processing."""
        # Create test signal
        signal = AudioSignal.create_mono(data=[0.5] * 1000, sample_rate=44100)

        # Process with emotion
        result = self.service.process_emotion_spatial(signal, 'joyful', 'small_room')

        # Check metadata was added
        self.assertIn('emotion', result.metadata)
        self.assertIn('environment', result.metadata)
        self.assertIn('spatial_description', result.metadata)
        self.assertEqual(result.metadata['emotion'], 'joyful')
        self.assertEqual(result.metadata['environment'], 'small_room')

        # Check it's stereo output
        self.assertEqual(result.channels, 2)

    def test_immersive_scene_creation(self):
        """Test creating immersive scenes from multiple audio elements."""
        # Create test signals
        signal1 = AudioSignal.create_mono(data=[0.3] * 500, sample_rate=44100)
        signal2 = AudioSignal.create_mono(data=[0.4] * 500, sample_rate=44100)

        audio_elements = {
            'joyful_melody': signal1,
            'calm_bass': signal2
        }

        # Create immersive scene
        scene = self.service.create_immersive_scene(audio_elements)

        # Check it's stereo
        self.assertEqual(scene.channels, 2)
        # Check length matches longest signal
        self.assertEqual(len(scene.data[0]), 500)

    def test_emotion_positions_access(self):
        """Test accessing emotion positions through service."""
        positions = self.service.get_emotion_positions()
        self.assertIsInstance(positions, dict)
        self.assertGreater(len(positions), 0)

    def test_environments_access(self):
        """Test accessing environments through service."""
        environments = self.service.get_environments()
        self.assertIsInstance(environments, dict)
        self.assertGreater(len(environments), 0)

    def test_status_includes_emotion_features(self):
        """Test that service status includes emotion spatialization features."""
        status = self.service.get_status()

        self.assertTrue(status['features']['emotion_spatialization'])
        self.assertTrue(status['features']['immersive_scenes'])
        self.assertIn('emotion_positions', status)
        self.assertIn('environments', status)

    def test_unknown_emotion_defaults_to_calm(self):
        """Test that unknown emotions default to calm positioning."""
        signal = AudioSignal.create_mono(data=[0.5] * 1000, sample_rate=44100)
        result = self.service.process_emotion_spatial(signal, 'unknown_emotion')

        # Should still work with calm defaults
        self.assertEqual(result.metadata['emotion'], 'unknown_emotion')
        self.assertEqual(result.channels, 2)


if __name__ == "__main__":
    unittest.main()
