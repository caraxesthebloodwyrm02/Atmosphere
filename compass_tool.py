# compass_tool.py (bug‑fixed)
"""
Coverage Oracle – “Compass” CLI
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Portable terminal helper for test coverage progress.

Author: Your Name – 2025
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

# ──────────────────────────────────────────────
# 1️⃣  Data structures
# ──────────────────────────────────────────────
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


# ──────────────────────────────────────────────
# 2️⃣  Default snapshot
# ──────────────────────────────────────────────
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

# ──────────────────────────────────────────────
# 3️⃣  Prophecy phases
# ──────────────────────────────────────────────
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
            "⚠️ Don't refactor during this phase – only fix bugs",
            "⚠️ Commit after each successful fix – preserve progress",
        ],
    ),
    Phase(
        id=2,
        name="Phase 2: The Ascent",
        subtitle="Expanding Coverage – Scaling the Peaks",
        celestial_event="☀️ Morning Phase",
        duration="2 Weeks (10–15 hrs)",
        current_coverage=30,
        target_coverage=60,
        cosmic_alignment="Mars in Ascendancy – Time for aggressive expansion",
        overview="With failing tests tamed, we now scale the coverage peaks, method by method, class by class.",
        key_actions=[
            {
                "action": "Add tests for core security module",
                "impact": "🌟 Increases coverage by 15%",
                "technique": "Parameterized testing for security validators",
                "cosmic_wisdom": "As the sun rises, so too shall your test coverage",
            },
            {
                "action": "Implement test generators for common patterns",
                "impact": "🌟 Reduces test writing time by 30%",
                "technique": "Pytest fixtures and parameterization",
                "cosmic_wisdom": "A single spark can start a prairie fire",
            },
        ],
        expected_outcome={
            "failingTests": "10 → 2",
            "coverageGain": "+30%",
            "newTerritory": "Base camp to mid-mountain",
            "velocity": "+1.5% per day",
            "confidence": 85,
        },
        rituals=[
            "Run: pytest --cov=src --cov-report=term-missing",
            "Review coverage reports and identify low-hanging fruit",
        ],
        warnings=[
            "⚠️ Watch for flaky tests – they're like avalanches waiting to happen",
            "⚠️ Keep test runs fast to maintain developer productivity",
        ],
    ),
    Phase(
        id=3,
        name="Phase 3: The Summit Push",
        subtitle="Hardening – The Final Ascent",
        celestial_event="🌇 Dusk Phase",
        duration="1 Week (5–8 hrs)",
        current_coverage=60,
        target_coverage=80,
        cosmic_alignment="Saturn's Rings Align – Time for discipline",
        overview="The air is thin at these altitudes. Every percentage point requires careful planning and execution.",
        key_actions=[
            {
                "action": "Tackle complex edge cases",
                "impact": "🌟 Final 10% coverage gain",
                "technique": "Property-based testing with Hypothesis",
                "cosmic_wisdom": "As the mountain gets steeper, each step requires more effort",
            },
            {
                "action": "Refactor for testability",
                "impact": "🌟 Makes remaining tests easier to write",
                "technique": "Dependency injection and interface segregation",
                "cosmic_wisdom": "A well-prepared base camp is key to a successful summit attempt",
            },
        ],
        expected_outcome={
            "failingTests": "2 → 0",
            "coverageGain": "+20%",
            "newTerritory": "Approaching the summit",
            "velocity": "+1.0% per day",
            "confidence": 75,
        },
        rituals=[
            "Run: pytest -x --pdb --cov-fail-under=80",
            "Review and update documentation for test patterns",
        ],
        warnings=[
            "⚠️ Diminishing returns – some modules may be hard to test",
            "⚠️ Consider if 100% coverage is necessary for all modules",
        ],
    ),
    Phase(
        id=4,
        name="Phase 4: The Summit",
        subtitle="Maintenance – Holding the High Ground",
        celestial_event="🌃 Night Phase",
        duration="Ongoing (1–2 hrs/week)",
        current_coverage=80,
        target_coverage=80,
        cosmic_alignment="Full Moon – Time for reflection",
        overview="You've reached the summit, but the work isn't over. Now we must hold this ground and prevent regression.",
        key_actions=[
            {
                "action": "Set up CI/CD enforcement",
                "impact": "🌟 Prevents coverage regression",
                "technique": "GitHub Actions with coverage thresholds",
                "cosmic_wisdom": "Eternal vigilance is the price of high coverage",
            },
            {
                "action": "Document test patterns",
                "impact": "🌟 Makes it easier to maintain tests",
                "technique": "Living documentation with examples",
                "cosmic_wisdom": "A well-documented codebase is a maintainable codebase",
            },
        ],
        expected_outcome={
            "failingTests": "0",
            "coverageGain": "+0% (maintenance)",
            "newTerritory": "The summit – enjoy the view!",
            "velocity": "Maintenance mode",
            "confidence": 90,
        },
        rituals=[
            "Weekly: Review coverage reports",
            "Monthly: Refactor tests for maintainability",
        ],
        warnings=[
            "⚠️ Don't let coverage become a vanity metric",
            "⚠️ Focus on test quality, not just quantity",
        ],
    ),
]

# ──────────────────────────────────────────────
# 4️⃣  Read state from JSON
# ──────────────────────────────────────────────
def read_state_from_json(path: Path) -> OracularState:
    """Load a full coverage snapshot from file."""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    modules = [Module(**m) for m in data.get("modules", [])]
    return OracularState(
        coverage=data["coverage"],
        target=data["target"],
        passing_tests=data["passingTests"],
        failing_tests=data["failingTests"],
        total_tests=data["totalTests"],
        modules=modules,
    )


def merge_state(state: OracularState, update_data: dict) -> OracularState:
    """Merge a JSON snippet into the current state."""
    if "coverage" in update_data:
        state.coverage = update_data["coverage"]
    if "target" in update_data:
        state.target = update_data["target"]
    if "passingTests" in update_data:
        state.passing_tests = update_data["passingTests"]
    if "failingTests" in update_data:
        state.failing_tests = update_data["failingTests"]
    if "totalTests" in update_data:
        state.total_tests = update_data["totalTests"]
    
    if "modules" in update_data:
        # Update or add modules
        for mod_data in update_data["modules"]:
            mod_name = mod_data["name"]
            # Find if module exists
            mod_exists = False
            for i, mod in enumerate(state.modules):
                if mod.name == mod_name:
                    # Update existing module
                    for key, value in mod_data.items():
                        setattr(state.modules[i], key, value)
                    mod_exists = True
                    break
            
            if not mod_exists:
                # Add new module
                state.modules.append(Module(**mod_data))
    
    return state

# ──────────────────────────────────────────────
# 5️⃣  Rich helpers (fallback if missing)
# ──────────────────────────────────────────────
import sys
import os

# Set up Windows console for UTF-8 if needed
if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleCP(65001)
    kernel32.SetConsoleOutputCP(65001)
    os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    from rich import print
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    
    # Initialize console with UTF-8 encoding
    console = Console(force_terminal=True, color_system="auto")
    
    def create_panel(content, title=None, subtitle=None):
        """Create a panel with the given content and title/subtitle"""
        if title:
            if subtitle:
                return Panel(content, title=title, subtitle=subtitle)
            return Panel(content, title=title)
        return Panel(content)
        
except Exception:  # pragma: no cover – rich missing
    class Dummy:
        def __getattr__(self, *_):  # pragma: no cover
            return lambda *_, **__: None
        
        def __call__(self, *args, **kwargs):
            return self
            
        def fit(self, *args, **kwargs):
            return self

    console = Dummy()
    print = console.print
    Table = Dummy
    Console = Dummy
    Panel = Dummy()
    create_panel = lambda *_, **__: None


def progress_bar(rate: float, bar_len: int = 30) -> str:
    if not 0 <= rate <= 1:
        raise ValueError("rate must be between 0 and 1")
    filled = int(bar_len * rate)
    # Use basic ASCII characters for better compatibility
    return f"[{'#' * filled}{'-' * (bar_len - filled)}]"


def panel_fit(content: str, **attrs):
    """Compatibility wrapper for Rich.Panel.fit()"""
    try:
        return Panel.fit(content, **attrs)
    except TypeError:  # pragma: no cover
        # older Rich – strip 'expand'
        attrs.pop("expand", None)
        return Panel.fit(content, **attrs)


def render_header(state: OracularState) -> None:
    pct = min(1, state.coverage / state.target)
    bar = progress_bar(pct)
    panel = create_panel(bar, title="Progress", subtitle="Journey to Summit")
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
    header = f"[bold magenta]{phase.name}[/bold magenta]"
    panel = create_panel(header, title=phase.name, subtitle=phase.subtitle)
    console.print(panel)

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
        # Highlight the specified module if provided
        if highlight and m.name == highlight.name:
            style = "bold red"
        else:
            style = "white"
            
        table.add_row(
            f"[{style}]{m.name}",
            f"[bold {style}]{m.coverage}%",
            f"[{style}]{m.terrain}",
            f"[{style}]{m.energy}",
        )
    console.print(table)


# ──────────────────────────────────────────────
# 6️⃣  CLI / Entry
# ──────────────────────────────────────────────
def render_module(state: OracularState, module_name: str) -> None:
    """Render details for a specific module."""
    module = None
    for mod in state.modules:
        if mod.name == module_name:
            module = mod
            break
    
    if not module:
        print(f"\n[red]Error:[/red] Module '{module_name}' not found.")
        return
    
    # Create a table for module details
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    table.add_row("Module:", f"[bold]{module.name}[/bold]")
    table.add_row("Coverage:", f"{module.coverage}%")
    table.add_row("Terrain:", module.terrain)
    table.add_row("Energy:", module.energy)
    
    console.print("\n[bold magenta]Module Details[/bold magenta]")
    console.print(table)
    
    # Show coverage bar
    pct = module.coverage / 100
    bar = progress_bar(pct)
    console.print("\n[bold]Coverage:[/bold]")
    console.print(bar)
    console.print(f"{module.coverage}% of code covered")


def main(argv: List[str]) -> None:
    parser = argparse.ArgumentParser(
        description="Coverage Oracle - Compass CLI for test coverage.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  Show module details:   compass_tool.py --module core/security.py
  Show map:              compass_tool.py --map
  Show phase 2:          compass_tool.py --phase 2
  Load custom settings:  compass_tool.py --settings patch.json
  Show module on map:    compass_tool.py --module echo/core/core.py --map
"""
    )
    parser.add_argument("--phase", "-p", type=int, choices=range(1, len(PROPHECY_PHASES) + 1))
    parser.add_argument("--map", "-m", action="store_true", help="Show the terrain map")
    parser.add_argument("--module", "-M", type=str, help="Show details for a specific module")
    parser.add_argument("--settings", "-s", type=Path, help="Path to JSON snippet to merge into the default state")
    parser.add_argument("--state", type=Path, help="Path to JSON with full coverage snapshot")
    args = parser.parse_args(argv)

    # Load initial state
    state = DEFAULT_STATE
    if args.state:
        state = read_state_from_json(args.state)
    
    # Apply settings if provided
    if args.settings:
        try:
            with open(args.settings, 'r', encoding='utf-8') as f:
                update_data = json.load(f)
            state = merge_state(state, update_data)
        except Exception as e:
            print(f"Error loading settings: {e}", file=sys.stderr)
            return 1
    
    # Handle module view
    if args.module:
        if args.map:
            # Show map with highlighted module
            module_to_highlight = next((m for m in state.modules if m.name == args.module), None)
            render_map(state, highlight=module_to_highlight)
        else:
            # Show module details
            render_module(state, args.module)
        return
    
    # Handle phase view
    if args.phase:
        phase = next((p for p in PROPHECY_PHASES if p.id == args.phase), None)
        if phase:
            render_phase_view(phase)
        else:
            print(f"Error: Phase {args.phase} not found.", file=sys.stderr)
        return
    
    # Handle map view
    if args.map:
        render_map(state)
        return
    
    # Interactive mode
    active = 1
    while True:
        try:
            os.system("cls" if os.name == "nt" else "clear")
            render_header(state)
            render_phase_selector(active)
            print("\nOptions:")
            print("1-4: Select phase")
            print("M: View map")
            print("Q: Quit")
            print("\nEnter your choice: ", end="", flush=True)
            
            choice = input().strip().lower()
            
            if choice == "q":
                break
            if choice == "m":
                render_map(state)
                input("\nPress Enter to return...")
                continue
            if choice.isdigit() and 1 <= int(choice) <= len(PROPHECY_PHASES):
                active = int(choice)
                phase = next(p for p in PROPHECY_PHASES if p.id == active)
                render_phase_view(phase)
                input("\nPress Enter to return...")
            else:
                print("\nInvalid choice. Please try again.")
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"\nAn error occurred: {e}")
            time.sleep(2)
    
    return 0


if __name__ == "__main__":
    main(sys.argv[1:])
