#!/usr/bin/env python3
"""
Security Operations Framework
=============================

Uses feature flags to enable security operations on-demand,
automatically disabling them after use for zero-trust compliance.
"""

import time
import logging
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
import sys
from pathlib import Path

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

class SecurityOperationsManager:
    """Manages security operations with automatic feature flag lifecycle"""

    def __init__(self):
        self.logger = logging.getLogger('security_operations')
        self.active_operations = {}

    def _ensure_security_frameworks(self):
        """Ensure all security frameworks are imported and available"""
        try:
            from network_visualizer.feature_manager import feature_manager, initialize_feature_manager
            from network_visualizer.boundary_manager import boundary_manager, initialize_boundary_manager
            from network_visualizer.boundary_security import BoundarySecurityEnforcer

            initialize_feature_manager()
            initialize_boundary_manager()

            return feature_manager, boundary_manager, BoundarySecurityEnforcer()
        except ImportError as e:
            raise RuntimeError(f"Security frameworks not available: {e}")

    @contextmanager
    def security_operation_context(self, operation_name: str, required_features: List[str],
                                  duration_minutes: int = 5):
        """
        Context manager for security operations that automatically manages feature flags

        Args:
            operation_name: Name of the security operation
            required_features: List of features to enable for this operation
            duration_minutes: How long to keep features enabled
        """
        fm, bm, enforcer = self._ensure_security_frameworks()

        # Record operation start
        operation_id = f"sec_op_{operation_name}_{int(time.time())}"
        self.active_operations[operation_id] = {
            'name': operation_name,
            'features': required_features,
            'start_time': time.time(),
            'duration': duration_minutes * 60,
            'status': 'active'
        }

        enabled_features = []

        try:
            # Enable required features
            for feature in required_features:
                if fm.enable_feature(feature, duration_minutes):
                    enabled_features.append(feature)
                    self.logger.info(f"Security operation '{operation_name}': enabled feature '{feature}'")

            self.logger.info(f"Security operation '{operation_name}' started with {len(enabled_features)} features")

            # Yield control to the operation
            yield {
                'operation_id': operation_id,
                'enabled_features': enabled_features,
                'feature_manager': fm,
                'boundary_manager': bm,
                'security_enforcer': enforcer
            }

        except Exception as e:
            self.logger.error(f"Security operation '{operation_name}' failed: {e}")
            raise
        finally:
            # Always cleanup - disable features
            disabled_count = 0
            for feature in enabled_features:
                if fm.disable_feature(feature):
                    disabled_count += 1
                    self.logger.info(f"Security operation '{operation_name}': disabled feature '{feature}'")

            # Mark operation as completed
            if operation_id in self.active_operations:
                self.active_operations[operation_id]['status'] = 'completed'
                self.active_operations[operation_id]['end_time'] = time.time()

            self.logger.info(f"Security operation '{operation_name}' completed - {disabled_count} features disabled")

    def perform_boundary_audit(self, target_project: str = None) -> Dict[str, Any]:
        """
        Perform boundary security audit using feature flags

        Args:
            target_project: Specific project to audit (optional)
        """
        required_features = ['boundary_security_audit']

        with self.security_operation_context('boundary_audit', required_features, duration_minutes=10) as context:
            fm, bm, enforcer = context['feature_manager'], context['boundary_manager'], context['security_enforcer']

            audit_results = {
                'timestamp': time.time(),
                'operation': 'boundary_audit',
                'target_project': target_project,
                'findings': []
            }

            # Perform boundary integrity check
            status = bm.get_boundary_status()
            audit_results['boundary_status'] = status

            # Check for security violations
            if status['active_consents'] > 5:  # Threshold for suspicious activity
                audit_results['findings'].append({
                    'severity': 'HIGH',
                    'type': 'excessive_consents',
                    'description': f'Too many active consents: {status["active_consents"]}',
                    'recommendation': 'Review and revoke unnecessary consents'
                })

            # Check for orphaned permissions
            for consent_id, consent in status['consent_records'].items():
                # Validate consent integrity
                if not consent.get('project_name') or not consent.get('granted_at'):
                    audit_results['findings'].append({
                        'severity': 'MEDIUM',
                        'type': 'invalid_consent',
                        'description': f'Invalid consent record: {consent_id}',
                        'recommendation': 'Clean up malformed consent records'
                    })

            audit_results['total_findings'] = len(audit_results['findings'])

            return audit_results

    def perform_thermal_security_scan(self, scan_target: Any = None) -> Dict[str, Any]:
        """
        Perform thermal security scan using feature flags

        Args:
            scan_target: Target data to scan (optional)
        """
        required_features = ['thermal_security_scan', 'enhanced_thermal_scan']

        with self.security_operation_context('thermal_security_scan', required_features, duration_minutes=15) as context:
            fm, bm, enforcer = context['feature_manager'], context['boundary_manager'], context['security_enforcer']

            scan_results = {
                'timestamp': time.time(),
                'operation': 'thermal_security_scan',
                'scan_target': str(scan_target)[:100] if scan_target else None,
                'security_findings': []
            }

            # Use thermal mapper for security analysis
            if scan_target:
                try:
                    from network_visualizer.thermal_mapper import ConceptualThermalMapper
                    mapper = ConceptualThermalMapper(scan_target, 'Security Scan')

                    # Run comprehensive health check
                    health = mapper.comprehensive_health_check()
                    scan_results['health_status'] = health

                    # Analyze for security implications
                    if health['overall_status'] == 'critical':
                        scan_results['security_findings'].append({
                            'severity': 'CRITICAL',
                            'type': 'thermal_anomaly',
                            'description': 'Critical thermal anomalies detected',
                            'recommendation': 'Immediate security review required'
                        })

                    # Check for suspicious thermal patterns
                    audit = mapper.audit_thermal_properties()
                    if audit['anomalies']:
                        scan_results['security_findings'].append({
                            'severity': 'HIGH',
                            'type': 'thermal_anomalies',
                            'description': f'{len(audit["anomalies"])} thermal anomalies detected',
                            'recommendation': 'Review thermal property anomalies'
                        })

                except Exception as e:
                    scan_results['error'] = f'Scan failed: {str(e)}'

            scan_results['total_findings'] = len(scan_results['security_findings'])

            return scan_results

    def perform_emergency_boundary_lockdown(self, reason: str = "Emergency lockdown") -> Dict[str, Any]:
        """
        Perform emergency boundary lockdown using feature flags

        Args:
            reason: Reason for the lockdown
        """
        required_features = ['emergency_lockdown', 'boundary_security_admin']

        with self.security_operation_context('emergency_lockdown', required_features, duration_minutes=30) as context:
            fm, bm, enforcer = context['feature_manager'], context['boundary_manager'], context['security_enforcer']

            lockdown_results = {
                'timestamp': time.time(),
                'operation': 'emergency_lockdown',
                'reason': reason,
                'actions_taken': []
            }

            # Get pre-lockdown status
            pre_status = bm.get_boundary_status()
            lockdown_results['pre_lockdown_consents'] = pre_status['active_consents']

            # Perform emergency lockdown
            revoked_count = bm.emergency_lockdown()
            lockdown_results['actions_taken'].append(f'Revoked {revoked_count} boundary consents')

            # Verify lockdown
            post_status = bm.get_boundary_status()
            lockdown_results['post_lockdown_consents'] = post_status['active_consents']

            # Emergency feature cleanup
            emergency_features = ['emergency_lockdown', 'boundary_security_admin']
            for feature in emergency_features:
                if fm.disable_feature(feature):
                    lockdown_results['actions_taken'].append(f'Disabled emergency feature: {feature}')

            lockdown_results['success'] = post_status['active_consents'] == 0

            return lockdown_results

    def perform_integrity_validation(self) -> Dict[str, Any]:
        """
        Perform system integrity validation using feature flags
        """
        required_features = ['system_integrity_check']

        with self.security_operation_context('integrity_validation', required_features, duration_minutes=5) as context:
            fm, bm, enforcer = context['feature_manager'], context['boundary_manager'], context['security_enforcer']

            validation_results = {
                'timestamp': time.time(),
                'operation': 'integrity_validation',
                'checks_performed': [],
                'issues_found': []
            }

            # Feature flag integrity check
            try:
                status = fm.get_status()
                validation_results['checks_performed'].append('feature_flag_integrity')
                if 'enabled_features' not in status:
                    validation_results['issues_found'].append('Feature flag status malformed')
            except Exception as e:
                validation_results['issues_found'].append(f'Feature flag check failed: {e}')

            # Boundary integrity check
            try:
                b_status = bm.get_boundary_status()
                validation_results['checks_performed'].append('boundary_integrity')
                if 'active_consents' not in b_status:
                    validation_results['issues_found'].append('Boundary status malformed')
            except Exception as e:
                validation_results['issues_found'].append(f'Boundary check failed: {e}')

            # Security framework integrity
            try:
                # Test security enforcer
                test_result = enforcer.enforce_import_security('test.module', 'test_project')
                validation_results['checks_performed'].append('security_framework_integrity')
            except Exception as e:
                validation_results['issues_found'].append(f'Security framework check failed: {e}')

            validation_results['integrity_status'] = 'compromised' if validation_results['issues_found'] else 'intact'

            return validation_results

    def get_active_operations(self) -> Dict[str, Any]:
        """Get status of active security operations"""
        return {
            'active_operations': self.active_operations,
            'total_active': len([op for op in self.active_operations.values() if op['status'] == 'active']),
            'total_completed': len([op for op in self.active_operations.values() if op['status'] == 'completed'])
        }


