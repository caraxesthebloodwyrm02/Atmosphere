"""
Comprehensive tests for echoes_essence module.
Tests the EchoesPlatform class and its processing chain.
"""

import pytest
from src.delay.core.echoes_essence import EchoesPlatform


class TestEchoesPlatformInitialization:
    """Test EchoesPlatform initialization."""

    def test_platform_initialization(self):
        """Test platform initializes with correct components."""
        platform = EchoesPlatform()
        
        assert platform.delay_line == "Trajectory Optimizer"
        assert platform.echo_chamber == "Multi-Agent Orchestrator"
        assert platform.reverb_plate == "Knowledge Graph"
        assert platform.master_controls == "Security & MLOps"

    def test_platform_components_are_strings(self):
        """Test all components are string representations."""
        platform = EchoesPlatform()
        
        assert isinstance(platform.delay_line, str)
        assert isinstance(platform.echo_chamber, str)
        assert isinstance(platform.reverb_plate, str)
        assert isinstance(platform.master_controls, str)


class TestEchoesPlatformProcessing:
    """Test EchoesPlatform processing chain."""

    def test_process_input_basic(self):
        """Test basic input processing through full chain."""
        platform = EchoesPlatform()
        result = platform.process_input("Test query")
        
        assert isinstance(result, str)
        assert "Test query" in result
        assert "Controlled" in result

    def test_process_chain_order(self):
        """Test processing follows correct order: Delay -> Echo -> Reverb -> Control."""
        platform = EchoesPlatform()
        result = platform.process_input("Signal")
        
        # Should contain all stages
        assert "Delayed" in result
        assert "Echoed" in result
        assert "Reverberated" in result
        assert "Controlled" in result
        
        # Chain nests: Controlled: Reverberated: Echoed: Delayed: Signal
        # So Controlled appears first, then Reverberated, etc.
        assert result.startswith("Controlled:")
        assert "Reverberated:" in result
        assert "Echoed:" in result
        assert "Delayed:" in result

    def test_process_empty_input(self):
        """Test processing with empty input."""
        platform = EchoesPlatform()
        result = platform.process_input("")
        
        assert isinstance(result, str)
        assert "Controlled" in result

    def test_process_special_characters(self):
        """Test processing with special characters."""
        platform = EchoesPlatform()
        special_input = "Query with !@#$%^&*() characters"
        result = platform.process_input(special_input)
        
        assert special_input in result
        assert "Controlled" in result

    def test_process_long_input(self):
        """Test processing with long input."""
        platform = EchoesPlatform()
        long_input = "A" * 1000
        result = platform.process_input(long_input)
        
        assert long_input in result
        assert "Controlled" in result


class TestEchoesPlatformInternalMethods:
    """Test internal processing methods."""

    def test_apply_delay(self):
        """Test delay application."""
        platform = EchoesPlatform()
        result = platform._apply_delay("Signal")
        
        assert result == "Delayed: Signal"
        assert "Delayed" in result

    def test_apply_echo(self):
        """Test echo application."""
        platform = EchoesPlatform()
        result = platform._apply_echo("Signal")
        
        assert result == "Echoed: Signal"
        assert "Echoed" in result

    def test_apply_reverb(self):
        """Test reverb application."""
        platform = EchoesPlatform()
        result = platform._apply_reverb("Signal")
        
        assert result == "Reverberated: Signal"
        assert "Reverberated" in result

    def test_apply_master_controls(self):
        """Test master controls application."""
        platform = EchoesPlatform()
        result = platform._apply_master_controls("Signal")
        
        assert result == "Controlled: Signal"
        assert "Controlled" in result


class TestEchoesPlatformChainIntegration:
    """Test integration of processing chain components."""

    def test_delay_to_echo_flow(self):
        """Test signal flows from delay to echo correctly."""
        platform = EchoesPlatform()
        
        delayed = platform._apply_delay("Input")
        echoed = platform._apply_echo(delayed)
        
        assert "Delayed: Input" in echoed
        assert "Echoed" in echoed

    def test_echo_to_reverb_flow(self):
        """Test signal flows from echo to reverb correctly."""
        platform = EchoesPlatform()
        
        delayed = platform._apply_delay("Input")
        echoed = platform._apply_echo(delayed)
        reverberated = platform._apply_reverb(echoed)
        
        assert "Echoed: Delayed: Input" in reverberated
        assert "Reverberated" in reverberated

    def test_reverb_to_control_flow(self):
        """Test signal flows from reverb to control correctly."""
        platform = EchoesPlatform()
        
        delayed = platform._apply_delay("Input")
        echoed = platform._apply_echo(delayed)
        reverberated = platform._apply_reverb(echoed)
        controlled = platform._apply_master_controls(reverberated)
        
        assert "Reverberated: Echoed: Delayed: Input" in controlled
        assert "Controlled" in controlled

    def test_full_chain_equals_process_input(self):
        """Test manual chain equals process_input result."""
        platform = EchoesPlatform()
        input_signal = "Test"
        
        # Manual chain
        delayed = platform._apply_delay(input_signal)
        echoed = platform._apply_echo(delayed)
        reverberated = platform._apply_reverb(echoed)
        manual_result = platform._apply_master_controls(reverberated)
        
        # Automated chain
        auto_result = platform.process_input(input_signal)
        
        assert manual_result == auto_result


class TestEchoesPlatformMultipleInstances:
    """Test multiple platform instances."""

    def test_multiple_instances_independent(self):
        """Test multiple platform instances are independent."""
        platform1 = EchoesPlatform()
        platform2 = EchoesPlatform()
        
        result1 = platform1.process_input("Query1")
        result2 = platform2.process_input("Query2")
        
        assert "Query1" in result1
        assert "Query2" in result2
        assert result1 != result2

    def test_instance_state_isolation(self):
        """Test instance state doesn't leak between instances."""
        platform1 = EchoesPlatform()
        platform2 = EchoesPlatform()
        
        # Modify platform1
        platform1.delay_line = "Modified Delay"
        
        # platform2 should be unchanged
        assert platform2.delay_line == "Trajectory Optimizer"
        assert platform1.delay_line == "Modified Delay"


class TestEchoesPlatformEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_unicode_input(self):
        """Test processing with unicode characters."""
        platform = EchoesPlatform()
        unicode_input = "Query with émojis 🎵🎶 and ñ characters"
        result = platform.process_input(unicode_input)
        
        assert unicode_input in result

    def test_newline_input(self):
        """Test processing with newline characters."""
        platform = EchoesPlatform()
        multiline_input = "Line 1\nLine 2\nLine 3"
        result = platform.process_input(multiline_input)
        
        assert multiline_input in result
        assert "Controlled" in result

    def test_numeric_string_input(self):
        """Test processing with numeric strings."""
        platform = EchoesPlatform()
        numeric_input = "12345"
        result = platform.process_input(numeric_input)
        
        assert numeric_input in result

    def test_whitespace_only_input(self):
        """Test processing with whitespace-only input."""
        platform = EchoesPlatform()
        whitespace_input = "   \t\n   "
        result = platform.process_input(whitespace_input)
        
        assert isinstance(result, str)
        assert "Controlled" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
