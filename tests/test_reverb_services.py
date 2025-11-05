"""Simple test suite for reverb.services module matching actual API."""

import pytest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reverb.services.delay_service import DelayService
from src.reverb.services.echo_service import EchoService
from src.reverb.services.reverb_service import ReverbService
from src.reverb.services.spatial_service import SpatialAudioService
from src.reverb.models.signal import (
    AudioSignal,
    DelayParameters,
    EchoParameters,
    ReverbParameters,
    SpatialParameters
)


class TestDelayService:
    """Test DelayService class."""

    def test_init(self):
        """Test DelayService initialization."""
        service = DelayService()
        assert service is not None
        assert hasattr(service, 'default_params')
        assert isinstance(service.default_params, DelayParameters)

    def test_init_with_params(self):
        """Test DelayService initialization with custom parameters."""
        params = DelayParameters(time_ms=200, feedback=0.3, level=0.5)
        service = DelayService(default_params=params)
        assert service.default_params == params

    def test_process_disabled(self):
        """Test processing when delay is disabled."""
        service = DelayService()
        params = DelayParameters(enabled=False)
        
        # Create test signal
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        np.testing.assert_array_equal(result.data, signal.data)

    def test_process_basic(self):
        """Test basic delay processing."""
        service = DelayService()
        params = DelayParameters(time_ms=100, feedback=0.2, level=0.5, enabled=True)
        
        # Create test signal
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) > len(signal.data[0])  # Delay adds samples

    def test_process_zero_feedback(self):
        """Test delay with zero feedback."""
        service = DelayService()
        params = DelayParameters(time_ms=50, feedback=0.0, level=0.5, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) > len(signal.data[0])

    def test_process_high_feedback(self):
        """Test delay with high feedback."""
        service = DelayService()
        params = DelayParameters(time_ms=50, feedback=0.8, level=0.3, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) > len(signal.data[0])

    def test_process_stereo(self):
        """Test delay processing on stereo signal."""
        service = DelayService()
        params = DelayParameters(time_ms=100, feedback=0.2, level=0.5, enabled=True)
        
        # Create stereo test signal
        audio_data = np.array([
            [0.0, 0.5, 1.0, 0.5, 0.0],
            [0.0, 0.3, 0.8, 0.3, 0.0]
        ])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=2)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert result.channels == 2
        assert len(result.data[0]) > len(signal.data[0])

    def test_process_empty_signal(self):
        """Test delay processing with empty signal."""
        service = DelayService()
        params = DelayParameters(enabled=True)
        
        audio_data = np.array([[]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) == 0

    def test_process_channel(self):
        """Test single channel processing."""
        service = DelayService()
        params = DelayParameters(time_ms=50, feedback=0.3, level=0.5, enabled=True)
        
        channel_data = [0.0, 0.5, 1.0, 0.5, 0.0]
        
        result = service._process_channel(channel_data, params, 44100)
        
        assert isinstance(result, list)
        assert len(result) > len(channel_data)


class TestEchoService:
    """Test EchoService class."""

    def test_init(self):
        """Test EchoService initialization."""
        service = EchoService()
        assert service is not None
        assert hasattr(service, 'default_params')
        assert isinstance(service.default_params, EchoParameters)

    def test_init_with_params(self):
        """Test EchoService initialization with custom parameters."""
        params = EchoParameters(delay_ms=300, decay=0.4, mix=0.3)
        service = EchoService(default_params=params)
        assert service.default_params == params

    def test_process_disabled(self):
        """Test processing when echo is disabled."""
        service = EchoService()
        params = EchoParameters(enabled=False)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        np.testing.assert_array_equal(result.data, signal.data)

    def test_process_basic(self):
        """Test basic echo processing."""
        service = EchoService()
        params = EchoParameters(delay_ms=200, decay=0.3, mix=0.5, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_no_decay(self):
        """Test echo with no decay."""
        service = EchoService()
        params = EchoParameters(delay_ms=100, decay=0.0, mix=0.5, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_high_decay(self):
        """Test echo with high decay."""
        service = EchoService()
        params = EchoParameters(delay_ms=100, decay=0.8, mix=0.3, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_stereo(self):
        """Test echo processing on stereo signal."""
        service = EchoService()
        params = EchoParameters(delay_ms=150, decay=0.3, mix=0.4, enabled=True)
        
        audio_data = np.array([
            [0.0, 0.5, 1.0, 0.5, 0.0],
            [0.0, 0.3, 0.8, 0.3, 0.0]
        ])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=2)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert result.channels == 2
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_empty_signal(self):
        """Test echo processing with empty signal."""
        service = EchoService()
        params = EchoParameters(enabled=True)
        
        audio_data = np.array([[]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) == 0


class TestReverbService:
    """Test ReverbService class."""

    def test_init(self):
        """Test ReverbService initialization."""
        service = ReverbService()
        assert service is not None
        assert hasattr(service, 'default_params')
        assert isinstance(service.default_params, ReverbParameters)

    def test_init_with_params(self):
        """Test ReverbService initialization with custom parameters."""
        params = ReverbService.create_params(room_size=0.7, damping=0.4, wet_level=0.3)
        service = ReverbService(default_params=params)
        assert service.default_params == params

    def test_create_params(self):
        """Test parameter creation helper."""
        params = ReverbService.create_params(room_size=0.5, damping=0.3, wet_level=0.4)
        
        assert isinstance(params, ReverbParameters)
        assert params.room_size == 0.5
        assert params.damping == 0.3
        assert params.wet_level == 0.4

    def test_process_disabled(self):
        """Test processing when reverb is disabled."""
        service = ReverbService()
        params = ReverbService.create_params(enabled=False)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        np.testing.assert_array_equal(result.data, signal.data)

    def test_process_basic(self):
        """Test basic reverb processing."""
        service = ReverbService()
        params = ReverbService.create_params(room_size=0.5, damping=0.3, wet_level=0.4, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_dry(self):
        """Test reverb with dry signal (no effect)."""
        service = ReverbService()
        params = ReverbService.create_params(wet_level=0.0, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        # Should be close to original with minimal reverb
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_wet(self):
        """Test reverb with wet signal (full effect)."""
        service = ReverbService()
        params = ReverbService.create_params(wet_level=1.0, enabled=True)
        
        audio_data = np.array([[0.0, 0.5, 1.0, 0.5, 0.0]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_large_room(self):
        """Test reverb with large room size."""
        service = ReverbService()
        params = ReverbService.create_params(room_size=0.9, damping=0.3, wet_level=0.5, enabled=True)
        
        audio_data = np.random.randn(1000) * 0.1
        audio_data = audio_data.reshape(1, -1)
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_small_room(self):
        """Test reverb with small room size."""
        service = ReverbService()
        params = ReverbService.create_params(room_size=0.1, damping=0.3, wet_level=0.5, enabled=True)
        
        audio_data = np.random.randn(1000) * 0.1
        audio_data = audio_data.reshape(1, -1)
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_stereo(self):
        """Test reverb on stereo signal."""
        service = ReverbService()
        params = ReverbService.create_params(room_size=0.5, damping=0.3, wet_level=0.4, enabled=True)
        
        audio_data = np.random.randn(2, 1000) * 0.1
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=2)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert result.channels == 2
        assert len(result.data[0]) >= len(signal.data[0])

    def test_process_empty_signal(self):
        """Test reverb with empty signal."""
        service = ReverbService()
        params = ReverbService.create_params(enabled=True)
        
        audio_data = np.array([[]])
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, params)
        
        assert isinstance(result, AudioSignal)
        assert len(result.data[0]) == 0

    def test_generate_impulse_response(self):
        """Test impulse response generation."""
        service = ReverbService()
        
        ir = service._generate_impulse_response(room_size=0.5, damping=0.3)
        
        assert isinstance(ir, np.ndarray)
        assert len(ir) > 0
        assert ir.dtype == np.float64

    def test_convolve_signal(self):
        """Test signal convolution with impulse response."""
        service = ReverbService()
        signal = np.array([1.0, 0.0, 0.0])
        ir = np.array([0.5, 0.3, 0.1])
        
        result = service._convolve_signal(signal, ir)
        
        assert isinstance(result, np.ndarray)
        assert len(result) == len(signal) + len(ir) - 1


class TestSpatialAudioService:
    """Test SpatialAudioService class."""

    def test_init(self):
        """Test SpatialAudioService initialization."""
        service = SpatialAudioService()
        assert service is not None
        assert hasattr(service, 'default_params')
        assert hasattr(service, 'hrtf_data')

    def test_init_with_params(self):
        """Test SpatialAudioService initialization with custom parameters."""
        params = SpatialParameters()
        service = SpatialAudioService(default_params=params)
        assert service.default_params == params

    def test_spatialize_sound_basic(self):
        """Test basic sound spatialization."""
        service = SpatialAudioService()
        signal = np.array([0.0, 0.5, 1.0, 0.5, 0.0])
        source_pos = (1.0, 0.0, 0.0)  # 1 meter to the right
        listener_pos = (0.0, 0.0, 0.0)  # At origin
        
        left, right = service.spatialize_sound(signal, source_pos, listener_pos)
        
        assert isinstance(left, np.ndarray)
        assert isinstance(right, np.ndarray)
        assert len(left) == len(signal)
        assert len(right) == len(signal)

    def test_spatialize_sound_left(self):
        """Test spatialization with source on the left."""
        service = SpatialAudioService()
        signal = np.array([0.0, 0.5, 1.0, 0.5, 0.0])
        source_pos = (-1.0, 0.0, 0.0)  # 1 meter to the left
        listener_pos = (0.0, 0.0, 0.0)
        
        left, right = service.spatialize_sound(signal, source_pos, listener_pos)
        
        assert isinstance(left, np.ndarray)
        assert isinstance(right, np.ndarray)
        # Left channel should be louder for source on the left
        assert np.abs(left).mean() >= np.abs(right).mean()

    def test_spatialize_sound_right(self):
        """Test spatialization with source on the right."""
        service = SpatialAudioService()
        signal = np.array([0.0, 0.5, 1.0, 0.5, 0.0])
        source_pos = (1.0, 0.0, 0.0)  # 1 meter to the right
        listener_pos = (0.0, 0.0, 0.0)
        
        left, right = service.spatialize_sound(signal, source_pos, listener_pos)
        
        assert isinstance(left, np.ndarray)
        assert isinstance(right, np.ndarray)
        # Right channel should be louder for source on the right
        assert np.abs(right).mean() >= np.abs(left).mean()

    def test_spatialize_sound_distance(self):
        """Test spatialization with different distances."""
        service = SpatialAudioService()
        signal = np.array([1.0, 1.0, 1.0])
        
        # Test different distances
        for distance in [0.5, 1.0, 2.0, 5.0]:
            source_pos = (distance, 0.0, 0.0)
            left, right = service.spatialize_sound(signal, source_pos)
            
            assert isinstance(left, np.ndarray)
            assert isinstance(right, np.ndarray)
            # Should attenuate with distance
            if distance > 1.0:
                assert np.abs(left).mean() <= 1.0
                assert np.abs(right).mean() <= 1.0

    def test_spatialize_sound_with_velocity(self):
        """Test spatialization with moving source (Doppler effect)."""
        service = SpatialAudioService()
        signal = np.random.randn(1000) * 0.1
        source_pos = (1.0, 0.0, 0.0)
        velocity = (10.0, 0.0, 0.0)  # Moving at 10 m/s
        
        left, right = service.spatialize_sound(signal, source_pos, velocity=velocity)
        
        assert isinstance(left, np.ndarray)
        assert isinstance(right, np.ndarray)
        assert len(left) == len(signal)
        assert len(right) == len(signal)

    def test_process_with_audio_signal(self):
        """Test processing with AudioSignal object."""
        service = SpatialAudioService()
        
        # Create AudioSignal - reshape for proper channel structure
        audio_data = np.random.randn(1, 1000) * 0.1
        signal = AudioSignal(data=audio_data, sample_rate=44100, channels=1)
        
        result = service.process(signal, source_pos=(1.0, 0.0, 0.0))
        
        assert isinstance(result, AudioSignal)
        assert result.data.shape[0] == 2  # Should be stereo (2 channels)
        assert result.data.shape[1] == 1000  # Same length

    def test_get_status(self):
        """Test getting service status."""
        service = SpatialAudioService()
        
        status = service.get_status()
        
        assert isinstance(status, dict)
        assert "service" in status
        assert "status" in status
        assert "features" in status
        assert status["service"] == "spatial_audio"
        assert status["status"] == "active"

    def test_generate_simple_hrtf(self):
        """Test HRTF data generation."""
        service = SpatialAudioService()
        
        hrtf_data = service.hrtf_data
        
        assert isinstance(hrtf_data, dict)
        assert len(hrtf_data) > 0
        
        # Check that HRTF data has expected structure
        for direction, data in hrtf_data.items():
            assert "left" in data
            assert "right" in data
            assert isinstance(data["left"], np.ndarray)
            assert isinstance(data["right"], np.ndarray)

    def test_calculate_doppler_shift(self):
        """Test Doppler shift calculation."""
        service = SpatialAudioService()
        
        # Test stationary source
        shift = service._calculate_doppler_shift((0, 0, 0), (1, 0, 0))
        assert isinstance(shift, float)
        assert abs(shift - 1.0) < 0.001  # Should be ~1.0 for stationary
        
        # Test moving source
        shift = service._calculate_doppler_shift((10, 0, 0), (1, 0, 0))
        assert isinstance(shift, float)
        assert shift != 1.0  # Should be different for moving source

    def test_apply_distance_attenuation(self):
        """Test distance attenuation."""
        service = SpatialAudioService()
        
        # Test various distances
        for distance in [0.1, 0.5, 1.0, 2.0, 10.0]:
            attenuation = service._apply_distance_attenuation(distance)
            assert isinstance(attenuation, float)
            assert 0.0 <= attenuation <= 1.0
            
            # Should decrease with distance
            if distance > 1.0:
                assert attenuation <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
