"""
Comprehensive unit tests for Compass CLI tools
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import argparse

# Import the compass modules
from compass import (
    Module, Phase, OracularState, DEFAULT_STATE, PROPHECY_PHASES,
    read_state_from_json, merge_dict, merge_state, progress_bar,
    render_header, render_phase_selector, render_phase_view,
    render_map, render_module, main
)

from compass_tool import (
    read_state_from_json as read_state_tool,
    merge_state as merge_state_tool,
    progress_bar as progress_bar_tool,
    render_header as render_header_tool,
    render_phase_selector as render_phase_selector_tool,
    render_phase_view as render_phase_view_tool,
    render_map as render_map_tool,
    render_module as render_module_tool,
    main as main_tool
)


class TestDataModels:
    """Test data model classes."""

    def test_module_creation(self):
        """Test Module dataclass creation."""
        module = Module(
            name="test_module.py",
            coverage=75,
            terrain="🌲 Forest",
            energy="strong"
        )

        assert module.name == "test_module.py"
        assert module.coverage == 75
        assert module.terrain == "🌲 Forest"
        assert module.energy == "strong"

    def test_phase_creation(self):
        """Test Phase dataclass creation."""
        phase = Phase(
            id=1,
            name="Test Phase",
            subtitle="Test subtitle",
            celestial_event="🌅 Dawn",
            duration="1 week",
            current_coverage=10,
            target_coverage=30,
            cosmic_alignment="Test alignment",
            overview="Test overview",
            key_actions=[{"action": "test", "impact": "high"}],
            expected_outcome={"result": "success"},
            rituals=["test ritual"],
            warnings=["test warning"]
        )

        assert phase.id == 1
        assert phase.name == "Test Phase"
        assert len(phase.key_actions) == 1
        assert phase.expected_outcome["result"] == "success"

    def test_oracular_state_creation(self):
        """Test OracularState dataclass creation."""
        modules = [Module("test.py", 50, "🏜️ Desert", "awakening")]
        state = OracularState(
            coverage=25,
            target=80,
            passing_tests=100,
            failing_tests=20,
            total_tests=120,
            modules=modules
        )

        assert state.coverage == 25
        assert state.target == 80
        assert len(state.modules) == 1
        assert state.modules[0].name == "test.py"

    def test_default_state(self):
        """Test DEFAULT_STATE has expected values."""
        assert DEFAULT_STATE.coverage == 16
        assert DEFAULT_STATE.target == 80
        assert DEFAULT_STATE.passing_tests == 108
        assert DEFAULT_STATE.failing_tests == 42
        assert DEFAULT_STATE.total_tests == 150
        assert len(DEFAULT_STATE.modules) == 4


class TestUtilityFunctions:
    """Test utility functions."""

    def test_progress_bar(self):
        """Test progress bar generation."""
        # Test normal values
        assert progress_bar(0.0) == "[------------------------------]"
        assert progress_bar(0.5) == "[###############---------------]"
        assert progress_bar(1.0) == "[##############################]"

        # Test invalid values
        with pytest.raises(ValueError):
            progress_bar(-0.1)
        with pytest.raises(ValueError):
            progress_bar(1.1)

    def test_merge_dict(self):
        """Test dictionary merging."""
        dst = {"a": 1, "b": {"x": 10}}
        src = {"b": {"y": 20}, "c": 3}

        result = merge_dict(dst, src)

        assert result["a"] == 1
        assert result["b"]["x"] == 10
        assert result["b"]["y"] == 20
        assert result["c"] == 3

    def test_merge_state(self):
        """Test state merging."""
        state = OracularState(
            coverage=10,
            target=50,
            passing_tests=80,
            failing_tests=20,
            total_tests=100,
            modules=[]
        )

        update = {
            "coverage": 25,
            "modules": [
                {"name": "new_module.py", "coverage": 60, "terrain": "🌲 Forest", "energy": "strong"}
            ]
        }

        result = merge_state(state, update)

        assert result.coverage == 25
        assert result.target == 50  # Unchanged
        assert len(result.modules) == 1
        assert result.modules[0].name == "new_module.py"


class TestJSONHandling:
    """Test JSON loading and saving."""

    def test_read_state_from_json(self):
        """Test reading state from JSON file."""
        json_data = {
            "coverage": 30,
            "target": 85,
            "passingTests": 120,
            "failingTests": 10,
            "totalTests": 130,
            "modules": [
                {
                    "name": "test_module.py",
                    "coverage": 70,
                    "terrain": "🌲 Forest",
                    "energy": "strong"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            temp_path = Path(f.name)

        try:
            state = read_state_from_json(temp_path)

            assert state.coverage == 30
            assert state.target == 85
            assert state.passing_tests == 120
            assert len(state.modules) == 1
            assert state.modules[0].name == "test_module.py"
        finally:
            temp_path.unlink()

    def test_read_state_invalid_file(self):
        """Test reading from non-existent file."""
        with pytest.raises(FileNotFoundError):
            read_state_from_json(Path("nonexistent.json"))


class TestRenderingFunctions:
    """Test rendering functions."""

    @patch('compass.console')
    def test_render_header(self, mock_console):
        """Test header rendering."""
        state = OracularState(coverage=40, target=80, passing_tests=0, failing_tests=0, total_tests=0)
        render_header(state)

        # Verify console.print was called
        mock_console.print.assert_called()

    @patch('compass.console')
    def test_render_phase_selector(self, mock_console):
        """Test phase selector rendering."""
        render_phase_selector(1)

        mock_console.print.assert_called()

    @patch('compass.console')
    def test_render_phase_view(self, mock_console):
        """Test phase view rendering."""
        phase = PROPHECY_PHASES[0]
        render_phase_view(phase)

        # Should call console.print multiple times
        assert mock_console.print.call_count > 1

    @patch('compass.console')
    def test_render_map(self, mock_console):
        """Test map rendering."""
        state = DEFAULT_STATE
        render_map(state)

        mock_console.print.assert_called()

    @patch('compass.console')
    def test_render_module_found(self, mock_console):
        """Test module rendering when module exists."""
        state = DEFAULT_STATE
        render_module(state, "core/security.py")

        mock_console.print.assert_called()

    @patch('compass.console')
    def test_render_module_not_found(self, mock_console):
        """Test module rendering when module doesn't exist."""
        state = DEFAULT_STATE
        render_module(state, "nonexistent.py")

        mock_console.print.assert_called()


