#!/usr/bin/env python3
"""
Conceptual Thermal Mapper (General-Purpose Edition)
===================================================
Lightweight visualization engine that transforms any Python data structure
into a smooth thermal topology. Zero configuration. No domain bias.
"""

import json
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Optional


@dataclass
class ThermalNode:
    """Atomic visualization unit"""
    name: str
    value: Any
    heat: float = 0.0
    stability: float = 0.5
    mass: float = 1.0
    coordinates: Tuple[float, float] = field(default_factory=lambda: (0.0, 0.0))
    articulation: str = ""


class ConceptualThermalMapper:
    """Universal topological visualizer for structured data"""

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
        else:
            if path not in self.nodes:
                self.nodes[path] = ThermalNode(name=path.split(".")[-1], value=obj, mass=0.5)
            if isinstance(obj, (int, float)):
                self.nodes[path].heat = self._normalize(obj)
                self.nodes[path].stability = 0.9

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
        """Basic deterministic radial layout"""
        for path, node in self.nodes.items():
            depth = path.count(".")
            angle = abs(hash(path)) % 360
            radius = 5 + depth * 2
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
        """Compact terminal summary"""
        print(f"\n📊 {self.title}\n")
        if not self.nodes:
            print("No nodes found.")
            return
        sorted_nodes = sorted(self.nodes.values(), key=lambda n: n.heat, reverse=True)
        print("Top hot regions:")
        for n in sorted_nodes[:3]:
            print(f"🔥 {n.name}: {n.articulation}")
        print("\nMost stable regions:")
        for n in sorted_nodes[-3:]:
            print(f"❄️ {n.name}: {n.articulation}")


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


if __name__ == "__main__":
    demo = {
        "team": {"members": 5, "velocity": 0.78},
        "pipeline": [32, 15, 8, 12],
        "config": {"debug": False, "version": "1.4.2"},
    }
    visualize(demo, title="System Snapshot")
