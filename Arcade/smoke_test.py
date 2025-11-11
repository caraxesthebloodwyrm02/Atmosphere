#!/usr/bin/env python3
"""
Atmosphere Ecosystem Smoke Test & Integration Validation
========================================================

Quick smoke test to validate that all Atmosphere ecosystem components
are properly integrated and functioning together.
"""

import requests
import json
import time
import sys
from pathlib import Path

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

def run_smoke_test():
    """Run comprehensive smoke test of Atmosphere ecosystem."""

    base_url = "http://localhost:7681"

    print("🚀 Atmosphere Ecosystem Smoke Test")
    print("=" * 45)

    # Test 1: Server Health
    print("1️⃣  Testing Server Health...")
    try:
        response = requests.get(f"{base_url}/arcade/status", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Server Status: {data.get('status', 'unknown')}")
            print(f"   📊 Version: {data.get('version', 'unknown')}")
            print(f"   🤖 AI Services: {len(data.get('ai_enabled', []))}")
        else:
            print(f"   ❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Server connection failed: {e}")
        return False

    # Test 2: AI Integrations
    print("\n2️⃣  Testing AI Integrations...")
    ai_tests = [
        ("Grok", "/grokipedia/query", {"q": "test", "limit": 1}),
        ("ChatGPT", "/chatgpt/conversation/start", {"user_id": "smoke_test", "primary_language": "en"}),
        ("Claude", "/claude/session/start", {"user_id": "smoke_test"}),
    ]

    ai_passed = 0
    for ai_name, endpoint, payload in ai_tests:
        try:
            if endpoint == "/grokipedia/query":
                response = requests.get(f"{base_url}{endpoint}", params=payload, timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=10)

            if response.status_code == 200:
                print(f"   ✅ {ai_name}: Integration working")
                ai_passed += 1
            else:
                print(f"   ⚠️  {ai_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {ai_name}: {str(e)[:50]}...")

    print(f"   📊 AI Tests: {ai_passed}/{len(ai_tests)} passed")

    # Test 3: Design Intelligence
    print("\n3️⃣  Testing Design Intelligence...")
    design_tests = [
        ("Correspondence Analysis", "/io/analyze/smoke_test_user", {
            "interactions": [{"component": "test", "frequency": 1, "satisfaction": 0.8, "success": True}]
        }),
        ("Compass Navigation", "/io/compass/smoke_test_user", {"target_zone": "core_nexus"}),
        ("Design Zones", "/io/zones", {}),
    ]

    design_passed = 0
    for test_name, endpoint, payload in design_tests:
        try:
            if endpoint == "/io/zones":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=10)

            if response.status_code == 200:
                print(f"   ✅ {test_name}: Working")
                design_passed += 1
            else:
                print(f"   ⚠️  {test_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {test_name}: {str(e)[:50]}...")

    print(f"   📊 Design Tests: {design_passed}/{len(design_tests)} passed")

    # Test 4: Ecosystem Orchestration
    print("\n4️⃣  Testing Ecosystem Orchestration...")
    ecosystem_tests = [
        ("Ecosystem Health", "/atmosphere/ecosystem/health", {}),
        ("Component Info", "/atmosphere/components", {}),
        ("Feedback Processing", "/atmosphere/process-feedback", {
            "user_id": "smoke_test",
            "content": "Quick smoke test of feedback system",
            "feedback_type": "smoke_test"
        }),
    ]

    ecosystem_passed = 0
    for test_name, endpoint, payload in ecosystem_tests:
        try:
            if test_name == "Component Info":
                response = requests.get(f"{base_url}{endpoint}", timeout=10)
            else:
                response = requests.post(f"{base_url}{endpoint}", json=payload, timeout=10)

            if response.status_code == 200:
                print(f"   ✅ {test_name}: Working")
                ecosystem_passed += 1
            else:
                print(f"   ⚠️  {test_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {test_name}: {str(e)[:50]}...")

    print(f"   📊 Ecosystem Tests: {ecosystem_passed}/{len(ecosystem_tests)} passed")

    # Test 5: Enterprise Management
    print("\n5️⃣  Testing Enterprise Management...")
    enterprise_tests = [
        ("Executive Dashboard", "/architecture/dashboard", {}),
        ("Business Metrics", "/architecture/metrics", {}),
        ("Enterprise Health", "/architecture/health", {}),
        ("Resource Allocation", "/architecture/resources", {}),
    ]

    enterprise_passed = 0
    for test_name, endpoint, payload in enterprise_tests:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=10)

            if response.status_code == 200:
                print(f"   ✅ {test_name}: Working")
                enterprise_passed += 1
            else:
                print(f"   ⚠️  {test_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {test_name}: {str(e)[:50]}...")

    print(f"   📊 Enterprise Tests: {enterprise_passed}/{len(enterprise_tests)} passed")

    # Test 6: WebSocket Connection
    print("\n6️⃣  Testing WebSocket Connection...")
    try:
        # Simple WebSocket connection test (basic connectivity)
        import websocket
        ws_url = f"ws://localhost:7681/arcade/ws"
        ws = websocket.create_connection(ws_url, timeout=5)
        ws.close()
        print("   ✅ WebSocket: Connection successful")
        websocket_passed = True
    except Exception as e:
        print(f"   ❌ WebSocket: {str(e)[:50]}...")
        websocket_passed = False

    # Overall Results
    print("\n" + "=" * 45)
    print("🎯 SMOKE TEST RESULTS")

    total_tests = len(ai_tests) + len(design_tests) + len(ecosystem_tests) + len(enterprise_tests) + 1
    total_passed = ai_passed + design_passed + ecosystem_passed + enterprise_passed + (1 if websocket_passed else 0)
    success_rate = (total_passed / total_tests) * 100

    print(f"📊 Total Tests: {total_tests}")
    print(f"✅ Passed: {total_passed}")
    print(f"📈 Success Rate: {success_rate:.1f}%")

    # Component breakdown
    print("
🔍 Component Status:"    print(f"   🤖 AI Integrations: {ai_passed}/{len(ai_tests)}")
    print(f"   🎯 Design Intelligence: {design_passed}/{len(design_tests)}")
    print(f"   🌍 Ecosystem Orchestration: {ecosystem_passed}/{len(ecosystem_tests)}")
    print(f"   🏗️ Enterprise Management: {enterprise_passed}/{len(enterprise_tests)}")
    print(f"   🔌 WebSocket Connection: {'✅' if websocket_passed else '❌'}")

    # Final assessment
    print("
🏁 FINAL ASSESSMENT:"    if success_rate >= 95:
        print("   🏆 EXCELLENT: All systems operational! Atmosphere ecosystem fully functional.")
        return True
    elif success_rate >= 85:
        print("   ✅ GOOD: Core functionality working. Minor issues detected.")
        return True
    elif success_rate >= 70:
        print("   ⚠️  FAIR: Basic operations functional but some components need attention.")
        return True
    else:
        print("   ❌ POOR: Critical components failing. System needs immediate attention.")
        return False

def main():
    """Main smoke test function."""
    success = run_smoke_test()

    if success:
        print("\n🚀 Atmosphere Ecosystem Ready for Production!")
        print("\n💡 Next Steps:")
        print("   • Run comprehensive tests: python demo_comprehensive_atmosphere.py")
        print("   • Performance testing: python performance_load_test.py")
        print("   • Access web interface: http://localhost:7681")
        print("   • Check API docs: http://localhost:7681/docs")
    else:
        print("\n⚠️  Issues detected. Please check server logs and component configurations.")
        print("   Run individual component tests for detailed diagnostics.")

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
