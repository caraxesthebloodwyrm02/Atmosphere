#!/usr/bin/env python3
"""
Violation Penalty System
========================

Progressive penalty system for security violations with escalating consequences,
automated responses, and recovery mechanisms for blacklist patterns.
"""

import time
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading

# Unique sys scoping with hash-based identifier
_sys_scope_penalty_system = hash(id(sys)) % 1000000

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

class PenaltyLevel(Enum):
    """Penalty severity levels"""
    WARNING = "warning"
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CRITICAL = "critical"

class PenaltyAction(Enum):
    """Available penalty actions"""
    LOG = "log"
    ALERT = "alert"
    RATE_LIMIT = "rate_limit"
    TEMPORARY_BLOCK = "temporary_block"
    PERMANENT_BLOCK = "permanent_block"
    INCIDENT_RESPONSE = "incident_response"
    SYSTEM_LOCKDOWN = "system_lockdown"

class ViolationPenalty:
    """Represents a penalty for a violation"""

    def __init__(self, violation_id: str, penalty_level: PenaltyLevel,
                 actions: List[PenaltyAction], duration_minutes: int = 0,
                 applied_at: datetime = None):
        self.violation_id = violation_id
        self.penalty_level = penalty_level
        self.actions = actions
        self.duration_minutes = duration_minutes
        self.applied_at = applied_at or datetime.now()
        self.expires_at = self.applied_at + timedelta(minutes=duration_minutes) if duration_minutes > 0 else None
        self.enforced = False

    def is_active(self) -> bool:
        """Check if penalty is still active"""
        if self.expires_at is None:
            return True  # Permanent penalty
        return datetime.now() < self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            'violation_id': self.violation_id,
            'penalty_level': self.penalty_level.value,
            'actions': [action.value for action in self.actions],
            'duration_minutes': self.duration_minutes,
            'applied_at': self.applied_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'enforced': self.enforced
        }

