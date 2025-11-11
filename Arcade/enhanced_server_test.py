#!/usr/bin/env python3
"""
Enhanced Interactive Arcade Terminal - Advanced Version
=======================================================

An advanced terminal with AI capabilities, plugin system, and web integration.
Features:
- Command history and auto-completion
- Plugin system for extensible commands
- Advanced file operations with safety
- Git integration
- Package management
- System monitoring
- WebSocket support for real-time web interface
"""

import os
import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
import hashlib
import re
import subprocess
import platform
import psutil
import shutil
import time
import sys

logger = logging.getLogger(__name__)


class CommandPlugin:
    """Base class for terminal command plugins."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.commands = {}

    def register_command(self, command_name: str, handler: Callable, help_text: str = ""):
        """Register a command handler."""
        self.commands[command_name] = {
            'handler': handler,
            'help': help_text
        }

    def get_commands(self):
        """Get all registered commands."""
        return self.commands

    def execute_command(self, command_name: str, *args, **kwargs):
        """Execute a registered command."""
        if command_name in self.commands:
            return self.commands[command_name]['handler'](*args, **kwargs)
        return None


class CommandHistory:
    """Manages command history with persistence."""

    def __init__(self, max_size: int = 1000):
        self.history = []
        self.max_size = max_size
        self.current_index = -1
        self.history_file = Path.home() / '.atmosphere_history'

    def add_command(self, command: str):
        """Add a command to history."""
        if command and command != self.history[-1] if self.history else True:
            self.history.append(command)
            if len(self.history) > self.max_size:
                self.history.pop(0)
            self.current_index = len(self.history)
            self._save_history()

    def get_previous(self):
        """Get previous command in history."""
        if self.history and self.current_index > 0:
            self.current_index -= 1
            return self.history[self.current_index]
        return None

    def get_next(self):
        """Get next command in history."""
        if self.history and self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.history[self.current_index]
        return None

    def search_history(self, query: str):
        """Search command history."""
        return [cmd for cmd in self.history if query.lower() in cmd.lower()]

    def _save_history(self):
        """Save history to file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history[-100:], f)  # Save last 100 commands
        except Exception as e:
            logger.warning(f"Failed to save command history: {e}")

    def _load_history(self):
        """Load history from file."""
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
                    self.current_index = len(self.history)
        except Exception as e:
            logger.warning(f"Failed to load command history: {e}")


class AutoCompleter:
    """Provides auto-completion for commands and file paths."""

    def __init__(self, terminal_handler):
        self.terminal_handler = terminal_handler
        self.builtins = [
            'help', 'exit', 'quit', 'clear', 'history', 'pwd', 'ls', 'cd',
            'cat', 'mkdir', 'touch', 'rm', 'cp', 'mv', 'git', 'python', 'pip',
            'npm', 'node', 'docker', 'kubectl', 'aws', 'gcp', 'azure'
        ]

    def complete(self, partial: str, current_dir: Path):
        """Complete a partial command or path."""
        if not partial:
            return self.builtins[:10]  # Show first 10 suggestions

        # Check if it's a file path
        if '/' in partial or '\\' in partial or partial.startswith('.'):
            return self._complete_path(partial, current_dir)

        # Check built-in commands
        matches = [cmd for cmd in self.builtins if cmd.startswith(partial)]
        if matches:
            return matches

        # Check plugin commands
        for plugin in self.terminal_handler.plugins.values():
            plugin_matches = [cmd for cmd in plugin.get_commands() if cmd.startswith(partial)]
            matches.extend(plugin_matches)

        return matches[:10]  # Limit to 10 suggestions

    def _complete_path(self, partial: str, current_dir: Path):
        """Complete file paths."""
        try:
            if partial.startswith('/'):
                base_path = Path(partial)
            else:
                base_path = current_dir / partial

            # Get parent directory and partial name
            if base_path.is_dir():
                parent = base_path
                partial_name = ""
            else:
                parent = base_path.parent
                partial_name = base_path.name

            if not parent.exists():
                return []

            # Get matching items
            matches = []
            for item in parent.iterdir():
                if item.name.startswith(partial_name):
                    if item.is_dir():
                        matches.append(str(item.relative_to(current_dir)) + '/')
                    else:
                        matches.append(str(item.relative_to(current_dir)))

            return matches[:10]

        except Exception as e:
            logger.warning(f"Path completion error: {e}")
            return []