class TestCLIArguments:
    """Test CLI argument parsing."""

    @patch('compass.render_module')
    def test_main_module_view(self, mock_render):
        """Test main function with module argument."""
        with patch('sys.argv', ['compass.py', '--module', 'test.py']):
            main(['--module', 'test.py'])

        mock_render.assert_called_once()

    @patch('compass.render_phase_view')
    def test_main_phase_view(self, mock_render):
        """Test main function with phase argument."""
        with patch('sys.argv', ['compass.py', '--phase', '1']):
            main(['--phase', '1'])

        mock_render.assert_called_once()

    @patch('compass.render_map')
    def test_main_map_view(self, mock_render):
        """Test main function with map argument."""
        with patch('sys.argv', ['compass.py', '--map']):
            main(['--map'])

        mock_render.assert_called_once()

    @patch('compass.read_state_from_json')
    def test_main_state_loading(self, mock_read):
        """Test main function with state file."""
        mock_state = DEFAULT_STATE
        mock_read.return_value = mock_state

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"coverage": 50}, f)
            temp_path = f.name

        try:
            with patch('compass.render_map'):
                main(['--state', temp_path, '--map'])

            mock_read.assert_called_once_with(Path(temp_path))
        finally:
            Path(temp_path).unlink()

    @patch('compass.merge_state')
    @patch('compass.render_map')
    def test_main_settings_merge(self, mock_render, mock_merge):
        """Test main function with settings file."""
        mock_merge.return_value = DEFAULT_STATE

        settings_data = {"coverage": 75}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(settings_data, f)
            temp_path = f.name

        try:
            main(['--settings', temp_path, '--map'])

            mock_merge.assert_called_once()
        finally:
            Path(temp_path).unlink()


