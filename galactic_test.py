#!/usr/bin/env python3
"""
Galactic PyPI Test - Verify package functionality before launch!
"""

import numpy as np

def test_delay_module():
    """Test the delay module works"""
    try:
        from src.delay.core.delay_essence import Delay
        delay = Delay(time_ms=100, feedback=0.3)
        signal = np.random.randn(1000)
        processed = delay.process_signal(signal)
        print("✅ Delay module working!")
        return True
    except Exception as e:
        print(f"❌ Delay module failed: {e}")
        return False

def test_reverb_module():
    """Test the reverb module works"""
    try:
        from src.reverb.services.reverb_service import ReverbService
        service = ReverbService()
        print("✅ Reverb module working!")
        return True
    except Exception as e:
        print(f"❌ Reverb module failed: {e}")
        return False

def test_network_module():
    """Test the network module works"""
    try:
        from src.network import NetworkPresence
        network = NetworkPresence(device_id="test")
        print("✅ Network module working!")
        return True
    except Exception as e:
        print(f"❌ Network module failed: {e}")
        return False

def main():
    """Run galactic verification tests"""
    print("🚀 GALACTIC PyPI PRE-LAUNCH VERIFICATION")
    print("=" * 50)

    tests = [
        test_delay_module,
        test_reverb_module,
        test_network_module,
    ]

    passed = 0
    for test in tests:
        if test():
            passed += 1

    print("=" * 50)
    print(f"Tests passed: {passed}/{len(tests)}")

    if passed == len(tests):
        print("🎉 ALL SYSTEMS GO! Ready for PyPI launch!")
        return True
    else:
        print("⚠️  Some systems need attention before launch.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
