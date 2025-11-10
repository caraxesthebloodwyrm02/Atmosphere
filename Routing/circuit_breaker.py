"""
Circuit Breaker Pattern Implementation
=====================================

This module implements a circuit breaker pattern to prevent cascading failures
in the routing system. It monitors for failures and opens the circuit when
errors exceed a threshold, allowing the failing component time to recover.
"""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, TypeVar, cast

# Type variable for the wrapped function's return type
T = TypeVar('T')


class CircuitState(Enum):
    """Represents the possible states of a circuit breaker."""
    CLOSED = auto()  # Normal operation, requests allowed
    OPEN = auto()    # Circuit is open, requests blocked
    HALF_OPEN = auto()  # Trial period to check if service has recovered


@dataclass
class CircuitBreakerMetrics:
    """Tracks metrics for the circuit breaker."""
    failures: int = 0
    successes: int = 0
    total_requests: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_failures: int = 0
    consecutive_successes: int = 0


class CircuitBreakerError(Exception):
    """Raised when the circuit breaker is open and blocks a request."""
    def __init__(self, circuit_name: str, state: CircuitState):
        self.circuit_name = circuit_name
        self.state = state
        super().__init__(f"Circuit '{circuit_name}' is {state.name}")


class CircuitBreaker:
    """
    Implements the circuit breaker pattern to prevent cascading failures.
    
    The circuit breaker monitors for failures and opens the circuit when the 
    failure rate exceeds a threshold, preventing further requests to the failing
    service and giving it time to recover.
    """
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 30.0,
        success_threshold: int = 3,
        excluded_exceptions: Optional[tuple] = None,
        on_state_change: Optional[Callable[[str, CircuitState], None]] = None
    ):
        """
        Initialize the circuit breaker.
        
        Args:
            name: Name of the circuit breaker
            failure_threshold: Number of failures before opening the circuit
            recovery_timeout: Time in seconds before attempting to close the circuit
            success_threshold: Number of successful requests required to close the circuit
            excluded_exceptions: Exceptions that shouldn't be counted as failures
            on_state_change: Callback when the circuit state changes
        """
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.excluded_exceptions = tuple(excluded_exceptions) if excluded_exceptions else ()
        self.on_state_change = on_state_change
        
        self._state = CircuitState.CLOSED
        self._metrics = CircuitBreakerMetrics()
        self._last_state_change = time.time()
        self._lock = asyncio.Lock()
    
    @property
    def state(self) -> CircuitState:
        """Get the current state of the circuit breaker."""
        return self._state
    
    @property
    def is_closed(self) -> bool:
        """Check if the circuit is closed (normal operation)."""
        return self._state == CircuitState.CLOSED
    
    @property
    def is_open(self) -> bool:
        """Check if the circuit is open (blocking requests)."""
        return self._state == CircuitState.OPEN
    
    @property
    def is_half_open(self) -> bool:
        """Check if the circuit is half-open (trial period)."""
        return self._state == CircuitState.HALF_OPEN
    
    @property
    def metrics(self) -> CircuitBreakerMetrics:
        """Get a copy of the current metrics."""
        return CircuitBreakerMetrics(
            failures=self._metrics.failures,
            successes=self._metrics.successes,
            total_requests=self._metrics.total_requests,
            last_failure_time=self._metrics.last_failure_time,
            last_success_time=self._metrics.last_success_time,
            consecutive_failures=self._metrics.consecutive_failures,
            consecutive_successes=self._metrics.consecutive_successes
        )
    
    def _change_state(self, new_state: CircuitState) -> None:
        """Change the state of the circuit breaker."""
        if self._state != new_state:
            old_state = self._state
            self._state = new_state
            self._last_state_change = time.time()
            
            # Reset appropriate counters
            if new_state == CircuitState.CLOSED:
                self._metrics.consecutive_failures = 0
            elif new_state == CircuitState.OPEN:
                self._metrics.consecutive_successes = 0
            
            # Notify state change
            if self.on_state_change:
                try:
                    self.on_state_change(self.name, new_state)
                except Exception as e:
                    # Don't let callback exceptions break the circuit breaker
                    import logging
                    logging.error(f"Error in state change callback: {e}")
            
            # Log the state change
            logging.info(
                f"Circuit '{self.name}' changed from {old_state.name} to {new_state.name}"
            )
    
    async def _before_call(self) -> bool:
        """
        Called before executing the wrapped function.
        
        Returns:
            bool: True if the call should proceed, False if the circuit is open
        """
        async with self._lock:
            # If circuit is open, check if we should try to recover
            if self._state == CircuitState.OPEN:
                time_since_open = time.time() - self._last_state_change
                if time_since_open >= self.recovery_timeout:
                    self._change_state(CircuitState.HALF_OPEN)
                    return True
                return False
            
            # For half-open state, we allow a limited number of requests
            if self._state == CircuitState.HALF_OPEN:
                # Only allow one request at a time in half-open state
                if self._metrics.consecutive_successes < self.success_threshold:
                    return True
                return False
            
            # Circuit is closed, allow the request
            return True
    
    def _after_call(self, success: bool) -> None:
        """
        Called after executing the wrapped function.
        
        Args:
            success: Whether the call was successful
        """
        async def _update_state():
            async with self._lock:
                self._metrics.total_requests += 1
                
                if success:
                    self._metrics.successes += 1
                    self._metrics.last_success_time = time.time()
                    self._metrics.consecutive_successes += 1
                    self._metrics.consecutive_failures = 0
                    
                    # If we're in half-open state and have enough successes, close the circuit
                    if self._state == CircuitState.HALF_OPEN:
                        if self._metrics.consecutive_successes >= self.success_threshold:
                            self._change_state(CircuitState.CLOSED)
                else:
                    self._metrics.failures += 1
                    self._metrics.last_failure_time = time.time()
                    self._metrics.consecutive_failures += 1
                    self._metrics.consecutive_successes = 0
                    
                    # If we've hit the failure threshold, open the circuit
                    if self._metrics.consecutive_failures >= self.failure_threshold:
                        self._change_state(CircuitState.OPEN)
        
        # Run the update in the background
        asyncio.create_task(_update_state())
    
    async def execute(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: The function to execute
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            The result of the function call
            
        Raises:
            CircuitBreakerError: If the circuit is open
            Exception: Any exception raised by the wrapped function
        """
        # Check if we should allow the request
        should_proceed = await self._before_call()
        if not should_proceed:
            raise CircuitBreakerError(self.name, self._state)
        
        # Execute the function
        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # If we get here, the call was successful
            self._after_call(True)
            return result
            
        except self.excluded_exceptions as e:
            # Don't count excluded exceptions as failures
            self._after_call(True)
            raise
            
        except Exception as e:
            # Count other exceptions as failures
            self._after_call(False)
            raise
    
    def __call__(self, func: Callable[..., T]) -> Callable[..., T]:
        """
        Decorator to apply the circuit breaker to a function.
        
        Example:
            @circuit_breaker
            async def my_function():
                # ...
        """
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            return await self.execute(func, *args, **kwargs)
        
        return cast(Callable[..., T], wrapper)


class CircuitBreakerManager:
    """Manages multiple circuit breakers."""
    
    _instance = None
    _breakers: Dict[str, CircuitBreaker] = {}
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CircuitBreakerManager, cls).__new__(cls)
        return cls._instance
    
    @classmethod
    async def get_breaker(
        cls,
        name: str,
        **kwargs: Any
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker with the given name.
        
        Args:
            name: Name of the circuit breaker
            **kwargs: Additional arguments to pass to the CircuitBreaker constructor
            
        Returns:
            The circuit breaker instance
        """
        async with cls._lock:
            if name not in cls._breakers:
                cls._breakers[name] = CircuitBreaker(name, **kwargs)
            return cls._breakers[name]
    
    @classmethod
    def get_breakers(cls) -> Dict[str, CircuitBreaker]:
        """Get all circuit breakers."""
        return cls._breakers.copy()
    
    @classmethod
    def get_breaker_status(cls) -> Dict[str, Dict[str, Any]]:
        """Get the status of all circuit breakers."""
        return {
            name: {
                'state': breaker.state.name,
                'metrics': {
                    'total_requests': breaker.metrics.total_requests,
                    'failures': breaker.metrics.failures,
                    'successes': breaker.metrics.successes,
                    'failure_rate': (
                        breaker.metrics.failures / breaker.metrics.total_requests 
                        if breaker.metrics.total_requests > 0 else 0.0
                    ),
                    'last_failure': (
                        datetime.fromtimestamp(breaker.metrics.last_failure_time).isoformat() 
                        if breaker.metrics.last_failure_time else None
                    ),
                    'last_success': (
                        datetime.fromtimestamp(breaker.metrics.last_success_time).isoformat() 
                        if breaker.metrics.last_success_time else None
                    ),
                    'consecutive_failures': breaker.metrics.consecutive_failures,
                    'consecutive_successes': breaker.metrics.consecutive_successes
                },
                'config': {
                    'failure_threshold': breaker.failure_threshold,
                    'recovery_timeout': breaker.recovery_timeout,
                    'success_threshold': breaker.success_threshold
                }
            }
            for name, breaker in cls._breakers.items()
        }