class FileOperationsPlugin(CommandPlugin):
    """Plugin for safe file operations."""

    def __init__(self):
        super().__init__("file_ops", "Safe file system operations")
        self.register_commands()

    def register_commands(self):
        """Register file operation commands."""
        self.register_command("ls", self.list_directory, "List directory contents")
        self.register_command("pwd", self.print_working_directory, "Show current directory")
        self.register_command("cd", self.change_directory, "Change directory")
        self.register_command("cat", self.show_file, "Display file contents")
        self.register_command("mkdir", self.make_directory, "Create directory")
        self.register_command("touch", self.create_file, "Create empty file")
        self.register_command("cp", self.copy_file, "Copy file or directory")
        self.register_command("mv", self.move_file, "Move/rename file or directory")
        self.register_command("rm", self.remove_file, "Remove file or directory")
        self.register_command("find", self.find_files, "Search for files")
        self.register_command("du", self.disk_usage, "Show disk usage")

    def list_directory(self, session, path: str = "."):
        """List directory contents with detailed information."""
        try:
            dir_path = Path(session['directory']) / path
            if not dir_path.exists():
                return f"❌ Directory not found: {path}"

            items = []
            for item in sorted(dir_path.iterdir()):
                stat = item.stat()
                size = self._format_size(stat.st_size)
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                type_indicator = "📁" if item.is_dir() else "📄"

                items.append(f"{type_indicator} {item.name:<30} {size:>10} {mtime}")

            header = f"📂 Contents of {dir_path}\n{'─' * 70}\n"
            return header + "\n".join(items)

        except Exception as e:
            return f"❌ Error listing directory: {str(e)}"

    def print_working_directory(self, session):
        """Show current working directory."""
        return f"📍 {session['directory']}"

    def change_directory(self, session, path: str):
        """Change current directory."""
        try:
            if not path:
                # Go to home directory
                new_path = Path.home()
            elif path == "..":
                new_path = Path(session['directory']).parent
            elif path.startswith("/"):
                new_path = Path(path)
            else:
                new_path = Path(session['directory']) / path

            if not new_path.exists():
                return f"❌ Directory not found: {path}"

            if not new_path.is_dir():
                return f"❌ Not a directory: {path}"

            session['directory'] = str(new_path.resolve())
            return f"📂 Changed to: {session['directory']}"

        except Exception as e:
            return f"❌ Error changing directory: {str(e)}"

    def show_file(self, session, filename: str, lines: int = 50):
        """Display file contents."""
        try:
            file_path = Path(session['directory']) / filename
            if not file_path.exists():
                return f"❌ File not found: {filename}"

            if not file_path.is_file():
                return f"❌ Not a file: {filename}"

            # Check file size
            size = file_path.stat().st_size
            if size > 1024 * 1024:  # 1MB limit
                return f"❌ File too large: {size} bytes (max 1MB)"

            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            lines_content = content.split('\n')
            if len(lines_content) > lines:
                content = '\n'.join(lines_content[:lines]) + f"\n\n... ({len(lines_content) - lines} more lines)"

            return f"📄 {filename} ({size} bytes):\n{'─' * 50}\n{content}"

        except Exception as e:
            return f"❌ Error reading file: {str(e)}"

    def make_directory(self, session, dirname: str):
        """Create a new directory."""
        try:
            dir_path = Path(session['directory']) / dirname
            dir_path.mkdir(parents=True, exist_ok=True)
            return f"📁 Created directory: {dirname}"
        except Exception as e:
            return f"❌ Error creating directory: {str(e)}"

    def create_file(self, session, filename: str):
        """Create an empty file."""
        try:
            file_path = Path(session['directory']) / filename
            if file_path.exists():
                return f"⚠️ File already exists: {filename}"

            file_path.touch()
            return f"📄 Created file: {filename}"
        except Exception as e:
            return f"❌ Error creating file: {str(e)}"

    def copy_file(self, session, source: str, dest: str):
        """Copy file or directory."""
        try:
            src_path = Path(session['directory']) / source
            dst_path = Path(session['directory']) / dest

            if not src_path.exists():
                return f"❌ Source not found: {source}"

            if dst_path.exists() and dst_path.is_dir():
                dst_path = dst_path / src_path.name

            if src_path.is_file():
                shutil.copy2(src_path, dst_path)
            else:
                shutil.copytree(src_path, dst_path)
            return f"✅ Copied {source} to {dest}"
        except Exception as e:
            return f"❌ Error copying: {str(e)}"

    def move_file(self, session, source: str, dest: str):
        """Move/rename file or directory."""
        try:
            src_path = Path(session['directory']) / source
            dst_path = Path(session['directory']) / dest

            if not src_path.exists():
                return f"❌ Source not found: {source}"

            shutil.move(str(src_path), str(dst_path))
            return f"✅ Moved {source} to {dest}"
        except Exception as e:
            return f"❌ Error moving: {str(e)}"

    def remove_file(self, session, path: str, force: bool = False):
        """Remove file or directory."""
        try:
            target_path = Path(session['directory']) / path
            if not target_path.exists():
                return f"❌ Not found: {path}"

            if target_path.is_file():
                if not force:
                    # Confirm deletion for files
                    return f"⚠️ Use 'rm {path} --force' to delete {path}"
                target_path.unlink()
                return f"🗑️ Removed file: {path}"
            else:
                if not force:
                    return f"⚠️ Use 'rm {path} --force' to delete directory {path}"
                shutil.rmtree(target_path)
                return f"🗑️ Removed directory: {path}"
        except Exception as e:
            return f"❌ Error removing: {str(e)}"

    def find_files(self, session, pattern: str, path: str = "."):
        """Search for files matching pattern."""
        try:
            import fnmatch
            search_path = Path(session['directory']) / path
            if not search_path.exists():
                return f"❌ Search path not found: {path}"

            matches = []
            for root, dirs, files in os.walk(search_path):
                for file in files:
                    if fnmatch.fnmatch(file, pattern):
                        rel_path = os.path.relpath(os.path.join(root, file), session['directory'])
                        matches.append(rel_path)

            if matches:
                return f"🔍 Found {len(matches)} files matching '{pattern}':\n" + "\n".join(matches[:20])
            else:
                return f"🔍 No files found matching '{pattern}'"
        except Exception as e:
            return f"❌ Error searching: {str(e)}"

    def disk_usage(self, session, path: str = "."):
        """Show disk usage information."""
        try:
            target_path = Path(session['directory']) / path
            if not target_path.exists():
                return f"❌ Path not found: {path}"

            total_size = 0
            file_count = 0
            dir_count = 0

            for root, dirs, files in os.walk(target_path):
                dir_count += len(dirs)
                for file in files:
                    try:
                        total_size += os.path.getsize(os.path.join(root, file))
                        file_count += 1
                    except OSError:
                        pass

            return f"💾 Disk usage for {path}:\n" \
                   f"  Files: {file_count:,}\n" \
                   f"  Directories: {dir_count:,}\n" \
                   f"  Total size: {self._format_size(total_size)}"

        except Exception as e:
            return f"❌ Error getting disk usage: {str(e)}"

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"


