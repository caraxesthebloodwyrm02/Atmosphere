#!/usr/bin/env python3
"""
Feature Flag Manager for Temporary Integrations
==============================================

Controls temporary feature integrations that are enabled only upon explicit
user request and automatically disabled after task completion. These are
"integrating features" that should not persist in the system.

Features managed:
- Privacy-preserving feature extraction
- Safety-governed intervention router
- Bias thermal scanner
- Immutable audit logging
- Enhanced thermal mapping
- Advanced visualization modes

All features default to DISABLED. Only explicit activation enables them
temporarily for the current task.
"""

import json
import time
import threading
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path
from contextlib import contextmanager

# Unique sys scoping with hash-based identifier
_sys_scope_feature_manager = hash(id(sys)) % 1000000


class FeatureFlagManager:
    """Manages temporary feature integrations with auto-disable"""

    def __init__(self, config_path: str = "config/feature_flags.json"):
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Default: ALL FEATURES DISABLED
        self.flags = {
            # Privacy & Safety Features
            "privacy_feature_extraction": False,
            "safety_intervention_router": False,
            "bias_thermal_scanner": False,
            "immutable_audit_log": False,

            # Thermal Mapping Features
            "thermal_mapper_standard": False,
            "thermal_mapper_flash": False,
            "thermal_mapper_raw": False,
            "enhanced_thermal_scan": False,

            # Integration Features
            "atmosphere_privacy_safety": False,
            "atmosphere_thermal_viz": False,
        }

        # Task tracking
        self.active_tasks: Dict[str, Dict] = {}
        self.task_timeouts: Dict[str, float] = {}

        # Auto-cleanup thread
        self.cleanup_thread = threading.Thread(target=self._auto_cleanup, daemon=True)
        self.cleanup_thread.start()

        # Load persisted state (if any)
        self._load_state()

    def _load_state(self):
        """Load feature flag state from disk"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                    # Only load explicitly enabled flags (never auto-enable)
                    for flag, enabled in data.get('flags', {}).items():
                        if flag in self.flags and enabled:
                            self.flags[flag] = True
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    def _save_state(self):
        """Save current flag state"""
        data = {
            'flags': self.flags.copy(),
            'last_updated': time.time(),
            'active_tasks': list(self.active_tasks.keys())
        }
        try:
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass  # Don't fail if we can't save

    def _auto_cleanup(self):
        """Background thread to auto-disable expired features"""
        while True:
            current_time = time.time()
            expired_tasks = []

            for task_id, task_info in self.active_tasks.items():
                if current_time > task_info['expires_at']:
                    expired_tasks.append(task_id)

            for task_id in expired_tasks:
                self.disable_task(task_id, reason="auto_cleanup")

            time.sleep(30)  # Check every 30 seconds

    def enable_feature(self, feature_name: str, duration_minutes: int = 60) -> bool:
        """
        Enable a feature temporarily

        Args:
            feature_name: Name of the feature to enable
            duration_minutes: How long to keep it enabled (default: 1 hour)

        Returns:
            bool: True if successfully enabled
        """
        if feature_name not in self.flags:
            return False

        self.flags[feature_name] = True
        self._save_state()

        # Log the enable event
        print(f"🔧 Feature '{feature_name}' enabled for {duration_minutes} minutes")

        # Auto-disable after duration
        def auto_disable():
            time.sleep(duration_minutes * 60)
            self.disable_feature(feature_name, reason="auto_timeout")

        thread = threading.Thread(target=auto_disable, daemon=True)
        thread.start()

        return True

    def disable_feature(self, feature_name: str, reason: str = "manual") -> bool:
        """Disable a feature"""
        if feature_name not in self.flags:
            return False

        was_enabled = self.flags[feature_name]
        self.flags[feature_name] = False
        self._save_state()

        if was_enabled:
            print(f"🔌 Feature '{feature_name}' disabled ({reason})")

        return True

    def enable_task(self, task_name: str, required_features: List[str],
                   duration_minutes: int = 30) -> str:
        """
        Enable multiple features for a specific task

        Args:
            task_name: Descriptive name for the task
            required_features: List of features needed for this task
            duration_minutes: Task duration (default: 30 minutes)

        Returns:
            str: Task ID for tracking
        """
        task_id = f"{task_name}_{int(time.time())}"

        # Enable all required features
        enabled_features = []
        for feature in required_features:
            if self.enable_feature(feature, duration_minutes):
                enabled_features.append(feature)

        # Track the task
        self.active_tasks[task_id] = {
            'name': task_name,
            'features': enabled_features,
            'started_at': time.time(),
            'expires_at': time.time() + (duration_minutes * 60),
            'duration_minutes': duration_minutes
        }

        print(f"🚀 Task '{task_name}' started with features: {', '.join(enabled_features)}")
        print(f"⏰ Task will auto-complete in {duration_minutes} minutes")

        return task_id

    def disable_task(self, task_id: str, reason: str = "manual") -> bool:
        """Disable all features associated with a task"""
        if task_id not in self.active_tasks:
            return False

        task_info = self.active_tasks[task_id]
        disabled_count = 0

        # Disable all features used by this task
        for feature in task_info['features']:
            if self.disable_feature(feature, f"task_{reason}"):
                disabled_count += 1

        # Remove task tracking
        del self.active_tasks[task_id]

        print(f"✅ Task '{task_info['name']}' completed - {disabled_count} features disabled")
        return True

    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is currently enabled"""
        return self.flags.get(feature_name, False)

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all features and tasks"""
        return {
            'features': self.flags.copy(),
            'active_tasks': {
                task_id: {
                    'name': info['name'],
                    'features': info['features'],
                    'minutes_remaining': max(0, (info['expires_at'] - time.time()) / 60)
                }
                for task_id, info in self.active_tasks.items()
            },
            'enabled_features': [f for f, enabled in self.flags.items() if enabled],
            'total_enabled': sum(1 for enabled in self.flags.values() if enabled)
        }

    def emergency_disable_all(self) -> int:
        """Emergency: disable all features immediately"""
        disabled_count = 0
        for feature in list(self.flags.keys()):
            if self.disable_feature(feature, "emergency"):
                disabled_count += 1

        # Clear all tasks
        self.active_tasks.clear()

        print(f"🚨 EMERGENCY: All {disabled_count} features disabled")
        return disabled_count

    @contextmanager
    def temporary_features(self, features: List[str], task_name: str = "temporary"):
        """
        Context manager for temporary feature activation

        Usage:
            with feature_manager.temporary_features(['thermal_mapper_flash'], 'quick_viz'):
                # Features are enabled here
                visualize_data(data)
            # Features automatically disabled here
        """
        task_id = self.enable_task(task_name, features, duration_minutes=5)  # 5 min default
        try:
            yield
        finally:
            self.disable_task(task_id, "context_exit")


# Global feature flag manager instance
feature_manager = FeatureFlagManager()

# Convenience functions for common tasks
def enable_privacy_safety_task(task_name: str = "privacy_analysis", duration_minutes: int = 30):
    """Enable privacy and safety features for analysis tasks"""
    return feature_manager.enable_task(
        task_name,
        ['privacy_feature_extraction', 'safety_intervention_router', 'bias_thermal_scanner'],
        duration_minutes
    )

def enable_thermal_viz_task(task_name: str = "thermal_visualization", duration_minutes: int = 15):
    """Enable thermal visualization features"""
    return feature_manager.enable_task(
        task_name,
        ['thermal_mapper_standard', 'thermal_mapper_flash', 'thermal_mapper_raw'],
        duration_minutes
    )

def enable_atmosphere_integration(task_name: str = "atmosphere_integration", duration_minutes: int = 60):
    """Enable full Atmosphere integration features"""
    return feature_manager.enable_task(
        task_name,
        ['atmosphere_privacy_safety', 'atmosphere_thermal_viz', 'enhanced_thermal_scan'],
        duration_minutes
    )


if __name__ == "__main__":
    # Demo usage
    print("🔧 Feature Flag Manager Demo")
    print("=" * 50)

    # Show initial status
    status = feature_manager.get_status()
    print(f"Initially enabled features: {status['enabled_features']}")

    # Enable a task temporarily
    task_id = enable_thermal_viz_task("demo_visualization", duration_minutes=1)
    print(f"Task ID: {task_id}")

    # Check status
    status = feature_manager.get_status()
    print(f"After enabling: {status['enabled_features']}")
    print(f"Active tasks: {list(status['active_tasks'].keys())}")

    # Wait a bit then check again
    print("Waiting 5 seconds...")
    time.sleep(5)

    # Complete the task
    feature_manager.disable_task(task_id)

    # Final status
    status = feature_manager.get_status()
    print(f"Finally enabled features: {status['enabled_features']}")
