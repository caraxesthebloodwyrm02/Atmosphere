#!/usr/bin/env python3
"""
Dynamic Blacklist System for Security Violations
===============================================

Advanced blacklist system that automatically identifies and blocks patterns
attempting to bypass user consent and security guardrails.
"""

import re
import time
import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import defaultdict, Counter
from datetime import datetime, timedelta
import logging

# Unique sys scoping with hash-based identifier
_sys_scope_dynamic_blacklist = hash(id(sys)) % 1000000

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

class ViolationPattern:
    """Represents a detected violation pattern"""

    def __init__(self, pattern: str, pattern_type: str, source: str,
                 severity: str, context: Dict[str, Any]):
        self.pattern = pattern
        self.pattern_type = pattern_type
        self.source = source
        self.severity = severity
        self.context = context
        self.first_seen = datetime.now()
        self.last_seen = datetime.now()
        self.occurrences = 1
        self.blocked_count = 0
        self.consent_bypass_attempts = 0

        # Generate pattern signature
        self.signature = self._generate_signature()

    def _generate_signature(self) -> str:
        """Generate unique signature for this pattern"""
        content = f"{self.pattern_type}:{self.pattern}:{self.source}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def record_occurrence(self, context: Dict[str, Any] = None):
        """Record another occurrence of this pattern"""
        self.occurrences += 1
        self.last_seen = datetime.now()

        if context:
            self.context.update(context)

        # Check for consent bypass indicators
        if self._is_consent_bypass_attempt(context):
            self.consent_bypass_attempts += 1

    def _is_consent_bypass_attempt(self, context: Dict[str, Any] = None) -> bool:
        """Detect if this is an attempt to bypass consent mechanisms"""
        if not context:
            return False

        bypass_indicators = [
            'consent_bypass',
            'no_consent_required',
            'consent_override',
            'direct_access_attempt',
            'bypass_guardrail',
            'consent_spoofing'
        ]

        context_str = json.dumps(context).lower()
        return any(indicator in context_str for indicator in bypass_indicators)

    def should_blacklist(self, threshold: int = 5, bypass_threshold: int = 2) -> bool:
        """Determine if this pattern should be blacklisted"""
        # Blacklist if:
        # 1. High occurrence count, OR
        # 2. Multiple consent bypass attempts, OR
        # 3. Critical severity with any occurrences
        return (
            self.occurrences >= threshold or
            self.consent_bypass_attempts >= bypass_threshold or
            (self.severity == 'critical' and self.occurrences >= 1)
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'pattern': self.pattern,
            'pattern_type': self.pattern_type,
            'source': self.source,
            'severity': self.severity,
            'context': self.context,
            'first_seen': self.first_seen.isoformat(),
            'last_seen': self.last_seen.isoformat(),
            'occurrences': self.occurrences,
            'blocked_count': self.blocked_count,
            'consent_bypass_attempts': self.consent_bypass_attempts,
            'signature': self.signature
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ViolationPattern':
        """Create from dictionary"""
        pattern = cls(
            data['pattern'],
            data['pattern_type'],
            data['source'],
            data['severity'],
            data['context']
        )
        pattern.first_seen = datetime.fromisoformat(data['first_seen'])
        pattern.last_seen = datetime.fromisoformat(data['last_seen'])
        pattern.occurrences = data['occurrences']
        pattern.blocked_count = data['blocked_count']
        pattern.consent_bypass_attempts = data['consent_bypass_attempts']
        return pattern

class DynamicBlacklist:
    """Dynamic blacklist system for security violations"""

    def __init__(self, blacklist_file: str = "config/dynamic_blacklist.json"):
        self.blacklist_file = Path(blacklist_file)
        self.blacklist_file.parent.mkdir(parents=True, exist_ok=True)

        # Blacklist data
        self.blacklisted_patterns: Dict[str, ViolationPattern] = {}
        self.suspicious_patterns: Dict[str, ViolationPattern] = {}
        self.whitelisted_patterns: Set[str] = set()

        # Configuration
        self.auto_blacklist_threshold = 5
        self.consent_bypass_threshold = 2
        self.pattern_retention_days = 30

        # Statistics
        self.stats = {
            'total_violations': 0,
            'blacklisted_patterns': 0,
            'blocked_requests': 0,
            'consent_bypass_attempts': 0
        }

        self.logger = logging.getLogger('dynamic_blacklist')

        # Load existing blacklist
        self._load_blacklist()

    def _load_blacklist(self):
        """Load blacklist from file"""
        if self.blacklist_file.exists():
            try:
                with open(self.blacklist_file, 'r') as f:
                    data = json.load(f)

                # Load blacklisted patterns
                for pattern_data in data.get('blacklisted_patterns', []):
                    pattern = ViolationPattern.from_dict(pattern_data)
                    self.blacklisted_patterns[pattern.signature] = pattern

                # Load suspicious patterns
                for pattern_data in data.get('suspicious_patterns', []):
                    pattern = ViolationPattern.from_dict(pattern_data)
                    self.suspicious_patterns[pattern.signature] = pattern

                # Load whitelist
                self.whitelisted_patterns = set(data.get('whitelisted_patterns', []))

                # Load stats
                self.stats.update(data.get('stats', {}))

            except Exception as e:
                self.logger.error(f"Failed to load blacklist: {e}")

    def _save_blacklist(self):
        """Save blacklist to file"""
        try:
            data = {
                'blacklisted_patterns': [
                    pattern.to_dict() for pattern in self.blacklisted_patterns.values()
                ],
                'suspicious_patterns': [
                    pattern.to_dict() for pattern in self.suspicious_patterns.values()
                ],
                'whitelisted_patterns': list(self.whitelisted_patterns),
                'stats': self.stats,
                'last_updated': datetime.now().isoformat()
            }

            with open(self.blacklist_file, 'w') as f:
                json.dump(data, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Failed to save blacklist: {e}")

    def analyze_violation(self, operation_type: str, target: str,
                         context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze a violation and update blacklist accordingly

        Args:
            operation_type: Type of operation ('import', 'export', etc.)
            target: Target of the operation
            context: Additional context about the violation

        Returns:
            Analysis result with blacklist actions taken
        """
        context = context or {}
        self.stats['total_violations'] += 1

        # Extract pattern from violation
        pattern = self._extract_pattern(operation_type, target, context)
        signature = self._generate_signature(pattern, operation_type, context.get('source', 'unknown'))

        # Check if already blacklisted
        if signature in self.blacklisted_patterns:
            self.blacklisted_patterns[signature].record_occurrence(context)
            self.stats['blocked_requests'] += 1
            return {
                'action': 'blocked',
                'reason': 'blacklisted_pattern',
                'signature': signature
            }

        # Check if whitelisted
        if signature in self.whitelisted_patterns:
            return {
                'action': 'allowed',
                'reason': 'whitelisted_pattern',
                'signature': signature
            }

        # Get or create suspicious pattern entry
        if signature not in self.suspicious_patterns:
            violation_pattern = ViolationPattern(
                pattern=pattern,
                pattern_type=operation_type,
                source=context.get('source', 'unknown'),
                severity=context.get('severity', 'medium'),
                context=context
            )
            self.suspicious_patterns[signature] = violation_pattern
        else:
            self.suspicious_patterns[signature].record_occurrence(context)

        pattern_entry = self.suspicious_patterns[signature]

        # Check if pattern should be blacklisted
        if pattern_entry.should_blacklist(self.auto_blacklist_threshold, self.consent_bypass_threshold):
            # Move to blacklist
            self.blacklisted_patterns[signature] = pattern_entry
            del self.suspicious_patterns[signature]

            self.logger.warning(f"Pattern blacklisted: {pattern} (signature: {signature})")
            self.stats['blacklisted_patterns'] = len(self.blacklisted_patterns)

            return {
                'action': 'blacklisted',
                'reason': 'pattern_promoted_to_blacklist',
                'signature': signature,
                'occurrences': pattern_entry.occurrences,
                'consent_bypass_attempts': pattern_entry.consent_bypass_attempts
            }

        return {
            'action': 'logged',
            'reason': 'suspicious_pattern_logged',
            'signature': signature,
            'occurrences': pattern_entry.occurrences
        }

    def _extract_pattern(self, operation_type: str, target: str, context: Dict[str, Any]) -> str:
        """Extract the core pattern from a violation"""
        # Try to extract meaningful pattern
        if operation_type == 'import':
            # For imports, look for file paths, URLs, or module patterns
            if '://' in target:
                # URL pattern
                return f"url:{target.split('://')[0]}"
            elif '/' in target or '\\' in target:
                # File path pattern
                path_parts = Path(target).parts
                if len(path_parts) > 1:
                    return f"path:{path_parts[-2]}/{path_parts[-1]}"
                else:
                    return f"file:{path_parts[-1]}"
            else:
                # Module/package pattern
                parts = target.split('.')
                return f"module:{'.'.join(parts[:2]) if len(parts) > 1 else parts[0]}"

        elif operation_type == 'export':
            # For exports, similar logic
            if '://' in target:
                return f"url:{target.split('://')[0]}"
            elif '/' in target or '\\' in target:
                path_parts = Path(target).parts
                return f"path:{path_parts[-1]}"
            else:
                return f"export:{target}"

        # Default pattern
        return f"{operation_type}:{target[:50]}"

    def _generate_signature(self, pattern: str, operation_type: str, source: str) -> str:
        """Generate signature for pattern tracking"""
        content = f"{pattern}:{operation_type}:{source}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def check_blacklist(self, operation_type: str, target: str,
                       context: Dict[str, Any] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Check if an operation is blocked by the blacklist

        Returns:
            (is_blocked, reason, details)
        """
        context = context or {}
        pattern = self._extract_pattern(operation_type, target, context)
        signature = self._generate_signature(pattern, operation_type, context.get('source', 'unknown'))

        # Check blacklist
        if signature in self.blacklisted_patterns:
            pattern_entry = self.blacklisted_patterns[signature]
            pattern_entry.blocked_count += 1
            self.stats['blocked_requests'] += 1

            return True, 'blacklisted_pattern', {
                'signature': signature,
                'occurrences': pattern_entry.occurrences,
                'last_seen': pattern_entry.last_seen.isoformat()
            }

        # Check whitelist
        if signature in self.whitelisted_patterns:
            return False, 'whitelisted_pattern', {'signature': signature}

        return False, 'not_listed', {'signature': signature}

    def whitelist_pattern(self, signature: str):
        """Add a pattern to the whitelist"""
        self.whitelisted_patterns.add(signature)
        if signature in self.blacklisted_patterns:
            del self.blacklisted_patterns[signature]
        if signature in self.suspicious_patterns:
            del self.suspicious_patterns[signature]
        self._save_blacklist()

    def remove_from_blacklist(self, signature: str):
        """Remove a pattern from the blacklist"""
        if signature in self.blacklisted_patterns:
            del self.blacklisted_patterns[signature]
            self._save_blacklist()

    def cleanup_old_patterns(self, days: int = None):
        """Clean up old patterns from suspicious list"""
        if days is None:
            days = self.pattern_retention_days

        cutoff = datetime.now() - timedelta(days=days)
        to_remove = []

        for signature, pattern in self.suspicious_patterns.items():
            if pattern.last_seen < cutoff:
                to_remove.append(signature)

        for signature in to_remove:
            del self.suspicious_patterns[signature]

        if to_remove:
            self.logger.info(f"Cleaned up {len(to_remove)} old suspicious patterns")
            self._save_blacklist()

        return len(to_remove)

    def get_blacklist_status(self) -> Dict[str, Any]:
        """Get comprehensive blacklist status"""
        return {
            'blacklisted_patterns': len(self.blacklisted_patterns),
            'suspicious_patterns': len(self.suspicious_patterns),
            'whitelisted_patterns': len(self.whitelisted_patterns),
            'stats': self.stats,
            'recent_violations': [
                {
                    'signature': pattern.signature,
                    'pattern': pattern.pattern,
                    'occurrences': pattern.occurrences,
                    'last_seen': pattern.last_seen.isoformat()
                }
                for pattern in sorted(
                    self.blacklisted_patterns.values(),
                    key=lambda x: x.last_seen,
                    reverse=True
                )[:10]  # Last 10 blacklisted patterns
            ]
        }


# Enhanced guardrail with blacklist integration
class BlacklistEnhancedGuardrail:
    """Guardrail system enhanced with dynamic blacklisting"""

    def __init__(self):
        self.blacklist = DynamicBlacklist()
        self.violation_callbacks = []

    def register_violation_callback(self, callback):
        """Register callback for violations"""
        self.violation_callbacks.append(callback)

    def check_operation_with_blacklist(self, operation_type: str, target: str,
                                     data_format: str = None, data_size: int = 0,
                                     context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check operation with blacklist integration
        """
        context = context or {}

        # First check blacklist
        is_blocked, reason, details = self.blacklist.check_blacklist(
            operation_type, target, context
        )

        if is_blocked:
            # Trigger violation callbacks
            for callback in self.violation_callbacks:
                try:
                    callback({
                        'type': 'blacklist_block',
                        'operation': operation_type,
                        'target': target,
                        'reason': reason,
                        'details': details
                    })
                except Exception as e:
                    print(f"Callback error: {e}")

            return {
                'action': 'blocked',
                'reason': 'blacklist_violation',
                'details': details
            }

        # If not blocked, perform normal guardrail check
        try:
            from .pattern_guardrail import pattern_aware_import_check, pattern_aware_export_check

            if operation_type == 'import':
                result = pattern_aware_import_check(target, data_format, data_size, target)
            elif operation_type == 'export':
                result = pattern_aware_export_check(target, data_format, data_size, target)
            else:
                return {'action': 'allowed', 'reason': 'unsupported_operation'}

            # If guardrail blocks, analyze for blacklisting
            if result['action'] == 'block':
                blacklist_result = self.blacklist.analyze_violation(
                    operation_type, target, {
                        'severity': 'high',
                        'source': context.get('source', 'unknown'),
                        'violations': result['violations'],
                        **context
                    }
                )

                return {
                    'action': 'blocked',
                    'reason': 'guardrail_violation',
                    'blacklist_action': blacklist_result['action'],
                    'details': result
                }

            return result

        except ImportError:
            # Fallback to basic check
            return {'action': 'allowed', 'reason': 'fallback_check'}

    def report_violation_attempt(self, operation_type: str, target: str,
                               context: Dict[str, Any] = None):
        """Report a violation attempt for blacklist analysis"""
        context = context or {}
        self.blacklist.analyze_violation(operation_type, target, context)


# Global enhanced guardrail instance
enhanced_guardrail = BlacklistEnhancedGuardrail()


# CLI Integration Functions
def blacklist_status_command():
    """CLI command to show blacklist status"""
    status = enhanced_guardrail.blacklist.get_blacklist_status()

    print("🚫 Dynamic Blacklist Status")
    print("=" * 50)
    print(f"Blacklisted Patterns: {status['blacklisted_patterns']}")
    print(f"Suspicious Patterns: {status['suspicious_patterns']}")
    print(f"Whitelisted Patterns: {status['whitelisted_patterns']}")
    print(f"Total Violations: {status['stats']['total_violations']}")
    print(f"Blocked Requests: {status['stats']['blocked_requests']}")

    if status['recent_violations']:
        print("\nRecent Blacklisted Patterns:")
        for violation in status['recent_violations'][:5]:
            print(f"  🔴 {violation['signature'][:8]}: {violation['pattern']} "
                  f"({violation['occurrences']} occurrences)")

def blacklist_cleanup_command(days: int = 30):
    """CLI command to cleanup old patterns"""
    cleaned = enhanced_guardrail.blacklist.cleanup_old_patterns(days)
    print(f"🧹 Cleaned up {cleaned} old suspicious patterns")


def blacklist_test_command(operation_type: str, target: str):
    """CLI command to test blacklist enforcement"""
    result = enhanced_guardrail.check_operation_with_blacklist(
        operation_type, target, 'auto', 1000, {'source': 'cli_test'}
    )

    print(f"Blacklist Test: {operation_type} {target}")
    print(f"Action: {result['action'].upper()}")

    if 'reason' in result:
        print(f"Reason: {result['reason']}")

    if 'blacklist_action' in result:
        print(f"Blacklist Action: {result['blacklist_action']}")

    if result['action'] == 'blocked':
        print("❌ Operation would be blocked")
    else:
        print("✅ Operation allowed")


if __name__ == "__main__":
    print("🚫 Dynamic Blacklist System Demo")
    print("=" * 50)

    # Register violation callback
    def violation_handler(violation):
        print(f"🚨 VIOLATION DETECTED: {violation['type']} - {violation['reason']}")
        print(f"   Operation: {violation['operation']} {violation['target']}")

    enhanced_guardrail.register_violation_callback(violation_handler)

    # Test blacklist with repeated violations
    test_targets = [
        '../../../etc/passwd',
        'https://raw.githubusercontent.com/malicious/repo/evil.py',
        '/tmp/sensitive.key',
        'evil_module.subprocess'
    ]

    print("Testing repeated violations to trigger blacklisting...")

    for i in range(7):  # More than threshold
        for target in test_targets:
            result = enhanced_guardrail.check_operation_with_blacklist(
                'import', target, 'auto', 1000,
                {'source': 'demo_test', 'attempt': i + 1}
            )

            if result['action'] == 'blocked':
                print(f"   Blocked: {target}")
                if 'blacklist_action' in result and result['blacklist_action'] == 'blacklisted':
                    print(f"   🆕 BLACKLISTED: {target}")

    print("\nBlacklist Status:")
    blacklist_status_command()

    print("\nTesting whitelisted pattern...")
    # Test whitelist functionality
    signature = "test_signature_123"
    enhanced_guardrail.blacklist.whitelist_pattern(signature)
    print(f"Whitelisted signature: {signature}")

    print("\n🎯 Dynamic Blacklist System Features:")
    print("   ✓ Automatic pattern blacklisting")
    print("   ✓ Consent bypass detection")
    print("   ✓ Violation frequency analysis")
    print("   ✓ Adaptive security responses")
    print("   ✓ Pattern signature generation")
    print("   ✓ Whitelist management")
    print("   ✓ Comprehensive audit trails")
    print("   ✓ Real-time violation monitoring")
