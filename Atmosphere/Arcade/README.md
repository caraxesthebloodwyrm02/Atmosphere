# Arcade Terminal - Retro Entertainment Space

A web-accessible terminal-based entertainment arena with retro arcade styling. Navigate through liminal spaces using PowerShell commands, with a "bumper car" game mechanic that lets you travel between cities (Echoes, Reverb, Delay) using `cd` commands.

## Features

- 🎮 **Web-based Terminal**: Access PowerShell terminal through your browser
- 🚗 **Bumper Car Game**: Navigate using `cd` commands with time travel mechanics
- 🏙️ **City Navigation**: Travel between Echoes, Reverb, and Delay cities
- ⏱️ **Time Travel**: Use `cd ..` and `cd ...` to go back in time/location history
- 🔒 **Secure Sandbox**: Isolated environment with command whitelisting
- 🎨 **Retro Arcade Theme**: Classic terminal styling with neon colors

## Quick Start

### Prerequisites

- Python 3.8+
- PowerShell Core 7.x (included in `terminal/` directory)
- Modern web browser

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the server:
```bash
python -m Arcade.api.server
```

Or using uvicorn directly:
```bash
uvicorn Arcade.api.server:app --host 0.0.0.0 --port 7681 --reload
```

3. Open your browser:
```
http://localhost:7681
```

## Architecture

### Components

- **`api/server.py`**: FastAPI WebSocket server
- **`api/terminal_handler.py`**: PowerShell process management
- **`api/security.py`**: Security layer with sandboxing
- **`api/game_engine.py`**: Game mechanics and navigation
- **`api/routing_integration.py`**: Integration with Routing system
- **`web/`**: Frontend files (HTML, CSS, JavaScript)
- **`sandbox/`**: Sandbox configuration and virtual filesystem

### Security Features

- Command whitelisting (only safe commands allowed)
- Process resource limits (CPU, memory, time)
- Filesystem isolation (restricted to sandbox)
- Session timeout handling
- Input sanitization

## Game Commands

### Navigation

- `cd <location>` - Navigate to a location (Echoes, Reverb, Delay, Arcade)
- `cd ..` - Go back one level (time travel backward)
- `cd ...` - Go back two levels (further time travel)
- `pwd` or `Get-Location` - Show current location

### Information

- `ls` or `dir` or `Get-ChildItem` - List available destinations
- `help` - Show help message
- `speed` - Check your current speed
- `status` - Show game status (score, level, location)

### Interactive Tools

#### Audio Analysis
- `analyze 808-bass` - Analyze 808 bass frequencies
- `analyze bass-delay` - Compare bass vs delay effects
- `analyze sound-effects [--effect reverb|echo|delay]` - Analyze sound effects

#### Visualization
- `visualize 3d [--source x y z] [--listener x y z]` - 3D spatial audio visualization
- `visualize comprehensive` - Comprehensive 6-panel visualization

#### Games & Playground
- `game list` - List available games
- `game guessing [--max 100]` - Number guessing game
- `game quiz` - Audio frequency quiz
- `game memory [--length 5]` - Spatial memory game
- `playground` - Interactive playground menu
- `demo audio|spatial|trajectory|preview` - Run demos

### Keyboard Shortcuts

- `F1` - Toggle help panel

## Cities

The Arcade connects to three cities through the Routing system:

- **Echoes**: The city of echoes, where sound reverberates through time
- **Reverb**: The city of reverb, where acoustic spaces define reality  
- **Delay**: The city of delay, where time flows differently
- **Arcade**: The central entertainment hub (starting location)

## Configuration

### Security Configuration

Edit `sandbox/security_config.json` to customize:
- Allowed commands (whitelist)
- Blocked commands (blacklist)
- Resource limits (CPU, memory, time)
- Session timeout

### Sandbox Configuration

Edit `sandbox/config.json` to configure:
- Sandbox root directory
- Network access permissions
- Process limits

## Audio-Arcade Pipeline

The Arcade includes an automated tool dispatcher system:

### Quick Start

1. **Start the dispatcher**:
```bash
python Arcade/ui_cli.py run
```

2. **Play a tool**:
```bash
python Arcade/ui_cli.py play audio_tool
```

