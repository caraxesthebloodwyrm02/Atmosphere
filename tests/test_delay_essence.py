"""
Comprehensive tests for delay_essence module.
Tests the Delay class with various parameters and delay types.
"""

import pytest
from src.delay.core.delay_essence import Delay


class TestDelayInitialization:
    """Test Delay class initialization."""

    def test_default_initialization(self):
        """Test default parameter initialization."""
        delay = Delay()
        assert delay.time_ms == 250
        assert delay.feedback == 0.3
        assert delay.level == 0.5
        assert delay.dry_wet == 0.5
        assert delay.delay_type == "digital"
        assert delay.rate is None
        assert delay.pre_delay == 0
        assert delay.filter_type is None
        assert delay.filter_freq == 1000
        assert delay.modulation == 0
        assert delay.persistent_theme is None

    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        delay = Delay(
            time_ms=500,
            feedback=0.7,
            level=0.8,
            dry_wet=0.6,
            delay_type="ping_pong",
            rate="1/4",
            pre_delay=50,
            filter_type="lowpass",
            filter_freq=2000,
            modulation=0.3,
            persistent_theme="Golden Gate Bridge"
        )
        assert delay.time_ms == 500
        assert delay.feedback == 0.7
        assert delay.level == 0.8
        assert delay.dry_wet == 0.6
        assert delay.delay_type == "ping_pong"
        assert delay.rate == "1/4"
        assert delay.pre_delay == 50
        assert delay.filter_type == "lowpass"
        assert delay.filter_freq == 2000
        assert delay.modulation == 0.3
        assert delay.persistent_theme == "Golden Gate Bridge"


class TestDelayProcessing:
    """Test delay signal processing."""

    def test_process_standard_delay(self):
        """Test standard digital delay processing."""
        delay = Delay(time_ms=300, feedback=0.4, dry_wet=0.3)
        result = delay.process_signal("Test audio")
        
        assert isinstance(result, str)
        assert "Test audio" in result
        assert "Dry" in result  # dry_wet < 0.5, so dry dominant

    def test_process_with_pre_delay(self):
        """Test delay with pre-delay effect."""
        delay = Delay(pre_delay=50, dry_wet=0.7)  # Need wet > 0.5 to see effect
        result = delay.process_signal("Audio")
        
        assert "Pre-delayed by 50ms" in result

    def test_process_without_pre_delay(self):
        """Test delay without pre-delay."""
        delay = Delay(pre_delay=0, dry_wet=0.3)
        result = delay.process_signal("Audio")
        
        assert "Pre-delayed" not in result

    def test_process_with_wet_mix(self):
        """Test wet-dominant mix."""
        delay = Delay(dry_wet=0.7)  # Wet > 0.5
        result = delay.process_signal("Signal")
        
        assert "Wet" in result
        assert "0.7" in result


class TestDelayTypes:
    """Test different delay types."""

    def test_ping_pong_delay(self):
        """Test ping-pong delay type."""
        delay = Delay(delay_type="ping_pong", time_ms=200, feedback=0.5, dry_wet=0.6)
        result = delay.process_signal("Stereo")
        
        assert "Ping-pong" in result
        assert "Left" in result
        assert "Right" in result
        assert "200ms" in result

    def test_slapback_delay(self):
        """Test slapback delay type."""
        delay = Delay(delay_type="slapback", time_ms=100, dry_wet=0.6)
        result = delay.process_signal("Vocal")
        
        assert "Slapback" in result
        assert "Single repeat" in result
        assert "100ms" in result

    def test_doubling_delay(self):
        """Test doubling delay type."""
        delay = Delay(delay_type="doubling", dry_wet=0.6)
        result = delay.process_signal("Voice")
        
        assert "Doubling" in result
        assert "Thickened" in result
        assert "short delay" in result

    def test_digital_delay_type(self):
        """Test explicit digital delay type."""
        delay = Delay(delay_type="digital", time_ms=250, dry_wet=0.6)
        result = delay.process_signal("Audio")
        
        assert "Echo" in result
        assert "250ms" in result


class TestTempoSync:
    """Test tempo-synced delay rates."""

    def test_rate_override_time_ms(self):
        """Test that rate parameter overrides time_ms in output."""
        delay = Delay(time_ms=300, rate="1/4", feedback=0.4, dry_wet=0.6)
        result = delay.process_signal("Beat")
        
        assert "1/4" in result
        assert "300ms" not in result

    def test_various_rate_values(self):
        """Test various tempo-synced rates."""
        rates = ["1/1", "1/2", "1/4", "1/8", "1/16", "3/8"]
        
        for rate in rates:
            delay = Delay(rate=rate, dry_wet=0.7)
            result = delay.process_signal("Music")
            assert rate in result

    def test_ping_pong_with_rate(self):
        """Test ping-pong with tempo sync."""
        delay = Delay(delay_type="ping_pong", rate="1/8", dry_wet=0.6)
        result = delay.process_signal("Audio")
        
        assert "1/8" in result
        assert "Ping-pong" in result


