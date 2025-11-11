#!/usr/bin/env python3
"""
Mental Load Balancer - A tool to help developers manage cognitive load
with timely, context-aware breaks and light-hearted interventions.
"""
import os
import sys
import json
import time
import random
import signal
import logging
import threading
import psutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Callable

# Try to import optional dependencies
try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except (ImportError, OSError):
    KEYBOARD_AVAILABLE = False
    print("Note: Keyboard monitoring is not available. Some features may be limited.")

# Try to import PyQt6
try:
    from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget,
                              QVBoxLayout, QLabel, QSlider, QPushButton, QComboBox,
                              QSpinBox, QFormLayout, QDialog, QMessageBox, QStyle)
    from PyQt6.QtGui import QIcon, QAction, QPixmap
    from PyQt6.QtCore import Qt, QTimer, QThread as QtQThread, pyqtSignal
    QT_AVAILABLE = True
    
    # Create alias for QThread when PyQt6 is available
    QThread = QtQThread
    
except ImportError:
    QT_AVAILABLE = False
    print("Note: PyQt6 is not available. Running in headless mode.")
    
    # Fallback implementation of QThread for headless mode
    class QThread:
        def __init__(self, parent=None):
            self.parent = parent
            self._is_running = False
            self.finished = None  # Signal placeholder
            self.started = None   # Signal placeholder

        def start(self):
            self._is_running = True
            if hasattr(self, 'run'):
                self.run()

        def run(self):
            pass

        def quit(self):
            self._is_running = False

        def wait(self):
            pass

        def isRunning(self):
            return self._is_running

        def terminate(self):
            self._is_running = False

# Try to import VS Code integration
try:
    from vscode_integration import VSCodeMonitor
    VSCODE_AVAILABLE = True
except ImportError:
    VSCODE_AVAILABLE = False
    print("VS Code extension API not available. Running in standalone mode.")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mental_load_balancer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MentalLoadBalancer')

# Default configuration
DEFAULT_CONFIG = {
    "keystroke_threshold": 500,
    "time_threshold": 45,  # minutes
    "error_threshold": 10,
    "joke_style": "programming",
    "intervention_style": "popup",
    "min_time_between_interventions": 30,  # minutes
    "enabled": True
}

# Joke templates
JOKE_TEMPLATES = {
    "programming": [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🌙",
        "Why was the JavaScript developer sad? He didn't Node how to Express himself! 💔",
        "Why do Java developers wear glasses? Because they don't C#! 👓",
        "Why do programmers hate nature? It has too many bugs! 🐞",
        "Why do programmers always mix up Halloween and Christmas? Because Oct 31 == Dec 25! 🎃🎄"
    ],
    "general": [
        "Why don't scientists trust atoms? Because they make up everything! ⚛️",
        "I told my wife she was drawing her eyebrows too high. She looked surprised! 😲",
        "What's the best thing about Switzerland? I don't know, but the flag is a big plus! 🇨🇭",
        "Did you hear about the mathematician who's afraid of negative numbers? He'll stop at nothing to avoid them! ➖",
        "I'm reading a book about anti-gravity. It's impossible to put down! 📚"
    ]
}

class MetricsCollector:
    """Collects and analyzes developer activity metrics."""
    
    def __init__(self):
        self.keystroke_count = 0
        self.error_count = 0
        self.last_reset = time.time()
        self.last_keystroke_time = 0
        self.keystroke_timestamps = []
        
    def record_keystroke(self):
        """Record a keystroke event."""
        current_time = time.time()
        self.keystroke_count += 1
        self.last_keystroke_time = current_time
        self.keystroke_timestamps.append(current_time)
        
        # Clean up old timestamps (keep last hour)
        one_hour_ago = current_time - 3600
        self.keystroke_timestamps = [t for t in self.keystroke_timestamps if t > one_hour_ago]
        
    def record_error(self):
        """Record an error event."""
        self.error_count += 1
        
    def get_metrics(self):
        """Get current metrics."""
        current_time = time.time()
        time_active = (current_time - self.last_reset) / 60  # in minutes
        
        # Calculate keystrokes per minute (last 5 minutes)
        five_min_ago = current_time - 300
        recent_keystrokes = sum(1 for t in self.keystroke_timestamps if t > five_min_ago)
        kpm = recent_keystrokes / 5 if recent_keystrokes > 0 else 0
        
        return {
            "keystroke_count": self.keystroke_count,
            "error_count": self.error_count,
            "time_active": time_active,
            "keystrokes_per_minute": kpm,
            "last_activity": self.last_keystroke_time
        }
    
    def reset(self):
        """Reset all metrics."""
        self.keystroke_count = 0
        self.error_count = 0
        self.last_reset = time.time()
        self.keystroke_timestamps = []


