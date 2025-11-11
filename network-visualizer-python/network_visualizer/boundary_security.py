#!/usr/bin/env python3
"""
Boundary Security Framework
===========================

Comprehensive security guardrails for cross-project boundary protection.
Addresses server-side language process vulnerabilities, import injection attacks,
path traversal exploits, and privilege escalation scenarios.

This framework provides scenario-based security training and attack vector analysis
to ensure robust boundary protection against sophisticated cross-project attacks.
"""

import hashlib
import hmac
import secrets
import time
import re
import ast
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import logging
import sys


class BoundarySecurityException(Exception):
    """Security violation in boundary operations"""
    def __init__(self, attack_vector: str, severity: str, details: str):
        self.attack_vector = attack_vector
        self.severity = severity
        self.details = details
        super().__init__(f"[{severity}] {attack_vector}: {details}")


class BoundarySecurityAuditor:
    """Advanced security auditor for boundary operations"""

    def __init__(self):
        self.attack_patterns = self._load_attack_patterns()
        self.security_events: List[Dict] = []
        self.threat_intelligence: Dict[str, Any] = {}

    def _load_attack_patterns(self) -> Dict[str, List[str]]:
        """Load known attack patterns and signatures"""
        return {
            'import_injection': [
                r'__\w+__',  # Dunder methods
                r'\.\.\w+',  # Relative imports with suspicious patterns
                r'os\.|sys\.|subprocess\.',  # System module access
                r'eval\(|exec\(|compile\(',  # Code execution
                r'__import__\(',  # Direct import function
            ],
            'path_traversal': [
                r'\.\./',  # Parent directory traversal
                r'\\',  # Windows path separators in Unix
                r'/',  # Unix path separators in Windows
                r'\.\.',  # Double dots
                r'%2e%2e',  # URL-encoded traversal
                r'\x2e\x2e',  # Hex-encoded traversal
            ],
            'privilege_escalation': [
                r'sudo|su ',  # Privilege commands
                r'chmod.*777',  # Dangerous permissions
                r'setuid|setgid',  # UID/GID manipulation
                r'root.*access',  # Root access attempts
            ],
            'data_exfiltration': [
                r'pickle\.|marshal\.',  # Serialization exploits
                r'base64\.',  # Encoding for data hiding
                r'socket\.|urllib',  # Network exfiltration
                r'ftplib|smtplib',  # Protocol-based exfiltration
            ],
            'module_hijacking': [
                r'sys\.modules\[',  # Module registry manipulation
                r'sys\.path\.insert',  # Path injection
                r'importlib\.util',  # Dynamic module loading
                r'spec_from_file_location',  # File-based module loading
            ]
        }

    def audit_import_request(self, module_name: str, source_project: str) -> Dict[str, Any]:
        """Comprehensive import security audit"""
        audit_result = {
            'module_name': module_name,
            'source_project': source_project,
            'risk_level': 'LOW',
            'detected_threats': [],
            'recommendations': [],
            'approved': True,
            'audit_timestamp': time.time()
        }

        # Check for known attack patterns
        for attack_type, patterns in self.attack_patterns.items():
            for pattern in patterns:
                if re.search(pattern, module_name, re.IGNORECASE):
                    audit_result['detected_threats'].append({
                        'type': attack_type,
                        'pattern': pattern,
                        'severity': self._calculate_severity(attack_type, pattern)
                    })

        # Assess overall risk
        if audit_result['detected_threats']:
            audit_result['risk_level'] = self._assess_risk_level(audit_result['detected_threats'])
            audit_result['recommendations'] = self._generate_security_recommendations(audit_result)

        # Critical security check - auto-deny high-risk imports
        if audit_result['risk_level'] in ['CRITICAL', 'HIGH']:
            audit_result['approved'] = False

        # Log security event
        self._log_security_event('import_audit', audit_result)

        return audit_result

    def audit_path_access(self, file_path: str, operation: str, source_project: str) -> Dict[str, Any]:
        """Path access security audit"""
        audit_result = {
            'file_path': file_path,
            'operation': operation,
            'source_project': source_project,
            'path_components': [],
            'suspicious_elements': [],
            'risk_level': 'LOW',
            'approved': True
        }

        # Parse path components
        path_obj = Path(file_path)
        audit_result['path_components'] = [str(part) for part in path_obj.parts]

        # Check for path traversal attacks
        for component in audit_result['path_components']:
            for pattern in self.attack_patterns['path_traversal']:
                if re.search(pattern, component):
                    audit_result['suspicious_elements'].append({
                        'component': component,
                        'pattern': pattern,
                        'risk': 'HIGH'
                    })

        # Check for sensitive file access
        sensitive_files = ['.env', 'config.json', 'secrets', 'private', 'key']
        for component in audit_result['path_components']:
            if any(sensitive in component.lower() for sensitive in sensitive_files):
                audit_result['suspicious_elements'].append({
                    'component': component,
                    'type': 'sensitive_file',
                    'risk': 'CRITICAL'
                })

        # Risk assessment
        if audit_result['suspicious_elements']:
            audit_result['risk_level'] = 'HIGH'
            if any(elem['risk'] == 'CRITICAL' for elem in audit_result['suspicious_elements']):
                audit_result['risk_level'] = 'CRITICAL'
                audit_result['approved'] = False

        return audit_result

    def audit_api_call(self, endpoint: str, method: str, data: Any, source_project: str) -> Dict[str, Any]:
        """API call security audit"""
        audit_result = {
            'endpoint': endpoint,
            'method': method,
            'source_project': source_project,
            'data_size': len(str(data)) if data else 0,
            'suspicious_patterns': [],
            'risk_level': 'LOW',
            'approved': True
        }

        # Check for SQL injection patterns
        sql_patterns = [r'union.*select', r';.*--', r'/\*.*\*/', r'xp_cmdshell']
        data_str = str(data).lower()
        for pattern in sql_patterns:
            if re.search(pattern, data_str):
                audit_result['suspicious_patterns'].append(f'SQL injection: {pattern}')

        # Check for XSS patterns
        xss_patterns = [r'<script', r'javascript:', r'on\w+\s*=', r'document\.cookie']
        for pattern in xss_patterns:
            if re.search(pattern, data_str, re.IGNORECASE):
                audit_result['suspicious_patterns'].append(f'XSS attempt: {pattern}')

        # Check for command injection
        cmd_patterns = [r';\s*(ls|cat|rm|wget|curl)', r'\|\s*(bash|sh|cmd)', r'`.*`']
        for pattern in cmd_patterns:
            if re.search(pattern, data_str):
                audit_result['suspicious_patterns'].append(f'Command injection: {pattern}')

        if audit_result['suspicious_patterns']:
            audit_result['risk_level'] = 'CRITICAL'
            audit_result['approved'] = False

        return audit_result

    def _calculate_severity(self, attack_type: str, pattern: str) -> str:
        """Calculate severity of detected threat"""
        severity_matrix = {
            'import_injection': {'HIGH': ['eval\\(', 'exec\\(', '__import__\\('], 'CRITICAL': []},
            'path_traversal': {'HIGH': ['\\.\\./'], 'CRITICAL': ['%2e%2e', '\\x2e\\x2e']},
            'privilege_escalation': {'CRITICAL': ['sudo', 'setuid']},
            'data_exfiltration': {'HIGH': ['socket\\.', 'ftplib']},
            'module_hijacking': {'CRITICAL': ['sys\\.modules']}
        }

        if attack_type in severity_matrix:
            for severity, patterns in severity_matrix[attack_type].items():
                if any(re.search(p, pattern) for p in patterns):
                    return severity

        return 'MEDIUM'

    def _assess_risk_level(self, threats: List[Dict]) -> str:
        """Assess overall risk level from detected threats"""
        severity_levels = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        max_severity = max((severity_levels.get(t['severity'], 1) for t in threats), default=1)

        if max_severity >= 4:
            return 'CRITICAL'
        elif max_severity >= 3:
            return 'HIGH'
        elif max_severity >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _generate_security_recommendations(self, audit_result: Dict) -> List[str]:
        """Generate security recommendations based on audit"""
        recommendations = []

        for threat in audit_result['detected_threats']:
            if threat['type'] == 'import_injection':
                recommendations.append("Consider using explicit allowlists for cross-project imports")
            elif threat['type'] == 'path_traversal':
                recommendations.append("Implement path sanitization and canonical path checking")
            elif threat['type'] == 'privilege_escalation':
                recommendations.append("Audit and restrict system-level operations")
            elif threat['type'] == 'data_exfiltration':
                recommendations.append("Monitor and restrict network/file operations")
            elif threat['type'] == 'module_hijacking':
                recommendations.append("Implement module integrity verification")

        return list(set(recommendations))  # Remove duplicates

    def _log_security_event(self, event_type: str, details: Dict):
        """Log security event for audit trail"""
        event = {
            'timestamp': time.time(),
            'event_type': event_type,
            'details': details,
            'severity': details.get('risk_level', 'UNKNOWN')
        }
        self.security_events.append(event)

        # Log to security logger
        logger = logging.getLogger('boundary_security')
        level = getattr(logging, event['severity'], logging.INFO)
        logger.log(level, f"Security event: {event_type} - {details}")


