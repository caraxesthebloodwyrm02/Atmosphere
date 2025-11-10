"""
Terminal Handler for PowerShell Process Management
Manages PowerShell processes, PTY handling, and command execution.
"""

import os
import sys
import subprocess
import platform
import logging
import threading
import queue
import time
from pathlib import Path
from typing import Optional, Callable, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TerminalSession:
    """Represents a terminal session"""
    session_id: str
    process: Optional[subprocess.Popen]
    process_id: Optional[int]
    working_directory: Path
    environment: Dict[str, str]
    created_at: float
    last_activity: float


class TerminalHandler:
    """Handles PowerShell terminal processes"""
    
    def __init__(
        self,
        pwsh_path: Optional[Path] = None,
        sandbox_root: Optional[Path] = None,
        security_manager: Optional[Any] = None
    ):
        self.pwsh_path = pwsh_path or self._find_pwsh()
        self.sandbox_root = sandbox_root
        self.security_manager = security_manager
        self.sessions: Dict[str, TerminalSession] = {}
        
        if not self.pwsh_path or not self.pwsh_path.exists():
            raise FileNotFoundError(
                f"PowerShell executable not found at {self.pwsh_path}. "
                "Please ensure PowerShell Core is installed."
            )
    
    def _find_pwsh(self) -> Optional[Path]:
        """Find PowerShell executable"""
        # Check in Arcade/terminal directory
        arcade_root = Path(__file__).parent.parent
        terminal_dir = arcade_root / "terminal"
        
        if platform.system() == "Windows":
            pwsh_exe = terminal_dir / "pwsh.exe"
        else:
            pwsh_exe = terminal_dir / "pwsh"
        
        if pwsh_exe.exists():
            return pwsh_exe
        
        # Try system PATH
        try:
            result = subprocess.run(
                ["pwsh", "--version"],
                capture_output=True,
                timeout=2
            )
            if result.returncode == 0:
                return Path("pwsh")  # Use system pwsh
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        return None
    
    def create_session(
        self,
        session_id: str,
        initial_directory: Optional[Path] = None,
        environment: Optional[Dict[str, str]] = None
    ) -> TerminalSession:
        """Create a new terminal session"""
        if session_id in self.sessions:
            raise ValueError(f"Session {session_id} already exists")
        
        # Determine working directory
        if initial_directory:
            work_dir = initial_directory
        elif self.sandbox_root:
            work_dir = self.sandbox_root
        else:
            work_dir = Path.home()
        
        work_dir = work_dir.resolve()
        work_dir.mkdir(parents=True, exist_ok=True)
        
        # Prepare environment
        env = os.environ.copy()
        env.update(environment or {})
        
        # Set PowerShell execution policy to Restricted for security
        env['PSExecutionPolicyPreference'] = 'Restricted'
        
        # Create PowerShell process with restricted mode
        try:
            # On Windows, use subprocess directly
            # On Unix, we'd use pty, but for Windows we'll use subprocess
            process = subprocess.Popen(
                [str(self.pwsh_path), "-NoLogo", "-NoProfile", "-ExecutionPolicy", "Restricted"],
                cwd=str(work_dir),
                env=env,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=0,
                shell=False
            )
            
            session = TerminalSession(
                session_id=session_id,
                process=process,
                process_id=process.pid,
                working_directory=work_dir,
                environment=env,
                created_at=__import__('time').time(),
                last_activity=__import__('time').time()
            )
            
            self.sessions[session_id] = session
            
            # Start resource monitoring if security manager is available
            if self.security_manager and process.pid:
                self.security_manager.start_resource_monitoring(process.pid)
            
            logger.info(f"Created terminal session {session_id} (PID: {process.pid})")
            return session
            
        except Exception as e:
            logger.error(f"Failed to create terminal session: {e}")
            raise
    
    def execute_command(
        self,
        session_id: str,
        command: str,
        timeout: float = 10.0
    ) -> tuple[str, str, int]:
        """
        Execute a command in the session.
        Returns (stdout, stderr, return_code)
        """
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        if not session.process:
            raise RuntimeError(f"Session {session_id} process not available")
        
        # Update last activity
        session.last_activity = time.time()
        
        # Validate command if security manager is available
        if self.security_manager:
            is_allowed, reason = self.security_manager.validate_command(command)
            if not is_allowed:
                return "", f"Command blocked: {reason}", 1
        
        # Check resource limits
        if self.security_manager and session.process_id:
            within_limits, reason = self.security_manager.check_resource_limits(session.process_id)
            if not within_limits:
                return "", f"Resource limit exceeded: {reason}", 1
        
        try:
            # Execute command
            session.process.stdin.write(command + "\n")
            session.process.stdin.flush()
            
            # Read output with timeout
            stdout_lines = []
            stderr_lines = []
            
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                # Check if process is still running
                if session.process.poll() is not None:
                    # Process has terminated
                    break
                
                # Read available output
                # Note: This is a simplified implementation
                # For production, consider using threading or asyncio
                try:
                    # For Windows, we need a different approach
                    if platform.system() == "Windows":
                        # Use a thread to read output
                        output_queue = queue.Queue()
                        
                        def read_output():
                            try:
                                while True:
                                    line = session.process.stdout.readline()
                                    if not line:
                                        break
                                    output_queue.put(('stdout', line))
                            except Exception:
                                pass
                        
                        def read_error():
                            try:
                                while True:
                                    line = session.process.stderr.readline()
                                    if not line:
                                        break
                                    output_queue.put(('stderr', line))
                            except Exception:
                                pass
                        
                        stdout_thread = threading.Thread(target=read_output, daemon=True)
                        stderr_thread = threading.Thread(target=read_error, daemon=True)
                        stdout_thread.start()
                        stderr_thread.start()
                        
                        # Wait for output with timeout
                        end_time = time.time() + timeout
                        while time.time() < end_time:
                            try:
                                stream_type, line = output_queue.get(timeout=0.1)
                                if stream_type == 'stdout':
                                    stdout_lines.append(line)
                                else:
                                    stderr_lines.append(line)
                            except queue.Empty:
                                if session.process.poll() is not None:
                                    break
                                continue
                        
                        break
                    else:
                        # Unix-like systems
                        if select.select([session.process.stdout], [], [], 0.1)[0]:
                            line = session.process.stdout.readline()
                            if line:
                                stdout_lines.append(line)
                except Exception as e:
                    logger.debug(f"Error reading output: {e}")
                    break
            
            stdout = "".join(stdout_lines)
            stderr = "".join(stderr_lines)
            
            # Get return code
            return_code = session.process.poll()
            if return_code is None:
                return_code = 0  # Still running
            
            return stdout, stderr, return_code
            
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            return "", str(e), 1
    
    def send_input(self, session_id: str, data: bytes) -> None:
        """Send raw input to terminal"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        if session.process and session.process.stdin:
            try:
                session.process.stdin.write(data.decode('utf-8', errors='ignore'))
                session.process.stdin.flush()
            except Exception as e:
                logger.error(f"Error sending input: {e}")
    
    def get_output(self, session_id: str) -> tuple[str, str]:
        """Get available output from terminal"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        stdout = ""
        stderr = ""
        
        if session.process:
            # Read available output (non-blocking)
            # This is a simplified implementation
            # In production, use proper async I/O
            pass
        
        return stdout, stderr
    
    def terminate_session(self, session_id: str) -> None:
        """Terminate a terminal session"""
        if session_id not in self.sessions:
            return
        
        session = self.sessions[session_id]
        
        if session.process:
            try:
                # Stop resource monitoring
                if self.security_manager and session.process_id:
                    stats = self.security_manager.stop_resource_monitoring(session.process_id)
                    logger.info(f"Session {session_id} resource stats: {stats}")
                
                # Terminate process
                session.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    session.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if needed
                    session.process.kill()
                
                logger.info(f"Terminated session {session_id}")
            except Exception as e:
                logger.error(f"Error terminating session: {e}")
        
        del self.sessions[session_id]
    
    def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        return {
            'session_id': session_id,
            'process_id': session.process_id,
            'working_directory': str(session.working_directory),
            'created_at': session.created_at,
            'last_activity': session.last_activity,
            'is_running': session.process.poll() is None if session.process else False
        }
    
    def list_sessions(self) -> List[str]:
        """List all active session IDs"""
        return list(self.sessions.keys())

