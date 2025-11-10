# Full-Stack TUI Implementation Plan

## Overview
Transform the Arcade Terminal from a web-based terminal with CLI commands into a full-stack Text User Interface (TUI) application using `textual` framework. The TUI will provide a rich, interactive terminal experience with multi-panel layouts, real-time updates, and integrated access to all Arcade features.

## Architecture Decisions
- **Framework**: `textual` (Python) - Modern reactive TUI framework built on `rich`
- **Architecture**: Standalone TUI app with optional server connection for WebSocket features
- **Layout**: Multi-panel layout with terminal output, navigation sidebar, status bar, and tool panels
- **Features**: All existing features integrated (games, tools, playground, navigation)

## Implementation Plan

### Phase 1: Core TUI Infrastructure

#### 1.1 Create TUI Application Structure
- **File**: `Arcade/tui/__init__.py`
  - Initialize TUI module
  - Export main TUI classes

- **File**: `Arcade/tui/app.py`
  - Main `textual.app.App` subclass
  - Application lifecycle management
  - Screen/window management
  - Key bindings (F1 help, F2 history, F3 tools, ESC back, etc.)
  - Theme management (retro arcade colors)

- **File**: `Arcade/tui/layout.py`
  - Layout definitions for different screens
  - Multi-panel layouts (terminal, sidebar, status bar)
  - Responsive layout handlers

#### 1.2 Core Widgets
- **File**: `Arcade/tui/widgets/terminal_output.py`
  - Terminal output widget using `rich.console.Console`
  - ANSI color code support
  - Scrollable output buffer
  - Real-time output streaming

- **File**: `Arcade/tui/widgets/navigation_sidebar.py`
  - Sidebar widget with navigation menu
  - Location/city list (Arcade, Echoes, Reverb, Delay)
  - Quick access to tools and games
  - Collapsible sections

- **File**: `Arcade/tui/widgets/status_bar.py`
  - Status bar at bottom
  - Current location, score, level, speed
  - Connection status (if server connected)
  - Real-time updates

- **File**: `Arcade/tui/widgets/command_input.py`
  - Command input widget with history
  - Auto-completion support
  - Command suggestions
  - Integration with existing tool commands

### Phase 2: Screen Management

#### 2.1 Main Screen
- **File**: `Arcade/tui/screens/main_screen.py`
  - Main arcade interface screen
  - Combines terminal output, sidebar, status bar
  - Command input at bottom
  - Game state display

#### 2.2 Tool Screens
- **File**: `Arcade/tui/screens/audio_analyzer_screen.py`
  - Full-screen audio analysis interface
  - Input forms for analysis parameters
  - Real-time result display
  - Integration with `tools/audio_analyzer.py`

- **File**: `Arcade/tui/screens/spatial_visualizer_screen.py`
  - Spatial visualization interface
  - Position input controls
  - ASCII visualization display
  - Integration with `tools/spatial_visualizer.py`

- **File**: `Arcade/tui/screens/game_screen.py`
  - Game collection interface
  - Game selection menu
  - Game-specific UI (guessing, quiz, memory)
  - Score tracking display

- **File**: `Arcade/tui/screens/playground_screen.py`
  - Interactive playground interface
  - Demo selection menu
  - Real-time demo output
  - Integration with `tools/interactive_playground.py`

#### 2.3 Navigation Screen
- **File**: `Arcade/tui/screens/navigation_screen.py`
  - City/location navigation interface
  - Visual location map
  - History navigation (time travel)
  - Integration with `api/game_engine.py`

#### 2.4 Help Screen
- **File**: `Arcade/tui/screens/help_screen.py`
  - Help documentation screen
  - Command reference
  - Keyboard shortcuts
  - Scrollable help content

### Phase 3: Integration Layer

#### 3.1 Tool Integration
- **File**: `Arcade/tui/integration/tool_executor.py`
  - Execute tools with output capture
  - Stream output to terminal widget
  - Handle tool errors gracefully
  - Integration with `api/tool_integration.py`

#### 3.2 Game Engine Integration
- **File**: `Arcade/tui/integration/game_controller.py`
  - Game state management
  - Navigation commands
  - Score tracking
  - Integration with `api/game_engine.py`

#### 3.3 Server Connection (Optional)
- **File**: `Arcade/tui/integration/server_client.py`
  - WebSocket client for server connection
  - Optional server mode
  - Real-time updates from server
  - Fallback to standalone mode

### Phase 4: Entry Point and Configuration

#### 4.1 Main Entry Point
- **File**: `Arcade/tui/main.py`
  - Main entry point for TUI application
  - Argument parsing (--server, --standalone)
  - Initialize and run TUI app
  - Error handling and graceful shutdown

