#!/usr/bin/env python3
"""
ui_cli.py – Tiny "arc-theme" command line that calls dispatcher operations.
Integrated with Arcade Terminal system.
"""

import click
import pathlib
import subprocess
import sys
import os
import shutil
import textwrap
import logging

BASE_DIR = pathlib.Path(__file__).parent.resolve()
ZONES_ROOT = BASE_DIR / "zones"
INCOMING_DIR = BASE_DIR / "incoming"
CONF = BASE_DIR / "config" / "routing.yaml"
EXAMPLE_TOOLS = BASE_DIR / "example_tools"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------- #
# Some fun ASCII "theme-park" art for the prompt
# --------------------------------------------------------------- #
def park_prompt():
    return click.style("🎟️ Arcade:", fg="magenta") + click.style("~", fg="cyan") + click.style("$ ", fg="green")


# --------------------------------------------------------------- #
# 1️⃣  Start decorator
# --------------------------------------------------------------- #
@click.group()
def cli():
    """Arcade Terminal - Audio-Arcade Pipeline CLI
    
    🎟️ Arcade Terminal - A retro-style entertainment space with
    automated tool dispatching and zone routing.
    """
    pass


# --------------------------------------------------------------- #
# 2️⃣  Banner / "Tour" command
# --------------------------------------------------------------- #
@cli.command()
def tour():
    """Show a quick scenic tour of the arcade."""
    click.echo(textwrap.dedent(f"""
    {click.style("┌─────────────────────────────────────┐", fg="yellow")}
    {click.style("│ 🏰 Audio-Arcade Terminal Tour      │", fg="yellow")}
    {click.style("├─────────────────────────────────────┤", fg="yellow")}
    {click.style("│ 1️⃣  play <tool>  - Fire up a tool  │", fg="cyan")}
    {click.style("│ 2️⃣  log <zone>   - View zone logs   │", fg="cyan")}
    {click.style("│ 3️⃣  zones        - List all zones   │", fg="cyan")}
    {click.style("│ 4️⃣  status       - Check dispatcher│", fg="cyan")}
    {click.style("│ 5️⃣  run          - Start dispatcher │", fg="cyan")}
    {click.style("│ 6️⃣  web          - Open web UI      │", fg="cyan")}
    {click.style("└─────────────────────────────────────┘", fg="yellow")}
    """))


# --------------------------------------------------------------- #
# 3️⃣  Command to play a tool into the incoming folder
# --------------------------------------------------------------- #
@cli.command()
@click.argument("tool_name")
@click.option("--file", "-f", help="Path to tool file (optional)")
def play(tool_name, file):
    """Drop a tool into the dispatcher."""
    # If file path provided, use it
    if file:
        tool_path = pathlib.Path(file)
        if not tool_path.exists():
            click.echo(f"{click.style('❌', fg='red')} File not found: {file}")
            sys.exit(1)
    else:
        # Find a demo tool file in `example_tools/`
        demo_path = EXAMPLE_TOOLS / f"{tool_name}.py"
        if not demo_path.exists():
            click.echo(f"{click.style('❌', fg='red')} No demo tool called {tool_name}")
            click.echo(f"{click.style('💡', fg='yellow')} Available tools: {list_tools()}")
            sys.exit(1)
        tool_path = demo_path

    # Create a trigger file for the dispatcher
    trigger = INCOMING_DIR / f"{tool_name}.trigger"
    with open(trigger, "w") as fh:
        fh.write(tool_name + "\n")
        fh.write(f"This file triggers {tool_name}.\n")
        fh.write(f"Source: {tool_path}\n")
    
    # Copy the tool file to incoming
    tool_copy = INCOMING_DIR / f"{tool_name}.py"
    shutil.copy2(tool_path, tool_copy)
    
    click.echo(f"{click.style('✅', fg='green')} Triggered {tool_name} → {trigger}")
    click.echo(f"{click.style('📁', fg='cyan')} Tool file: {tool_copy}")


def list_tools():
    """List available example tools."""
    if not EXAMPLE_TOOLS.exists():
        return []
    return [f.stem for f in EXAMPLE_TOOLS.glob("*.py") if f.stem != "__init__"]


