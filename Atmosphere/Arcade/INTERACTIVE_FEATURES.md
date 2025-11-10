# Interactive Arcade Features

## Overview

The Arcade Terminal now includes interactive tools integrated from the codebase, accessible through both CLI and web terminal with proper color coding and real-time output.

## Available Tools

### 🎵 Audio Analysis Tools

**Location**: `zones/audio/`

#### Commands:
- `analyze 808-bass` - Analyze 808 bass frequencies (150-240 Hz)
- `analyze bass-delay` - Compare bass vs delay effects
- `analyze sound-effects [--effect reverb|echo|delay]` - Analyze sound effects

**Examples**:
```bash
# CLI
python Arcade/ui_cli.py analyze 808-bass
python Arcade/ui_cli.py analyze bass-delay --file audio.wav
python Arcade/ui_cli.py analyze sound-effects --effect reverb

# Web Terminal
analyze 808-bass
analyze bass-delay --file audio.wav
analyze sound-effects --effect echo
```

**Output**: Colored analysis results with frequency data, tactile intensity, and body resonance information.

### 🎨 Spatial Audio Visualization

**Location**: `zones/visual/`

#### Commands:
- `visualize 3d [--source x y z] [--listener x y z] [--save]` - 3D spatial audio visualization
- `visualize comprehensive` - Comprehensive 6-panel visualization

**Examples**:
```bash
# CLI
python Arcade/ui_cli.py visualize 3d
python Arcade/ui_cli.py visualize 3d --source 4 1 2 --listener -1 0 0 --save
python Arcade/ui_cli.py visualize comprehensive

# Web Terminal
visualize 3d
visualize 3d --source 5 0 2 --listener 0 0 0
visualize comprehensive
```

**Output**: 
- Text-based ASCII visualization in terminal
- Image generation (when matplotlib available)
- Distance calculations and spatial properties

### 🎮 Interactive Playground

**Location**: `zones/games/`

#### Commands:
- `playground` - Show interactive menu
- `demo audio` - Run audio analysis demo
- `demo spatial` - Run spatial visualization demo
- `demo trajectory` - Run trajectory visualization demo
- `demo preview` - Run real-time preview demo
- `demo random` - Run random demo

**Examples**:
```bash
# CLI
python Arcade/ui_cli.py playground
python Arcade/ui_cli.py playground --demo audio
python Arcade/ui_cli.py demo spatial

# Web Terminal
playground
demo audio
demo spatial
```

**Output**: Interactive menu-driven interface with demos.

### 🎲 Game Collection

**Location**: `zones/games/`

#### Commands:
- `game list` - List available games
- `game guessing [--max 100]` - Number guessing game
- `game quiz` - Audio frequency quiz
- `game memory [--length 5]` - Spatial memory game
- `game challenge` - Random challenge game

**Examples**:
```bash
# CLI
python Arcade/ui_cli.py game list
python Arcade/ui_cli.py game guessing --max 200
python Arcade/ui_cli.py game memory --length 7
python Arcade/ui_cli.py game quiz

# Web Terminal
game list
game guessing
game quiz
game memory --length 5
```

**Output**: Game interfaces with colored output, scores, and interactive gameplay.

## Color Coding

All tools use consistent color coding:

- **Green** (`#00ff00`): Success messages, primary actions, active states
- **Cyan** (`#00ffff`): Information, neutral output, commands
- **Yellow** (`#ffff00`): Warnings, hints, highlights, data values
- **Red** (`#ff0000`): Errors, critical alerts
- **Magenta** (`#ff00ff`): Accent, special features, tool names
- **Gray** (`#808080`): Inactive, disabled, metadata

## Output Formatting

All tools:
1. Print colored output using ANSI escape codes
2. Stream output in real-time via WebSocket
3. Include progress indicators for long operations
4. Format results with clear structure
5. Handle errors with colored error messages

## Integration Points

### CLI Integration

Tools are accessible via `ui_cli.py`:
```bash
python Arcade/ui_cli.py analyze 808-bass
python Arcade/ui_cli.py visualize 3d
python Arcade/ui_cli.py game list
python Arcade/ui_cli.py playground
```

### Web Terminal Integration

Tools are accessible via terminal commands:
```
analyze 808-bass
visualize 3d --source 5 0 2
game guessing
playground
```

### Dispatcher Integration

Tools can be triggered via dispatcher:
```bash
python Arcade/ui_cli.py play audio_analyzer
```

## Tool Execution Flow

1. **Command Parsing**: `tool_integration.py` parses command
2. **Tool Selection**: Determines which tool to execute
3. **Output Streaming**: Real-time output via WebSocket
4. **Result Display**: Colored output in terminal
5. **Completion**: Success/failure notification

## Example Session

### Web Terminal Session:
```
🎟️ Arcade:~$ analyze 808-bass
🎵 VTEC 808 Bass Analysis
==================================================
📊 Analyzing 808 bass frequencies (150-240 Hz)...
   Frequency range: 150-240 Hz
   VTEC mode: High precision

✅ Analysis Complete!

📈 Results:
   Frequency: 200.0 Hz
   Amplitude: 0.850
   Tactile Intensity: 0.75

🎟️ Arcade:~$ visualize 3d --source 5 0 2 --listener 0 0 0
🎨 3D Spatial Audio Visualization
==================================================
📍 Source Position: (5.0, 0.0, 2.0)
👂 Listener Position: (0.0, 0.0, 0.0)
📏 Distance: 5.39 units

📊 Spatial Layout (Top View):
  🔴 = Sound Source
  👂 = Listener
  · = Acoustic field

🎟️ Arcade:~$ game quiz
🎵 Audio Frequency Quiz
==================================================
❓ What frequency range is typical for 808 bass?
  1. 50-100 Hz
  2. 150-240 Hz
  3. 500-1000 Hz
  4. 2000-5000 Hz
```

## Troubleshooting

### Tool Not Found
- Ensure tool is in `Arcade/tools/` directory
- Check tool is imported correctly in `tool_integration.py`

### No Output
- Check WebSocket connection (web terminal)
- Verify tool execution completed successfully
- Check zone logs: `python Arcade/ui_cli.py log audio`

### Color Codes Not Working
- Ensure terminal supports ANSI colors
- Check xterm.js version (web terminal)
- Verify color codes in tool output

## Extending Tools

### Adding New Tool

1. Create tool wrapper in `Arcade/tools/`:
```python
# tools/my_tool.py
class MyTool:
    def _print_colored(self, message, color, stream=None):
        # ... colored output ...
    
    def run(self, args, output_stream=None):
        # ... tool logic ...
```

2. Add to `tool_integration.py`:
```python
elif tool_name == 'my_tool':
    from tools.my_tool import MyTool
    tool = MyTool()
    result = tool.run(args, output_stream=output_buffer)
```

3. Update command parser:
```python
elif command.startswith('my-command'):
    return {
        'tool_name': 'my_tool',
        'args': {...}
    }
```

4. Update security config to allow command
5. Update routing.yaml if using dispatcher

## Configuration

Tool configurations are in `config/tools.yaml`:
- Tool names and descriptions
- Available commands
- Zone assignments
- Color schemes