#### 4.2 TUI Configuration
- **File**: `Arcade/config/tui_config.yaml`
  - TUI-specific configuration
  - Theme settings
  - Layout preferences
  - Key binding customizations

#### 4.3 Update CLI
- **File**: `Arcade/ui_cli.py`
  - Add `tui` command to launch TUI
  - Keep existing CLI commands for scripting
  - Add `--tui` flag option

### Phase 5: Enhanced Features

#### 5.1 Command History
- **File**: `Arcade/tui/widgets/command_history.py`
  - Persistent command history
  - History navigation (up/down arrows)
  - Search through history
  - History file management

#### 5.2 Auto-completion
- **File**: `Arcade/tui/widgets/completion.py`
  - Command auto-completion
  - Tool name completion
  - Parameter suggestions
  - Integration with existing commands

#### 5.3 Real-time Updates
- **File**: `Arcade/tui/widgets/updates.py`
  - Real-time game state updates
  - Tool execution progress
  - Status bar refresh
  - Event-driven updates

### Phase 6: Styling and Theming

#### 6.1 Arcade Theme
- **File**: `Arcade/tui/themes/arcade_theme.css`
  - Retro arcade color scheme
  - Green/cyan/magenta palette
  - Neon glow effects (using rich markup)
  - Consistent with existing web colors

#### 6.2 Theme Application
- Apply theme in `app.py`
- Color mappings for different widget types
- Status indicators (success, error, warning)

### Phase 7: Dependencies and Documentation

#### 7.1 Update Requirements
- **File**: `Arcade/requirements.txt`
  - Add `textual>=0.40.0`
  - Ensure `rich>=13.0.0` (textual dependency)
  - Keep existing dependencies

#### 7.2 Documentation
- **File**: `Arcade/TUI.md`
  - TUI usage guide
  - Keyboard shortcuts
  - Screen navigation
  - Feature overview

#### 7.3 Update README
- **File**: `Arcade/README.md`
  - Add TUI section
  - Installation instructions
  - Usage examples
  - Launch command

## File Structure
```
Arcade/
├── tui/
│   ├── __init__.py
│   ├── app.py                    # Main TUI application
│   ├── main.py                   # Entry point
│   ├── layout.py                 # Layout definitions
│   ├── widgets/
│   │   ├── __init__.py
│   │   ├── terminal_output.py
│   │   ├── navigation_sidebar.py
│   │   ├── status_bar.py
│   │   ├── command_input.py
│   │   ├── command_history.py
│   │   └── completion.py
│   ├── screens/
│   │   ├── __init__.py
│   │   ├── main_screen.py
│   │   ├── audio_analyzer_screen.py
│   │   ├── spatial_visualizer_screen.py
│   │   ├── game_screen.py
│   │   ├── playground_screen.py
│   │   ├── navigation_screen.py
│   │   └── help_screen.py
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── tool_executor.py
│   │   ├── game_controller.py
│   │   └── server_client.py
│   └── themes/
│       ├── __init__.py
│       └── arcade_theme.css
├── config/
│   └── tui_config.yaml           # TUI configuration
└── TUI.md                         # TUI documentation
```

## Key Implementation Details

### Textual App Structure
```python
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer, Static, Input, RichLog

class ArcadeApp(App):
    CSS_PATH = "arcade_theme.css"
    BINDINGS = [
        ("f1", "help", "Help"),
        ("f2", "history", "History"),
        ("f3", "tools", "Tools"),
        ("escape", "back", "Back"),
    ]
```

### Terminal Output Widget
- Use `RichLog` widget for scrollable output
- Capture tool output with ANSI codes
- Real-time streaming support
- Color preservation

### Navigation Sidebar
- Collapsible sidebar with location list
- Quick tool access buttons
- Active location highlighting
- Game status summary

### Command Input
- Use `Input` widget with history
- Auto-completion dropdown
- Command validation
- Integration with existing command parser

### Screen Transitions
- Smooth screen transitions
- Context preservation
- Back navigation stack
- State management

## Testing Strategy
- Manual testing of all screens
- Command execution verification
- Tool integration testing
- Game functionality testing
- Error handling verification

## Migration Path
1. Keep existing web interface and CLI
2. TUI runs alongside (not replacing)
3. Users can choose interface (web, CLI, or TUI)
4. Gradual feature parity
5. Eventually make TUI the primary interface

## Estimated Files Created
- ~15 new Python files
- 1 configuration file
- 1 documentation file
- Updates to 3 existing files

