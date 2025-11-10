"""
Main Screen
Main arcade interface screen with terminal, sidebar, and status bar.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual import events

from ..widgets.terminal_output import TerminalOutput
from ..widgets.navigation_sidebar import NavigationSidebar
from ..widgets.status_bar import StatusBar
from ..widgets.command_input import CommandInput
from ..integration.tool_executor import ToolExecutor
from ..integration.game_controller import GameController


class MainScreen(Screen):
    """Main arcade interface screen."""
    
    BINDINGS = [
        ("f1", "help", "Help"),
        ("f2", "history", "History"),
        ("f3", "tools", "Tools"),
        ("escape", "back", "Back"),
        ("ctrl+c", "quit", "Quit"),
    ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tool_executor = ToolExecutor()
        self.game_controller = GameController()
    
    def compose(self) -> ComposeResult:
        """Compose main screen layout."""
        with Container(id="main-container"):
            with Horizontal():
                # Sidebar
                yield NavigationSidebar(
                    on_location_select=self.on_location_select,
                    id="sidebar"
                )
                
                # Main content area
                with Vertical():
                    # Terminal output
                    yield TerminalOutput(id="terminal-output")
                    
                    # Command input
                    yield CommandInput(
                        on_command=self.handle_command,
                        id="command-input"
                    )
            
            # Status bar
            yield StatusBar(id="status-bar")
    
    def on_mount(self) -> None:
        """Called when screen is mounted."""
        # Update status bar with initial state
        self.update_status()
        
        # Write welcome message
        terminal = self.query_one("#terminal-output", TerminalOutput)
        terminal.write_colored("🎟️ Arcade Terminal TUI", "magenta")
        terminal.write_colored("=" * 50, "cyan")
        terminal.write_colored("\nWelcome to the Arcade Terminal!", "green")
        terminal.write_colored("Type 'help' for commands or press F1 for help.\n", "cyan")
        terminal.write_colored("Try: analyze 808-bass | visualize 3d | game list\n", "yellow")
    
    def update_status(self):
        """Update status bar with current game state."""
        state = self.game_controller.get_state()
        status_bar = self.query_one("#status-bar", StatusBar)
        
        if state:
            status_bar.set_location(state.get('location', 'Arcade'))
            status_bar.set_score(state.get('score', 0))
            status_bar.set_level(state.get('level', 1))
            status_bar.set_speed(state.get('speed', 0.0))
    
    async def handle_command(self, command: str):
        """Handle command input."""
        terminal = self.query_one("#terminal-output", TerminalOutput)
        
        # Write command to terminal
        terminal.write_colored(f"\n> {command}", "cyan")
        
        # Check if it's a tool command
        tool_cmd = self.tool_executor.parse_command(command)
        if tool_cmd:
            await self.handle_tool_command(tool_cmd, terminal)
            return
        
        # Check if it's a game command
        result = self.game_controller.process_command(command)
        if result.get('success'):
            await self.handle_game_result(result, terminal)
        else:
            # Try as regular command
            terminal.write_colored(f"Command: {command}", "gray")
    
    async def handle_tool_command(self, tool_cmd: dict, terminal: TerminalOutput):
        """Handle tool command execution."""
        tool_name = tool_cmd['tool_name']
        args = tool_cmd['args']
        
        terminal.write_colored(f"\n🔧 Executing {tool_name}...", "yellow")
        
        def output_callback(line: str):
            """Stream output to terminal."""
            terminal.write(line)
        
        try:
            result = await self.tool_executor.execute(
                tool_name,
                args,
                output_callback=output_callback
            )
            
            if result.get('success'):
                terminal.write_colored("\n✅ Tool completed successfully", "green")
            else:
                terminal.write_colored(f"\n❌ Tool failed: {result.get('error', 'Unknown error')}", "red")
        except Exception as e:
            terminal.write_colored(f"\n❌ Error executing tool: {e}", "red")
        
        # Update status
        self.update_status()
    
    async def handle_game_result(self, result: dict, terminal: TerminalOutput):
        """Handle game command result."""
        message = result.get('message', '')
        if message:
            terminal.write_colored(message, "green")
        
        # Update status bar
        self.update_status()
    
    def on_location_select(self, location: str):
        """Handle location selection from sidebar."""
        result = self.game_controller.navigate_to(location)
        terminal = self.query_one("#terminal-output", TerminalOutput)
        
        if result.get('success'):
            terminal.write_colored(f"\n📍 Navigated to {location}", "cyan")
            self.update_status()
        else:
            terminal.write_colored(f"\n❌ Navigation failed: {result.get('message', 'Unknown error')}", "red")
    
    def action_help(self):
        """Show help."""
        terminal = self.query_one("#terminal-output", TerminalOutput)
        terminal.write_colored("\n📖 Help", "magenta")
        terminal.write_colored("=" * 50, "cyan")
        terminal.write_colored("\nAvailable Commands:", "yellow")
        terminal.write_colored("  analyze <type>     - Audio analysis tools", "cyan")
        terminal.write_colored("  visualize <type>   - Spatial visualization", "cyan")
        terminal.write_colored("  game <type>        - Play games", "cyan")
        terminal.write_colored("  playground         - Interactive playground", "cyan")
        terminal.write_colored("  cd <location>      - Navigate to location", "cyan")
        terminal.write_colored("  help               - Show this help", "cyan")
        terminal.write_colored("\nKeyboard Shortcuts:", "yellow")
        terminal.write_colored("  F1                 - Show help", "cyan")
        terminal.write_colored("  F2                 - Command history", "cyan")
        terminal.write_colored("  ESC                - Go back", "cyan")
        terminal.write_colored("  Ctrl+C             - Quit\n", "cyan")
    
    def action_history(self):
        """Show command history."""
        terminal = self.query_one("#terminal-output", TerminalOutput)
        command_input = self.query_one("#command-input", CommandInput)
        
        if command_input.history:
            terminal.write_colored("\n📜 Command History:", "magenta")
            for i, cmd in enumerate(command_input.history[-10:], 1):  # Last 10 commands
                terminal.write_colored(f"  {i}. {cmd}", "cyan")
        else:
            terminal.write_colored("\n📜 No command history yet", "gray")
    
    def action_tools(self):
        """Show tools menu."""
        terminal = self.query_one("#terminal-output", TerminalOutput)
        terminal.write_colored("\n🛠️ Available Tools:", "magenta")
        terminal.write_colored("=" * 50, "cyan")
        terminal.write_colored("\nAudio Analysis:", "yellow")
        terminal.write_colored("  analyze 808-bass", "cyan")
        terminal.write_colored("  analyze bass-delay", "cyan")
        terminal.write_colored("  analyze sound-effects", "cyan")
        terminal.write_colored("\nVisualization:", "yellow")
        terminal.write_colored("  visualize 3d", "cyan")
        terminal.write_colored("  visualize comprehensive", "cyan")
        terminal.write_colored("\nGames:", "yellow")
        terminal.write_colored("  game list", "cyan")
        terminal.write_colored("  game guessing", "cyan")
        terminal.write_colored("  game quiz", "cyan")
        terminal.write_colored("  game memory", "cyan")
    
    async def action_back(self) -> None:
        """Go back (no-op on main screen)."""
        pass
    
    async def action_quit(self) -> None:
        """Quit application."""
        await self.app.action_quit()

