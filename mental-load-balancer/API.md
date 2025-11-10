# Mental Load Balancer API Documentation

## Core APIs

### MentalStateTracker

The main class responsible for monitoring and analyzing developer activity.

#### Methods

##### `calculatePressureScore(): PressureScore`
Calculates the current mental load pressure score.

```typescript
interface PressureScore {
    total: number;          // Overall score (0-1)
    factors: {
        debugging: number;  // Impact from debugging (0-1)
        contextSwitches: number; // Impact from file switching (0-1)
        timeOfDay: number; // Impact from time of day (0-1)
        errors: number;    // Impact from errors (0-1)
        keystrokes: number; // Impact from typing intensity (0-1)
    };
}
```

##### `getCurrentMetrics(): MentalStateMetrics`
Returns the current state metrics.

```typescript
interface MentalStateMetrics {
    debuggingDuration: number;     // Minutes
    fileContextSwitches: number;   // Count
    errorPatterns: ErrorPattern[]; // Array of error patterns
    timeOfDay: number;            // Hour (0-23)
    workSessionDuration: number;  // Minutes
    keystrokeCount: number;       // Count
    errorCount: number;          // Count
    lastResetTime: number;       // Timestamp
}
```

##### `reset()`
Resets all metrics to their initial state.

### BackoffStrategy

Manages intervention timing using exponential backoff.

#### Methods

##### `getNextInterval(): number`
Calculates the next intervention interval in minutes.

##### `canTriggerIntervention(): boolean`
Determines if enough time has passed for next intervention.

##### `recordIntervention()`
Records that an intervention occurred.

##### `reset()`
Resets the backoff strategy.

### EnhancedJokeEngine

Generates context-aware jokes and break suggestions.

#### Methods

##### `async getContextualJoke(metrics: MentalStateMetrics): Promise<string>`
Returns a joke based on the current context.

#### Joke Categories
- Debugging
- Late Night
- Context Switch
- Error
- Language-specific

## Configuration

### Settings Interface

```typescript
interface ExtensionConfiguration {
    pressurePoints: {
        debuggingThreshold: number;
        contextSwitchThreshold: number;
        lateNightThreshold: number;
    };
    backoff: {
        baseInterval: number;
        maxInterval: number;
        resetAfterBreak: boolean;
    };
    ui: {
        showStatusBar: boolean;
        notificationStyle: 'popup' | 'notification';
        colorTheme: string;
    };
}
```

### VS Code Commands

| Command | Description | Arguments |
|---------|-------------|-----------|
| `mentalLoadBalancer.showDashboard` | Opens metrics dashboard | None |
| `mentalLoadBalancer.takeBreak` | Initiates a manual break | None |
| `mentalLoadBalancer.resetMetrics` | Resets all metrics | None |

## Events

### VS Code Event Subscriptions

```typescript
// Document changes
vscode.workspace.onDidChangeTextDocument

// Editor changes
vscode.window.onDidChangeActiveTextEditor

// Debug sessions
vscode.debug.onDidStartDebugSession
vscode.debug.onDidTerminateDebugSession
```

## UI Components

### Status Bar

```typescript
interface StatusBarState {
    score: number;
    icon: string;
    color: string;
    tooltip: string;
}
```

### Dashboard

```typescript
interface DashboardData {
    metrics: MentalStateMetrics;
    score: PressureScore;
    history: MetricHistory[];
}
```

## Extension API

### Activation Events

```json
{
    "activationEvents": [
        "*"
    ]
}
```

### Extension Context

```typescript
interface ExtensionContext {
    subscriptions: Disposable[];
    workspaceState: Memento;
    globalState: Memento;
    extensionPath: string;
}
```

## Using the APIs

### Basic Usage

```typescript
// Initialize components
const settings = new SettingsManager();
const mentalState = new MentalStateTracker();
const backoff = new BackoffStrategy(settings.backoffConfig);

// Monitor pressure
setInterval(() => {
    const score = mentalState.calculatePressureScore();
    if (score.total > 0.7 && backoff.canTriggerIntervention()) {
        triggerIntervention();
    }
}, 30000);
```

### Custom Intervention Strategy

```typescript
class CustomIntervention implements InterventionStrategy {
    constructor(private context: vscode.ExtensionContext) {}

    async trigger(metrics: MentalStateMetrics) {
        const score = this.calculateCustomScore(metrics);
        if (score > this.getThreshold()) {
            await this.showIntervention();
        }
    }

    private calculateCustomScore(metrics: MentalStateMetrics): number {
        // Custom scoring logic
        return 0.0;
    }
}
```

### Error Handling

```typescript
try {
    const metrics = await mentalState.getCurrentMetrics();
    // Process metrics
} catch (error) {
    vscode.window.showErrorMessage('Failed to get metrics');
    // Log error
}
```

## Best Practices

1. **Event Handling**
   - Use proper cleanup
   - Implement error boundaries
   - Handle disposables

2. **Performance**
   - Debounce frequent events
   - Batch updates
   - Clean up resources

3. **User Experience**
   - Respect user settings
   - Provide feedback
   - Allow intervention control

4. **Testing**
   - Mock VS Code API
   - Test edge cases
   - Verify cleanup

## Examples

### Implementing Custom Metrics

```typescript
class CustomMetricProvider implements MetricProvider {
    getName(): string {
        return 'custom.metric';
    }

    calculateMetric(): number {
        // Custom calculation
        return 0.0;
    }

    getWeight(): number {
        return 0.1; // 10% weight
    }
}
```

### Custom UI Integration

```typescript
class CustomDashboard {
    private panel: vscode.WebviewPanel;

    constructor() {
        this.panel = vscode.window.createWebviewPanel(
            'customDashboard',
            'Custom Dashboard',
            vscode.ViewColumn.Beside,
            { enableScripts: true }
        );
    }

    update(data: DashboardData) {
        this.panel.webview.html = this.getWebviewContent(data);
    }
}
```

## Troubleshooting

### Common Issues

1. **High CPU Usage**
   - Check event listeners
   - Verify update frequency
   - Monitor calculations

2. **Memory Leaks**
   - Dispose resources
   - Clear timers
   - Clean up listeners

3. **UI Lag**
   - Debounce updates
   - Optimize calculations
   - Batch notifications

## API Versioning

The extension follows semantic versioning:
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

## Support

For issues and feature requests:
- GitHub Issues
- VS Code Extension Issues
- Documentation Updates