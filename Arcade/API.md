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

---

# Learning Companion API

## Overview

The Emotionally-Adaptive Learning Companion provides REST API endpoints for AI-powered personalized learning experiences that adapt content based on learner emotional states and behavioral patterns.

## Base URL

```python
http://localhost:7681/learning
```

## Authentication

Currently no authentication required. For production use, implement API key authentication.

## Endpoints

### GET /learning/status

Get system status and capabilities.

**Response:**
```json
{
  "success": true,
  "data": {
    "system_status": "operational",
    "available_topics": ["python_functions"],
    "emotional_states_supported": [
      "exploratory", "creative", "analytical", "urgent", "calm",
      "frustrated", "confused", "engaged"
    ],
    "content_types": [
      "interactive_exercise", "concept_explanation",
      "visual_demonstration", "practical_project",
      "quiz_assessment", "story_based_learning"
    ],
    "intervention_types": [
      "stress_relief", "engagement_boost",
      "confusion_support", "frustration_relief"
    ],
    "capabilities": [
      "real_time_emotional_detection",
      "adaptive_content_routing",
      "intervention_triggers",
      "progress_tracking",
      "behavioral_analytics"
    ]
  }
}
```

### GET /learning/topics

Get list of available learning topics.

**Response:**
```json
{
  "success": true,
  "data": {
    "topics": ["python_functions"],
    "count": 1
  }
}
```

### POST /learning/session/start

Create a new learning session.

**Query Parameters:**
- `learner_id` (string, required): Unique identifier for the learner
- `topic` (string, optional): Learning topic (default: "python_functions")

**Request Body (optional):**
```json
{
  "response_times": [1.5, 2.0, 1.8],
  "error_count": 0,
  "total_attempts": 3,
  "help_requests": 0,
  "session_duration": 300,
  "interaction_frequency": 1.5,
  "content_difficulty": 0.6,
  "progress_rate": 0.8,
  "time_since_last_interaction": 0
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "user_topic_1234567890",
    "status": "active",
    "welcome_message": "🌟 Welcome to your emotionally-adaptive learning session...",
    "initial_content": {
      "module_id": "func_intro_exploratory",
      "title": "Function Discovery Lab",
      "content_type": "interactive_exercise",
      "difficulty": "beginner",
      "estimated_duration": 15,
      "content_data": {...},
      "learning_objectives": [...]
    },
    "progress_checkpoint": {
      "checkpoint_id": "cp_1",
      "estimated_time": 15,
      "success_criteria": {...}
    },
    "estimated_completion": 45
  }
}
```

### POST /learning/session/interact

Process a learning interaction and adapt content accordingly.

**Request Body:**
```json
{
  "session_id": "user_topic_1234567890",
  "interaction_type": "correct_answer",
  "interaction_data": {
    "response_time": 1.5,
    "confidence": 0.9,
    "exploration_depth": "high"
  }
}
```

**Response (Normal):**
```json
{
  "success": true,
  "data": {
    "response_type": "positive_feedback",
    "message": "Excellent! That's correct. 🎉",
    "next_action": "continue_module"
  }
}
```

**Response (Emotional Shift):**
```json
{
  "success": true,
  "data": {
    "adaptation_type": "emotional_shift",
    "new_emotional_state": {
      "primary": "frustrated",
      "confidence": 0.85,
      "engagement": 0.4
    },
    "adapted_content": {...},
    "adaptation_reason": "Detected shift from analytical to frustrated emotional state..."
  }
}
```

**Response (Intervention):**
```json
{
  "success": true,
  "data": {
    "intervention_type": "stress_relief",
    "message": "I notice you might be feeling stressed. Would you like to take a short break?",
    "suggestion": "Try the breathing exercise: Inhale for 4 counts, hold for 4, exhale for 4."
  }
}
```

### POST /learning/session/end/{session_id}

