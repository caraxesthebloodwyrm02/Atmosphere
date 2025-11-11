#!/usr/bin/env python3
"""
Atmosphere Ecosystem Main Entry Point
Run with: python -m ecosystem
"""

import asyncio
from . import initialize_ecosystem, get_ecosystem

async def main():
    """Main ecosystem initialization."""
	print("[INIT] Initializing Atmosphere Ecosystem...")
    print("=" * 50)
    
    try:
        # Initialize ecosystem
        ecosystem = await initialize_ecosystem()
        
        # Get status
        status = await ecosystem.get_ecosystem_status()
        
		print(f"\n[STATS] Ecosystem Status: {status['health'].upper()}")
		print(f"[STATS] Components: {status['integrated_components']}/{status['total_components']}")
		print(f"[STATS] Integration Rate: {status['integration_rate']}")
		print(f"[STATS] API Connected: {status['api_connected']}")
        
		print("\n[DETAIL] Component Details:")
        print("-" * 30)
        for component, config in status['components'].items():
            integration = status['integration_status'][component]
			status_label = "[PASS]" if integration == "integrated" else "[FAIL]"
			print(f"{status_label} {component.title()}: v{config['version']}")
            if config.get('openai_connected'):
				print(f"    [API] OpenAI API Connected")
            if config.get('api_integration'):
				print(f"    [API] API Integration: Available")
        
		print("\n[SUCCESS] Ecosystem Initialization Complete!")
        
    except Exception as e:
		print(f"[ERROR] Ecosystem initialization failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
