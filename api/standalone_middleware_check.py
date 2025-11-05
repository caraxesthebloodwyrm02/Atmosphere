#!/usr/bin/env python3
"""
Standalone Middleware Interference Check
Test for any middleware or components interfering with direct API communication.
"""

import asyncio
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, Any, List

# Add atmosphere root to path
atmosphere_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, atmosphere_root)

# Test direct OpenAI API communication
async def test_direct_openai_connection():
    """Test direct OpenAI API connection without any middleware."""
    print("🔍 Testing Direct OpenAI API Connection...")
    
    try:
        # Import direct client
        from api.client import DirectOpenAIClient
        
        # Initialize client
        client = DirectOpenAIClient()
        
        # Test simple request
        start_time = time.time()
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "Say 'Direct connection successful'"}],
            max_tokens=10
        )
        end_time = time.time()
        
        print(f"✅ Direct OpenAI API: Connected")
        print(f"   • Response: {response['content']}")
        print(f"   • Response time: {(end_time - start_time):.2f}s")
        print(f"   • Model: {response['model']}")
        print(f"   • Tokens: {response['usage']['total_tokens']}")
        
        return True, response
        
    except Exception as e:
        print(f"❌ Direct OpenAI API failed: {e}")
        return False, {"error": str(e)}

async def test_echoes_middleware_interference():
    """Test if Echoes middleware interferes with API communication."""
    print("\n🔍 Testing Echoes Middleware Interference...")
    
    try:
        # Check if Echoes API server is running and has middleware
        from Echoes.api.config import get_config
        
        config = get_config()
        
        print(f"📋 Echoes API Configuration:")
        print(f"   • API Key Required: {config.security.api_key_required}")
        print(f"   • Rate Limiting: {config.security.rate_limit_requests} req/{config.security.rate_limit_window}s")
        print(f"   • Timeout: {config.api.request_timeout}s")
        print(f"   • OpenAI API Key: {'Set' if config.openai_api_key else 'Not Set'}")
        
        # Check middleware status
        middleware_status = {
            "authentication_enabled": config.security.api_key_required,
            "rate_limiting_enabled": config.security.rate_limit_requests > 0,
            "timeout_enabled": config.api.request_timeout > 0,
            "cors_enabled": True,  # Always enabled in Echoes
            "logging_enabled": True
        }
        
        print(f"\n🔧 Middleware Status:")
        for middleware, enabled in middleware_status.items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {middleware.replace('_', ' ').title()}")
        
        # Test if middleware affects OpenAI calls
        if config.security.api_key_required:
            print(f"\n⚠️ WARNING: Echoes API requires authentication")
            print(f"   This may interfere with direct OpenAI API calls")
            return False, {"error": "Authentication middleware enabled"}
        
        print(f"\n✅ Echoes middleware should not interfere with direct API calls")
        return True, middleware_status
        
    except Exception as e:
        print(f"❌ Echoes middleware check failed: {e}")
        return False, {"error": str(e)}

async def test_proxy_interference():
    """Test for any proxy or network interference."""
    print("\n🔍 Testing Proxy/Network Interference...")
    
    # Check environment variables for proxy settings
    proxy_vars = [
        'HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy',
        'ALL_PROXY', 'all_proxy', 'NO_PROXY', 'no_proxy'
    ]
    
    proxy_found = False
    for var in proxy_vars:
        if os.getenv(var):
            print(f"⚠️ Proxy environment variable found: {var}={os.getenv(var)}")
            proxy_found = True
    
    if not proxy_found:
        print("✅ No proxy environment variables detected")
    
    # Check for OpenAI-specific proxy settings
    openai_proxy = os.getenv('OPENAI_PROXY')
    if openai_proxy:
        print(f"⚠️ OpenAI proxy configured: {openai_proxy}")
        return False, {"error": "OpenAI proxy may interfere with direct connection"}
    else:
        print("✅ No OpenAI proxy configured")
    
    return True, {"proxy_detected": proxy_found}

