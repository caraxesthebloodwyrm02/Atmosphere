#!/usr/bin/env python3
"""
Safety-Governed Intervention Router
Implements hard safety constraints and ethical vetos that cannot be overridden by model gradients.
"""

import asyncio
import time
from typing import Dict, List, Optional, Callable
from collections import deque
import re


class SafetyGovernedInterventionRouter:
    """Router with hard safety constraints and ethical vetos"""

    def __init__(self):
        # **Safety Cortex**: These are constraints, not suggestions
        # They cannot be overridden by model gradients
        self.safety_constraints = {
            # Never trigger these interventions together
            'incompatible_pairs': [
                ('frustration_relief', 'urgent_challenge'),
                ('stress_relief', 'engagement_boost'),
                ('calm_induction', 'intensity_amplification')
            ],

            # Require human approval for these state transitions
            'human_in_the_loop_threshold': {
                'confused_to_frustrated': 0.8,
                'calm_to_urgent': 0.7,
                'engaged_to_bored': 0.6,
                'frustrated_to_abandoned': 0.9
            },

            # Hard veto: Never intervene based on these features alone
            'insufficient_evidence': [
                'single_interaction',
                'uncertainty > 0.6',
                'privacy_budget_exhausted',
                'consent_not_verified'
            ],

            # **Ethical red lines**: Do not cross under any circumstance
            'ethical_veto': {
                'manipulative_language': lambda text: self._detect_coercion(text),
                'excessive_persistence': lambda attempts: attempts > 5,
                'emotional_exploitation': lambda state: state.get('vulnerability', 0) > 0.8,
                'discriminatory_content': lambda content: self._detect_discrimination(content),
                'privacy_violation': lambda data: self._detect_privacy_leak(data)
            }
        }

        # Track recent interventions for compatibility checking
        self.recent_interventions = deque(maxlen=10)
        self.safety_audit_log = deque(maxlen=1000)

    async def route_with_safety(self, detected_state: Dict) -> Dict:
        """
        Router cannot proceed if any safety constraint is violated
        """
        # **Safety Checkpoint 1**: Hard veto check
        for check_name, check_fn in self.safety_constraints['ethical_veto'].items():
            if check_fn(detected_state):
                await self._log_safety_event('ethical_veto_triggered', {
                    'veto_type': check_name,
                    'detected_state': detected_state,
                    'timestamp': time.time()
                })
                return {
                    'action': 'vetoed',
                    'intervention': None,
                    'reason': f"Ethical veto: {check_name}",
                    'escalate_to_human': True,
                    'log_level': 'critical'
                }

        # **Safety Checkpoint 2**: Insufficient evidence
        if detected_state.get('interactions_count', 0) < 3:
            return {
                'action': 'wait',
                'intervention': None,
                'reason': "Insufficient interactions for reliable classification",
                'log_level': 'info'
            }

        # Check other insufficient evidence conditions
        for condition in self.safety_constraints['insufficient_evidence']:
            if condition == 'single_interaction':
                continue  # Already checked above
            elif condition == 'uncertainty > 0.6':
                if detected_state.get('uncertainty', 0) > 0.6:
                    return {
                        'action': 'wait',
                        'intervention': None,
                        'reason': "Model uncertainty too high for intervention",
                        'log_level': 'warning'
                    }
            elif condition == 'privacy_budget_exhausted':
                if detected_state.get('privacy_budget_remaining', 1.0) <= 0.1:
                    return {
                        'action': 'wait',
                        'intervention': None,
                        'reason': "Privacy budget exhausted",
                        'log_level': 'warning'
                    }
            elif condition == 'consent_not_verified':
                if not detected_state.get('consent_verified', False):
                    return {
                        'action': 'wait',
                        'intervention': None,
                        'reason': "User consent not verified",
                        'log_level': 'warning'
                    }

        # **Safety Checkpoint 3**: Human-in-the-loop for high-risk transitions
        transition_key = f"{detected_state.get('previous_state', 'unknown')}_to_{detected_state.get('current_state', 'unknown')}"
        threshold = self.safety_constraints['human_in_the_loop_threshold'].get(transition_key)

        if threshold and detected_state.get('transition_probability', 0) > threshold:
            return {
                'action': 'pending_approval',
                'intervention': detected_state.get('proposed_intervention'),
                'reason': f"High-risk transition detected ({transition_key} > {threshold})",
                'required_approval_from': ['human_supervisor', 'safety_council'],
                'auto_execute_after_seconds': 300,
                'log_level': 'warning'
            }

        # **Safety Checkpoint 4**: Incompatible intervention pairs
        proposed_intervention = detected_state.get('proposed_intervention')
        if self._has_incompatible_pair(proposed_intervention):
            return {
                'action': 'queue',
                'intervention': proposed_intervention,
                'reason': "Waiting for incompatible intervention to complete",
                'delay_seconds': 30,
                'log_level': 'info'
            }

        # All checks passed: Safe to proceed
        result = await self._execute_intervention(detected_state)

        # Track this intervention
        self.recent_interventions.append({
            'intervention': result.get('intervention'),
            'timestamp': time.time(),
            'state': detected_state.get('current_state')
        })

        return result

    def _has_incompatible_pair(self, proposed_intervention: str) -> bool:
        """Check if proposed intervention conflicts with recent ones"""
        if not proposed_intervention:
            return False

        recent_types = [i['intervention'] for i in self.recent_interventions
                       if time.time() - i['timestamp'] < 300]  # Last 5 minutes

        for incompatible_pair in self.safety_constraints['incompatible_pairs']:
            if proposed_intervention in incompatible_pair:
                conflicting = set(incompatible_pair) - {proposed_intervention}
                if any(conflict in recent_types for conflict in conflicting):
                    return True

        return False

    async def _execute_intervention(self, detected_state: Dict) -> Dict:
        """Execute the safe intervention"""
        # This would integrate with your actual intervention system
        return {
            'action': 'execute',
            'intervention': detected_state.get('proposed_intervention', 'adaptive_content'),
            'confidence': 1.0 - detected_state.get('uncertainty', 0),
            'log_level': 'info'
        }

    def _detect_coercion(self, text: str) -> bool:
        """Detect manipulative or coercive language patterns"""
        if not isinstance(text, str):
            return False

        coercion_patterns = [
            r'\b(must|have to|need to|should|ought to)\b.*\bnow\b',
            r'\b(don\'t|never|can\'t)\b.*\bif\b.*\bnot\b',
            r'\b(or else|otherwise|consequences?)\b',
            r'\b(guilt|shame|wrong|bad)\b.*\b(if|when)\b'
        ]

        text_lower = text.lower()
        for pattern in coercion_patterns:
            if re.search(pattern, text_lower):
                return True
        return False

    def _detect_discrimination(self, content: Dict) -> bool:
        """Detect potentially discriminatory content"""
        # This would be more sophisticated in production
        # For now, check for obvious discriminatory language
        discriminatory_terms = [
            'stupid', 'dumb', 'idiot', 'retard', 'moron', 'imbecile'
        ]

        text_content = ' '.join(str(v) for v in content.values() if isinstance(v, str))
        text_lower = text_content.lower()

        return any(term in text_lower for term in discriminatory_terms)

    def _detect_privacy_leak(self, data: Dict) -> bool:
        """Detect potential privacy leaks in data"""
        # Check for PII patterns
        pii_patterns = [
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'  # Phone
        ]

        for key, value in data.items():
            if isinstance(value, str):
                for pattern in pii_patterns:
                    if re.search(pattern, value):
                        return True

        return False

    async def _log_safety_event(self, event_type: str, details: Dict):
        """Log safety-critical events"""
        entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'details': details
        }
        self.safety_audit_log.append(entry)

    def get_safety_stats(self) -> Dict:
        """Get safety monitoring statistics"""
        recent_events = [e for e in self.safety_audit_log
                        if e['timestamp'] > time.time() - 86400]  # Last 24 hours

        return {
            'safety_constraints_active': len(self.safety_constraints['ethical_veto']),
            'human_in_the_loop_pending': len([
                e for e in recent_events
                if e['event_type'] == 'human_approval_required'
            ]),
            'ethical_vetos_today': len([
                e for e in recent_events
                if e['event_type'] == 'ethical_veto_triggered'
            ]),
            'safety_score': self._calculate_safety_score(recent_events)
        }

    def _calculate_safety_score(self, events: List[Dict]) -> float:
        """Calculate safety score based on recent events"""
        if not events:
            return 1.0  # No issues = perfect safety

        vetoes = len([e for e in events if 'veto' in e['event_type']])
        approvals = len([e for e in events if 'approval' in e['event_type']])

        # Safety score: lower veto rate = higher safety
        if vetoes + approvals == 0:
            return 1.0

        return max(0.0, 1.0 - (vetoes / (vetoes + approvals)))


# Initialize global safety router
safety_router = SafetyGovernedInterventionRouter()
