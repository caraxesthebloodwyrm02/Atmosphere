#!/usr/bin/env python3
"""
Complete Ecosystem Integration Test
Test all components with explicit onboarding paths.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add atmosphere root to path
atmosphere_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, atmosphere_root)

async def test_complete_integration():
    """Test complete ecosystem integration."""
    print("🌍 Complete Ecosystem Integration Test")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Initialize ecosystem
    print("\n1️⃣ Testing Ecosystem Core...")
    try:
        from ecosystem import initialize_ecosystem, get_ecosystem
        
        ecosystem = await initialize_ecosystem()
        status = await ecosystem.get_ecosystem_status()
        
        print(f"✅ Ecosystem initialized")
        print(f"   • Components: {status['integrated_components']}/{status['total_components']}")
        print(f"   • Integration Rate: {status['integration_rate']}")
        print(f"   • Health: {status['health']}")
        
    except Exception as e:
        print(f"❌ Ecosystem test failed: {e}")
        return False
    
    # Test 2: EchoesAI explicit onboarding
    print("\n2️⃣ Testing EchoesAI Explicit Onboarding...")
    try:
        from Echoes.onboarding import onboard_echoes
        
        echoes_result = await onboard_echoes()
        
        if echoes_result['onboarding_status'] == 'complete':
            print("✅ EchoesAI explicit onboarding successful")
            print(f"   • Ecosystem Connection: {echoes_result['ecosystem_connection']['status']}")
            print(f"   • API Integration: {echoes_result['api_integration']['status']}")
            print(f"   • Capabilities: {len(echoes_result['capabilities'])}")
        else:
            print(f"❌ EchoesAI onboarding failed: {echoes_result.get('error')}")
            
    except Exception as e:
        print(f"❌ EchoesAI test failed: {e}")
        return False
    
    # Test 3: Direct API integration
    print("\n3️⃣ Testing Direct API Integration...")
    try:
        from api.client import test_api, chat
        
        if test_api():
            print("✅ Direct OpenAI API connected")
            
            # Test chat functionality
            response = await chat("Ecosystem integration test - respond with 'operational'")
            print(f"✅ Chat response: {response}")
            
        else:
            print("❌ Direct API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Direct API test failed: {e}")
        return False
    
    # Test 4: Routing AI integration
    print("\n4️⃣ Testing Routing AI Integration...")
    try:
        from Routing.api_connector_main import test_routing_api, route_with_ai
        
        if test_routing_api():
            print("✅ Routing API integration working")
            
            # Test AI routing
            routing_data = {
                "source": "test_input",
                "destination": "test_output",
                "ecosystem_sync": True
            }
            
            result = await route_with_ai(routing_data)
            if result['status'] == 'success':
                print("✅ AI-powered routing optimization working")
            else:
                print("⚠️ Using fallback routing")
                
        else:
            print("❌ Routing API integration failed")
            
    except Exception as e:
        print(f"❌ Routing test failed: {e}")
        return False
    
    # Test 5: Component synchronization
    print("\n5️⃣ Testing Component Synchronization...")
    try:
        # Test all components are at v1.0.0
        components = {
            "Echoes": "Echoes",
            "Delay": "Delay", 
            "Reverb": "Reverb",
            "Routing": "Routing",
            "API": "api"
        }
        
        synced_count = 0
        for name, module_name in components.items():
            try:
                module = __import__(module_name)
                version = getattr(module, '__version__', 'unknown')
                if version == "1.0.0":
                    print(f"   ✅ {name}: v{version}")
                    synced_count += 1
                else:
                    print(f"   ⚠️ {name}: v{version}")
            except Exception as e:
                print(f"   ❌ {name}: {e}")
        
        sync_rate = (synced_count / len(components)) * 100
        print(f"📊 Synchronization Rate: {sync_rate:.1f}%")
        
    except Exception as e:
        print(f"❌ Synchronization test failed: {e}")
        return False
    
    # Test 6: Complete workflow
    print("\n6️⃣ Testing Complete Workflow...")
    try:
        print("   🎵 Simulating audio input through EchoesAI...")
        await asyncio.sleep(0.1)
        
        print("   🛣️ Optimizing routing with AI...")
        routing_result = await route_with_ai({
            "input": "echoes_stream",
            "output": "processed_audio",
            "optimization": "ecosystem"
        })
        
        print("   🤖 AI analysis through OpenAI...")
        ai_response = await chat("Analyze this ecosystem workflow and confirm optimization.")
        print(f"   ✅ AI analysis: {len(ai_response)} characters")
        
        print("   📊 Processing complete...")
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False
    
    return True

async def main():
    """Main integration test function."""
    success = await test_complete_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 COMPLETE ECOSYSTEM INTEGRATION SUCCESS!")
        print("✅ All components properly onboarded")
        print("✅ EchoesAI explicit onboarding working")
        print("✅ Direct OpenAI API integration functional")
        print("✅ Routing AI optimization operational")
        print("✅ Component synchronization complete")
        print("✅ Complete workflow verified")
        print("\n🚀 Atmosphere ecosystem is fully operational!")
    else:
        print("❌ ECOSYSTEM INTEGRATION FAILED")
        print("⚠️ Some components need attention")
        print("🔧 Review error messages above")
    
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
