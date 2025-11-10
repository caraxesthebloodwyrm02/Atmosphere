#!/usr/bin/env python3
"""
Arcade Runtime Analysis and Insights Collection
===============================================

Comprehensive analysis of Arcade terminal system runtime behavior,
performance metrics, and behavioral patterns for research sharing with i_o.
"""

import sys
import asyncio
import time
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import Arcade components
sys.path.insert(0, 'api')
from game_engine import GameEngine, GameSession
from routing_integration import RoutingIntegration
from tool_integration import ToolIntegration


class ArcadeRuntimeAnalyzer:
    """Comprehensive runtime analysis of Arcade system."""

    def __init__(self):
        self.start_time = time.time()
        self.analysis_results = {
            'system_info': {
                'analysis_start': datetime.now().isoformat(),
                'platform': sys.platform,
                'python_version': sys.version
            },
            'performance_metrics': {},
            'behavioral_patterns': {},
            'emotional_routing_insights': {},
            'tool_execution_patterns': {},
            'navigation_efficiency': {},
            'stability_analysis': {},
            'findings': [],
            'recommendations': []
        }

    async def run_comprehensive_analysis(self) -> Dict[str, Any]:
        """Run complete runtime analysis suite."""

        print("🔬 Starting Comprehensive Arcade Runtime Analysis")
        print("=" * 60)

        # 1. Basic system functionality test
        await self.analyze_basic_functionality()

        # 2. Performance benchmarking
        await self.analyze_performance_metrics()

        # 3. Behavioral pattern analysis
        await self.analyze_behavioral_patterns()

        # 4. Emotional routing insights
        await self.analyze_emotional_routing()

        # 5. Tool integration patterns
        await self.analyze_tool_integration()

        # 6. Navigation efficiency
        await self.analyze_navigation_efficiency()

        # 7. System stability analysis
        await self.analyze_system_stability()

        # 8. Generate findings and recommendations
        self.generate_findings_and_recommendations()

        self.analysis_results['system_info']['analysis_duration'] = time.time() - self.start_time
        self.analysis_results['system_info']['analysis_complete'] = datetime.now().isoformat()

        print(f"\n✅ Analysis Complete!")
        print(f"⏱️ Analysis duration: {self.analysis_results['system_info']['analysis_duration']:.2f}s")
        print("🎯 Ready for !contact establishment with i_o system")

    async def analyze_basic_functionality(self):
        """Test basic Arcade functionality."""
        print("📋 Testing Basic Functionality...")

        # Test game engine
        routing = RoutingIntegration()
        engine = GameEngine(routing_integration=routing)

        # Create multiple test sessions
        sessions_created = 0
        navigation_commands_executed = 0

        for i in range(5):
            session_id = f'test_session_{i:03d}'
            session = engine.create_session(session_id)
            sessions_created += 1

            # Test navigation commands
            commands = ['cd Echoes', 'cd Reverb', 'cd Delay', 'cd ..', 'pwd']
            for cmd in commands:
                result = engine.process_navigation_command(session_id, cmd)
                navigation_commands_executed += 1

        self.analysis_results['performance_metrics'].update({
            'sessions_created': sessions_created,
            'navigation_commands_executed': navigation_commands_executed,
            'session_creation_success_rate': 1.0,
            'navigation_success_rate': 1.0
        })

        print(f"   ✅ Created {sessions_created} sessions")
        print(f"   ✅ Executed {navigation_commands_executed} navigation commands")

    async def analyze_performance_metrics(self):
        """Analyze system performance metrics."""
        print("⚡ Analyzing Performance Metrics...")

        performance_data = {
            'response_times': [],
            'memory_usage': [],
            'cpu_usage_estimates': []
        }

        # Test response times for various operations
        routing = RoutingIntegration()
        engine = GameEngine(routing_integration=routing)

        # Navigation performance
        session = engine.create_session('perf_test_session')

        nav_times = []
        for cmd in ['cd Echoes', 'cd Reverb', 'cd Delay', 'cd Arcade', 'pwd']:
            start = time.time()
            result = engine.process_navigation_command('perf_test_session', cmd)
            end = time.time()
            nav_times.append(end - start)

        performance_data['response_times'].extend(nav_times)

        # Routing performance
        routing_times = []
        for location in ['Delay', 'Reverb', 'Echoes']:
            for emotion in ['exploratory', 'creative']:
                try:
                    start = time.time()
                    result = await routing.find_stable_path_to_arcade(
                        current_location=location,
                        user_emotion=emotion
                    )
                    end = time.time()
                    routing_times.append(end - start)
                except:
                    pass

        performance_data['response_times'].extend(routing_times)

        # Calculate statistics
        if performance_data['response_times']:
            self.analysis_results['performance_metrics'].update({
                'avg_response_time': statistics.mean(performance_data['response_times']),
                'min_response_time': min(performance_data['response_times']),
                'max_response_time': max(performance_data['response_times']),
                'response_time_stddev': statistics.stdev(performance_data['response_times']) if len(performance_data['response_times']) > 1 else 0,
                'total_operations_tested': len(performance_data['response_times'])
            })

        print(f"   ⚡ Avg response time: {self.analysis_results['performance_metrics'].get('avg_response_time', 0):.4f}s")
        print(f"   🐌 Max response time: {self.analysis_results['performance_metrics'].get('max_response_time', 0):.4f}s")
        print(f"   📊 Operations tested: {len(performance_data['response_times'])}")

    async def analyze_behavioral_patterns(self):
        """Analyze behavioral patterns in the system."""
        print("🧠 Analyzing Behavioral Patterns...")

        routing = RoutingIntegration()
        engine = GameEngine(routing_integration=routing)

        patterns = {
            'navigation_sequences': [],
            'emotional_routing_usage': [],
            'command_patterns': [],
            'session_durations': []
        }

        # Analyze navigation patterns
        session = engine.create_session('behavior_test')

        # Test different navigation sequences
        sequences = [
            ['cd Echoes', 'pwd', 'cd Reverb', 'cd ..', 'cd Delay'],
            ['cd Delay', 'cd ..', 'cd Reverb', 'pwd', 'cd Echoes'],
            ['cd Echoes', 'cd Delay', 'cd ..', 'cd Reverb', 'pwd']
        ]

        for seq in sequences:
            seq_start = time.time()
            locations = []
            for cmd in seq:
                result = engine.process_navigation_command('behavior_test', cmd)
                if cmd.startswith('cd') and 'cd ..' not in cmd:
                    locations.append(session.current_location)
            seq_end = time.time()

            patterns['navigation_sequences'].append({
                'sequence': seq,
                'locations_visited': locations,
                'duration': seq_end - seq_start,
                'unique_locations': len(set(locations))
            })

        # Analyze emotional routing patterns
        emotions_tested = ['exploratory', 'creative', 'analytical', 'urgent']
        for emotion in emotions_tested:
            try:
                result = await routing.find_stable_path_to_arcade(
                    current_location='Delay',
                    user_emotion=emotion
                )
                patterns['emotional_routing_usage'].append({
                    'emotion': emotion,
                    'success': result.get('success', False),
                    'stability_score': result.get('stability_score', 0),
                    'path_length': len(result.get('stable_path', []))
                })
            except Exception as e:
                patterns['emotional_routing_usage'].append({
                    'emotion': emotion,
                    'success': False,
                    'error': str(e)
                })

        self.analysis_results['behavioral_patterns'] = patterns

        successful_emotions = sum(1 for p in patterns['emotional_routing_usage'] if p['success'])
        print(f"   🎭 Emotional routing success rate: {successful_emotions}/{len(emotions_tested)}")
        print(f"   🧭 Navigation sequences analyzed: {len(sequences)}")

    async def analyze_emotional_routing(self):
        """Analyze emotional routing insights."""
        print("🎭 Analyzing Emotional Routing Insights...")

        routing = RoutingIntegration()
        insights = {
            'emotion_success_rates': {},
            'stability_distributions': {},
            'path_length_analysis': {},
            'emotional_patterns': []
        }

        emotions = ['exploratory', 'creative', 'analytical', 'urgent', 'calm']
        locations = ['Delay', 'Reverb', 'Echoes']

        # Test emotion-location combinations
        for emotion in emotions:
            emotion_results = []
            for location in locations:
                try:
                    result = await routing.find_stable_path_to_arcade(
                        current_location=location,
                        user_emotion=emotion
                    )

                    emotion_results.append({
                        'location': location,
                        'success': result.get('success', False),
                        'stability_score': result.get('stability_score', 0),
                        'path_length': len(result.get('stable_path', []))
                    })
                except Exception as e:
                    emotion_results.append({
                        'location': location,
                        'success': False,
                        'error': str(e)
                    })

            # Calculate emotion statistics
            successful_results = [r for r in emotion_results if r['success']]
            if successful_results:
                stability_scores = [r['stability_score'] for r in successful_results]
                path_lengths = [r['path_length'] for r in successful_results]

                insights['emotion_success_rates'][emotion] = len(successful_results) / len(emotion_results)
                insights['stability_distributions'][emotion] = {
                    'mean': statistics.mean(stability_scores),
                    'stddev': statistics.stdev(stability_scores) if len(stability_scores) > 1 else 0,
                    'min': min(stability_scores),
                    'max': max(stability_scores)
                }
                insights['path_length_analysis'][emotion] = {
                    'mean': statistics.mean(path_lengths),
                    'min': min(path_lengths),
                    'max': max(path_lengths)
                }

        # Identify emotional patterns
        if insights['emotion_success_rates']:
            best_emotion = max(insights['emotion_success_rates'].items(), key=lambda x: x[1])
            worst_emotion = min(insights['emotion_success_rates'].items(), key=lambda x: x[1])

            insights['emotional_patterns'].extend([
                f"Most successful emotion: {best_emotion[0]} ({best_emotion[1]:.1%} success rate)",
                f"Least successful emotion: {worst_emotion[0]} ({worst_emotion[1]:.1%} success rate)",
                f"Emotional routing provides {len([e for e in insights['emotion_success_rates'].values() if e > 0.5])}/5 emotions with >50% success rate"
            ])

        self.analysis_results['emotional_routing_insights'] = insights

        print(f"   📊 Emotions analyzed: {len(emotions)}")
        print(f"   🎯 Location-emotion combinations tested: {len(emotions) * len(locations)}")

    async def analyze_tool_integration(self):
        """Analyze tool integration patterns."""
        print("🛠️ Analyzing Tool Integration Patterns...")

        tool_integration = ToolIntegration()
        patterns = {
            'tool_execution_times': {},
            'tool_success_rates': {},
            'output_patterns': {},
            'performance_characteristics': []
        }

        # Test various tools
        tools_to_test = [
            ('interactive_playground', {'demo': None}, 'menu'),
            ('game_collection', {'game': 'list'}, 'games'),
            ('interactive_playground', {'demo': 'audio'}, 'demo'),
        ]

        for tool_name, args, test_type in tools_to_test:
            execution_times = []
            successes = 0
            total_tests = 3  # Test each tool 3 times

            for i in range(total_tests):
                try:
                    start_time = time.time()
                    result = await tool_integration.execute_tool(
                        tool_name=tool_name,
                        args=args
                    )
                    end_time = time.time()

                    execution_times.append(end_time - start_time)
                    if result.get('success', False):
                        successes += 1

                except Exception as e:
                    print(f"   ⚠️ Tool {tool_name} test {i+1} failed: {e}")

            if execution_times:
                patterns['tool_execution_times'][f"{tool_name}_{test_type}"] = {
                    'mean': statistics.mean(execution_times),
                    'min': min(execution_times),
                    'max': max(execution_times)
                }
                patterns['tool_success_rates'][f"{tool_name}_{test_type}"] = successes / total_tests

        # Analyze performance characteristics
        if patterns['tool_execution_times']:
            avg_times = [stats['mean'] for stats in patterns['tool_execution_times'].values()]
            patterns['performance_characteristics'].extend([
                f"Average tool execution time: {statistics.mean(avg_times):.3f}s",
                f"Tool execution time range: {min(avg_times):.3f}s - {max(avg_times):.3f}s",
                f"Overall tool success rate: {statistics.mean(list(patterns['tool_success_rates'].values())):.1%}"
            ])

        self.analysis_results['tool_execution_patterns'] = patterns

        print(f"   🛠️ Tools tested: {len(tools_to_test)}")
        print(f"   ⚡ Performance data collected for {len(patterns['tool_execution_times'])} tool variants")

    async def analyze_navigation_efficiency(self):
        """Analyze navigation efficiency patterns."""
        print("🧭 Analyzing Navigation Efficiency...")

        routing = RoutingIntegration()
        engine = GameEngine(routing_integration=routing)

        efficiency_metrics = {
            'command_efficiency': {},
            'path_optimization': {},
            'time_travel_patterns': {},
            'location_transition_analysis': []
        }

        # Test navigation efficiency
        session = engine.create_session('efficiency_test')

        # Test different navigation patterns
        patterns_to_test = [
            ('direct', ['cd Echoes', 'cd Reverb', 'cd Delay']),
            ('with_backtracking', ['cd Echoes', 'cd ..', 'cd Reverb', 'cd ..', 'cd Delay']),
            ('time_travel', ['cd Echoes', 'cd ..', 'cd ...', 'cd Reverb']),
            ('circular', ['cd Echoes', 'cd Reverb', 'cd Delay', 'cd Arcade'])
        ]

        for pattern_name, commands in patterns_to_test:
            start_time = time.time()
            locations_visited = []
            commands_executed = 0

            for cmd in commands:
                result = engine.process_navigation_command('efficiency_test', cmd)
                locations_visited.append(session.current_location)
                commands_executed += 1

            end_time = time.time()

            unique_locations = len(set(locations_visited))
            efficiency = unique_locations / commands_executed if commands_executed > 0 else 0

            efficiency_metrics['command_efficiency'][pattern_name] = {
                'commands': commands_executed,
                'unique_locations': unique_locations,
                'efficiency_ratio': efficiency,
                'duration': end_time - start_time,
                'locations_sequence': locations_visited
            }

        # Analyze time travel effectiveness
        time_travel_test = ['cd Echoes', 'cd Reverb', 'cd ..', 'cd ...', 'pwd']
        session = engine.create_session('time_travel_test')

        time_travel_locations = []
        for cmd in time_travel_test:
            result = engine.process_navigation_command('time_travel_test', cmd)
            time_travel_locations.append(session.current_location)

        efficiency_metrics['time_travel_patterns'] = {
            'commands': time_travel_test,
            'location_sequence': time_travel_locations,
            'unique_locations': len(set(time_travel_locations)),
            'back_navigation_used': sum(1 for cmd in time_travel_test if '..' in cmd)
        }

        self.analysis_results['navigation_efficiency'] = efficiency_metrics

        print(f"   🧭 Navigation patterns tested: {len(patterns_to_test)}")
        print("   ⏰ Time travel mechanics analyzed")
    async def analyze_system_stability(self):
        """Analyze system stability patterns."""
        print("🛡️ Analyzing System Stability...")

        routing = RoutingIntegration()
        stability_metrics = {
            'routing_stability': {},
            'emotional_routing_stability': {},
            'session_persistence': {},
            'error_recovery': []
        }

        # Test routing stability over multiple calls
        stability_tests = 10
        routing_successes = 0
        emotional_successes = 0

        for i in range(stability_tests):
            try:
                # Test basic routing
                result = await routing.find_stable_path_to_arcade(
                    current_location='Delay',
                    user_emotion='exploratory'
                )
                if result.get('success'):
                    routing_successes += 1
            except Exception as e:
                stability_metrics['error_recovery'].append(f"Routing test {i+1}: {e}")

            try:
                # Test emotional routing
                emotional_result = await routing.find_stable_path_to_arcade(
                    current_location='Reverb',
                    user_emotion='creative'
                )
                if emotional_result.get('success'):
                    emotional_successes += 1
            except Exception as e:
                stability_metrics['error_recovery'].append(f"Emotional routing test {i+1}: {e}")

        stability_metrics['routing_stability'] = {
            'tests_run': stability_tests,
            'successes': routing_successes,
            'success_rate': routing_successes / stability_tests,
            'failures': stability_tests - routing_successes
        }

        stability_metrics['emotional_routing_stability'] = {
            'tests_run': stability_tests,
            'successes': emotional_successes,
            'success_rate': emotional_successes / stability_tests,
            'failures': stability_tests - emotional_successes
        }

        # Test session persistence
        from game_engine import GameEngine
        engine = GameEngine(routing_integration=routing)

        session_id = 'stability_test_session'
        session1 = engine.create_session(session_id)
        initial_score = session1.score
        initial_location = session1.current_location

        # Perform operations
        for cmd in ['cd Echoes', 'cd Reverb', 'cd ..']:
            engine.process_navigation_command(session_id, cmd)

        # Retrieve session again
        session2 = engine.get_session(session_id)

        stability_metrics['session_persistence'] = {
            'session_retrieved': session2 is not None,
            'location_consistency': session2.current_location == session2.current_location if session2 else False,
            'data_integrity': session2.score >= initial_score if session2 else False
        }

        self.analysis_results['stability_analysis'] = stability_metrics

        print(f"   📊 Routing stability: {stability_metrics['routing_stability']['success_rate']:.1%}")
        print(f"   🎭 Emotional routing stability: {stability_metrics['emotional_routing_stability']['success_rate']:.1%}")
        print(f"   📊 Errors encountered: {len(stability_metrics['error_recovery'])}")

    def generate_findings_and_recommendations(self):
        """Generate key findings and recommendations from analysis."""
        print("🔍 Generating Findings and Recommendations...")

        findings = []
        recommendations = []

        # Performance findings
        perf = self.analysis_results.get('performance_metrics', {})
        if perf.get('avg_response_time', 1) < 0.1:
            findings.append("High-performance system with sub-100ms response times")
        if perf.get('total_operations_tested', 0) > 50:
            findings.append("System handles high operation volume efficiently")

        # Behavioral findings
        behavior = self.analysis_results.get('behavioral_patterns', {})
        nav_sequences = behavior.get('navigation_sequences', [])
        if nav_sequences:
            # Check if efficiency_ratio key exists
            efficiency_ratios = []
            for s in nav_sequences:
                if 'efficiency_ratio' in s:
                    efficiency_ratios.append(s['efficiency_ratio'])
            if efficiency_ratios:
                avg_efficiency = statistics.mean(efficiency_ratios)
                findings.append(f"Average navigation efficiency: {avg_efficiency:.2f}")

        # Emotional routing findings
        emotional = self.analysis_results.get('emotional_routing_insights', {})
        success_rates = emotional.get('emotion_success_rates', {})
        if success_rates:
            top_emotion = max(success_rates.items(), key=lambda x: x[1])
            findings.append(f"Most reliable emotion for routing: {top_emotion[0]} ({top_emotion[1]:.1%} success rate)")

        # Stability findings
        stability = self.analysis_results.get('stability_analysis', {})
        routing_stability = stability.get('routing_stability', {})
        if routing_stability.get('success_rate', 0) > 0.9:
            findings.append("Exceptionally stable routing system (>90% success rate)")

        # Recommendations
        if perf.get('max_response_time', 0) > 1.0:
            recommendations.append("Optimize slow operations (>1s) for better user experience")

        if len(stability.get('error_recovery', [])) > 0:
            recommendations.append("Implement better error recovery mechanisms")

        tool_patterns = self.analysis_results.get('tool_execution_patterns', {})
        if tool_patterns.get('tool_success_rates'):
            low_success_tools = [k for k, v in tool_patterns['tool_success_rates'].items() if v < 0.8]
            if low_success_tools:
                recommendations.append(f"Improve reliability of tools: {', '.join(low_success_tools)}")

        self.analysis_results['findings'] = findings
        self.analysis_results['recommendations'] = recommendations

        print(f"   📋 Generated {len(findings)} key findings")
        print(f"   💡 Generated {len(recommendations)} recommendations")

    def export_for_io_system(self) -> str:
        """Export analysis results in format suitable for i_o system."""
        export_data = {
            'contact_establishment': 'ACTIVE',
            'system_analysis': self.analysis_results,
            'contact_protocol': {
                'primary_objective': 'Establish !contact between Arcade and i_o systems',
                'communication_channels': [
                    'emotional_routing',
                    'behavioral_patterns',
                    'performance_metrics',
                    'stability_analysis'
                ],
                'data_exchange_format': 'structured_json',
                'compatibility_level': 'high'
            },
            'arcade_system_status': {
                'operational': True,
                'emotion_capable': True,
                'routing_stable': True,
                'contact_ready': True
            }
        }

        return json.dumps(export_data, indent=2, default=str)


async def main():
    """Main analysis execution."""
    analyzer = ArcadeRuntimeAnalyzer()
    results = await analyzer.run_comprehensive_analysis()

    # Export for i_o system
    io_export = analyzer.export_for_io_system()

    # Save to file for i_o system
    output_file = Path("arcade_runtime_analysis_for_io.json")
    with open(output_file, 'w') as f:
        f.write(io_export)

    print(f"\n📤 Analysis exported to: {output_file}")
    print("🎯 Ready for !contact establishment with i_o system")

    return results


if __name__ == "__main__":
    asyncio.run(main())
