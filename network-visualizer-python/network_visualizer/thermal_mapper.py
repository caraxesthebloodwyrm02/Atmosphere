#!/usr/bin/env python3
"""
Conceptual Thermal Mapper - Network Visualizer Integration
===========================================================

Lightweight visualization engine that transforms network data and any Python
data structure into smooth thermal topologies. Zero configuration. No domain bias.
"""

import json
import math
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional, Set


@dataclass
class ThermalNode:
    """Atomic visualization unit with governance metadata"""
    name: str
    value: Any
    heat: float = 0.0
    stability: float = 0.5
    mass: float = 1.0
    coordinates: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    articulation: str = ""

    # Governance metadata
    node_id: str = field(default_factory=lambda: f"node_{id(None) % 10000:04d}")
    version: int = 1
    created_at: float = field(default_factory=time.time)
    last_modified: float = field(default_factory=time.time)
    semantic_tags: Set[str] = field(default_factory=set)
    validation_status: str = "pending"
    anomaly_score: float = 0.0

    def update_validation_status(self, status: str):
        """Update node validation status"""
        self.validation_status = status
        self.last_modified = time.time()

    def add_semantic_tag(self, tag: str):
        """Add semantic tag for governance"""
        self.semantic_tags.add(tag.lower())
        self.last_modified = time.time()

    def calculate_anomaly_score(self, global_stats: Dict[str, float]) -> float:
        """Calculate anomaly score based on global statistics"""
        heat_deviation = abs(self.heat - global_stats.get('mean_heat', 0.5))
        mass_deviation = abs(self.mass - global_stats.get('mean_mass', 1.0))
        stability_deviation = abs(self.stability - global_stats.get('mean_stability', 0.5))

        # Weighted anomaly score
        self.anomaly_score = (
            heat_deviation * 0.4 +
            mass_deviation * 0.3 +
            stability_deviation * 0.3
        )
        return self.anomaly_score