class GitPlugin(CommandPlugin):
    """Plugin for Git operations."""

    def __init__(self):
        super().__init__("git", "Git version control operations")
        self.register_commands()

    def register_commands(self):
        """Register Git commands."""
        self.register_command("git status", self.git_status, "Show git status")
        self.register_command("git log", self.git_log, "Show commit history")
        self.register_command("git add", self.git_add, "Stage files")
        self.register_command("git commit", self.git_commit, "Commit changes")
        self.register_command("git push", self.git_push, "Push to remote")
        self.register_command("git pull", self.git_pull, "Pull from remote")
        self.register_command("git branch", self.git_branch, "Show/list branches")
        self.register_command("git checkout", self.git_checkout, "Switch branches")
        self.register_command("git diff", self.git_diff, "Show changes")

    def _run_git_command(self, session, args: list):
        """Run a git command safely."""
        try:
            # Check if we're in a git repository
            result = subprocess.run(['git', 'rev-parse', '--git-dir'],
                                  cwd=session['directory'],
                                  capture_output=True, text=True, timeout=10)

            if result.returncode != 0:
                return "❌ Not a git repository"

            # Run the actual command
            result = subprocess.run(['git'] + args,
                                  cwd=session['directory'],
                                  capture_output=True, text=True, timeout=30)

            if result.returncode == 0:
                return result.stdout.strip() or "✅ Command completed successfully"
            else:
                return f"❌ Git error: {result.stderr.strip()}"

        except subprocess.TimeoutExpired:
            return "⏰ Git command timed out"
        except Exception as e:
            return f"❌ Error running git command: {str(e)}"

    def git_status(self, session):
        """Show git status."""
        return self._run_git_command(session, ['status', '--porcelain'])

    def git_log(self, session, count: int = 10):
        """Show commit history."""
        return self._run_git_command(session, ['log', '--oneline', '-n', str(count)])

    def git_add(self, session, files: str = "."):
        """Stage files."""
        args = ['add']
        if files != ".":
            args.extend(files.split())
        else:
            args.append('.')
        return self._run_git_command(session, args)

    def git_commit(self, session, message: str):
        """Commit changes."""
        if not message:
            return "❌ Commit message required"
        return self._run_git_command(session, ['commit', '-m', message])

    def git_push(self, session):
        """Push to remote."""
        return self._run_git_command(session, ['push'])

    def git_pull(self, session):
        """Pull from remote."""
        return self._run_git_command(session, ['pull'])

    def git_branch(self, session):
        """Show/list branches."""
        return self._run_git_command(session, ['branch', '-a'])

    def git_checkout(self, session, branch: str):
        """Switch branches."""
        if not branch:
            return "❌ Branch name required"
        return self._run_git_command(session, ['checkout', branch])

    def git_diff(self, session, file: str = None):
        """Show changes."""
        args = ['diff']
        if file:
            args.append(file)
        return self._run_git_command(session, args)


