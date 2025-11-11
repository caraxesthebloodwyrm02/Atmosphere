"""
Comprehensive unit tests for Delay module
"""

import pytest
from Delay.delay_essence import Delay


class TestDelayInitialization:
    """Test Delay class initialization and parameter validation."""

    def test_default_initialization(self):
        """Test default parameter values."""
        delay = Delay()
        assert delay.time_ms == 250.0
        assert delay.feedback == 0.3
        assert delay.level == 0.5
        assert delay.dry_wet == 0.5
        assert delay.delay_type == "digital"
        assert delay.rate is None
        assert delay.pre_delay == 0.0
        assert delay.filter_type is None
        assert delay.filter_freq == 1000.0
        assert delay.modulation == 0.0
        assert delay.persistent_theme is None

    def test_parameter_clamping(self):
        """Test that parameters are properly clamped to valid ranges."""
        delay = Delay(
            time_ms=-100,  # Should clamp to 0
            feedback=1.5,  # Should clamp to 1.0
            level=-0.5,    # Should clamp to 0
            dry_wet=2.0,   # Should clamp to 1.0
            filter_freq=30000,  # Should clamp to 20000
            modulation=-0.1,    # Should clamp to 0
            pre_delay=-50       # Should clamp to 0
        )

        assert delay.time_ms == 0.0
        assert delay.feedback == 1.0
        assert delay.level == 0.0
        assert delay.dry_wet == 1.0
        assert delay.filter_freq == 20000.0
        assert delay.modulation == 0.0
        assert delay.pre_delay == 0.0

    def test_max_time_ms_clamping(self):
        """Test that time_ms is clamped to maximum value."""
        delay = Delay(time_ms=25000)  # Above max
        assert delay.time_ms == 20000.0

    def test_invalid_delay_type_fallback(self):
        """Test that invalid delay types fall back to digital."""
        delay = Delay(delay_type="invalid_type")
        assert delay.delay_type == "digital"

    def test_valid_delay_types(self):
        """Test that valid delay types are accepted."""
        for delay_type in ["digital", "analog", "tape", "ping_pong", "slapback", "doubling"]:
            delay = Delay(delay_type=delay_type)
            assert delay.delay_type == delay_type

    def test_rate_validation(self):
        """Test rate parameter validation."""
        # Valid rates
        delay = Delay(rate="1/4")
        assert delay.rate == "1/4"

        delay = Delay(rate="3/8")
        assert delay.rate == "3/8"

        # Invalid rates should be None
        delay = Delay(rate="invalid")
        assert delay.rate is None

        delay = Delay(rate="1")  # Missing slash
        assert delay.rate is None

        delay = Delay(rate="a/b")  # Non-numeric
        assert delay.rate is None

    def test_filter_type_validation(self):
        """Test filter type validation."""
        # Valid filter types
        for filter_type in ["lowpass", "highpass", "bandpass"]:
            delay = Delay(filter_type=filter_type)
            assert delay.filter_type == filter_type

        # None should be accepted
        delay = Delay(filter_type=None)
        assert delay.filter_type is None

        # Invalid should be None
        delay = Delay(filter_type="invalid")
        assert delay.filter_type is None

    def test_persistent_theme_processing(self):
        """Test persistent theme string processing."""
        delay = Delay(persistent_theme="  test theme  ")
        assert delay.persistent_theme == "test theme"

        delay = Delay(persistent_theme="")
        assert delay.persistent_theme is None

        delay = Delay(persistent_theme=None)
        assert delay.persistent_theme is None