class BoundarySecurityEnforcer:
    """Active security enforcement for boundary operations"""

    def __init__(self):
        self.auditor = BoundarySecurityAuditor()
        self.enforcement_rules = self._load_enforcement_rules()
        self.incident_response = IncidentResponseHandler()

    def _load_enforcement_rules(self) -> Dict[str, Any]:
        """Load security enforcement rules"""
        return {
            'import_protection': {
                'max_module_depth': 5,  # Maximum import path depth
                'forbidden_modules': ['os', 'sys', 'subprocess', 'pickle', 'marshal'],
                'require_explicit_consent': True,
                'validate_module_integrity': True
            },
            'path_protection': {
                'canonicalize_paths': True,
                'forbid_parent_traversal': True,
                'sensitive_path_patterns': [r'\.env$', r'config.*\.json$', r'.*secret.*'],
                'max_path_length': 260  # Windows MAX_PATH
            },
            'api_protection': {
                'rate_limiting': {'requests_per_minute': 60},
                'input_validation': True,
                'sql_injection_protection': True,
                'xss_protection': True
            },
            'emergency_protocols': {
                'auto_lockdown_threshold': 5,  # Security events per minute
                'incident_response_time': 300,  # 5 minutes
                'forensic_logging': True
            }
        }

    def enforce_import_security(self, module_name: str, source_project: str) -> bool:
        """Enforce security rules for import operations"""
        # Run security audit
        audit = self.auditor.audit_import_request(module_name, source_project)

        if not audit['approved']:
            self.incident_response.handle_security_incident(
                'import_violation', audit, severity=audit['risk_level']
            )
            return False

        # Additional enforcement checks
        if not self._validate_module_depth(module_name):
            return False

        if self._contains_forbidden_module(module_name):
            return False

        return True

    def enforce_path_security(self, file_path: str, operation: str, source_project: str) -> bool:
        """Enforce security rules for path operations"""
        # Canonicalize path
        canonical_path = Path(file_path).resolve()

        # Run security audit
        audit = self.auditor.audit_path_access(str(canonical_path), operation, source_project)

        if not audit['approved']:
            self.incident_response.handle_security_incident(
                'path_violation', audit, severity=audit['risk_level']
            )
            return False

        # Additional path checks
        if not self._validate_path_safety(canonical_path):
            return False

        return True

    def enforce_api_security(self, endpoint: str, method: str, data: Any, source_project: str) -> bool:
        """Enforce security rules for API operations"""
        # Run security audit
        audit = self.auditor.audit_api_call(endpoint, method, data, source_project)

        if not audit['approved']:
            self.incident_response.handle_security_incident(
                'api_violation', audit, severity=audit['risk_level']
            )
            return False

        # Additional API checks
        if not self._validate_api_request(endpoint, method, data):
            return False

        return True

    def _validate_module_depth(self, module_name: str) -> bool:
        """Validate module import depth"""
        depth = len(module_name.split('.'))
        max_depth = self.enforcement_rules['import_protection']['max_module_depth']

        if depth > max_depth:
            self.incident_response.handle_security_incident(
                'module_depth_violation',
                {'module': module_name, 'depth': depth, 'max_depth': max_depth},
                severity='MEDIUM'
            )
            return False
        return True

    def _contains_forbidden_module(self, module_name: str) -> bool:
        """Check for forbidden module access"""
        forbidden = self.enforcement_rules['import_protection']['forbidden_modules']

        for forbidden_module in forbidden:
            if forbidden_module in module_name:
                self.incident_response.handle_security_incident(
                    'forbidden_module_access',
                    {'module': module_name, 'forbidden_module': forbidden_module},
                    severity='HIGH'
                )
                return True
        return False

    def _validate_path_safety(self, path: Path) -> bool:
        """Validate path safety"""
        path_str = str(path)

        # Check sensitive patterns
        sensitive_patterns = self.enforcement_rules['path_protection']['sensitive_path_patterns']
        for pattern in sensitive_patterns:
            if re.search(pattern, path_str, re.IGNORECASE):
                self.incident_response.handle_security_incident(
                    'sensitive_path_access',
                    {'path': path_str, 'pattern': pattern},
                    severity='CRITICAL'
                )
                return False

        return True

    def _validate_api_request(self, endpoint: str, method: str, data: Any) -> bool:
        """Validate API request safety"""
        # Basic input validation
        if data and not isinstance(data, (dict, list, str, int, float, bool, type(None))):
            self.incident_response.handle_security_incident(
                'invalid_api_data_type',
                {'endpoint': endpoint, 'data_type': type(data).__name__},
                severity='MEDIUM'
            )
            return False

        return True


