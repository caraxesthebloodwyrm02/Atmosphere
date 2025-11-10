import * as vscode from 'vscode';
import {MentalStateTracker} from './mentalState';
import {EnhancedJokeEngine} from './jokeEngine';
import {BackoffStrategy} from './backoff';
import {BackoffConfig} from './types';

export function activate(context: vscode.ExtensionContext) {
    // Initialize components
    const config=vscode.workspace.getConfiguration('mentalLoadBalancer');
    const backoffConfig: BackoffConfig={
        baseInterval: config.get('backoff.baseInterval',5),
        maxInterval: config.get('backoff.maxInterval',60),
        resetAfterBreak: config.get('backoff.resetAfterBreak',true)
    };

    const mentalState=new MentalStateTracker();
    const jokeEngine=new EnhancedJokeEngine(context);
    const backoff=new BackoffStrategy(backoffConfig);

    // Create status bar item
    const statusBarItem=vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.command='mentalLoadBalancer.showDashboard';
    context.subscriptions.push(statusBarItem);

    // Update status bar periodically
    setInterval(() => {
        const score=mentalState.calculatePressureScore();
        updateStatusBar(statusBarItem,score.total);
    },5000);

    // Register commands
    const showDashboard=vscode.commands.registerCommand(
        'mentalLoadBalancer.showDashboard',
        () => {
            const panel=vscode.window.createWebviewPanel(
                'mentalLoadDashboard',
                'Mental Load Dashboard',
                vscode.ViewColumn.Beside,
                {enableScripts: true}
            );
            updateDashboard(panel,mentalState);
        }
    );

    // Check mental state periodically
    setInterval(async () => {
        const score=mentalState.calculatePressureScore();

        if(score.total>0.7&&backoff.canTriggerIntervention()) {
            const joke=await jokeEngine.getContextualJoke(mentalState.getCurrentMetrics());
            showIntervention(joke,score);
            backoff.recordIntervention();
        }
    },30000);

    context.subscriptions.push(showDashboard);
}

function updateStatusBar(statusBarItem: vscode.StatusBarItem,score: number) {
    const icon=score>0.7? '⚠️':score>0.4? '⚡':'🧠';
    statusBarItem.text=`${icon} Load: ${Math.round(score*100)}%`;
    statusBarItem.show();
}

function showIntervention(joke: string,score: PressureScore) {
    const actions=['Take a Break','Snooze','Show Details'];

    vscode.window.showWarningMessage(
        `Mental Load Alert!\n\n${joke}`,
        ...actions
    ).then(selection => {
        if(selection==='Take a Break') {
            vscode.commands.executeCommand('mentalLoadBalancer.showDashboard');
        }
    });
}

function updateDashboard(panel: vscode.WebviewPanel,mentalState: MentalStateTracker) {
    const metrics=mentalState.getCurrentMetrics();
    const score=mentalState.calculatePressureScore();

    panel.webview.html=getDashboardHtml(metrics,score);
}

function getDashboardHtml(metrics: MentalStateMetrics,score: PressureScore): string {
    return `<!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: var(--vscode-font-family); padding: 20px; }
            .metric { margin: 15px 0; }
            .score-card {
                padding: 15px;
                border-radius: 5px;
                background: var(--vscode-editor-background);
                margin-bottom: 20px;
            }
            .progress {
                height: 8px;
                background: var(--vscode-progressBar-background);
                border-radius: 4px;
                margin-top: 5px;
            }
            .progress-fill {
                height: 100%;
                background: var(--vscode-progressBar-foreground);
                border-radius: 4px;
                transition: width 0.3s ease;
            }
        </style>
    </head>
    <body>
        <h2>Mental Load Dashboard</h2>
        
        <div class="score-card">
            <h3>Overall Pressure Score: ${Math.round(score.total*100)}%</h3>
            <div class="progress">
                <div class="progress-fill" style="width: ${score.total*100}%"></div>
            </div>
        </div>

        <div class="metric">
            <h4>Debugging Time</h4>
            <div>${Math.round(metrics.debuggingDuration)} minutes</div>
        </div>

        <div class="metric">
            <h4>Context Switches</h4>
            <div>${metrics.fileContextSwitches} switches</div>
        </div>

        <div class="metric">
            <h4>Error Count</h4>
            <div>${metrics.errorCount} errors</div>
        </div>

        <div class="metric">
            <h4>Session Duration</h4>
            <div>${Math.round((Date.now()-metrics.lastResetTime)/1000/60)} minutes</div>
        </div>
    </body>
    </html>`;
}

export function deactivate() {}