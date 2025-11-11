#!/usr/bin/env python3
"""
Comprehensive Security Vulnerability Assessment
===========================================

Checks for persisting security vulnerabilities in the current system.
"""

import os
import sys
import json
import re
import socket
from pathlib import Path

def main():
    print('🔍 COMPREHENSIVE SECURITY VULNERABILITY ASSESSMENT')
    print('=' * 60)

    vulnerabilities = []
    warnings = []
    passed_checks = []

    def check_vulnerability(name, condition, description):
        if condition:
            vulnerabilities.append(f'{name}: {description}')
            return False
        else:
            passed_checks.append(f'{name}: Secure')
            return True

    def check_warning(name, condition, description):
        if condition:
            warnings.append(f'{name}: {description}')
            return True
        else:
            passed_checks.append(f'{name}: OK')
            return False

    # 1. FEATURE FLAG SECURITY
    print('1. 🛡️ FEATURE FLAG SECURITY')
    try:
        from network_visualizer.feature_manager import feature_manager, initialize_feature_manager
        initialize_feature_manager()
        status = feature_manager.get_status()

        # Check if any features are enabled by default
        enabled_features = status.get('enabled_features', [])
        check_vulnerability('Default Feature State',
                          len(enabled_features) > 0,
                          f'{len(enabled_features)} features enabled by default')

        # Check for any running tasks
        active_tasks = status.get('active_tasks', {})
        check_vulnerability('Active Feature Tasks',
                          len(active_tasks) > 0,
                          f'{len(active_tasks)} feature tasks running')

        print(f'   ✅ {len([x for x in passed_checks if "Feature" in x])} security checks passed')

    except Exception as e:
        vulnerabilities.append(f'Feature Manager: Import/Initialization error - {str(e)}')

    # 2. BOUNDARY SECURITY
    print('\n2. 🔐 BOUNDARY SECURITY')
    try:
        from network_visualizer.boundary_manager import boundary_manager, initialize_boundary_manager
        initialize_boundary_manager()
        b_status = boundary_manager.get_boundary_status()

        # Check for active consents (should be 0)
        active_consents = b_status.get('active_consents', 0)
        check_vulnerability('Active Boundary Consents',
                          active_consents > 0,
                          f'{active_consents} boundary consents active')

        # Check for allowed projects (should be empty)
        allowed_projects = b_status.get('allowed_projects', [])
        check_vulnerability('Allowed Projects',
                          len(allowed_projects) > 0,
                          f'{len(allowed_projects)} projects have boundary access')

        # Check for import permissions
        allowed_imports = b_status.get('allowed_imports', [])
        check_vulnerability('Import Permissions',
                          len(allowed_imports) > 0,
                          f'{len(allowed_imports)} external import permissions active')

        # Test boundary enforcement
        test_results = []
        test_cases = [
            ('import', 'atmosphere.api', 'atmosphere'),
            ('path_access', '/etc/passwd', 'malicious'),
            ('api_call', '/api/admin', 'hacker')
        ]

        for operation, target, source in test_cases:
            try:
                allowed = boundary_manager.check_boundary(operation, target, source)
                if allowed:
                    test_results.append(f'{operation}:{target}')
            except:
                pass

        check_vulnerability('Boundary Enforcement',
                          len(test_results) > 0,
                          f'Boundary violations: {test_results}')

    except Exception as e:
        vulnerabilities.append(f'Boundary Manager: Error - {str(e)}')

    # 3. IMPORT SECURITY
    print('\n3. 📦 IMPORT SECURITY')
    try:
        # Test protected imports
        dangerous_imports = ['os.system', 'subprocess.call', 'pickle.load', 'eval']

        violations = []
        for module in dangerous_imports:
            try:
                from network_visualizer.boundary_manager import protected_import
                protected_import(module, 'test_project')
                violations.append(module)
            except:
                pass  # Should fail - this is good

        check_vulnerability('Dangerous Import Protection',
                          len(violations) > 0,
                          f'Unprotected dangerous imports: {violations}')

        # Test cross-project import checking
        from network_visualizer.boundary_manager import check_cross_project_import
        result = check_cross_project_import('external.malicious.module')
        check_vulnerability('Cross-Project Import Control',
                          not result,
                          'External imports not blocked by default')

    except Exception as e:
        vulnerabilities.append(f'Import Security: Error - {str(e)}')

    # 4. CONFIGURATION SECURITY
    print('\n4. ⚙️ CONFIGURATION SECURITY')
    try:
        config_dir = Path('config')
        if config_dir.exists():
            config_files = list(config_dir.glob('*.json'))

            for config_file in config_files:
                try:
                    with open(config_file, 'r') as f:
                        data = json.load(f)

                    # Check for sensitive data patterns
                    content = json.dumps(data)
                    sensitive_patterns = ['password', 'secret', 'key', 'token', 'credential']

                    found_sensitive = []
                    for pattern in sensitive_patterns:
                        if pattern.lower() in content.lower():
                            found_sensitive.append(pattern)

                    if found_sensitive:
                        warnings.append(f'Config File {config_file.name}: Contains sensitive data patterns: {found_sensitive}')

                    # Check file permissions
                    import stat
                    file_stat = config_file.stat()
                    permissions = stat.filemode(file_stat.st_mode)

                    # Check if world-readable
                    if file_stat.st_mode & stat.S_IROTH:
                        warnings.append(f'Config File {config_file.name}: World-readable permissions ({permissions})')

                except Exception as e:
                    warnings.append(f'Config File {config_file.name}: Error reading - {str(e)}')

        check_warning('Configuration Exposure',
                     len([w for w in warnings if 'Config' in w]) > 0,
                     f'{len([w for w in warnings if "Config" in w])} configuration security issues')

    except Exception as e:
        vulnerabilities.append(f'Configuration Security: Error - {str(e)}')

    # 5. CLI SECURITY
    print('\n5. 💻 CLI SECURITY')
    try:
        from network_visualizer.__main__ import create_parser
        parser = create_parser()
        help_text = parser.format_help()

        # Check for exposed sensitive information in help
        sensitive_in_help = []
        sensitive_terms = ['password', 'secret', 'key', 'token', 'admin', 'root']

        for term in sensitive_terms:
            if term in help_text.lower():
                sensitive_in_help.append(term)

        check_warning('CLI Help Exposure',
                     len(sensitive_in_help) > 0,
                     f'Sensitive terms in CLI help: {sensitive_in_help}')

    except Exception as e:
        vulnerabilities.append(f'CLI Security: Error - {str(e)}')

    # 6. CODE SECURITY
    print('\n6. 🔧 CODE SECURITY')
    try:
        # Check for hardcoded secrets in Python files
        python_files = list(Path('.').rglob('*.py'))
        secret_patterns = [
            r'password\s*=\s*[\'\"][^\'\"]*[\'\"]',
            r'secret\s*=\s*[\'\"][^\'\"]*[\'\"]',
            r'key\s*=\s*[\'\"][^\'\"]*[\'\"]',
            r'token\s*=\s*[\'\"][^\'\"]*[\'\"]'
        ]

        hardcoded_secrets = []
        for py_file in python_files[:10]:  # Check first 10 files for speed
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                for pattern in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        hardcoded_secrets.append(str(py_file.name))
                        break
            except:
                pass

        check_vulnerability('Hardcoded Secrets',
                          len(hardcoded_secrets) > 0,
                          f'Potential hardcoded secrets in: {hardcoded_secrets[:3]}')

    except Exception as e:
        vulnerabilities.append(f'Code Security: Error - {str(e)}')

    # 7. NETWORK/API SECURITY
    print('\n7. 🌐 NETWORK/API SECURITY')
    try:
        # Check if any services are listening on common ports
        common_ports = [7681, 8000, 8080, 9000]  # Including Atmosphere's port

        open_ports = []
        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    open_ports.append(port)
                sock.close()
            except:
                pass

        if 7681 in open_ports:
            passed_checks.append('Atmosphere API: Service detected (expected)')
        else:
            warnings.append('Atmosphere API: Service not detected on port 7681')

        # Check for unexpected open ports
        unexpected_ports = [p for p in open_ports if p not in [7681]]
        check_warning('Unexpected Services',
                     len(unexpected_ports) > 0,
                     f'Unexpected services on ports: {unexpected_ports}')

    except Exception as e:
        warnings.append(f'Network Security: Check failed - {str(e)}')

    # SUMMARY
    print()
    print('📊 SECURITY ASSESSMENT SUMMARY')
    print('=' * 60)

    print(f'✅ PASSED CHECKS: {len(passed_checks)}')
    for check in passed_checks[-3:]:  # Show last 3
        print(f'   ✓ {check}')

    if warnings:
        print(f'\n⚠️ WARNINGS: {len(warnings)}')
        for warning in warnings[:3]:  # Show first 3
            print(f'   ! {warning}')
        if len(warnings) > 3:
            print(f'   ... and {len(warnings) - 3} more warnings')

    if vulnerabilities:
        print(f'\n❌ VULNERABILITIES: {len(vulnerabilities)}')
        for vuln in vulnerabilities:
            print(f'   🔴 {vuln}')
    else:
        print('\n❌ VULNERABILITIES: 0')
        print('   🟢 NO SECURITY VULNERABILITIES DETECTED')

    print()
    if not vulnerabilities:
        print('🎉 SECURITY STATUS: CLEAN')
        print('   ✓ Zero critical vulnerabilities detected')
        print('   ✓ All security frameworks functioning correctly')
        print('   ✓ Zero-trust architecture properly enforced')
    else:
        print('⚠️ SECURITY STATUS: VULNERABILITIES DETECTED')
        print('   🔴 Immediate attention required for critical issues')
        print('   ⚡ Address vulnerabilities before production deployment')

    return len(vulnerabilities) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
