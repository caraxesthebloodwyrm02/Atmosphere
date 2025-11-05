"""
Demo: Self-Aware Auto-Repairing Routing System
==============================================

This demonstrates how the routing layer manages itself:
- Monitors health continuously
- Detects and resolves conflicts automatically
- Provides friendly feedback
- Requires minimal manual intervention
- Demonstrates circuit breaker functionality
"""

import asyncio
import random
import time
from orchestral_connector import OrchestralConnector
from self_aware_routing import (
    SelfAwareRouter, 
    create_self_aware_router, 
    HealthStatus, 
    CircuitState, 
    HealthCheck
)


async def simulate_workload(router: SelfAwareRouter, connector: OrchestralConnector):
    """Simulate various workload patterns with circuit breaker awareness"""
    print("🎮 Starting workload simulation...")
    print("⏱️  Duration: 20 seconds      ")
    
    end_time = time.time() + 20
    component_states = {}
    
    while time.time() < end_time:
        # Randomly simulate different conditions
        r = random.random()
        
        if r < 0.1:  # 10% chance of connection hiccup
            print("\n⚡ Simulating connection hiccup...")
            # Randomly mark a component as failing
            components = list(connector.module_status.keys())
            if components:
                component = random.choice(components)
                component_states[component] = 'failing'
                
                # Add a failing health check
                if component not in router.health_history:
                    router.health_history[component] = []
                
                # Check if circuit is open
                cb = router.circuit_breakers.get(component)
                if cb and cb.state == CircuitState.OPEN:
                    print(f"  ⚠️  {component} circuit is OPEN, not sending requests")
                    continue
                
                router.health_history[component].append(
                    HealthCheck(
                        component=component,
                        status=HealthStatus.FAILING,
                        timestamp=time.time(),
                        latency_ms=1000 + random.random() * 1000,
                        throughput_mbps=0.1,
                        error_count=1,
                        message="Connection lost"
                    )
                )
        
        elif r < 0.3:  # 20% chance of high load
            print("\n🔥 Simulating high load...")
            # Simulate high latency on random components
            for component in connector.module_status:
                if component not in router.health_history or not router.health_history[component]:
                    continue
                
                # Skip if circuit is open
                cb = router.circuit_breakers.get(component)
                if cb and cb.state == CircuitState.OPEN:
                    component_states[component] = 'circuit_open'
                    continue
                
                last = router.health_history[component][-1]
                router.health_history[component].append(
                    last.replace(
                        latency_ms=last.latency_ms * (1.5 + random.random()),
                        status=HealthStatus.DEGRADED,
                        message="High load detected"
                    )
                )
                component_states[component] = 'high_load'
        
        else:  # Normal operation
            print("\n📊 Normal load...", end="\r")
            # Reset component states
            for component in connector.module_status:
                if component in component_states and component_states[component] != 'failing':
                    component_states[component] = 'normal'
        
        # Occasionally show circuit breaker status
        if random.random() < 0.3:  # 30% chance to show status
            status = []
            for component in sorted(router.circuit_breakers.keys()):
                cb = router.circuit_breakers[component]
                state = "🟢" if cb.state == CircuitState.CLOSED else "🔴"
                status.append(f"{component[0].upper()}:{state}")
            
            state_info = " | ".join(status)
            print(f"\n🔌 Circuit States: {state_info}")
            
            # Show component states
            if component_states:
                states = [f"{k}:{v}" for k, v in component_states.items()]
                print(f"   Components: {', '.join(states)}")
        
        # Print status occasionally
        if random.random() < 0.2:  # 20% chance to show full status
            print(f"\n{router.get_friendly_status()}")
        
        # Sleep for a bit
        await asyncio.sleep(2)
    print(f"   Modules available: {sum(connector.module_status.values())}/{len(connector.module_status)}")
    print()


def print_status(router: SelfAwareRouter, title: str = ""):
    """Print a formatted status update"""
    if title:
        print("\n" + "=" * 70)
        print(f"{title:^70}")
        print("=" * 70)
    
    status = router.get_health_summary()
    print(f"\n{status['message']} ({status['overall_status']})")
    
    # Print component status
    print("\nComponent Status:")
    for name, comp in status['components'].items():
        state = comp['circuit_state'].capitalize()
        print(f"  {name}: {comp['status']} ({comp['latency_ms']:.1f}ms, {state})")
    
    # Print circuit breaker status
    if 'circuit_breakers' in status:
        print("\nCircuit Breakers:")
        for name, cb in status['circuit_breakers'].items():
            print(f"  {name}: {cb['state']} (Fails: {cb['failures']}, Success: {cb['successes']})")
    
    # Print any recent repairs
    if status.get('recent_repairs'):
        print("\nRecent Repairs:")
        for repair in status['recent_repairs'][-3:]:
            result = "✅" if repair['success'] else "❌"
            print(f"  {result} {repair['component']}: {repair['details']}")
    
    return status


async def demo_circuit_breakers():
    """Demonstrate circuit breaker functionality"""
    print("=" * 70)
    print("🔌 Circuit Breaker Demonstration")
    print("=" * 70)
    
    connector = OrchestralConnector()
    router = await create_self_aware_router(connector)
    
    # Wait for initial health check
    await asyncio.sleep(2)
    
    print("\n🔌 Initializing with circuit breakers...")
    status = print_status(router, "Initial Status")
    
    # Simulate failures to trigger circuit breakers
    print("\n💥 Simulating repeated failures to trigger circuit breakers...")
    for _ in range(5):
        # Force a failure in the echoes component
        if 'echoes' in router.health_history:
            router.health_history['echoes'].append(
                router.health_history['echoes'][-1].replace(
                    status=HealthStatus.FAILING,
                    message="Simulated failure"
                )
            )
        await asyncio.sleep(1)
    
    # Show circuit breakers in action
    status = print_status(router, "After Simulated Failures")
    
    # Show recovery after failures stop
    print("\n🔄 Waiting for circuit breakers to recover...")
    await asyncio.sleep(35)  # Wait for recovery timeout
    
    # Show final status
    status = print_status(router, "After Recovery")
    
    print("\n✅ Circuit Breaker Demo Complete!")
    return router