class ConceptualThermalMapper:
    """Universal topological visualizer for structured data and networks"""

    def __init__(self, data: Any, title: str = "Thermal Topology"):
        self.data = data
        self.title = title
        self.nodes: Dict[str, ThermalNode] = {}
        self.edges: List[Tuple[str, str, float]] = []
        self._extract(data, "root")
        self._compute_heat()
        self._map_coordinates()
        self._articulate()

    def _extract(self, obj: Any, path: str):
        """Recursive extraction of structures"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                child = f"{path}.{k}"
                self.nodes[child] = ThermalNode(name=k, value=v, mass=1.0 + len(str(v)) / 100)
                self.edges.append((path, child, 0.5))
                self._extract(v, child)
        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                child = f"{path}[{i}]"
                self.nodes[child] = ThermalNode(name=f"{path.split('.')[-1]}[{i}]", value=item, mass=0.8)
                self.edges.append((path, child, 0.3))
                self._extract(item, child)
        elif hasattr(obj, 'nodes') and hasattr(obj, 'edges'):  # NetworkX-like object
            self._extract_network(obj, path)
        else:
            if path not in self.nodes:
                self.nodes[path] = ThermalNode(name=path.split(".")[-1], value=obj, mass=0.5)
            if isinstance(obj, (int, float)):
                self.nodes[path].heat = self._normalize(obj)
                self.nodes[path].stability = 0.9

    def _extract_network(self, network, path: str):
        """Extract network structure (NetworkX compatible)"""
        # Add nodes
        for node_id, node_data in network.nodes(data=True):
            node_path = f"{path}.node_{node_id}"
            self.nodes[node_path] = ThermalNode(
                name=f"node_{node_id}",
                value=node_data,
                mass=1.0 + len(str(node_data)) / 100
            )

        # Add edges
        for source, target, edge_data in network.edges(data=True):
            source_path = f"{path}.node_{source}"
            target_path = f"{path}.node_{target}"
            weight = edge_data.get('weight', 1.0) if isinstance(edge_data, dict) else 1.0
            self.edges.append((source_path, target_path, weight))

    @staticmethod
    def _normalize(value: float) -> float:
        """Normalize numeric magnitude to 0–1"""
        if not math.isfinite(value):
            return 0.0
        return min(1.0, math.log1p(abs(value)) / math.log1p(1000))

    def _compute_heat(self):
        """Blend local and propagated heat signatures"""
        for parent, child, weight in self.edges:
            if parent in self.nodes and child in self.nodes:
                parent_heat = self.nodes[parent].heat
                child_heat = self.nodes[child].heat
                self.nodes[parent].heat = max(parent_heat, child_heat * weight)

    def _map_coordinates(self):
        """Basic deterministic radial layout with adaptive scaling"""
        if not self.nodes:
            return

        node_count = len(self.nodes)

        # Adaptive scaling: increase radius spread as node count grows
        # Base radius multiplier grows logarithmically with node count
        scale_factor = max(1.0, math.log2(node_count + 1) * 0.5)

        # Minimum and maximum scale bounds for visual clarity
        scale_factor = max(0.8, min(scale_factor, 3.0))

        for path, node in self.nodes.items():
            depth = path.count(".")
            angle = abs(hash(path)) % 360

            # Adaptive radius: base + depth contribution, scaled by node density
            base_radius = 5 * scale_factor
            depth_radius = depth * 2 * scale_factor
            radius = base_radius + depth_radius

            node.coordinates = (
                radius * math.cos(math.radians(angle)),
                radius * math.sin(math.radians(angle)),
            )

    def _articulate(self):
        """Generate plain-language articulation"""
        for node in self.nodes.values():
            heat_desc = self._heat_label(node.heat)
            stab_desc = self._stab_label(node.stability)
            v = node.value
            if isinstance(v, dict):
                node.articulation = f"{node.name}: {len(v)} nested elements, {heat_desc}, {stab_desc}."
            elif isinstance(v, list):
                node.articulation = f"{node.name}: sequence of {len(v)} items, {heat_desc}, {stab_desc}."
            elif isinstance(v, (int, float)):
                node.articulation = f"{node.name}: value={v:.2f}, {heat_desc}, {stab_desc}."
            else:
                node.articulation = f"{node.name}: {heat_desc}, {stab_desc}."

    @staticmethod
    def _heat_label(h: float) -> str:
        if h < 0.2: return "cold"
        if h < 0.4: return "cool"
        if h < 0.6: return "warm"
        if h < 0.8: return "hot"
        return "critical"

    @staticmethod
    def _stab_label(s: float) -> str:
        if s < 0.3: return "volatile"
        if s < 0.6: return "fluid"
        if s < 0.8: return "stable"
        return "solid"

    def render_terminal(self, width: int = 80, height: int = 24) -> str:
        """Render as ASCII heat field"""
        if not self.nodes:
            return "No data to visualize."
        canvas = [[" " for _ in range(width)] for _ in range(height)]
        xs = [n.coordinates[0] for n in self.nodes.values()]
        ys = [n.coordinates[1] for n in self.nodes.values()]
        min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
        x_range, y_range = max(max_x - min_x, 1), max(max_y - min_y, 1)
        chars = "·∘○◐●■"

        for n in self.nodes.values():
            x = int((n.coordinates[0] - min_x) / x_range * (width - 1))
            y = height - 1 - int((n.coordinates[1] - min_y) / y_range * (height - 1))
            idx = int(n.heat * (len(chars) - 1))
            canvas[y][x] = chars[idx]

        frame = [
            "╔" + "═" * (width - 2) + "╗",
            f"║{self.title:^{width-2}}║",
            "╠" + "═" * (width - 2) + "╣",
        ]
        frame.extend("║" + "".join(r) + "║" for r in canvas)
        frame.append("╚" + "═" * (width - 2) + "╝")
        frame.append("\n[Legend] Heat: ·∘○◐●■")
        frame.append(f"Nodes: {len(self.nodes)} | Edges: {len(self.edges)}")
        return "\n".join(frame)

    def validate_node_integrity(self) -> Dict[str, Any]:
        """Diagnostic: Validate node schema and attribute integrity"""
        validation_results = {
            'total_nodes': len(self.nodes),
            'valid_nodes': 0,
            'invalid_nodes': 0,
            'anomalies': [],
            'connectivity_issues': [],
            'schema_violations': []
        }

        for path, node in self.nodes.items():
            is_valid = True

            # Schema validation
            if not isinstance(node.name, str) or not node.name:
                validation_results['schema_violations'].append(f"{path}: invalid name")
                is_valid = False

            if not isinstance(node.heat, (int, float)) or not (0.0 <= node.heat <= 1.0):
                validation_results['schema_violations'].append(f"{path}: invalid heat value")
                is_valid = False

            if not isinstance(node.stability, (int, float)) or not (0.0 <= node.stability <= 1.0):
                validation_results['schema_violations'].append(f"{path}: invalid stability value")
                is_valid = False

            # Connectivity validation
            connected = any(path in edge[0] or path in edge[1] for edge in self.edges)
            if not connected and path != "root":
                validation_results['connectivity_issues'].append(f"{path}: orphaned node")

            # Mark validation status
            node.update_validation_status("valid" if is_valid else "invalid")

            if is_valid:
                validation_results['valid_nodes'] += 1
            else:
                validation_results['invalid_nodes'] += 1

        return validation_results

    def audit_thermal_properties(self) -> Dict[str, Any]:
        """Diagnostic: Audit thermal values and detect anomalies"""
        if not self.nodes:
            return {'error': 'No nodes to audit'}

        # Calculate global statistics
        heats = [node.heat for node in self.nodes.values()]
        masses = [node.mass for node in self.nodes.values()]
        stabilities = [node.stability for node in self.nodes.values()]

        global_stats = {
            'mean_heat': sum(heats) / len(heats),
            'mean_mass': sum(masses) / len(masses),
            'mean_stability': sum(stabilities) / len(stabilities),
            'max_heat': max(heats),
            'min_heat': min(heats),
            'heat_variance': sum((h - sum(heats)/len(heats))**2 for h in heats) / len(heats)
        }

        audit_results = {
            'global_stats': global_stats,
            'anomalies': [],
            'zero_heat_nodes': [],
            'outlier_nodes': [],
            'thermal_distribution': {}
        }

        # Analyze each node for anomalies
        for path, node in self.nodes.items():
            anomaly_score = node.calculate_anomaly_score(global_stats)

            if anomaly_score > 0.7:  # High anomaly threshold
                audit_results['anomalies'].append({
                    'path': path,
                    'score': anomaly_score,
                    'heat': node.heat,
                    'mass': node.mass,
                    'stability': node.stability
                })

            if node.heat == 0.0:
                audit_results['zero_heat_nodes'].append(path)

            # Outlier detection (simplified)
            if abs(node.heat - global_stats['mean_heat']) > 2 * math.sqrt(global_stats['heat_variance']):
                audit_results['outlier_nodes'].append(path)

        # Thermal distribution analysis
        heat_ranges = {'cold': 0, 'cool': 0, 'warm': 0, 'hot': 0, 'critical': 0}
        for node in self.nodes.values():
            if node.heat < 0.2: heat_ranges['cold'] += 1
            elif node.heat < 0.4: heat_ranges['cool'] += 1
            elif node.heat < 0.6: heat_ranges['warm'] += 1
            elif node.heat < 0.8: heat_ranges['hot'] += 1
            else: heat_ranges['critical'] += 1

        audit_results['thermal_distribution'] = heat_ranges

        return audit_results

    def optimize_topology_balance(self) -> Dict[str, Any]:
        """Optimization: Normalize mass and stabilize thermal properties"""
        if not self.nodes:
            return {'error': 'No nodes to optimize'}

        optimization_results = {
            'mass_normalization': {},
            'stability_adjustments': {},
            'coordinate_rebalancing': {},
            'nodes_optimized': 0
        }

        # Calculate target values
        all_masses = [node.mass for node in self.nodes.values()]
        target_mass = sum(all_masses) / len(all_masses)

        all_stabilities = [node.stability for node in self.nodes.values()]
        target_stability = 0.6  # Target for balanced stability

        # Optimize each node
        for path, node in self.nodes.items():
            changes_made = False

            # Mass normalization (prevent extreme outliers)
            if node.mass > target_mass * 2:
                old_mass = node.mass
                node.mass = min(node.mass * 0.8, target_mass * 1.5)
                optimization_results['mass_normalization'][path] = {
                    'old': old_mass,
                    'new': node.mass,
                    'reduction': old_mass - node.mass
                }
                changes_made = True

            # Stability tuning
            if abs(node.stability - target_stability) > 0.3:
                old_stability = node.stability
                # Gradually adjust toward target
                adjustment = (target_stability - node.stability) * 0.2
                node.stability = max(0.0, min(1.0, node.stability + adjustment))
                optimization_results['stability_adjustments'][path] = {
                    'old': old_stability,
                    'new': node.stability,
                    'adjustment': adjustment
                }
                changes_made = True

            if changes_made:
                optimization_results['nodes_optimized'] += 1
                node.last_modified = time.time()

        # Re-coordinate after optimization
        if optimization_results['nodes_optimized'] > 0:
            self._map_coordinates()
            optimization_results['coordinate_rebalancing'] = {
                'status': 'recalculated',
                'reason': 'topology optimization'
            }

        return optimization_results

    def apply_semantic_governance(self) -> Dict[str, Any]:
        """Governance: Apply semantic tags and version control"""
        governance_results = {
            'tags_applied': {},
            'version_snapshots': {},
            'traceability_matrix': {},
            'governed_nodes': 0
        }

        # Semantic tagging based on thermal properties
        for path, node in self.nodes.items():
            tags_added = []

            # Heat-based tags
            if node.heat > 0.8:
                node.add_semantic_tag('critical_thermal')
                tags_added.append('critical_thermal')
            elif node.heat < 0.2:
                node.add_semantic_tag('cold_zone')
                tags_added.append('cold_zone')

            # Stability-based tags
            if node.stability > 0.8:
                node.add_semantic_tag('high_stability')
                tags_added.append('high_stability')
            elif node.stability < 0.3:
                node.add_semantic_tag('volatile')
                tags_added.append('volatile')

            # Mass-based tags
            if node.mass > 3.0:
                node.add_semantic_tag('heavy_node')
                tags_added.append('heavy_node')

            # Path-based tags
            if 'config' in path.lower():
                node.add_semantic_tag('configuration')
                tags_added.append('configuration')
            elif 'error' in path.lower() or 'exception' in path.lower():
                node.add_semantic_tag('error_related')
                tags_added.append('error_related')

            if tags_added:
                governance_results['tags_applied'][path] = tags_added

            # Version snapshot
            governance_results['version_snapshots'][path] = {
                'version': node.version,
                'heat': node.heat,
                'stability': node.stability,
                'mass': node.mass,
                'coordinates': node.coordinates,
                'tags': list(node.semantic_tags)
            }

            governance_results['governed_nodes'] += 1

        return governance_results

    def monitor_topology_delta(self, baseline_snapshot: Optional[Dict] = None) -> Dict[str, Any]:
        """Governance: Monitor deviations from baseline"""
        current_snapshot = {}
        for path, node in self.nodes.items():
            current_snapshot[path] = {
                'heat': node.heat,
                'stability': node.stability,
                'mass': node.mass,
                'coordinates': node.coordinates,
                'tags': list(node.semantic_tags)
            }

        if baseline_snapshot is None:
            return {
                'baseline_created': True,
                'snapshot': current_snapshot,
                'deviations': {}
            }

        deviations = {}
        for path in set(baseline_snapshot.keys()) | set(current_snapshot.keys()):
            if path in baseline_snapshot and path in current_snapshot:
                baseline = baseline_snapshot[path]
                current = current_snapshot[path]

                path_deviations = {}
                for metric in ['heat', 'stability', 'mass']:
                    delta = current[metric] - baseline[metric]
                    if abs(delta) > 0.01:  # Significant change threshold
                        path_deviations[metric] = {
                            'delta': delta,
                            'baseline': baseline[metric],
                            'current': current[metric]
                        }

                coord_delta = math.sqrt(
                    (current['coordinates'][0] - baseline['coordinates'][0])**2 +
                    (current['coordinates'][1] - baseline['coordinates'][1])**2
                )
                if coord_delta > 1.0:
                    path_deviations['coordinates'] = {
                        'delta_distance': coord_delta,
                        'baseline': baseline['coordinates'],
                        'current': current['coordinates']
                    }

                if path_deviations:
                    deviations[path] = path_deviations

        return {
            'baseline_comparison': True,
            'total_deviations': len(deviations),
            'deviations': deviations,
            'current_snapshot': current_snapshot
        }

    def comprehensive_health_check(self) -> Dict[str, Any]:
        """Execute complete diagnostic and governance health check"""
        health_report = {
            'timestamp': time.time(),
            'overall_status': 'unknown',
            'component_status': {},
            'recommendations': [],
            'critical_issues': []
        }

        # Run all diagnostic checks
        try:
            validation = self.validate_node_integrity()
            health_report['component_status']['validation'] = 'passed' if validation['invalid_nodes'] == 0 else 'failed'
            if validation['invalid_nodes'] > 0:
                health_report['critical_issues'].extend(validation['schema_violations'])
                health_report['recommendations'].append("Fix schema violations in node attributes")

        except Exception as e:
            health_report['component_status']['validation'] = 'error'
            health_report['critical_issues'].append(f"Validation error: {e}")

        try:
            audit = self.audit_thermal_properties()
            health_report['component_status']['thermal_audit'] = 'passed'
            health_report['thermal_stats'] = audit['global_stats']

            if audit['anomalies']:
                health_report['recommendations'].append(f"Address {len(audit['anomalies'])} thermal anomalies")
                if len(audit['anomalies']) > len(self.nodes) * 0.1:  # >10% anomalies
                    health_report['critical_issues'].append("High anomaly rate detected")

        except Exception as e:
            health_report['component_status']['thermal_audit'] = 'error'
            health_report['critical_issues'].append(f"Thermal audit error: {e}")

        try:
            governance = self.apply_semantic_governance()
            health_report['component_status']['governance'] = 'passed'
            health_report['tagged_nodes'] = governance['governed_nodes']

        except Exception as e:
            health_report['component_status']['governance'] = 'error'
            health_report['critical_issues'].append(f"Governance error: {e}")

        # Overall status determination
        all_passed = all(status in ['passed', 'error'] for status in health_report['component_status'].values())
        has_critical = len(health_report['critical_issues']) > 0

        if all_passed and not has_critical:
            health_report['overall_status'] = 'healthy'
        elif has_critical:
            health_report['overall_status'] = 'critical'
        else:
            health_report['overall_status'] = 'degraded'

        return health_report

    def render_json(self) -> str:
        """Structured export"""
        payload = {
            "title": self.title,
            "nodes": [
                {
                    "id": p,
                    "name": n.name,
                    "value": str(n.value)[:80],
                    "heat": n.heat,
                    "stability": n.stability,
                    "mass": n.mass,
                    "x": n.coordinates[0],
                    "y": n.coordinates[1],
                    "articulation": n.articulation,
                }
                for p, n in self.nodes.items()
            ],
            "edges": [{"source": s, "target": t, "weight": w} for s, t, w in self.edges],
        }
        return json.dumps(payload, indent=2)

    def print_summary(self):
        """Compact terminal summary with governance info"""
        print(f"\n📊 {self.title}\n")
        if not self.nodes:
            print("No nodes found.")
            return
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.heat, reverse=True)
        print("🔥 Hotspots:")
        for n in sorted_nodes[:3]:
            tags = f" [{', '.join(n.semantic_tags)}]" if n.semantic_tags else ""
            print(f"  {n.name}: {n.articulation}{tags}")
        print("\n❄️ Cold zones:")
        for n in sorted_nodes[-3:]:
            tags = f" [{', '.join(n.semantic_tags)}]" if n.semantic_tags else ""
            print(f"  {n.name}: {n.articulation}{tags}")

        # Governance summary
        total_tags = sum(len(node.semantic_tags) for node in self.nodes.values())
        validated_nodes = sum(1 for node in self.nodes.values() if node.validation_status == 'valid')
        print(f"\n🏷️ Governance: {total_tags} tags applied, {validated_nodes}/{len(self.nodes)} nodes validated")


def visualize(data: Any, title: str = "", mode: str = "terminal"):
    """Entry point for visualization"""
    mapper = ConceptualThermalMapper(data, title or "Thermal Topology")
    if mode == "terminal":
        print(mapper.render_terminal())
        mapper.print_summary()
    elif mode == "json":
        print(mapper.render_json())
    else:
        raise ValueError("Mode must be 'terminal' or 'json'")
    return mapper


# $lash Mode - Compact, high-performance version
class ThermalMapperFlash:
    """Ultra-compact thermal mapper for high-throughput visualization"""

    def __init__(self, concept: Any, title: str = "Thermal Topology"):
        self.concept = concept
        self.title = title
        self.nodes = {}
        self.edges = []
        self._x(concept, "root")
        self._h()
        self._c()
        self._a()

    def _x(self, obj: Any, path: str):
        """Extract - compact version"""
        if isinstance(obj, dict):
            for k, v in obj.items():
                cp = f"{path}.{k}"
                self.nodes[cp] = ThermalNode(k, v, mass=1+len(str(v))/100)
                self.edges.append((path, cp, 0.5))
                self._x(v, cp)
        elif isinstance(obj, (list, tuple)):
            for i, item in enumerate(obj):
                cp = f"{path}[{i}]"
                self.nodes[cp] = ThermalNode(f"{path.split('.')[-1]}[{i}]", item, mass=0.8)
                self.edges.append((path, cp, 0.3))
                self._x(item, cp)
        else:
            if path not in self.nodes:
                self.nodes[path] = ThermalNode(path.split(".")[-1], obj, mass=0.5)
            if isinstance(obj, (int, float)):
                self.nodes[path].heat = min(1.0, math.log1p(abs(obj))/math.log1p(1000))
                self.nodes[path].stability = 0.9

    def _h(self):
        """Heat computation - compact"""
        hk = {'uncertainty', 'risk', 'latency', 'error', 'critical', 'breach'}
        ck = {'stable', 'healthy', 'success', 'compliant'}
        for p, n in self.nodes.items():
            if any(k in p.lower() for k in hk): n.heat = max(n.heat, 0.7)
            if any(k in p.lower() for k in ck): n.heat, n.stability = min(n.heat, 0.3), 0.9
            if n.mass > 5: n.heat = min(1.0, n.heat + 0.1)
        for pa, ch, w in self.edges:
            if pa in self.nodes and ch in self.nodes:
                self.nodes[pa].heat = max(self.nodes[pa].heat, self.nodes[ch].heat * w)

    def _c(self):
        """Coordinates - compact radial layout"""
        for p, n in self.nodes.items():
            d = p.count(".")
            a = abs(hash(p)) % 360
            r = 5 + d * 2
            n.coordinates = (r * math.cos(math.radians(a)), r * math.sin(math.radians(a)))

    def _a(self):
        """Articulation - compact"""
        for n in self.nodes.values():
            hd = "cold" if n.heat<0.2 else "cool" if n.heat<0.4 else "warm" if n.heat<0.6 else "hot" if n.heat<0.8 else "critical"
            sd = "volatile" if n.stability<0.3 else "fluid" if n.stability<0.6 else "stable" if n.stability<0.8 else "solid"
            v = n.value
            if isinstance(v, dict): n.articulation = f"{n.name}: {len(v)} nested, {hd}, {sd}."
            elif isinstance(v, list): n.articulation = f"{n.name}: {len(v)} items, {hd}, {sd}."
            elif isinstance(v, (int, float)): n.articulation = f"{n.name}: {v:.2f}, {hd}, {sd}."
            else: n.articulation = f"{n.name}: {hd}, {sd}."

    def render_terminal(self, w: int = 80, h: int = 24) -> str:
        """Compact ASCII renderer"""
        if not self.nodes: return "No data."
        c = [[" " for _ in range(w)] for _ in range(h)]
        xs, ys = [n.coordinates[0] for n in self.nodes.values()], [n.coordinates[1] for n in self.nodes.values()]
        mx, Mx, my, My = min(xs), max(xs), min(ys), max(ys)
        xr, yr = max(Mx-mx, 1), max(My-my, 1)
        chars = "·∘○◐●■"
        for n in self.nodes.values():
            x = int((n.coordinates[0]-mx)/xr*(w-1))
            y = h-1-int((n.coordinates[1]-my)/yr*(h-1))
            c[y][x] = chars[int(n.heat*(len(chars)-1))]
        f = [f"╔{'═'*(w-2)}╗", f"║{self.title:^{w-2}}║", f"╠{'═'*(w-2)}╣"]
        f.extend(f"║{''.join(r)}║" for r in c)
        f.append(f"╚{'═'*(w-2)}╝")
        f.append(f"\n[Legend] Heat: {chars} | Nodes: {len(self.nodes)} | Edges: {len(self.edges)}")
        return "\n".join(f)

    def render_json(self) -> str:
        """Compact JSON export"""
        return json.dumps({
            "title": self.title,
            "nodes": [{"id": p, "name": n.name, "value": str(n.value)[:80], "heat": n.heat, "stability": n.stability, "mass": n.mass, "x": n.coordinates[0], "y": n.coordinates[1], "articulation": n.articulation} for p, n in self.nodes.items()],
            "edges": [{"source": s, "target": t, "weight": w} for s, t, w in self.edges]
        }, indent=2)

    def print_summary(self):
        """Compact summary"""
        print(f"\n📊 {self.title}\n")
        if not self.nodes: return
        sn = sorted(self.nodes.values(), key=lambda n: n.heat, reverse=True)
        print("🔥 Hotspots:")
        for n in sn[:3]: print(f"  {n.name}: {n.articulation}")
        print("❄️ Cold zones:")
        for n in sn[-3:]: print(f"  {n.name}: {n.articulation}")


def visualize_flash(data: Any, title: str = "", mode: str = "terminal"):
    """Flash mode - ultra-compact visualization"""
    m = ThermalMapperFlash(data, title or "Thermal Topology")
    if mode == "terminal":
        print(m.render_terminal())
        m.print_summary()
    elif mode == "json":
        print(m.render_json())
    return m


# RAW Mode - Full-featured with advanced capabilities
class ConceptualThermalMapperRAW:
    """Full-featured thermal mapper with advanced capabilities"""

    def __init__(self, concept: Any, title: str = "Conceptual Topology"):
        self.concept = concept
        self.title = title
        self.nodes: Dict[str, ThermalNode] = {}
        self.edges: List[Tuple[str, str, float]] = []
        self.thermal_center: Tuple[float, float] = (0.0, 0.0)

        self._extract_concepts(self.concept, "root")
        self._infer_thermal_properties()
        self._map_coordinates()
        self._generate_articulation()

    def _extract_concepts(self, obj: Any, path: str):
        """Recursively extract every concept as a node"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                child_path = f"{path}.{key}"
                self.nodes[child_path] = ThermalNode(
                    name=key, value=value, mass=1 + len(str(value)) / 100.0
                )
                self._extract_concepts(value, child_path)
                if path != "root":
                    self.edges.append((path, child_path, 0.5))
        elif isinstance(obj, (list, tuple)):
            for idx, item in enumerate(obj):
                child_path = f"{path}[{idx}]"
                self.nodes[child_path] = ThermalNode(
                    name=f"{path.split('.')[-1]}[{idx}]", value=item, mass=0.8
                )
                self._extract_concepts(item, child_path)
                if path != "root":
                    self.edges.append((path, child_path, 0.3))
        elif hasattr(obj, 'nodes') and hasattr(obj, 'edges'):
            self._extract_network(obj, path)
        else:
            if path not in self.nodes:
                self.nodes[path] = ThermalNode(
                    name=path.split(".")[-1], value=obj, mass=0.5
                )
            if isinstance(obj, (int, float)):
                self.nodes[path].heat = self._normalize_to_heat(obj)
                self.nodes[path].stability = 0.9

    def _extract_network(self, network, path: str):
        """Extract network structure (NetworkX compatible)"""
        for node_id, node_data in network.nodes(data=True):
            node_path = f"{path}.node_{node_id}"
            self.nodes[node_path] = ThermalNode(
                name=f"node_{node_id}", value=node_data, mass=1.0 + len(str(node_data)) / 100
            )
        for source, target, edge_data in network.edges(data=True):
            source_path = f"{path}.node_{source}"
            target_path = f"{path}.node_{target}"
            weight = edge_data.get('weight', 1.0) if isinstance(edge_data, dict) else 1.0
            self.edges.append((source_path, target_path, weight))

    def _normalize_to_heat(self, value: float) -> float:
        """Convert any numeric to 0-1 heat signature"""
        if math.isinf(value) or math.isnan(value):
            return 0.0
        abs_val = abs(value)
        if abs_val > 1.0:
            return min(1.0, math.log1p(abs_val) / math.log1p(1000))
        return abs_val

    def _infer_thermal_properties(self):
        """Propagate heat and stability through the graph"""
        heat_keywords = {'uncertainty', 'risk', 'latency', 'error', 'critical', 'breach'}
        cold_keywords = {'stable', 'healthy', 'success', 'compliant'}

        for path, node in self.nodes.items():
            if any(kw in path.lower() for kw in heat_keywords):
                node.heat = max(node.heat, 0.7)
            if any(kw in path.lower() for kw in cold_keywords):
                node.heat = min(node.heat, 0.3)
                node.stability = 0.9
            if node.mass > 5.0:
                node.heat = min(1.0, node.heat + 0.1)

        for parent, child, weight in self.edges:
            if parent in self.nodes and child in self.nodes:
                child_heat = self.nodes[child].heat
                parent_heat = self.nodes[parent].heat
                self.nodes[parent].heat = max(parent_heat, child_heat * weight)

    def _map_coordinates(self):
        """Map nodes to 2D space using simple force-directed layout"""
        for path, node in self.nodes.items():
            depth = path.count(".")
            angle = hash(path) % 360
            radius = 5 + depth * 3
            node.coordinates = (
                radius * math.cos(math.radians(angle)),
                radius * math.sin(math.radians(angle))
            )

        for _ in range(1):
            for parent, child, weight in self.edges:
                p_node = self.nodes[parent]
                c_node = self.nodes[child]
                dx = p_node.coordinates[0] - c_node.coordinates[0]
                dy = p_node.coordinates[1] - c_node.coordinates[1]
                force = weight * 0.5
                c_node.coordinates = (
                    c_node.coordinates[0] + dx * force,
                    c_node.coordinates[1] + dy * force
                )

    def _generate_articulation(self):
        """Generate natural language explanations"""
        for path, node in self.nodes.items():
            heat_desc = self._describe_heat(node.heat)
            stability_desc = self._describe_stability(node.stability)

            if isinstance(node.value, dict):
                node.articulation = f"{node.name} is a {heat_desc} conceptual cluster with {len(node.value)} sub-components. It feels {stability_desc}."
            elif isinstance(node.value, list):
                node.articulation = f"{node.name} is a {heat_desc} sequence of {len(node.value)} items, currently {stability_desc}."
            elif isinstance(node.value, (int, float)):
                node.articulation = f"{node.name} measures {node.value:.2f}, which is {heat_desc}. Signal is {stability_desc}."
            else:
                node.articulation = f"{node.name} holds '{node.value}', a {heat_desc} qualitative marker. Interpret with caution."

    def _describe_heat(self, heat: float) -> str:
        if heat < 0.2: return "cold"
        if heat < 0.4: return "cool"
        if heat < 0.6: return "warm"
        if heat < 0.8: return "hot"
        return "critical"

    def _describe_stability(self, stability: float) -> str:
        if stability < 0.3: return "volatile"
        if stability < 0.6: return "fluid"
        if stability < 0.8: return "stable"
        return "solid"

    def render_terminal(self, width: int = 80, height: int = 24) -> str:
        """Render as ASCII thermal map"""
        canvas = [[" " for _ in range(width)] for _ in range(height)]

        if not self.nodes:
            return "No concepts to visualize."

        min_x = min(n.coordinates[0] for n in self.nodes.values())
        max_x = max(n.coordinates[0] for n in self.nodes.values())
        min_y = min(n.coordinates[1] for n in self.nodes.values())
        max_y = max(n.coordinates[1] for n in self.nodes.values())

        x_range = max_x - min_x if max_x != min_x else 1
        y_range = max_y - min_y if max_y != min_y else 1

        heat_chars = "·∘○◐●■"

        for path, node in self.nodes.items():
            x = int((node.coordinates[0] - min_x) / x_range * (width - 1))
            y = int((node.coordinates[1] - min_y) / y_range * (height - 1))
            y = height - 1 - y

            heat_idx = int(node.heat * (len(heat_chars) - 1))
            char = heat_chars[heat_idx]

            if node.stability < 0.5:
                char = char.lower() if char.isalpha() else char

            canvas[y][x] = char

        output = []
        output.append("╔" + "═" * (width - 2) + "╗")
        output.append(f"║{self.title:^{width-2}}║")
        output.append("╠" + "═" * (width - 2) + "╣")

        for row in canvas:
            output.append("║" + "".join(row) + "║")

        output.append("╚" + "═" * (width - 2) + "╝")

        output.append("\n[Legend] Heat: ·∘○◐●■  Stability: lowercase=volatile")
        output.append(f"Nodes: {len(self.nodes)} | Edges: {len(self.edges)} | Center: {self.thermal_center}")

        return "\n".join(output)

    def render_json(self) -> str:
        """Export as interactive JSON for web visualization"""
        return json.dumps({
            "title": self.title,
            "nodes": [
                {
                    "id": path,
                    "name": node.name,
                    "value": str(node.value)[:50],
                    "heat": node.heat,
                    "stability": node.stability,
                    "mass": node.mass,
                    "x": node.coordinates[0],
                    "y": node.coordinates[1],
                    "articulation": node.articulation
                }
                for path, node in self.nodes.items()
            ],
            "edges": [
                {"source": src, "target": dst, "weight": w}
                for src, dst, w in self.edges
            ],
            "thermal_center": self.thermal_center
        }, indent=2)

    def print_articulation(self, focus_path: Optional[str] = None):
        """Print natural language explanation"""
        print(f"\n🔍 Articulation: {self.title}\n")

        if focus_path and focus_path in self.nodes:
            node = self.nodes[focus_path]
            print(f"Focused on '{node.name}':")
            print(f"  → {node.articulation}")
            print(f"  → Heat: {node.heat:.2f}, Stability: {node.stability:.2f}")
        else:
            hot_nodes = sorted(self.nodes.items(), key=lambda x: x[1].heat, reverse=True)[:3]
            print("Thermal Hotspots:")
            for path, node in hot_nodes:
                print(f"  🔥 {path}: {node.articulation}")

            cold_nodes = sorted(self.nodes.items(), key=lambda x: x[1].heat)[:3]
            print("\nCold Zones:")
            for path, node in cold_nodes:
                print(f"  ❄️  {path}: {node.articulation}")

            if any('safety' in path.lower() for path in self.nodes):
                print("\nSafety Constraints: Active")
            if any('privacy' in path.lower() for path in self.nodes):
                print("Privacy Budget: Tracked")


