import {BackoffConfig} from './types';

export class BackoffStrategy {
    private currentStep: number=0;
    private lastInterventionTime: number=0;

    constructor(private config: BackoffConfig) {}

    getNextInterval(): number {
        const interval=Math.min(
            this.config.baseInterval*Math.pow(2,this.currentStep),
            this.config.maxInterval
        );
        this.currentStep++;
        return interval;
    }

    canTriggerIntervention(): boolean {
        const now=Date.now();
        const nextInterval=this.getNextInterval()*60*1000; // Convert to milliseconds
        return (now-this.lastInterventionTime)>=nextInterval;
    }

    recordIntervention() {
        this.lastInterventionTime=Date.now();
    }

    reset() {
        if(this.config.resetAfterBreak) {
            this.currentStep=0;
        }
    }
}