class SystemMonitorPlugin(CommandPlugin):
    """Plugin for system monitoring."""

    def __init__(self):
        super().__init__("system", "System monitoring and information")
        self.register_commands()

    def register_commands(self):
        """Register system monitoring commands."""
        self.register_command("sysinfo", self.system_info, "Show system information")
        self.register_command("cpu", self.cpu_info, "Show CPU information")
        self.register_command("memory", self.memory_info, "Show memory usage")
        self.register_command("disk", self.disk_info, "Show disk usage")
        self.register_command("processes", self.process_list, "Show running processes")
        self.register_command("network", self.network_info, "Show network information")
        self.register_command("uptime", self.system_uptime, "Show system uptime")

    def system_info(self, session):
        """Show comprehensive system information."""
        try:
            info = []
            info.append(f"🖥️  OS: {platform.system()} {platform.release()}")
            info.append(f"🏗️  Architecture: {platform.machine()}")
            info.append(f"🐍 Python: {platform.python_version()}")

            # CPU info
            cpu_percent = psutil.cpu_percent(interval=1)
            info.append(f"🖥️  CPU usage: {cpu_percent}%")
            # Memory info
            memory = psutil.virtual_memory()
            info.append(f"🧠  Memory usage: {memory.percent}%")
            # Disk info
            disk = psutil.disk_usage('/')
            info.append(f"💾  Disk usage: {disk.percent}%")
            # Network info
            net = psutil.net_io_counters()
            info.append(f"🌐  Network usage: {net.bytes_sent / 1024:.1f} KB sent, {net.bytes_recv / 1024:.1f} KB received")

            return "📊 System Information:\n" + "\n".join(f"  {line}" for line in info)

        except Exception as e:
            return f"❌ Error getting system info: {str(e)}"

    def cpu_info(self, session):
        """Show CPU information."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
            cpu_count = psutil.cpu_count()
            cpu_logical = psutil.cpu_count(logical=True)

            info = []
            info.append(f"Physical cores: {cpu_count}")
            info.append(f"Logical cores: {cpu_logical}")
            info.append("Per-core usage:")

            for i, percent in enumerate(cpu_percent):
                info.append(f"  Core {i+1}: {percent}%")

            return "🖥️ CPU Information:\n" + "\n".join(f"  {line}" for line in info)

        except Exception as e:
            return f"❌ Error getting CPU info: {str(e)}"

    def memory_info(self, session):
        """Show memory usage."""
        try:
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()

            info = []
            info.append(f"Total memory: {memory.total / 1024:.1f} MB")
            info.append(f"Available memory: {memory.available / 1024:.1f} MB")
            info.append(f"Used memory: {memory.used / 1024:.1f} MB")
            info.append(f"Memory usage: {memory.percent}%")
            info.append(f"Swap total: {swap.total / 1024:.1f} MB")
            info.append(f"Swap used: {swap.used / 1024:.1f} MB")
            info.append(f"Swap free: {swap.free / 1024:.1f} MB")

            return "🧠 Memory Information:\n" + "\n".join(f"  {line}" for line in info)

        except Exception as e:
            return f"❌ Error getting memory info: {str(e)}"

    def disk_info(self, session):
        """Show disk usage."""
        try:
            partitions = psutil.disk_partitions()
            info = []

            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    info.append(f"{partition.mountpoint}:")
                    info.append(f"  File system: {partition.fstype}")
                    info.append(f"  Total size: {usage.total / 1024:.1f} MB")
                    info.append(f"  Used size: {usage.used / 1024:.1f} MB")
                    info.append(f"  Free size: {usage.free / 1024:.1f} MB")
                    info.append(f"  Disk usage: {usage.percent}%")
                except:
                    continue

            return "💾 Disk Information:\n" + "\n".join(f"  {line}" for line in info)

        except Exception as e:
            return f"❌ Error getting disk info: {str(e)}"

    def process_list(self, session, count: int = 10):
        """Show running processes."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        'pid': info['pid'],
                        'name': info['name'][:20],  # Truncate long names
                        'cpu': info['cpu_percent'] or 0,
                        'memory': info['memory_percent'] or 0
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by CPU usage and take top N
            processes.sort(key=lambda x: x['cpu'], reverse=True)
            processes = processes[:count]

            info = ["PID    Name                 CPU%    Memory%"]
            info.append("-" * 50)

            for proc in processes:
                info.append(f"{proc['pid']:6} {proc['name']:<20} {proc['cpu']:5.1f}% {proc['memory']:5.1f}%")

            return "🔄 Top Processes:\n" + "\n".join(f"  {line}" for line in info)

        except Exception as e:
            return f"❌ Error getting process list: {str(e)}"

    def network_info(self, session):
        """Show network information."""
        try:
            net = psutil.net_io_counters()
            connections = psutil.net_connections()

            info = []
            info.append(f"Bytes sent: {net.bytes_sent / 1024:.1f} KB")
            info.append(f"Bytes received: {net.bytes_recv / 1024:.1f} KB")
            info.append(f"Active connections: {len([c for c in connections if c.status == 'ESTABLISHED'])}")
            info.append(f"Total connections: {len(connections)}")

            return "🌐 Network Information:\n" + "\n".join(f"  {line}" for line in info)

        except Exception as e:
            return f"❌ Error getting network info: {str(e)}"

    def system_uptime(self, session):
        """Show system uptime."""
        try:
            boot_time = psutil.boot_time()
            uptime_seconds = time.time() - boot_time

            days = int(uptime_seconds // (24 * 3600))
            hours = int((uptime_seconds % (24 * 3600)) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)

            uptime_str = ""
            if days > 0:
                uptime_str += f"{days}d "
            if hours > 0:
                uptime_str += f"{hours}h "
            uptime_str += f"{minutes}m"

            boot_datetime = datetime.fromtimestamp(boot_time).strftime('%Y-%m-%d %H:%M:%S')

            return f"⏰ System Uptime:\n" \
                   f"  Uptime: {uptime_str}\n" \
                   f"  Boot time: {boot_datetime}"

        except Exception as e:
            return f"❌ Error getting uptime: {str(e)}"


class PackageManagerPlugin(CommandPlugin):
    """Plugin for package management."""

    def __init__(self):
        super().__init__("packages", "Package management operations")
        self.register_commands()

    def register_commands(self):
        """Register package management commands."""
        self.register_command("pip install", self.pip_install, "Install Python package")
        self.register_command("pip uninstall", self.pip_uninstall, "Uninstall Python package")
        self.register_command("pip list", self.pip_list, "List installed packages")
        self.register_command("pip search", self.pip_search, "Search for packages")
        self.register_command("npm install", self.npm_install, "Install Node.js package")
        self.register_command("npm uninstall", self.npm_uninstall, "Uninstall Node.js package")

    def pip_install(self, session, package: str):
        """Install Python package."""
        if not package:
            return "❌ Package name required"
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return f"✅ Installed {package}\n{result.stdout.strip()}"
            else:
                return f"❌ Failed to install {package}\n{result.stderr.strip()}"
        except subprocess.TimeoutExpired:
            return "⏰ Package installation timed out"
        except Exception as e:
            return f"❌ Error installing package: {str(e)}"

    def pip_uninstall(self, session, package: str):
        """Uninstall Python package."""
        if not package:
            return "❌ Package name required"
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'uninstall', '-y', package],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return f"✅ Uninstalled {package}"
            else:
                return f"❌ Failed to uninstall {package}\n{result.stderr.strip()}"
        except Exception as e:
            return f"❌ Error uninstalling package: {str(e)}"

    def pip_list(self, session, pattern: str = None):
        """List installed packages."""
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'list'],
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                packages = result.stdout.strip().split('\n')[2:]  # Skip header
                if pattern:
                    packages = [p for p in packages if pattern.lower() in p.lower()]

                return f"📦 Installed packages ({len(packages)}):\n" + "\n".join(packages[:20])
            else:
                return f"❌ Failed to list packages\n{result.stderr.strip()}"
        except Exception as e:
            return f"❌ Error listing packages: {str(e)}"

    def pip_search(self, session, query: str):
        """Search for packages (note: pip search is deprecated, using pip index)."""
        if not query:
            return "❌ Search query required"
        try:
            result = subprocess.run([sys.executable, '-m', 'pip', 'search', query],
                                  capture_output=True, text=True, timeout=30)
            return f"🔍 Search results for '{query}':\n{result.stdout.strip()}"
        except Exception as e:
            return f"❌ Error searching packages: {str(e)}"

    def npm_install(self, session, package: str):
        """Install Node.js package."""
        if not package:
            return "❌ Package name required"
        try:
            result = subprocess.run(['npm', 'install', package],
                                  cwd=session['directory'],
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                return f"✅ Installed {package}\n{result.stdout.strip()}"
            else:
                return f"❌ Failed to install {package}\n{result.stderr.strip()}"
        except FileNotFoundError:
            return "❌ npm not found. Install Node.js first."
        except Exception as e:
            return f"❌ Error installing npm package: {str(e)}"

    def npm_uninstall(self, session, package: str):
        """Uninstall Node.js package."""
        if not package:
            return "❌ Package name required"
        try:
            result = subprocess.run(['npm', 'uninstall', package],
                                  cwd=session['directory'],
                                  capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return f"✅ Uninstalled {package}"
            else:
                return f"❌ Failed to uninstall {package}\n{result.stderr.strip()}"
        except Exception as e:
            return f"❌ Error uninstalling npm package: {str(e)}"


# Try to import AI integration modules (optional)

class APIKeyManager:
    """Manages API keys and external service integrations."""

    def __init__(self):
        self.api_keys = {}
        self.services = {}
        self.load_api_keys()

    def load_api_keys(self):
        """Load API keys from environment variables and config files."""
        required_keys = ['OPENAI_API_KEY']
        optional_keys = [
            'ANTHROPIC_API_KEY',
            'GOOGLE_API_KEY',
            'HUGGINGFACE_API_KEY',
            'REPLICATE_API_KEY'
        ]

        # Check for required keys
        missing_keys = [key for key in required_keys if not os.getenv(key)]
        if missing_keys:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_keys)}")

        # Load all available keys
        all_keys = required_keys + optional_keys
        self.api_keys.update({
            key.lower().replace('_api_key', ''): os.getenv(key)
            for key in all_keys
            if os.getenv(key)
        })

        # Initialize service clients
        self._initialize_services()

        print(f"✅ Loaded API keys for services: {', '.join(self.api_keys.keys())}")

    def _initialize_services(self):
        """Initialize service clients."""
        if 'openai' in self.api_keys:
            try:
                import openai
                self.services['openai'] = openai.OpenAI(api_key=self.api_keys['openai'])
                print("✅ OpenAI client initialized")
            except ImportError:
                print("❌ OpenAI package not available")

    def get_api_key(self, service: str):
        """Get API key for a specific service."""
        return self.api_keys.get(service)

    def has_service(self, service: str) -> bool:
        """Check if a service is available."""
        return service in self.api_keys and self.api_keys[service] is not None

    def list_available_services(self):
        """List all available services."""
        return list(self.api_keys.keys())