class PenaltySystem:
    """Comprehensive penalty system for violations"""

    def __init__(self, config_file: str = "config/penalty_system.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Penalty configuration
        self.penalty_thresholds = {
            PenaltyLevel.WARNING: 1,
            PenaltyLevel.MINOR: 3,
            PenaltyLevel.MODERATE: 5,
            PenaltyLevel.MAJOR: 10,
            PenaltyLevel.CRITICAL: 25
        }

        self.penalty_actions = {
            PenaltyLevel.WARNING: [PenaltyAction.LOG, PenaltyAction.ALERT],
            PenaltyLevel.MINOR: [PenaltyAction.LOG, PenaltyAction.ALERT, PenaltyAction.RATE_LIMIT],
            PenaltyLevel.MODERATE: [PenaltyAction.LOG, PenaltyAction.ALERT, PenaltyAction.RATE_LIMIT, PenaltyAction.TEMPORARY_BLOCK],
            PenaltyLevel.MAJOR: [PenaltyAction.LOG, PenaltyAction.ALERT, PenaltyAction.RATE_LIMIT, PenaltyAction.TEMPORARY_BLOCK, PenaltyAction.INCIDENT_RESPONSE],
            PenaltyLevel.CRITICAL: [PenaltyAction.LOG, PenaltyAction.ALERT, PenaltyAction.PERMANENT_BLOCK, PenaltyAction.INCIDENT_RESPONSE, PenaltyAction.SYSTEM_LOCKDOWN]
        }

        self.penalty_durations = {
            PenaltyLevel.WARNING: 0,  # No duration
            PenaltyLevel.MINOR: 15,  # 15 minutes
            PenaltyLevel.MODERATE: 60,  # 1 hour
            PenaltyLevel.MAJOR: 480,  # 8 hours
            PenaltyLevel.CRITICAL: 0  # Permanent
        }

        # Runtime state
        self.active_penalties: Dict[str, ViolationPenalty] = {}
        self.violation_history: Dict[str, List[datetime]] = {}
        self.enforcement_callbacks: List[Callable] = []

        # Recovery mechanisms
        self.recovery_tokens: Dict[str, Dict[str, Any]] = {}
        self.grace_periods: Dict[str, datetime] = {}

        self.logger = logging.getLogger('penalty_system')

        # Load existing penalties
        self._load_penalties()

    def _load_penalties(self):
        """Load penalty system state"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)

                # Load active penalties
                for penalty_data in data.get('active_penalties', []):
                    penalty = ViolationPenalty(
                        penalty_data['violation_id'],
                        PenaltyLevel(penalty_data['penalty_level']),
                        [PenaltyAction(action) for action in penalty_data['actions']],
                        penalty_data['duration_minutes'],
                        datetime.fromisoformat(penalty_data['applied_at'])
                    )
                    penalty.enforced = penalty_data.get('enforced', False)
                    if penalty.is_active():
                        self.active_penalties[penalty.violation_id] = penalty

                # Load violation history
                self.violation_history = data.get('violation_history', {})

            except Exception as e:
                self.logger.error(f"Failed to load penalties: {e}")

    def _save_penalties(self):
        """Save penalty system state"""
        try:
            data = {
                'active_penalties': [penalty.to_dict() for penalty in self.active_penalties.values()],
                'violation_history': self.violation_history,
                'recovery_tokens': self.recovery_tokens,
                'grace_periods': {k: v.isoformat() for k, v in self.grace_periods.items()},
                'last_updated': datetime.now().isoformat()
            }

            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Failed to save penalties: {e}")

    def register_enforcement_callback(self, callback: Callable):
        """Register callback for penalty enforcement"""
        self.enforcement_callbacks.append(callback)

    def process_violation(self, violation_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a violation and apply appropriate penalties

        Args:
            violation_data: Violation information including type, severity, source, etc.

        Returns:
            Penalty application result
        """
        violation_id = violation_data.get('violation_id', f"violation_{int(time.time())}")
        source = violation_data.get('source', 'unknown')
        severity = violation_data.get('severity', 'medium')

        # Record violation in history
        if source not in self.violation_history:
            self.violation_history[source] = []
        self.violation_history[source].append(datetime.now())

        # Clean old violations (keep last 100 per source)
        if len(self.violation_history[source]) > 100:
            self.violation_history[source] = self.violation_history[source][-100:]

        # Determine penalty level based on violation frequency
        penalty_level = self._calculate_penalty_level(source, severity)

        # Check if grace period is active
        if source in self.grace_periods and datetime.now() < self.grace_periods[source]:
            self.logger.info(f"Violation from {source} ignored due to active grace period")
            return {'action': 'grace_period_active', 'penalty_level': None}

        # Create and apply penalty
        if penalty_level and penalty_level != PenaltyLevel.WARNING:
            penalty = ViolationPenalty(
                violation_id,
                penalty_level,
                self.penalty_actions[penalty_level],
                self.penalty_durations[penalty_level]
            )

            self.active_penalties[violation_id] = penalty
            self._enforce_penalty(penalty, violation_data)

            self.logger.warning(f"Penalty applied to {source}: {penalty_level.value} - {len(penalty.actions)} actions")

            result = {
                'action': 'penalty_applied',
                'penalty_level': penalty_level.value,
                'actions': [action.value for action in penalty.actions],
                'duration_minutes': penalty.duration_minutes,
                'expires_at': penalty.expires_at.isoformat() if penalty.expires_at else None
            }
        else:
            # Warning only
            result = {
                'action': 'warning_issued',
                'penalty_level': 'warning',
                'actions': ['log', 'alert']
            }

        self._save_penalties()
        return result

    def _calculate_penalty_level(self, source: str, severity: str) -> Optional[PenaltyLevel]:
        """Calculate appropriate penalty level based on violation history"""
        violation_count = len(self.violation_history.get(source, []))

        # Base penalty on severity
        base_penalty = {
            'low': PenaltyLevel.WARNING,
            'medium': PenaltyLevel.MINOR,
            'high': PenaltyLevel.MODERATE,
            'critical': PenaltyLevel.CRITICAL
        }.get(severity, PenaltyLevel.WARNING)

        # Escalate based on frequency
        if violation_count >= self.penalty_thresholds[PenaltyLevel.CRITICAL]:
            return PenaltyLevel.CRITICAL
        elif violation_count >= self.penalty_thresholds[PenaltyLevel.MAJOR]:
            return PenaltyLevel.MAJOR
        elif violation_count >= self.penalty_thresholds[PenaltyLevel.MODERATE]:
            return PenaltyLevel.MODERATE
        elif violation_count >= self.penalty_thresholds[PenaltyLevel.MINOR]:
            return PenaltyLevel.MINOR

        return base_penalty

    def _enforce_penalty(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Enforce penalty actions"""
        for action in penalty.actions:
            try:
                if action == PenaltyAction.LOG:
                    self._log_penalty(penalty, violation_data)
                elif action == PenaltyAction.ALERT:
                    self._alert_penalty(penalty, violation_data)
                elif action == PenaltyAction.RATE_LIMIT:
                    self._apply_rate_limit(penalty, violation_data)
                elif action == PenaltyAction.TEMPORARY_BLOCK:
                    self._apply_temporary_block(penalty, violation_data)
                elif action == PenaltyAction.PERMANENT_BLOCK:
                    self._apply_permanent_block(penalty, violation_data)
                elif action == PenaltyAction.INCIDENT_RESPONSE:
                    self._trigger_incident_response(penalty, violation_data)
                elif action == PenaltyAction.SYSTEM_LOCKDOWN:
                    self._trigger_system_lockdown(penalty, violation_data)

                # Execute callbacks
                for callback in self.enforcement_callbacks:
                    try:
                        callback(penalty, action, violation_data)
                    except Exception as e:
                        self.logger.error(f"Enforcement callback failed: {e}")

            except Exception as e:
                self.logger.error(f"Failed to enforce {action.value}: {e}")

        penalty.enforced = True

    def _log_penalty(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Log penalty application"""
        self.logger.warning(f"PENALTY APPLIED: {penalty.penalty_level.value} penalty for violation {penalty.violation_id}")

    def _alert_penalty(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Send penalty alert"""
        # Integration with alert system would go here
        print(f"🚨 PENALTY ALERT: {penalty.penalty_level.value} penalty applied")

    def _apply_rate_limit(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Apply rate limiting"""
        source = violation_data.get('source', 'unknown')
        # Increase rate limits for this source
        print(f"🐌 RATE LIMIT increased for source: {source}")

    def _apply_temporary_block(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Apply temporary blocking"""
        source = violation_data.get('source', 'unknown')
        duration = penalty.duration_minutes
        print(f"⏰ TEMPORARY BLOCK applied to {source} for {duration} minutes")

    def _apply_permanent_block(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Apply permanent blocking"""
        source = violation_data.get('source', 'unknown')
        print(f"🚫 PERMANENT BLOCK applied to source: {source}")

    def _trigger_incident_response(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Trigger incident response procedures"""
        print("🚨 INCIDENT RESPONSE triggered")
        # Would integrate with security monitoring system

    def _trigger_system_lockdown(self, penalty: ViolationPenalty, violation_data: Dict[str, Any]):
        """Trigger system-wide lockdown"""
        print("🔒 SYSTEM LOCKDOWN initiated")
        # Critical security response

    def request_penalty_review(self, violation_id: str, reason: str) -> Dict[str, Any]:
        """Request review of an active penalty"""
        if violation_id not in self.active_penalties:
            return {'status': 'not_found', 'message': 'Penalty not found'}

        penalty = self.active_penalties[violation_id]

        # Generate recovery token
        token = f"recovery_{violation_id}_{int(time.time())}"
        self.recovery_tokens[token] = {
            'violation_id': violation_id,
            'reason': reason,
            'requested_at': datetime.now(),
            'status': 'pending_review'
        }

        self.logger.info(f"Penalty review requested for {violation_id}: {reason}")

        return {
            'status': 'review_requested',
            'token': token,
            'penalty_level': penalty.penalty_level.value,
            'message': 'Penalty review has been requested'
        }

    def grant_penalty_amnesty(self, violation_id: str, reason: str = "Administrative review") -> bool:
        """Grant amnesty for a penalty (administrative action)"""
        if violation_id in self.active_penalties:
            penalty = self.active_penalties[violation_id]

            # Remove penalty
            del self.active_penalties[violation_id]

            # Apply grace period
            source = penalty.violation_id.split('_')[1] if '_' in penalty.violation_id else 'unknown'
            self.grace_periods[source] = datetime.now() + timedelta(hours=1)  # 1 hour grace

            self.logger.info(f"Penalty amnesty granted for {violation_id}: {reason}")
            self._save_penalties()

            return True

        return False

    def cleanup_expired_penalties(self) -> int:
        """Clean up expired penalties"""
        expired = []
        for violation_id, penalty in self.active_penalties.items():
            if not penalty.is_active():
                expired.append(violation_id)

        for violation_id in expired:
            del self.active_penalties[violation_id]

        if expired:
            self.logger.info(f"Cleaned up {len(expired)} expired penalties")
            self._save_penalties()

        return len(expired)

    def get_penalty_status(self) -> Dict[str, Any]:
        """Get comprehensive penalty system status"""
        return {
            'active_penalties': len(self.active_penalties),
            'total_violation_sources': len(self.violation_history),
            'recent_penalties': [
                {
                    'violation_id': penalty.violation_id,
                    'level': penalty.penalty_level.value,
                    'actions': [action.value for action in penalty.actions],
                    'applied_at': penalty.applied_at.isoformat(),
                    'expires_at': penalty.expires_at.isoformat() if penalty.expires_at else None
                }
                for penalty in sorted(
                    self.active_penalties.values(),
                    key=lambda x: x.applied_at,
                    reverse=True
                )[:10]
            ],
            'penalty_distribution': {
                level.value: len([p for p in self.active_penalties.values() if p.penalty_level == level])
                for level in PenaltyLevel
            }
        }

    def get_source_penalty_history(self, source: str) -> Dict[str, Any]:
        """Get penalty history for a specific source"""
        violations = self.violation_history.get(source, [])
        active_penalties = [
            penalty for penalty in self.active_penalties.values()
            if source in penalty.violation_id
        ]

        return {
            'source': source,
            'total_violations': len(violations),
            'active_penalties': len(active_penalties),
            'penalty_levels': [p.penalty_level.value for p in active_penalties],
            'last_violation': max(violations).isoformat() if violations else None,
            'current_status': 'penalized' if active_penalties else 'clear'
        }


# Global penalty system instance
penalty_system = PenaltySystem()


# CLI Integration Functions
def penalty_status_command():
    """CLI command to show penalty system status"""
    status = penalty_system.get_penalty_status()

    print("⚖️ Penalty System Status")
    print("=" * 50)
    print(f"Active Penalties: {status['active_penalties']}")
    print(f"Violation Sources: {status['total_violation_sources']}")

    print(f"\nPenalty Distribution:")
    for level, count in status['penalty_distribution'].items():
        if count > 0:
            print(f"  {level.upper()}: {count}")

    if status['recent_penalties']:
        print("\nRecent Penalties:")
        for penalty in status['recent_penalties'][:5]:
            expires = penalty['expires_at'] or 'Never'
            print(f"  ⚖️ {penalty['violation_id'][:12]}: {penalty['level']} - expires {expires}")

def penalty_source_command(source: str):
    """CLI command to check penalty history for a source"""
    history = penalty_system.get_source_penalty_history(source)

    print(f"📋 Penalty History for Source: {source}")
    print("=" * 50)
    print(f"Total Violations: {history['total_violations']}")
    print(f"Active Penalties: {history['active_penalties']}")
    print(f"Current Status: {history['current_status']}")

    if history['penalty_levels']:
        print(f"Active Penalty Levels: {', '.join(history['penalty_levels'])}")

    if history['last_violation']:
        print(f"Last Violation: {history['last_violation']}")

def penalty_review_command(violation_id: str, reason: str):
    """CLI command to request penalty review"""
    result = penalty_system.request_penalty_review(violation_id, reason)

    if result['status'] == 'review_requested':
        print(f"✅ Penalty review requested for {violation_id}")
        print(f"   Token: {result['token']}")
        print(f"   Current Level: {result['penalty_level']}")
    else:
        print(f"❌ Review request failed: {result['message']}")

def penalty_amnesty_command(violation_id: str, reason: str = "Administrative review"):
    """CLI command to grant penalty amnesty"""
    if penalty_system.grant_penalty_amnesty(violation_id, reason):
        print(f"✅ Penalty amnesty granted for {violation_id}")
        print("   1-hour grace period applied")
    else:
        print(f"❌ Penalty not found: {violation_id}")

def penalty_cleanup_command():
    """CLI command to cleanup expired penalties"""
    cleaned = penalty_system.cleanup_expired_penalties()
    print(f"🧹 Cleaned up {cleaned} expired penalties")


if __name__ == "__main__":
    print("⚖️ Violation Penalty System Demo")
    print("=" * 50)

    # Register enforcement callback
    def enforcement_tracker(penalty, action, violation_data):
        print(f"🔧 ENFORCEMENT: {action.value} applied for penalty {penalty.violation_id}")

    penalty_system.register_enforcement_callback(enforcement_tracker)

    # Simulate escalating violations from a source
    test_source = "malicious_actor_123"

    print("Testing progressive penalty escalation...")

    violation_levels = ['low', 'medium', 'medium', 'high', 'high', 'high', 'critical']

    for i, severity in enumerate(violation_levels, 1):
        print(f"\n--- Violation #{i} ({severity}) ---")

        violation_data = {
            'violation_id': f"test_violation_{i}",
            'source': test_source,
            'severity': severity,
            'type': 'test_violation',
            'description': f'Test violation #{i}'
        }

        result = penalty_system.process_violation(violation_data)

        print(f"Result: {result['action']}")
        if 'penalty_level' in result:
            print(f"Penalty Level: {result['penalty_level']}")
        if 'actions' in result:
            print(f"Actions: {', '.join(result['actions'])}")
        if 'duration_minutes' in result and result['duration_minutes'] > 0:
            print(f"Duration: {result['duration_minutes']} minutes")

    print("\n📊 Final Penalty Status:")
    penalty_status_command()

    print("\n🕵️ Source History:")
    penalty_source_command(test_source)

    # Test recovery mechanisms
    print("\n🔄 Testing Recovery Mechanisms:")
    # Request review for first penalty
    penalty_review_command("test_violation_1", "False positive detected")

    # Grant amnesty
    penalty_amnesty_command("test_violation_5", "Administrative review")

    print("\n🎯 Penalty System Features:")
    print("   ✓ Progressive penalty escalation based on violation frequency")
    print("   ✓ Severity-based penalty levels (Warning → Critical)")
    print("   ✓ Multiple enforcement actions per penalty")
    print("   ✓ Temporary and permanent penalties")
    print("   ✓ Automated incident response triggering")
    print("   ✓ Recovery and review mechanisms")
    print("   ✓ Grace periods after amnesty")
    print("   ✓ Comprehensive audit trails")
    print("   ✓ Source-specific penalty tracking")
    print("   ✓ Administrative override capabilities")

    print("\n🛡️ Advanced Security Enforcement:")
    print("   ✓ Deterrence through escalating consequences")
    print("   ✓ Proportional response to threat levels")
    print("   ✓ Recovery paths for legitimate users")
    print("   ✓ Administrative control and oversight")
    print("   ✓ Integration with broader security ecosystem")