3. **View logs**:
```bash
python Arcade/ui_cli.py log audio
```

### CLI Commands

- `tour` - Show arcade tour and available commands
- `play <tool>` - Fire up a tool (drops into incoming folder)
- `log <zone>` - View zone logs (use `-f` to follow)
- `zones` - List all zones and their status
- `status` - Check dispatcher status
- `run` - Start dispatcher daemon
- `web` - Open web interface

### How It Works

1. **Watch Folder**: Dispatcher watches `Arcade/incoming/` for new files
2. **Routing**: Tools are routed to zones (audio, visual, games) based on `config/routing.yaml`
3. **Execution**: Tools run as subprocesses with output captured to zone logs
4. **Logging**: All output goes to `zones/<zone>/<tool>.log`

### Configuration

Edit `config/routing.yaml` to map tool names to zones:
```yaml
audio_tool: audio
visual_tool: visual
games_tool: games
```

## Integration

### With Routing System

The Arcade integrates with the Routing system via `orchestral_channel.py`:
- Receives city status from Echoes-Reverb-Delay system
- Routes game commands through routing system
- Displays city information in terminal

### With Audio-Arcade Pipeline

Tools dispatched through the pipeline can:
- Integrate with terminal commands
- Access zone-specific resources
- Stream output to web interface
- Trigger game events

### With Existing API

Can be integrated with existing FastAPI applications:
```python
from Arcade.api.server import app

# Mount at /arcade
app.mount("/arcade", arcade_app)
```

## Development

### Project Structure

```
Arcade/
├── api/                    # Backend API
│   ├── server.py          # FastAPI server
│   ├── terminal_handler.py
│   ├── security.py
│   ├── game_engine.py
│   └── routing_integration.py
├── web/                    # Frontend
│   ├── index.html
│   ├── arcade.css
│   ├── terminal.js
│   └── game-overlay.js
├── sandbox/                # Sandbox configuration
│   ├── config.json
│   ├── security_config.json
│   └── virtual_fs/        # Virtual filesystem
├── terminal/               # PowerShell Core
└── requirements.txt
```

### Adding New Games

1. Extend `game_engine.py` with new game logic
2. Add game commands to `sandbox/allowed_commands.json`
3. Update frontend in `web/` to support new game features

### Interactive Features

The Arcade includes interactive tools from the codebase:

### Audio Analysis Tools
- Analyze 808 bass frequencies
- Compare bass vs delay effects
- Analyze sound effects (reverb, echo, delay)

### Spatial Visualization
- 3D spatial audio visualization
- Comprehensive 6-panel analysis
- Interactive position manipulation

### Games & Entertainment
- Number guessing game
- Audio frequency quiz
- Spatial memory game
- Random challenges
- Interactive playground

See [INTERACTIVE_FEATURES.md](INTERACTIVE_FEATURES.md) for complete documentation.

## Customization

- **Theme**: Edit `web/arcade.css` for styling
- **Game Mechanics**: Modify `api/game_engine.py`
- **Commands**: Update `sandbox/security_config.json`
- **Tools**: Add new tools in `tools/` directory

## Security Considerations

⚠️ **Important**: This is an entertainment space with restricted access. For production use:

1. **Authentication**: Add user authentication
2. **Rate Limiting**: Implement rate limiting per user
3. **Docker Isolation**: Consider containerization for stronger isolation
4. **Audit Logging**: Enable comprehensive logging
5. **Network Isolation**: Block external network access

## Troubleshooting

### Terminal not connecting

- Check if PowerShell is available at `terminal/pwsh.exe` (Windows) or `terminal/pwsh` (Unix)
- Verify WebSocket connection in browser console
- Check server logs for errors

### Commands not working

- Verify command is in allowed list (`sandbox/security_config.json`)
- Check resource limits (process may have been terminated)
- Review security logs

### Game not responding

- Check routing system connection
- Verify game session is active
- Review browser console for JavaScript errors

## License

Part of the Atmosphere project. See main LICENSE file.

## Acknowledgments

- Built with [xterm.js](https://xtermjs.org/) for terminal emulation
- Powered by FastAPI and WebSockets
- Integrated with Atmosphere Routing system

