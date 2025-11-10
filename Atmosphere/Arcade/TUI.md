# Arcade Terminal TUI

## Overview

The Arcade Terminal TUI (Text User Interface) is a full-stack terminal application that provides a rich, interactive experience for accessing all Arcade Terminal features. Built with `textual` framework, it offers a native terminal interface with multi-panel layouts, real-time updates, and integrated access to tools, games, and navigation.

## Installation

### Prerequisites

- Python 3.9+
- Terminal with color support

### Install Dependencies

```bash
pip install textual rich
```

Or install from requirements:

```bash
pip install -r Arcade/requirements.txt
```

## Usage

### Launch TUI

From the CLI:

```bash
python Arcade/ui_cli.py tui
```

Or directly:

```bash
python -m Arcade.tui.main
```

### Launch Options

- `--standalone` (default): Run in standalone mode
- `--server`: Connect to server mode (future feature)

## Interface

### Layout

The TUI consists of:

1. **Sidebar** (left): Navigation menu with locations, tools, and quick actions
2. **Terminal Output** (center): Scrollable output area for commands and tool results
3. **Command Input** (bottom center): Command input with history support
4. **Status Bar** (bottom): Current game state (location, score, level, speed)

### Keyboard Shortcuts

- `F1`: Show help
- `F2`: Show command history
- `F3`: Show tools menu
- `ESC`: Go back (context-dependent)
- `Ctrl+C`: Quit application
- `Up/Down`: Navigate command history

### Commands

All existing Arcade Terminal commands are supported:

#### Audio Analysis
- `analyze 808-bass` - Analyze 808 bass frequencies
- `analyze bass-delay` - Compare bass vs delay effects
- `analyze sound-effects [--effect reverb|echo|delay]` - Analyze sound effects

#### Visualization
- `visualize 3d [--source x y z] [--listener x y z]` - 3D spatial audio visualization
- `visualize comprehensive` - Comprehensive 6-panel visualization

#### Games
- `game list` - List available games
- `game guessing [--max 100]` - Number guessing game
- `game quiz` - Audio frequency quiz
- `game memory [--length 5]` - Spatial memory game
- `game challenge` - Random challenge game

#### Navigation
- `cd <location>` - Navigate to location (Arcade, Echoes, Reverb, Delay)
- `cd ..` - Go back in time (previous location)
- `cd ...` - Go further back in time
- `pwd` - Show current location
- `ls` - List available destinations

#### Information
- `help` - Show help
- `status` - Show game status
- `speed` - Check current speed

#### Playground
- `playground` - Interactive playground menu
- `demo audio` - Run audio demo
- `demo spatial` - Run spatial demo
- `demo trajectory` - Run trajectory demo
- `demo preview` - Run real-time preview
- `demo random` - Run random demo

## Features

### Command History

- Persistent command history stored in `~/.arcade_tui_history`
- Navigate with Up/Down arrows
- View last 10 commands with F2
- Maximum 100 commands stored

### Real-time Output

- Tool output streams in real-time
- ANSI color codes preserved
- Scrollable output buffer (1000 lines max)

### Status Updates

- Game state updates automatically
- Location changes reflected immediately
- Score and level tracking
- Speed monitoring

### Sidebar Navigation

- Quick location navigation
- Tool access shortcuts
- Collapsible sections
- Click to navigate or execute

## Configuration

TUI configuration is stored in `Arcade/config/tui_config.yaml`:

```yaml
theme:
  name: "arcade"
  colors:
    primary: "#00ff00"
    secondary: "#00ffff"
    accent: "#ff00ff"

layout:
  sidebar_width: 25
  status_bar_height: 1
  command_input_height: 3

history:
  max_size: 100
  file_path: "~/.arcade_tui_history"
```

## Troubleshooting

### TUI Won't Launch

**Error**: `ModuleNotFoundError: No module named 'textual'`

**Solution**: Install dependencies:
```bash
pip install textual rich
```

### Colors Not Displaying

**Issue**: Terminal doesn't support colors

**Solution**: 
- Use a terminal with color support (most modern terminals)
- Check terminal color settings
- TUI will still work but without colors

### Command History Not Working

**Issue**: History not persisting

**Solution**:
- Check write permissions for `~/.arcade_tui_history`
- Ensure home directory is accessible

### Tool Execution Fails

**Issue**: Tools not executing properly

**Solution**:
- Check tool dependencies are installed
- Verify tool paths in `Arcade/tools/`
- Check error messages in terminal output

## Architecture

### Components

- **App** (`tui/app.py`): Main application class
- **Screens** (`tui/screens/`): Screen definitions
- **Widgets** (`tui/widgets/`): Reusable UI components
- **Integration** (`tui/integration/`): Tool and game engine integration
- **Themes** (`tui/themes/`): Styling and color schemes

### Integration

- **Tool Executor**: Executes tools and streams output
- **Game Controller**: Manages game state and navigation
- **Command Parser**: Parses commands and routes to appropriate handlers

## Development

### Adding New Screens

1. Create screen file in `tui/screens/`
2. Inherit from `Screen`
3. Implement `compose()` method
4. Add navigation logic
5. Register in app if needed

### Adding New Widgets

1. Create widget file in `tui/widgets/`
2. Inherit from appropriate textual widget
3. Implement required methods
4. Export in `__init__.py`

### Customizing Theme

1. Edit `tui/themes/arcade_theme.css`
2. Update color definitions in CSS
3. Modify widget styles as needed

## Future Enhancements

- Server connection mode
- Auto-completion dropdown
- Multi-screen navigation
- Customizable key bindings
- Plugin system
- Advanced visualization rendering

## See Also

- [README.md](README.md) - General Arcade Terminal documentation
- [INTERACTIVE_FEATURES.md](INTERACTIVE_FEATURES.md) - Interactive features guide
- [API.md](API.md) - API documentation

