#!/usr/bin/env python3
"""
Violation Penalty System Demonstration
======================================

Demonstrates progressive penalty escalation for security violations,
blacklist patterns, and recovery mechanisms.
"""

import time

def demo_penalty_system():
    print("⚖️ Violation Penalty System Demonstration")
    print("=" * 60)

    # Initialize penalty system
    from network_visualizer.penalty_system import penalty_system

    # Register enforcement callback to track actions
    enforcement_log = []

    def enforcement_tracker(penalty, action, violation_data):
        enforcement_log.append({
            'penalty_id': penalty.violation_id,
            'action': action.value,
            'level': penalty.penalty_level.value,
            'source': violation_data.get('source', 'unknown')
        })
        print(f"🔧 ENFORCED: {action.value} for {penalty.violation_id} ({penalty.penalty_level.value})")

    penalty_system.register_enforcement_callback(enforcement_tracker)

    # Simulate escalating violations from malicious actor
    malicious_source = "malicious_actor_demo"

    print("Testing progressive penalty escalation...")
    print("(Penalties escalate from Warning → Minor → Moderate → Major → Critical)")
    print()

    # Test violations that should trigger different penalty levels
    violations = [
        # Low frequency violations (should stay at warning/minor)
        {'severity': 'low', 'description': 'Minor policy violation'},
        {'severity': 'low', 'description': 'Another minor violation'},
        {'severity': 'medium', 'description': 'Moderate violation'},

        # Medium frequency (should hit minor/moderate penalties)
        {'severity': 'medium', 'description': 'Repeated moderate violation'},
        {'severity': 'medium', 'description': 'Another moderate violation'},

        # High frequency (should trigger major penalties)
        {'severity': 'high', 'description': 'High severity violation'},
        {'severity': 'high', 'description': 'Repeated high severity'},
        {'severity': 'high', 'description': 'Critical threshold reached'},
        {'severity': 'high', 'description': 'Major penalty triggered'},

        # Critical violations (should trigger system lockdown)
        {'severity': 'critical', 'description': 'Critical security breach'},
        {'severity': 'critical', 'description': 'System lockdown initiated'},
    ]

    applied_penalties = []

    for i, violation_info in enumerate(violations, 1):
        print(f"\n--- Violation #{i}: {violation_info['description']} ---")

        violation_data = {
            'violation_id': f"demo_violation_{i}",
            'source': malicious_source,
            'severity': violation_info['severity'],
            'type': 'demo_violation',
            'description': violation_info['description'],
            'timestamp': time.time()
        }

        result = penalty_system.process_violation(violation_data)

        print(f"Result: {result['action']}")
        if result['action'] == 'penalty_applied':
            applied_penalties.append(result)
            print(f"Penalty Level: {result['penalty_level']}")
            print(f"Actions: {', '.join(result['actions'])}")
            if result.get('duration_minutes'):
                print(f"Duration: {result['duration_minutes']} minutes")

    print(f"\n📊 Penalty Escalation Summary:")
    print(f"   Total violations processed: {len(violations)}")
    print(f"   Penalties applied: {len(applied_penalties)}")

    if applied_penalties:
        print(f"   Penalty levels applied: {', '.join(set(p['penalty_level'] for p in applied_penalties))}")

    # Show enforcement actions taken
    print(f"\n🔧 Enforcement Actions Taken: {len(enforcement_log)}")
    action_counts = {}
    for action in enforcement_log:
        action_counts[action['action']] = action_counts.get(action['action'], 0) + 1

    for action, count in action_counts.items():
        print(f"   {action}: {count} times")

    # Show current penalty status
    print("
⚖️ Current Penalty Status:"    from network_visualizer.penalty_system import penalty_status_command
    penalty_status_command()

    # Demonstrate recovery mechanisms
    print("
🔄 Testing Recovery Mechanisms:"    if applied_penalties:
        # Request review for first major penalty
        major_penalties = [p for p in applied_penalties if p['penalty_level'] in ['major', 'critical']]
        if major_penalties:
            penalty_id = major_penalties[0]['penalty_level'] + "_penalty_1"  # Approximate
            review_result = penalty_system.request_penalty_review(f"demo_violation_{len(violations)//2}", "False positive detected")
            print(f"Review requested: {review_result['status']}")

        # Grant amnesty for demonstration
        amnesty_result = penalty_system.grant_penalty_amnesty("demo_violation_8", "Administrative demonstration")
        if amnesty_result:
            print("Amnesty granted for demonstration penalty")
            print("1-hour grace period applied")

    # Show source history
    print("
📋 Source Penalty History:"    from network_visualizer.penalty_system import penalty_source_command
    penalty_source_command(malicious_source)

    # Cleanup demonstration
    print("
🧹 Cleaning up demonstration penalties:"    cleaned = penalty_system.cleanup_expired_penalties()
    print(f"Expired penalties cleaned: {cleaned}")

    print("
🎯 Penalty System Features Demonstrated:"    print("   ✓ Progressive penalty escalation based on violation frequency")
    print("   ✓ Severity-based penalty levels (Warning → Critical)")
    print("   ✓ Multiple enforcement actions per penalty level")
    print("   ✓ Temporary and permanent penalty durations")
    print("   ✓ Incident response and system lockdown capabilities")
    print("   ✓ Administrative review and amnesty procedures")
    print("   ✓ Grace periods for recovered sources")
    print("   ✓ Comprehensive audit trails")
    print("   ✓ Source-specific penalty tracking")

    print("
🛡️ Advanced Security Enforcement:"    print("   ✓ Deterrence through escalating consequences")
    print("   ✓ Proportional response to threat levels")
    print("   ✓ Recovery paths for legitimate users")
    print("   ✓ Administrative control and oversight")
    print("   ✓ Integration with blacklist and guardrail systems")

    # Final status check
    final_status = penalty_system.get_penalty_status()
    active_penalties = final_status['active_penalties']

    if active_penalties == 0:
        print("
✨ Demonstration completed - No active penalties remain"    else:
        print(f"\n⚠️ {active_penalties} penalties still active for demonstration")

if __name__ == "__main__":
    demo_penalty_system()
