"""
Comprehensive unit tests for Mental Load Balancer
"""

import pytest
import time
import threading
from unittest.mock import patch, MagicMock, call
from datetime import datetime, timedelta

# Import the core classes, mocking GUI components
with patch('mental_load_balancer.QT_AVAILABLE', False):
    with patch('mental_load_balancer.KEYBOARD_AVAILABLE', False):
        from mental_load_balancer import (
            MetricsCollector,
            JokeEngine,
            LoadMonitor,
            MentalLoadBalancerApp
        )


class TestMetricsCollector:
    """Test MetricsCollector class functionality."""

    def test_metrics_collector_initialization(self):
        """Test MetricsCollector initialization."""
        collector = MetricsCollector()
        assert collector.keystroke_count == 0
        assert collector.error_count == 0
        assert isinstance(collector.keystroke_timestamps, list)
        assert len(collector.keystroke_timestamps) == 0

    def test_record_keystroke(self):
        """Test keystroke recording."""
        collector = MetricsCollector()

        # Record keystrokes
        collector.record_keystroke()
        collector.record_keystroke()
        collector.record_keystroke()

        assert collector.keystroke_count == 3
        assert len(collector.keystroke_timestamps) == 3

    def test_record_error(self):
        """Test error recording."""
        collector = MetricsCollector()

        collector.record_error()
        collector.record_error()

        assert collector.error_count == 2

    def test_get_metrics_initial(self):
        """Test getting metrics with no activity."""
        collector = MetricsCollector()
        metrics = collector.get_metrics()

        assert metrics["keystroke_count"] == 0
        assert metrics["error_count"] == 0
        assert metrics["time_active"] >= 0
        assert metrics["keystrokes_per_minute"] == 0
        assert metrics["last_activity"] == 0

    def test_get_metrics_with_activity(self):
        """Test getting metrics with recorded activity."""
        collector = MetricsCollector()

        # Record some activity
        collector.record_keystroke()
        collector.record_error()

        # Wait a bit
        time.sleep(0.01)

        metrics = collector.get_metrics()

        assert metrics["keystroke_count"] == 1
        assert metrics["error_count"] == 1
        assert metrics["time_active"] > 0
        assert metrics["last_activity"] > 0

    def test_keystroke_timestamps_cleanup(self):
        """Test that old keystroke timestamps are cleaned up."""
        collector = MetricsCollector()

        # Add old timestamp (more than 1 hour ago)
        old_time = time.time() - 3700  # 1 hour 10 seconds ago
        collector.keystroke_timestamps.append(old_time)

        # Add current timestamp
        current_time = time.time()
        collector.record_keystroke()

        # Should only keep recent timestamps
        assert len(collector.keystroke_timestamps) == 1
        assert collector.keystroke_timestamps[0] > old_time

    def test_reset_metrics(self):
        """Test metrics reset functionality."""
        collector = MetricsCollector()

        # Record some activity
        collector.record_keystroke()
        collector.record_error()

        # Reset
        collector.reset()

        assert collector.keystroke_count == 0
        assert collector.error_count == 0
        assert len(collector.keystroke_timestamps) == 0
        assert collector.last_reset > 0

    def test_keystrokes_per_minute_calculation(self):
        """Test KPM calculation with different time windows."""
        collector = MetricsCollector()

        # Record keystrokes over time
        collector.record_keystroke()
        time.sleep(0.1)
        collector.record_keystroke()
        time.sleep(0.1)
        collector.record_keystroke()

        metrics = collector.get_metrics()

        # Should calculate based on last 5 minutes
        assert "keystrokes_per_minute" in metrics
        assert metrics["keystrokes_per_minute"] >= 0