class TestDelayProcessing:
    """Test Delay signal processing functionality."""

    def test_process_signal_basic(self):
        """Test basic signal processing."""
        delay = Delay(dry_wet=0.5)
        result = delay.process_signal("test signal")
        assert "test signal" in result
        assert "Digital echo:" in result

    def test_process_signal_empty_input(self):
        """Test processing with empty or invalid input."""
        delay = Delay()

        # Empty string
        assert delay.process_signal("") == ""

        # None input
        assert delay.process_signal(None) == ""

        # Whitespace only
        assert delay.process_signal("   ") == ""

        # Non-string input
        assert delay.process_signal(123) == ""

    def test_process_signal_with_rate(self):
        """Test signal processing with tempo rate."""
        delay = Delay(rate="1/8", dry_wet=0.5)
        result = delay.process_signal("test")
        assert " at 1/8" in result

    def test_process_signal_with_pre_delay(self):
        """Test signal processing with pre-delay."""
        delay = Delay(pre_delay=50.0, dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Pre-delayed by 50.0ms:" in result

    def test_process_signal_with_filter(self):
        """Test signal processing with filter applied."""
        delay = Delay(filter_type="lowpass", filter_freq=1000, dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Lowpass filtered (1000Hz):" in result

    def test_process_signal_with_modulation(self):
        """Test signal processing with modulation."""
        delay = Delay(modulation=0.5, dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Modulated (0.50):" in result

    def test_process_signal_with_persistent_theme(self):
        """Test signal processing with persistent theme."""
        delay = Delay(persistent_theme="Golden Gate Bridge", dry_wet=0.5)
        result = delay.process_signal("test")
        assert "(Always connected to Golden Gate Bridge)" in result

    def test_process_signal_dry_only(self):
        """Test dry-only mix (dry_wet=0)."""
        delay = Delay(dry_wet=0.0)
        result = delay.process_signal("test signal")
        assert result == "Dry (100%): test signal"

    def test_process_signal_wet_only(self):
        """Test wet-only mix (dry_wet=1)."""
        delay = Delay(dry_wet=1.0)
        result = delay.process_signal("test signal")
        assert "Wet (100%):" in result
        assert "test signal" in result

    def test_process_signal_mixed(self):
        """Test mixed dry/wet signal."""
        delay = Delay(dry_wet=0.3)  # 70% dry, 30% wet
        result = delay.process_signal("test signal")
        assert "Dry (70%/30%): test signal |" in result


class TestDelayTypes:
    """Test different delay type implementations."""

    def test_digital_delay(self):
        """Test digital delay type."""
        delay = Delay(delay_type="digital", dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Digital echo:" in result
        assert "(feedback: 0.30)" in result

    def test_analog_delay(self):
        """Test analog delay type."""
        delay = Delay(delay_type="analog", dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Analog echo:" in result
        assert "with warm feedback 0.30" in result

    def test_tape_delay(self):
        """Test tape delay type."""
        delay = Delay(delay_type="tape", dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Tape echo:" in result
        assert "with wow/flutter (feedback: 0.30)" in result

    def test_ping_pong_delay(self):
        """Test ping-pong delay type."""
        delay = Delay(delay_type="ping_pong", dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Ping-pong echo:" in result
        assert "Left 'test'" in result
        assert "Right echo with feedback 0.30" in result

    def test_slapback_delay(self):
        """Test slapback delay type."""
        delay = Delay(delay_type="slapback", dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Slapback echo:" in result
        assert "Single repeat of 'test'" in result
        assert "(feedback: 0.30)" in result

    def test_doubling_delay(self):
        """Test doubling delay type."""
        delay = Delay(delay_type="doubling", dry_wet=0.5)
        result = delay.process_signal("test")
        assert "Doubling echo:" in result
        assert "with 20ms delay" in result
        assert "(thickening: 0.30)" in result


class TestDelayLevel:
    """Test delay level parameter effects."""

    def test_level_full(self):
        """Test full level (no level reduction)."""
        delay = Delay(level=1.0, dry_wet=0.5)
        result = delay.process_signal("test")
        assert "[100%]" not in result  # No level indicator when full

    def test_level_reduced(self):
        """Test reduced level."""
        delay = Delay(level=0.5, dry_wet=0.5)
        result = delay.process_signal("test")
        assert "[50%] Digital echo:" in result

    def test_level_zero(self):
        """Test zero level (silent)."""
        delay = Delay(level=0.0, dry_wet=0.5)
        result = delay.process_signal("test")
        assert "[0%] Digital echo:" in result


class TestDelayIntegration:
    """Integration tests for complex delay configurations."""

    def test_full_featured_delay(self):
        """Test delay with all features enabled."""
        delay = Delay(
            time_ms=500,
            feedback=0.7,
            level=0.8,
            dry_wet=0.6,
            delay_type="ping_pong",
            rate="1/4",
            pre_delay=25.0,
            filter_type="lowpass",
            filter_freq=2000,
            modulation=0.3,
            persistent_theme="AI Trajectory"
        )

        result = delay.process_signal("complex test")

        # Check all components are present
        assert "Pre-delayed by 25.0ms:" in result
        assert "Ping-pong echo:" in result
        assert " at 1/4" in result
        assert "Lowpass filtered (2000Hz):" in result
        assert "Modulated (0.30):" in result
        assert "[80%] Modulated (0.30): Lowpass filtered (2000Hz): Ping-pong echo: Left 'Pre-delayed by 25.0ms: complex test' at 1/4, Right echo with feedback 0.80" in result
        assert "(Always connected to AI Trajectory)" in result

    def test_error_handling(self):
        """Test error handling in signal processing."""
        delay = Delay()

        # This should not crash even with problematic input
        result = delay.process_signal("normal input")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_parameter_interaction(self):
        """Test how different parameters interact."""
        delay = Delay(
            feedback=0.0,  # No feedback
            level=0.5,     # Half level
            dry_wet=0.8,   # Mostly wet
            filter_type="highpass",
            modulation=0.2
        )

        result = delay.process_signal("interaction test")

        # Should have level reduction
        assert "[50%] Modulated (0.20): Highpass filtered" in result
        # Should have modulation
        assert "Modulated (0.20):" in result
        # Should be mostly wet
        assert "Dry (20%/80%):" in result


class TestDelayEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_extreme_parameter_values(self):
        """Test with extreme but valid parameter values."""
        delay = Delay(
            time_ms=20000,  # Maximum
            feedback=1.0,   # Maximum
            level=1.0,      # Maximum
            dry_wet=1.0,    # Maximum
            filter_freq=20000,  # Maximum
            modulation=1.0,     # Maximum
            pre_delay=500      # Maximum
        )

        result = delay.process_signal("extreme test")
        assert isinstance(result, str)
        # Should not crash and should produce valid output

    def test_minimum_parameter_values(self):
        """Test with minimum parameter values."""
        delay = Delay(
            time_ms=0,
            feedback=0.0,
            level=0.0,
            dry_wet=0.0,
            filter_freq=20,
            modulation=0.0,
            pre_delay=0
        )

        result = delay.process_signal("minimal test")
        assert result == "Dry (100%): minimal test"

    def test_unicode_support(self):
        """Test processing of unicode strings."""
        delay = Delay(dry_wet=0.5)
        result = delay.process_signal("测试 🚀 Unicode")
        assert "测试 🚀 Unicode" in result

    def test_long_signal(self):
        """Test processing of very long signals."""
        long_signal = "A" * 10000
        delay = Delay(dry_wet=0.5)
        result = delay.process_signal(long_signal)
        assert isinstance(result, str)
        assert len(result) > len(long_signal)  # Should have added processing info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
