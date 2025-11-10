# Arcade Terminal API Documentation

## Overview

The Arcade Terminal API provides a WebSocket-based interface for terminal access and game mechanics. All communication happens through WebSocket connections for real-time interaction.

## WebSocket Endpoint

**Endpoint**: `ws://localhost:7681/arcade/ws`

**Protocol**: JSON messages over WebSocket

## Message Types

### Client → Server

#### Command Message
```json
{
  "type": "command",
  "command": "cd Echoes"
}
```

Executes a command in the terminal. The command is validated against the security whitelist before execution.

#### Resize Message
```json
{
  "type": "resize",
  "cols": 80,
  "rows": 24
}
```

Notifies the server of terminal size changes.

#### Ping Message
```json
{
  "type": "ping"
}
```

Heartbeat message to keep connection alive.

#### Get Status Message
```json
{
  "type": "get_status"
}
```

Requests current game and terminal status.

### Server → Client

#### Welcome Message
```json
{
  "type": "welcome",
  "message": "Welcome to the Arcade Terminal!",
  "session_id": "uuid-here",
  "location": "Arcade"
}
```

Sent when a new WebSocket connection is established.

#### Terminal Output
```json
{
  "type": "terminal_output",
  "stdout": "Command output here",
  "stderr": "",
  "return_code": 0
}
```

Contains the output from a command execution.

#### Game Response
```json
{
  "type": "game_response",
  "result": {
    "success": true,
    "message": "Navigating to Echoes...",
    "location": "Echoes",
    "speed": 5.0,
    "effect": "navigation"
  }
}
```

Response from game engine for navigation commands.

#### Status Message
```json
{
  "type": "status",
  "game": {
    "session_id": "uuid",
    "state": "playing",
    "score": 0,
    "level": 1,
    "location": "Arcade",
    "speed": 0.0,
    "time_played": 123.45
  },
  "terminal": {
    "session_id": "uuid",
    "process_id": 12345,
    "working_directory": "/path/to/sandbox",
    "is_running": true
  }
}
```

Current game and terminal status.

#### Error Message
```json
{
  "type": "error",
  "message": "Error description here"
}
```

Error notification.

#### Pong Message
```json
{
  "type": "pong"
}
```

Response to ping message.

## REST API Endpoints

### GET `/`
Returns the main HTML page for the Arcade Terminal.

### GET `/arcade/status`
Get server status information.

**Response**:
```json
{
  "status": "running",
  "active_sessions": 2,
  "active_connections": 2,
  "routing": {
    "connected": true,
    "platform_status": {...}
  }
}
```

## Interactive Tool Commands

### Audio Analysis Commands

#### `analyze 808-bass`
Analyze 808 bass frequencies.

**Response**:
```json
{
  "type": "tool_output",
  "line": "🎵 VTEC 808 Bass Analysis\n",
  "tool": "audio_analyzer"
}
```

#### `analyze bass-delay [--file <path>]`
Compare bass vs delay effects.

#### `analyze sound-effects [--effect reverb|echo|delay]`
Analyze sound effects.

### Visualization Commands

#### `visualize 3d [--source x y z] [--listener x y z] [--save]`
Create 3D spatial audio visualization.

**Response**:
```json
{
  "type": "tool_output",
  "line": "🎨 3D Spatial Audio Visualization\n",
  "tool": "spatial_visualizer"
}
```

#### `visualize comprehensive`
Create comprehensive 6-panel visualization.

### Game Commands

#### `game list`
List available games.

#### `game guessing [--max 100]`
Play number guessing game.

#### `game quiz`
Play audio frequency quiz.

#### `game memory [--length 5]`
Play spatial memory game.

### Playground Commands

#### `playground`
Show interactive playground menu.

#### `demo <type>`
Run specific demo (audio, spatial, trajectory, preview, random).

## Game Commands

### Navigation Commands

#### `cd <location>`
Navigate to a location.

**Locations**:
- `Echoes` - The city of echoes
- `Reverb` - The city of reverb
- `Delay` - The city of delay
- `Arcade` - Central entertainment hub

**Example**:
```
cd Echoes
```

**Response**:
```json
{
  "success": true,
  "message": "Navigating to Echoes...",
  "location": "Echoes",
  "speed": 5.0,
  "effect": "navigation"
}
```

#### `cd ..`
Go back one level in location history (time travel backward).

**Example**:
```
cd ..
```

**Response**:
```json
{
  "success": true,
  "message": "Time travel! You went back to Arcade",
  "location": "Arcade",
  "speed": 10.0,
  "effect": "time_travel_backward"
}
```

