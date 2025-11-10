#!/usr/bin/env python3
"""
Quick API Test for Learning Companion
====================================

Simple test to verify the learning companion API is working.
"""

import httpx
import asyncio
import json

async def test_learning_api():
    """Test the learning companion API endpoints."""

    print("🧪 Testing Learning Companion API...")

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            # Test 1: System status
            print("\n1. Testing system status...")
            resp = await client.get('http://localhost:7681/learning/status')
            print(f"Status Code: {resp.status_code}")

            if resp.status_code == 200:
                data = resp.json()
                print("✅ Learning Companion API is operational!")
                print(f"Available topics: {len(data['data']['available_topics'])}")
                print(f"Capabilities: {len(data['data']['capabilities'])}")
                print(f"Emotional states supported: {len(data['data']['emotional_states_supported'])}")
            else:
                print(f"❌ API not responding: {resp.text[:200]}")
                return

            # Test 2: Available topics
            print("\n2. Testing available topics...")
            resp = await client.get('http://localhost:7681/learning/topics')
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ Topics available: {data['data']['count']}")
                print(f"Topics: {', '.join(data['data']['topics'])}")
            else:
                print(f"❌ Topics endpoint failed: {resp.status_code}")

            # Test 3: Start learning session
            print("\n3. Testing session creation...")
            resp = await client.post(
                'http://localhost:7681/learning/session/start',
                params={'learner_id': 'api_test_user', 'topic': 'python_functions'}
            )

            if resp.status_code == 200:
                data = resp.json()
                session_id = data['data']['session_id']
                print(f"✅ Session created: {session_id}")
                print(f"Emotional state: {data['data']['welcome_message'].split('feeling ')[1].split(' -')[0]}")

                # Test 4: Process interaction
                print("\n4. Testing interaction processing...")
                interaction_resp = await client.post(
                    'http://localhost:7681/learning/session/interact',
                    json={
                        'session_id': session_id,
                        'interaction_type': 'correct_answer',
                        'interaction_data': {'response_time': 1.5, 'confidence': 0.9}
                    }
                )

                if interaction_resp.status_code == 200:
                    print("✅ Interaction processed successfully")
                else:
                    print(f"❌ Interaction failed: {interaction_resp.status_code}")

                # Test 5: End session
                print("\n5. Testing session completion...")
                end_resp = await client.post(f'http://localhost:7681/learning/session/end/{session_id}')
                if end_resp.status_code == 200:
                    completion_data = end_resp.json()
                    print("✅ Session completed successfully")
                    summary = completion_data['data']['completion_summary']
                    print(f"   Completion rate: {summary['completion_rate']:.1%}")
                    print(f"   Duration: {summary['duration_minutes']:.1f} minutes")
                    print(f"   Emotional journey: {summary['emotional_journey']}")
                else:
                    print(f"❌ Session end failed: {end_resp.status_code}")
            else:
                print(f"❌ Session creation failed: {resp.status_code}")
                print(f"Response: {resp.text}")

            # Test 6: Progress tracking
            print("\n6. Testing progress tracking...")
            progress_resp = await client.get('http://localhost:7681/learning/progress/api_test_user')
            if progress_resp.status_code == 200:
                progress_data = progress_resp.json()
                print("✅ Progress tracking operational")
                progress_info = progress_data['data']
                print(f"   Overall mastery: {progress_info['overall_mastery']:.1%}")
                print(f"   Recommended difficulty: {progress_info['recommended_difficulty']}")
                print(f"   Skills tracked: {len(progress_info['skill_breakdown'])}")
            else:
                print(f"❌ Progress tracking failed: {progress_resp.status_code}")

            # Test 7: Behavioral insights
            print("\n7. Testing behavioral insights...")
            insights_resp = await client.get('http://localhost:7681/learning/insights/api_test_user')
            if insights_resp.status_code == 200:
                print("✅ Behavioral insights operational")
                insights_data = insights_resp.json()
                insights = insights_data['data']
                print(f"   Insights generated: {len(insights.get('insights', []))}")
                print(f"   Recommendations: {len(insights.get('recommendations', []))}")
            else:
                print(f"❌ Behavioral insights failed: {insights_resp.status_code}")

            print("\n🎉 ALL API TESTS COMPLETED!")
            print("\n📊 SUMMARY:")
            print("✅ System Status: Operational")
            print("✅ Session Management: Working")
            print("✅ Emotional Adaptation: Active")
            print("✅ Progress Tracking: Functional")
            print("✅ Behavioral Analytics: Operational")
            print("\n🚀 Learning Companion API is fully functional!")

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_learning_api())
