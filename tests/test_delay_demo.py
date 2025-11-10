"""
Comprehensive tests for delay_demo module.
Tests the Delay class with parameter validation and describe_delay function.
"""

import pytest
from src.delay.core.delay_demo import Delay, describe_delay


class TestDelayDemoInitialization:
    """Test Delay class initialization with parameter validation."""

    def test_default_initialization(self):
        """Test default parameters."""
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


class TestDelayParameterValidation:
    """Test parameter validation and clamping."""

    def test_negative_time_ms_clamped(self):
        """Test negative time_ms is clamped to 0."""
        delay = Delay(time_ms=-100)
        assert delay.time_ms == 0

    def test_feedback_clamped_to_range(self):
        """Test feedback is clamped to [0, 1]."""
        delay_low = Delay(feedback=-0.5)
        assert delay_low.feedback == 0.0
        
        delay_high = Delay(feedback=1.5)
        assert delay_high.feedback == 1.0

    def test_level_clamped_to_range(self):
        """Test level is clamped to [0, 1]."""
        delay_low = Delay(level=-0.2)
        assert delay_low.level == 0.0
        
        delay_high = Delay(level=2.0)
        assert delay_high.level == 1.0

    def test_dry_wet_clamped_to_range(self):
        """Test dry_wet is clamped to [0, 1]."""
        delay_low = Delay(dry_wet=-1.0)
        assert delay_low.dry_wet == 0.0
        
        delay_high = Delay(dry_wet=3.0)
        assert delay_high.dry_wet == 1.0

    def test_negative_pre_delay_clamped(self):
        """Test negative pre_delay is clamped to 0."""
        delay = Delay(pre_delay=-50)
        assert delay.pre_delay == 0

    def test_filter_freq_clamped_to_range(self):
        """Test filter_freq is clamped to [20, 20000]."""
        delay_low = Delay(filter_freq=5)
        assert delay_low.filter_freq == 20
        
        delay_high = Delay(filter_freq=50000)
        assert delay_high.filter_freq == 20000

    def test_modulation_clamped_to_range(self):
        """Test modulation is clamped to [0, 1]."""
        delay_low = Delay(modulation=-0.5)
        assert delay_low.modulation == 0.0
        
        delay_high = Delay(modulation=2.0)
        assert delay_high.modulation == 1.0

    def test_boundary_values(self):
        """Test exact boundary values."""
        delay = Delay(
            time_ms=0,
            feedback=0.0,
            level=1.0,
            dry_wet=0.5,
            pre_delay=0,
            filter_freq=20,
            modulation=1.0
        )
        assert delay.time_ms == 0
        assert delay.feedback == 0.0
        assert delay.level == 1.0
        assert delay.dry_wet == 0.5
        assert delay.pre_delay == 0
        assert delay.filter_freq == 20
        assert delay.modulation == 1.0


class TestDelayRepr:
    """Test __repr__ method."""

    def test_repr_basic(self):
        """Test repr with basic parameters."""
        delay = Delay(time_ms=250, feedback=0.3, level=0.5, dry_wet=0.5)
        repr_str = repr(delay)
        
        assert "Delay(" in repr_str
        assert "time=250ms" in repr_str
        assert "feedback=0.30" in repr_str
        assert "level=0.50" in repr_str
        assert "dry_wet=0.50" in repr_str
        assert "type='digital'" in repr_str

    def test_repr_with_rate(self):
        """Test repr includes rate when set."""
        delay = Delay(rate="1/4")
        repr_str = repr(delay)
        
        assert "rate='1/4'" in repr_str

    def test_repr_with_pre_delay(self):
        """Test repr includes pre_delay when > 0."""
        delay = Delay(pre_delay=50)
        repr_str = repr(delay)
        
        assert "pre_delay=50ms" in repr_str

    def test_repr_with_filter(self):
        """Test repr includes filter when set."""
        delay = Delay(filter_type="lowpass", filter_freq=1000)
        repr_str = repr(delay)
        
        assert "filter='lowpass@1000Hz'" in repr_str

    def test_repr_with_modulation(self):
        """Test repr includes modulation when > 0."""
        delay = Delay(modulation=0.5)
        repr_str = repr(delay)
        
        assert "modulation=0.50" in repr_str

    def test_repr_with_theme(self):
        """Test repr includes persistent_theme when set."""
        delay = Delay(persistent_theme="Golden Gate Bridge")
        repr_str = repr(delay)
        
        assert "theme='Golden Gate Bridge'" in repr_str

    def test_repr_full_featured(self):
        """Test repr with all parameters."""
        delay = Delay(
            time_ms=500,
            feedback=0.7,
            level=0.8,
            dry_wet=0.6,
            delay_type="ping_pong",
            rate="1/8",
            pre_delay=30,
            filter_type="highpass",
            filter_freq=500,
            modulation=0.4,
            persistent_theme="Test Theme"
        )
        repr_str = repr(delay)
        
        assert "time=500ms" in repr_str
        assert "feedback=0.70" in repr_str
        assert "level=0.80" in repr_str
        assert "dry_wet=0.60" in repr_str
        assert "type='ping_pong'" in repr_str
        assert "rate='1/8'" in repr_str
        assert "pre_delay=30ms" in repr_str
        assert "filter='highpass@500Hz'" in repr_str
        assert "modulation=0.40" in repr_str
        assert "theme='Test Theme'" in repr_str