#### `cd ...`
Go back two levels in location history.

**Example**:
```
cd ...
```

### Information Commands

#### `pwd` or `Get-Location`
Show current location.

**Response**:
```json
{
  "success": true,
  "message": "Current location: Arcade",
  "location": "Arcade",
  "history": ["Arcade"]
}
```

#### `ls` or `dir` or `Get-ChildItem`
List available destinations.

**Response**:
```json
{
  "success": true,
  "message": "Available destinations:",
  "locations": ["Echoes", "Reverb", "Delay", "Arcade"],
  "current": "Arcade"
}
```

#### `help`
Show help message.

**Response**:
```json
{
  "success": true,
  "message": "Arcade Navigation Commands:",
  "commands": {
    "cd <location>": "Navigate to a location",
    "cd ..": "Go back in time",
    ...
  }
}
```

#### `speed`
Check current speed.

**Response**:
```json
{
  "success": true,
  "message": "Current speed: 5.0 (liminal space - no speed limit!)",
  "speed": 5.0
}
```

#### `status`
Show game status.

**Response**:
```json
{
  "success": true,
  "game_state": {
    "state": "playing",
    "score": 0,
    "level": 1,
    "location": "Arcade",
    "speed": 5.0,
    "time_played": 123.45
  }
}
```

## Security

### Command Whitelist

Only commands in the whitelist are allowed. See `sandbox/security_config.json` for the full list.

**Allowed Categories**:
- Navigation: `cd`, `pwd`, `Get-Location`
- Listing: `ls`, `dir`, `Get-ChildItem`
- Information: `help`, `Get-Help`, `history`
- Display: `echo`, `Write-Host`, `clear`, `cls`

### Command Blacklist

Commands that are explicitly blocked:
- File operations: `rm`, `del`, `Remove-Item`
- System commands: `format`, `diskpart`, `net`, `wmic`
- Dangerous PowerShell: `Invoke-Expression`, `Invoke-WebRequest`

### Resource Limits

- **Max Process Time**: 30 seconds
- **Max Memory**: 512 MB
- **Max CPU**: 50%
- **Session Timeout**: 3600 seconds (1 hour)

## Integration Points

### With Routing System

The Arcade integrates with the Routing system through `routing_integration.py`:

- **Connection**: Automatically connects on server startup
- **City Status**: Can query status of Echoes, Reverb, Delay cities
- **Navigation**: Routes navigation commands through routing system
- **Data**: Receives orchestral data from routing system

### With Existing FastAPI Apps

The Arcade can be integrated into existing FastAPI applications:

```python
from fastapi import FastAPI
from Arcade.api.server import app as arcade_app

app = FastAPI()

# Mount Arcade at /arcade
app.mount("/arcade", arcade_app)
```

## Error Handling

### Connection Errors

- **WebSocket Disconnect**: Automatically attempts to reconnect
- **Session Timeout**: Session is terminated after inactivity
- **Resource Limit**: Process is terminated if limits exceeded

### Command Errors

- **Not Allowed**: Returns error message explaining why command is blocked
- **Execution Error**: Returns stderr with error details
- **Timeout**: Command execution is terminated after timeout

## WebSocket Protocol Flow

1. **Connection**: Client connects to `/arcade/ws`
2. **Welcome**: Server sends welcome message with session ID
3. **Command Loop**: 
   - Client sends command
   - Server validates command
   - Server executes command (if allowed)
   - Server sends terminal output and game response
4. **Heartbeat**: Client sends ping every 30 seconds
5. **Disconnection**: Either side can close connection

## Example Client Implementation

```javascript
const socket = new WebSocket('ws://localhost:7681/arcade/ws');

socket.onopen = () => {
  console.log('Connected to Arcade Terminal');
};

socket.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
  
  switch (message.type) {
    case 'welcome':
      console.log('Session ID:', message.session_id);
      break;
    case 'terminal_output':
      console.log('Output:', message.stdout);
      break;
    case 'game_response':
      console.log('Game:', message.result);
      break;
  }
};

// Send command
socket.send(JSON.stringify({
  type: 'command',
  command: 'cd Echoes'
}));
```

## Rate Limiting

Currently no rate limiting is implemented. For production use, consider:
- Rate limiting per IP address
- Rate limiting per session
- Command throttling

## Logging

All operations are logged:
- Connection/disconnection events
- Command execution
- Security violations
- Resource limit violations

Check server logs for detailed information.