# --------------------------------------------------------------- #
# 4️⃣  View zone log
# --------------------------------------------------------------- #
@cli.command()
@click.argument("zone")
@click.option("--follow", "-f", is_flag=True, help="Follow log file (tail -f)")
def log(zone, follow):
    """View the latest log file in a zone."""
    zone_dir = ZONES_ROOT / zone
    if not zone_dir.is_dir():
        click.echo(f"{click.style('❌', fg='red')} Zone {zone} does not exist")
        click.echo(f"{click.style('💡', fg='yellow')} Available zones: {list_zones()}")
        sys.exit(1)

    logs = list(zone_dir.glob("*.log"))
    if not logs:
        click.echo(f"{click.style('⚠️', fg='yellow')} No logs in {zone} yet.")
        return

    latest = max(logs, key=lambda p: p.stat().st_ctime)
    click.echo(f"{click.style('📄', fg='cyan')} Showing {latest.name}:")
    click.echo("-" * 40)
    
    if follow:
        # Tail -f style following
        import time
        try:
            with open(latest, 'r') as f:
                # Read existing content
                f.seek(0, 2)  # Seek to end
                while True:
                    line = f.readline()
                    if line:
                        click.echo(line.rstrip())
                    else:
                        time.sleep(0.1)
        except KeyboardInterrupt:
            click.echo("\n" + "-" * 40)
    else:
        # Show entire log
        click.secho(open(latest).read(), fg="white")
        click.echo("-" * 40)


def list_zones():
    """List available zones."""
    if not ZONES_ROOT.exists():
        return []
    return [d.name for d in ZONES_ROOT.iterdir() if d.is_dir()]


# --------------------------------------------------------------- #
# 5️⃣  List zones
# --------------------------------------------------------------- #
@cli.command()
def zones():
    """List all available zones and their status."""
    if not ZONES_ROOT.exists():
        click.echo(f"{click.style('⚠️', fg='yellow')} No zones directory found")
        return
    
    zone_dirs = [d for d in ZONES_ROOT.iterdir() if d.is_dir()]
    if not zone_dirs:
        click.echo(f"{click.style('⚠️', fg='yellow')} No zones created yet")
        return
    
    click.echo(f"{click.style('🎯', fg='cyan')} Available Zones:")
    click.echo("-" * 40)
    
    for zone_dir in sorted(zone_dirs):
        logs = list(zone_dir.glob("*.log"))
        active_tools = [f.stem for f in zone_dir.glob("*.log") if f.stat().st_mtime > (os.path.getmtime(__file__) - 3600)]
        
        status = click.style("●", fg="green") if logs else click.style("○", fg="bright_black")
        click.echo(f"  {status} {zone_dir.name}")
        if logs:
            latest = max(logs, key=lambda p: p.stat().st_ctime)
            size = latest.stat().st_size
            click.echo(f"     Latest: {latest.name} ({size} bytes)")
    click.echo("-" * 40)


# --------------------------------------------------------------- #
# 6️⃣  Check dispatcher status
# --------------------------------------------------------------- #
@cli.command()
def status():
    """Check dispatcher status and active tools."""
    # Check if dispatcher is running
    import psutil
    
    dispatcher_running = False
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'dispatcher.py' in ' '.join(proc.info['cmdline'] or []):
                dispatcher_running = True
                click.echo(f"{click.style('✅', fg='green')} Dispatcher is running (PID: {proc.info['pid']})")
                break
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    if not dispatcher_running:
        click.echo(f"{click.style('⚠️', fg='yellow')} Dispatcher is not running")
        click.echo(f"{click.style('💡', fg='cyan')} Run 'arcade run' to start it")
    
    # Check incoming directory
    if INCOMING_DIR.exists():
        pending = list(INCOMING_DIR.glob("*.trigger"))
        if pending:
            click.echo(f"{click.style('📋', fg='cyan')} Pending triggers: {len(pending)}")
            for p in pending:
                click.echo(f"   - {p.name}")
        else:
            click.echo(f"{click.style('📋', fg='cyan')} No pending triggers")


