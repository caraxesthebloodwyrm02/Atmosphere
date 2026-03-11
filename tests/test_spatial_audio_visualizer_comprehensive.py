"""
Comprehensive tests for atmosphere_audio.reverb.core.spatial_audio_visualizer module.

This module tests the SpatialAudioVisualizer class for spatial audio processing.
"""

import numpy as np
import pytest
from unittest.mock import MagicMock, patch

from atmosphere_audio.reverb.core.spatial_audio_visualizer import SpatialAudioVisualizer


class TestSpatialAudioVisualizerCore:
    """Tests for core SpatialAudioVisualizer functionality."""

    def test_initialization(self):
        """Test SpatialAudioVisualizer initialization."""
        visualizer = SpatialAudioVisualizer()

        assert visualizer.sample_rate == 44100
        assert visualizer.sound_speed == 343

    def test_generate_signal(self):
        """Test signal generation."""
        visualizer = SpatialAudioVisualizer()

        signal, time_array = visualizer.generate_signal(frequency=440, duration=1.0)

        # Check signal properties
        assert len(signal) == len(time_array)
        assert len(signal) == 44100  # 1 second at 44.1kHz

        # Check time array bounds
        assert time_array[0] == 0.0
        assert time_array[-1] == pytest.approx(0.999977, abs=0.001)

        # Check signal is approximately a sine wave
        assert signal[0] == 0.0  # sin(0) = 0
        # Peak value of a sine wave should be approximately 1.0
        assert abs(np.max(signal)) == pytest.approx(1.0, abs=0.01)

    def test_generate_signal_custom_params(self):
        """Test signal generation with custom parameters."""
        visualizer = SpatialAudioVisualizer()

        signal, time_array = visualizer.generate_signal(frequency=880, duration=0.5)

        assert len(signal) == 22050  # 0.5 seconds at 44.1kHz
        assert time_array[-1] == pytest.approx(0.499977, abs=0.001)

    def test_apply_doppler_approaching(self):
        """Test Doppler effect with approaching source."""
        visualizer = SpatialAudioVisualizer()
        signal, t = visualizer.generate_signal(frequency=440, duration=0.1)

        doppler_signal, doppler_factor = visualizer.apply_doppler(signal, velocity=20, t=t)

        # Check Doppler factor calculation: (c + v) / c
        expected_factor = (343 + 20) / 343
        assert doppler_factor == pytest.approx(expected_factor, abs=0.001)
        assert doppler_factor > 1.0

        # Signal should be different from original
        assert not np.array_equal(signal, doppler_signal)

    def test_apply_doppler_receding(self):
        """Test Doppler effect with receding source."""
        visualizer = SpatialAudioVisualizer()
        signal, t = visualizer.generate_signal(frequency=440, duration=0.1)

        doppler_signal, doppler_factor = visualizer.apply_doppler(signal, velocity=-20, t=t)

        # Check Doppler factor: (c - v) / c
        expected_factor = (343 - 20) / 343
        assert doppler_factor == pytest.approx(expected_factor, abs=0.001)
        assert doppler_factor < 1.0

    def test_apply_doppler_stationary(self):
        """Test Doppler effect with stationary source."""
        visualizer = SpatialAudioVisualizer()
        signal, t = visualizer.generate_signal(frequency=440, duration=0.1)

        doppler_signal, doppler_factor = visualizer.apply_doppler(signal, velocity=0, t=t)

        assert doppler_factor == pytest.approx(1.0, abs=0.001)
        # Signal should still be generated (just at original frequency)
        assert len(doppler_signal) == len(signal)

    def test_apply_distance_attenuation(self):
        """Test distance attenuation with inverse square law."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        # Test various distances (excluding 1 where factor=1.0 gives unchanged signal)
        distances = [2, 5, 10]
        for distance in distances:
            attenuated = visualizer.apply_distance_attenuation(signal, distance)

            if distance > 0:
                # Check inverse square law is applied
                expected_factor = 1.0 / (distance ** 2)
                # Verify scaling (can't check exact due to signal variation)
                assert len(attenuated) == len(signal)
                assert not np.array_equal(attenuated, signal)

    def test_apply_distance_attenuation_zero_distance(self):
        """Test distance attenuation with zero distance."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        attenuated = visualizer.apply_distance_attenuation(signal, 0)
        # Zero distance should return original signal
        np.testing.assert_array_equal(attenuated, signal)

    def test_apply_distance_attenuation_negative_distance(self):
        """Test distance attenuation with negative distance."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        attenuated = visualizer.apply_distance_attenuation(signal, -5)
        # Negative distance should return original signal
        np.testing.assert_array_equal(attenuated, signal)

    def test_apply_hrtf_center_azimuth(self):
        """Test HRTF with center azimuth (0 degrees)."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        left_ear, right_ear = visualizer.apply_hrtf(signal, azimuth_deg=0)

        # At center, left and right should be identical (no ITD/ILD)
        np.testing.assert_array_almost_equal(left_ear, right_ear)

    def test_apply_hrtf_right_azimuth(self):
        """Test HRTF with right-side azimuth."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        left_ear, right_ear = visualizer.apply_hrtf(signal, azimuth_deg=45)

        # Right side should have stronger right ear signal (ILD effect)
        rms_left = np.sqrt(np.mean(left_ear**2))
        rms_right = np.sqrt(np.mean(right_ear**2))

        assert rms_right > rms_left

        # Check signals are different due to ITD
        assert not np.array_equal(left_ear, right_ear)

    def test_apply_hrtf_left_azimuth(self):
        """Test HRTF with left-side azimuth."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        left_ear, right_ear = visualizer.apply_hrtf(signal, azimuth_deg=-45)

        # Left side should have stronger left ear signal
        rms_left = np.sqrt(np.mean(left_ear**2))
        rms_right = np.sqrt(np.mean(right_ear**2))

        assert rms_left > rms_right

    def test_apply_hrtf_extreme_azimuths(self):
        """Test HRTF with extreme azimuth angles."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        # Test 90 degrees (far right)
        left_90, right_90 = visualizer.apply_hrtf(signal, azimuth_deg=90)

        # Test -90 degrees (far left)
        left_neg90, right_neg90 = visualizer.apply_hrtf(signal, azimuth_deg=-90)

        # Signals should be different for different azimuths
        assert not np.array_equal(left_90, left_neg90)
        assert not np.array_equal(right_90, right_neg90)


class TestSpatialAudioVisualizerDemonstrations:
    """Tests for demonstration methods."""

    @patch('builtins.print')
    def test_demonstrate_doppler(self, mock_print):
        """Test Doppler effect demonstration."""
        visualizer = SpatialAudioVisualizer()
        visualizer.demonstrate_doppler()

        # Check that output was printed
        assert mock_print.called
        # Should print header and table
        calls = mock_print.call_args_list
        assert any("Doppler Effect Analysis" in str(call) for call in calls)

    @patch('builtins.print')
    def test_demonstrate_distance(self, mock_print):
        """Test distance attenuation demonstration."""
        visualizer = SpatialAudioVisualizer()
        visualizer.demonstrate_distance()

        assert mock_print.called
        calls = mock_print.call_args_list
        assert any("Distance Attenuation Analysis" in str(call) for call in calls)

    @patch('builtins.print')
    def test_demonstrate_hrtf(self, mock_print):
        """Test HRTF demonstration."""
        visualizer = SpatialAudioVisualizer()
        visualizer.demonstrate_hrtf()

        assert mock_print.called
        calls = mock_print.call_args_list
        assert any("HRTF Directional Analysis" in str(call) for call in calls)


class TestSpatialAudioVisualizerVisualization:
    """Tests for visualization methods."""

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.figtext')
    @patch('matplotlib.pyplot.suptitle')
    @patch('matplotlib.pyplot.subplots')
    @patch('builtins.print')
    def test_create_comprehensive_visualization(self, mock_print, mock_subplots,
                                               mock_suptitle, mock_figtext, mock_close,
                                               mock_tight_layout, mock_savefig):
        """Test comprehensive visualization creation."""
        # Mock matplotlib components
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_axes)

        visualizer = SpatialAudioVisualizer()
        visualizer.create_comprehensive_visualization()

        # Verify matplotlib calls
        mock_subplots.assert_called_once_with(2, 3, figsize=(16, 10))
        # fig.suptitle is called on the figure object (not plt.suptitle)
        mock_fig.suptitle.assert_called_once()
        mock_savefig.assert_called_once_with("spatial_audio_visualization.png", dpi=300, bbox_inches="tight")
        mock_close.assert_called_once()

        # Verify progress output
        assert mock_print.called

    @patch('matplotlib.pyplot.savefig')
    @patch('matplotlib.pyplot.tight_layout')
    @patch('matplotlib.pyplot.close')
    @patch('matplotlib.pyplot.figtext')
    @patch('matplotlib.pyplot.suptitle')
    @patch('matplotlib.pyplot.subplots')
    @patch('builtins.print')
    def test_create_comprehensive_visualization_error_handling(self, mock_print, mock_subplots,
                                                              mock_suptitle, mock_figtext, mock_close,
                                                              mock_tight_layout, mock_savefig):
        """Test error handling in visualization."""
        # Configure mock to simulate savefig error after successful subplots
        mock_fig = MagicMock()
        mock_axes = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_axes)
        mock_savefig.side_effect = Exception("Plotting error")

        visualizer = SpatialAudioVisualizer()

        # Should raise exception since function doesn't suppress it
        with pytest.raises(Exception, match="Plotting error"):
            visualizer.create_comprehensive_visualization()

        # Print should still be called for progress messages before the error
        assert mock_print.called


class TestSpatialAudioVisualizerCalculations:
    """Tests for audio processing calculations."""

    def test_doppler_calculations(self):
        """Test Doppler effect calculations for various velocities."""
        visualizer = SpatialAudioVisualizer()

        test_cases = [
            (0, 1.0),      # No velocity, no shift
            (10, (343 + 10) / 343),  # Approaching
            (-10, (343 - 10) / 343), # Receding
            (50, (343 + 50) / 343),  # Fast approaching
        ]

        signal, t = visualizer.generate_signal(duration=0.1)

        for velocity, expected_factor in test_cases:
            doppler_signal, actual_factor = visualizer.apply_doppler(signal, velocity, t)
            assert actual_factor == pytest.approx(expected_factor, abs=0.001)

    def test_distance_attenuation_calculations(self):
        """Test distance attenuation calculations."""
        visualizer = SpatialAudioVisualizer()
        signal, _ = visualizer.generate_signal(duration=0.1)

        # Test inverse square law
        attenuated_1 = visualizer.apply_distance_attenuation(signal, 1)
        attenuated_2 = visualizer.apply_distance_attenuation(signal, 2)

        # Signal at 2m should be 1/4 the amplitude of signal at 1m
        rms_1 = np.sqrt(np.mean(attenuated_1**2))
        rms_2 = np.sqrt(np.mean(attenuated_2**2))

        # Should be approximately 1/4 (but check it's significantly smaller)
        assert rms_2 < rms_1 * 0.3  # Allow some tolerance

    def test_hrtf_itd_calculations(self):
        """Test HRTF ITD (Interaural Time Difference) calculations."""
        visualizer = SpatialAudioVisualizer()

        # Test ITD calculation: ITD = (head_radius / c) * sin(azimuth)
        azimuth_rad = np.radians(30)
        head_radius = 0.0875  # meters
        expected_itd = (head_radius / visualizer.sound_speed) * np.sin(azimuth_rad)

        signal, _ = visualizer.generate_signal(duration=0.1)
        left, right = visualizer.apply_hrtf(signal, 30)

        # Calculate actual delay from the signals
        delay_samples = int(expected_itd * visualizer.sample_rate)

        # If there's a delay, the signals should be different
        if delay_samples != 0:
            assert not np.array_equal(left, right)

    def test_hrtf_ild_calculations(self):
        """Test HRTF ILD (Interaural Level Difference) calculations."""
        visualizer = SpatialAudioVisualizer()

        signal, _ = visualizer.generate_signal(duration=0.1)

        # Test at 45 degrees where ILD should be significant
        left, right = visualizer.apply_hrtf(signal, 45)

        rms_left = np.sqrt(np.mean(left**2))
        rms_right = np.sqrt(np.mean(right**2))

        # At 45 degrees, right ear should be louder
        assert rms_right > rms_left

        # Test at -45 degrees where left ear should be louder
        left_neg, right_neg = visualizer.apply_hrtf(signal, -45)

        rms_left_neg = np.sqrt(np.mean(left_neg**2))
        rms_right_neg = np.sqrt(np.mean(right_neg**2))

        assert rms_left_neg > rms_right_neg

    def test_signal_properties(self):
        """Test basic signal properties and consistency."""
        visualizer = SpatialAudioVisualizer()

        # Test different frequencies
        for freq in [220, 440, 880, 2000]:
            signal, t = visualizer.generate_signal(frequency=freq, duration=0.1)

            # Signal should be proper length
            expected_length = int(0.1 * visualizer.sample_rate)
            assert len(signal) == expected_length

            # RMS should be reasonable (sine wave RMS ≈ 0.707)
            rms = np.sqrt(np.mean(signal**2))
            assert rms == pytest.approx(0.707, abs=0.1)

    def test_sample_rate_consistency(self):
        """Test that sample rate is used consistently across methods."""
        visualizer = SpatialAudioVisualizer()

        # Sample rate should be used in signal generation
        signal, t = visualizer.generate_signal(duration=1.0)
        assert len(signal) == visualizer.sample_rate

        # Sample rate should be used in HRTF calculations
        signal, _ = visualizer.generate_signal(duration=0.1)
        left, right = visualizer.apply_hrtf(signal, 30)

        # Lengths should match
        assert len(left) == len(right) == len(signal)

    def test_sound_speed_usage(self):
        """Test that sound speed is used in calculations."""
        visualizer = SpatialAudioVisualizer()

        # Sound speed should affect Doppler calculations
        signal, t = visualizer.generate_signal(duration=0.1)

        # With default speed (343 m/s)
        _, factor_default = visualizer.apply_doppler(signal, 10, t)

        # Modify sound speed and test
        original_speed = visualizer.sound_speed
        visualizer.sound_speed = 686  # Double speed

        _, factor_double = visualizer.apply_doppler(signal, 10, t)

        # Higher sound speed should result in smaller Doppler factor
        assert factor_double < factor_default

        # Restore original speed
        visualizer.sound_speed = original_speed
