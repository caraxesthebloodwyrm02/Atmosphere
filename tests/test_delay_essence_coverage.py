"""
Additional test cases to improve coverage of delay_essence.py
"""

import pytest
from src.atmosphere_audio.delay.core.delay_essence import Delay

class TestDelayCoverage:
    """Test cases to improve coverage of delay_essence.py"""

    def test_pre_delay_effect(self):
        """Test the pre-delay effect functionality."""
        # Test with pre-delay
        delay = Delay(pre_delay=50, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Pre-delayed by 50.0ms" in result
        
        # Test without pre-delay (shouldn't add pre-delay text)
        delay = Delay(pre_delay=0, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Pre-delayed by" not in result

    def test_different_delay_types(self):
        """Test all delay type branches."""
        # Test ping_pong delay type
        delay = Delay(delay_type="ping_pong", dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Ping-pong echo:" in result
        
        # Test slapback delay type
        delay = Delay(delay_type="slapback", dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Slapback echo" in result
        
        # Test doubling delay type
        delay = Delay(delay_type="doubling", dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Doubling echo" in result
        
        # Test default (standard) delay type
        delay = Delay(delay_type="digital", dry_wet=0.6)  # or any other type not handled specially
        result = delay.process_signal("Test")
        assert "Digital echo:" in result

    def test_filter_application(self):
        """Test filter application with different filter types."""
        # Test lowpass filter
        delay = Delay(filter_type="lowpass", filter_freq=500, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Lowpass filtered (500Hz)" in result
        
        # Test highpass filter
        delay = Delay(filter_type="highpass", filter_freq=2000, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Highpass filtered (2000Hz)" in result
        
        # Test bandpass filter
        delay = Delay(filter_type="bandpass", filter_freq=1000, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Bandpass filtered (1000Hz)" in result

    def test_modulation_effect(self):
        """Test modulation effect application."""
        # Test with modulation
        delay = Delay(modulation=0.5, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Modulated (0.50)" in result
        
        # Test without modulation
        delay = Delay(modulation=0, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Modulated" not in result

    def test_persistent_theme(self):
        """Test persistent theme application."""
        # Test with persistent theme
        theme = "Golden Gate Bridge"
        delay = Delay(persistent_theme=theme, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert f"Always connected to {theme}" in result
        
        # Test without persistent theme
        delay = Delay(persistent_theme=None, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "Always connected to" not in result

    def test_mix_method(self):
        """Test the _mix method's branches."""
        # Test wet-dominant mix (dry_wet=0.6 → 40% dry / 60% wet)
        delay = Delay(dry_wet=0.6)
        result = delay._mix("dry", "wet")
        assert "Dry (40%/60%):" in result
        assert "dry" in result
        assert "wet" in result
        
        # Test dry-dominant mix (dry_wet=0.4 → 60% dry / 40% wet)
        delay = Delay(dry_wet=0.4)
        result = delay._mix("dry", "wet")
        assert "Dry (60%/40%):" in result

    def test_time_info_formatting(self):
        """Test time info formatting with and without rate."""
        # Test with rate
        delay = Delay(rate="1/4", dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "at 1/4" in result
        
        # Test with time_ms
        delay = Delay(time_ms=300, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert "at 300.0ms" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
