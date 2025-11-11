# compass_tool.py
"""
Coverage Oracle – “Compass” CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Ported from the original TypeScript UI.  
New options:

  -M, --module    Show details for a single module
  -S, --settings  JSON snippet to merge into the default state / phases
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

# --------------------------------------------------------------------------
# 1️⃣  Data models
# --------------------------------------------------------------------------
@dataclass
class Module:
    name: str
    coverage: int
    terrain: str
    energy: str


@dataclass
class Phase:
    id: int
    name: str
    subtitle: str
    celestial_event: str
    duration: str
    current_coverage: int
    target_coverage: int
    cosmic_alignment: str
    overview: str
    key_actions: List[Dict[str, Any]]
    expected_outcome: Dict[str, Any]
    rituals: List[str]
    warnings: List[str]


@dataclass
class OracularState:
    coverage: int
    target: int
    passing_tests: int
    failing_tests: int
    total_tests: int
    modules: List[Module] = field(default_factory=list)


# --------------------------------------------------------------------------
# 2️⃣  Default snapshot (used when no JSON supplied)
# --------------------------------------------------------------------------
DEFAULT_STATE = OracularState(
    coverage=16,
    target=80,
    passing_tests=108,
    failing_tests=42,
    total_tests=150,
    modules=[
        Module(
            name="core/security.py",
            coverage=59,
            terrain="🌲 Forest",
            energy="strong",
        ),
        Module(
            name="delay/core/delay_essence.py",
            coverage=22,
            terrain="🏜️ Desert",
            energy="awakening",
        ),
        Module(name="echo/core/core.py", coverage=0, terrain="🌋 Lava Zone", energy="dormant"),
        Module(
            name="network_integration.py",
            coverage=0,
            terrain="🌋 Lava Zone",
            energy="dormant",
        ),
    ],
)

# --------------------------------------------------------------------------
# 3️⃣  Prophecy phases – just a few for illustration
# --------------------------------------------------------------------------
#   Copy the *full* list of 4 phases from your original TypeScript file
#   (only Phase 1 is shown here to keep the file size reasonable.)
PROPHECY_PHASES: List[Phase] = [
    Phase(
        id=1,
        name="Phase 1: The Awakening",
        subtitle="Quick Wins – Conquering the Failing Tests",
        celestial_event="🌅 Dawn Phase",
        duration="1 Week (5–8 hrs)",
        current_coverage=16,
        target_coverage=30,
        cosmic_alignment="Mercury in Retrograde – Perfect for debugging",
        overview="The stars align for rapid conquest. Your failing tests are like meteors blocking your path – fix them and the heavens open.",
        key_actions=[
            {
                "action": "Fix visualization.py min(delays) bug",
                "impact": "🌟 Rescues 12 failing tests instantly",
                "technique": "Operator precedence ritual – guard both min() and max()",
                "cosmic_wisdom": "Like the moon controlling tides, proper precedence governs code flow",
            },
            {
                "action": "Implement matplotlib.use('Agg') across visualizers",
                "impact": "🌟 Conquers 8 headless test failures",
                "technique": "Backend binding incantation at module dawn",
                "cosmic_wisdom": "As light bends through different mediums, matplotlib adapts to different backends",
            },
        ],
        expected_outcome={
            "failingTests": "42 → 10",
            "coverageGain": "+14%",
            "newTerritory": "Base camp established in hostile terrain",
            "velocity": "+2.0% per day",
            "confidence": 95,
        },
        rituals=[
            "Run: pytest tests/ -v --tb=short | grep FAILED > fallen_tests.txt",
            "Apply fixes one by one, marking each in Test Navigator",
        ],
        warnings=[
            "⚠️ Don’t refactor during this phase – only fix bugs",
            "⚠️ Commit after each successful fix – preserve progress",
        ],
    ),
    # ▼ Phase 2, 3, 4 …
]

# --------------------------------------------------------------------------
# 4️⃣  Misc funcs
# --------------------------------------------------------------------------
def read_state_from_json(path: Path) -> OracularState:
    """Load a full coverage snapshot from file."""
    data = json.loads(path.read_text())
    modules = [Module(**m) for m in data["modules"]]
    return OracularState(
        coverage=data["coverage"],
        target=data["target"],
        passing_tests=data["passingTests"],
        failing_tests=data["failingTests"],
        total_tests=data["totalTests"],
        modules=modules,
    )


def merge_dict(dst: dict, src: dict) -> dict:
    """Simple deep‑merging: src overwrites dst, nested dicts are merged."""
    for k, v in src.items():
        if isinstance(v, dict) and k in dst and isinstance(dst[k], dict):
            dst[k] = merge_dict(dst[k], v)
        else:
            dst[k] = v
    return dst


def merge_state(state: OracularState, src: dict) -> None:
    for key in ("coverage", "target", "passing_tests", "failing_tests", "total_tests"):
        if key in src:
            setattr(state, key, src[key])
    if "modules" in src:
        state.modules = [Module(**m) for m in src["modules"]]


# --------------------------------------------------------------------------
# 5️⃣  Rich helpers (fallback shell if rich missing)
# --------------------------------------------------------------------------
try:
    from rich import print
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
except Exception:  # pragma: no cover
    class Dummy:
        def __getattr__(self, *_):  # pragma: no cover
            return lambda *_, **__: None

    console, print, Table, Panel = Dummy(), Dummy(), Dummy(), Dummy()

console = Console()


def progress_bar(rate: float, bar_len: int = 30) -> str:
    """Return a █░‑style bar; rate∈[0,1]"""
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    filled = int(bar_len * rate)
    return f"[{'█' * filled}{'░' * (bar_len - filled)}]"


def panel_fit(content: str, **attrs):
    """Compatibility wrapper for Rich.Panel.fit() that works across all Rich major releases."""
    try:
        return Panel.fit(content, **attrs)
    except TypeError:  # pragma: no cover – older Rich
        attrs.pop("expand", None)
        return Panel.fit(content, **attrs)


# --------------------------------------------------------------------------
# 6️⃣  Render helpers
# --------------------------------------------------------------------------
def render_header(state: OracularState) -> None:
    pct = min(1, state.coverage / state.target)
    bar = progress_bar(pct)
    panel = panel_fit(bar, title="Progress", subtitle="Journey to Summit")
    console.print(panel)


def render_phase_selector(active: int) -> None:
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Phase")
    table.add_column("Coverage")
    table.add_column("Goal")
    table.add_column("Status")
    for p in PROPHECY_PHASES:
        status = "[bold cyan]ACTIVE[/bold cyan]" if p.id == active else ""
        table.add_row(
            f"Phase {p.id}",
            f"{p.current_coverage}%",
            f"{p.target_coverage}%",
            status,
        )
    console.print(table)


def render_phase_view(phase: Phase) -> None:
    console.print(panel_fit(f"[bold magenta]{phase.name}[/bold magenta]", subtitle=phase.subtitle))
    console.print(
        f"[yellow][{phase.celestial_event}] {phase.duration}[/yellow]\n"
        f"Target gain: +{phase.target_coverage - phase.current_coverage}% | "
        f"Confidence: {phase.expected_outcome.get('confidence')}"
    )

    console.print("\n[bold cyan]Key Missions[/bold cyan]")
    for idx, act in enumerate(phase.key_actions, 1):
        console.print(
            f"\n[bold]Mission {idx} – {act['action']}[/bold]",
            f"[green]{act['impact']}[/green]",
            f"[blue]{act['technique']}[/blue]",
            f"[magenta]{act['cosmic_wisdom']}[/magenta]",
        )

    console.print("\n[bold green]Prophesied Outcomes[/bold green]")
    for k, v in phase.expected_outcome.items():
        console.print(f"  • [magenta]{k}:[/magenta] {v}")

    console.print("\n[bold yellow]Daily Rituals[/bold yellow]")
    for r in phase.rituals:
        console.print(f"  • [yellow]{r}")

    console.print("\n[bold red]Warnings[/bold red]")
    for w in phase.warnings:
        console.print(f"  • [red]{w}")


def render_map(state: OracularState, highlight: Optional[Module] = None) -> None:
    console.print("[bold magenta]Terrain Map – Module Coverage Landscape[/bold magenta]\n")
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Module")
    table.add_column("Coverage")
    table.add_column("Terrain")
    table.add_column("Energy")
    for m in state.modules:
        opts = ("bold white", "bold green dark")
        if highlight and m.name == highlight.name:
            opts = ("bold white on red", "bold red")
        table.add_row(
            f"[{opts[0]}]{m.name}",
            f"[{opts[0]}]{m.coverage}%",
            f"[{opts[1]}]{m.terrain}",
            f"[{opts[1]}]{m.energy}",
        )
    console.print(table)

    console.print("\n🗺️  Terrain Legend")
    console.print("🌋 Lava Zone – 0 %  (untested)")
    console.print("🏜️ Desert – 1–30 %")
    console.print("🌾 Plains – 31–60 %")
    console.print("🌲 Forest – 61–79 %")
    console.print("🏔️ Summit – 80 %+")


def render_module(state: OracularState, name: str) -> None:
    mod = next((m for m in state.modules if m.name == name), None)
    if not mod:
        console.print(f"[red]❌ Module not found: {name}[/red]")
        return
    console.print(panel_fit(f"[bold white]{mod.name}[/bold white]"))
    console.print(f"Coverage: [bold]{mod.coverage}%[/bold]")
    console.print(f"Terrain: {mod.terrain}")
    console.print(f"Energy: {mod.energy}")


# --------------------------------------------------------------------------
# 7️⃣  CLI driver
# --------------------------------------------------------------------------
def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(description="Coverage Oracle – Compass CLI")
    parser.add_argument(
        "--phase",
        "-p",
        type=int,
        choices=range(1, len(PROPHECY_PHASES) + 1),
        help="Show details for a specific phase",
    )
    parser.add_argument("--map", "-M", action="store_true", help="Show the terrain map")
    parser.add_argument(
        "--state",
        "-s",
        type=Path,
        help="Path to a full coverage snapshot JSON file",
    )
    parser.add_argument(
        "--settings",
        "-S",
        type=Path,
        help="Merge this JSON snippet into the defaults",
    )
    parser.add_argument(
        "--module",
        "-m",
        type=str,
        help="Show details for a single module (ignored if also given --map)",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
    )
    args = parser.parse_args(argv)

    # Load defaults
    state = DEFAULT_STATE
    # Load optional snapshot
    if args.state:
        if not args.state.is_file():
            console.print(f"[red]❌ File not found: {args.state}[/red]")
            sys.exit(1)
        state = read_state_from_json(args.state)

    # Merge settings snippet if present
    if args.settings:
        src = json.loads(args.settings.read_text())
        if "state" in src:
            merge_state(state, src["state"])
        if "phases" in src:
            global PROPHECY_PHASES
            PROPHECY_PHASES = [Phase(**p) for p in src["phases"]]

    # 1️⃣  Module view – takes precedence
    if args.module:
        render_module(state, args.module)
        return

    # 2️⃣  Phase view
    if args.phase is not None:
        ph = next(p for p in PROPHECY_PHASES if p.id == args.phase)
        render_phase_view(ph)
        return

    # 3️⃣  Map view
    if args.map:
        render_map(state)
        return

    # 4️⃣  Interactive mode (default)
    active = 1
    while True:
        os.system("clear" if os.name == "posix" else "cls")
        render_header(state)
        render_phase_selector(active)
        console.print("\nEnter phase number (1‑4), 'M' for map, 'Q' to quit:", style="bold")
        choice = input().strip().lower()
        if choice == "q":
            break
        if choice == "m":
            render_map(state)
            input("\nPress <Enter> to return…")
            continue
        if choice.isdigit() and 1 <= int(choice) <= len(PROPHECY_PHASES):
            active = int(choice)
            ph = next(p for p in PROPHECY_PHASES if p.id == active)
            render_phase_view(ph)
            input("\nPress <Enter> to return…")
        else:
            console.print("[red]❌ Unknown command[/red]")



if __name__ == "__main__":
    main(sys.argv[1:])
