"""Tests for atmosphere_audio.reverb.core.spatial_audio_visualizer module."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
from atmosphere_audio.reverb.core.spatial_audio_visualizer import SpatialAudioVisualizer, logger


class TestSpatialAudioVisualizer:
    """Test the spatial audio visualizer."""

    def test_spatial_audio_visualizer_init(self):
        """Test SpatialAudioVisualizer initialization."""
        visualizer = SpatialAudioVisualizer()
        assert visualizer.sample_rate == 44100
        assert visualizer.sound_speed == 343

    def test_generate_signal(self):
        """Test signal generation."""
        visualizer = SpatialAudioVisualizer()
        signal, t = visualizer.generate_signal(frequency=440, duration=0.1)

        # Check signal properties
        assert len(signal) == len(t)
        assert len(signal) == int(0.1 * 44100)  # duration * sample_rate

        # Check signal is roughly sinusoidal (basic check)
        assert np.mean(signal) < 0.1  # Should be close to zero mean
        assert np.std(signal) > 0.5   # Should have reasonable amplitude

    @patch('atmosphere_audio.reverb.core.spatial_audio_visualizer.plt')
    def test_visualize_doppler_effect(self, mock_plt):
        """Test Doppler effect visualization."""
        # Mock matplotlib
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())
        mock_plt.figure.return_value = MagicMock()

        visualizer = SpatialAudioVisualizer()
        
        # This should not raise an exception
        visualizer.demonstrate_doppler()

    @patch('atmosphere_audio.reverb.core.spatial_audio_visualizer.plt')
    def test_visualize_distance_attenuation(self, mock_plt):
        """Test distance attenuation visualization."""
        # Mock matplotlib
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())

        visualizer = SpatialAudioVisualizer()
        
        # This should not raise an exception
        visualizer.demonstrate_distance()

    @patch('atmosphere_audio.reverb.core.spatial_audio_visualizer.plt')
    def test_visualize_hrtf_processing(self, mock_plt):
        """Test HRTF processing visualization."""
        # Mock matplotlib
        mock_plt.subplots.return_value = (MagicMock(), MagicMock())

        visualizer = SpatialAudioVisualizer()
        
        # This should not raise an exception
        visualizer.demonstrate_hrtf()

    def test_apply_doppler(self):
        """Test Doppler effect application."""
        visualizer = SpatialAudioVisualizer()
        signal, t = visualizer.generate_signal(duration=0.1)

        # Apply Doppler effect (returns tuple)
        result = visualizer.apply_doppler(signal, velocity=10.0, t=t)
        doppler_signal, doppler_factor = result

        # Signal should be modified
        assert len(doppler_signal) == len(signal)
        assert not np.array_equal(doppler_signal, signal)  # Should be different
        assert isinstance(doppler_factor, float)
        assert doppler_factor > 1.0  # Should be greater than 1 for positive velocity

    def test_distance_attenuation(self):
        """Test distance attenuation."""
        visualizer = SpatialAudioVisualizer()
        signal, t = visualizer.generate_signal(duration=0.1)

        # Apply distance attenuation
        attenuated = visualizer.apply_distance_attenuation(signal, distance=5.0)

        # Signal should be attenuated (smaller amplitude)
        assert len(attenuated) == len(signal)
        assert np.max(np.abs(attenuated)) < np.max(np.abs(signal))

    def test_logger_configuration(self):
        """Test that logger is properly configured."""
        assert logger is not None
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
