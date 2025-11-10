# Helper Processes in Mental Load Balancer

This document outlines the various helper processes that support the core functionality of the Mental Load Balancer extension.

## Core Helper Processes

### 1. Backoff System (`backoff.ts`)
Manages the timing and frequency of interventions using an exponential backoff strategy.

**Key Functions:**
- `calculateNextInterval()`: Determines when the next intervention should occur
- `reset()`: Resets the backoff counter
- `getCurrentState()`: Returns the current backoff state

### 2. Joke Engine (`jokeEngine.ts`)
Provides context-appropriate programming humor and break suggestions.

**Features:**
- Language-specific jokes
- Time-aware humor
- Break suggestions based on current activity

### 3. Mental State Tracker (`mentalState.ts`)
Monitors and calculates the developer's cognitive load.

**Metrics Tracked:**
- Debugging duration
- Context switches
- Error patterns
- Keystroke intensity
- Time-based factors

## Integration Points

These helper processes work together through the main extension (`extension.ts`), which coordinates their activities and manages the VS Code integration.

## Configuration

Each helper can be configured through the main extension settings:

```json
{
  "mentalLoadBalancer.backoff": {
    "baseInterval": 5,
    "maxInterval": 60,
    "resetAfterBreak": true
  }
}
```

## Error Handling

Each helper implements consistent error handling:
1. Logs errors to the VS Code output channel
2. Fails gracefully without disrupting the user experience
3. Provides fallback behaviors when possible

## Testing

Helper processes include unit tests that verify:
- Core functionality
- Edge cases
- Integration points

## Performance Considerations

- Lightweight monitoring with minimal performance impact
- Efficient state management
- Background processing for intensive operations