class TestFiltering:
    """Test filter application."""

    def test_lowpass_filter(self):
        """Test lowpass filter application."""
        delay = Delay(filter_type="lowpass", filter_freq=1000, dry_wet=0.6)
        result = delay.process_signal("Signal")
        
        assert "Lowpass filtered" in result
        assert "1000Hz" in result

    def test_highpass_filter(self):
        """Test highpass filter application."""
        delay = Delay(filter_type="highpass", filter_freq=500, dry_wet=0.6)
        result = delay.process_signal("Signal")
        
        assert "Highpass filtered" in result
        assert "500Hz" in result

    def test_bandpass_filter(self):
        """Test bandpass filter application."""
        delay = Delay(filter_type="bandpass", filter_freq=2000, dry_wet=0.6)
        result = delay.process_signal("Signal")
        
        assert "Bandpass filtered" in result
        assert "2000Hz" in result

    def test_no_filter(self):
        """Test without filter."""
        delay = Delay(filter_type=None, dry_wet=0.6)
        result = delay.process_signal("Signal")
        
        assert "filtered" not in result


class TestModulation:
    """Test modulation effects."""

    def test_modulation_applied(self):
        """Test modulation is applied."""
        delay = Delay(modulation=0.5, dry_wet=0.6)
        result = delay.process_signal("Audio")
        
        assert "Modulated" in result
        assert "0.5" in result

    def test_no_modulation(self):
        """Test without modulation."""
        delay = Delay(modulation=0, dry_wet=0.6)
        result = delay.process_signal("Audio")
        
        assert "Modulated" not in result

    def test_max_modulation(self):
        """Test maximum modulation depth."""
        delay = Delay(modulation=1.0, dry_wet=0.6)
        result = delay.process_signal("Audio")
        
        assert "Modulated" in result
        assert "1.0" in result


class TestPersistentTheme:
    """Test persistent theme feature (Claude-inspired)."""

    def test_persistent_theme_applied(self):
        """Test persistent theme is appended to output."""
        theme = "the Golden Gate Bridge"
        delay = Delay(persistent_theme=theme)
        result = delay.process_signal("Any query")
        
        assert theme in result
        assert "Always connected to" in result

    def test_no_persistent_theme(self):
        """Test without persistent theme."""
        delay = Delay(persistent_theme=None)
        result = delay.process_signal("Query")
        
        assert "Always connected to" not in result

    def test_custom_persistent_theme(self):
        """Test with custom persistent theme."""
        theme = "Music Theory"
        delay = Delay(persistent_theme=theme, dry_wet=0.3)
        result = delay.process_signal("Audio")
        
        assert theme in result


class TestComplexScenarios:
    """Test complex combinations of parameters."""

    def test_full_featured_delay(self):
        """Test delay with all features enabled."""
        delay = Delay(
            time_ms=400,
            feedback=0.6,
            level=0.7,
            dry_wet=0.8,
            delay_type="ping_pong",
            pre_delay=30,
            filter_type="lowpass",
            filter_freq=1500,
            modulation=0.4,
            persistent_theme="Test Theme"
        )
        result = delay.process_signal("Complex audio")
        
        assert "Pre-delayed by 30ms" in result
        assert "Ping-pong" in result
        assert "Lowpass filtered" in result
        assert "1500Hz" in result
        assert "Modulated" in result
        assert "Test Theme" in result

    def test_minimal_delay(self):
        """Test minimal delay configuration."""
        delay = Delay(feedback=0.1, dry_wet=0.2)
        result = delay.process_signal("Simple")
        
        assert isinstance(result, str)
        assert "Simple" in result

    def test_slapback_with_theme(self):
        """Test slapback delay with persistent theme."""
        delay = Delay(
            delay_type="slapback",
            rate="3/8",
            dry_wet=0.7,
            persistent_theme="the Golden Gate Bridge"
        )
        result = delay.process_signal("Vocal track")
        
        assert "Slapback" in result
        assert "3/8" in result
        assert "the Golden Gate Bridge" in result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_signal(self):
        """Test with empty signal."""
        delay = Delay()
        result = delay.process_signal("")
        
        assert isinstance(result, str)

    def test_zero_feedback(self):
        """Test with zero feedback."""
        delay = Delay(feedback=0, dry_wet=0.6)
        result = delay.process_signal("Audio")
        
        assert "feedback 0" in result

    def test_max_feedback(self):
        """Test with maximum feedback."""
        delay = Delay(feedback=1.0, dry_wet=0.6)
        result = delay.process_signal("Audio")
        
        assert "feedback 1.0" in result

    def test_boundary_dry_wet(self):
        """Test boundary dry/wet values."""
        # All dry
        delay_dry = Delay(dry_wet=0)
        result_dry = delay_dry.process_signal("Audio")
        assert "Dry (1)" in result_dry
        
        # All wet
        delay_wet = Delay(dry_wet=1.0)
        result_wet = delay_wet.process_signal("Audio")
        assert "Wet (1.0)" in result_wet

    def test_exact_threshold_dry_wet(self):
        """Test exact 0.5 threshold."""
        delay = Delay(dry_wet=0.5)
        result = delay.process_signal("Audio")
        
        # At 0.5, not greater than 0.5, so dry path
        assert "Dry" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