class JokeEngine:
    """Generates context-aware jokes and interventions."""
    
    def __init__(self):
        self.joke_templates = JOKE_TEMPLATES
        self.last_joke_time = 0
        
    def get_joke(self, style="programming"):
        """Get a random joke from the specified style."""
        jokes = self.joke_templates.get(style, [])
        if not jokes and style != "general":
            jokes = self.joke_templates["general"]
        return random.choice(jokes) if jokes else "Time for a quick break! 🚀"
    
    def get_contextual_joke(self, context=None):
        """Get a joke based on the current context."""
        style = context.get("joke_style", "programming") if context else "programming"
        return self.get_joke(style)


class LoadMonitor(QThread):
    """Monitors system and user activity to detect high cognitive load."""
    
    # Define the signal with a default None value that will be set if PyQt6 is available
    if QT_AVAILABLE:
        intervention_needed = pyqtSignal(dict)  # Signal when an intervention is needed
    else:
        intervention_needed = None
    
    def __init__(self, config=None):
        super().__init__()
        self.config = config or {}
        self.metrics = MetricsCollector()
        self.joke_engine = JokeEngine()
        self.running = False
        
        # Initialize metrics update signal if in GUI mode
        if QT_AVAILABLE:
            self.update_metrics = pyqtSignal(dict)
        else:
            self.update_metrics = None
        self.last_intervention_time = 0
        
    def run(self):
        """Main monitoring loop."""
        logger.info("Starting load monitor...")
        
        while self.running:
            try:
                self._check_load()
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait longer on error
    
    def stop(self):
        """Stop the monitoring thread."""
        self.running = False
        self.wait()
    
    def _check_load(self):
        """Check if an intervention is needed based on current metrics."""
        if not self.config.get("enabled", True):
            return
            
        current_time = time.time()
        metrics = self.metrics.get_metrics()
        
        # Check minimum time between interventions
        min_interval = self.config.get("min_time_between_interventions", 30) * 60  # Convert to seconds
        if (current_time - self.last_intervention_time) < min_interval:
            return
        
        # Check thresholds
        thresholds = {
            "keystroke": metrics["keystroke_count"] > self.config.get("keystroke_threshold", 500),
            "time": metrics["time_active"] > self.config.get("time_threshold", 45),
            "error": metrics["error_count"] > self.config.get("error_threshold", 10),
            "typing_speed": metrics["keystrokes_per_minute"] > 200  # Very fast typing
        }
        
        # If any threshold is exceeded
        if any(thresholds.values()):
            logger.info(f"Intervention triggered by thresholds: {thresholds}")
            self.last_intervention_time = current_time
            
            # Prepare context for the intervention
            context = {
                "trigger": next(k for k, v in thresholds.items() if v),
                "metrics": metrics,
                "joke_style": self.config.get("joke_style", "programming")
            }
            
            # Emit signal with context
            self.intervention_needed.emit(context)
            
            # Reset relevant metrics
            self.metrics.reset()
    
    def record_keystroke(self):
        """Record a keystroke event."""
        # Always record keystrokes for monitoring purposes, regardless of keyboard hook availability
        self.metrics.record_keystroke()
    
    def record_error(self):
        """Record an error event."""
        self.metrics.record_error()


