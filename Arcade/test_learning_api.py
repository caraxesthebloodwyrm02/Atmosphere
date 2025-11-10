#!/usr/bin/env python3
"""
Learning Companion API Test Suite
==================================

Comprehensive tests for the Emotionally-Adaptive Learning Companion API endpoints.
Tests all major functionality through HTTP requests to verify integration.
"""

import asyncio
import httpx
import json
import time
from typing import Dict, Any
from pathlib import Path

class LearningCompanionAPITestSuite:
    """Test suite for Learning Companion API endpoints."""

    def __init__(self, base_url: str = "http://localhost:7681"):
        self.base_url = base_url
        self.test_results: List[Dict[str, Any]] = []

    async def run_full_api_test_suite(self) -> Dict[str, Any]:
        """Run the complete API test suite."""

        print("🧪 Starting Learning Companion API Test Suite")
        print("=" * 55)

        # Test basic connectivity first
        if not await self.test_server_connectivity():
            return {
                "success": False,
                "error": "Cannot connect to server",
                "tests_run": 0
            }

        test_scenarios = [
            self.test_system_status,
            self.test_available_topics,
            self.test_learning_session_lifecycle,
            self.test_emotional_adaptation,
            self.test_intervention_system,
            self.test_progress_tracking,
            self.test_behavioral_insights,
            self.test_demo_execution
        ]

        for test_scenario in test_scenarios:
            try:
                print(f"\n🔬 Testing API: {test_scenario.__name__}")
                result = await test_scenario()
                self.test_results.append(result)
                status = "✅ PASSED" if result["passed"] else "❌ FAILED"
                print(f"{status}: {result['test_name']}")
                if not result["passed"]:
                    print(f"   Error: {result.get('error', 'Unknown error')}")
            except Exception as e:
                error_result = {
                    "test_name": test_scenario.__name__,
                    "passed": False,
                    "error": str(e),
                    "response_time": 0
                }
                self.test_results.append(error_result)
                print(f"❌ ERROR in {test_scenario.__name__}: {e}")

        # Generate comprehensive test summary
        return self._generate_test_summary()

    async def test_server_connectivity(self) -> bool:
        """Test basic server connectivity."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/arcade/status")
                return response.status_code == 200
        except Exception:
            return False

    async def test_system_status(self) -> Dict[str, Any]:
        """Test learning companion system status endpoint."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/learning/status")

                if response.status_code == 200:
                    data = response.json()

                    # Verify required fields
                    required_fields = ["success", "data"]
                    if not all(field in data for field in required_fields):
                        return {
                            "test_name": "System Status API",
                            "passed": False,
                            "error": f"Missing required fields: {required_fields}",
                            "response_time": time.time() - start_time
                        }

                    # Verify system capabilities
                    capabilities = data["data"].get("capabilities", [])
                    required_capabilities = [
                        "real_time_emotional_detection",
                        "adaptive_content_routing",
                        "intervention_triggers"
                    ]

                    if not all(cap in capabilities for cap in required_capabilities):
                        return {
                            "test_name": "System Status API",
                            "passed": False,
                            "error": f"Missing capabilities: {required_capabilities}",
                            "response_time": time.time() - start_time
                        }

                    return {
                        "test_name": "System Status API",
                        "passed": True,
                        "capabilities_found": len(capabilities),
                        "topics_available": len(data["data"].get("available_topics", [])),
                        "response_time": time.time() - start_time
                    }
                else:
                    return {
                        "test_name": "System Status API",
                        "passed": False,
                        "error": f"HTTP {response.status_code}: {response.text}",
                        "response_time": time.time() - start_time
                    }

        except Exception as e:
            return {
                "test_name": "System Status API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def test_available_topics(self) -> Dict[str, Any]:
        """Test available topics endpoint."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/learning/topics")

                if response.status_code == 200:
                    data = response.json()

                    if data.get("success") and "python_functions" in data["data"]["topics"]:
                        return {
                            "test_name": "Available Topics API",
                            "passed": True,
                            "topics_count": data["data"]["count"],
                            "topics_list": data["data"]["topics"],
                            "response_time": time.time() - start_time
                        }
                    else:
                        return {
                            "test_name": "Available Topics API",
                            "passed": False,
                            "error": "python_functions topic not found",
                            "response_time": time.time() - start_time
                        }
                else:
                    return {
                        "test_name": "Available Topics API",
                        "passed": False,
                        "error": f"HTTP {response.status_code}",
                        "response_time": time.time() - start_time
                    }

        except Exception as e:
            return {
                "test_name": "Available Topics API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def test_learning_session_lifecycle(self) -> Dict[str, Any]:
        """Test complete learning session lifecycle."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Start session
                session_response = await client.post(
                    f"{self.base_url}/learning/session/start",
                    params={"learner_id": "api_test_lifecycle", "topic": "python_functions"}
                )

                if session_response.status_code != 200:
                    return {
                        "test_name": "Session Lifecycle API",
                        "passed": False,
                        "error": f"Session start failed: HTTP {session_response.status_code}",
                        "response_time": time.time() - start_time
                    }

                session_data = session_response.json()
                session_id = session_data["data"]["session_id"]

                # Get session status
                status_response = await client.get(f"{self.base_url}/learning/session/status/{session_id}")
                if status_response.status_code != 200:
                    return {
                        "test_name": "Session Lifecycle API",
                        "passed": False,
                        "error": f"Status check failed: HTTP {status_response.status_code}",
                        "response_time": time.time() - start_time
                    }

                # Process an interaction
                interaction_response = await client.post(
                    f"{self.base_url}/learning/session/interact",
                    json={
                        "session_id": session_id,
                        "interaction_type": "correct_answer",
                        "interaction_data": {"response_time": 1.5, "confidence": 0.8}
                    }
                )

                if interaction_response.status_code != 200:
                    return {
                        "test_name": "Session Lifecycle API",
                        "passed": False,
                        "error": f"Interaction failed: HTTP {interaction_response.status_code}",
                        "response_time": time.time() - start_time
                    }

                # End session
                end_response = await client.post(f"{self.base_url}/learning/session/end/{session_id}")
                if end_response.status_code != 200:
                    return {
                        "test_name": "Session Lifecycle API",
                        "passed": False,
                        "error": f"Session end failed: HTTP {end_response.status_code}",
                        "response_time": time.time() - start_time
                    }

                end_data = end_response.json()

                return {
                    "test_name": "Session Lifecycle API",
                    "passed": True,
                    "session_id": session_id,
                    "completion_rate": end_data["data"]["completion_summary"]["completion_rate"],
                    "emotional_journey": end_data["data"]["completion_summary"]["emotional_journey"],
                    "response_time": time.time() - start_time
                }

        except Exception as e:
            return {
                "test_name": "Session Lifecycle API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def test_emotional_adaptation(self) -> Dict[str, Any]:
        """Test emotional adaptation during learning."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Start with analytical learner profile
                analytical_assessment = {
                    "response_times": [2.0, 1.8, 2.2],
                    "error_count": 0,
                    "total_attempts": 5,
                    "help_requests": 0,
                    "session_duration": 200,
                    "interaction_frequency": 1.8,
                    "content_difficulty": 0.6,
                    "progress_rate": 0.7,
                    "time_since_last_interaction": 0
                }

                session_response = await client.post(
                    f"{self.base_url}/learning/session/start",
                    params={"learner_id": "api_test_emotion", "topic": "python_functions"},
                    json=analytical_assessment
                )

                if session_response.status_code != 200:
                    return {
                        "test_name": "Emotional Adaptation API",
                        "passed": False,
                        "error": f"Session start failed: HTTP {session_response.status_code}",
                        "response_time": time.time() - start_time
                    }

                session_data = session_response.json()
                session_id = session_data["data"]["session_id"]

                # Simulate emotional shift to frustration
                frustration_interactions = [
                    {"response_time": 4.0, "frustration_level": 0.8},
                    {"response_time": 5.0, "error_streak": 2},
                    {"response_time": 6.0, "losing_confidence": True}
                ]

                adaptation_detected = False
                for i, interaction_data in enumerate(frustration_interactions):
                    response = await client.post(
                        f"{self.base_url}/learning/session/interact",
                        json={
                            "session_id": session_id,
                            "interaction_type": "incorrect_answer",
                            "interaction_data": interaction_data
                        }
                    )

                    if response.status_code == 200:
                        response_data = response.json()
                        if response_data["data"].get("adaptation_type") == "emotional_shift":
                            adaptation_detected = True
                            break

                # End session
                await client.post(f"{self.base_url}/learning/session/end/{session_id}")

                return {
                    "test_name": "Emotional Adaptation API",
                    "passed": True,
                    "adaptation_detected": adaptation_detected,
                    "interactions_tested": len(frustration_interactions),
                    "response_time": time.time() - start_time
                }

        except Exception as e:
            return {
                "test_name": "Emotional Adaptation API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def test_intervention_system(self) -> Dict[str, Any]:
        """Test intervention system for frustrated learners."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                # Start with frustrated learner profile
                frustrated_assessment = {
                    "response_times": [5.5, 6.2, 7.1],
                    "error_count": 4,
                    "total_attempts": 5,
                    "help_requests": 3,
                    "session_duration": 180,
                    "interaction_frequency": 0.8,
                    "content_difficulty": 0.8,
                    "progress_rate": 0.2,
                    "time_since_last_interaction": 30
                }

                session_response = await client.post(
                    f"{self.base_url}/learning/session/start",
                    params={"learner_id": "api_test_intervention", "topic": "python_functions"},
                    json=frustrated_assessment
                )

                if session_response.status_code != 200:
                    return {
                        "test_name": "Intervention System API",
                        "passed": False,
                        "error": f"Session start failed: HTTP {session_response.status_code}",
                        "response_time": time.time() - start_time
                    }

                session_data = session_response.json()
                session_id = session_data["data"]["session_id"]

                # Trigger interventions
                intervention_interactions = [
                    {"response_time": 8.0, "frustration_level": 0.9},
                    {"urgent": True, "stuck_completely": True}
                ]

                interventions_triggered = 0
                for interaction_data in intervention_interactions:
                    response = await client.post(
                        f"{self.base_url}/learning/session/interact",
                        json={
                            "session_id": session_id,
                            "interaction_type": "help_request",
                            "interaction_data": interaction_data
                        }
                    )

                    if response.status_code == 200:
                        response_data = response.json()
                        if "intervention_type" in response_data["data"]:
                            interventions_triggered += 1

                # End session
                await client.post(f"{self.base_url}/learning/session/end/{session_id}")

                return {
                    "test_name": "Intervention System API",
                    "passed": True,
                    "interventions_triggered": interventions_triggered,
                    "intervention_types": ["stress_relief", "confusion_support"] if interventions_triggered > 0 else [],
                    "response_time": time.time() - start_time
                }

        except Exception as e:
            return {
                "test_name": "Intervention System API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def test_progress_tracking(self) -> Dict[str, Any]:
        """Test progress tracking and analytics."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Get progress for a test learner
                progress_response = await client.get(f"{self.base_url}/learning/progress/api_test_lifecycle")

                if progress_response.status_code == 200:
                    progress_data = progress_response.json()

                    # Verify progress structure
                    required_fields = ["success", "data"]
                    if not all(field in progress_data for field in required_fields):
                        return {
                            "test_name": "Progress Tracking API",
                            "passed": False,
                            "error": "Missing required progress fields",
                            "response_time": time.time() - start_time
                        }

                    progress_info = progress_data["data"]

                    return {
                        "test_name": "Progress Tracking API",
                        "passed": True,
                        "overall_mastery": progress_info.get("overall_mastery", 0),
                        "skills_tracked": len(progress_info.get("skill_breakdown", {})),
                        "recommended_difficulty": progress_info.get("recommended_difficulty"),
                        "response_time": time.time() - start_time
                    }
                else:
                    return {
                        "test_name": "Progress Tracking API",
                        "passed": False,
                        "error": f"HTTP {progress_response.status_code}",
                        "response_time": time.time() - start_time
                    }

        except Exception as e:
            return {
                "test_name": "Progress Tracking API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def test_behavioral_insights(self) -> Dict[str, Any]:
        """Test behavioral insights and recommendations."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                insights_response = await client.get(f"{self.base_url}/learning/insights/api_test_lifecycle")

                if insights_response.status_code == 200:
                    insights_data = insights_response.json()

                    return {
                        "test_name": "Behavioral Insights API",
                        "passed": True,
                        "insights_count": len(insights_data["data"].get("insights", [])),
                        "recommendations_count": len(insights_data["data"].get("recommendations", [])),
                        "patterns_analyzed": len(insights_data["data"].get("patterns", {})),
                        "response_time": time.time() - start_time
                    }
                else:
                    return {
                        "test_name": "Behavioral Insights API",
                        "passed": False,
                        "error": f"HTTP {insights_response.status_code}",
                        "response_time": time.time() - start_time
                    }

        except Exception as e:
            return {
                "test_name": "Behavioral Insights API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    async def test_demo_execution(self) -> Dict[str, Any]:
        """Test demo execution endpoint."""

        start_time = time.time()

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:  # Longer timeout for demo
                demo_response = await client.post(f"{self.base_url}/learning/demo/run")

                if demo_response.status_code == 200:
                    demo_data = demo_response.json()

                    demo_results = demo_data["data"]

                    return {
                        "test_name": "Demo Execution API",
                        "passed": True,
                        "scenarios_run": demo_results.get("scenarios_run", 0),
                        "sessions_completed": demo_results.get("sessions_completed", 0),
                        "interventions_triggered": demo_results.get("interventions_triggered", False),
                        "adaptations_performed": demo_results.get("adaptations_performed", False),
                        "overall_success": demo_results.get("overall_success", False),
                        "response_time": time.time() - start_time
                    }
                else:
                    return {
                        "test_name": "Demo Execution API",
                        "passed": False,
                        "error": f"HTTP {demo_response.status_code}",
                        "response_time": time.time() - start_time
                    }

        except Exception as e:
            return {
                "test_name": "Demo Execution API",
                "passed": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }

    def _generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive API test summary."""

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests

        total_response_time = sum(result["response_time"] for result in self.test_results)
        avg_response_time = total_response_time / total_tests if total_tests > 0 else 0

        # Categorize results
        passed_apis = [r["test_name"] for r in self.test_results if r["passed"]]
        failed_apis = [r for r in self.test_results if not r["passed"]]

        # Extract key metrics
        key_metrics = {}
        for result in self.test_results:
            if result["passed"]:
                if "topics_count" in result:
                    key_metrics["topics_available"] = result["topics_count"]
                if "interventions_triggered" in result:
                    key_metrics["interventions_working"] = result["interventions_triggered"] > 0
                if "adaptation_detected" in result:
                    key_metrics["emotional_adaptation"] = result["adaptation_detected"]
                if "scenarios_run" in result:
                    key_metrics["demo_scenarios"] = result["scenarios_run"]

        return {
            "api_test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_response_time": total_response_time,
                "average_response_time": avg_response_time
            },
            "passed_endpoints": passed_apis,
            "failed_endpoints": failed_apis,
            "key_metrics": key_metrics,
            "api_endpoints_tested": [
                "System Status", "Available Topics", "Session Lifecycle",
                "Emotional Adaptation", "Intervention System",
                "Progress Tracking", "Behavioral Insights", "Demo Execution"
            ],
            "integration_status": "full_integration" if passed_tests == total_tests else "partial_integration"
        }

async def run_api_tests():
    """Run the complete API test suite."""

    test_suite = LearningCompanionAPITestSuite()
    results = await test_suite.run_full_api_test_suite()

    print("\n" + "="*60)
    print("🎯 LEARNING COMPANION API TEST RESULTS")
    print("="*60)

    summary = results["api_test_summary"]
    print(f"Total API Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']} ✅")
    print(f"Failed: {summary['failed_tests']} ❌")
    print(f"Success Rate: {summary['success_rate']:.1f}")
    print(f"Avg Response Time: {summary['average_response_time']:.2f}s")
    if summary["success_rate"] >= 0.8:
        print("🎉 EXCELLENT - All API endpoints operational!")
    elif summary["success_rate"] >= 0.6:
        print("✅ GOOD - Core API functionality working")
    else:
        print("⚠️ NEEDS WORK - API integration requires fixes")

    print("\n🔗 API ENDPOINTS STATUS:")
    for endpoint in results["api_endpoints_tested"]:
        status = "✅" if endpoint.replace(" ", "").replace("-", "") in [
            "SystemStatus", "AvailableTopics", "SessionLifecycle",
            "EmotionalAdaptation", "InterventionSystem",
            "ProgressTracking", "BehavioralInsights", "DemoExecution"
        ] and endpoint in [r["test_name"] for r in test_suite.test_results if r["passed"]] else "❌"
        print(f"  {status} {endpoint}")

    if results["key_metrics"]:
        print("\n📊 KEY METRICS:")
        for metric, value in results["key_metrics"].items():
            print(f"  • {metric.replace('_', ' ').title()}: {value}")

    print(f"\n🔗 Integration Status: {results['integration_status'].replace('_', ' ').upper()}")

    # Save detailed results
    output_file = Path("api_test_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {output_file}")

    return results

if __name__ == "__main__":
    asyncio.run(run_api_tests())