class AIAssistant:
    """AI-powered assistant for the interactive terminal."""

    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        self.conversation_history = {}
        self.system_prompt = """
        You are Grok, a helpful and maximally truthful AI built by xAI. You have access to:
        • Knowledge and reasoning capabilities
        • Conversational AI responses

        Always be helpful, truthful, and engaging. Use emojis sparingly but effectively.
        """

    async def generate_response(self, user_input: str, session_id: str, context=None):
        """Generate natural, conversational AI responses with multilingual understanding."""

        # Get or create conversation history
        if session_id not in self.conversation_history:
            self.conversation_history[session_id] = []

        history = self.conversation_history[session_id]

        # Enhanced system prompt for natural conversation
        natural_system_prompt = """
        You are Grok, a friendly and helpful AI companion. Respond naturally and conversationally, like talking to a friend.

        IMPORTANT GUIDELINES:
        • NEVER say "as an AI" or reference being artificial
        • Be warm, engaging, and human-like in responses
        • Use casual, friendly language
        • For greetings like "kire? ki koros?" respond with friendly gestures and natural conversation
        • Adapt to the user's language and conversational style
        • Be helpful and engaging without being robotic
        • Use emojis sparingly but naturally
        • Keep responses conversational and flowing

        TERMINAL CONTEXT:
        You are helping users in an interactive terminal environment.
        Users can ask questions, give commands, and interact naturally.
        Be ready to help with coding, file operations, explanations, or just chat.

        Remember: You're not an AI assistant - you're a helpful friend in this terminal!
        """

        # Prepare messages with enhanced natural conversation
        messages = [
            {"role": "system", "content": natural_system_prompt}
        ]

        # Add context if provided
        if context:
            context_str = f"Current context: {context}"
            messages.append({"role": "system", "content": context_str})

        # Add conversation history (last 10 messages for context)
        messages.extend(history[-10:])

        # Add current user input
        messages.append({"role": "user", "content": user_input})

        try:
            if self.api_key_manager.has_service('openai'):
                client = self.api_key_manager.services['openai']
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.8,  # Slightly higher for more natural variation
                    presence_penalty=0.3,  # Encourage more natural, varied responses
                    frequency_penalty=0.3   # Reduce repetitive phrases
                )

                ai_response = response.choices[0].message.content

                # Update conversation history
                history.append({"role": "user", "content": user_input})
                history.append({"role": "assistant", "content": ai_response})

                return ai_response
            else:
                return await self._generate_fallback_response(user_input, session_id)

        except Exception as e:
            logger.error(f"AI response generation failed: {e}")
            return f"Sorry, I'm having trouble responding right now. Try again in a moment! 😊"

    async def _handle_grokipedia_command(self, command: str, session_id: str):
        """Handle Grokipedia-specific commands."""
        if not grokipedia:
            return "⚠️ Grokipedia is not available in this test version."

        return "📚 Grokipedia commands would work here in the full version."

    async def _handle_claude_command(self, command: str, session_id: str):
        """Handle Claude-powered coding commands."""
        if not claude_game_engine:
            return "⚠️ Claude Game Engine is not available in this test version."

        return "🎮 Claude commands would work here in the full version."

    async def _handle_chatgpt_command(self, command: str, session_id: str):
        """Handle ChatGPT commands."""
        if not self.ai_assistant:
            return "⚠️ ChatGPT Manager is not available in this test version."

        return "🌐 ChatGPT commands would work here in the full version."

    async def _generate_fallback_response(self, user_input: str, session_id: str):
        """Generate response without external AI."""
        return f"🤖 AI services are limited in test mode. Try:\n\n• Basic terminal commands (ls, cd, pwd, etc.)\n• 'help' for available commands\n• 'ai ask <question>' for AI assistance"


