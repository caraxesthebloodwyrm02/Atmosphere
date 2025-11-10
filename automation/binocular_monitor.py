#!/usr/bin/env python3
"""
Atmosphere TODO Monitoring System
Tracks the last 20 TODO execution steps and dumps to JSON every 3 hours
Monitors persistently for 24 hours
"""

import json
import os
import schedule
import socket
import sys
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any

@dataclass
class TodoStep:
    """Represents a TODO execution step"""
    timestamp: str
    action: str  # create, update, complete, etc.
    todo_id: str
    content: str
    status: str
    priority: str
    previous_status: str = None
    execution_time: float = None

class TodoMonitor:
    """Monitors TODO execution steps and manages persistent tracking"""

    def __init__(self, binocular_path: str = "binocular"):
        self.binocular_path = Path(binocular_path)
        self.binocular_path.mkdir(exist_ok=True)

        # Track the last 20 execution steps
        self.execution_steps: List[TodoStep] = []
        self.max_steps = 20

        # Track current TODO state for change detection
        self.previous_todos: Dict[str, Dict] = {}
        self.current_todos: Dict[str, Dict] = {}

        # Monitoring statistics
        self.stats = {
            "monitoring_start": datetime.now().isoformat(),
            "total_steps_tracked": 0,
            "dumps_performed": 0,
            "uptime_hours": 0
        }

        # Load previous state if exists
        self._load_state()

    def _load_state(self):
        """Load previous monitoring state"""
        state_file = self.binocular_path / "monitor_state.json"
        if state_file.exists():
            try:
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.execution_steps = [TodoStep(**step) for step in data.get('execution_steps', [])]
                    self.stats.update(data.get('stats', {}))
                    print(f"📚 Loaded {len(self.execution_steps)} previous execution steps")
            except Exception as e:
                print(f"⚠️  Failed to load previous state: {e}")

    def _save_state(self):
        """Save current monitoring state"""
        state_file = self.binocular_path / "monitor_state.json"
        try:
            state_data = {
                "execution_steps": [asdict(step) for step in self.execution_steps],
                "stats": self.stats,
                "last_updated": datetime.now().isoformat()
            }
            with open(state_file, 'w') as f:
                json.dump(state_data, f, indent=2, default=str)
        except Exception as e:
            print(f"⚠️  Failed to save state: {e}")

    def check_todo_changes(self) -> List[TodoStep]:
        """Check for TODO changes and return new execution steps"""
        new_steps = []

        # Get current TODO state (this would integrate with the todo_list tool)
        # For now, we'll simulate by checking for file changes
        current_todos = self._get_current_todos()

        # Detect changes
        for todo_id, todo_data in current_todos.items():
            if todo_id not in self.previous_todos:
                # New TODO created
                step = TodoStep(
                    timestamp=datetime.now().isoformat(),
                    action="created",
                    todo_id=todo_id,
                    content=todo_data.get('content', ''),
                    status=todo_data.get('status', 'pending'),
                    priority=todo_data.get('priority', 'medium')
                )
                new_steps.append(step)
            else:
                # Check for status changes
                prev_status = self.previous_todos[todo_id].get('status')
                curr_status = todo_data.get('status')
                if prev_status != curr_status:
                    step = TodoStep(
                        timestamp=datetime.now().isoformat(),
                        action="status_changed",
                        todo_id=todo_id,
                        content=todo_data.get('content', ''),
                        status=curr_status,
                        priority=todo_data.get('priority', 'medium'),
                        previous_status=prev_status
                    )
                    new_steps.append(step)

        # Check for deleted TODOs
        for todo_id, todo_data in self.previous_todos.items():
            if todo_id not in current_todos:
                step = TodoStep(
                    timestamp=datetime.now().isoformat(),
                    action="deleted",
                    todo_id=todo_id,
                    content=todo_data.get('content', ''),
                    status="deleted",
                    priority=todo_data.get('priority', 'medium'),
                    previous_status=todo_data.get('status')
                )
                new_steps.append(step)

        self.previous_todos = current_todos.copy()
        return new_steps

    def _get_current_todos(self) -> Dict[str, Dict]:
        """Get current TODO state (would integrate with actual todo_list tool)"""
        # For demonstration, we'll create a sample TODO state
        # In real implementation, this would call the todo_list tool
        return {
            "implement_auth_system": {
                "content": "Implement authentication system with user management, tokens, and validation",
                "status": "completed",
                "priority": "high"
            },
            "add_access_controls": {
                "content": "Add access control decorators/guards to all entry points",
                "status": "completed",
                "priority": "high"
            },
            "test_security_measures": {
                "content": "Test all security measures and entry points",
                "status": "completed",
                "priority": "high"
            }
        }

    def add_execution_step(self, step: TodoStep):
        """Add a new execution step to the monitoring queue"""
        self.execution_steps.append(step)

        # Keep only the last 20 steps
        if len(self.execution_steps) > self.max_steps:
            self.execution_steps = self.execution_steps[-self.max_steps:]

        self.stats["total_steps_tracked"] += 1
        print(f"📝 Recorded execution step: {step.action} - {step.todo_id}")

    def check_network_presence(self) -> Dict[str, Any]:
        """Monitor network presence and device discovery."""
        try:
            # Import here to avoid circular dependencies
            sys.path.insert(0, os.path.dirname(__file__))
            from src.network import NetworkPresence

            # Create a temporary presence monitor (read-only)
            temp_presence = NetworkPresence(
                device_id="monitor-agent",
                broadcast_port=37020,
                presence_interval=60  # Don't actually broadcast
            )

            # Just check for existing devices without starting service
            devices = {}
            sock = None
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                sock.bind(('0.0.0.0', 37020))
                sock.settimeout(0.1)  # Very short timeout for quick check

                # Try to receive any pending announcements
                try:
                    while True:
                        data, addr = sock.recvfrom(1024)
                        # Parse and add to devices dict
                        try:
                            import json
                            message = json.loads(data.decode('utf-8'))
                            if (isinstance(message, dict) and
                                message.get('type') == 'PRESENCE'):
                                device_id = str(message.get('device_id', ''))
                                if device_id and device_id != "monitor-agent":
                                    devices[device_id] = {
                                        'address': addr[0],
                                        'port': message.get('port', 37021),
                                        'last_seen': time.time(),
                                        'metadata': message.get('metadata', {})
                                    }
                        except (json.JSONDecodeError, KeyError):
                            pass
                except socket.timeout:
                    pass  # Expected when no more data

            except Exception as e:
                print(f"Network presence check error: {e}")
            finally:
                if sock:
                    sock.close()

            return {
                "active_devices": len(devices),
                "devices": devices,
                "last_check": datetime.now().isoformat()
            }

        except ImportError:
            return {"error": "NetworkPresence module not available"}
        except Exception as e:
            return {"error": str(e)}

    def perform_json_dump(self):
        """Perform scheduled JSON dump with enhanced monitoring data."""
        timestamp = datetime.now()
        dump_file = self.binocular_path / f"todo_monitor_{timestamp.strftime('%Y%m%d_%H%M%S')}.json"

        # Include network presence data
        network_status = self.check_network_presence()

        dump_data = {
            "dump_timestamp": timestamp.isoformat(),
            "execution_steps": [asdict(step) for step in self.execution_steps],
            "current_todos": self.current_todos,
            "statistics": self.stats,
            "uptime_hours": (datetime.now() - datetime.fromisoformat(self.stats["monitoring_start"])).total_seconds() / 3600,
            "network_presence": network_status
        }

        try:
            with open(dump_file, 'w') as f:
                json.dump(dump_data, f, indent=2, default=str)

            self.stats["dumps_performed"] += 1
            print(f"💾 JSON dump completed: {dump_file.name}")
            print(f"📊 Steps tracked: {len(self.execution_steps)}, Network devices: {network_status.get('active_devices', 'N/A')}")

        except Exception as e:
            print(f"❌ Failed to create JSON dump: {e}")

    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        try:
            # Check for TODO changes
            new_steps = self.check_todo_changes()

            # Add new steps to monitoring
            for step in new_steps:
                self.add_execution_step(step)

            # Update uptime
            self.stats["uptime_hours"] = (datetime.now() - datetime.fromisoformat(self.stats["monitoring_start"])).total_seconds() / 3600

        except Exception as e:
            print(f"⚠️  Monitoring cycle error: {e}")

    def start_monitoring(self, duration_hours: int = 24):
        """Start persistent monitoring for specified duration"""
        print("🔭 Starting Atmosphere TODO Monitoring System")
        print(f"📁 Monitoring data will be saved to: {self.binocular_path.absolute()}")
        print(f"⏰ Scheduled dumps every 3 hours for {duration_hours} hours")
        print("=" * 60)

        # Schedule JSON dumps every 3 hours on the hour
        schedule.every(3).hours.at(":00").do(self.perform_json_dump)

        # Calculate end time
        end_time = datetime.now() + timedelta(hours=duration_hours)

        print(f"🚀 Monitoring started at: {datetime.now().isoformat()}")
        print(f"🏁 Monitoring will end at: {end_time.isoformat()}")
        print()

        # Initial dump
        self.perform_json_dump()

        # Monitoring loop
        monitoring_interval = 30  # Check every 30 seconds
        cycle_count = 0

        try:
            while datetime.now() < end_time:
                cycle_count += 1

                # Run monitoring cycle
                self.run_monitoring_cycle()

                # Check for scheduled tasks
                schedule.run_pending()

                # Save state every 10 cycles (5 minutes)
                if cycle_count % 10 == 0:
                    self._save_state()
                    print(f"💾 State saved (cycle {cycle_count})")

                # Progress update every 20 cycles (10 minutes)
                if cycle_count % 20 == 0:
                    hours_remaining = (end_time - datetime.now()).total_seconds() / 3600
                    print(f"⏳ Monitoring active - {hours_remaining:.1f} hours remaining")

                time.sleep(monitoring_interval)

        except KeyboardInterrupt:
            print("\n🛑 Monitoring interrupted by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        finally:
            # Final dump and cleanup
            print("\n🔄 Performing final monitoring tasks...")
            self.perform_json_dump()
            self._save_state()

            print("✅ Monitoring session completed")
            print(f"📊 Final statistics:")
            print(f"   - Total execution steps tracked: {self.stats['total_steps_tracked']}")
            print(f"   - JSON dumps performed: {self.stats['dumps_performed']}")
            print(f"   - Total uptime: {self.stats['uptime_hours']:.1f} hours")

def main():
    """Main entry point for the monitoring system"""
    import argparse

    parser = argparse.ArgumentParser(description="Atmosphere TODO Monitoring System")
    parser.add_argument("--duration", type=int, default=24,
                       help="Monitoring duration in hours (default: 24)")
    parser.add_argument("--binocular-path", type=str, default="binocular",
                       help="Path to binocular monitoring folder (default: binocular)")

    args = parser.parse_args()

    # Create and start monitor
    monitor = TodoMonitor(args.binocular_path)
    monitor.start_monitoring(args.duration)

if __name__ == "__main__":
    main()
