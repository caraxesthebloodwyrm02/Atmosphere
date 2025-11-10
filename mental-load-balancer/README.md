# Mental Load Balancer for VS Code

A smart, context-aware extension that helps developers manage cognitive load through timely interventions and breaks. Using advanced metrics and pattern recognition, it detects high-pressure coding situations and provides well-timed, contextual breaks to prevent mental fatigue.

## Features

### 🧠 Smart Load Detection
- Monitors multiple pressure indicators:
  - Debugging session duration
  - File context switching frequency
  - Error patterns and frequency
  - Keystroke intensity
  - Time-of-day awareness
- Calculates a comprehensive pressure score using weighted factors
- Adapts to your coding patterns and work style

### ⚡ Context-Aware Interventions
- Language-specific programming jokes
- Time-aware notifications (different approach for late-night coding)
- Situation-specific break suggestions
- Smart timing with exponential backoff

### 📊 Real-time Dashboard
- Visual pressure score indicator
- Detailed metrics breakdown
- Session statistics
- Interactive configuration

### 🎯 Customizable Settings
- Adjustable thresholds for all metrics
- Configurable intervention styles
- Flexible notification preferences
- Personalized backoff strategy

## Installation

1. Open VS Code
2. Press `Ctrl+P` / `Cmd+P`
3. Type `ext install mental-load-balancer`
4. Press Enter

## Usage

### Status Bar
The extension adds a status bar item showing your current mental load:
- 🧠 Normal load (0-40%)
- ⚡ Moderate load (41-70%)
- ⚠️ High load (71-100%)

Click the status bar item to open the dashboard.

### Dashboard
Open the dashboard using:
- Click the status bar item
- Command Palette: `Mental Load: Show Dashboard`
- Keyboard Shortcut: `Ctrl+Shift+M` / `Cmd+Shift+M`

### Interventions
When the system detects high pressure points, it will:
1. Show a notification with a contextual joke
2. Offer quick actions:
   - Take a Break
   - Snooze
   - Show Details

## Configuration

### General Settings
\`\`\`json
{
  "mentalLoadBalancer.pressurePoints": {
    "debuggingThreshold": 60,    // Minutes before considering debug session as pressure
    "contextSwitchThreshold": 10, // Number of file switches before alert
    "lateNightThreshold": 22     // Hour (24h) to start late night detection
  },
  "mentalLoadBalancer.backoff": {
    "baseInterval": 5,           // Minutes between initial interventions
    "maxInterval": 60,           // Maximum minutes between interventions
    "resetAfterBreak": true      // Reset backoff after manual break
  },
  "mentalLoadBalancer.ui": {
    "showStatusBar": true,
    "notificationStyle": "popup", // "popup" or "notification"
    "colorTheme": "default"
  }
}
\`\`\`

### Customizing Thresholds
Adjust these settings based on your work style:
1. Open VS Code Settings
2. Search for "Mental Load"
3. Modify values to match your preferences

## Privacy

- All processing happens locally
- No data leaves your machine
- No telemetry collection
- No cloud services required

## How It Works

### Pressure Score Calculation
The extension calculates a pressure score (0-1) using these weighted factors:
- Debugging Duration (30%)
- Context Switches (20%)
- Error Patterns (20%)
- Time of Day (15%)
- Keystroke Intensity (15%)

### Intervention Timing
Uses an exponential backoff strategy:
1. Starts with base interval (default: 5 minutes)
2. Doubles interval after each intervention
3. Caps at maximum interval (default: 60 minutes)
4. Resets after manual breaks

### Context Detection
Analyzes multiple factors:
- Current programming language
- Time of day
- Activity patterns
- Error frequencies
- Work session duration

## Contributing

We welcome contributions! See our [Contributing Guide](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.