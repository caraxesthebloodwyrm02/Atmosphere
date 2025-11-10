import * as vscode from 'vscode';
import {MentalStateMetrics,PressureScore,ErrorPattern} from './types';

export class MentalStateTracker {
    private metrics: MentalStateMetrics={
        debuggingDuration: 0,
        fileContextSwitches: 0,
        errorPatterns: [],
        timeOfDay: 0,
        workSessionDuration: 0,
        keystrokeCount: 0,
        errorCount: 0,
        lastResetTime: Date.now()
    };

    private readonly PRESSURE_WEIGHTS={
        debugging: 0.3,
        contextSwitches: 0.2,
        timeOfDay: 0.15,
        errors: 0.2,
        keystrokes: 0.15
    };

    constructor() {
        this.setupListeners();
    }

    private setupListeners() {
        // Track debugging sessions
        vscode.debug.onDidStartDebugSession(() => {
            this.metrics.debuggingDuration=Date.now();
        });

        vscode.debug.onDidTerminateDebugSession(() => {
            if(this.metrics.debuggingDuration>0) {
                const duration=(Date.now()-this.metrics.debuggingDuration)/1000/60; // in minutes
                this.metrics.debuggingDuration=duration;
            }
        });

        // Track file switches
        vscode.window.onDidChangeActiveTextEditor(() => {
            this.metrics.fileContextSwitches++;
        });

        // Track errors
        vscode.workspace.onDidChangeTextDocument(() => {
            this.updateErrorPatterns();
        });
    }

    private updateErrorPatterns() {
        const diagnostics=vscode.languages.getDiagnostics();
        let newErrors=0;

        for(const [uri,diags] of diagnostics) {
            newErrors+=diags.filter(d => d.severity===vscode.DiagnosticSeverity.Error).length;
        }

        if(newErrors>this.metrics.errorCount) {
            const pattern: ErrorPattern={
                type: 'compilation',
                count: newErrors-this.metrics.errorCount,
                timeWindow: Date.now()
            };
            this.metrics.errorPatterns.push(pattern);
        }

        this.metrics.errorCount=newErrors;
    }

    calculatePressureScore(): PressureScore {
        const now=Date.now();
        const hour=new Date().getHours();

        // Calculate individual factors
        const debuggingScore=Math.min(this.metrics.debuggingDuration/60,1); // Cap at 1 hour
        const switchesScore=Math.min(this.metrics.fileContextSwitches/20,1); // Cap at 20 switches
        const timeScore=(hour>=22||hour<=6)? 1:(hour>=18? 0.5:0);
        const errorScore=Math.min(this.metrics.errorCount/10,1); // Cap at 10 errors
        const keystrokeScore=Math.min(this.metrics.keystrokeCount/1000,1); // Cap at 1000 keystrokes

        // Calculate weighted total
        const total=
            debuggingScore*this.PRESSURE_WEIGHTS.debugging+
            switchesScore*this.PRESSURE_WEIGHTS.contextSwitches+
            timeScore*this.PRESSURE_WEIGHTS.timeOfDay+
            errorScore*this.PRESSURE_WEIGHTS.errors+
            keystrokeScore*this.PRESSURE_WEIGHTS.keystrokes;

        return {
            total,
            factors: {
                debugging: debuggingScore,
                contextSwitches: switchesScore,
                timeOfDay: timeScore,
                errors: errorScore,
                keystrokes: keystrokeScore
            }
        };
    }

    reset() {
        this.metrics={
            debuggingDuration: 0,
            fileContextSwitches: 0,
            errorPatterns: [],
            timeOfDay: new Date().getHours(),
            workSessionDuration: 0,
            keystrokeCount: 0,
            errorCount: 0,
            lastResetTime: Date.now()
        };
    }

    getCurrentMetrics(): MentalStateMetrics {
        return {...this.metrics};
    }
}