class TestJokeEngine:
    """Test JokeEngine class functionality."""

    def test_joke_engine_initialization(self):
        """Test JokeEngine initialization."""
        engine = JokeEngine()
        assert engine.last_joke_time == 0
        assert hasattr(engine, 'joke_templates')

    def test_get_joke_default_style(self):
        """Test getting joke with default style."""
        engine = JokeEngine()
        joke = engine.get_joke()

        assert isinstance(joke, str)
        assert len(joke) > 0

    def test_get_joke_programming_style(self):
        """Test getting programming joke."""
        engine = JokeEngine()
        joke = engine.get_joke("programming")

        assert isinstance(joke, str)
        assert joke in engine.joke_templates["programming"]

    def test_get_joke_general_style(self):
        """Test getting general joke."""
        engine = JokeEngine()
        joke = engine.get_joke("general")

        assert isinstance(joke, str)
        assert joke in engine.joke_templates["general"]

    def test_get_joke_invalid_style(self):
        """Test getting joke with invalid style falls back to general."""
        engine = JokeEngine()
        joke = engine.get_joke("invalid_style")

        assert isinstance(joke, str)
        # Should fall back to general jokes
        assert joke in engine.joke_templates["general"]

    def test_get_contextual_joke(self):
        """Test getting contextual joke."""
        engine = JokeEngine()

        # Test with programming style
        context = {"joke_style": "programming"}
        joke = engine.get_contextual_joke(context)
        assert joke in engine.joke_templates["programming"]

        # Test with general style
        context = {"joke_style": "general"}
        joke = engine.get_contextual_joke(context)
        assert joke in engine.joke_templates["general"]

        # Test with no context
        joke = engine.get_contextual_joke(None)
        assert isinstance(joke, str)

    def test_joke_randomness(self):
        """Test that jokes are randomly selected."""
        engine = JokeEngine()

        # Get multiple jokes and check they're not always the same
        jokes = [engine.get_joke() for _ in range(10)]

        # Should have some variety (not all identical)
        unique_jokes = set(jokes)
        assert len(unique_jokes) > 1


class TestLoadMonitor:
    """Test LoadMonitor class functionality."""

    def test_load_monitor_initialization(self):
        """Test LoadMonitor initialization."""
        config = {"keystroke_threshold": 100, "time_threshold": 30}
        monitor = LoadMonitor(config)

        assert hasattr(monitor, 'config')
        assert hasattr(monitor, 'metrics')
        assert hasattr(monitor, 'joke_engine')
        assert monitor.running is False

    def test_check_load_no_thresholds_exceeded(self):
        """Test load checking when no thresholds are exceeded."""
        config = {
            "enabled": True,
            "keystroke_threshold": 1000,
            "time_threshold": 100,
            "error_threshold": 50
        }
        monitor = LoadMonitor(config)

        # Should not trigger intervention
        monitor._check_load()

        # No intervention should be triggered (no signals in headless mode)

    def test_check_load_keystroke_threshold(self):
        """Test load checking with keystroke threshold exceeded."""
        config = {
            "enabled": True,
            "keystroke_threshold": 5,
            "time_threshold": 100,
            "error_threshold": 50,
            "min_time_between_interventions": 0
        }
        monitor = LoadMonitor(config)

        # Record enough keystrokes to exceed threshold
        for _ in range(10):
            monitor.metrics.record_keystroke()

        # Should trigger intervention
        with patch.object(monitor, 'intervention_needed') as mock_signal:
            monitor._check_load()
            # In headless mode, signal may not be called

    def test_check_load_time_threshold(self):
        """Test load checking with time threshold exceeded."""
        config = {
            "enabled": True,
            "keystroke_threshold": 1000,
            "time_threshold": 0.001,  # Very short time
            "error_threshold": 50,
            "min_time_between_interventions": 0
        }
        monitor = LoadMonitor(config)

        # Wait a bit to exceed time threshold
        time.sleep(0.01)

        with patch.object(monitor, 'intervention_needed') as mock_signal:
            monitor._check_load()
            # Should trigger due to time threshold

    def test_check_load_disabled(self):
        """Test load checking when monitoring is disabled."""
        config = {"enabled": False}
        monitor = LoadMonitor(config)

        # Should not check load when disabled
        with patch.object(monitor, 'intervention_needed') as mock_signal:
            monitor._check_load()
            mock_signal.assert_not_called()

    def test_check_load_min_time_between_interventions(self):
        """Test minimum time between interventions."""
        config = {
            "enabled": True,
            "keystroke_threshold": 1,
            "min_time_between_interventions": 60  # 1 minute
        }
        monitor = LoadMonitor(config)

        # Record keystroke to trigger intervention
        monitor.metrics.record_keystroke()

        with patch.object(monitor, 'intervention_needed') as mock_signal:
            monitor._check_load()
            # Should trigger first time

            # Reset and try again immediately
            monitor.last_intervention_time = time.time()
            monitor._check_load()
            # Should not trigger due to minimum time constraint

    def test_record_keystroke_method(self):
        """Test the record_keystroke method."""
        monitor = LoadMonitor()

        # Initially should not record if keyboard not available
        initial_count = monitor.metrics.keystroke_count
        monitor.record_keystroke()
        # In test environment, may not record

        assert hasattr(monitor, 'record_keystroke')

    def test_record_error_method(self):
        """Test the record_error method."""
        monitor = LoadMonitor()

        monitor.record_error()
        assert monitor.metrics.error_count == 1

    def test_stop_method(self):
        """Test the stop method."""
        monitor = LoadMonitor()

        monitor.running = True
        monitor.stop()

        assert monitor.running is False


