import * as vscode from 'vscode';
import {MentalStateMetrics} from './types';

export class EnhancedJokeEngine {
    private readonly jokes={
        debugging: [
            "Why did the debugger break up with the function? Because it had too much baggage! 🧳",
            "Debugging: Being the detective in a crime movie where you're also the murderer 🔍",
            "Don't worry, that bug you've been chasing for 4 hours is probably just a semicolon... 😅",
            "Time flies like an arrow, fruit flies like a banana, but bugs... bugs just stick around 🐛"
        ],
        lateNight: [
            "Even my coffee needs coffee right now... ☕️",
            "The code is dark and full of errors 🌙",
            "It's not a bug, it's a feature... that's what I'm telling myself at 3 AM 🦉",
            "Remember when you said 'just one more commit'? That was 4 hours ago 🕐"
        ],
        contextSwitch: [
            "My brain has too many tabs open 📑",
            "Task switching? More like task juggling! 🤹",
            "I'm not multitasking, I'm rapidly failing at multiple things! 😅",
            "Context switching: The art of forgetting what you were doing 🔄"
        ],
        error: [
            "Error 404: Brain not found 🧠",
            "The good news: I found the bug! The bad news: That wasn't the bug 🐞",
            "Keep calm and blame it on the compiler 🎯",
            "It works on my machine... oh wait, I am on my machine 💻"
        ],
        language: {
            typescript: [
                "Why do TypeScript developers wear glasses? Because they can't C# 👓",
                "TypeScript: Making JavaScript developers miss 'any' 😉",
            ],
            python: [
                "Why do Python developers wear glasses? Because they can't C! 🐍",
                "What's a snake's favorite programming language? Python! 🐍"
            ],
            javascript: [
                "Why did the JavaScript developer quit his job? Because he didn't get arrays! 💔",
                "JavaScript: Where 'undefined' is not 'null' but 'null' is an object 🤔"
            ]
        }
    };

    constructor(private context: vscode.ExtensionContext) {}

    async getContextualJoke(metrics: MentalStateMetrics): Promise<string> {
        // Determine the most relevant joke category based on metrics
        const pressurePoints=this.analyzePressurePoints(metrics);
        const category=this.selectCategory(pressurePoints);

        // Get the active editor's language for extra context
        const language=vscode.window.activeTextEditor?.document.languageId||'';

        // Select and return the most appropriate joke
        return this.selectJoke(category,language);
    }

    private analyzePressurePoints(metrics: MentalStateMetrics): string[] {
        const points: string[]=[];

        if(metrics.debuggingDuration>60) points.push('debugging');
        if(this.isLateNight()) points.push('lateNight');
        if(metrics.fileContextSwitches>10) points.push('contextSwitch');
        if(metrics.errorCount>5) points.push('error');

        return points;
    }

    private selectCategory(pressurePoints: string[]): string {
        if(pressurePoints.length===0) return 'language';

        // Select the most relevant category based on severity
        const priorities={
            debugging: 4,
            lateNight: 3,
            error: 2,
            contextSwitch: 1
        };

        return pressurePoints.sort((a,b) =>
            (priorities[a]||0)-(priorities[b]||0)
        )[0];
    }

    private selectJoke(category: string,language: string): string {
        if(category==='language'&&this.jokes.language[language]) {
            return this.getRandomJoke(this.jokes.language[language]);
        }

        return this.getRandomJoke(this.jokes[category]||this.jokes.debugging);
    }

    private getRandomJoke(jokes: string[]): string {
        return jokes[Math.floor(Math.random()*jokes.length)];
    }

    private isLateNight(): boolean {
        const hour=new Date().getHours();
        return hour>=22||hour<=6;
    }
}