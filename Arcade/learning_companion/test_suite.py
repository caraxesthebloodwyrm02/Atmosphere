#!/usr/bin/env python3
"""
Comprehensive Test Suite for Emotionally-Adaptive Learning Companion
===================================================================

Test scenarios covering various emotional states, learning patterns, and edge cases
to validate the emotionally-adaptive learning system's functionality.
"""

import asyncio
import json
import time
from typing import Dict, List, Any
from pathlib import Path

from .emotionally_adaptive_learning_companion import EmotionallyAdaptiveLearningCompanion

class LearningCompanionTestSuite:
    """Comprehensive test suite for the emotionally-adaptive learning companion."""

    def __init__(self):
        self.companion = EmotionallyAdaptiveLearningCompanion()
        self.test_results: List[Dict[str, Any]] = []

    async def run_full_test_suite(self) -> Dict[str, Any]:
        """Run the complete test suite."""

        print("🧪 Starting Comprehensive Learning Companion Test Suite")
        print("=" * 60)

        test_scenarios = [
            self.test_exploratory_learning_scenario,
            self.test_analytical_learning_scenario,
            self.test_frustrated_learner_scenario,
            self.test_urgent_deadline_scenario,
            self.test_progressive_learning_scenario,
            self.test_emotional_shift_scenario,
            self.test_intervention_triggers_scenario,
            self.test_edge_cases_scenario
        ]

        for test_scenario in test_scenarios:
            try:
                print(f"\n🔬 Running {test_scenario.__name__}...")
                result = await test_scenario()
                self.test_results.append(result)
                status = "✅ PASSED" if result["passed"] else "❌ FAILED"
                print(f"{status}: {result['scenario']}")
            except Exception as e:
                error_result = {
                    "scenario": test_scenario.__name__,
                    "passed": False,
                    "error": str(e),
                    "duration": 0
                }
                self.test_results.append(error_result)
                print(f"❌ ERROR in {test_scenario.__name__}: {e}")

        # Generate test summary
        return self._generate_test_summary()

    async def test_exploratory_learning_scenario(self) -> Dict[str, Any]:
        """Test scenario for an exploratory learner."""

        start_time = time.time()
        scenario_name = "Exploratory Learning Scenario"

        try:
            # Simulate exploratory learner
            learner_id = "test_exploratory_001"
            topic = "python_functions"

            # Start session with exploratory emotional profile
            initial_assessment = {
                'response_times': [0.5, 0.8, 0.6],  # Quick responses
                'error_count': 1,
                'total_attempts': 5,
                'help_requests': 0,  # Independent exploration
                'session_duration': 120,
                'interaction_frequency': 2.5,  # High engagement
                'content_difficulty': 0.6,
                'progress_rate': 0.8,
                'time_since_last_interaction': 0
            }

            session_result = await self.companion.start_learning_session(
                learner_id, topic, initial_assessment
            )

            # Verify exploratory content selection
            content_type = session_result["initial_content"]["content_type"]
            assert content_type == "interactive_exercise", f"Expected interactive_exercise, got {content_type}"

            # Simulate successful exploratory interactions
            interactions = [
                ("correct_answer", {"response_time": 0.7, "confidence": 0.9}),
                ("help_request", {"topic": "function_parameters"}),
                ("module_completed", {"module_index": 0, "success_rate": 0.9})
            ]

            for interaction_type, interaction_data in interactions:
                response = await self.companion.process_interaction(
                    session_result["session_id"], interaction_type, interaction_data
                )

                if interaction_type == "module_completed":
                    assert "next_module" in response, "Should provide next module for exploratory learner"

            # End session
            completion_result = await self.companion.end_learning_session(session_result["session_id"])

            # Verify exploratory learning outcomes
            assert completion_result["completion_summary"]["emotional_journey"] in ["highly_engaged", "balanced"]
            assert completion_result["progress_report"]["performance_metrics"]["learning_efficiency"] > 1.0

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": "Exploratory learner correctly routed to interactive, discovery-based content"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def test_analytical_learning_scenario(self) -> Dict[str, Any]:
        """Test scenario for an analytical learner."""

        start_time = time.time()
        scenario_name = "Analytical Learning Scenario"

        try:
            learner_id = "test_analytical_001"
            topic = "python_functions"

            # Analytical learner profile
            initial_assessment = {
                'response_times': [2.1, 1.8, 2.3],  # Deliberate thinking
                'error_count': 0,
                'total_attempts': 5,
                'help_requests': 0,
                'session_duration': 300,  # Longer, methodical approach
                'interaction_frequency': 1.2,  # Steady pace
                'content_difficulty': 0.7,
                'progress_rate': 0.6,  # Methodical progress
                'time_since_last_interaction': 0
            }

            session_result = await self.companion.start_learning_session(
                learner_id, topic, initial_assessment
            )

            # Verify analytical content selection
            content_type = session_result["initial_content"]["content_type"]
            assert content_type in ["concept_explanation", "quiz_assessment"], f"Expected structured content, got {content_type}"

            # Simulate analytical learning pattern
            interactions = [
                ("correct_answer", {"response_time": 2.0, "methodical_approach": True}),
                ("correct_answer", {"response_time": 1.9, "deep_understanding": True}),
                ("module_completed", {"module_index": 0, "comprehensive_mastery": True})
            ]

            for interaction_type, interaction_data in interactions:
                response = await self.companion.process_interaction(
                    session_result["session_id"], interaction_type, interaction_data
                )

            completion_result = await self.companion.end_learning_session(session_result["session_id"])

            # Verify analytical learning outcomes
            assert completion_result["completion_summary"]["completion_rate"] > 0.8
            assert "methodical" in str(completion_result.get("behavioral_insights", {}))

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": "Analytical learner correctly routed to structured, concept-focused content"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def test_frustrated_learner_scenario(self) -> Dict[str, Any]:
        """Test scenario for a frustrated learner requiring intervention."""

        start_time = time.time()
        scenario_name = "Frustrated Learner Intervention Scenario"

        try:
            learner_id = "test_frustrated_001"
            topic = "python_functions"

            # Frustrated learner profile
            initial_assessment = {
                'response_times': [4.5, 5.2, 6.1],  # Very slow responses
                'error_count': 4,
                'total_attempts': 5,
                'help_requests': 3,  # Frequent help requests
                'session_duration': 180,
                'interaction_frequency': 0.8,  # Low engagement
                'content_difficulty': 0.8,
                'progress_rate': 0.2,  # Struggling
                'time_since_last_interaction': 30
            }

            session_result = await self.companion.start_learning_session(
                learner_id, topic, initial_assessment
            )

            # Simulate frustration-building interactions
            interactions = [
                ("incorrect_answer", {"response_time": 5.0, "frustration_level": 0.8}),
                ("incorrect_answer", {"response_time": 6.0, "error_streak": 2}),
                ("help_request", {"urgent": True, "topic": "function_syntax"})
            ]

            intervention_triggered = False
            for interaction_type, interaction_data in interactions:
                response = await self.companion.process_interaction(
                    session_result["session_id"], interaction_type, interaction_data
                )

                if "intervention_type" in response:
                    intervention_triggered = True
                    assert response["intervention_type"] in ["frustration_relief", "confusion_support"]

            # Verify intervention was triggered
            assert intervention_triggered, "Frustrated learner should trigger intervention"

            completion_result = await self.companion.end_learning_session(session_result["session_id"])

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": "Frustration detection and intervention system working correctly"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def test_urgent_deadline_scenario(self) -> Dict[str, Any]:
        """Test scenario for urgent learning with time pressure."""

        start_time = time.time()
        scenario_name = "Urgent Deadline Learning Scenario"

        try:
            learner_id = "test_urgent_001"
            topic = "python_functions"

            # Urgent learner profile
            initial_assessment = {
                'response_times': [0.3, 0.4, 0.2],  # Very fast responses
                'error_count': 2,
                'total_attempts': 5,
                'help_requests': 1,
                'session_duration': 45,  # Very short session
                'interaction_frequency': 4.0,  # High frequency
                'content_difficulty': 0.4,  # Easier content needed
                'progress_rate': 0.9,  # Fast progress
                'time_since_last_interaction': 0
            }

            session_result = await self.companion.start_learning_session(
                learner_id, topic, initial_assessment
            )

            # Verify urgent/time-sensitive content
            estimated_duration = session_result["initial_content"]["estimated_duration"]
            assert estimated_duration <= 15, f"Urgent learning should have short modules, got {estimated_duration}"

            # Simulate urgent learning pattern
            interactions = [
                ("correct_answer", {"response_time": 0.3, "quick_decision": True}),
                ("incorrect_answer", {"response_time": 0.2, "rushed": True}),
                ("module_completed", {"module_index": 0, "time_efficient": True})
            ]

            for interaction_type, interaction_data in interactions:
                response = await self.companion.process_interaction(
                    session_result["session_id"], interaction_type, interaction_data
                )

            completion_result = await self.companion.end_learning_session(session_result["session_id"])

            # Verify urgent learning outcomes
            assert completion_result["completion_summary"]["duration_minutes"] < 10
            assert completion_result["progress_report"]["performance_metrics"]["learning_efficiency"] > 2.0

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": "Urgent learning correctly adapts to time pressure with efficient, focused content"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def test_progressive_learning_scenario(self) -> Dict[str, Any]:
        """Test scenario showing progressive skill development."""

        start_time = time.time()
        scenario_name = "Progressive Learning Development Scenario"

        try:
            learner_id = "test_progressive_001"
            topic = "python_functions"

            # Start with beginner level
            initial_assessment = {
                'response_times': [3.0, 2.8, 3.2],
                'error_count': 2,
                'total_attempts': 4,
                'help_requests': 1,
                'session_duration': 240,
                'interaction_frequency': 1.5,
                'content_difficulty': 0.3,  # Beginner level
                'progress_rate': 0.5,
                'time_since_last_interaction': 0
            }

            session_result = await self.companion.start_learning_session(
                learner_id, topic, initial_assessment
            )

            # Complete beginner module
            await self.companion.process_interaction(
                session_result["session_id"], "module_completed",
                {"module_index": 0, "success_rate": 0.8, "mastery_gain": 0.3}
            )

            # Simulate progression through intermediate content
            await self.companion.process_interaction(
                session_result["session_id"], "module_completed",
                {"module_index": 1, "success_rate": 0.9, "mastery_gain": 0.4}
            )

            completion_result = await self.companion.end_learning_session(session_result["session_id"])

            # Verify progressive improvement
            progress_report = completion_result["progress_report"]
            assert progress_report["performance_metrics"]["learning_efficiency"] > 0.8

            # Check behavioral insights show improvement
            insights = completion_result.get("behavioral_insights", {})
            assert "progress" in str(insights).lower() or "improvement" in str(insights).lower()

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": "Progressive learning correctly tracks skill development and adapts difficulty"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def test_emotional_shift_scenario(self) -> Dict[str, Any]:
        """Test scenario showing emotional state changes during learning."""

        start_time = time.time()
        scenario_name = "Emotional Shift Adaptation Scenario"

        try:
            learner_id = "test_emotional_shift_001"
            topic = "python_functions"

            # Start with calm analytical state
            initial_assessment = {
                'response_times': [2.0, 1.8, 2.2],
                'error_count': 0,
                'total_attempts': 5,
                'help_requests': 0,
                'session_duration': 200,
                'interaction_frequency': 1.8,
                'content_difficulty': 0.6,
                'progress_rate': 0.7,
                'time_since_last_interaction': 0
            }

            session_result = await self.companion.start_learning_session(
                learner_id, topic, initial_assessment
            )

            # Simulate emotional shift to frustration
            frustrated_interactions = [
                ("incorrect_answer", {"response_time": 4.0, "frustration_building": True}),
                ("incorrect_answer", {"response_time": 5.0, "error_streak": 2}),
                ("incorrect_answer", {"response_time": 6.0, "losing_confidence": True})
            ]

            adaptation_triggered = False
            for interaction_type, interaction_data in frustrated_interactions:
                response = await self.companion.process_interaction(
                    session_result["session_id"], interaction_type, interaction_data
                )

                if "adaptation_type" in response and response["adaptation_type"] == "emotional_shift":
                    adaptation_triggered = True
                    assert "frustrated" in str(response.get("new_emotional_state", {}))

            # Verify adaptation occurred
            assert adaptation_triggered, "Emotional shift should trigger content adaptation"

            completion_result = await self.companion.end_learning_session(session_result["session_id"])

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": "Emotional shift detection and adaptive content switching working correctly"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def test_intervention_triggers_scenario(self) -> Dict[str, Any]:
        """Test scenario for intervention trigger mechanisms."""

        start_time = time.time()
        scenario_name = "Intervention Triggers Scenario"

        try:
            learner_id = "test_intervention_001"
            topic = "python_functions"

            # Start with high stress profile
            initial_assessment = {
                'response_times': [5.5, 6.2, 7.1],  # Very slow, frustrated
                'error_count': 4,
                'total_attempts': 5,
                'help_requests': 2,
                'session_duration': 150,
                'interaction_frequency': 0.6,  # Low engagement
                'content_difficulty': 0.9,  # Very challenging
                'progress_rate': 0.1,  # Barely progressing
                'time_since_last_interaction': 45
            }

            session_result = await self.companion.start_learning_session(
                learner_id, topic, initial_assessment
            )

            # Trigger multiple interventions
            stress_inducing_interactions = [
                ("incorrect_answer", {"response_time": 8.0, "high_frustration": True}),
                ("help_request", {"urgent": True, "stuck_completely": True}),
                ("long_pause", {"pause_duration": 120, "overwhelmed": True})
            ]

            interventions_triggered = []
            for interaction_type, interaction_data in stress_inducing_interactions:
                response = await self.companion.process_interaction(
                    session_result["session_id"], interaction_type, interaction_data
                )

                if "intervention_type" in response:
                    interventions_triggered.append(response["intervention_type"])

            # Verify multiple interventions triggered
            assert len(interventions_triggered) >= 2, f"Expected multiple interventions, got {interventions_triggered}"
            assert "stress_relief" in interventions_triggered or "frustration_relief" in interventions_triggered

            completion_result = await self.companion.end_learning_session(session_result["session_id"])

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": f"Intervention system triggered {len(interventions_triggered)} appropriate interventions"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    async def test_edge_cases_scenario(self) -> Dict[str, Any]:
        """Test scenario for edge cases and error handling."""

        start_time = time.time()
        scenario_name = "Edge Cases and Error Handling Scenario"

        try:
            # Test invalid session ID
            invalid_response = await self.companion.process_interaction(
                "invalid_session_id", "test_interaction", {}
            )
            assert "error" in invalid_response

            # Test session status for non-existent session
            status_response = self.companion.get_session_status("non_existent_session")
            assert "error" in status_response

            # Test empty learning history
            progress = self.companion.progress_tracker.get_learning_progress("new_learner")
            assert progress.overall_mastery == 0.0

            # Test available topics
            topics = self.companion.get_available_topics()
            assert "python_functions" in topics

            # Test valid session creation and completion
            learner_id = "test_edge_case_001"
            session_result = await self.companion.start_learning_session(learner_id, "python_functions")

            # Immediately end session (edge case)
            completion_result = await self.companion.end_learning_session(session_result["session_id"])
            assert completion_result["status"] == "completed"

            return {
                "scenario": scenario_name,
                "passed": True,
                "duration": time.time() - start_time,
                "key_findings": "Error handling and edge cases properly managed"
            }

        except Exception as e:
            return {
                "scenario": scenario_name,
                "passed": False,
                "duration": time.time() - start_time,
                "error": str(e)
            }

    def _generate_test_summary(self) -> Dict[str, Any]:
        """Generate comprehensive test summary."""

        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["passed"])
        failed_tests = total_tests - passed_tests

        total_duration = sum(result["duration"] for result in self.test_results)

        # Categorize results
        passed_scenarios = [r["scenario"] for r in self.test_results if r["passed"]]
        failed_scenarios = [r for r in self.test_results if not r["passed"]]

        # Extract key findings
        key_findings = []
        for result in self.test_results:
            if result["passed"] and "key_findings" in result:
                key_findings.append(result["key_findings"])

        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
                "total_duration_seconds": total_duration,
                "average_test_duration": total_duration / total_tests if total_tests > 0 else 0
            },
            "passed_scenarios": passed_scenarios,
            "failed_scenarios": failed_scenarios,
            "key_findings": key_findings,
            "system_validation": {
                "emotional_detection": self._validate_emotional_detection(passed_scenarios),
                "content_adaptation": self._validate_content_adaptation(passed_scenarios),
                "intervention_system": self._validate_intervention_system(passed_scenarios),
                "progress_tracking": self._validate_progress_tracking(passed_scenarios),
                "error_handling": self._validate_error_handling(passed_scenarios)
            },
            "recommendations": self._generate_test_recommendations(failed_scenarios, key_findings)
        }

        return summary

    def _validate_emotional_detection(self, passed_scenarios: List[str]) -> str:
        """Validate emotional detection system."""

        emotional_tests = [s for s in passed_scenarios if any(keyword in s.lower() for keyword in
                        ["exploratory", "analytical", "frustrated", "urgent", "emotional_shift"])]

        if len(emotional_tests) >= 4:
            return "✅ EXCELLENT - All emotional detection scenarios passed"
        elif len(emotional_tests) >= 2:
            return "✅ GOOD - Core emotional detection working"
        else:
            return "⚠️ LIMITED - Emotional detection needs improvement"

    def _validate_content_adaptation(self, passed_scenarios: List[str]) -> str:
        """Validate content adaptation system."""

        adaptation_tests = [s for s in passed_scenarios if "progressive" in s.lower() or "emotional_shift" in s.lower()]

        if len(adaptation_tests) >= 2:
            return "✅ EXCELLENT - Content adaptation working correctly"
        elif len(adaptation_tests) >= 1:
            return "✅ GOOD - Basic content adaptation functional"
        else:
            return "❌ POOR - Content adaptation not validated"

    def _validate_intervention_system(self, passed_scenarios: List[str]) -> str:
        """Validate intervention system."""

        intervention_tests = [s for s in passed_scenarios if "intervention" in s.lower() or "frustrated" in s.lower()]

        if len(intervention_tests) >= 2:
            return "✅ EXCELLENT - Intervention system fully functional"
        elif len(intervention_tests) >= 1:
            return "✅ GOOD - Basic interventions working"
        else:
            return "⚠️ LIMITED - Intervention system needs testing"

    def _validate_progress_tracking(self, passed_scenarios: List[str]) -> str:
        """Validate progress tracking system."""

        progress_tests = [s for s in passed_scenarios if "progressive" in s.lower()]

        if len(progress_tests) >= 1:
            return "✅ EXCELLENT - Progress tracking validated"
        else:
            return "⚠️ LIMITED - Progress tracking needs more testing"

    def _validate_error_handling(self, passed_scenarios: List[str]) -> str:
        """Validate error handling."""

        error_tests = [s for s in passed_scenarios if "edge" in s.lower()]

        if len(error_tests) >= 1:
            return "✅ EXCELLENT - Error handling robust"
        else:
            return "⚠️ LIMITED - Error handling needs validation"

    def _generate_test_recommendations(self, failed_scenarios: List[Dict[str, Any]], key_findings: List[str]) -> List[str]:
        """Generate test-based recommendations."""

        recommendations = []

        if failed_scenarios:
            recommendations.append(f"Fix {len(failed_scenarios)} failing test scenarios")

        # Check for patterns in findings
        findings_text = " ".join(key_findings).lower()

        if "intervention" not in findings_text:
            recommendations.append("Strengthen intervention trigger testing")

        if "emotional" not in findings_text:
            recommendations.append("Add more emotional state transition tests")

        if "progress" not in findings_text:
            recommendations.append("Validate long-term progress tracking")

        if not recommendations:
            recommendations.append("All core systems validated - consider adding performance and scalability tests")

        return recommendations