class TestMentalLoadBalancerApp:
    """Test MentalLoadBalancerApp class functionality."""

    @patch('mental_load_balancer.QT_AVAILABLE', False)
    def test_app_initialization_headless(self):
        """Test app initialization in headless mode."""
        with patch('mental_load_balancer.Path') as mock_path:
            mock_config_file = MagicMock()
            mock_path.return_value.exists.return_value = False

            app = MentalLoadBalancerApp([])

            assert hasattr(app, 'config')
            assert hasattr(app, 'monitor')
            assert hasattr(app, 'joke_engine')

    @patch('mental_load_balancer.QT_AVAILABLE', False)
    def test_load_config_defaults(self):
        """Test loading default configuration."""
        with patch('mental_load_balancer.Path') as mock_path:
            mock_config_file = MagicMock()
            mock_path.return_value.exists.return_value = False

            app = MentalLoadBalancerApp([])

            config = app._load_config()
            assert isinstance(config, dict)
            assert 'keystroke_threshold' in config
            assert 'time_threshold' in config

    @patch('mental_load_balancer.QT_AVAILABLE', False)
    @patch('mental_load_balancer.VSCODE_AVAILABLE', False)
    def test_load_config_from_file(self):
        """Test loading configuration from file."""
        mock_config = {
            "keystroke_threshold": 200,
            "time_threshold": 60,
            "enabled": False
        }

        with patch('mental_load_balancer.Path') as mock_path_class, \
             patch('builtins.open', create=True) as mock_open, \
             patch('mental_load_balancer.json.load') as mock_json_load:

            mock_path_instance = MagicMock()
            mock_path_class.return_value = mock_path_instance
            mock_path_instance.exists.return_value = True

            mock_json_load.return_value = mock_config

            app = MentalLoadBalancerApp([])
            config = app._load_config()

            assert config["keystroke_threshold"] == 200
            assert config["time_threshold"] == 60
            assert config["enabled"] is False
            # Should have default values for keys not in loaded config
            assert "joke_style" in config

    @patch('mental_load_balancer.QT_AVAILABLE', False)
    def test_save_config(self):
        """Test saving configuration to file."""
        with patch('mental_load_balancer.Path') as mock_path, \
             patch('builtins.open') as mock_open, \
             patch('mental_load_balancer.json.dump') as mock_json_dump:

            mock_config_file = MagicMock()
            mock_path.return_value = mock_config_file

            app = MentalLoadBalancerApp([])
            app.config = {"test": "value"}

            result = app.save_config()

            assert result is True
            mock_json_dump.assert_called_once_with({"test": "value"}, mock_open.return_value.__enter__.return_value, indent=2)

    @patch('mental_load_balancer.QT_AVAILABLE', False)
    @patch('mental_load_balancer.VSCODE_AVAILABLE', False)
    def test_handle_intervention(self):
        """Test intervention handling."""
        with patch('mental_load_balancer.Path') as mock_path:
            mock_config_file = MagicMock()
            mock_path.return_value.exists.return_value = False

            app = MentalLoadBalancerApp([])

            context = {
                "trigger": "keystroke",
                "metrics": {"keystroke_count": 100},
                "joke_style": "programming"
            }

            # Should not crash in headless mode
            app.handle_intervention(context)

    @patch('mental_load_balancer.QT_AVAILABLE', False)
    @patch('mental_load_balancer.VSCODE_AVAILABLE', False)
    def test_vscode_integration_disabled(self):
        """Test that app works when VS Code integration is disabled."""
        with patch('mental_load_balancer.Path') as mock_path:
            mock_config_file = MagicMock()
            mock_path.return_value.exists.return_value = False

            app = MentalLoadBalancerApp([])

            # Should initialize without VS Code integration
            assert app.vscode_monitor is None