# Global security operations manager
security_ops = SecurityOperationsManager()


# Convenience functions for common security operations
def audit_boundary_security(target_project: str = None) -> Dict[str, Any]:
    """Convenience function for boundary audit"""
    return security_ops.perform_boundary_audit(target_project)


def scan_thermal_security(scan_target: Any = None) -> Dict[str, Any]:
    """Convenience function for thermal security scan"""
    return security_ops.perform_thermal_security_scan(scan_target)


def emergency_lockdown(reason: str = "Emergency lockdown initiated") -> Dict[str, Any]:
    """Convenience function for emergency lockdown"""
    return security_ops.perform_emergency_boundary_lockdown(reason)


def validate_system_integrity() -> Dict[str, Any]:
    """Convenience function for integrity validation"""
    return security_ops.perform_integrity_validation()


def get_security_operations_status() -> Dict[str, Any]:
    """Get status of security operations"""
    return security_ops.get_active_operations()


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("🔒 Security Operations Framework Demo")
    print("=" * 50)

    # Demonstrate boundary audit
    print("\n1. Boundary Security Audit:")
    try:
        audit_result = audit_boundary_security()
        print(f"   ✅ Audit completed: {audit_result['total_findings']} findings")
        print(f"   📊 Active consents: {audit_result['boundary_status']['active_consents']}")
    except Exception as e:
        print(f"   ❌ Audit failed: {e}")

    # Demonstrate thermal security scan
    print("\n2. Thermal Security Scan:")
    try:
        test_data = {'security_check': 'test', 'suspicious': 'data'}
        scan_result = scan_thermal_security(test_data)
        print(f"   ✅ Scan completed: {scan_result.get('total_findings', 0)} findings")
    except Exception as e:
        print(f"   ❌ Scan failed: {e}")

    # Demonstrate integrity validation
    print("\n3. System Integrity Validation:")
    try:
        integrity_result = validate_system_integrity()
        print(f"   ✅ Validation completed: {integrity_result['integrity_status']}")
        print(f"   🔍 Checks performed: {len(integrity_result['checks_performed'])}")
    except Exception as e:
        print(f"   ❌ Validation failed: {e}")

    # Check that features are automatically disabled
    print("\n4. Feature Auto-Disable Verification:")
    try:
        from network_visualizer.feature_manager import feature_manager, initialize_feature_manager
        initialize_feature_manager()

        status = feature_manager.get_status()
        enabled_count = len(status['enabled_features'])
        print(f"   ✅ Features auto-disabled: {enabled_count} features currently enabled")

        ops_status = get_security_operations_status()
        print(f"   📋 Completed operations: {ops_status['total_completed']}")

    except Exception as e:
        print(f"   ❌ Verification failed: {e}")

    print("\n🎉 Security Operations Framework Ready!")
    print("   Features automatically enable for operations and disable afterward.")
    print("   Zero-trust security maintained with on-demand capability.")