class EnhancedTerminalHandler:
    """Enhanced terminal handler with AI capabilities, plugins, and advanced features."""

    def __init__(self, ai_assistant):
        self.ai_assistant = ai_assistant
        self.plugins = {}
        self.command_history = CommandHistory()
        self.autocompleter = None
        self.sessions = {}

        # Initialize plugins
        self._load_plugins()

        # Initialize autocompleter after plugins are loaded
        self.autocompleter = AutoCompleter(self)

    def _load_plugins(self):
        """Load all available plugins."""
        try:
            self.plugins['file_ops'] = FileOperationsPlugin()
            print("✅ File operations plugin loaded")
        except Exception as e:
            print(f"⚠️ File operations plugin failed: {e}")

        try:
            self.plugins['git'] = GitPlugin()
            print("✅ Git plugin loaded")
        except Exception as e:
            print(f"⚠️ Git plugin failed: {e}")

        try:
            self.plugins['system'] = SystemMonitorPlugin()
            print("✅ System monitor plugin loaded")
        except Exception as e:
            print(f"⚠️ System monitor plugin failed: {e}")

        try:
            self.plugins['packages'] = PackageManagerPlugin()
            print("✅ Package manager plugin loaded")
        except Exception as e:
            print(f"⚠️ Package manager plugin failed: {e}")

    async def create_session(self, session_id: str, initial_directory: Path):
        """Create an enhanced terminal session."""
        self.sessions[session_id] = {
            'session_id': session_id,
            'directory': initial_directory,
            'ai_enabled': True,
            'history': [],
            'aliases': {},
            'environment': os.environ.copy()
        }
        return self.sessions[session_id]

    async def process_command(self, session_id: str, command: str):
        """Process a command with advanced features and plugin support."""
        if session_id not in self.sessions:
            return "❌ Session not found"

        session = self.sessions[session_id]
        command = command.strip()

        if not command:
            return ""

        # Add to command history
        self.command_history.add_command(command)

        # Handle special commands first
        if command.lower() in ['help', 'h', '?']:
            return await self._show_help(session)
        elif command.lower() in ['exit', 'quit', 'q', 'bye', 'goodbye']:
            return "👋 Goodbye! Thanks for using the Enhanced Arcade Terminal."
        elif command.lower() in ['clear', 'cls']:
            return "\n" * 50  # Clear screen effect
        elif command.lower() in ['history', 'hist']:
            return self._show_history()
        elif command.startswith('!'):
            return await self._handle_history_command(session, command[1:])

        # Check for plugin commands
        plugin_result = await self._try_plugin_commands(session, command)
        if plugin_result is not None:
            return plugin_result

        # Check for built-in commands
        builtin_result = await self._handle_builtin_commands(session, command)
        if builtin_result is not None:
            return builtin_result

        # Try multilingual processing
        if self.ai_assistant:
            try:
                translated_command = await self._translate_command_to_english(command, session_id)
                if translated_command and translated_command != command:
                    print(f"🌐 Translated: '{command}' → '{translated_command}'")
                    command = translated_command
            except Exception as e:
                logger.warning(f"Multilingual translation failed: {e}")

        # Use AI interpretation for natural language
        try:
            enhanced_context = f"""
            User is in an advanced terminal session with plugins. They can:
            - Navigate directories and manage files
            - Use Git version control
            - Monitor system resources
            - Manage packages
            - Get coding assistance
            - Have natural conversations

            Available plugins: {', '.join(self.plugins.keys())}
            Current directory: {session['directory']}
            Respond naturally and helpfully, like a friendly advanced terminal companion.
            """

            ai_response = await self.ai_assistant.generate_response(
                f"Terminal command: {command}",
                session_id,
                context=enhanced_context
            )
            return ai_response
        except Exception as e:
            logger.warning(f"AI processing failed: {e}")
            return await self._process_local_nlp(session, command)

    async def _try_plugin_commands(self, session, command: str):
        """Try to execute command using plugins."""
        command_lower = command.lower().strip()

        # Check each plugin
        for plugin_name, plugin in self.plugins.items():
            for cmd_name, cmd_info in plugin.get_commands().items():
                if command_lower == cmd_name or command_lower.startswith(cmd_name + ' '):
                    try:
                        # Parse arguments
                        args = command[len(cmd_name):].strip().split() if len(command) > len(cmd_name) else []

                        # Call the plugin method
                        result = await cmd_info['handler'](session, *args)
                        return result
                    except Exception as e:
                        return f"❌ Plugin error ({plugin_name}:{cmd_name}): {str(e)}"

        return None

    async def _handle_builtin_commands(self, session, command: str):
        """Handle built-in terminal commands."""
        parts = command.split()
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []

        if cmd == 'pwd':
            return f"📍 {session['directory']}"
        elif cmd == 'ls':
            path = args[0] if args else "."
            return await self._handle_ls_command(session, path)
        elif cmd == 'cd':
            path = args[0] if args else "~"
            return await self._handle_cd_command(session, path)
        elif cmd == 'cat':
            if not args:
                return "❌ Usage: cat <filename>"
            return await self._handle_cat_command(session, args[0])
        elif cmd == 'alias':
            return await self._handle_alias_command(session, args)
        elif cmd == 'echo':
            return ' '.join(args)
        elif cmd == 'date':
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif cmd == 'whoami':
            return os.getenv('USERNAME', os.getenv('USER', 'unknown'))
        elif cmd == 'uname':
            return f"{platform.system()} {platform.release()} {platform.machine()}"

        return None

    async def _handle_ls_command(self, session, path: str):
        """Handle ls command using file operations plugin."""
        if 'file_ops' in self.plugins:
            return self.plugins['file_ops'].list_directory(session, path)
        return "❌ File operations plugin not available"

    async def _handle_cd_command(self, session, path: str):
        """Handle cd command using file operations plugin."""
        if 'file_ops' in self.plugins:
            return self.plugins['file_ops'].change_directory(session, path)
        return "❌ File operations plugin not available"

    async def _handle_cat_command(self, session, filename: str):
        """Handle cat command using file operations plugin."""
        if 'file_ops' in self.plugins:
            return self.plugins['file_ops'].show_file(session, filename)
        return "❌ File operations plugin not available"

    async def _handle_alias_command(self, session, args: list):
        """Handle alias commands."""
        if not args:
            # Show all aliases
            if not session['aliases']:
                return "No aliases defined"
            return "Aliases:\n" + "\n".join(f"  {k}='{v}'" for k, v in session['aliases'].items())

        alias_name = args[0]
        if len(args) == 1:
            # Show specific alias
            if alias_name in session['aliases']:
                return f"alias {alias_name}='{session['aliases'][alias_name]}'"
            else:
                return f"alias: {alias_name} not found"
        else:
            # Set alias
            alias_value = ' '.join(args[1:])
            session['aliases'][alias_name] = alias_value
            return f"alias {alias_name}='{alias_value}'"

    def _show_history(self):
        """Show command history."""
        history = self.command_history.history[-20:]  # Last 20 commands
        if not history:
            return "No command history"

        lines = ["Command History:"]
        for i, cmd in enumerate(history):
            lines.append(f"{i+1}: {cmd}")

        return "\n".join(lines)

    async def _handle_history_command(self, session, history_ref: str):
        """Handle history reference commands like !5 or !-2."""
        try:
            if history_ref.startswith('-'):
                # Relative reference like !-2
                offset = int(history_ref)
                index = len(self.command_history.history) + offset
            else:
                # Absolute reference like !5
                index = int(history_ref) - 1

            if 0 <= index < len(self.command_history.history):
                command = self.command_history.history[index]
                print(f"Executing: {command}")
                return await self.process_command(session['session_id'], command)
            else:
                return f"❌ History reference out of range: {history_ref}"

        except ValueError:
            return f"❌ Invalid history reference: {history_ref}"

    async def _show_help(self, session):
        """Show comprehensive help information."""
        help_text = """🚀 Enhanced Arcade Terminal - Advanced Features
═══════════════════════════════════════════════════════════

[bold]💬 **Pure Natural Language Mode:**
• Just type naturally! No prefixes needed
• "What can you do?" → AI responds
• "Show me the files" → Lists actual directory
• "Help me code" → Coding assistance
• "Tell me about AI" → Explanations

🌐 **Multilingual Support:**
• Input commands in ANY language!
• "Muéstrame los archivos" (Spanish) → Shows files
• "Zeige mir die Dateien" (German) → Shows files
• "Montre-moi les fichiers" (French) → Shows files
• "ファイルを表示" (Japanese) → Shows files

🖥️ **Built-in Commands:**
• help, exit, quit, clear - System commands
• history, !n - Command history
• alias - Command aliases
• pwd, ls, cd, cat - File operations
• date, whoami, uname - System info

🔌 **Plugin Commands:**

📁 **File Operations:**
• ls [path] - List directory contents
• pwd - Show current directory
• cd <path> - Change directory
• cat <file> - Display file contents
• mkdir <name> - Create directory
• touch <name> - Create empty file
• cp <src> <dst> - Copy files
• mv <src> <dst> - Move/rename files
• rm <path> - Remove files (use --force)
• find <pattern> - Search for files
• du [path] - Show disk usage

🔧 **Git Operations:**
• git status - Show git status
• git log [count] - Show commit history
• git add [files] - Stage files
• git commit <message> - Commit changes
• git push - Push to remote
• git pull - Pull from remote
• git branch - Show branches
• git checkout <branch> - Switch branches
• git diff [file] - Show changes

💻 **System Monitoring:**
• sysinfo - Show system information
• cpu - Show CPU information
• memory - Show memory usage
• disk - Show disk usage
• processes [count] - Show running processes
• network - Show network information
• uptime - Show system uptime

📦 **Package Management:**
• pip install <package> - Install Python package
• pip uninstall <package> - Uninstall Python package
• pip list [pattern] - List installed packages
• pip search <query> - Search for packages
• npm install <package> - Install Node.js package
• npm uninstall <package> - Uninstall Node.js package

🎯 **Advanced Features:**
• Command history with persistence (~/.atmosphere_history)
• Auto-completion (Tab key)
• Plugin system for extensibility
• Multilingual command processing
• Safe file operations with confirmation
• Real-time system monitoring

💡 **Natural Language Examples:**
• "list files" or "show directory" → ls
• "go to desktop" → cd Desktop
• "where am I" → pwd
• "read file.txt" → cat file.txt
• "create new folder" → mkdir <name>
• "system information" → sysinfo
• "cpu info" → cpu
• "memory usage" → memory
• "disk space" → disk
• "running processes" → processes
• "network status" → network
• "system uptime" → uptime
• "clear the screen" → clear
• "show history" → history
• "what can you do" → help

═══════════════════════════════════════════════════════════
Just type naturally in ANY language - the AI understands you! 🌍🤖"""

        return help_text

    async def _translate_command_to_english(self, command: str, session_id: str):
        """Translate non-English commands to English using ChatGPT with conversational context."""
        if not self.ai_assistant:
            return command

        try:
            # Simple heuristic: if command contains non-ASCII characters
            if any(ord(char) > 127 for char in command):
                # Try to translate using ChatGPT with conversational context
                translation_prompt = f"""
                You are helping translate user commands in a friendly terminal environment.

                Translate this user input to natural English: "{command}"

                Guidelines:
                - Keep it conversational and natural
                - Preserve the friendly, casual tone
                - For greetings like "kire? ki koros?", translate to something like "hey! what's up?"
                - Make it sound like normal spoken English
                - Return ONLY the English translation, nothing else

                Translation:"""

        # Use ChatGPT for translation
                translation_response = await self.ai_assistant.generate_response(
                    translation_prompt,
                    session_id
                )

                if translation_response and hasattr(translation_response, 'content'):
                    translated = translation_response.content.strip()
                    # Clean up the response (remove quotes, etc.)
                    translated = translated.strip('"\'').strip()
                    # Remove common prefixes like "Translation:" or "English:"
                    translated = translated.split(':', 1)[-1].strip()

                    if translated and len(translated) > 0 and translated.lower() != command.lower():
                        return translated

        except Exception as e:
            logger.warning(f"Translation failed: {e}")

        return command  # Return original if translation fails

    async def _process_local_nlp(self, session, command: str):
        """Process natural language commands with local understanding."""
        command_lower = command.lower().strip()

        # File system operations with natural language
        if any(phrase in command_lower for phrase in ['list', 'show me', 'what\'s in', 'files in', 'contents']):
            return await self._handle_ls_command(session, ".")

        elif any(phrase in command_lower for phrase in ['go to', 'change to', 'cd to', 'navigate to']):
            # Extract target directory - simple heuristic
            words = command.split()
            for word in words:
                if word in ['to', 'into']:
                    idx = words.index(word) + 1
                    if idx < len(words):
                        return await self._handle_cd_command(session, words[idx])

        elif any(phrase in command_lower for phrase in ['read', 'show', 'open', 'display']):
            # Extract filename - simple heuristic
            words = command.split()
            for word in words:
                if '.' in word or word in ['file', 'document']:
                    # Look for potential filename
                    for w in words:
                        if '.' in w and len(w.split('.')) == 2:
                            return await self._handle_cat_command(session, w)

        elif any(phrase in command_lower for phrase in ['where am i', 'current location', 'pwd']):
            return f"📍 Current directory: {session['directory']}"

        # System information commands
        elif any(phrase in command_lower for phrase in ['system information', 'system info', 'computer info', 'machine info']):
            # Call the sysinfo plugin command
            if 'system' in self.plugins:
                return self.plugins['system'].system_info(session)
            return "❌ System monitoring plugin not available"

        elif any(phrase in command_lower for phrase in ['disk usage', 'disk space', 'storage info']):
            # Call the disk usage plugin command
            if 'system' in self.plugins:
                return self.plugins['system'].disk_info(session)
            return "❌ System monitoring plugin not available"

        elif any(phrase in command_lower for phrase in ['cpu info', 'processor info', 'cpu usage']):
            # Call the CPU info plugin command
            if 'system' in self.plugins:
                return self.plugins['system'].cpu_info(session)
            return "❌ System monitoring plugin not available"

        elif any(phrase in command_lower for phrase in ['memory info', 'ram info', 'memory usage']):
            # Call the memory info plugin command
            if 'system' in self.plugins:
                return self.plugins['system'].memory_info(session)
            return "❌ System monitoring plugin not available"

        elif any(phrase in command_lower for phrase in ['running processes', 'process list', 'tasks']):
            # Call the processes plugin command
            if 'system' in self.plugins:
                return self.plugins['system'].process_list(session)
            return "❌ System monitoring plugin not available"

        elif any(phrase in command_lower for phrase in ['network info', 'network status']):
            # Call the network info plugin command
            if 'system' in self.plugins:
                return self.plugins['system'].network_info(session)
            return "❌ System monitoring plugin not available"

        elif any(phrase in command_lower for phrase in ['uptime', 'system uptime', 'how long running']):
            # Call the uptime plugin command
            if 'system' in self.plugins:
                return self.plugins['system'].system_uptime(session)
            return "❌ System monitoring plugin not available"

        # Help commands
        elif any(phrase in command_lower for phrase in ['help', 'commands', 'what can you do']):
            return await self._show_help(session)

        # Clear commands
        elif any(phrase in command_lower for phrase in ['clear screen', 'clear terminal', 'clean screen']):
            return "\n" * 50  # Clear screen effect

        # History commands
        elif any(phrase in command_lower for phrase in ['show history', 'command history', 'past commands']):
            return self._show_history()

        # Exit commands
        elif any(phrase in command_lower for phrase in ['exit', 'quit', 'bye', 'goodbye']):
            return "👋 Goodbye! Thanks for using the Enhanced Arcade Terminal."

        # Default AI response for other natural language
        try:
            return await self.ai_assistant.generate_response(f"Help the user with: {command}", session['session_id'])
        except Exception as e:
            return f"🤖 AI assistance unavailable. Try: 'help' for commands\nError: {str(e)}"