if QT_AVAILABLE:
    class SettingsDialog(QDialog):
        """Dialog for configuring the Mental Load Balancer settings."""
        
        def __init__(self, config, parent=None):
            super().__init__(parent)
            self.config = config
            self.setWindowTitle("Mental Load Balancer Settings")
            self.setMinimumWidth(400)
            
            # Create form layout
            layout = QFormLayout()
            
            # Keystroke threshold
            self.keystroke_slider = QSlider(Qt.Orientation.Horizontal)
            self.keystroke_slider.setRange(100, 2000)
            self.keystroke_slider.setValue(self.config.get("keystroke_threshold", 500))
            self.keystroke_slider.valueChanged.connect(self.update_keystroke_label)
            self.keystroke_label = QLabel(f"{self.keystroke_slider.value()} keystrokes")
            
            # Time threshold
            self.time_spin = QSpinBox()
            self.time_spin.setRange(5, 120)
            self.time_spin.setValue(self.config.get("time_threshold", 45))
            self.time_spin.setSuffix(" minutes")
            
            # Error threshold
            self.error_spin = QSpinBox()
            self.error_spin.setRange(1, 50)
            self.error_spin.setValue(self.config.get("error_threshold", 10))
            self.error_spin.setSuffix(" errors")
            
            # Joke style
            self.joke_combo = QComboBox()
            self.joke_combo.addItems(["programming", "general"])
            self.joke_combo.setCurrentText(self.config.get("joke_style", "programming"))
            
            # Intervention style
            self.intervention_combo = QComboBox()
            self.intervention_combo.addItems(["popup", "notification"])
            self.intervention_combo.setCurrentText(self.config.get("intervention_style", "popup"))
            
            # Min time between interventions
            self.min_time_spin = QSpinBox()
            self.min_time_spin.setRange(1, 240)
            self.min_time_spin.setValue(self.config.get("min_time_between_interventions", 30))
            self.min_time_spin.setSuffix(" minutes")
            
            # Buttons
            self.save_btn = QPushButton("Save")
            self.save_btn.clicked.connect(self.accept)
            self.cancel_btn = QPushButton("Cancel")
            self.cancel_btn.clicked.connect(self.reject)
            
            # Add widgets to layout
            layout.addRow("Keystroke threshold:", self.keystroke_slider)
            layout.addRow("", self.keystroke_label)
            layout.addRow("Time threshold:", self.time_spin)
            layout.addRow("Error threshold:", self.error_spin)
            layout.addRow("Joke style:", self.joke_combo)
            layout.addRow("Intervention style:", self.intervention_combo)
            layout.addRow("Min time between interventions:", self.min_time_spin)
            
            # Add buttons
            button_layout = QVBoxLayout()
            button_layout.addWidget(self.save_btn)
            button_layout.addWidget(self.cancel_btn)
            layout.addRow("", button_layout)
            
            self.setLayout(layout)
        
        def update_keystroke_label(self, value):
            """Update the keystroke threshold label."""
            self.keystroke_label.setText(f"{value} keystrokes")
        
        def get_values(self):
            """Get the current values from the dialog."""
            return {
                "keystroke_threshold": self.keystroke_slider.value(),
                "time_threshold": self.time_spin.value(),
                "error_threshold": self.error_spin.value(),
                "joke_style": self.joke_combo.currentText(),
                "intervention_style": self.intervention_combo.currentText(),
                "min_time_between_interventions": self.min_time_spin.value()
            }
else:
    # Fallback implementation when Qt is not available
    class SettingsDialog:
        """Fallback settings dialog when Qt is not available."""
        
        def __init__(self, config, parent=None):
            self.config = config
        
        def exec(self):
            print("Settings dialog not available in headless mode")
            return 0  # Rejected
        
        def get_values(self):
            return self.config.copy()


