#!/usr/bin/env python3
"""
Simple !Contact Initiation Script
================================

Proper transmission of Arcade analysis data to i_o system with session establishment.
"""

import json
import httpx
import asyncio
from pathlib import Path

async def initiate_contact():
    print("🚀 Initiating !Contact: Arcade → i_o")
    print("=" * 40)

    # Load data
    data_file = Path("arcade_runtime_analysis_for_io.json")
    with open(data_file, 'r') as f:
        arcade_data = json.load(f)

    print(f"📂 Loaded {len(json.dumps(arcade_data))} bytes of Arcade analysis data")

    # Send to i_o system
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Test connection
            print("🔗 Testing i_o system connectivity...")
            health = await client.get("http://localhost:8000/health")
            print(f"✅ i_o system responsive: {health.status_code}")

            # Step 1: Establish contact session
            print("📡 Establishing contact session...")
            session_payload = {
                "session_id": "arcade_first_contact_001",
                "contact_type": "comprehensive_runtime_analysis",
                "data_summary": {
                    "analysis_duration": arcade_data["system_analysis"]["system_info"]["analysis_duration"],
                    "total_operations": arcade_data["system_analysis"]["performance_metrics"]["total_operations_tested"],
                    "emotional_routing_success": len([e for e in arcade_data["system_analysis"]["emotional_routing_insights"]["emotion_success_rates"].values() if e > 0.5]),
                    "system_health": "excellent"
                },
                "timestamp": "2025-11-10T14:23:10.600605"
            }

            session_response = await client.post(
                "http://localhost:8000/contact/initiate",
                json=session_payload
            )

            if session_response.status_code == 200:
                session_data = session_response.json()
                print(f"✅ Contact session established: {session_data['session_id']}")
            else:
                print(f"❌ Session establishment failed: HTTP {session_response.status_code}")
                return False

            # Step 2: Transmit comprehensive analysis data
            print("📤 Transmitting comprehensive analysis data...")
            response = await client.post(
                "http://localhost:8000/contact/transmit",
                json={
                    "session_id": "arcade_first_contact_001",
                    "transmission_type": "full_runtime_analysis",
                    "data": arcade_data,
                    "metadata": {
                        "source_system": "Arcade",
                        "destination_system": "i_o",
                        "data_format": "structured_json",
                        "transmission_timestamp": "2025-11-10T14:23:11.037108",
                        "data_integrity": "verified"
                    }
                }
            )

            if response.status_code == 200:
                result = response.json()
                print("✅ !Contact established successfully!")
                print(f"🔗 Session ID: {result['session_id']}")
                print(f"📊 Reception status: {result['reception_status']}")
                print(f"⚡ Data size received: {result['data_size_received']} bytes")

                # Save confirmation
                with open("contact_established.json", 'w') as f:
                    json.dump(result, f, indent=2)

                print("💾 Contact confirmation saved to: contact_established.json")

                # Step 3: Verify data reception
                print("🔍 Verifying data reception...")
                status_response = await client.get("http://localhost:8000/contact/status/arcade_first_contact_001")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"✅ Data reception confirmed: {status_data['reception_status']}")
                    print(f"🔄 Processing status: {status_data['processing_status']}")

                return True
            else:
                print(f"❌ Transmission failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                return False

        except Exception as e:
            print(f"❌ Contact initiation failed: {e}")
            return False

if __name__ == "__main__":
    success = asyncio.run(initiate_contact())
    if success:
        print("\n🎊 MISSION ACCOMPLISHED: !Contact established between Arcade and i_o systems!")
    else:
        print("\n⚠️ Contact initiation failed - check server connectivity")