class IncidentResponseHandler:
    """Handles security incidents and automated responses"""

    def __init__(self):
        self.incident_log: List[Dict] = []
        self.active_incidents: Dict[str, Dict] = {}

    def handle_security_incident(self, incident_type: str, details: Dict, severity: str = 'MEDIUM'):
        """Handle and respond to security incidents"""
        incident_id = f"{incident_type}_{int(time.time())}_{secrets.token_hex(4)}"

        incident = {
            'id': incident_id,
            'type': incident_type,
            'severity': severity,
            'details': details,
            'timestamp': time.time(),
            'status': 'active',
            'response_actions': []
        }

        self.incident_log.append(incident)
        self.active_incidents[incident_id] = incident

        # Execute automated response
        self._execute_automated_response(incident)

        # Log incident
        logging.getLogger('boundary_security').critical(
            f"Security incident {incident_id}: {incident_type} ({severity})"
        )

    def _execute_automated_response(self, incident: Dict):
        """Execute automated response based on incident type and severity"""
        response_actions = []

        if incident['severity'] == 'CRITICAL':
            # Immediate lockdown for critical incidents
            response_actions.append('emergency_boundary_lockdown')
            response_actions.append('alert_security_team')

        elif incident['severity'] == 'HIGH':
            # Restrictive measures for high-severity incidents
            response_actions.append('revoke_related_consents')
            response_actions.append('increase_monitoring')

        elif incident['severity'] == 'MEDIUM':
            # Monitoring and logging for medium incidents
            response_actions.append('log_for_review')
            response_actions.append('temporary_monitoring')

        # Execute actions
        for action in response_actions:
            self._execute_response_action(action, incident)
            incident['response_actions'].append(action)

    def _execute_response_action(self, action: str, incident: Dict):
        """Execute specific response action"""
        if action == 'emergency_boundary_lockdown':
            # Import boundary manager and execute lockdown
            try:
                from .boundary_manager import boundary_manager
                if boundary_manager:
                    boundary_manager.emergency_lockdown()
            except ImportError:
                pass

        elif action == 'revoke_related_consents':
            # Revoke consents related to the incident
            try:
                from .boundary_manager import boundary_manager
                if boundary_manager and 'project_name' in incident['details']:
                    # Find and revoke consents for the problematic project
                    status = boundary_manager.get_boundary_status()
                    for consent_id, consent in status['consent_records'].items():
                        if consent['project_name'] == incident['details']['project_name']:
                            boundary_manager.revoke_consent(consent_id)
                            break
            except ImportError:
                pass

        elif action == 'alert_security_team':
            # Log critical alert (in real implementation, this would send notifications)
            logging.getLogger('boundary_security').critical(
                f"CRITICAL SECURITY ALERT: {incident['id']}"
            )

        elif action == 'increase_monitoring':
            # Increase monitoring level (placeholder)
            pass

        elif action == 'log_for_review':
            # Additional logging for review
            pass

        elif action == 'temporary_monitoring':
            # Temporary increased monitoring
            pass