End a learning session and get comprehensive feedback.

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "user_topic_1234567890",
    "status": "completed",
    "completion_summary": {
      "session_topic": "python_functions",
      "duration_minutes": 42.5,
      "completion_rate": 1.0,
      "emotional_journey": "balanced",
      "learning_effectiveness": 1.8,
      "key_achievements": [
        "Completed all planned modules",
        "Maintained positive learning experience"
      ],
      "personal_growth": "You showed strong comprehension and steady progress..."
    },
    "progress_report": {
      "performance_metrics": {
        "learning_efficiency": 1.8,
        "emotional_stability": 0.9
      },
      "insights": [
        "Strong engagement with interactive content",
        "Effective emotional state management"
      ],
      "recommendations": [
        "Continue with advanced function concepts",
        "Try more creative coding challenges"
      ]
    },
    "behavioral_insights": {
      "insights": [
        "Most productive learning time: 14:00",
        "Consistent daily learning pattern"
      ],
      "patterns": {...},
      "recommendations": [...]
    },
    "next_session_recommendations": {
      "suggested_duration_minutes": 45,
      "recommended_difficulty": "intermediate",
      "focus_areas": ["practice", "review"],
      "emotional_preparation": "Start with engaging examples"
    }
  }
}
```

### GET /learning/session/status/{session_id}

Get current status of a learning session.

**Response:**
```json
{
  "success": true,
  "data": {
    "session_id": "user_topic_1234567890",
    "learner_id": "test_user",
    "topic": "python_functions",
    "duration": 1850.5,
    "current_emotion": "engaged",
    "content_progress": 2,
    "active_interventions": 0
  }
}
```

### GET /learning/progress/{learner_id}

Get comprehensive learning progress for a learner.

**Query Parameters:**
- `topic` (string, optional): Filter by specific topic

**Response:**
```json
{
  "success": true,
  "data": {
    "learner_id": "test_user",
    "topic": "python_functions",
    "overall_mastery": 0.73,
    "skill_breakdown": {
      "problem_solving": 0.8,
      "concept_understanding": 0.7,
      "code_writing": 0.75,
      "debugging": 0.65
    },
    "learning_velocity": 1.2,
    "recommended_difficulty": "intermediate",
    "next_focus_areas": [
      "strengthen_debugging",
      "advance_concept_understanding"
    ]
  }
}
```

### GET /learning/insights/{learner_id}

Get behavioral insights and learning patterns.

**Query Parameters:**
- `time_window_days` (integer, optional): Analysis window (default: 30)

**Response:**
```json
{
  "success": true,
  "data": {
    "insights": [
      "Most productive learning time: 14:00",
      "Consistent daily learning pattern - excellent momentum!",
      "Most common learning emotion: engaged"
    ],
    "patterns": {
      "avg_session_duration": 2700.5,
      "preferred_learning_times": [14],
      "topic_sequence": ["python_functions"],
      "success_patterns": {...}
    },
    "recommendations": [
      "Maintain current learning schedule - it's working well!",
      "Try more frequent, shorter learning sessions"
    ]
  }
}
```

### POST /learning/demo/run

Run demonstration scenarios for the learning companion.

**Response:**
```json
{
  "success": true,
  "data": {
    "scenarios_run": 3,
    "sessions_completed": 3,
    "interventions_triggered": true,
    "adaptations_performed": true,
    "overall_success": true,
    "scenario_results": [
      {
        "scenario": "exploratory_learner",
        "success": true,
        "emotional_journey": "highly_engaged"
      },
      {
        "scenario": "frustrated_learner",
        "success": true,
        "interventions_triggered": true,
        "emotional_journey": "challenging"
      },
      {
        "scenario": "emotional_shift",
        "success": true,
        "adaptations_performed": true,
        "emotional_journey": "variable"
      }
    ]
  }
}
```

## Error Responses

All endpoints return errors in this format:

```json
{
  "success": false,
  "error": "Description of the error"
}
```

Common HTTP status codes:
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (session/topic doesn't exist)
- `500` - Internal Server Error (server-side issues)

## Rate Limiting

Currently no rate limiting implemented. For production:
- Per-user rate limiting
- API key validation
- Request throttling

## Data Privacy

- Emotional data processed locally
- No external data transmission
- Configurable data retention
- Research-grade privacy controls

## Integration Examples

### JavaScript Client
```javascript
// Start learning session
const response = await fetch('/learning/session/start?learner_id=user123&topic=python_functions');
const session = await response.json();

// Process interaction
const interaction = await fetch('/learning/session/interact', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: session.data.session_id,
    interaction_type: 'correct_answer',
    interaction_data: {response_time: 1.2, confidence: 0.95}
  })
});
```

### Python Client
```python
import httpx

async def learning_session():
    async with httpx.AsyncClient(base_url='http://localhost:7681') as client:
        # Start session
        response = await client.post('/learning/session/start', 
                                   params={'learner_id': 'user123', 'topic': 'python_functions'})
        session = response.json()
        
        # Interact
        await client.post('/learning/session/interact', json={
            'session_id': session['data']['session_id'],
            'interaction_type': 'correct_answer',
            'interaction_data': {'response_time': 1.2, 'confidence': 0.95}
        })
```

## Performance Characteristics

- **Response Time**: <100ms for most endpoints
- **Concurrent Sessions**: Supports multiple simultaneous learners
- **Emotional Processing**: Real-time multi-signal analysis
- **Content Adaptation**: Instantaneous routing decisions
- **Data Persistence**: Efficient session storage and retrieval

## Monitoring & Analytics

The API provides built-in monitoring:
- Session analytics and completion tracking
- Emotional state distribution analysis
- Intervention effectiveness metrics
- Learning progress velocity tracking
- Behavioral pattern recognition