# --------------------------------------------------------------- #
# 7️⃣  Start the dispatcher daemon
# --------------------------------------------------------------- #
@cli.command()
@click.option("--background", "-b", is_flag=True, help="Run in background")
def run(background):
    """Start dispatcher in a subprocess."""
    dispatcher_path = BASE_DIR / "dispatcher.py"
    
    if not dispatcher_path.exists():
        click.echo(f"{click.style('❌', fg='red')} dispatcher.py not found")
        sys.exit(1)
    
    # Check if already running
    import psutil
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'dispatcher.py' in ' '.join(proc.info['cmdline'] or []):
                click.echo(f"{click.style('⚠️', fg='yellow')} Dispatcher already running (PID: {proc.info['pid']})")
                return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    click.echo(f"{click.style('🚀', fg='green')} Starting dispatcher...")
    
    if background:
        # Start in background
        if os.name == 'nt':  # Windows
            subprocess.Popen(
                [sys.executable, str(dispatcher_path)],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:  # Unix
            subprocess.Popen(
                [sys.executable, str(dispatcher_path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        click.echo(f"{click.style('✅', fg='green')} Dispatcher started in background")
    else:
        # Run in foreground
        try:
            subprocess.run([sys.executable, str(dispatcher_path)])
        except KeyboardInterrupt:
            click.echo(f"\n{click.style('🛑', fg='yellow')} Dispatcher stopped")


# --------------------------------------------------------------- #
# 8️⃣  Open web UI
# --------------------------------------------------------------- #
@cli.command()
def web():
    """Open the Arcade Terminal web interface."""
    import webbrowser
    
    url = "http://localhost:7681"
    click.echo(f"{click.style('🌐', fg='cyan')} Opening web interface: {url}")
    click.echo(f"{click.style('💡', fg='yellow')} Make sure the server is running: python -m Arcade.api.server")
    
    webbrowser.open(url)


# --------------------------------------------------------------- #
# 9️⃣  Audio Analysis Commands
# --------------------------------------------------------------- #
@cli.command()
@click.argument('analysis_type', type=click.Choice(['808-bass', 'bass-delay', 'sound-effects', 'spectral']))
@click.option('--file', '-f', help='Audio file path (optional)')
@click.option('--effect', '-e', default='reverb', help='Effect type for sound-effects')
def analyze(analysis_type, file, effect):
    """Run audio analysis tools."""
    sys.path.insert(0, str(BASE_DIR))
    from tools.audio_analyzer import AudioAnalyzer
    
    analyzer = AudioAnalyzer()
    
    if analysis_type == '808-bass':
        analyzer.analyze_808_bass(file)
    elif analysis_type == 'bass-delay':
        analyzer.analyze_bass_vs_delay(file)
    elif analysis_type == 'sound-effects':
        analyzer.analyze_sound_effects(effect)
    elif analysis_type == 'spectral':
        analyzer.advanced_spectral_analysis(file)


# --------------------------------------------------------------- #
# 🔟  Spatial Visualization Commands
# --------------------------------------------------------------- #
@cli.command()
@click.argument('viz_type', type=click.Choice(['3d', 'comprehensive']))
@click.option('--source', nargs=3, type=float, default=[5.0, 0.0, 2.0], help='Source position (x y z)')
@click.option('--listener', nargs=3, type=float, default=[0.0, 0.0, 0.0], help='Listener position (x y z)')
@click.option('--save', is_flag=True, help='Save image instead of displaying')
def visualize(viz_type, source, listener, save):
    """Run spatial audio visualization."""
    sys.path.insert(0, str(BASE_DIR))
    from tools.spatial_visualizer import SpatialVisualizer
    
    visualizer = SpatialVisualizer()
    
    if viz_type == '3d':
        visualizer.visualize_3d_spatial(
            tuple(source),
            tuple(listener),
            save_image=save
        )
    elif viz_type == 'comprehensive':
        visualizer.visualize_comprehensive()


# --------------------------------------------------------------- #
# 1️⃣1️⃣  Interactive Playground Commands
# --------------------------------------------------------------- #
@cli.command()
@click.option('--demo', '-d', type=click.Choice(['audio', 'spatial', 'trajectory', 'preview', 'random']), help='Run specific demo')
def playground(demo):
    """Interactive playground with demos."""
    sys.path.insert(0, str(BASE_DIR))
    from tools.interactive_playground import InteractivePlayground
    
    playground = InteractivePlayground()
    
    if demo:
        playground.run_demo(demo)
    else:
        playground.show_menu()


@cli.command()
@click.argument('command', type=click.Choice(['chat', 'analyze', 'generate']))
@click.option('--message', '-m', help='Message for chat')
@click.option('--code', '-c', help='Code to analyze')
@click.option('--description', '-d', help='Description for code generation')
@click.option('--language', '-l', default='python', help='Programming language')
def ai(command, message, code, description, language):
    """AI assistant commands."""
    sys.path.insert(0, str(BASE_DIR))
    from tools.ai_assistant import AIAssistant
    
    assistant = AIAssistant()
    
    if command == 'chat':
        if not message:
            click.echo("Error: --message required for chat")
            return
        assistant.chat(message)
    elif command == 'analyze':
        if not code:
            click.echo("Error: --code required for analyze")
            return
        assistant.analyze_code(code, language)
    elif command == 'generate':
        if not description:
            click.echo("Error: --description required for generate")
            return
        assistant.generate_code(description, language)


# --------------------------------------------------------------- #
# 1️⃣2️⃣  Game Collection Commands
# --------------------------------------------------------------- #
@cli.command()
@click.argument('game', type=click.Choice(['list', 'guessing', 'quiz', 'memory', 'challenge']))
@click.option('--max', type=int, default=100, help='Max number for guessing game')
@click.option('--length', type=int, default=5, help='Sequence length for memory game')
def game(game, max, length):
    """Play mini-games."""
    sys.path.insert(0, str(BASE_DIR))
    from tools.game_collection import GameCollection
    
    games = GameCollection()
    
    if game == 'list':
        games.list_games()
    elif game == 'guessing':
        games.play_guessing(max)
    elif game == 'quiz':
        games.play_quiz()
    elif game == 'memory':
        games.play_memory(length)
    elif game == 'challenge':
        games.play_challenge()


# --------------------------------------------------------------- #
# 1️⃣3️⃣  Demo Command (alias for playground)
# --------------------------------------------------------------- #
@cli.command()
@click.argument('demo_type', type=click.Choice(['audio', 'spatial', 'trajectory', 'preview', 'random', 'interactive']))
def demo(demo_type):
    """Run interactive demos."""
    sys.path.insert(0, str(BASE_DIR))
    from tools.interactive_playground import InteractivePlayground
    
    playground = InteractivePlayground()
    
    if demo_type == 'interactive':
        playground.show_menu()
    else:
        playground.run_demo(demo_type)


# --------------------------------------------------------------- #
# 1️⃣4️⃣  Launch TUI
# --------------------------------------------------------------- #
@cli.command()
@click.option('--server', is_flag=True, help='Connect to server mode')
@click.option('--standalone', is_flag=True, default=True, help='Run in standalone mode')
def tui(server, standalone):
    """Launch the full-stack TUI interface."""
    import sys
    from pathlib import Path
    
    # Add Arcade to path
    sys.path.insert(0, str(BASE_DIR))
    
    try:
        from tui.main import main as tui_main
        
        # Prepare arguments for TUI
        if server:
            sys.argv = ['tui', '--server']
        else:
            sys.argv = ['tui', '--standalone']
        
        tui_main()
    except ImportError as e:
        click.echo(f"{click.style('❌', fg='red')} TUI dependencies not installed.")
        click.echo(f"{click.style('💡', fg='yellow')} Install with: pip install textual rich")
        click.echo(f"{click.style('⚠️', fg='yellow')} Error: {e}")
        sys.exit(1)
    except Exception as e:
        click.echo(f"{click.style('❌', fg='red')} Failed to launch TUI: {e}")
        sys.exit(1)


if __name__ == "__main__":
    cli()