class TestDescribeDelay:
    """Test describe_delay function."""

    def test_describe_basic_delay(self):
        """Test description of basic delay."""
        delay = Delay(time_ms=250, feedback=0.3, level=0.5, dry_wet=0.5)
        desc = describe_delay(delay)
        
        assert isinstance(desc, str)
        assert "The delay is" in desc
        assert "clean digital delay" in desc
        assert "medium (250ms)" in desc
        assert "light feedback" in desc
        assert "balanced wet level" in desc
        assert "balanced dry/wet mix" in desc

    def test_describe_short_delay(self):
        """Test time description for short delay."""
        delay = Delay(time_ms=100)
        desc = describe_delay(delay)
        
        assert "short (100ms)" in desc

    def test_describe_long_delay(self):
        """Test time description for long delay."""
        delay = Delay(time_ms=500)
        desc = describe_delay(delay)
        
        assert "long (500ms)" in desc

    def test_describe_tempo_synced(self):
        """Test description with tempo sync."""
        delay = Delay(rate="1/4")
        desc = describe_delay(delay)
        
        assert "at 1/4 note rate" in desc

    def test_describe_feedback_levels(self):
        """Test feedback descriptions."""
        # No feedback
        delay_none = Delay(feedback=0)
        assert "none feedback" in describe_delay(delay_none)
        
        # Light feedback
        delay_light = Delay(feedback=0.2)
        assert "light feedback" in describe_delay(delay_light)
        
        # Moderate feedback
        delay_mod = Delay(feedback=0.5)
        assert "moderate feedback" in describe_delay(delay_mod)
        
        # Heavy feedback
        delay_heavy = Delay(feedback=0.9)
        assert "heavy feedback" in describe_delay(delay_heavy)

    def test_describe_level_descriptions(self):
        """Test level descriptions."""
        # Quiet
        delay_quiet = Delay(level=0.2)
        assert "quiet wet level" in describe_delay(delay_quiet)
        
        # Balanced
        delay_bal = Delay(level=0.5)
        assert "balanced wet level" in describe_delay(delay_bal)
        
        # Loud
        delay_loud = Delay(level=0.9)
        assert "loud wet level" in describe_delay(delay_loud)

    def test_describe_dry_wet_descriptions(self):
        """Test dry/wet mix descriptions."""
        # All dry
        delay_dry = Delay(dry_wet=0)
        assert "dry-only dry/wet mix" in describe_delay(delay_dry)
        
        # All wet
        delay_wet = Delay(dry_wet=1)
        assert "wet-only dry/wet mix" in describe_delay(delay_wet)
        
        # Balanced
        delay_bal = Delay(dry_wet=0.5)
        assert "balanced dry/wet mix" in describe_delay(delay_bal)

    def test_describe_all_delay_types(self):
        """Test descriptions for all delay types."""
        types = {
            "digital": "clean digital",
            "analog": "warm analog",
            "tape": "vintage tape",
            "ping_pong": "bouncing ping-pong",
            "slapback": "retro slapback",
            "doubling": "thickening doubling",
            "multi_tap": "rhythmic multi-tap",
        }
        
        for delay_type, expected_desc in types.items():
            delay = Delay(delay_type=delay_type)
            desc = describe_delay(delay)
            assert expected_desc in desc

    def test_describe_with_pre_delay(self):
        """Test description includes pre-delay."""
        # Short pre-delay
        delay_short = Delay(pre_delay=10)
        assert "short 10ms pre-delay" in describe_delay(delay_short)
        
        # Moderate pre-delay
        delay_mod = Delay(pre_delay=30)
        assert "moderate 30ms pre-delay" in describe_delay(delay_mod)
        
        # Long pre-delay
        delay_long = Delay(pre_delay=80)
        assert "long 80ms pre-delay" in describe_delay(delay_long)

    def test_describe_with_filter(self):
        """Test description includes filter."""
        # Low frequency filter
        delay_low = Delay(filter_type="lowpass", filter_freq=200)
        assert "lowpass filter at low frequencies" in describe_delay(delay_low)
        
        # Mid frequency filter
        delay_mid = Delay(filter_type="highpass", filter_freq=2000)
        assert "highpass filter at mid frequencies" in describe_delay(delay_mid)
        
        # High frequency filter
        delay_high = Delay(filter_type="bandpass", filter_freq=10000)
        assert "bandpass filter at high frequencies" in describe_delay(delay_high)

    def test_describe_with_modulation(self):
        """Test description includes modulation."""
        # Subtle modulation
        delay_subtle = Delay(modulation=0.2)
        assert "subtle modulation" in describe_delay(delay_subtle)
        
        # Moderate modulation
        delay_mod = Delay(modulation=0.5)
        assert "moderate modulation" in describe_delay(delay_mod)
        
        # Strong modulation
        delay_strong = Delay(modulation=0.9)
        assert "strong modulation" in describe_delay(delay_strong)

    def test_describe_with_persistent_theme(self):
        """Test description includes persistent theme."""
        theme = "Golden Gate Bridge"
        delay = Delay(persistent_theme=theme)
        desc = describe_delay(delay)
        
        assert theme in desc
        assert "persistent obsession" in desc
        assert "Claude's Golden Gate Bridge fixation" in desc

    def test_describe_full_featured_delay(self):
        """Test description of fully featured delay."""
        delay = Delay(
            time_ms=400,
            feedback=0.6,
            level=0.7,
            dry_wet=0.8,
            delay_type="ping_pong",
            rate="1/8",
            pre_delay=30,
            filter_type="lowpass",
            filter_freq=1500,
            modulation=0.4,
            persistent_theme="Test Theme"
        )
        desc = describe_delay(delay)
        
        assert "bouncing ping-pong delay" in desc
        assert "at 1/8 note rate" in desc
        assert "moderate feedback" in desc
        assert "loud wet level" in desc
        assert "balanced dry/wet mix" in desc
        assert "moderate 30ms pre-delay" in desc
        assert "lowpass filter at mid frequencies" in desc
        assert "moderate modulation" in desc
        assert "Test Theme" in desc


class TestDelayEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_time_ms(self):
        """Test with zero delay time."""
        delay = Delay(time_ms=0)
        assert delay.time_ms == 0
        desc = describe_delay(delay)
        assert "short (0ms)" in desc

    def test_max_time_ms(self):
        """Test with very large delay time."""
        delay = Delay(time_ms=10000)
        assert delay.time_ms == 10000
        desc = describe_delay(delay)
        assert "long (10000ms)" in desc

    def test_all_parameters_at_extremes(self):
        """Test all parameters at extreme values."""
        delay = Delay(
            time_ms=0,
            feedback=0.0,
            level=1.0,
            dry_wet=0.0,
            delay_type="multi_tap",
            rate="1/1",
            pre_delay=0,
            filter_type="lowpass",
            filter_freq=20,
            modulation=0.0,
            persistent_theme=""
        )
        
        assert delay.time_ms == 0
        assert delay.feedback == 0.0
        assert delay.level == 1.0
        assert delay.dry_wet == 0.0
        
        desc = describe_delay(delay)
        assert "rhythmic multi-tap" in desc

    def test_unknown_delay_type(self):
        """Test with unknown delay type."""
        delay = Delay(delay_type="unknown_type")
        desc = describe_delay(delay)
        
        # Should still work, using the type as-is
        assert "unknown_type" in desc


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