def visualizeRAW(concept: Any, title: str = "", mode: str = "terminal", focus: Optional[str] = None):
    """
    RAW mode - Full-featured thermal visualization with advanced capabilities

    Args:
        concept: Any Python object (dict, list, class, primitive)
        title: Title for the visualization
        mode: "terminal", "json", or "articulation"
        focus: Specific node path to articulate in detail
    """
    mapper = ConceptualThermalMapperRAW(concept, title or "Conceptual Topology")

    if mode == "terminal":
        print(mapper.render_terminal())
        mapper.print_articulation(focus)
    elif mode == "json":
        print(mapper.render_json())
    elif mode == "articulation":
        mapper.print_articulation(focus)
    else:
        raise ValueError(f"Unknown mode: {mode}")

    return mapper


# Enhanced visualize function with mode selection
def visualize(data: Any, title: str = "", mode: str = "terminal", variant: str = "standard", focus: Optional[str] = None):
    """
    Enhanced visualization with multiple variants

    Args:
        data: Any Python data structure
        title: Visualization title
        mode: "terminal", "json", or "articulation"
        variant: "standard", "flash", or "RAW"
        focus: Specific node path for detailed articulation (RAW mode only)
    """
    # Import feature manager for checks
    try:
        from .feature_manager import feature_manager
    except ImportError:
        # Fallback if feature manager not available
        class DummyFeatureManager:
            def is_enabled(self, feature): return True  # Allow all if no manager
        feature_manager = DummyFeatureManager()

    if variant == "flash" or variant == "$lash":
        if not feature_manager.is_enabled("thermal_mapper_flash"):
            print("❌ Flash thermal mapper not enabled. Use: network-visualizer features enable thermal_mapper_flash")
            return None
        return visualize_flash(data, title, mode)
    elif variant == "RAW":
        if not feature_manager.is_enabled("thermal_mapper_raw"):
            print("❌ RAW thermal mapper not enabled. Use: network-visualizer features enable thermal_mapper_raw")
            return None
        return visualizeRAW(data, title, mode, focus)
    else:  # standard - always available
        mapper = ConceptualThermalMapper(data, title or "Thermal Topology")
        if mode == "terminal":
            print(mapper.render_terminal())
            mapper.print_summary()
        elif mode == "json":
            print(mapper.render_json())
        else:
            raise ValueError("Mode must be 'terminal' or 'json'")
        return mapper


# Network Visualizer Integration
class ThermalNetworkVisualizer:
    """Network visualization using thermal mapping"""

    def __init__(self, network_data=None):
        self.network_data = network_data
        self.mapper = None

    def load_network(self, network):
        """Load network data (NetworkX compatible)"""
        self.network_data = network
        return self

    def analyze_thermal_properties(self):
        """Analyze thermal properties of the network"""
        if not self.network_data:
            raise ValueError("No network data loaded")

        self.mapper = ConceptualThermalMapper(self.network_data, "Network Thermal Analysis")
        return self.mapper

    def render_terminal(self, **kwargs):
        """Render network as thermal topology"""
        if not self.mapper:
            self.analyze_thermal_properties()
        return self.mapper.render_terminal(**kwargs)

    def render_json(self):
        """Export network thermal analysis as JSON"""
        if not self.mapper:
            self.analyze_thermal_properties()
        return self.mapper.render_json()


if __name__ == "__main__":
    demo = {
        "team": {"members": 5, "velocity": 0.78},
        "pipeline": [32, 15, 8, 12],
        "config": {"debug": False, "version": "1.4.2"},
    }
    visualize(demo, title="System Snapshot")
