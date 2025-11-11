"""
Enhanced tests for delay_essence module with additional coverage.
Focuses on edge cases and additional scenarios not covered in the main test file.
"""

"""
Enhanced tests for delay_essence module with additional coverage.
Focuses on edge cases and additional scenarios not covered in the main test file.
"""

import pytest
from src.atmosphere_audio.delay.core.delay_essence import Delay

class TestDelayEnhanced:
    """Enhanced test cases for Delay class."""

    @pytest.mark.parametrize("time_ms,expected_in_result", [
        (0, [" at 0.0ms"]),
        (10, [" at 10.0ms"]),
        (1000, [" at 1000.0ms"]),
        (10000, [" at 10000.0ms"]),
        (0.5, [" at 0.5ms"]),
        (-100, [" at 0.0ms"]),  # Should clamp to minimum
        (1e6, [f" at {int(20000)}.0ms"])  # Very large value gets clamped to 20000
    ])
    def test_time_values(self, time_ms, expected_in_result):
        """Test various time values including edge cases."""
        delay = Delay(time_ms=time_ms, dry_wet=0.6)
        result = delay.process_signal("Test")
        assert any(exp in result for exp in expected_in_result), \
            f"Expected one of {expected_in_result} in result: {result}"

    @pytest.mark.parametrize("feedback,expected_in_result", [
        (0.0, ["(feedback: 0.00)"]),
        (0.5, ["(feedback: 0.50)"]),
        (1.0, ["(feedback: 1.00)"]),
        (-0.1, ["(feedback: 0.00)"]),  # Should clamp to 0.0
        (1.1, ["(feedback: 1.00)"])     # Should clamp to 1.0
    ])
    def test_feedback_values(self, feedback, expected_in_result):
        """Test various feedback values including boundary conditions."""
        delay = Delay(feedback=feedback, dry_wet=0.7)
        result = delay.process_signal("Test")
        assert any(exp in result for exp in expected_in_result), \
            f"Expected one of {expected_in_result} in result: {result}"

    @pytest.mark.parametrize("delay_type,expected_in_result", [
        ("invalid_type", ["Digital echo:"]),  # Should fall back to digital
        ("ping_pong", ["Ping-pong echo:"]),
        ("slapback", ["Slapback echo:"]),
        ("doubling", ["Doubling echo:"]),
        ("digital", ["Digital echo:"]),
        ("analog", ["Analog echo:"]),
        ("tape", ["Tape echo:"]),
        ("", ["Digital echo:"]),  # Empty string should default to digital
        (None, ["Digital echo:"])   # None should default to digital
    ])
    def test_delay_types(self, delay_type, expected_in_result):
        """Test all delay types including invalid ones."""
        kwargs = {"dry_wet": 0.6}
        if delay_type is not None:
            kwargs["delay_type"] = delay_type
            
        delay = Delay(**kwargs)
        result = delay.process_signal("Test")
        assert any(exp in result for exp in expected_in_result), \
            f"Expected one of {expected_in_result} in result: {result}"

    @pytest.mark.parametrize("test_str,expected_in_result", [
        ("Special !@#$%^&*()_+{}|:<>?", ["Special !@#$%^&*()_+{}|:<>?"]),
        ("Unicode: こんにちは 你好", ["Unicode: こんにちは 你好"]),
        ("New\nLines\nEverywhere", ["New\nLines\nEverywhere"]),
        ("   Leading and trailing spaces   ", ["Leading and trailing spaces"]),
        ("", [""]),  # Empty string
        (" ", [""]),  # Whitespace only
        ("\t\n\r", [""]),  # Various whitespace characters
        ("A" * 1000, ["A" * 1000]),  # Very long string
        ("Null\x00Character", ["Null\x00Character"]),  # Null byte
        ("Quotes: 'single' and \"double\"", ["Quotes: 'single' and \"double\""]),
        ("Backslash: \\ and \'escaped\'", ["Backslash: \\ and 'escaped'"])
    ])
    def test_special_characters_in_signal(self, test_str, expected_in_result):
        """Test with special characters in input signal."""
        delay = Delay(dry_wet=0.6)
        result = delay.process_signal(test_str)
        # Should process without errors
        assert isinstance(result, str)
        # For empty/whitespace inputs, result should be empty
        if not test_str.strip():
            assert result == "", f"Expected empty result for whitespace input, got: {repr(result)}"
        else:
            # The original string (stripped) should be in the result
            assert any(exp in result for exp in expected_in_result if exp), \
                f"Expected one of {expected_in_result} in result: {result}"

    @pytest.mark.parametrize("chain_length", [2, 3, 5])
    def test_delay_chaining(self, chain_length):
        """Test chaining multiple delay instances with different configurations."""
        # Create a chain of delays with different settings
        delays = [
            Delay(
                time_ms=100 + (i * 50),  # Increasing delay time
                feedback=0.2 + (i * 0.1),  # Increasing feedback
                dry_wet=0.3 + (i * 0.1),  # Increasing wet/dry mix
                delay_type=["ping_pong", "slapback", "doubling"][i % 3]  # Rotate through types
            )
            for i in range(chain_length)
        ]
        
        # Process signal through the chain
        signal = "Chained"
        for delay in delays:
            signal = delay.process_signal(signal)
        
        # Verify the final result contains the original signal
        assert "Chained" in signal
        
        # Verify the chain preserved all delay characteristics
        for i, delay in enumerate(delays):
            if delay.delay_type == "ping_pong":
                assert "Ping-pong" in signal
            elif delay.delay_type == "slapback":
                assert "Slapback" in signal
            elif delay.delay_type == "doubling":
                assert "Doubling" in signal
        
        # Test with a very long chain (stress test)
        if chain_length == 5:
            long_chain = [Delay(time_ms=10, feedback=0.1, dry_wet=0.5) for _ in range(10)]
            signal = "LongChain"
            for delay in long_chain:
                signal = delay.process_signal(signal)
            assert "LongChain" in signal

    @pytest.mark.parametrize("theme,should_appear", [
        ("", False),  # Empty theme should not appear
        (" ", False),  # Whitespace theme should not appear
        ("\t\n", False),  # Whitespace characters should not appear
        ("Golden Gate", True),  # Normal theme
        ("A" * 1000, True),  # Very long theme
        ("!@#$%^&*()_+{}|:<>?", True),  # Special characters
        ("Unicode: こんにちは 你好", True),  # Unicode characters
        ("Quotes: 'single' and \"double\"", True),  # Quotes
        ("Backslash: \\ and \'escaped\'", True),  # Escaped characters
        (None, False)  # None should be treated as no theme
    ])
    def test_persistent_theme(self, theme, should_appear):
        """Test persistent theme with various inputs."""
        kwargs = {"dry_wet": 0.6}
        if theme is not None:
            kwargs["persistent_theme"] = theme
            
        delay = Delay(**kwargs)
        result = delay.process_signal("Test")
        
        if should_appear:
            assert theme in result, f"Theme '{theme}' should appear in: {result}"
        else:
            assert "Always connected to" not in result, \
                f"Theme should not appear but did in: {result}"

    @pytest.mark.parametrize("filter_type,filter_freq,expected_in_result", [
        ("lowpass", 20, ["Lowpass filtered (20Hz)"]),
        ("highpass", 20000, ["Highpass filtered (20000Hz)"]),
        ("bandpass", 1000, ["Bandpass filtered (1000Hz)"]),
        ("invalid_filter", 1000, []),  # Invalid type should not produce filter message
        ("lowpass", 10, ["Lowpass filtered (20Hz)"]),  # Below min should clamp to 20
        ("highpass", 30000, ["Highpass filtered (20000Hz)"]),  # Above max should clamp to 20000
        (None, 1000, []),  # No filter type should mean no filter message
        ("", 1000, [])  # Empty filter type should mean no filter message
    ])
    def test_filter_combinations(self, filter_type, filter_freq, expected_in_result):
        """Test various filter type and frequency combinations."""
        kwargs = {
            "dry_wet": 0.6,
            "filter_freq": filter_freq
        }
        if filter_type is not None:
            kwargs["filter_type"] = filter_type
            
        delay = Delay(**kwargs)
        result = delay.process_signal("Test")
        
        if expected_in_result:
            assert any(exp in result for exp in expected_in_result), \
                f"Expected one of {expected_in_result} in result: {result}"
        else:
            assert "filtered" not in result, \
                f"Expected no filter message but got: {result}"

    @pytest.mark.parametrize("modulation,expected_in_result,not_expected_in_result", [
        (0.0, [], ["Modulated"]),  # No modulation
        (0.1, ["Modulated (0.10)"], []),  # Low modulation
        (0.5, ["Modulated (0.50)"], []),  # Medium modulation
        (1.0, ["Modulated (1.00)"], []),  # Maximum modulation
        (-0.1, [], ["Modulated"]),  # Negative should be treated as 0
        (1.1, ["Modulated (1.00)"], []),  # Above max should clamp to 1.0
        (None, [], ["Modulated"]),  # None should be treated as 0
    ])
    def test_modulation_values(self, modulation, expected_in_result, not_expected_in_result):
        """Test modulation with various values including boundary conditions."""
        kwargs = {"dry_wet": 0.6}
        if modulation is not None:
            kwargs["modulation"] = modulation
            
        delay = Delay(**kwargs)
        result = delay.process_signal("Test")
        
        for exp in expected_in_result:
            assert exp in result, f"Expected '{exp}' in result: {result}"
            
        for not_exp in not_expected_in_result:
            assert not_exp not in result, f"Did not expect '{not_exp}' in result: {result}"

    @pytest.mark.parametrize("size_multiplier", [1, 10, 100, 1000])
    def test_memory_usage_with_large_signals(self, size_multiplier):
        """Test memory usage with increasingly large input signals."""
        large_signal = "A" * (1000 * size_multiplier)
        delay = Delay(dry_wet=0.6)
        
        # Process the signal
        result = delay.process_signal(large_signal)
        
        # Basic validation
        assert isinstance(result, str)
        assert len(result) >= len(large_signal)
            
        # Verify the signal integrity
        assert large_signal in result
        
        # Test with different delay types to ensure they all handle large inputs
        for delay_type in ["ping_pong", "slapback", "doubling"]:
            delay = Delay(delay_type=delay_type, dry_wet=0.6)
            result = delay.process_signal(large_signal)
            assert large_signal in result

    @pytest.mark.parametrize("dry_wet,expected_in_result", [
        (0.0, ["Dry (100%)"]),  # All dry
        (0.5, ["Dry (50%/50%)"]),  # 50/50 mix
        (1.0, ["Wet (100%)"]),  # All wet
        (-0.1, ["Dry (100%)"]),  # Below 0 should clamp to 0
        (1.1, ["Wet (100%)"]),  # Above 1 should clamp to 1
        (None, ["Dry (50%/50%)"])  # None should use default 0.5
    ])
    def test_dry_wet_mix(self, dry_wet, expected_in_result):
        """Test dry/wet mixing with various ratios."""
        kwargs = {}
        if dry_wet is not None:
            kwargs["dry_wet"] = dry_wet
            
        delay = Delay(**kwargs)
        result = delay.process_signal("MixTest")
        
        for exp in expected_in_result:
            assert exp in result, f"Expected '{exp}' in result: {result}"

    def test_concurrent_instances(self):
        """Test that multiple Delay instances don't interfere with each other."""
        # Create multiple instances with different settings
        delays = [
            Delay(time_ms=100, feedback=0.3, dry_wet=0.5, delay_type="ping_pong"),
            Delay(time_ms=200, feedback=0.5, dry_wet=0.7, delay_type="slapback"),
            Delay(time_ms=300, feedback=0.7, dry_wet=0.9, delay_type="doubling")
        ]
        
        # Process the same signal through each delay
        results = [delay.process_signal("Concurrent") for delay in delays]
        
        # Verify all results are different
        assert len(results) == len(set(results)), "All results should be unique"
        
        # Verify each delay applied its settings correctly
        assert "Ping-pong" in results[0]
        assert "Slapback" in results[1]
        assert "Doubling" in results[2]

    @pytest.mark.parametrize("method_name,args,expected_result", [
        ("_generate_standard_echo", ("Test",), ["Digital echo:"]),
        ("_generate_ping_pong_echo", ("Test",), ["Ping-pong echo:"]),
        ("_generate_slapback_echo", ("Test",), ["Slapback echo:"]),
        ("_generate_doubling_echo", ("Test",), ["Doubling echo:"]),
        ("_mix", ("Dry", "Wet"), ["Dry (50%/50%)"])
    ])
    def test_private_methods(self, method_name, args, expected_result):
        """Test internal methods directly for better coverage."""
        delay = Delay()
        method = getattr(delay, method_name)
        result = method(*args)
        
        if isinstance(expected_result, list):
            assert any(exp in result for exp in expected_result), \
                f"Expected one of {expected_result} in result: {result}"
        else:
            assert expected_result in result

    def test_module_docstring(self):
        """Test that the module has a docstring."""
        import src.atmosphere_audio.delay.core.delay_essence as delay_module
        assert delay_module.__doc__, "Module should have a docstring"
        assert len(delay_module.__doc__.split('\n')) > 5, "Module docstring should be descriptive"

    def test_class_docstring(self):
        """Test that the Delay class has a docstring."""
        from src.atmosphere_audio.delay.core.delay_essence import Delay
        assert Delay.__doc__, "Delay class should have a docstring"
        assert len(Delay.__doc__.split('\n')) > 10, "Delay class docstring should be descriptive"

    def test_method_docstrings(self):
        """Test that all public methods have docstrings."""
        from src.atmosphere_audio.delay.core.delay_essence import Delay
        
        # Get all public methods (not starting with _)
        methods = [
            name for name, member in vars(Delay).items()
            if callable(member) and not name.startswith('_')
        ]
        
        for method_name in methods:
            method = getattr(Delay, method_name)
            assert method.__doc__, f"Method {method_name} should have a docstring"
            assert len(method.__doc__.split('\n')) > 1, \
                f"Method {method_name} docstring should be descriptive"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.atmosphere_audio.delay.core.delay_essence", "--cov-report=term-missing"])