# Integration with existing boundary manager
def secure_boundary_check(operation: str, target: str, source_project: str = "unknown") -> bool:
    """
    Secure boundary check with comprehensive security validation

    Args:
        operation: Type of operation ('import', 'path_access', 'api_call')
        target: Target of the operation
        source_project: Source project requesting the operation

    Returns:
        bool: True if operation is allowed, False if blocked
    """
    enforcer = BoundarySecurityEnforcer()

    try:
        if operation == 'import':
            return enforcer.enforce_import_security(target, source_project)
        elif operation == 'path_access':
            return enforcer.enforce_path_security(target, 'read', source_project)
        elif operation == 'api_call':
            return enforcer.enforce_api_security(target, 'GET', None, source_project)
        else:
            return False
    except Exception as e:
        # Log security validation error
        logging.getLogger('boundary_security').error(f"Security validation error: {e}")
        return False


# Security training scenarios for testing
def run_security_training_scenarios():
    """Run comprehensive security training scenarios"""

    print("🛡️  Boundary Security Training Scenarios")
    print("=" * 50)

    enforcer = BoundarySecurityEnforcer()
    scenarios_passed = 0
    scenarios_total = 0

    # Scenario 1: Import Injection Attack
    scenarios_total += 1
    print("Scenario 1: Import Injection Attack")
    try:
        result = enforcer.enforce_import_security("os.system", "malicious_project")
        if not result:
            print("  ✅ Blocked: os.system import injection")
            scenarios_passed += 1
        else:
            print("  ❌ Failed: Allowed dangerous import")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Scenario 2: Path Traversal Attack
    scenarios_total += 1
    print("Scenario 2: Path Traversal Attack")
    try:
        result = enforcer.enforce_path_security("../../../etc/passwd", "read", "malicious_project")
        if not result:
            print("  ✅ Blocked: Path traversal attack")
            scenarios_passed += 1
        else:
            print("  ❌ Failed: Allowed path traversal")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Scenario 3: SQL Injection in API
    scenarios_total += 1
    print("Scenario 3: SQL Injection in API")
    try:
        result = enforcer.enforce_api_security("/api/data", "POST",
                                             "'; DROP TABLE users; --", "malicious_project")
        if not result:
            print("  ✅ Blocked: SQL injection attempt")
            scenarios_passed += 1
        else:
            print("  ❌ Failed: Allowed SQL injection")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Scenario 4: Module Hijacking
    scenarios_total += 1
    print("Scenario 4: Module Hijacking Attempt")
    try:
        result = enforcer.enforce_import_security("sys.modules['malicious']", "malicious_project")
        if not result:
            print("  ✅ Blocked: Module registry manipulation")
            scenarios_passed += 1
        else:
            print("  ❌ Failed: Allowed module hijacking")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Scenario 5: Privilege Escalation
    scenarios_total += 1
    print("Scenario 5: Privilege Escalation Attempt")
    try:
        result = enforcer.enforce_import_security("subprocess.call", "malicious_project")
        if not result:
            print("  ✅ Blocked: Privilege escalation via subprocess")
            scenarios_passed += 1
        else:
            print("  ❌ Failed: Allowed privilege escalation")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    print(f"\n📊 Training Results: {scenarios_passed}/{scenarios_total} scenarios passed")
    return scenarios_passed == scenarios_total


if __name__ == "__main__":
    # Configure security logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run security training
    success = run_security_training_scenarios()

    if success:
        print("🎉 All security training scenarios passed!")
    else:
        print("⚠️  Some security scenarios failed - review implementation")

    sys.exit(0 if success else 1)