async def test_concurrent_connections():
    """Test concurrent connections to check for rate limiting interference."""
    print("\n🔍 Testing Concurrent Connections...")
    
    try:
        from api.client import DirectOpenAIClient
        
        client = DirectOpenAIClient()
        
        # Make multiple concurrent requests
        tasks = []
        for i in range(3):
            task = client.chat_completion(
                messages=[{"role": "user", "content": f"Concurrent test {i+1}"}],
                max_tokens=5
            )
            tasks.append(task)
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        successful_requests = [r for r in results if not isinstance(r, Exception)]
        failed_requests = [r for r in results if isinstance(r, Exception)]
        
        print(f"📊 Concurrent Request Results:")
        print(f"   • Total requests: {len(tasks)}")
        print(f"   • Successful: {len(successful_requests)}")
        print(f"   • Failed: {len(failed_requests)}")
        print(f"   • Total time: {(end_time - start_time):.2f}s")
        
        if len(successful_requests) >= 2:
            print("✅ Concurrent connections working properly")
            return True, {"successful": len(successful_requests), "failed": len(failed_requests)}
        else:
            print("⚠️ Possible rate limiting or interference detected")
            return False, {"successful": len(successful_requests), "failed": len(failed_requests)}
            
    except Exception as e:
        print(f"❌ Concurrent connection test failed: {e}")
        return False, {"error": str(e)}

async def test_endpoint_authenticity():
    """Test if we're hitting authentic OpenAI endpoints."""
    print("\n🔍 Testing Endpoint Authenticity...")
    
    try:
        from api.client import DirectOpenAIClient
        
        client = DirectOpenAIClient()
        
        # Test with a specific model to verify we're hitting real OpenAI
        response = await client.chat_completion(
            messages=[{"role": "user", "content": "What is 2+2?"}],
            model="gpt-3.5-turbo",
            max_tokens=10
        )
        
        # Check response characteristics
        content = response.get('content', '').lower()
        model = response.get('model', '')
        usage = response.get('usage', {})
        
        print(f"📋 Authenticity Check Results:")
        print(f"   • Model: {model}")
        print(f"   • Content: {response.get('content', '')}")
        print(f"   • Usage: {usage}")
        
        # Verify it's a real OpenAI response
        is_authentic = (
            'gpt' in model.lower() and 
            len(content.strip()) > 0 and
            usage.get('total_tokens', 0) > 0
        )
        
        if is_authentic:
            print("✅ Authentic OpenAI endpoint response confirmed")
            return True, response
        else:
            print("❌ Response appears to be from non-authentic endpoint")
            return False, {"error": "Non-authentic endpoint detected"}
            
    except Exception as e:
        print(f"❌ Endpoint authenticity test failed: {e}")
        return False, {"error": str(e)}

async def test_routing_api_interference():
    """Test if Routing API middleware interferes."""
    print("\n🔍 Testing Routing API Interference...")
    
    try:
        from Routing.api_connector_main import test_routing_api
        
        if test_routing_api():
            print("✅ Routing API connection working")
            print("✅ No routing middleware interference detected")
            return True, {"routing_connected": True}
        else:
            print("❌ Routing API connection failed")
            return False, {"routing_connected": False}
            
    except Exception as e:
        print(f"❌ Routing API test failed: {e}")
        return False, {"error": str(e)}

async def main():
    """Main middleware interference check."""
    print("🔍 Standalone Middleware Interference Check")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    tests = [
        ("Direct OpenAI Connection", test_direct_openai_connection),
        ("Echoes Middleware Interference", test_echoes_middleware_interference),
        ("Proxy/Network Interference", test_proxy_interference),
        ("Concurrent Connections", test_concurrent_connections),
        ("Endpoint Authenticity", test_endpoint_authenticity),
        ("Routing API Interference", test_routing_api_interference)
    ]
    
    results = {}
    overall_status = "PASS"
    
    for test_name, test_func in tests:
        try:
            success, result = await test_func()
            results[test_name] = {"success": success, "result": result}
            if not success:
                overall_status = "FAIL"
        except Exception as e:
            results[test_name] = {"success": False, "error": str(e)}
            overall_status = "FAIL"
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 MIDDLEWARE INTERFERENCE CHECK SUMMARY")
    print("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        print(f"{status} {test_name}")
        
        if not result["success"]:
            if "error" in result:
                print(f"    • Error: {result['error']}")
            if "result" in result and isinstance(result["result"], dict):
                for key, value in result["result"].items():
                    print(f"    • {key}: {value}")
    
    print(f"\n🎯 OVERALL STATUS: {overall_status}")
    
    if overall_status == "PASS":
        print("✅ No middleware interference detected")
        print("✅ Direct API communication is authentic and unobstructed")
        print("✅ All endpoints are properly accessible")
    else:
        print("❌ Middleware interference detected")
        print("⚠️ Some components may be blocking direct API communication")
        print("🔧 Review failed tests above for specific issues")
    
    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    return overall_status == "PASS"

if __name__ == "__main__":
    asyncio.run(main())
