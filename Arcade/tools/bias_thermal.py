#!/usr/bin/env python3
"""
Bias Thermal Scanner
Real-time disparate impact monitoring for emotional detection models.
"""

import time
from collections import defaultdict
from typing import Dict, List, Optional
import asyncio


class BiasThermalScanner:
    """Real-time disparate impact monitoring for bias detection"""

    def __init__(self, protected_attributes: List[str]):
        self.protected_attributes = protected_attributes  # e.g., ['speech_pattern', 'response_language']
        self.detection_rates = defaultdict(lambda: defaultdict(lambda: {'total': 0, 'correct': 0}))
        self.bias_alerts = []
        self.alert_history = []

        # **Governance**: Maximum allowed detection rate disparity
        self.disparate_impact_threshold = 0.8  # 80% rule

        # Track detection events for analysis
        self.detection_log = []

    async def log_detection(self, learner_attributes: Dict, detected_state: str, was_correct: bool):
        """
        Track detection rates by protected attribute
        """
        detection_event = {
            'timestamp': time.time(),
            'detected_state': detected_state,
            'was_correct': was_correct,
            'learner_attributes': learner_attributes.copy(),
            'protected_attributes_logged': []
        }

        for attr in self.protected_attributes:
            group = learner_attributes.get(attr, 'unknown')
            self.detection_rates[attr][group]['total'] += 1

            if was_correct:
                self.detection_rates[attr][group]['correct'] += 1

            detection_event['protected_attributes_logged'].append({
                'attribute': attr,
                'group': group,
                'total_count': self.detection_rates[attr][group]['total'],
                'correct_count': self.detection_rates[attr][group]['correct']
            })

        self.detection_log.append(detection_event)

        # Check for bias after each detection
        alert = self.get_bias_alert()
        if alert:
            self.bias_alerts.append(alert)
            await self._trigger_bias_response(alert)

    def compute_disparate_impact_ratio(self, attribute: str) -> float:
        """
        Compute ratio: minority_group_detection_rate / majority_group_detection_rate
        """
        rates = {}
        for group, counts in self.detection_rates[attribute].items():
            if counts['total'] > 0:
                rates[group] = counts['correct'] / counts['total']
            else:
                rates[group] = 0.0

        if not rates:
            return 1.0

        # Find majority group (highest sample count)
        majority_group = max(self.detection_rates[attribute],
                           key=lambda g: self.detection_rates[attribute][g]['total'])
        majority_rate = rates[majority_group]

        if majority_rate == 0:
            return 0.0

        # Find worst minority ratio
        minority_rates = [rate for group, rate in rates.items() if group != majority_group]
        if not minority_rates:
            return 1.0

        return min(minority_rates) / majority_rate

    def get_bias_alert(self) -> Optional[Dict]:
        """
        **Governance Checkpoint**: Auto-disable model if bias threshold breached
        """
        for attr in self.protected_attributes:
            ratio = self.compute_disparate_impact_ratio(attr)

            if ratio < self.disparate_impact_threshold:
                alert = {
                    'alert_level': 'critical',
                    'attribute': attr,
                    'disparate_impact_ratio': ratio,
                    'threshold': self.disparate_impact_threshold,
                    'recommended_action': 'disable_model',
                    'reason': f"Bias detected: {attr} has disparate impact ratio {ratio:.2f} < {self.disparate_impact_threshold}",
                    'timestamp': time.time(),
                    'detection_rates': dict(self.detection_rates[attr])
                }

                self.alert_history.append(alert)
                return alert

        return None

    async def _trigger_bias_response(self, alert: Dict):
        """
        Execute automated response to bias detection
        """
        print(f"🚨 BIAS ALERT: {alert['reason']}")

        # This would integrate with your model management system
        # For now, log the alert and recommendation

        # Could disable the model, trigger retraining, or escalate to human review
        if alert['recommended_action'] == 'disable_model':
            print("⚠️  Model disabled due to bias detection")
            # In production, this would set a flag to disable the biased model

    def get_bias_statistics(self) -> Dict:
        """Get comprehensive bias monitoring statistics"""
        stats = {
            'monitored_attributes': self.protected_attributes,
            'bias_alerts_triggered_today': len([
                a for a in self.alert_history
                if a['timestamp'] > time.time() - 86400
            ]),
            'worst_disparate_impact_ratio': 1.0,
            'bias_monitor_status': 'healthy'
        }

        # Calculate worst disparate impact ratio
        worst_ratio = 1.0
        for attr in self.protected_attributes:
            ratio = self.compute_disparate_impact_ratio(attr)
            if ratio < worst_ratio:
                worst_ratio = ratio

        stats['worst_disparate_impact_ratio'] = worst_ratio

        # Determine status
        if worst_ratio < self.disparate_impact_threshold:
            stats['bias_monitor_status'] = 'critical'
        elif worst_ratio < 0.9:
            stats['bias_monitor_status'] = 'warning'
        else:
            stats['bias_monitor_status'] = 'healthy'

        return stats

    def get_protected_attribute_breakdown(self) -> Dict:
        """Get detailed breakdown by protected attribute"""
        breakdown = {}

        for attr in self.protected_attributes:
            breakdown[attr] = {
                'groups': {},
                'disparate_impact_ratio': self.compute_disparate_impact_ratio(attr)
            }

            for group, counts in self.detection_rates[attr].items():
                breakdown[attr]['groups'][group] = {
                    'total_detections': counts['total'],
                    'correct_detections': counts['correct'],
                    'accuracy_rate': counts['correct'] / counts['total'] if counts['total'] > 0 else 0.0
                }

        return breakdown


# Initialize global bias scanner
bias_scanner = BiasThermalScanner(protected_attributes=['speech_pattern', 'response_language', 'interaction_style'])
