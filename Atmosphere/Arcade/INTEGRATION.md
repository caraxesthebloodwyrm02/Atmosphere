# Arcade Terminal Integration Guide

## Overview

The Arcade Terminal now includes both:
1. **Web Terminal Interface** - Browser-based PowerShell terminal with game mechanics
2. **Audio-Arcade Pipeline** - Automated tool dispatcher with zone routing

## Architecture

```
Arcade/
├── api/                    # Web terminal API
│   ├── server.py           # WebSocket server
│   ├── terminal_handler.py # PowerShell process management
│   ├── game_engine.py     # Game mechanics
│   └── routing_integration.py
├── web/                    # Frontend
│   ├── index.html
│   ├── terminal.js
│   └── game-overlay.js
├── dispatcher.py           # Tool dispatcher
├── ui_cli.py              # CLI interface
├── config/
│   └── routing.yaml       # Tool routing configuration
├── incoming/              # Watched folder for tools
└── zones/                 # Zone directories
    ├── audio/
    ├── visual/
    └── games/
```

## Using Both Systems Together

### Scenario 1: Terminal Command Triggers Tool

You can trigger tools from the terminal interface:

```powershell
# In terminal web interface
cd Arcade
# Create a trigger file
echo "audio_tool" > incoming/audio_tool.trigger
```

The dispatcher will automatically pick it up and route it to the `audio` zone.

### Scenario 2: CLI Triggers Tool, Web Shows Status

```bash
# In CLI
python Arcade/ui_cli.py play audio_tool

# In web interface, check status
status
```

### Scenario 3: Tool Output in Terminal

Tools can write to zone logs, which can be viewed in the terminal:

```powershell
# In terminal
Get-Content zones/audio/audio_tool.log
```

## Integration Points

### 1. Shared Configuration

Both systems use shared configuration:
- `config/routing.yaml` - Defines tool-to-zone routing
- `sandbox/security_config.json` - Security settings

### 2. Shared Zones

The zones directory is shared:
- Terminal can access zone logs
- Dispatcher writes to zones
- Both can read/write zone files

### 3. WebSocket Integration (Future)

The dispatcher can emit events to the WebSocket server:
- Tool started events
- Tool completed events
- Zone status updates

## Example Workflow

### Complete Tool Execution Flow

1. **User triggers tool via CLI**:
   ```bash
   python Arcade/ui_cli.py play visual_tool
   ```

2. **Dispatcher detects file**:
   - Watches `incoming/` directory
   - Sees new `visual_tool.trigger` file
   - Reads routing config: `visual_tool → visual`

3. **Tool executes**:
   - Dispatcher runs `visual_tool.py`
   - Captures output to `zones/visual/visual_tool.log`
   - Process runs in background

4. **User monitors in terminal**:
   ```powershell
   # In web terminal
   Get-Content zones/visual/visual_tool.log -Tail 10 -Wait
   ```

5. **User checks status**:
   ```bash
   python Arcade/ui_cli.py status
   ```

## Extending the System

### Adding New Tools

1. Create tool script in `example_tools/`:
   ```python
   # example_tools/my_tool.py
   print("[my_tool] Starting...")
   # ... tool logic ...
   ```

2. Add routing in `config/routing.yaml`:
   ```yaml
   my_tool: audio  # or visual, games, etc.
   ```

3. Use it:
   ```bash
   python Arcade/ui_cli.py play my_tool
   ```

### Creating New Zones

1. Add zone to routing config:
   ```yaml
   my_tool: new_zone
   ```

2. Zone directory is created automatically when first tool is dispatched

3. Zone appears in `zones` command:
   ```bash
   python Arcade/ui_cli.py zones
   ```

### Custom Tool Execution

Tools can be:
- Python scripts (`.py`)
- Shell scripts (`.sh`, `.bat`, `.ps1`)
- Executables (any file)

The dispatcher will attempt to execute them appropriately.

## Security Considerations

### Tool Execution

- Tools run as subprocesses
- Output is captured to zone logs
- No network access by default
- Process resource limits apply

### File Access

- Tools can only access files in their zone directory
- Sandbox restrictions apply to terminal commands
- Both systems respect security configuration

## Troubleshooting

### Dispatcher Not Starting

```bash
# Check if already running
python Arcade/ui_cli.py status

# Start manually
python Arcade/dispatcher.py
```

### Tool Not Routing

1. Check routing config: `config/routing.yaml`
2. Verify tool name matches config key
3. Check dispatcher logs for errors

### Zone Logs Not Appearing

1. Verify zone directory exists: `zones/<zone>/`
2. Check tool execution: Look for `.log` files
3. Check dispatcher is running: `python Arcade/ui_cli.py status`

## Advanced Usage

### Custom Tool Handlers

You can extend the dispatcher to handle custom tool types by modifying `dispatcher.py`:

```python
def _dispatch_to_zone(self, tool_name, file_path, zone_name):
    # Add custom handling for specific tool types
    if file_path.suffix == ".custom":
        # Custom execution logic
        pass
```

### WebSocket Events (Future)

The dispatcher can emit WebSocket events:

```python
# In dispatcher.py
async def emit_tool_event(event_type, data):
    # Send to WebSocket server
    pass
```

This allows real-time updates in the web terminal interface.

## Best Practices

1. **Tool Naming**: Use descriptive names matching routing config
2. **Zone Organization**: Group related tools in same zone
3. **Log Management**: Regularly clean old logs
4. **Error Handling**: Tools should handle errors gracefully
5. **Resource Limits**: Monitor tool resource usage

## Next Steps

- [ ] Add WebSocket event streaming from dispatcher
- [ ] Integrate tool status into terminal game mechanics
- [ ] Add zone visualization in web UI
- [ ] Implement tool scheduling/queuing
- [ ] Add tool dependencies and chaining

