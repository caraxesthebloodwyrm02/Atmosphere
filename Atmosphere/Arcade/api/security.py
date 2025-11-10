"""
Security Layer for Arcade Terminal
Provides sandboxing, command validation, and resource management.
"""

import os
import json
import logging
import platform
from pathlib import Path
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
import psutil
import time

logger = logging.getLogger(__name__)


@dataclass
class SecurityConfig:
    """Security configuration for terminal sessions"""
    allowed_commands: Set[str]
    blocked_commands: Set[str]
    max_process_time: float = 30.0  # seconds
    max_memory_mb: int = 512
    max_cpu_percent: float = 50.0
    session_timeout: int = 3600  # seconds
    sandbox_root: Optional[Path] = None
    allow_network: bool = False


class CommandValidator:
    """Validates and filters commands before execution"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.allowed_commands = config.allowed_commands
        self.blocked_commands = config.blocked_commands
        
    def is_command_allowed(self, command: str) -> tuple[bool, Optional[str]]:
        """
        Check if a command is allowed.
        Returns (is_allowed, reason)
        """
        command_lower = command.strip().lower()
        
        # Check for blocked commands first
        for blocked in self.blocked_commands:
            if blocked in command_lower:
                return False, f"Command '{blocked}' is not allowed for security reasons"
        
        # Check for allowed commands (whitelist approach)
        if self.allowed_commands:
            # Extract base command (first word)
            base_command = command_lower.split()[0] if command_lower.split() else ""
            
            # Special handling for cd commands (game navigation)
            if command_lower.startswith("cd"):
                return True, None
            
            # Check if base command is in whitelist
            if base_command in self.allowed_commands:
                return True, None
            
            # Check for PowerShell cmdlets (Get-*, Set-*, etc.)
            if "-" in base_command and any(
                base_command.startswith(prefix) 
                for prefix in ["get-", "set-", "show-", "write-", "read-", "test-"]
            ):
                # Extract the verb
                verb_part = base_command.split("-")[0]
                if verb_part in ["get", "set", "show", "write", "read", "test"]:
                    return True, None
            
            return False, f"Command '{base_command}' is not in the allowed list"
        
        return True, None
    
    def sanitize_input(self, input_str: str) -> str:
        """Sanitize user input to prevent injection attacks"""
        # Remove control characters except newline and tab
        sanitized = "".join(
            char for char in input_str 
            if ord(char) >= 32 or char in ['\n', '\t']
        )
        # Limit length
        if len(sanitized) > 1000:
            sanitized = sanitized[:1000]
            logger.warning(f"Input truncated to 1000 characters")
        return sanitized


class ResourceLimiter:
    """Monitors and limits resource usage"""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.process_monitors: Dict[int, Dict] = {}
    
    def start_monitoring(self, process_id: int) -> None:
        """Start monitoring a process"""
        try:
            process = psutil.Process(process_id)
            self.process_monitors[process_id] = {
                'start_time': time.time(),
                'process': process,
                'max_memory': 0,
                'max_cpu': 0.0
            }
        except psutil.NoSuchProcess:
            logger.warning(f"Process {process_id} not found for monitoring")
    
    def check_limits(self, process_id: int) -> tuple[bool, Optional[str]]:
        """
        Check if process exceeds resource limits.
        Returns (within_limits, reason)
        """
        if process_id not in self.process_monitors:
            return True, None
        
        monitor = self.process_monitors[process_id]
        process = monitor['process']
        
        try:
            # Check if process still exists
            if not process.is_running():
                return False, "Process has terminated"
            
            # Check execution time
            elapsed = time.time() - monitor['start_time']
            if elapsed > self.config.max_process_time:
                return False, f"Process exceeded max execution time ({self.config.max_process_time}s)"
            
            # Check memory usage
            memory_info = process.memory_info()
            memory_mb = memory_info.rss / (1024 * 1024)
            monitor['max_memory'] = max(monitor['max_memory'], memory_mb)
            
            if memory_mb > self.config.max_memory_mb:
                return False, f"Process exceeded max memory ({self.config.max_memory_mb}MB)"
            
            # Check CPU usage
            cpu_percent = process.cpu_percent(interval=0.1)
            monitor['max_cpu'] = max(monitor['max_cpu'], cpu_percent)
            
            if cpu_percent > self.config.max_cpu_percent:
                return False, f"Process exceeded max CPU ({self.config.max_cpu_percent}%)"
            
            return True, None
            
        except psutil.NoSuchProcess:
            return False, "Process no longer exists"
        except Exception as e:
            logger.error(f"Error checking process limits: {e}")
            return False, f"Error monitoring process: {e}"
    
    def stop_monitoring(self, process_id: int) -> Dict:
        """Stop monitoring and return stats"""
        if process_id not in self.process_monitors:
            return {}
        
        monitor = self.process_monitors.pop(process_id)
        return {
            'execution_time': time.time() - monitor['start_time'],
            'max_memory_mb': monitor['max_memory'],
            'max_cpu_percent': monitor['max_cpu']
        }


class SecurityManager:
    """Main security manager coordinating all security features"""
    
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self.validator = CommandValidator(self.config)
        self.limiter = ResourceLimiter(self.config)
        
    def _load_config(self, config_path: Optional[Path] = None) -> SecurityConfig:
        """Load security configuration"""
        if config_path is None:
            # Default to sandbox config
            arcade_root = Path(__file__).parent.parent
            config_path = arcade_root / "sandbox" / "security_config.json"
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                
                return SecurityConfig(
                    allowed_commands=set(config_data.get('allowed_commands', [])),
                    blocked_commands=set(config_data.get('blocked_commands', [])),
                    max_process_time=config_data.get('max_process_time', 30.0),
                    max_memory_mb=config_data.get('max_memory_mb', 512),
                    max_cpu_percent=config_data.get('max_cpu_percent', 50.0),
                    session_timeout=config_data.get('session_timeout', 3600),
                    sandbox_root=Path(config_data['sandbox_root']) if config_data.get('sandbox_root') else None,
                    allow_network=config_data.get('allow_network', False)
                )
            except Exception as e:
                logger.error(f"Failed to load security config: {e}")
        
        # Default configuration
        return SecurityConfig(
            allowed_commands={
                'cd', 'ls', 'dir', 'pwd', 'get-location', 'get-childitem',
                'clear', 'cls', 'echo', 'write-host', 'help', 'get-help',
                'exit', 'quit', 'history', 'get-history'
            },
            blocked_commands={
                'rm', 'del', 'remove-item', 'format', 'diskpart', 'net',
                'wmic', 'reg', 'shutdown', 'restart', 'stop-computer',
                'invoke-webrequest', 'invoke-expression', 'iex'
            },
            sandbox_root=Path(__file__).parent.parent / "sandbox" / "virtual_fs"
        )
    
    def validate_command(self, command: str) -> tuple[bool, Optional[str]]:
        """Validate a command before execution"""
        sanitized = self.validator.sanitize_input(command)
        return self.validator.is_command_allowed(sanitized)
    
    def get_sandbox_path(self, requested_path: str) -> Path:
        """Convert requested path to sandboxed path"""
        if self.config.sandbox_root:
            # Ensure path stays within sandbox
            sandbox = self.config.sandbox_root.resolve()
            requested = Path(requested_path).resolve()
            
            # Check if path is within sandbox
            try:
                requested.relative_to(sandbox)
                return requested
            except ValueError:
                # Path outside sandbox, return sandbox root
                return sandbox
        
        return Path(requested_path)
    
    def is_network_allowed(self) -> bool:
        """Check if network access is allowed"""
        return self.config.allow_network
    
    def start_resource_monitoring(self, process_id: int) -> None:
        """Start monitoring process resources"""
        self.limiter.start_monitoring(process_id)
    
    def check_resource_limits(self, process_id: int) -> tuple[bool, Optional[str]]:
        """Check if process is within resource limits"""
        return self.limiter.check_limits(process_id)
    
    def stop_resource_monitoring(self, process_id: int) -> Dict:
        """Stop monitoring and get resource stats"""
        return self.limiter.stop_monitoring(process_id)