class TestCompassToolFunctions:
    """Test compass_tool specific functions."""

    def test_tool_read_state_from_json(self):
        """Test reading state from JSON in compass_tool."""
        json_data = {
            "coverage": 40,
            "target": 90,
            "passingTests": 140,
            "failingTests": 10,
            "totalTests": 150,
            "modules": [
                {
                    "name": "tool_module.py",
                    "coverage": 80,
                    "terrain": "🏔️ Summit",
                    "energy": "peak"
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(json_data, f)
            temp_path = Path(f.name)

        try:
            state = read_state_tool(temp_path)

            assert state.coverage == 40
            assert state.target == 90
            assert len(state.modules) == 1
            assert state.modules[0].name == "tool_module.py"
        finally:
            temp_path.unlink()

    def test_tool_merge_state(self):
        """Test state merging in compass_tool."""
        state = OracularState(
            coverage=20,
            target=70,
            passing_tests=90,
            failing_tests=30,
            total_tests=120,
            modules=[]
        )

        update = {
            "coverage": 35,
            "modules": [
                {"name": "merged_module.py", "coverage": 65, "terrain": "🌾 Plains", "energy": "balanced"}
            ]
        }

        result = merge_state_tool(state, update)

        assert result.coverage == 35
        assert result.target == 70  # Unchanged
        assert len(result.modules) == 1

    def test_tool_progress_bar(self):
        """Test progress bar in compass_tool."""
        # Test basic functionality
        assert progress_bar_tool(0.0) == "[------------------------------]"
        assert progress_bar_tool(1.0) == "[##############################]"

        # Test invalid input
        with pytest.raises(ValueError):
            progress_bar_tool(-0.1)
        with pytest.raises(ValueError):
            progress_bar_tool(1.1)


class TestCompassToolCLI:
    """Test compass_tool CLI functionality."""

    @patch('compass_tool.console')
    def test_tool_render_module_found(self, mock_console):
        """Test module rendering in compass_tool when module exists."""
        state = DEFAULT_STATE
        render_module_tool(state, "core/security.py")

        mock_console.print.assert_called()

    @patch('compass_tool.console')
    def test_tool_render_module_not_found(self, mock_console):
        """Test module rendering in compass_tool when module doesn't exist."""
        state = DEFAULT_STATE
        render_module_tool(state, "nonexistent.py")

        # Should print error message
        mock_console.print.assert_called()

    @patch('compass_tool.render_map')
    def test_tool_main_map_view(self, mock_render):
        """Test compass_tool main with map view."""
        main_tool(['--map'])

        mock_render.assert_called_once()

    @patch('compass_tool.render_module')
    def test_tool_main_module_view(self, mock_render):
        """Test compass_tool main with module view."""
        main_tool(['--module', 'test.py'])

        mock_render.assert_called_once()

    @patch('compass_tool.render_phase_view')
    def test_tool_main_phase_view(self, mock_render):
        """Test compass_tool main with phase view."""
        main_tool(['--phase', '1'])

        mock_render.assert_called_once()


class TestIntegration:
    """Integration tests for compass functionality."""

    def test_full_state_workflow(self):
        """Test complete workflow from JSON to rendering."""
        # Create a test state
        test_state = OracularState(
            coverage=45,
            target=85,
            passing_tests=135,
            failing_tests=15,
            total_tests=150,
            modules=[
                Module("integration_test.py", 75, "🌲 Forest", "strong"),
                Module("another_test.py", 30, "🏜️ Desert", "awakening")
            ]
        )

        # Test progress calculation
        progress = test_state.coverage / test_state.target
        assert progress == 45/85

        # Test module access
        assert len(test_state.modules) == 2
        assert test_state.modules[0].coverage == 75
        assert test_state.modules[1].terrain == "🏜️ Desert"

    def test_phase_data_integrity(self):
        """Test that phase data is properly structured."""
        assert len(PROPHECY_PHASES) == 4

        for phase in PROPHECY_PHASES:
            assert phase.id >= 1
            assert phase.name
            assert phase.current_coverage >= 0
            assert phase.target_coverage >= phase.current_coverage
            assert len(phase.key_actions) > 0
            assert "confidence" in phase.expected_outcome
            assert len(phase.rituals) > 0

    def test_module_coverage_calculation(self):
        """Test module coverage categorization."""
        # This would test the terrain assignment logic
        # For now, just verify the default modules have expected properties
        security_module = None
        for module in DEFAULT_STATE.modules:
            if "security" in module.name:
                security_module = module
                break

        assert security_module is not None
        assert security_module.coverage == 59
        assert "Forest" in security_module.terrain


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
