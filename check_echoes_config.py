#!/usr/bin/env python3
"""
Check Echoes API Configuration
"""

import sys
import os

# Add atmosphere root to path
atmosphere_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, atmosphere_root)

try:
    from Echoes.api.config import get_config
    
    config = get_config()
    
    print("🔍 Echoes API Configuration Analysis")
    print("=" * 50)
    print(f"API Key Required: {config.security.api_key_required}")
    print(f"Rate Limiting: {config.security.rate_limit_requests} req/{config.security.rate_limit_window}s")
    print(f"Timeout: {config.api.request_timeout}s")
    print(f"OpenAI API Key: {'Set' if config.openai_api_key else 'Not Set'}")
    
    print("\n🔧 Middleware Status:")
    auth_status = "ENABLED ⚠️" if config.security.api_key_required else "DISABLED ✅"
    rate_status = "ENABLED ⚠️" if config.security.rate_limit_requests > 0 else "DISABLED ✅"
    timeout_status = "ENABLED ⚠️" if config.api.request_timeout > 0 else "DISABLED ✅"
    
    print(f"  Authentication: {auth_status}")
    print(f"  Rate Limiting: {rate_status}")
    print(f"  Timeout: {timeout_status}")
    print(f"  CORS: ENABLED ✅")
    print(f"  Logging: ENABLED ✅")
    
    print("\n📊 Interference Assessment:")
    if config.security.api_key_required:
        print("❌ Authentication middleware may interfere with direct API calls")
        print("   • Requires API key for all requests except health/docs")
        print("   • May block direct OpenAI API communication")
    else:
        print("✅ Authentication middleware disabled - no interference")
    
    if config.security.rate_limit_requests > 0:
        print("⚠️ Rate limiting may affect concurrent requests")
        print(f"   • Limited to {config.security.rate_limit_requests} requests per {config.security.rate_limit_window}s")
    else:
        print("✅ No rate limiting - unrestricted access")
    
    if config.api.request_timeout > 0:
        print("⚠️ Timeout middleware may interrupt long requests")
        print(f"   • Requests timeout after {config.api.request_timeout}s")
    else:
        print("✅ No timeout restrictions")
    
    print("\n🎯 Recommendation:")
    if config.security.api_key_required:
        print("🔧 Set api_key_required = False to avoid interference")
    else:
        print("✅ Echoes middleware configuration is optimal for direct API access")
        
except Exception as e:
    print(f"❌ Failed to check Echoes configuration: {e}")