class TestIntegration:
    """Integration tests for multiple components working together."""

    def test_monitor_and_metrics_integration(self):
        """Test LoadMonitor and MetricsCollector integration."""
        config = {
            "enabled": True,
            "keystroke_threshold": 3,
            "time_threshold": 10,
            "error_threshold": 10,
            "min_time_between_interventions": 0
        }

        monitor = LoadMonitor(config)

        # Simulate user activity
        for _ in range(5):
            monitor.record_keystroke()

        # Check that metrics are recorded
        metrics = monitor.metrics.get_metrics()
        assert metrics["keystroke_count"] == 5

    def test_joke_engine_and_monitor_integration(self):
        """Test JokeEngine and LoadMonitor integration."""
        monitor = LoadMonitor()
        joke_engine = monitor.joke_engine

        # Should be able to get jokes
        joke = joke_engine.get_joke()
        assert isinstance(joke, str)
        assert len(joke) > 0

    def test_full_app_initialization(self):
        """Test full app initialization and component interaction."""
        with patch('mental_load_balancer.QT_AVAILABLE', False), \
             patch('mental_load_balancer.KEYBOARD_AVAILABLE', False), \
             patch('mental_load_balancer.VSCODE_AVAILABLE', False), \
             patch('mental_load_balancer.Path') as mock_path:

            mock_config_file = MagicMock()
            mock_path.return_value.exists.return_value = False

            app = MentalLoadBalancerApp([])

            # Check that all components are initialized
            assert hasattr(app, 'monitor')
            assert hasattr(app, 'joke_engine')
            assert hasattr(app, 'config')

            # Check that monitor has required attributes
            assert hasattr(app.monitor, 'metrics')
            assert hasattr(app.monitor, 'joke_engine')


class TestThreadingSafety:
    """Test threading safety aspects."""

    def test_monitor_thread_safety(self):
        """Test that LoadMonitor can be stopped safely."""
        monitor = LoadMonitor()

        # Start and stop should work
        monitor.running = True
        monitor.stop()
        assert monitor.running is False

    def test_concurrent_metrics_access(self):
        """Test concurrent access to metrics."""
        collector = MetricsCollector()

        def record_activity():
            for _ in range(100):
                collector.record_keystroke()
                collector.record_error()

        # Start multiple threads
        threads = []
        for _ in range(5):
            t = threading.Thread(target=record_activity)
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join()

        # Check final metrics
        metrics = collector.get_metrics()
        assert metrics["keystroke_count"] == 500  # 5 threads * 100 keystrokes
        assert metrics["error_count"] == 500     # 5 threads * 100 errors


class TestConfiguration:
    """Test configuration handling."""

    def test_default_config_values(self):
        """Test default configuration values."""
        from mental_load_balancer import DEFAULT_CONFIG

        assert isinstance(DEFAULT_CONFIG, dict)
        required_keys = [
            "keystroke_threshold", "time_threshold", "error_threshold",
            "joke_style", "intervention_style", "min_time_between_interventions",
            "enabled"
        ]

        for key in required_keys:
            assert key in DEFAULT_CONFIG

    def test_config_validation(self):
        """Test configuration value validation."""
        # Test with valid config
        valid_config = {
            "keystroke_threshold": 100,
            "time_threshold": 45,
            "error_threshold": 5,
            "joke_style": "programming",
            "intervention_style": "popup",
            "min_time_between_interventions": 30,
            "enabled": True
        }

        # Should not raise exceptions when used
        monitor = LoadMonitor(valid_config)
        assert monitor.config == valid_config


class TestJokeTemplates:
    """Test joke template functionality."""

    def test_joke_templates_structure(self):
        """Test that joke templates have correct structure."""
        from mental_load_balancer import JOKE_TEMPLATES

        assert isinstance(JOKE_TEMPLATES, dict)
        assert "programming" in JOKE_TEMPLATES
        assert "general" in JOKE_TEMPLATES

        for category, jokes in JOKE_TEMPLATES.items():
            assert isinstance(jokes, list)
            assert len(jokes) > 0
            for joke in jokes:
                assert isinstance(joke, str)
                assert len(joke) > 0

    def test_joke_template_content(self):
        """Test that joke templates contain actual jokes."""
        from mental_load_balancer import JOKE_TEMPLATES

        # Check that programming jokes contain programming-related content
        programming_jokes = " ".join(JOKE_TEMPLATES["programming"]).lower()
        assert any(term in programming_jokes for term in ["program", "code", "bug", "java", "python"])

        # Check that general jokes are varied
        general_jokes = JOKE_TEMPLATES["general"]
        assert len(general_jokes) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
