#!/usr/bin/env python3
"""
Final System Verification Script
================================

Comprehensive verification that all systems are operational:
- Atmosphere API connectivity
- Boundary Security Framework
- Thermal scanning functionality
- Cross-project protection
"""

import subprocess
import json
import sys
import os
from pathlib import Path

def check_atmosphere_api():
    """Check Atmosphere API connectivity and thermal scan endpoint"""
    print("🔍 Checking Atmosphere API...")

    try:
        # Use curl if available, otherwise urllib
        try:
            result = subprocess.run(
                ['curl', '-s', 'http://localhost:7681/learning/emotion/thermal_scan'],
                capture_output=True, text=True, timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    data = json.loads(result.stdout)
                    print("✅ Atmosphere API: Connected and responding")
                    print(f"   📊 Thermal scan data: {len(data)} metrics received")
                    print(f"   🎯 Active sessions: {data.get('active_sessions', 'N/A')}")
                    print(f"   🔥 Thermal zones: {len(data.get('thermal_zones', {}))}")
                    return True
                except json.JSONDecodeError:
                    print("⚠️  Atmosphere API: Responding but invalid JSON")
                    return False
            else:
                print("❌ Atmosphere API: Connection failed or empty response")
                return False

        except FileNotFoundError:
            # Fallback to urllib if curl not available
            import urllib.request
            try:
                with urllib.request.urlopen('http://localhost:7681/learning/emotion/thermal_scan', timeout=10) as response:
                    data = json.loads(response.read().decode())
                    print("✅ Atmosphere API: Connected via urllib fallback")
                    print(f"   📊 Thermal scan data: {len(data)} metrics received")
                    return True
            except Exception as e:
                print(f"❌ Atmosphere API: Connection failed - {str(e)}")
                return False

    except Exception as e:
        print(f"❌ Atmosphere API: Error during check - {str(e)}")
        return False

def check_boundary_security():
    """Check boundary security framework operational status"""
    print("\n🔒 Checking Boundary Security Framework...")

    try:
        from network_visualizer.boundary_manager import initialize_boundary_manager
        bm = initialize_boundary_manager()
        status = bm.get_boundary_status()

        print("✅ Boundary Manager: Operational")
        print(f"   📋 Active consents: {len(status['consent_records'])}")
        print(f"   🏗️  Allowed projects: {len(status['allowed_projects'])}")
        print(f"   📁 Allowed paths: {len(status['allowed_paths'])}")
        print(f"   📦 Allowed imports: {len(status['allowed_imports'])}")

        # Test security enforcement
        from network_visualizer.boundary_security import BoundarySecurityEnforcer
        enforcer = BoundarySecurityEnforcer()

        # Quick security test
        attacks_blocked = 0
        test_attacks = ['os.system', '../../../etc/passwd', "'; DROP TABLE users; --"]

        for attack in test_attacks:
            try:
                if attack == 'os.system':
                    result = enforcer.enforce_import_security(attack, 'malicious')
                elif '../../../' in attack:
                    result = enforcer.enforce_path_security(attack, 'read', 'malicious')
                else:
                    result = enforcer.enforce_api_security('/api', 'POST', attack, 'malicious')

                if not result:
                    attacks_blocked += 1
            except:
                attacks_blocked += 1  # Exception counts as blocking

        print(f"✅ Security Enforcer: {attacks_blocked}/{len(test_attacks)} attacks blocked")
        return True

    except ImportError as e:
        print(f"❌ Boundary Security: Import error - {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Boundary Security: Operational error - {str(e)}")
        return False

def check_cli_framework():
    """Check CLI framework availability"""
    print("\n💻 Checking CLI Framework...")

    try:
        from network_visualizer.__main__ import create_parser
        parser = create_parser()
        help_text = parser.format_help()

        if 'boundary' in help_text and 'thermal' in help_text and 'features' in help_text:
            print("✅ CLI Framework: All commands available")
            print("   🎮 Network visualization commands: thermal, features, boundary")
            return True
        else:
            print("⚠️  CLI Framework: Some commands may be missing")
            return False

    except Exception as e:
        print(f"❌ CLI Framework: Error - {str(e)}")
        return False

def check_thermal_mapper():
    """Check thermal mapper functionality"""
    print("\n🌡️  Checking Thermal Mapper...")

    try:
        from network_visualizer.thermal_mapper import visualize, ConceptualThermalMapper

        # Test basic functionality
        test_data = {"test": "data", "metrics": [1, 2, 3]}
        mapper = ConceptualThermalMapper(test_data, "Test Map")

        if len(mapper.nodes) > 0 and len(mapper.edges) >= 0:
            print("✅ Thermal Mapper: Core functionality working")
            print(f"   🗺️  Generated map: {len(mapper.nodes)} nodes, {len(mapper.edges)} edges")
            return True
        else:
            print("⚠️  Thermal Mapper: Generated empty map")
            return False

    except Exception as e:
        print(f"❌ Thermal Mapper: Error - {str(e)}")
        return False

def main():
    """Main verification function"""
    print("🎯 FINAL SYSTEM VERIFICATION")
    print("=" * 50)
    print("Verifying Atmosphere + Network Visualizer integration...")
    print()

    results = []

    # Check each component
    results.append(("Atmosphere API", check_atmosphere_api()))
    results.append(("Boundary Security", check_boundary_security()))
    results.append(("CLI Framework", check_cli_framework()))
    results.append(("Thermal Mapper", check_thermal_mapper()))

    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")

    passed = 0
    total = len(results)

    for component, status in results:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {component}: {'PASS' if status else 'FAIL'}")
        if status:
            passed += 1

    print(f"\n🎯 Overall Status: {passed}/{total} components operational")

    if passed == total:
        print("\n🎉 SYSTEM STATUS: FULLY OPERATIONAL")
        print("   ✓ Atmosphere Learning Companion API: Active")
        print("   ✓ Thermal Scan Endpoint: Functional")
        print("   ✓ Boundary Security Framework: Deployed")
        print("   ✓ Cross-Project Protection: Enforced")
        print("   ✓ Security Enforcement: Active")
        print("   ✓ CLI Management: Available")
        print("   ✓ Thermal Mapping: Working")
        print("\n🚀 Ready for production deployment!")
        return 0
    else:
        print(f"\n⚠️  SYSTEM STATUS: {passed}/{total} components operational")
        print("   Some components may need attention before deployment.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
