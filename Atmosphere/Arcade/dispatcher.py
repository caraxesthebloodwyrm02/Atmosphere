#!/usr/bin/env python3
"""
dispatcher.py – Watches './incoming/' for new files/tokens and routes them.
Integrated with Arcade Terminal system.
"""

import os
import sys
import yaml
import subprocess
import asyncio
import pathlib
import shutil
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #
# 1️⃣   Utilities: read routing config
# --------------------------------------------------------------------------- #
def load_config(config_path: str = None):
    """Load routing configuration from YAML file."""
    if config_path is None:
        # Default to Arcade config directory
        arcade_root = pathlib.Path(__file__).parent
        config_path = arcade_root / "config" / "routing.yaml"
    
    config_path = pathlib.Path(config_path)
    
    if not config_path.exists():
        logger.warning(f"Config file not found: {config_path}, using defaults")
        return {
            "audio_tool": "audio",
            "visual_tool": "visual",
            "games_tool": "games"
        }
    
    try:
        with open(config_path, "r") as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
        return {}


# --------------------------------------------------------------------------- #
# 2️⃣   Tracker that knows how to dispatch a given tool
# --------------------------------------------------------------------------- #
class DispatcherHandler(FileSystemEventHandler):
    """Handles file system events and dispatches tools to zones."""
    
    def __init__(self, zones_root, routing, incoming_dir):
        super().__init__()
        self.zones_root = pathlib.Path(zones_root)
        self.routing = routing
        self.incoming_dir = pathlib.Path(incoming_dir)
        self.active_processes = {}  # Track active tool processes

    def on_created(self, event):
        """Handle new file creation events."""
        if event.is_directory:
            return  # ignore directories

        file_path = pathlib.Path(event.src_path)
        
        # Skip already processed files
        if file_path.suffix == ".processed":
            return
        
        # Extract tool name from file
        tool_name = self._extract_tool_name(file_path)
        if not tool_name:
            return

        zone_name = self.routing.get(tool_name)
        if not zone_name:
            logger.warning(f"No zone mapped for tool '{tool_name}'.")
            return

        # Dispatch to zone
        self._dispatch_to_zone(tool_name, file_path, zone_name)

    def _extract_tool_name(self, file_path):
        """Extract tool name from file (first line or filename)."""
        try:
            # Try reading first line
            with open(file_path, "r") as fh:
                first_line = fh.readline().strip()
                if first_line and not first_line.startswith("#"):
                    return first_line
        except Exception as e:
            logger.debug(f"Could not read first line: {e}")
        
        # Fallback to filename without extension
        return file_path.stem

    def _dispatch_to_zone(self, tool_name, file_path, zone_name):
        """Dispatch a tool to its designated zone."""
        zone_dir = self.zones_root / zone_name
        zone_dir.mkdir(parents=True, exist_ok=True)

        log_file = zone_dir / f"{tool_name}.log"
        
        try:
            logger.info(f"Dispatching '{tool_name}' → zone:{zone_name}")
            
            # Determine how to run the tool
            if file_path.suffix == ".py":
                # Python script
                proc = subprocess.Popen(
                    [sys.executable, str(file_path)],
                    stdout=open(log_file, "w"),
                    stderr=subprocess.STDOUT,
                    cwd=str(zone_dir)
                )
            elif file_path.suffix in [".sh", ".bat", ".ps1"]:
                # Shell script
                proc = subprocess.Popen(
                    [str(file_path)],
                    stdout=open(log_file, "w"),
                    stderr=subprocess.STDOUT,
                    cwd=str(zone_dir)
                )
            else:
                # Try to execute as-is
                proc = subprocess.Popen(
                    [str(file_path)],
                    stdout=open(log_file, "w"),
                    stderr=subprocess.STDOUT,
                    cwd=str(zone_dir)
                )
            
            self.active_processes[tool_name] = proc
            
            # Log process info
            with open(log_file, "a") as lf:
                lf.write(f"\n[Dispatcher] Tool '{tool_name}' started (PID: {proc.pid})\n")
                lf.write(f"[Dispatcher] Zone: {zone_name}\n")
                lf.write(f"[Dispatcher] Source: {file_path}\n")
                lf.write("-" * 40 + "\n")
            
            # Wait for process (non-blocking check)
            def check_process():
                try:
                    proc.wait()
                    logger.info(f"'{tool_name}' finished (exit code: {proc.returncode})")
                    if tool_name in self.active_processes:
                        del self.active_processes[tool_name]
                except Exception as e:
                    logger.error(f"Error waiting for process: {e}")
            
            # Run in background thread
            import threading
            thread = threading.Thread(target=check_process, daemon=True)
            thread.start()
            
            # Move trigger file after dispatch
            processed_path = file_path.with_suffix(file_path.suffix + ".processed")
            try:
                shutil.move(str(file_path), str(processed_path))
            except Exception as e:
                logger.warning(f"Could not move processed file: {e}")
                
        except Exception as e:
            logger.error(f"Failed to dispatch '{tool_name}': {e}")
            with open(log_file, "a") as lf:
                lf.write(f"\n[ERROR] Failed to dispatch: {e}\n")

    def get_active_tools(self):
        """Get list of currently active tools."""
        active = []
        for tool_name, proc in list(self.active_processes.items()):
            if proc.poll() is None:  # Still running
                active.append(tool_name)
            else:
                del self.active_processes[tool_name]
        return active


# --------------------------------------------------------------------------- #
# 3️⃣   Main entry – start monitoring
# --------------------------------------------------------------------------- #
def main():
    """Main entry point for dispatcher."""
    # Basic paths relative to Arcade root
    arcade_root = pathlib.Path(__file__).parent
    incoming_dir = arcade_root / "incoming"
    zones_root = arcade_root / "zones"
    config_path = arcade_root / "config" / "routing.yaml"

    # Ensure directories exist
    incoming_dir.mkdir(exist_ok=True)
    zones_root.mkdir(exist_ok=True)
    (arcade_root / "config").mkdir(exist_ok=True)

    # Load routing table
    routing = load_config(config_path)
    logger.info(f"Loaded routing config: {routing}")

    # Set up watchdog observer
    event_handler = DispatcherHandler(
        zones_root=str(zones_root),
        routing=routing,
        incoming_dir=str(incoming_dir)
    )
    observer = Observer()
    observer.schedule(event_handler, str(incoming_dir), recursive=False)

    logger.info("Starting dispatcher. Press Ctrl+C to exit.")
    logger.info(f"Watching: {incoming_dir}")
    logger.info(f"Zones: {zones_root}")
    
    observer.start()
    try:
        while True:
            # Simple keep-alive loop
            import time
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down…")
        observer.stop()
    observer.join()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()