async def run_test_suite():
    """Run the complete test suite and display results."""

    test_suite = LearningCompanionTestSuite()
    results = await test_suite.run_full_test_suite()

    print("\n" + "="*60)
    print("🎯 LEARNING COMPANION TEST SUITE RESULTS")
    print("="*60)

    summary = results["test_summary"]
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed_tests']} ✅")
    print(f"Failed: {summary['failed_tests']} ❌")
    print(".1f"    print(".2f"
    if summary["success_rate"] >= 0.8:
        print("🎉 EXCELLENT - Core functionality validated!")
    elif summary["success_rate"] >= 0.6:
        print("✅ GOOD - System functional with minor issues")
    else:
        print("⚠️ NEEDS WORK - Significant testing required")

    print("\n🔍 SYSTEM VALIDATION:")
    for component, status in results["system_validation"].items():
        print(f"  {component.replace('_', ' ').title()}: {status}")

    if results["key_findings"]:
        print("\n💡 KEY FINDINGS:")
        for finding in results["key_findings"]:
            print(f"  • {finding}")

    if results["recommendations"]:
        print("\n🎯 RECOMMENDATIONS:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")

    # Save detailed results
    output_file = Path("test_results.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {output_file}")

    return results

if __name__ == "__main__":
    asyncio.run(run_test_suite())
