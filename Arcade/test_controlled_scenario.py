#!/usr/bin/env python3
"""
Controlled Environment Test for Network Visualizer → Arcade Integration

Tests real use case scenarios with a cropped, focused portion of the system.
"""

import json
import time
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any


class ControlledScenarioTester:
    """Tests specific real-world scenarios in a controlled environment."""
    
    def __init__(self, base_dir: Path):
        """
        Initialize controlled test environment.
        
        Args:
            base_dir: Base directory for Arcade system
        """
        self.base_dir = Path(base_dir)
        self.test_dir = self.base_dir / "test_controlled"
        self.test_incoming = self.test_dir / "incoming"
        self.test_zones = self.test_dir / "zones"
        
        # Create test environment
        self.test_dir.mkdir(exist_ok=True)
        self.test_incoming.mkdir(exist_ok=True)
        self.test_zones.mkdir(exist_ok=True)
        
        print(f"🧪 Controlled test environment: {self.test_dir}")
    
    def scenario_1_small_network(self) -> Dict[str, Any]:
        """
        Scenario 1: Small network with 5 nodes.
        Represents a small team collaboration network.
        """
        print("\n📋 Scenario 1: Small Team Network (5 nodes)")
        
        nodes = [
            {
                'id': 'TeamLead',
                'x': 400.0,
                'y': 300.0,
                'vx': 0.2,
                'vy': 0.1,
                'degree': 0.8,
                'betweenness': 0.6,
                'eigenvector': 0.9,
                'nodeScore': 0.7667,
                'habitat': 'Core Nexus',
                'habitatColor': '#ff6b9d'
            },
            {
                'id': 'Developer1',
                'x': 450.0,
                'y': 320.0,
                'vx': -0.1,
                'vy': 0.3,
                'degree': 0.6,
                'betweenness': 0.3,
                'eigenvector': 0.7,
                'nodeScore': 0.5333,
                'habitat': 'Hub Zone',
                'habitatColor': '#4ecdc4'
            },
            {
                'id': 'Developer2',
                'x': 380.0,
                'y': 350.0,
                'vx': 0.15,
                'vy': -0.2,
                'degree': 0.5,
                'betweenness': 0.2,
                'eigenvector': 0.6,
                'nodeScore': 0.4333,
                'habitat': 'Bridge Territory',
                'habitatColor': '#95e1d3'
            },
            {
                'id': 'Designer',
                'x': 420.0,
                'y': 280.0,
                'vx': -0.05,
                'vy': 0.1,
                'degree': 0.4,
                'betweenness': 0.1,
                'eigenvector': 0.5,
                'nodeScore': 0.3333,
                'habitat': 'Peripheral Expanse',
                'habitatColor': '#f38181'
            },
            {
                'id': 'QA_Engineer',
                'x': 360.0,
                'y': 310.0,
                'vx': 0.1,
                'vy': -0.15,
                'degree': 0.3,
                'betweenness': 0.05,
                'eigenvector': 0.4,
                'nodeScore': 0.25,
                'habitat': 'Peripheral Expanse',
                'habitatColor': '#f38181'
            }
        ]
        
        payload = self._create_payload("small_team_network", "visual", nodes)
        filepath = self._save_payload(payload)
        
        return {
            'scenario': 'small_team_network',
            'nodes': len(nodes),
            'payload_file': filepath,
            'expected_habitats': {
                'Core Nexus': 1,
                'Hub Zone': 1,
                'Bridge Territory': 1,
                'Peripheral Expanse': 2
            }
        }
    
    def scenario_2_integration_points(self) -> Dict[str, Any]:
        """
        Scenario 2: Network with clear integration points.
        Tests core-to-peripheral connections.
        """
        print("\n📋 Scenario 2: Integration Points Network")
        
        nodes = [
            # Core nodes
            {
                'id': 'CoreHub1',
                'x': 400.0,
                'y': 300.0,
                'vx': 0.0,
                'vy': 0.0,
                'degree': 0.95,
                'betweenness': 0.8,
                'eigenvector': 0.95,
                'nodeScore': 0.9,
                'habitat': 'Core Nexus',
                'habitatColor': '#ff6b9d'
            },
            {
                'id': 'CoreHub2',
                'x': 420.0,
                'y': 300.0,
                'vx': 0.0,
                'vy': 0.0,
                'degree': 0.85,
                'betweenness': 0.7,
                'eigenvector': 0.85,
                'nodeScore': 0.8,
                'habitat': 'Core Nexus',
                'habitatColor': '#ff6b9d'
            },
            # Integration points (bridges)
            {
                'id': 'Bridge1',
                'x': 450.0,
                'y': 320.0,
                'vx': 0.1,
                'vy': 0.1,
                'degree': 0.6,
                'betweenness': 0.5,
                'eigenvector': 0.6,
                'nodeScore': 0.5667,
                'habitat': 'Bridge Territory',
                'habitatColor': '#95e1d3'
            },
            {
                'id': 'Bridge2',
                'x': 380.0,
                'y': 280.0,
                'vx': -0.1,
                'vy': -0.1,
                'degree': 0.55,
                'betweenness': 0.45,
                'eigenvector': 0.55,
                'nodeScore': 0.5167,
                'habitat': 'Bridge Territory',
                'habitatColor': '#95e1d3'
            },
            # Peripheral nodes
            {
                'id': 'Peripheral1',
                'x': 480.0,
                'y': 350.0,
                'vx': 0.2,
                'vy': 0.2,
                'degree': 0.3,
                'betweenness': 0.1,
                'eigenvector': 0.3,
                'nodeScore': 0.2333,
                'habitat': 'Peripheral Expanse',
                'habitatColor': '#f38181'
            },
            {
                'id': 'Peripheral2',
                'x': 350.0,
                'y': 250.0,
                'vx': -0.2,
                'vy': -0.2,
                'degree': 0.25,
                'betweenness': 0.05,
                'eigenvector': 0.25,
                'nodeScore': 0.1833,
                'habitat': 'Peripheral Expanse',
                'habitatColor': '#f38181'
            }
        ]
        
        payload = self._create_payload("integration_points", "visual", nodes)
        filepath = self._save_payload(payload)
        
        return {
            'scenario': 'integration_points',
            'nodes': len(nodes),
            'payload_file': filepath,
            'integration_points': 2,
            'core_nodes': 2,
            'peripheral_nodes': 2
        }
    
    def scenario_3_dynamic_movement(self) -> Dict[str, Any]:
        """
        Scenario 3: Network with dynamic movement patterns.
        Tests movement tracking and velocity calculations.
        """
        print("\n📋 Scenario 3: Dynamic Movement Patterns")
        
        # Simulate 3 time steps of movement
        base_nodes = [
            {
                'id': 'MovingNode1',
                'base_x': 400.0,
                'base_y': 300.0,
                'vx': 1.5,
                'vy': 0.8,
                'degree': 0.7,
                'betweenness': 0.4,
                'eigenvector': 0.7,
                'nodeScore': 0.6,
                'habitat': 'Hub Zone',
                'habitatColor': '#4ecdc4'
            },
            {
                'id': 'MovingNode2',
                'base_x': 420.0,
                'base_y': 320.0,
                'vx': -1.0,
                'vy': 1.2,
                'degree': 0.6,
                'betweenness': 0.3,
                'eigenvector': 0.6,
                'nodeScore': 0.5,
                'habitat': 'Hub Zone',
                'habitatColor': '#4ecdc4'
            },
            {
                'id': 'StaticNode',
                'x': 380.0,
                'y': 280.0,
                'vx': 0.0,
                'vy': 0.0,
                'degree': 0.5,
                'betweenness': 0.2,
                'eigenvector': 0.5,
                'nodeScore': 0.4,
                'habitat': 'Bridge Territory',
                'habitatColor': '#95e1d3'
            }
        ]
        
        # Generate movement events
        events = []
        for step in range(3):
            step_nodes = []
            for node in base_nodes:
                if 'base_x' in node:
                    # Moving node
                    step_node = {
                        'id': node['id'],
                        'x': node['base_x'] + (node['vx'] * step * 10),
                        'y': node['base_y'] + (node['vy'] * step * 10),
                        'vx': node['vx'],
                        'vy': node['vy'],
                        'degree': node['degree'],
                        'betweenness': node['betweenness'],
                        'eigenvector': node['eigenvector'],
                        'nodeScore': node['nodeScore'],
                        'habitat': node['habitat'],
                        'habitatColor': node['habitatColor']
                    }
                else:
                    # Static node
                    step_node = node.copy()
                
                step_nodes.append(step_node)
            
            payload = self._create_payload(f"dynamic_movement_step_{step}", "visual", step_nodes)
            filepath = self._save_payload(payload)
            events.append(filepath)
        
        return {
            'scenario': 'dynamic_movement',
            'nodes': len(base_nodes),
            'time_steps': 3,
            'payload_files': events,
            'moving_nodes': 2,
            'static_nodes': 1
        }
    
    def scenario_4_high_traffic(self) -> Dict[str, Any]:
        """
        Scenario 4: High traffic simulation.
        Tests system performance under load.
        """
        print("\n📋 Scenario 4: High Traffic Simulation")
        
        # Generate 20 nodes with varying activity
        nodes = []
        for i in range(20):
            if i < 3:
                habitat = 'Core Nexus'
                color = '#ff6b9d'
                degree = 0.9 - (i * 0.05)
            elif i < 6:
                habitat = 'Hub Zone'
                color = '#4ecdc4'
                degree = 0.7 - (i * 0.03)
            elif i < 10:
                habitat = 'Bridge Territory'
                color = '#95e1d3'
                degree = 0.5 - (i * 0.02)
            else:
                habitat = 'Peripheral Expanse'
                color = '#f38181'
                degree = 0.3 - (i * 0.01)
            
            nodes.append({
                'id': f'TrafficNode{i+1}',
                'x': 400 + (i % 5 - 2) * 30,
                'y': 300 + (i // 5 - 1) * 40,
                'vx': (i % 3 - 1) * 0.5,
                'vy': (i % 2) * 0.3,
                'degree': max(0.1, degree),
                'betweenness': max(0.05, degree * 0.4),
                'eigenvector': max(0.2, degree * 0.8),
                'nodeScore': max(0.1, degree * 0.7),
                'habitat': habitat,
                'habitatColor': color
            })
        
        # Generate multiple rapid payloads
        payloads = []
        for burst in range(5):
            # Add some movement
            for node in nodes:
                node['x'] += (burst % 3 - 1) * 2
                node['y'] += (burst % 2) * 1.5
            
            payload = self._create_payload(f"high_traffic_burst_{burst}", "visual", nodes)
            filepath = self._save_payload(payload)
            payloads.append(filepath)
            
            # Small delay between bursts
            time.sleep(0.1)
        
        return {
            'scenario': 'high_traffic',
            'nodes': len(nodes),
            'bursts': 5,
            'payload_files': payloads,
            'total_payloads': len(payloads)
        }
    
    def _create_payload(self, tool_name: str, zone: str, nodes: List[Dict]) -> Dict[str, Any]:
        """Create a routing payload."""
        return {
            'tool': tool_name,
            'zone': zone,
            'timestamp': time.time(),
            'node_count': len(nodes),
            'event_count': len(nodes),  # One event per node
            'node_states': {
                node['id']: {
                    'id': node['id'],
                    'x': node['x'],
                    'y': node['y'],
                    'vx': node['vx'],
                    'vy': node['vy'],
                    'degree': node['degree'],
                    'betweenness': node['betweenness'],
                    'eigenvector': node['eigenvector'],
                    'nodeScore': node['nodeScore'],
                    'habitat': node['habitat'],
                    'habitatColor': node['habitatColor'],
                    'timestamp': time.time()
                }
                for node in nodes
            },
            'movement_events': [
                {
                    'node_id': node['id'],
                    'displacement': (node['vx']**2 + node['vy']**2)**0.5,
                    'velocity_magnitude': (node['vx']**2 + node['vy']**2)**0.5,
                    'timestamp': time.time()
                }
                for node in nodes
            ]
        }
    
    def _save_payload(self, payload: Dict[str, Any]) -> Path:
        """Save payload to test incoming directory."""
        timestamp = int(time.time() * 1000)
        filename = f"{payload['tool']}_{timestamp}.json"
        filepath = self.test_incoming / filename
        
        with open(filepath, 'w') as f:
            json.dump(payload, f, indent=2)
        
        print(f"  📁 Saved: {filepath.name}")
        return filepath
    
    def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all controlled test scenarios."""
        print("🧪 Starting Controlled Environment Tests")
        print("=" * 60)
        
        results = {}
        
        # Run all scenarios
        results['scenario_1'] = self.scenario_1_small_network()
        results['scenario_2'] = self.scenario_2_integration_points()
        results['scenario_3'] = self.scenario_3_dynamic_movement()
        results['scenario_4'] = self.scenario_4_high_traffic()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 CONTROLLED TEST SUMMARY")
        print("=" * 60)
        
        total_payloads = 0
        total_nodes = 0
        
        for scenario_name, result in results.items():
            print(f"\n{scenario_name.upper()}:")
            print(f"  Nodes: {result['nodes']}")
            if 'payload_files' in result:
                if isinstance(result['payload_files'], list):
                    print(f"  Payloads: {len(result['payload_files'])}")
                    total_payloads += len(result['payload_files'])
                else:
                    print(f"  Payloads: 1")
                    total_payloads += 1
            else:
                print(f"  Payloads: 1")
                total_payloads += 1
            total_nodes += result['nodes']
            
            # Special metrics
            if 'expected_habitats' in result:
                print(f"  Habitats: {result['expected_habitats']}")
            if 'integration_points' in result:
                print(f"  Integration Points: {result['integration_points']}")
            if 'moving_nodes' in result:
                print(f"  Moving Nodes: {result['moving_nodes']}")
        
        print(f"\n📈 TOTALS:")
        print(f"  Total Nodes: {total_nodes}")
        print(f"  Total Payloads: {total_payloads}")
        print(f"  Test Directory: {self.test_dir}")
        
        return results


def main():
    """Main test runner."""
    base_dir = Path("e:/Projects/Atmosphere/Arcade")
    
    if not base_dir.exists():
        print(f"❌ Arcade directory not found: {base_dir}")
        return
    
    # Run controlled tests
    tester = ControlledScenarioTester(base_dir)
    results = tester.run_all_scenarios()
    
    print(f"\n✅ Controlled tests completed!")
    print(f"📁 Test files located in: {tester.test_incoming}")
    print(f"\nNext steps:")
    print(f"1. Process payloads with: python tools/network_node_processor.py <payload> zones/visual")
    print(f"2. Check results in: {tester.test_zones}/visual/outputs/")


if __name__ == "__main__":
    main()
