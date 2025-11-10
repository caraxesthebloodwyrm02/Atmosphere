#!/usr/bin/env python3
"""
Atmosphere Ecosystem Main Entry Point
Run with: python -m ecosystem
"""

import asyncio
from . import initialize_ecosystem, get_ecosystem

async def main():
    """Main ecosystem initialization."""
    print("🌍 Initializing Atmosphere Ecosystem...")
    print("=" * 50)
    
    try:
        # Initialize ecosystem
        ecosystem = await initialize_ecosystem()
        
        # Get status
        status = await ecosystem.get_ecosystem_status()
        
        print(f"\n📊 Ecosystem Status: {status['health'].upper()}")
        print(f"📦 Components: {status['integrated_components']}/{status['total_components']}")
        print(f"📈 Integration Rate: {status['integration_rate']}")
        print(f"🔌 API Connected: {status['api_connected']}")
        
        print("\n📋 Component Details:")
        print("-" * 30)
        for component, config in status['components'].items():
            integration = status['integration_status'][component]
            status_icon = "✅" if integration == "integrated" else "❌"
            print(f"{status_icon} {component.title()}: v{config['version']}")
            if config.get('openai_connected'):
                print(f"    🔌 OpenAI API Connected")
            if config.get('api_integration'):
                print(f"    🔗 API Integration: Available")
        
        print("\n🎉 Ecosystem Initialization Complete!")
        
    except Exception as e:
        print(f"❌ Ecosystem initialization failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
