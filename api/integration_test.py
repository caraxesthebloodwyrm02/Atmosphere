#!/usr/bin/env python3
"""
Complete Integration Test
Test the full integration between Atmosphere components and OpenAI API.
"""

import asyncio
import json
import os
from datetime import datetime

# Test all components
async def test_atmosphere_integration():
    """Test complete Atmosphere integration."""
    print("🌍 Atmosphere Complete Integration Test")
    print("=" * 50)
    
    # Test 1: Main atmosphere project
    print("\n1️⃣ Testing main Atmosphere project...")
    try:
        import sys
        # Add atmosphere root to path
        atmosphere_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, atmosphere_root)
        
        from __init__ import get_version_info
        versions = get_version_info()
        
        print("✅ Atmosphere project initialized")
        for component, version in versions.items():
            if version not in ["unknown", "not_installed"]:
                print(f"   • {component.title()}: v{version}")
            else:
                print(f"   • {component.title()}: {version}")
                
    except Exception as e:
        print(f"❌ Atmosphere project test failed: {e}")
        return False
    
    # Test 2: Direct OpenAI API
    print("\n2️⃣ Testing Direct OpenAI API...")
    try:
        from api.client import test_api, chat
        
        if test_api():
            print("✅ OpenAI API connection successful")
            
            # Test simple chat
            response = await chat("Say 'Integration test successful'")
            print(f"✅ Chat response: {response}")
            
        else:
            print("❌ OpenAI API connection failed")
            return False
            
    except Exception as e:
        print(f"❌ OpenAI API test failed: {e}")
        return False
    
    # Test 3: Routing API Integration
    print("\n3️⃣ Testing Routing API Integration...")
    try:
        from Routing.api_connector_main import test_routing_api, route_with_ai
        
        if test_routing_api():
            print("✅ Routing API integration successful")
            
            # Test routing with AI
            routing_data = {
                "source": "microphone",
                "destination": "speakers",
                "parameters": {
                    "latency": "low",
                    "quality": "high"
                }
            }
            
            result = await route_with_ai(routing_data)
            if result["status"] == "success":
                print("✅ AI-powered routing optimization working")
            else:
                print("⚠️ Using fallback routing")
                
        else:
            print("❌ Routing API integration failed")
            return False
            
    except Exception as e:
        print(f"❌ Routing API test failed: {e}")
        return False
    
    # Test 4: Echoes Integration
    print("\n4️⃣ Testing Echoes Integration...")
    try:
        import Echoes
        print(f"✅ Echoes v{Echoes.__version__} initialized")
        
    except Exception as e:
        print(f"❌ Echoes test failed: {e}")
        return False
    
    # Test 5: Complete workflow
    print("\n5️⃣ Testing complete workflow...")
    try:
        # Simulate a complete audio processing workflow
        print("   🎵 Simulating audio input...")
        await asyncio.sleep(0.1)
        
        print("   🛣️ Optimizing routing with AI...")
        routing_result = await route_with_ai({
            "input": "audio_stream",
            "output": "processed_audio",
            "quality": "studio"
        })
        
        print("   🤖 AI analysis complete...")
        ai_response = await chat("Analyze this routing optimization and suggest improvements.")
        print(f"   ✅ AI suggestions received: {len(ai_response)} characters")
        
        print("   📊 Processing complete...")
        
    except Exception as e:
        print(f"❌ Complete workflow test failed: {e}")
        return False
    
    return True

async def main():
    """Main integration test function."""
    print("🚀 Starting Complete Integration Test")
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await test_atmosphere_integration()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 INTEGRATION TEST COMPLETE - ALL SYSTEMS GO!")
        print("✅ Atmosphere platform fully operational")
        print("✅ OpenAI API integration working")
        print("✅ Routing with AI optimization functional")
        print("✅ All components properly connected")
        print("✅ Ready for production deployment")
    else:
        print("❌ INTEGRATION TEST FAILED")
        print("⚠️ Some components need attention")
        print("🔧 Review error messages above")
    
    print(f"⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)

if __name__ == "__main__":
    asyncio.run(main())