class MentalLoadBalancerApp(QApplication if QT_AVAILABLE else object):
    """Main application class for the Mental Load Balancer."""
    
    def __init__(self, *args, **kwargs):
        if QT_AVAILABLE:
            super().__init__(*args, **kwargs)
            self.setQuitOnLastWindowClosed(False)
        
        # Load or create config
        self.config = self._load_config()
        
        # Initialize components
        self.monitor = LoadMonitor(self.config)
        self.joke_engine = JokeEngine()
        
        # Set up VS Code integration if available
        self.vscode_monitor = None
        if VSCODE_AVAILABLE:
            try:
                self.vscode_monitor = VSCodeMonitor()
                self.vscode_monitor.on_metrics_update(self._on_vscode_metrics_update)
                logger.info("VS Code integration enabled")
            except Exception as e:
                logger.error(f"Failed to initialize VS Code integration: {e}")
        
        # Set up system tray if Qt is available
        if QT_AVAILABLE:
            self._setup_tray()
        
        # Connect signals
        if QT_AVAILABLE and hasattr(self.monitor, 'intervention_needed') and self.monitor.intervention_needed:
            self.monitor.intervention_needed.connect(self.handle_intervention)
        
        # Start monitoring
        self.monitor.start()
        
        # Set up global keyboard hook if available
        if KEYBOARD_AVAILABLE:
            self._setup_keyboard_hook()
        
        logger.info("Mental Load Balancer started")
    
    def _on_vscode_metrics_update(self, metrics):
        """Handle VS Code metrics updates."""
        # Update monitor with VS Code specific metrics
        if hasattr(self, 'monitor') and hasattr(self.monitor, 'metrics'):
            # Example: Update error count based on VS Code diagnostics
            if hasattr(metrics, 'diagnostics') and metrics.diagnostics:
                error_count = len([d for d in metrics.diagnostics 
                                 if hasattr(d, 'severity') and d.severity >= 2])
                self.monitor.metrics.error_count = error_count
            
            # Update last activity time
            if hasattr(metrics, 'last_activity_time'):
                self.monitor.metrics.last_activity_time = metrics.last_activity_time
    
    def _load_config(self):
        """Load configuration from file or use defaults."""
        config_path = Path("mental_load_balancer_config.json")
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**DEFAULT_CONFIG, **config}
            except Exception as e:
                logger.error(f"Error loading config: {e}")
        return DEFAULT_CONFIG.copy()
    
    def save_config(self):
        """Save configuration to file."""
        config_path = Path("mental_load_balancer_config.json")
        try:
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("Configuration saved")
            return True
        except Exception as e:
            logger.error(f"Error saving config: {e}")
            return False
    
    def _setup_tray(self):
        """Set up the system tray icon and menu."""
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set icon (using a default icon for now)
        self.tray_icon.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_ComputerIcon))
        
        # Create menu
        self.tray_menu = QMenu()
        
        # Toggle enabled action
        self.toggle_action = QAction("Enabled", self, checkable=True)
        self.toggle_action.setChecked(self.config.get("enabled", True))
        self.toggle_action.triggered.connect(self.toggle_enabled)
        
        # Settings action
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.show_settings)
        
        # Show metrics action
        metrics_action = QAction("Show Metrics", self)
        metrics_action.triggered.connect(self.show_metrics)
        
        # Quit action
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        
        # Add actions to menu
        self.tray_menu.addAction(self.toggle_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(settings_action)
        self.tray_menu.addAction(metrics_action)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(quit_action)
        
        # Set the context menu
        self.tray_icon.setContextMenu(self.tray_menu)
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Show a message
        self.tray_icon.showMessage(
            "Mental Load Balancer",
            "Mental Load Balancer is running in the background.",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def _setup_keyboard_hook(self):
        """Set up global keyboard hook to monitor typing."""
        if not KEYBOARD_AVAILABLE:
            logger.warning("Keyboard monitoring is not available. Keystroke-based features will be limited.")
            return
            
        try:
            # Use a separate thread for the keyboard hook to avoid blocking the GUI
            def keyboard_listener():
                def on_key_event(event):
                    if event.event_type == keyboard.KEY_DOWN:
                        self.monitor.record_keystroke()
                
                keyboard.hook(on_key_event)
                keyboard.wait()
            
            keyboard_thread = threading.Thread(target=keyboard_listener, daemon=True)
            keyboard_thread.start()
            
        except Exception as e:
            logger.error(f"Error setting up keyboard hook: {e}")
            logger.info("Continuing without keyboard monitoring. Some features may be limited.")
    
    def toggle_enabled(self, checked):
        """Toggle whether the monitor is enabled."""
        self.config["enabled"] = checked
        self.toggle_action.setChecked(checked)
        self.save_config()
        
        status = "enabled" if checked else "disabled"
        self.tray_icon.showMessage(
            "Mental Load Balancer",
            f"Mental Load Balancer is now {status}.",
            QSystemTrayIcon.Information,
            2000
        )
    
    def show_settings(self):
        """Show the settings dialog."""
        dialog = SettingsDialog(self.config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Update config with new values
            new_values = dialog.get_values()
            self.config.update(new_values)
            self.save_config()
            
            # Update monitor config
            self.monitor.config = self.config
            
            self.tray_icon.showMessage(
                "Settings Saved",
                "Your settings have been updated.",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def show_metrics(self):
        """Show current metrics in a dialog."""
        metrics = self.monitor.metrics.get_metrics()
        
        msg = QMessageBox()
        msg.setWindowTitle("Current Metrics")
        msg.setIcon(QMessageBox.Icon.Information)
        
        # Format metrics
        metrics_text = (
            f"<b>Current Session:</b><br>"
            f"• Keystrokes: {metrics['keystroke_count']}<br>"
            f"• Errors: {metrics['error_count']}<br>"
            f"• Time active: {metrics['time_active']:.1f} minutes<br>"
            f"• Keystrokes/min (last 5 min): {metrics['keystrokes_per_minute']:.1f}<br>"
            f"<br><b>Next intervention in:</b><br>"
            f"• After {self.config.get('keystroke_threshold', 500) - metrics['keystroke_count']} more keystrokes<br>"
            f"• Or in {max(0, self.config.get('time_threshold', 45) - metrics['time_active']):.1f} minutes<br>"
            f"• Or after {max(0, self.config.get('error_threshold', 10) - metrics['error_count'])} more errors"
        )
        
        msg.setText(metrics_text)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def handle_intervention(self, context):
        """Handle an intervention event."""
        if not self.config.get("enabled", True):
            return
        
        # Get a joke based on context
        joke = self.joke_engine.get_contextual_joke(context)
        
        # Show the intervention based on user preference
        if self.config.get("intervention_style", "popup") == "popup":
            self.show_popup(joke, context)
        else:
            self.show_notification(joke)
    
    def show_popup(self, message, context):
        """Show a popup dialog with the intervention message."""
        # Create a non-modal dialog
        dialog = QDialog()
        dialog.setWindowTitle("🧠 Break Time!")
        dialog.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | 
                             Qt.WindowType.FramelessWindowHint)
        
        # Set up layout
        layout = QVBoxLayout()
        
        # Add message
        label = QLabel(message)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 14px; margin: 15px;")
        
        # Add close button
        close_btn = QPushButton("Got it!")
        close_btn.clicked.connect(dialog.accept)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                font-weight: bold;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Add widgets to layout
        layout.addWidget(label)
        layout.addWidget(close_btn, 0, Qt.AlignmentFlag.AlignHCenter)
        
        # Set dialog size and position
        dialog.setLayout(layout)
        dialog.setFixedSize(300, 150)
        
        # Center on screen
        screen = self.primaryScreen().availableGeometry()
        x = screen.width() - dialog.width() - 20  # 20px from right
        y = screen.height() - dialog.height() - 50  # 50px from bottom
        dialog.move(x, y)
        
        # Show the dialog
        dialog.exec()
    
    def show_notification(self, message):
        """Show a system notification."""
        self.tray_icon.showMessage(
            "🧠 Break Time!",
            message,
            QSystemTrayIcon.Information,
            5000  # 5 seconds
        )
    
    def quit_application(self):
        """Clean up and quit the application."""
        logger.info("Shutting down Mental Load Balancer...")
        
        # Stop the monitor thread
        self.monitor.stop()
        
        # Clean up keyboard hook
        try:
            keyboard.unhook_all()
        except:
            pass
        
        # Quit the application
        self.quit()


def run_standalone_console():
    """Run the application in standalone console mode."""
    print("\n=== Mental Load Balancer ===")
    print("Running in standalone console mode\n")
    
    # Simple console interface
    def print_menu():
        print("\nOptions:")
        print("1. View current metrics")
        print("2. Trigger test intervention")
        print("3. Show configuration")
        print("4. Exit")
        
    while True:
        print_menu()
        try:
            choice = input("\nEnter your choice (1-4): ")
            
            if choice == '1':
                # Show current metrics
                if hasattr(app, 'monitor') and hasattr(app.monitor, 'metrics'):
                    metrics = app.monitor.metrics.get_metrics()
                    print("\nCurrent Metrics:")
                    for key, value in metrics.items():
                        print(f"{key}: {value}")
                else:
                    print("Metrics not available in standalone mode.")
                    
            elif choice == '2':
                # Trigger test intervention
                print("\nTriggering test intervention...")
                if hasattr(app, 'handle_intervention'):
                    app.handle_intervention({"trigger": "manual", "message": "Test intervention triggered manually"})
                else:
                    print("Test joke:", app.joke_engine.get_joke())
                    
            elif choice == '3':
                # Show configuration
                print("\nCurrent Configuration:")
                for key, value in app.config.items():
                    print(f"{key}: {value}")
                    
            elif choice == '4':
                print("\nGoodbye!")
                if hasattr(app, 'monitor') and hasattr(app.monitor, 'stop'):
                    app.monitor.stop()
                break
                
            else:
                print("\nInvalid choice. Please enter a number between 1 and 4.")
                
        except KeyboardInterrupt:
            print("\nShutting down...")
            if hasattr(app, 'monitor') and hasattr(app.monitor, 'stop'):
                app.monitor.stop()
            break

def main():
    """Main entry point for the application."""
    # Handle command line arguments
    import argparse
    parser = argparse.ArgumentParser(description='Mental Load Balancer')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--no-gui', action='store_true', help='Run in headless mode')
    parser.add_argument('--console', action='store_true', help='Force console interface')
    args = parser.parse_args()
    
    # Set up logging level
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mental_load_balancer.log'),
            logging.StreamHandler()
        ]
    )
    
    # Create the application instance
    app = MentalLoadBalancerApp(sys.argv if QT_AVAILABLE else [])
    
    # Run the appropriate interface
    if args.console or not QT_AVAILABLE or args.no_gui:
        run_standalone_console()
    else:
        logger.info("Starting Mental Load Balancer with GUI")
        sys.exit(app.exec() if hasattr(app, 'exec') else 0)


if __name__ == "__main__":
    main()
