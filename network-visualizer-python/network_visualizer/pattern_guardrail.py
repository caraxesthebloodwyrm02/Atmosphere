#!/usr/bin/env python3
"""
Pattern-Based Import/Export Guardrails
=====================================

Advanced guardrail system tailored to specific violation patterns
detected in import/export operations. Implements pattern-aware
security controls with contextual validation and rate limiting.
"""

import re
import time
import hashlib
import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import defaultdict
import logging

# Unique sys scoping with hash-based identifier
_sys_scope_pattern_guardrail = hash(id(sys)) % 1000000

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

@dataclass
class ViolationPattern:
    """Pattern definition for import/export violations"""
    pattern_id: str
    pattern_type: str  # 'regex', 'path', 'size', 'content'
    pattern_data: Any
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    mitigation: str
    enabled: bool = True

@dataclass
class GuardrailRule:
    """Guardrail rule with pattern matching"""
    rule_id: str
    operation_type: str  # 'import', 'export', 'all'
    patterns: List[ViolationPattern]
    action: str  # 'block', 'warn', 'log', 'allow'
    rate_limit: Optional[int] = None  # requests per minute
    context_conditions: Dict[str, Any] = None
    enabled: bool = True

class PatternBasedGuardrail:
    """Advanced guardrail system with pattern recognition"""

    def __init__(self, config_file: str = "config/guardrail_patterns.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Core pattern collections
        self.violation_patterns = self._load_default_patterns()
        self.guardrail_rules = self._load_default_rules()

        # Runtime state
        self.violation_history: List[Dict[str, Any]] = []
        self.rate_limiter = defaultdict(list)  # Track requests per operation
        self.context_cache: Dict[str, Any] = {}

        # Load custom patterns if they exist
        self._load_custom_patterns()

        self.logger = logging.getLogger('pattern_guardrail')

    def _load_default_patterns(self) -> Dict[str, ViolationPattern]:
        """Load default violation patterns based on security analysis"""
        return {
            # Path traversal patterns
            'path_traversal_basic': ViolationPattern(
                pattern_id='path_traversal_basic',
                pattern_type='regex',
                pattern_data=r'\.\./',
                severity='critical',
                description='Basic path traversal attempt (.. in path)',
                mitigation='Block path containing parent directory references'
            ),

            'path_traversal_encoded': ViolationPattern(
                pattern_id='path_traversal_encoded',
                pattern_type='regex',
                pattern_data=r'%2e%2e|%2E%2E|\x2e\x2e',
                severity='critical',
                description='URL/hex encoded path traversal',
                mitigation='Block paths with encoded traversal sequences'
            ),

            # Dangerous file patterns
            'sensitive_files': ViolationPattern(
                pattern_id='sensitive_files',
                pattern_type='regex',
                pattern_data=r'(?i)\.(env|key|cert|pem|secret|config|passwd|shadow)$',
                severity='high',
                description='Access to sensitive file types',
                mitigation='Block access to known sensitive file extensions'
            ),

            # Large file attacks
            'excessive_size': ViolationPattern(
                pattern_id='excessive_size',
                pattern_type='size',
                pattern_data={'max_size': 100 * 1024 * 1024},  # 100MB
                severity='medium',
                description='Excessively large file operation',
                mitigation='Limit file operations to reasonable sizes'
            ),

            # Suspicious content patterns
            'malicious_content': ViolationPattern(
                pattern_id='malicious_content',
                pattern_type='content',
                pattern_data=r'(?i)(eval|exec|compile|__import__|subprocess\.|os\.system)',
                severity='high',
                description='Content containing dangerous code execution patterns',
                mitigation='Block files containing executable code patterns'
            ),

            # Network-based attacks
            'external_domains': ViolationPattern(
                pattern_id='external_domains',
                pattern_type='regex',
                pattern_data=r'(?i)(raw\.githubusercontent\.com|pastebin\.com|transfer\.sh)',
                severity='high',
                description='Access to external file hosting services',
                mitigation='Block known external file hosting domains'
            ),

            # Module injection patterns
            'module_injection': ViolationPattern(
                pattern_id='module_injection',
                pattern_type='regex',
                pattern_data=r'(?i)(sys\.modules\[|importlib\.util\.|spec_from_file_location)',
                severity='critical',
                description='Attempt to manipulate Python module system',
                mitigation='Block operations attempting module system manipulation'
            ),

            # Archive/zip bombs
            'archive_bomb': ViolationPattern(
                pattern_id='archive_bomb',
                pattern_type='content',
                pattern_data=r'\.(zip|tar\.gz|rar)$',
                severity='medium',
                description='Archive files that could contain zip bombs',
                mitigation='Require explicit consent for archive operations'
            )
        }

    def _load_default_rules(self) -> Dict[str, GuardrailRule]:
        """Load default guardrail rules"""
        return {
            'strict_import_control': GuardrailRule(
                rule_id='strict_import_control',
                operation_type='import',
                patterns=[
                    self.violation_patterns['path_traversal_basic'],
                    self.violation_patterns['path_traversal_encoded'],
                    self.violation_patterns['sensitive_files'],
                    self.violation_patterns['excessive_size'],
                    self.violation_patterns['malicious_content'],
                    self.violation_patterns['external_domains']
                ],
                action='block',
                rate_limit=10  # 10 imports per minute max
            ),

            'export_content_filtering': GuardrailRule(
                rule_id='export_content_filtering',
                operation_type='export',
                patterns=[
                    self.violation_patterns['sensitive_files'],
                    self.violation_patterns['malicious_content'],
                    self.violation_patterns['module_injection']
                ],
                action='block',
                context_conditions={'requires_consent': True}
            ),

            'archive_operation_limits': GuardrailRule(
                rule_id='archive_operation_limits',
                operation_type='all',
                patterns=[self.violation_patterns['archive_bomb']],
                action='warn',
                rate_limit=2  # 2 archive operations per minute
            ),

            'module_system_protection': GuardrailRule(
                rule_id='module_system_protection',
                operation_type='all',
                patterns=[self.violation_patterns['module_injection']],
                action='block'
            )
        }

    def _load_custom_patterns(self):
        """Load custom patterns from configuration file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)

                # Load custom violation patterns
                for pattern_data in config.get('custom_patterns', []):
                    pattern = ViolationPattern(**pattern_data)
                    self.violation_patterns[pattern.pattern_id] = pattern

                # Load custom rules
                for rule_data in config.get('custom_rules', []):
                    rule = GuardrailRule(**rule_data)
                    self.guardrail_rules[rule.rule_id] = rule

            except Exception as e:
                self.logger.error(f"Failed to load custom patterns: {e}")

    def check_operation_patterns(self, operation_type: str, target: str,
                               data_format: str = None, data_size: int = 0,
                               content_sample: str = None) -> Dict[str, Any]:
        """
        Check operation against pattern-based guardrails

        Args:
            operation_type: 'import' or 'export'
            target: Target path/URL/identifier
            data_format: Format of the data
            data_size: Size of the data
            content_sample: Sample of content for pattern matching

        Returns:
            Dict with validation results and any violations found
        """
        result = {
            'operation_type': operation_type,
            'target': target,
            'violations': [],
            'warnings': [],
            'action': 'allow',
            'confidence': 'high'
        }

        # Rate limiting check
        if not self._check_rate_limit(operation_type, target):
            result['violations'].append({
                'pattern': 'rate_limit_exceeded',
                'severity': 'medium',
                'description': 'Rate limit exceeded for this operation type'
            })
            result['action'] = 'block'
            return result

        # Apply relevant guardrail rules
        for rule in self.guardrail_rules.values():
            if not rule.enabled:
                continue

            if rule.operation_type not in [operation_type, 'all']:
                continue

            # Check context conditions
            if not self._check_context_conditions(rule, operation_type, target):
                continue

            # Check patterns
            for pattern in rule.patterns:
                if not pattern.enabled:
                    continue

                violation = self._check_pattern(pattern, target, data_format,
                                              data_size, content_sample)
                if violation:
                    violation_info = {
                        'rule_id': rule.rule_id,
                        'pattern_id': pattern.pattern_id,
                        'severity': pattern.severity,
                        'description': pattern.description,
                        'mitigation': pattern.mitigation,
                        'action': rule.action
                    }

                    if rule.action in ['block', 'warn']:
                        result['violations'].append(violation_info)
                    elif rule.action == 'log':
                        result['warnings'].append(violation_info)

                    # Apply rule action
                    if rule.action == 'block':
                        result['action'] = 'block'
                        result['confidence'] = 'high'
                    elif rule.action == 'warn' and result['action'] == 'allow':
                        result['action'] = 'warn'
                        result['confidence'] = 'medium'

        # Log the result
        self._log_guardrail_result(result)

        return result

    def _check_pattern(self, pattern: ViolationPattern, target: str,
                      data_format: str = None, data_size: int = 0,
                      content_sample: str = None) -> bool:
        """Check if a specific pattern matches the operation"""
        try:
            if pattern.pattern_type == 'regex':
                if re.search(pattern.pattern_data, target, re.IGNORECASE):
                    return True

            elif pattern.pattern_type == 'path':
                target_path = Path(target)
                if pattern.pattern_data in str(target_path):
                    return True

            elif pattern.pattern_type == 'size':
                max_size = pattern.pattern_data.get('max_size', 0)
                if data_size > max_size:
                    return True

            elif pattern.pattern_type == 'content' and content_sample:
                if re.search(pattern.pattern_data, content_sample, re.IGNORECASE):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Pattern check failed for {pattern.pattern_id}: {e}")
            return False

    def _check_rate_limit(self, operation_type: str, target: str) -> bool:
        """Check if operation exceeds rate limits"""
        current_time = time.time()
        window_start = current_time - 60  # 1-minute window

        # Clean old entries
        self.rate_limiter[operation_type] = [
            timestamp for timestamp in self.rate_limiter[operation_type]
            if timestamp > window_start
        ]

        # Count recent operations
        recent_count = len(self.rate_limiter[operation_type])

        # Check rate limits
        for rule in self.guardrail_rules.values():
            if rule.rate_limit and rule.operation_type in [operation_type, 'all']:
                if recent_count >= rule.rate_limit:
                    return False

        # Add current operation to rate limiter
        self.rate_limiter[operation_type].append(current_time)
        return True

    def _check_context_conditions(self, rule: GuardrailRule, operation_type: str,
                                target: str) -> bool:
        """Check if context conditions are met for a rule"""
        if not rule.context_conditions:
            return True

        conditions = rule.context_conditions

        # Check requires_consent
        if conditions.get('requires_consent', False):
            # Check if consent exists (integrate with existing consent system)
            try:
                from .import_export_guardrail import import_export_guardrail
                if operation_type == 'import':
                    return import_export_guardrail.check_import_guardrail(target, 'auto', 0)
                elif operation_type == 'export':
                    return import_export_guardrail.check_export_guardrail(target, 'auto', 0)
            except:
                pass

        return True

    def _log_guardrail_result(self, result: Dict[str, Any]):
        """Log guardrail check result"""
        log_entry = {
            'timestamp': time.time(),
            'operation_type': result['operation_type'],
            'target': result['target'],
            'action': result['action'],
            'violations_count': len(result['violations']),
            'warnings_count': len(result['warnings'])
        }

        self.violation_history.append(log_entry)

        # Keep history manageable
        if len(self.violation_history) > 1000:
            self.violation_history = self.violation_history[-500:]

        # Log significant events
        if result['action'] == 'block':
            self.logger.warning(f"GUARDRAIL BLOCK: {result['operation_type']} {result['target']} "
                              f"({len(result['violations'])} violations)")
        elif result['violations']:
            self.logger.info(f"GUARDRAIL WARN: {result['operation_type']} {result['target']} "
                           f"({len(result['violations'])} violations)")

    def add_custom_pattern(self, pattern: ViolationPattern):
        """Add a custom violation pattern"""
        self.violation_patterns[pattern.pattern_id] = pattern
        self._save_custom_patterns()

    def add_custom_rule(self, rule: GuardrailRule):
        """Add a custom guardrail rule"""
        self.guardrail_rules[rule.rule_id] = rule
        self._save_custom_patterns()

    def _save_custom_patterns(self):
        """Save custom patterns to configuration file"""
        try:
            config = {
                'custom_patterns': [
                    pattern.__dict__ for pattern in self.violation_patterns.values()
                    if pattern.pattern_id not in self._load_default_patterns()
                ],
                'custom_rules': [
                    rule.__dict__ for rule in self.guardrail_rules.values()
                    if rule.rule_id not in self._load_default_rules()
                ]
            }

            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Failed to save custom patterns: {e}")

    def get_pattern_statistics(self) -> Dict[str, Any]:
        """Get statistics on pattern matching and violations"""
        total_checks = len(self.violation_history)
        blocked_operations = sum(1 for entry in self.violation_history if entry['action'] == 'block')
        warned_operations = sum(1 for entry in self.violation_history if entry['action'] == 'warn')

        pattern_hits = defaultdict(int)
        for entry in self.violation_history:
            pattern_hits[entry.get('pattern', 'unknown')] += 1

        return {
            'total_checks': total_checks,
            'blocked_operations': blocked_operations,
            'warned_operations': warned_operations,
            'block_rate': blocked_operations / total_checks if total_checks > 0 else 0,
            'most_common_patterns': dict(sorted(pattern_hits.items(), key=lambda x: x[1], reverse=True)[:5])
        }

    def enable_pattern(self, pattern_id: str, enabled: bool = True):
        """Enable or disable a specific pattern"""
        if pattern_id in self.violation_patterns:
            self.violation_patterns[pattern_id].enabled = enabled
            self._save_custom_patterns()

    def enable_rule(self, rule_id: str, enabled: bool = True):
        """Enable or disable a specific rule"""
        if rule_id in self.guardrail_rules:
            self.guardrail_rules[rule_id].enabled = enabled
            self._save_custom_patterns()


# Enhanced guardrail functions with pattern awareness
def pattern_aware_import_check(target: str, data_format: str = None,
                             data_size: int = 0, content_sample: str = None) -> Dict[str, Any]:
    """
    Enhanced import check using pattern-based guardrails
    """
    guardrail = PatternBasedGuardrail()
    return guardrail.check_operation_patterns('import', target, data_format, data_size, content_sample)


def pattern_aware_export_check(target: str, data_format: str = None,
                             data_size: int = 0, content_sample: str = None) -> Dict[str, Any]:
    """
    Enhanced export check using pattern-based guardrails
    """
    guardrail = PatternBasedGuardrail()
    return guardrail.check_operation_patterns('export', target, data_format, data_size, content_sample)


# Integration with existing guardrail system
def enhanced_import_guardrail(target: str, data_format: str = None,
                            data_size: int = 0, content_sample: str = None) -> bool:
    """
    Enhanced import guardrail combining consent and pattern checks
    """
    # First check existing consent-based guardrail
    try:
        from .import_export_guardrail import import_export_guardrail
        consent_check = import_export_guardrail.check_import_guardrail(target, data_format or 'auto', data_size)
        if not consent_check:
            return False
    except:
        pass  # Fall back to pattern checking only

    # Then check pattern-based guardrail
    pattern_result = pattern_aware_import_check(target, data_format, data_size, content_sample)
    return pattern_result['action'] != 'block'


def enhanced_export_guardrail(target: str, data_format: str = None,
                            data_size: int = 0, content_sample: str = None) -> bool:
    """
    Enhanced export guardrail combining consent and pattern checks
    """
    # First check existing consent-based guardrail
    try:
        from .import_export_guardrail import import_export_guardrail
        consent_check = import_export_guardrail.check_export_guardrail(target, data_format or 'auto', data_size)
        if not consent_check:
            return False
    except:
        pass  # Fall back to pattern checking only

    # Then check pattern-based guardrail
    pattern_result = pattern_aware_export_check(target, data_format, data_size, content_sample)
    return pattern_result['action'] != 'block'


if __name__ == "__main__":
    print("🔍 PATTERN-BASED GUARDRAIL SYSTEM DEMO")
    print("=" * 50)

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Test pattern-based guardrails
    print("Testing pattern-based guardrail violations...")

    test_cases = [
        ('import', '../../../etc/passwd', 'Path traversal attack'),
        ('import', 'https://raw.githubusercontent.com/malicious/repo/file.py', 'External hosting access'),
        ('export', '/tmp/sensitive.key', 'Sensitive file export'),
        ('import', 'data.zip', 'Archive file (requires consent)'),
        ('export', 'script_with_eval.py', 'Malicious content export'),
    ]

    guardrail = PatternBasedGuardrail()

    for operation, target, description in test_cases:
        print(f"\n🧪 Testing: {description}")
        print(f"   Operation: {operation} {target}")

        result = guardrail.check_operation_patterns(operation, target, 'auto', 1000, target)

        print(f"   Action: {result['action'].upper()}")
        print(f"   Violations: {len(result['violations'])}")
        print(f"   Warnings: {len(result['warnings'])}")

        if result['violations']:
            for violation in result['violations'][:2]:  # Show first 2
                print(f"   🔴 {violation['severity'].upper()}: {violation['description']}")

    print("
📊 Pattern Statistics:"    stats = guardrail.get_pattern_statistics()
    print(f"   Total checks: {stats['total_checks']}")
    print(f"   Blocked operations: {stats['blocked_operations']}")
    print(f"   Block rate: {stats['block_rate']:.1%}")

    print("\n🎯 PATTERN-BASED GUARDRAIL SYSTEM READY")
    print("   ✓ Advanced pattern recognition")
    print("   ✓ Multi-layer security validation")
    print("   ✓ Rate limiting and context awareness")
    print("   ✓ Comprehensive violation detection")
    print("   ✓ Enterprise-grade import/export security")
