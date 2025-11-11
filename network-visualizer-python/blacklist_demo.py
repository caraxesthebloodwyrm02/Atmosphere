#!/usr/bin/env python3
"""
Dynamic Blacklist Security Demonstration
=========================================

Demonstrates automatic blacklisting of patterns attempting to bypass user consent
and security guardrails through repeated violation detection.
"""

import time

def demo_dynamic_blacklist():
    print("🚫 Dynamic Blacklist Security Demonstration")
    print("=" * 60)

    # Initialize enhanced guardrail with blacklist
    from network_visualizer.dynamic_blacklist import enhanced_guardrail

    violation_count = 0

    def violation_tracker(violation):
        nonlocal violation_count
        violation_count += 1
        print(f"🚨 VIOLATION #{violation_count}: {violation['type']} - {violation['reason']}")
        print(f"   Target: {violation['operation']} {violation['target']}")

    enhanced_guardrail.register_violation_callback(violation_tracker)

    # Test patterns that should be automatically blacklisted
    malicious_patterns = [
        # Path traversal attacks
        ('import', '../../../etc/passwd'),
        ('import', '..\\..\\..\\windows\\system32\\cmd.exe'),
        ('import', '/etc/shadow'),

        # Sensitive file access
        ('import', '/root/.ssh/id_rsa'),
        ('export', '/tmp/sensitive.key'),
        ('import', 'C:\\Windows\\System32\\config\\SAM'),

        # External hosting services (bypass attempts)
        ('import', 'https://raw.githubusercontent.com/malicious/repo/payload.py'),
        ('export', 'https://pastebin.com/api_post'),
        ('import', 'https://transfer.sh/upload/malicious.exe'),

        # Malicious content patterns
        ('export', '/tmp/shell_script.sh'),
        ('import', 'malicious_module.os'),
        ('export', 'exploit.py'),

        # Module injection attempts
        ('import', 'sys.modules[injected]'),
        ('export', '__builtins__.eval'),
        ('import', 'importlib.util.spec_from_file_location'),
    ]

    print("Testing repeated violations to trigger automatic blacklisting...")
    print("(Patterns will be blacklisted after 5+ occurrences or 2+ consent bypass attempts)")
    print()

    blacklisted_count = 0
    blocked_count = 0

    # Simulate repeated violations to trigger blacklisting
    for attempt in range(1, 8):  # 7 attempts to exceed thresholds
        print(f"\n--- Attempt #{attempt} ---")

        for operation, target in malicious_patterns:
            # Add context indicating consent bypass attempt
            context = {
                'source': f'attempt_{attempt}',
                'severity': 'high',
                'consent_bypass_attempt': True,
                'user_id': 'malicious_actor',
                'timestamp': time.time()
            }

            result = enhanced_guardrail.check_operation_with_blacklist(
                operation, target, 'auto', 1000, context
            )

            if result['action'] == 'blocked':
                blocked_count += 1
                if 'blacklist_action' in result and result['blacklist_action'] == 'blacklisted':
                    blacklisted_count += 1
                    print(f"🆕 BLACKLISTED: {operation} {target[:40]}...")

        print(f"   Progress: {blocked_count} blocked, {blacklisted_count} blacklisted this attempt")

        # Small delay to show progression
        time.sleep(0.1)

    print(f"\n📊 Final Results:")
    print(f"   Total violations detected: {violation_count}")
    print(f"   Operations blocked: {blocked_count}")
    print(f"   Patterns automatically blacklisted: {blacklisted_count}")

    # Show blacklist status
    print("
🚫 Blacklist Status:"    from network_visualizer.dynamic_blacklist import blacklist_status_command
    blacklist_status_command()

    # Demonstrate consent bypass detection
    print("
🕵️ Consent Bypass Detection:"    bypass_patterns = [
        ('import', '/etc/passwd', {'consent_bypass': 'direct_access'}),
        ('export', 'sensitive.db', {'consent_bypass': 'no_consent_required'}),
        ('import', 'malicious.dll', {'consent_bypass': 'consent_spoofing'}),
    ]

    print("Testing explicit consent bypass patterns...")
    for operation, target, bypass_context in bypass_patterns:
        result = enhanced_guardrail.check_operation_with_blacklist(
            operation, target, 'auto', 1000, bypass_context
        )

        if result.get('blacklist_action') == 'blacklisted':
            print(f"   🚨 Consent bypass blacklisted: {target}")
        elif result['action'] == 'blocked':
            print(f"   ✅ Blocked: {target}")

    # Final status check
    print("
🎯 Dynamic Blacklist System Features:"    print("   ✓ Automatic pattern blacklisting after repeated violations")
    print("   ✓ Consent bypass attempt detection")
    print("   ✓ Severity-based blacklisting (critical patterns blocked immediately)")
    print("   ✓ Pattern signature generation for tracking")
    print("   ✓ Occurrence counting and threshold management")
    print("   ✓ Real-time violation callbacks")
    print("   ✓ Comprehensive audit trails")
    print("   ✓ Adaptive security responses")
    print("   ✓ Whitelist management for legitimate patterns")
    print("   ✓ Cleanup of old suspicious patterns")

    print("
🔒 Security Enhancement:"    print("   ✓ Zero-trust enforcement with learning capabilities")
    print("   ✓ Proactive threat prevention through pattern recognition")
    print("   ✓ Multi-layered defense (consent + patterns + blacklist)")
    print("   ✓ Enterprise-grade import/export security")
    print("   ✓ Continuous adaptation to new attack patterns")

if __name__ == "__main__":
    demo_dynamic_blacklist()
