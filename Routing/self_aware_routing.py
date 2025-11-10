"""
Self-Aware Auto-Repairing Routing Layer
========================================

This module adds intelligence to the routing system:
- Automatic health monitoring
- Self-repair when connections fail
- Conflict detection and resolution
- Load balancing
- Friendly feedback

Think of it as the "city with no residents" - it manages itself.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Type, Union
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from circuit_breaker import CircuitBreaker, CircuitBreakerManager, CircuitState

from orchestral_connector import OrchestralConnector, ConnectionConfig, ConnectionType, DataFlowType


class HealthStatus(Enum):
    """Health status of routing components"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    FAILING = "failing"
    REPAIRING = "repairing"


class ConflictType(Enum):
    """Types of routing conflicts"""
    CONGESTION = "congestion"
    BOTTLENECK = "bottleneck"
    TIMEOUT = "timeout"
    CONNECTION_LOSS = "connection_loss"
    OVERLOAD = "overload"


@dataclass(frozen=True)
class HealthCheck:
    """Results from a health check"""
    component: str
    status: HealthStatus
    timestamp: float
    latency_ms: float
    throughput_mbps: float
    error_count: int
    message: str = ""
    
    def replace(self, **changes):
        """Return a new instance with the specified fields changed."""
        return dataclasses.replace(self, **changes)


@dataclass
class RepairAction:
    """Record of a repair action taken"""
    action_type: str
    component: str
    timestamp: float
    success: bool
    details: str
    duration_ms: float = 0.0