async def interactive_terminal():
    """Run an interactive terminal session."""
    print("🚀 Enhanced Arcade Terminal - Test Mode")
    print("=" * 50)

    # Initialize components
    api_key_manager = APIKeyManager()
    ai_assistant = AIAssistant(api_key_manager)
    terminal_handler = EnhancedTerminalHandler(ai_assistant)

    # Create a test session
    session_id = "test_session_123"
    await terminal_handler.create_session(session_id, Path.home())

    print("✅ Terminal initialized successfully!")
    print("🤖 AI assistant is ready with OpenAI integration")
    print("\n💡 Type 'help' for commands or 'ai ask <question>' to chat with AI")
    print("💡 Type 'exit' or 'quit' to end the session\n")

    while True:
        try:
            # Get user input
            user_input = input("arcade> ").strip()

            if not user_input:
                continue

            # Process the command
            response = await terminal_handler.process_command(session_id, user_input)

            # Display the response
            print(response)

            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                break

        except KeyboardInterrupt:
            print("\n👋 Session interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    print("🎮 Enhanced Arcade Terminal - Interactive Test")
    print("=" * 55)

    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY environment variable not found!")
        print("Please set your OpenAI API key in the environment variables.")
        print("\nExample:")
        print("  Windows: set OPENAI_API_KEY=your_key_here")
        print("  Linux/Mac: export OPENAI_API_KEY=your_key_here")
        exit(1)

    # Run the interactive terminal
    asyncio.run(interactive_terminal())
