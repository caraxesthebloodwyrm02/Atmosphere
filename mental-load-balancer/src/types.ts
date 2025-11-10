import * as vscode from 'vscode';

export interface MentalStateMetrics {
    debuggingDuration: number;
    fileContextSwitches: number;
    errorPatterns: ErrorPattern[];
    timeOfDay: number;
    workSessionDuration: number;
    keystrokeCount: number;
    errorCount: number;
    lastResetTime: number;
}

export interface ErrorPattern {
    type: 'syntax'|'runtime'|'compilation';
    count: number;
    timeWindow: number;
}

export interface PressureScore {
    total: number;
    factors: {
        debugging: number;
        contextSwitches: number;
        timeOfDay: number;
        errors: number;
        keystrokes: number;
    };
}

export interface InterventionConfig {
    style: 'notification'|'popup'|'statusBar';
    severity: 'info'|'warning'|'critical';
    allowSnooze: boolean;
    showMetrics: boolean;
}

export interface BackoffConfig {
    baseInterval: number;
    maxInterval: number;
    resetAfterBreak: boolean;
}