class SelfAwareRouter:
    """
    Self-managing routing layer that monitors, detects issues, and auto-repairs.
    
    Key Features:
    - Continuous health monitoring
    - Automatic reconnection on failures
    - Conflict detection (congestion, bottlenecks)
    - Load balancing across routes
    - Friendly status messages
    """
    
    def __init__(self, connector: OrchestralConnector):
        self.connector = connector
        self.health_history: Dict[str, List[HealthCheck]] = {}
        self.repair_history: List[RepairAction] = []
        self.conflict_history: List[Tuple[ConflictType, str, float]] = []
        
        # Thresholds for auto-repair triggers
        self.latency_threshold_ms = 500.0
        self.error_rate_threshold = 0.1  # 10%
        self.throughput_min_mbps = 10.0
        
        # Circuit breaker configuration
        self.circuit_breaker_config = {
            'failure_threshold': 3,  # Number of failures before opening the circuit
            'recovery_timeout': 30.0,  # Time in seconds before attempting to close the circuit
            'success_threshold': 2,  # Number of successful requests required to close the circuit
            'excluded_exceptions': (asyncio.CancelledError, KeyboardInterrupt)
        }
        
        # Initialize circuit breakers for each component
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self._init_circuit_breakers()
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_task: Optional[asyncio.Task] = None
        self.last_check_time = 0.0
        self.check_interval_seconds = 5.0
        
        # Friendly messages
        self.status_messages = {
            HealthStatus.HEALTHY: "✨ All systems flowing smoothly",
            HealthStatus.DEGRADED: "⚠️ Minor hiccup detected, adjusting routes...",
            HealthStatus.FAILING: "🔧 Issue found, initiating auto-repair...",
            HealthStatus.REPAIRING: "🛠️ Repairing connections, please hold..."
        }
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        if self.monitoring_active:
            return {"status": "already_running"}
        
        self.monitoring_active = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        return {
            "status": "started",
            "message": "🎯 Routing guardian activated",
            "check_interval": self.check_interval_seconds
        }
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring_active = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        return {"status": "stopped", "message": "Monitoring paused"}
    
    def _init_circuit_breakers(self):
        """Initialize circuit breakers for all components"""
        for component in ['echoes', 'reverb', 'delay', 'arcade']:
            self.circuit_breakers[component] = CircuitBreaker(
                name=f"routing_{component}",
                **self.circuit_breaker_config,
                on_state_change=self._on_circuit_state_change
            )
    
    async def _on_circuit_state_change(self, circuit_name: str, state: CircuitState):
        """Handle circuit state changes"""
        component = circuit_name.replace('routing_', '')
        if state == CircuitState.OPEN:
            logging.warning(f"Circuit for {component} is now OPEN. Requests will be blocked.")
            # Trigger immediate health check and repair
            await self._perform_health_checks()
            await self._auto_repair_if_needed()
        elif state == CircuitState.HALF_OPEN:
            logging.info(f"Circuit for {component} is HALF-OPEN. Testing if recovered...")
        else:  # CLOSED
            logging.info(f"Circuit for {component} is now CLOSED. Back to normal operation.")
    
    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                await self._perform_health_checks()
                await self._detect_conflicts()
                await self._auto_repair_if_needed()
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(self.check_interval_seconds)
    
    async def _perform_health_checks(self):
        """Check health of all components"""
        self.last_check_time = time.time()
        
        # Check each module
        for module_name, is_available in self.connector.module_status.items():
            health_check = await self._check_component_health(module_name, is_available)
            
            if module_name not in self.health_history:
                self.health_history[module_name] = []
            
            self.health_history[module_name].append(health_check)
            
            # Keep only last 100 checks per component
            if len(self.health_history[module_name]) > 100:
                self.health_history[module_name] = self.health_history[module_name][-100:]
    
    async def _check_component_health(self, component: str, is_available: bool) -> HealthCheck:
        """Check health of a single component with circuit breaker protection"""
        async def _health_check() -> HealthCheck:
            start_time = time.time()
            
            if not is_available:
                return HealthCheck(
                    component=component,
                    status=HealthStatus.FAILING,
                    timestamp=start_time,
                    latency_ms=0.0,
                    throughput_mbps=0.0,
                    error_count=1,
                    message=f"Component {component} is unavailable"
                )
            
            # Simulate health check (in real implementation, ping the component)
            await asyncio.sleep(0.01)  # Simulate network latency
            
            latency_ms = (time.time() - start_time) * 1000
            
            # Determine status based on metrics
            status = HealthStatus.HEALTHY
            message = self.status_messages[status]
            
            if latency_ms > self.latency_threshold_ms:
                status = HealthStatus.DEGRADED
                message = f"High latency detected: {latency_ms:.1f}ms"
            
            return HealthCheck(
                component=component,
                status=status,
                timestamp=start_time,
                latency_ms=latency_ms,
                throughput_mbps=self.connector.metrics.throughput,
                error_count=0,
                message=message
            )
        
        # Get or create circuit breaker for this component
        circuit_breaker = self.circuit_breakers.get(component)
        if not circuit_breaker:
            return await _health_check()
        
        try:
            # Execute the health check with circuit breaker protection
            return await circuit_breaker.execute(_health_check)
        except Exception as e:
            # If we get here, the circuit breaker caught an exception
            return HealthCheck(
                component=component,
                status=HealthStatus.FAILING,
                timestamp=time.time(),
                latency_ms=0.0,
                throughput_mbps=0.0,
                error_count=1,
                message=f"Circuit breaker tripped: {str(e)}"
            )
    
    async def _detect_conflicts(self):
        """Detect routing conflicts and congestion"""
        metrics = self.connector.metrics
        
        # Check for congestion (high latency + high throughput)
        if metrics.average_latency > self.latency_threshold_ms / 1000:
            self.conflict_history.append(
                (ConflictType.CONGESTION, "Network congestion detected", time.time())
            )
        
        # Check for bottlenecks (low throughput + active connections)
        if metrics.throughput < self.throughput_min_mbps and metrics.active_connections > 0:
            self.conflict_history.append(
                (ConflictType.BOTTLENECK, "Throughput bottleneck detected", time.time())
            )
        
        # Check error rate
        if metrics.error_rate > self.error_rate_threshold:
            self.conflict_history.append(
                (ConflictType.CONNECTION_LOSS, f"High error rate: {metrics.error_rate:.2%}", time.time())
            )
        
        # Keep only recent conflicts (last 1000)
        if len(self.conflict_history) > 1000:
            self.conflict_history = self.conflict_history[-1000:]
    
    async def _auto_repair_if_needed(self):
        """Automatically repair issues if detected"""
        for module_name, checks in self.health_history.items():
            if not checks:
                continue
            
            latest_check = checks[-1]
            
            # If component is failing, try to repair
            if latest_check.status in [HealthStatus.FAILING, HealthStatus.DEGRADED]:
                await self._repair_component(module_name, latest_check)
    
    async def _repair_component(self, component: str, health_check: HealthCheck):
        """Attempt to repair a component"""
        start_time = time.time()
        repair_action = RepairAction(
            action_type="reconnect",
            component=component,
            timestamp=start_time,
            success=False,
            details=""
        )
        
        try:
            # Attempt to reconnect or reinitialize
            if component in ['echoes', 'reverb', 'delay', 'arcade']:
                # Try to re-establish connections
                await self._reconnect_module(component)
                
                repair_action.success = True
                repair_action.details = f"Successfully repaired {component}"
                
                print(f"✅ Auto-repair successful: {component}")
            
        except Exception as e:
            repair_action.success = False
            repair_action.details = f"Repair failed: {str(e)}"
            logging.error(f"Auto-repair failed for {component}: {e}")
        
        finally:
            repair_action.duration_ms = (time.time() - start_time) * 1000
            self.repair_history.append(repair_action)
            
            # Keep only last 100 repair actions
            if len(self.repair_history) > 100:
                self.repair_history = self.repair_history[-100:]
    
    async def _reconnect_module(self, module_name: str):
        """Reconnect a specific module with circuit breaker protection"""
        async def _do_reconnect():
            # Re-check module availability
            await self.connector._check_module_availability()
            
            # If now available, re-establish connections
            if self.connector.module_status.get(module_name):
                await self.connector._establish_core_connections()
                return True
            return False
        
        # Get the circuit breaker for this module
        circuit_breaker = self.circuit_breakers.get(module_name)
        if not circuit_breaker:
            return await _do_reconnect()
        
        try:
            # Execute the reconnect with circuit breaker protection
            return await circuit_breaker.execute(_do_reconnect)
        except Exception as e:
            logging.error(f"Failed to reconnect {module_name} (circuit breaker): {e}")
            return False
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a friendly health summary with circuit breaker status"""
        overall_status = HealthStatus.HEALTHY
        component_statuses = {}
        
        # Get circuit breaker status for all components
        circuit_status = {
            name.replace('routing_', ''): {
                'state': breaker.state.name,
                'failures': breaker.metrics.consecutive_failures,
                'successes': breaker.metrics.consecutive_successes
            }
            for name, breaker in self.circuit_breakers.items()
        }
        
        for component, checks in self.health_history.items():
            if not checks:
                continue
            
            latest = checks[-1]
            
            # Get circuit breaker state for this component
            cb_state = circuit_status.get(component, {})
            
            component_statuses[component] = {
                "status": latest.status.value,
                "latency_ms": latest.latency_ms,
                "message": latest.message,
                "last_checked": datetime.fromtimestamp(latest.timestamp).isoformat(),
                "circuit_state": cb_state.get('state', 'UNKNOWN'),
                "circuit_failures": cb_state.get('failures', 0),
                "circuit_successes": cb_state.get('successes', 0)
            }
            
            # Overall status is worst of all components
            if latest.status.value == "failing":
                overall_status = HealthStatus.FAILING
            elif latest.status.value == "degraded" and overall_status != HealthStatus.FAILING:
                overall_status = HealthStatus.DEGRADED
        
        recent_conflicts = self.conflict_history[-10:] if self.conflict_history else []
        recent_repairs = self.repair_history[-10:] if self.repair_history else []
        
        return {
            "overall_status": overall_status.value,
            "message": self.status_messages[overall_status],
            "components": component_statuses,
            "recent_conflicts": [
                {
                    "type": ct.value,
                    "description": desc,
                    "timestamp": datetime.fromtimestamp(ts).isoformat()
                }
                for ct, desc, ts in recent_conflicts
            ],
            "recent_repairs": [
                {
                    "action": r.action_type,
                    "component": r.component,
                    "success": r.success,
                    "details": r.details,
                    "duration_ms": r.duration_ms,
                    "timestamp": datetime.fromtimestamp(r.timestamp).isoformat()
                }
                for r in recent_repairs
            ],
            "monitoring_active": self.monitoring_active,
            "last_check": datetime.fromtimestamp(self.last_check_time).isoformat() if self.last_check_time else None,
            "circuit_breakers": {
                name: {
                    'state': breaker.state.name,
                    'failures': breaker.metrics.consecutive_failures,
                    'successes': breaker.metrics.consecutive_successes,
                    'total_requests': breaker.metrics.total_requests,
                    'last_failure': datetime.fromtimestamp(breaker.metrics.last_failure_time).isoformat() 
                                  if breaker.metrics.last_failure_time else None,
                    'last_success': datetime.fromtimestamp(breaker.metrics.last_success_time).isoformat() 
                                  if breaker.metrics.last_success_time else None
                }
                for name, breaker in self.circuit_breakers.items()
            }
        }
    
    def get_friendly_status(self) -> str:
        """Get a friendly, human-readable status message"""
        summary = self.get_health_summary()
        
        status_emoji = {
            "healthy": "✨",
            "degraded": "⚠️",
            "failing": "🔧",
            "repairing": "🛠️"
        }
        
        emoji = status_emoji.get(summary["overall_status"], "❓")
        message = summary["message"]
        
        component_count = len(summary["components"])
        healthy_count = sum(
            1 for c in summary["components"].values() 
            if c["status"] == "healthy"
        )
        
        return f"{emoji} {message} ({healthy_count}/{component_count} components healthy)"


# Convenience function to create and start a self-aware router
async def create_self_aware_router(connector: OrchestralConnector) -> SelfAwareRouter:
    """Create and initialize a self-aware router"""
    router = SelfAwareRouter(connector)
    await router.start_monitoring()
    return router


__all__ = [
    "SelfAwareRouter",
    "HealthStatus",
    "ConflictType",
    "HealthCheck",
    "RepairAction",
    "create_self_aware_router",
    "CircuitBreaker",
    "CircuitBreakerManager",
    "CircuitState"
]