async def demo_basic_monitoring():
    """Demonstrate basic self-aware monitoring"""
    
    print("=" * 70)
    print("🌐 Self-Aware Routing System Demo")
    print("=" * 70)
    print()
    
    # Create orchestral connector
    print("Step 1: Initializing orchestral network...")
    connector = OrchestralConnector()
    init_result = await connector.initialize_orchestral_network()
    
    print(f"✅ Network initialized")
    print(f"   Modules available: {sum(connector.module_status.values())}/{len(connector.module_status)}")
    print()
    
    # Create self-aware router
    print("Step 2: Activating self-aware routing layer...")
    router = await create_self_aware_router(connector)
    
    print("✅ Self-aware layer activated")
    print(f"   Monitoring interval: {router.check_interval_seconds}s")
    print()
    
    # Let it monitor for a bit
    print("Step 3: Monitoring system health...")
    await asyncio.sleep(2)
    
    # Print initial status
    print("\nStep 2: Activating self-aware routing layer...")
    print(router.get_friendly_status())
    print("   Monitoring interval: 5.0s  ")
    
    # Add initial health checks if none exist
    for component in connector.module_status:
        if component not in router.health_history:
            router.health_history[component] = [
                HealthCheck(
                    component=component,
                    status=HealthStatus.HEALTHY,
                    timestamp=time.time(),
                    latency_ms=10.0 + random.random() * 5.0,
                    throughput_mbps=100.0,
                    error_count=0,
                    message="Initial health check"
                )
            ]
    
    # Show initial health
    summary = router.get_health_summary()
    print(f"\n{router.get_friendly_status()}")
    print("\nComponent Status:")
    for component, status in summary["components"].items():
        print(f"  {component}: {status['status']} ({status['latency_ms']:.1f}ms)")
    print()
    
    # Simulate some workload
    await simulate_workload(router, connector)
    
    # Final health report
    print("\n" + "=" * 70)
    print("📋 Final Health Report")
    print("=" * 70)
    
    summary = router.get_health_summary()
    
    print(f"\nOverall: {router.get_friendly_status()}")
    
    if summary["recent_conflicts"]:
        print(f"\n⚠️  Conflicts detected and resolved: {len(summary['recent_conflicts'])}")
        for conflict in summary["recent_conflicts"][-3:]:
            print(f"   - {conflict['type']}: {conflict['description']}")
    
    if summary["recent_repairs"]:
        print(f"\n🔧 Auto-repairs performed: {len(summary['recent_repairs'])}")
        for repair in summary["recent_repairs"][-3:]:
            status_icon = "✅" if repair["success"] else "❌"
            print(f"   {status_icon} {repair['action']} on {repair['component']}")
            print(f"      Duration: {repair['duration_ms']:.1f}ms")
    
    print("\n✨ Demo completed successfully!")
    print()
    
    # Stop monitoring
    await router.stop_monitoring()


async def demo_auto_repair():
    """Demonstrate auto-repair capabilities"""
    
    print("\n" + "=" * 70)
    print("🔧 Auto-Repair Demonstration")
    print("=" * 70)
    print()
    
    connector = OrchestralConnector()
    await connector.initialize_orchestral_network()
    
    router = await create_self_aware_router(connector)
    
    print("Simulating component failure...")
    print("(The router will detect and attempt auto-repair)")
    print()
    
    # Simulate a failure by marking a module as unavailable
    original_status = connector.module_status['echoes']
    connector.module_status['echoes'] = False
    
    # Wait for health check to detect the issue
    await asyncio.sleep(6)
    
    summary = router.get_health_summary()
    print(f"Status: {router.get_friendly_status()}")
    
    if summary["recent_repairs"]:
        print("\n🛠️  Auto-repair actions taken:")
        for repair in summary["recent_repairs"]:
            print(f"   Component: {repair['component']}")
            print(f"   Action: {repair['action']}")
            print(f"   Result: {'Success' if repair['success'] else 'Failed'}")
            print(f"   Details: {repair['details']}")
    
    # Restore status
    connector.module_status['echoes'] = original_status
    
    print("\n✅ Auto-repair demo completed")
    
    await router.stop_monitoring()


async def demo_friendly_feedback():
    """Demonstrate friendly, human-readable feedback"""
    
    print("\n" + "=" * 70)
    print("💬 Friendly Feedback System")
    print("=" * 70)
    print()
    
    connector = OrchestralConnector()
    await connector.initialize_orchestral_network()
    
    router = await create_self_aware_router(connector)
    
    print("The system provides friendly, non-technical status messages:")
    print()
    
    for i in range(5):
        await asyncio.sleep(2)
        status = router.get_friendly_status()
        print(f"  [{i+1}] {status}")
    
    print("\n✨ No complex technical jargon - just clear, helpful information!")
    
    await router.stop_monitoring()


async def main():
    """Run all demos"""
    
    try:
        # Basic monitoring demo
        await demo_basic_monitoring()
        
        await asyncio.sleep(2)
        
        # Auto-repair demo
        await demo_auto_repair()
        
        await asyncio.sleep(2)
        
        # Friendly feedback demo
        await demo_friendly_feedback()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🎯 Self-Aware Routing System")
    print("   The city with no residents - it manages itself\n")
    
    asyncio.run(main())
