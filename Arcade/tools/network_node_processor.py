#!/usr/bin/env python3
"""
Network Node Processor for Arcade

Processes moving network nodes routed to Arcade zones.
Analyzes node movements, tracks patterns, and generates visual outputs.
"""
import json
import sys
import time
from pathlib import Path
from typing import Dict, List, Any


class NetworkNodeProcessor:
    """Processes network node movement data in Arcade zones."""
    
    def __init__(self, zone_dir: Path):
        """
        Initialize node processor.
        
        Args:
            zone_dir: Zone directory for processing
        """
        self.zone_dir = Path(zone_dir)
        self.zone_dir.mkdir(parents=True, exist_ok=True)
        
        self.output_dir = self.zone_dir / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
    def process_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a network node payload.
        
        Args:
            payload: Node movement payload from router
            
        Returns:
            Processing results
        """
        tool = payload.get('tool', 'unknown')
        zone = payload.get('zone', 'unknown')
        node_states = payload.get('node_states', {})
        events = payload.get('movement_events', [])
        
        print(f"[Processor] Tool: {tool}, Zone: {zone}")
        print(f"[Processor] Processing {len(node_states)} nodes, {len(events)} events")
        
        # Analyze movement patterns
        analysis = self._analyze_movements(events)
        
        # Classify nodes by activity
        classification = self._classify_nodes(node_states, events)
        
        # Generate habitat report
        habitat_report = self._analyze_habitats(node_states)
        
        # Compile results
        results = {
            'timestamp': time.time(),
            'tool': tool,
            'zone': zone,
            'node_count': len(node_states),
            'event_count': len(events),
            'movement_analysis': analysis,
            'node_classification': classification,
            'habitat_report': habitat_report
        }
        
        # Save results
        self._save_results(results)
        
        return results
    
    def _analyze_movements(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze movement event patterns."""
        if not events:
            return {
                'total_events': 0,
                'avg_displacement': 0.0,
                'avg_velocity': 0.0,
                'max_displacement': 0.0,
                'max_velocity': 0.0
            }
        
        displacements = [e['displacement'] for e in events]
        velocities = [e['velocity_magnitude'] for e in events]
        
        return {
            'total_events': len(events),
            'avg_displacement': sum(displacements) / len(displacements),
            'avg_velocity': sum(velocities) / len(velocities),
            'max_displacement': max(displacements),
            'max_velocity': max(velocities),
            'active_nodes': len(set(e['node_id'] for e in events))
        }
    
    def _classify_nodes(
        self,
        node_states: Dict[str, Any],
        events: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Classify nodes by activity level."""
        # Get event counts per node
        event_counts = {}
        for event in events:
            node_id = event['node_id']
            event_counts[node_id] = event_counts.get(node_id, 0) + 1
        
        # Classify
        static_nodes = []
        slow_nodes = []
        active_nodes = []
        hyperactive_nodes = []
        
        for node_id, state in node_states.items():
            count = event_counts.get(node_id, 0)
            velocity = (state['vx']**2 + state['vy']**2)**0.5
            
            if count == 0:
                static_nodes.append(node_id)
            elif velocity < 0.5:
                slow_nodes.append(node_id)
            elif velocity < 2.0:
                active_nodes.append(node_id)
            else:
                hyperactive_nodes.append(node_id)
        
        return {
            'static': static_nodes,
            'slow': slow_nodes,
            'active': active_nodes,
            'hyperactive': hyperactive_nodes
        }
    
    def _analyze_habitats(self, node_states: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze node distribution across habitats."""
        habitat_counts = {}
        habitat_scores = {}
        
        for node_id, state in node_states.items():
            habitat = state['habitat']
            
            if habitat not in habitat_counts:
                habitat_counts[habitat] = 0
                habitat_scores[habitat] = []
            
            habitat_counts[habitat] += 1
            habitat_scores[habitat].append(state['nodeScore'])
        
        # Calculate average scores per habitat
        habitat_avg_scores = {
            h: sum(scores) / len(scores) if scores else 0.0
            for h, scores in habitat_scores.items()
        }
        
        return {
            'habitat_counts': habitat_counts,
            'habitat_avg_scores': habitat_avg_scores,
            'total_habitats': len(habitat_counts)
        }
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save processing results to output directory."""
        timestamp = int(time.time() * 1000)
        output_file = self.output_dir / f"network_analysis_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"[Processor] Results saved to: {output_file}")
        
        # Also save summary as latest
        latest_file = self.output_dir / "latest_analysis.json"
        with open(latest_file, 'w') as f:
            json.dump(results, f, indent=2)


def main():
    """Main entry point for network node processor."""
    if len(sys.argv) < 2:
        print("Usage: python network_node_processor.py <payload_file> [zone_dir]")
        sys.exit(1)
    
    payload_file = Path(sys.argv[1])
    zone_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    
    print(f"[Network Node Processor] Starting...")
    print(f"[Network Node Processor] Payload: {payload_file}")
    print(f"[Network Node Processor] Zone: {zone_dir}")
    
    # Load payload
    try:
        with open(payload_file, 'r') as f:
            payload = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load payload: {e}")
        sys.exit(1)
    
    # Process
    processor = NetworkNodeProcessor(zone_dir)
    results = processor.process_payload(payload)
    
    # Print summary
    print("\n" + "="*50)
    print("PROCESSING SUMMARY")
    print("="*50)
    print(f"Tool: {results['tool']}")
    print(f"Zone: {results['zone']}")
    print(f"Nodes: {results['node_count']}")
    print(f"Events: {results['event_count']}")
    print(f"\nMovement Analysis:")
    for key, value in results['movement_analysis'].items():
        print(f"  {key}: {value}")
    print(f"\nHabitat Distribution:")
    for habitat, count in results['habitat_report']['habitat_counts'].items():
        avg_score = results['habitat_report']['habitat_avg_scores'][habitat]
        print(f"  {habitat}: {count} nodes (avg score: {avg_score:.4f})")
    print("="*50)


if __name__ == "__main__":
    main()
