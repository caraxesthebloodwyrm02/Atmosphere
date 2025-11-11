#!/usr/bin/env python3
"""
Atmosphere Ecosystem Performance & Load Testing
==============================================

Comprehensive performance testing and load analysis for the Atmosphere ecosystem,
testing system behavior under various stress conditions, concurrency levels,
and scalability requirements.
"""

import asyncio
import aiohttp
import json
import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any, Tuple
import requests
from pathlib import Path
import sys

# Add the Arcade directory to the path
sys.path.insert(0, str(Path(__file__).parent))

class AtmosphereLoadTester:
    """Load testing framework for Atmosphere ecosystem."""

    def __init__(self, base_url: str = "http://localhost:7681"):
        self.base_url = base_url
        self.session = None
        self.results = []

    async def setup(self):
        """Setup test environment."""
        self.session = aiohttp.ClientSession()

    async def teardown(self):
        """Cleanup test environment."""
        if self.session:
            await self.session.close()

    def record_result(self, test_name: str, metrics: Dict[str, Any]):
        """Record test results."""
        result = {
            "test_name": test_name,
            "timestamp": time.time(),
            "metrics": metrics
        }
        self.results.append(result)

    async def run_performance_tests(self):
        """Run comprehensive performance tests."""

        print("🏃‍♂️ Starting Atmosphere Ecosystem Performance Tests")
        print("=" * 60)

        await self.setup()

        try:
            # Basic connectivity test
            await self.test_basic_connectivity()

            # API endpoint performance tests
            await self.test_api_endpoints_performance()

            # Concurrent user simulation
            await self.test_concurrent_users()

            # AI processing load tests
            await self.test_ai_processing_load()

            # Ecosystem orchestration stress test
            await self.test_ecosystem_orchestration_stress()

            # Memory and resource usage tests
            await self.test_memory_resource_usage()

            # Generate performance report
            self.generate_performance_report()

        finally:
            await self.teardown()

    async def test_basic_connectivity(self):
        """Test basic system connectivity and response times."""

        print("🔗 Testing Basic Connectivity...")

        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/arcade/status") as response:
                end_time = time.time()

                if response.status == 200:
                    response_time = (end_time - start_time) * 1000  # ms
                    self.record_result("basic_connectivity", {
                        "response_time_ms": response_time,
                        "status_code": response.status,
                        "success": True
                    })
                    print(".1f"                else:
                    self.record_result("basic_connectivity", {
                        "status_code": response.status,
                        "success": False,
                        "error": f"HTTP {response.status}"
                    })
                    print(f"❌ Connectivity failed: HTTP {response.status}")

        except Exception as e:
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            self.record_result("basic_connectivity", {
                "response_time_ms": response_time,
                "success": False,
                "error": str(e)
            })
            print(f"❌ Connectivity error: {e}")

    async def test_api_endpoints_performance(self):
        """Test performance of key API endpoints."""

        print("🎯 Testing API Endpoints Performance...")

        endpoints = [
            ("GET", "/arcade/status", "system_status"),
            ("GET", "/atmosphere/ecosystem/health", "ecosystem_health"),
            ("GET", "/architecture/dashboard", "executive_dashboard"),
            ("GET", "/io/zones", "design_zones"),
            ("GET", "/atmosphere/components", "ecosystem_components")
        ]

        for method, endpoint, test_name in endpoints:
            response_times = []

            # Test each endpoint 5 times
            for i in range(5):
                start_time = time.time()
                try:
                    if method == "GET":
                        async with self.session.get(f"{self.base_url}{endpoint}") as response:
                            end_time = time.time()
                            if response.status == 200:
                                response_times.append((end_time - start_time) * 1000)
                            else:
                                response_times.append(float('inf'))  # Mark as failed
                except Exception:
                    response_times.append(float('inf'))

                await asyncio.sleep(0.1)  # Small delay between requests

            # Calculate metrics
            valid_times = [t for t in response_times if t != float('inf')]
            if valid_times:
                avg_time = statistics.mean(valid_times)
                min_time = min(valid_times)
                max_time = max(valid_times)
                success_rate = len(valid_times) / len(response_times)

                self.record_result(f"api_performance_{test_name}", {
                    "average_response_time_ms": avg_time,
                    "min_response_time_ms": min_time,
                    "max_response_time_ms": max_time,
                    "success_rate": success_rate,
                    "requests_total": len(response_times),
                    "requests_successful": len(valid_times)
                })

                print(".1f"            else:
                self.record_result(f"api_performance_{test_name}", {
                    "success_rate": 0.0,
                    "error": "All requests failed"
                })
                print(f"❌ {test_name}: All requests failed")

    async def test_concurrent_users(self):
        """Test system behavior under concurrent user load."""

        print("👥 Testing Concurrent User Load...")

        # Test with different concurrency levels
        concurrency_levels = [10, 25, 50, 100]

        for concurrency in concurrency_levels:
            print(f"   Testing {concurrency} concurrent users...")

            start_time = time.time()

            # Create concurrent requests
            tasks = []
            for i in range(concurrency):
                # Mix of different request types
                if i % 4 == 0:
                    tasks.append(self.make_concurrent_request("GET", "/atmosphere/ecosystem/health"))
                elif i % 4 == 1:
                    tasks.append(self.make_concurrent_request("GET", "/architecture/dashboard"))
                elif i % 4 == 2:
                    tasks.append(self.make_concurrent_request("GET", "/io/zones"))
                else:
                    tasks.append(self.make_concurrent_request("GET", "/arcade/status"))

            # Execute concurrent requests
            results = await asyncio.gather(*tasks, return_exceptions=True)

            end_time = time.time()
            total_time = end_time - start_time

            # Analyze results
            successful_requests = len([r for r in results if not isinstance(r, Exception) and r.get('status') == 200])
            failed_requests = len([r for r in results if isinstance(r, Exception) or r.get('status') != 200])
            success_rate = successful_requests / concurrency

            response_times = [r.get('response_time', 0) for r in results if not isinstance(r, Exception)]

            if response_times:
                avg_response_time = statistics.mean(response_times)
                p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
            else:
                avg_response_time = 0
                p95_response_time = 0

            self.record_result(f"concurrent_users_{concurrency}", {
                "concurrency_level": concurrency,
                "total_requests": concurrency,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": success_rate,
                "total_time_seconds": total_time,
                "avg_response_time_ms": avg_response_time,
                "p95_response_time_ms": p95_response_time,
                "requests_per_second": concurrency / total_time if total_time > 0 else 0
            })

            status = "🟢" if success_rate >= 0.95 else "🟡" if success_rate >= 0.85 else "🔴"
            print(".1f"    async def make_concurrent_request(self, method: str, endpoint: str) -> Dict[str, Any]:
        """Make a single concurrent request for load testing."""

        start_time = time.time()
        try:
            if method == "GET":
                async with self.session.get(f"{self.base_url}{endpoint}") as response:
                    end_time = time.time()
                    return {
                        "status": response.status,
                        "response_time": (end_time - start_time) * 1000,
                        "endpoint": endpoint
                    }
        except Exception as e:
            end_time = time.time()
            return {
                "status": 0,
                "response_time": (end_time - start_time) * 1000,
                "error": str(e),
                "endpoint": endpoint
            }

    async def test_ai_processing_load(self):
        """Test AI processing under load."""

        print("🤖 Testing AI Processing Load...")

        # Test concurrent AI feedback processing
        concurrent_ai_requests = 20

        print(f"   Processing {concurrent_ai_requests} concurrent AI feedback requests...")

        start_time = time.time()

        tasks = []
        for i in range(concurrent_ai_requests):
            feedback_data = {
                "user_id": f"load_test_user_{i}",
                "content": f"AI load test feedback {i}: Testing system performance under AI processing load with complex analysis requirements",
                "feedback_type": "performance_test"
            }
            tasks.append(self.make_ai_feedback_request(feedback_data))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        successful_requests = len([r for r in results if not isinstance(r, Exception) and r.get('success')])
        success_rate = successful_requests / concurrent_ai_requests

        response_times = [r.get('response_time', 0) for r in results if not isinstance(r, Exception)]

        if response_times:
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18]
        else:
            avg_response_time = 0
            p95_response_time = 0

        self.record_result("ai_processing_load", {
            "concurrent_requests": concurrent_ai_requests,
            "successful_requests": successful_requests,
            "success_rate": success_rate,
            "total_time_seconds": total_time,
            "avg_response_time_ms": avg_response_time,
            "p95_response_time_ms": p95_response_time,
            "requests_per_second": concurrent_ai_requests / total_time if total_time > 0 else 0
        })

        status = "🟢" if success_rate >= 0.9 else "🟡" if success_rate >= 0.7 else "🔴"
        print(".1f"    async def make_ai_feedback_request(self, feedback_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make AI feedback processing request."""

        start_time = time.time()
        try:
            async with self.session.post(f"{self.base_url}/atmosphere/process-feedback", json=feedback_data) as response:
                end_time = time.time()
                return {
                    "success": response.status == 200,
                    "status": response.status,
                    "response_time": (end_time - start_time) * 1000
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": (end_time - start_time) * 1000,
                "error": str(e)
            }

    async def test_ecosystem_orchestration_stress(self):
        """Test ecosystem orchestration under stress."""

        print("🔄 Testing Ecosystem Orchestration Stress...")

        # Create complex orchestration scenario
        stress_operations = 15

        print(f"   Creating {stress_operations} simultaneous ecosystem operations...")

        start_time = time.time()

        tasks = []
        for i in range(stress_operations):
            if i % 5 == 0:
                # Feedback processing
                feedback_data = {
                    "user_id": f"stress_user_{i}",
                    "content": f"Complex orchestration stress test {i} requiring multi-component coordination",
                    "feedback_type": "system_stress_test"
                }
                tasks.append(self.make_ai_feedback_request(feedback_data))

            elif i % 5 == 1:
                # Design decision
                decision_data = {
                    "zone": "core_nexus",
                    "decision_type": "interface_optimization",
                    "context": {"stress_test": True, "load_level": "high"}
                }
                tasks.append(self.make_design_decision_request(decision_data))

            elif i % 5 == 2:
                # Communication bridge
                bridge_data = {
                    "gap_type": "coordination",
                    "source_component": "arcade",
                    "target_component": "routing"
                }
                tasks.append(self.make_bridge_request(bridge_data))

            elif i % 5 == 3:
                # IO analysis
                interaction_data = {
                    "interactions": [
                        {"component": "stress_test", "frequency": 10, "satisfaction": 0.8, "success": True}
                    ]
                }
                tasks.append(self.make_io_analysis_request(f"stress_user_{i}", interaction_data))

            else:
                # Ecosystem health check
                tasks.append(self.make_health_check_request())

        results = await asyncio.gather(*tasks, return_exceptions=True)

        end_time = time.time()
        total_time = end_time - start_time

        successful_operations = len([r for r in results if not isinstance(r, Exception) and r.get('success')])
        success_rate = successful_operations / stress_operations

        self.record_result("ecosystem_orchestration_stress", {
            "total_operations": stress_operations,
            "successful_operations": successful_operations,
            "success_rate": success_rate,
            "total_time_seconds": total_time,
            "operations_per_second": stress_operations / total_time if total_time > 0 else 0
        })

        status = "🟢" if success_rate >= 0.85 else "🟡" if success_rate >= 0.7 else "🔴"
        print(".1f"    async def make_design_decision_request(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make design decision request."""

        start_time = time.time()
        try:
            async with self.session.post(f"{self.base_url}/io/decision", json=decision_data) as response:
                end_time = time.time()
                return {
                    "success": response.status == 200,
                    "status": response.status,
                    "response_time": (end_time - start_time) * 1000
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": (end_time - start_time) * 1000,
                "error": str(e)
            }

    async def make_bridge_request(self, bridge_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make communication bridge request."""

        start_time = time.time()
        try:
            async with self.session.post(f"{self.base_url}/atmosphere/bridge/create", json=bridge_data) as response:
                end_time = time.time()
                return {
                    "success": response.status == 200,
                    "status": response.status,
                    "response_time": (end_time - start_time) * 1000
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": (end_time - start_time) * 1000,
                "error": str(e)
            }

    async def make_io_analysis_request(self, user_id: str, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make IO analysis request."""

        start_time = time.time()
        try:
            async with self.session.post(f"{self.base_url}/io/analyze/{user_id}", json=interaction_data) as response:
                end_time = time.time()
                return {
                    "success": response.status == 200,
                    "status": response.status,
                    "response_time": (end_time - start_time) * 1000
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": (end_time - start_time) * 1000,
                "error": str(e)
            }

    async def make_health_check_request(self) -> Dict[str, Any]:
        """Make ecosystem health check request."""

        start_time = time.time()
        try:
            async with self.session.get(f"{self.base_url}/atmosphere/ecosystem/health") as response:
                end_time = time.time()
                return {
                    "success": response.status == 200,
                    "status": response.status,
                    "response_time": (end_time - start_time) * 1000
                }
        except Exception as e:
            end_time = time.time()
            return {
                "success": False,
                "response_time": (end_time - start_time) * 1000,
                "error": str(e)
            }

    async def test_memory_resource_usage(self):
        """Test memory and resource usage patterns."""

        print("💾 Testing Memory & Resource Usage...")

        # Monitor system resources during load
        baseline_metrics = await self.get_system_metrics()

        # Generate load
        load_tasks = []
        for i in range(50):  # Moderate load
            feedback_data = {
                "user_id": f"resource_test_user_{i}",
                "content": f"Resource usage test {i}: Monitoring system performance under sustained load",
                "feedback_type": "resource_test"
            }
            load_tasks.append(self.make_ai_feedback_request(feedback_data))

        start_time = time.time()
        await asyncio.gather(*load_tasks, return_exceptions=True)
        end_time = time.time()

        peak_metrics = await self.get_system_metrics()

        # Calculate resource usage patterns
        cpu_increase = peak_metrics.get('cpu_percent', 0) - baseline_metrics.get('cpu_percent', 0)
        memory_increase = peak_metrics.get('memory_percent', 0) - baseline_metrics.get('memory_percent', 0)

        self.record_result("resource_usage_analysis", {
            "baseline_cpu_percent": baseline_metrics.get('cpu_percent', 0),
            "peak_cpu_percent": peak_metrics.get('cpu_percent', 0),
            "cpu_increase_percent": cpu_increase,
            "baseline_memory_percent": baseline_metrics.get('memory_percent', 0),
            "peak_memory_percent": peak_metrics.get('memory_percent', 0),
            "memory_increase_percent": memory_increase,
            "load_duration_seconds": end_time - start_time,
            "requests_processed": 50
        })

        print(".1f"    async def get_system_metrics(self) -> Dict[str, float]:
        """Get basic system metrics (simplified for demo)."""

        # In a real implementation, this would use psutil or similar
        # For demo, return simulated metrics
        return {
            "cpu_percent": 45.0 + (time.time() % 10),  # Simulated varying CPU
            "memory_percent": 60.0 + (time.time() % 5),  # Simulated varying memory
            "disk_usage_percent": 75.0,
            "network_connections": 150
        }

    def generate_performance_report(self):
        """Generate comprehensive performance report."""

        print("\n📊 Atmosphere Ecosystem Performance Report")
        print("=" * 60)

        # Basic connectivity results
        connectivity_results = [r for r in self.results if r["test_name"] == "basic_connectivity"]
        if connectivity_results:
            result = connectivity_results[0]
            metrics = result["metrics"]
            status = "🟢" if metrics.get("success") else "🔴"
            print(f"{status} Basic Connectivity: {metrics.get('response_time_ms', 0):.1f}ms")

        # API performance summary
        api_results = [r for r in self.results if r["test_name"].startswith("api_performance_")]
        if api_results:
            print(f"\n🎯 API Endpoints Performance ({len(api_results)} endpoints):")
            for result in api_results:
                metrics = result["metrics"]
                success_rate = metrics.get("success_rate", 0) * 100
                avg_time = metrics.get("average_response_time_ms", 0)
                status = "🟢" if success_rate >= 95 and avg_time < 500 else "🟡" if success_rate >= 85 else "🔴"
                endpoint_name = result["test_name"].replace("api_performance_", "")
                print(".1f"        # Concurrent user test summary
        concurrent_results = [r for r in self.results if r["test_name"].startswith("concurrent_users_")]
        if concurrent_results:
            print(f"\n👥 Concurrent User Performance:")
            for result in concurrent_results:
                metrics = result["metrics"]
                concurrency = metrics.get("concurrency_level", 0)
                success_rate = metrics.get("success_rate", 0) * 100
                rps = metrics.get("requests_per_second", 0)
                status = "🟢" if success_rate >= 95 else "🟡" if success_rate >= 85 else "🔴"
                print(".1f"        # AI processing load test
        ai_load_results = [r for r in self.results if r["test_name"] == "ai_processing_load"]
        if ai_load_results:
            result = ai_load_results[0]
            metrics = result["metrics"]
            success_rate = metrics.get("success_rate", 0) * 100
            rps = metrics.get("requests_per_second", 0)
            p95_time = metrics.get("p95_response_time_ms", 0)
            status = "🟢" if success_rate >= 90 and p95_time < 5000 else "🟡" if success_rate >= 75 else "🔴"
            print(f"\n🤖 AI Processing Load: {status} {success_rate:.1f}% success, {rps:.1f} RPS, P95: {p95_time:.1f}ms")

        # Ecosystem orchestration stress test
        orchestration_results = [r for r in self.results if r["test_name"] == "ecosystem_orchestration_stress"]
        if orchestration_results:
            result = orchestration_results[0]
            metrics = result["metrics"]
            success_rate = metrics.get("success_rate", 0) * 100
            ops_per_sec = metrics.get("operations_per_second", 0)
            status = "🟢" if success_rate >= 85 else "🟡" if success_rate >= 70 else "🔴"
            print(f"\n🔄 Ecosystem Orchestration: {status} {success_rate:.1f}% success, {ops_per_sec:.1f} ops/sec")

        # Resource usage analysis
        resource_results = [r for r in self.results if r["test_name"] == "resource_usage_analysis"]
        if resource_results:
            result = resource_results[0]
            metrics = result["metrics"]
            cpu_increase = metrics.get("cpu_increase_percent", 0)
            memory_increase = metrics.get("memory_increase_percent", 0)
            status = "🟢" if cpu_increase < 20 and memory_increase < 15 else "🟡" if cpu_increase < 35 else "🔴"
            print(f"\n💾 Resource Usage: {status} CPU +{cpu_increase:.1f}%, Memory +{memory_increase:.1f}% under load")

        # Performance recommendations
        print(f"\n💡 Performance Recommendations:")

        # Analyze results for recommendations
        all_success_rates = []
        all_response_times = []

        for result in self.results:
            metrics = result["metrics"]
            if "success_rate" in metrics:
                all_success_rates.append(metrics["success_rate"])
            if "average_response_time_ms" in metrics:
                all_response_times.append(metrics["average_response_time_ms"])
            if "p95_response_time_ms" in metrics:
                all_response_times.append(metrics["p95_response_time_ms"])

        avg_success_rate = statistics.mean(all_success_rates) if all_success_rates else 0
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0

        if avg_success_rate >= 0.95:
            print("   🏆 Excellent performance! System handles high concurrency well.")
        elif avg_success_rate >= 0.85:
            print("   ✅ Good performance. Consider optimizations for peak loads.")
        else:
            print("   ⚠️ Performance needs attention. Focus on stability and response times.")

        if avg_response_time < 1000:
            print("   ⚡ Fast response times. Excellent user experience.")
        elif avg_response_time < 3000:
            print("   🟡 Moderate response times. Consider caching optimizations.")
        else:
            print("   🐌 Slow response times. Implement performance optimizations.")

        print(f"\n🎯 Atmosphere Ecosystem Performance Testing Complete!")
        print(f"   📊 Tests Run: {len(self.results)}")
        print(f"   📈 Overall Success Rate: {avg_success_rate:.1f}%")
        print(f"   ⏱️  Average Response Time: {avg_response_time:.1f}ms")

async def main():
    """Main performance testing function."""

    print("🏃‍♂️ Atmosphere Ecosystem Performance & Load Testing")
    print("=" * 55)

    # Check if server is running
    tester = AtmosphereLoadTester()

    try:
        # Run performance tests
        await tester.run_performance_tests()

    except KeyboardInterrupt:
        print("\n⚠️  Testing interrupted by user")
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
    finally:
        print("\n🧹 Cleaning up test environment...")
        await tester.teardown()

    print("\n🎯 Atmosphere Ecosystem Performance Testing Complete!")
    print("\n🔬 Performance Testing Summary:")
    print("   • Basic connectivity and response times")
    print("   • API endpoint performance under load")
    print("   • Concurrent user handling capabilities")
    print("   • AI processing performance and scalability")
    print("   • Ecosystem orchestration stress testing")
    print("   • Memory and resource usage patterns")
    print("\n📊 Use the performance report above to optimize system performance!")

if __name__ == "__main__":
    asyncio.run(main())
