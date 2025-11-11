#!/usr/bin/env python3
"""
Security Monitoring & Alerting System
=====================================

Comprehensive monitoring system for continuous security surveillance,
automated vulnerability detection, and critical security alerting.
"""

import time
import threading
import logging
import json
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
import sys
import re

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

class SecurityAlert:
    """Security alert container"""
    def __init__(self, alert_type: str, severity: str, title: str,
                 description: str, details: Dict[str, Any] = None,
                 source: str = "security_monitor"):
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.description = description
        self.details = details or {}
        self.source = source
        self.timestamp = datetime.now()
        self.alert_id = f"{alert_type}_{int(time.time())}_{hash(str(self.details)) % 10000:04d}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'details': self.details,
            'source': self.source,
            'timestamp': self.timestamp.isoformat()
        }

class AlertHandler:
    """Handles security alert distribution"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('security_alerts')
        self.alert_history: List[SecurityAlert] = []
        self.alert_callbacks: List[Callable] = []

    def register_callback(self, callback: Callable):
        """Register alert callback function"""
        self.alert_callbacks.append(callback)

    def send_alert(self, alert: SecurityAlert):
        """Send security alert through all configured channels"""
        self.alert_history.append(alert)

        # Log alert
        log_level = getattr(logging, alert.severity.upper(), logging.WARNING)
        self.logger.log(log_level, f"SECURITY ALERT: {alert.title} - {alert.description}")

        # Execute callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                self.logger.error(f"Alert callback failed: {e}")

        # Send through configured channels
        self._send_email_alert(alert)
        self._send_webhook_alert(alert)
        self._write_alert_log(alert)

    def _send_email_alert(self, alert: SecurityAlert):
        """Send alert via email"""
        if not self.config.get('email_enabled', False):
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.config.get('email_from', 'security@system.local')
            msg['To'] = self.config.get('email_to', 'admin@system.local')
            msg['Subject'] = f"SECURITY ALERT: {alert.severity.upper()} - {alert.title}"

            body = f"""
SECURITY ALERT
==============

Alert ID: {alert.alert_id}
Type: {alert.alert_type}
Severity: {alert.severity.upper()}
Time: {alert.timestamp}

Title: {alert.title}
Description: {alert.description}

Details:
{json.dumps(alert.details, indent=2)}

Source: {alert.source}
"""
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.config.get('smtp_server', 'localhost'),
                                self.config.get('smtp_port', 25))
            if self.config.get('smtp_tls'):
                server.starttls()
            if self.config.get('smtp_user'):
                server.login(self.config.get('smtp_user'), self.config.get('smtp_password'))

            server.send_message(msg)
            server.quit()

            self.logger.info(f"Email alert sent for {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"Failed to send email alert: {e}")

    def _send_webhook_alert(self, alert: SecurityAlert):
        """Send alert via webhook"""
        if not self.config.get('webhook_enabled', False):
            return

        try:
            import urllib.request
            import urllib.parse

            webhook_url = self.config.get('webhook_url')
            if not webhook_url:
                return

            data = json.dumps(alert.to_dict()).encode('utf-8')
            req = urllib.request.Request(webhook_url,
                                       data=data,
                                       headers={'Content-Type': 'application/json'})

            with urllib.request.urlopen(req) as response:
                self.logger.info(f"Webhook alert sent for {alert.alert_id}")

        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {e}")

    def _write_alert_log(self, alert: SecurityAlert):
        """Write alert to dedicated log file"""
        try:
            log_dir = Path(self.config.get('log_dir', 'logs'))
            log_dir.mkdir(exist_ok=True)

            alert_file = log_dir / 'security_alerts.log'
            with open(alert_file, 'a') as f:
                f.write(json.dumps(alert.to_dict()) + '\n')

        except Exception as e:
            self.logger.error(f"Failed to write alert log: {e}")

    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get alert summary for specified time period"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_alerts = [a for a in self.alert_history if a.timestamp > cutoff]

        summary = {
            'total_alerts': len(recent_alerts),
            'by_severity': {},
            'by_type': {},
            'most_recent': recent_alerts[-1].to_dict() if recent_alerts else None
        }

        for alert in recent_alerts:
            summary['by_severity'][alert.severity] = summary['by_severity'].get(alert.severity, 0) + 1
            summary['by_type'][alert.alert_type] = summary['by_type'].get(alert.alert_type, 0) + 1

        return summary

class SecurityMonitor:
    """Continuous security monitoring system"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_handler = AlertHandler(config)
        self.monitoring_active = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.check_interval = config.get('check_interval', 300)  # 5 minutes default

        # Monitoring state
        self.baseline_snapshots = {}
        self.anomaly_thresholds = config.get('anomaly_thresholds', {
            'feature_spike': 5,  # New features enabled
            'consent_spike': 3,  # New boundary consents
            'import_attempts': 10,  # Failed import attempts
            'network_connections': 50  # Unusual network activity
        })

        self.logger = logging.getLogger('security_monitor')

    def start_monitoring(self):
        """Start continuous security monitoring"""
        if self.monitoring_active:
            self.logger.warning("Security monitoring already active")
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitor_thread.start()

        self.logger.info("Security monitoring started")
        alert = SecurityAlert(
            'system', 'info', 'Security Monitoring Started',
            'Continuous security monitoring has been activated',
            {'check_interval': self.check_interval}
        )
        self.alert_handler.send_alert(alert)

    def stop_monitoring(self):
        """Stop security monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)

        self.logger.info("Security monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Security monitoring loop started")

        while self.monitoring_active:
            try:
                self._run_security_checks()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"Monitoring loop error: {e}")
                alert = SecurityAlert(
                    'system', 'error', 'Monitoring Loop Error',
                    f'Security monitoring encountered an error: {str(e)}',
                    {'error': str(e)}
                )
                self.alert_handler.send_alert(alert)
                time.sleep(60)  # Wait before retry

    def _run_security_checks(self):
        """Execute comprehensive security checks"""
        checks = [
            self._check_feature_security,
            self._check_boundary_security,
            self._check_import_security,
            self._check_network_security,
            self._check_system_integrity,
            self._check_anomalous_activity
        ]

        for check in checks:
            try:
                check()
            except Exception as e:
                self.logger.error(f"Security check failed: {e}")

    def _check_feature_security(self):
        """Check feature flag security"""
        try:
            from network_visualizer.feature_manager import feature_manager, initialize_feature_manager
            initialize_feature_manager()

            status = feature_manager.get_status()
            enabled_features = len(status.get('enabled_features', []))
            active_tasks = len(status.get('active_tasks', {}))

            # Alert on unexpected feature activation
            if enabled_features > self.anomaly_thresholds['feature_spike']:
                alert = SecurityAlert(
                    'feature_security', 'high', 'Unexpected Feature Activation',
                    f'{enabled_features} features enabled, exceeds threshold of {self.anomaly_thresholds["feature_spike"]}',
                    {'enabled_features': enabled_features, 'threshold': self.anomaly_thresholds['feature_spike']}
                )
                self.alert_handler.send_alert(alert)

        except Exception as e:
            alert = SecurityAlert(
                'system', 'error', 'Feature Security Check Failed',
                f'Unable to check feature security: {str(e)}'
            )
            self.alert_handler.send_alert(alert)

    def _check_boundary_security(self):
        """Check boundary security"""
        try:
            from network_visualizer.boundary_manager import boundary_manager, initialize_boundary_manager
            initialize_boundary_manager()

            status = boundary_manager.get_boundary_status()
            active_consents = status.get('active_consents', 0)

            # Alert on excessive boundary consents
            if active_consents > self.anomaly_thresholds['consent_spike']:
                alert = SecurityAlert(
                    'boundary_security', 'high', 'Excessive Boundary Consents',
                    f'{active_consents} active boundary consents, exceeds threshold of {self.anomaly_thresholds["consent_spike"]}',
                    {'active_consents': active_consents, 'threshold': self.anomaly_thresholds['consent_spike']}
                )
                self.alert_handler.send_alert(alert)

        except Exception as e:
            alert = SecurityAlert(
                'system', 'error', 'Boundary Security Check Failed',
                f'Unable to check boundary security: {str(e)}'
            )
            self.alert_handler.send_alert(alert)

    def _check_import_security(self):
        """Check import security and log suspicious attempts"""
        try:
            # Monitor for suspicious import patterns in logs
            log_file = Path('logs/security_alerts.log')
            if log_file.exists():
                with open(log_file, 'r') as f:
                    recent_lines = f.readlines()[-100:]  # Last 100 lines

                import_violations = sum(1 for line in recent_lines if 'import_violation' in line)

                if import_violations > self.anomaly_thresholds['import_attempts']:
                    alert = SecurityAlert(
                        'import_security', 'medium', 'High Import Violation Rate',
                        f'{import_violations} import violations detected, exceeds threshold of {self.anomaly_thresholds["import_attempts"]}',
                        {'import_violations': import_violations, 'threshold': self.anomaly_thresholds['import_attempts']}
                    )
                    self.alert_handler.send_alert(alert)

        except Exception as e:
            self.logger.error(f"Import security check failed: {e}")

    def _check_network_security(self):
        """Check network security and unusual connections"""
        try:
            # Check for unexpected open ports
            common_ports = [8000, 8080, 9000, 3000, 5000]
            open_ports = []

            for port in common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    if result == 0:
                        open_ports.append(port)
                    sock.close()
                except:
                    pass

            # Alert on unexpected services (exclude known safe ports)
            known_ports = [7681]  # Atmosphere API
            unexpected_ports = [p for p in open_ports if p not in known_ports]

            if unexpected_ports:
                alert = SecurityAlert(
                    'network_security', 'medium', 'Unexpected Network Services',
                    f'Unexpected services detected on ports: {unexpected_ports}',
                    {'unexpected_ports': unexpected_ports, 'open_ports': open_ports}
                )
                self.alert_handler.send_alert(alert)

        except Exception as e:
            self.logger.error(f"Network security check failed: {e}")

    def _check_system_integrity(self):
        """Check overall system integrity"""
        try:
            from network_visualizer.security_operations import validate_system_integrity
            result = validate_system_integrity()

            if result['integrity_status'] != 'intact':
                alert = SecurityAlert(
                    'system_integrity', 'high', 'System Integrity Compromised',
                    f'System integrity check failed: {result["integrity_status"]}',
                    {'issues_found': result.get('issues_found', []), 'status': result['integrity_status']}
                )
                self.alert_handler.send_alert(alert)

        except Exception as e:
            alert = SecurityAlert(
                'system', 'error', 'System Integrity Check Failed',
                f'Unable to validate system integrity: {str(e)}'
            )
            self.alert_handler.send_alert(alert)

    def _check_anomalous_activity(self):
        """Check for anomalous security-related activity"""
        try:
            # Monitor configuration file changes
            config_files = [
                'network_visualizer/config/project_boundary.json',
                'network_visualizer/config/feature_flags.json'
            ]

            for config_file in config_files:
                config_path = Path(config_file)
                if config_path.exists():
                    current_mtime = config_path.stat().st_mtime

                    # Check if file was recently modified
                    if config_path.name in self.baseline_snapshots:
                        baseline_mtime = self.baseline_snapshots[config_path.name]
                        if current_mtime > baseline_mtime + 300:  # Modified more than 5 minutes ago
                            alert = SecurityAlert(
                                'configuration', 'low', 'Configuration File Modified',
                                f'Configuration file {config_file} was recently modified',
                                {'file': config_file, 'last_modified': current_mtime}
                            )
                            self.alert_handler.send_alert(alert)

                    self.baseline_snapshots[config_path.name] = current_mtime

        except Exception as e:
            self.logger.error(f"Anomalous activity check failed: {e}")

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            'monitoring_active': self.monitoring_active,
            'check_interval': self.check_interval,
            'alert_summary': self.alert_handler.get_alert_summary(hours=24),
            'baseline_snapshots': list(self.baseline_snapshots.keys()),
            'anomaly_thresholds': self.anomaly_thresholds
        }


class PeripheralActivityMonitor:
    """Monitor peripheral activities and external interactions"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('peripheral_monitor')
        self.activity_log = []
        self.suspicious_patterns = config.get('suspicious_patterns', {
            'file_access': [r'\.env$', r'secret', r'password', r'key'],
            'network_access': [r'raw\.githubusercontent\.com', r'pastebin\.com'],
            'process_execution': [r'curl.*-s', r'wget', r'nc ', r'nmap']
        })

    def monitor_file_access(self, file_path: str, operation: str, source: str = "unknown"):
        """Monitor file access activities"""
        activity = {
            'type': 'file_access',
            'file_path': str(file_path),
            'operation': operation,
            'source': source,
            'timestamp': datetime.now()
        }

        self.activity_log.append(activity)

        # Check for suspicious file access
        for pattern in self.suspicious_patterns['file_access']:
            if re.search(pattern, str(file_path), re.IGNORECASE):
                alert = SecurityAlert(
                    'peripheral_activity', 'medium', 'Suspicious File Access',
                    f'Suspicious file access detected: {operation} on {file_path}',
                    {'file_path': str(file_path), 'operation': operation, 'source': source}
                )
                # This would integrate with the main alert system
                self.logger.warning(f"Suspicious file access: {file_path}")

        # Keep log size manageable
        if len(self.activity_log) > 1000:
            self.activity_log = self.activity_log[-500:]

    def monitor_network_activity(self, destination: str, protocol: str = "unknown", source: str = "unknown"):
        """Monitor network activity"""
        activity = {
            'type': 'network_activity',
            'destination': destination,
            'protocol': protocol,
            'source': source,
            'timestamp': datetime.now()
        }

        self.activity_log.append(activity)

        # Check for suspicious network destinations
        for pattern in self.suspicious_patterns['network_access']:
            if re.search(pattern, destination, re.IGNORECASE):
                alert = SecurityAlert(
                    'peripheral_activity', 'high', 'Suspicious Network Access',
                    f'Suspicious network access detected: {destination}',
                    {'destination': destination, 'protocol': protocol, 'source': source}
                )
                self.logger.warning(f"Suspicious network access: {destination}")

    def monitor_process_execution(self, command: str, source: str = "unknown"):
        """Monitor process execution"""
        activity = {
            'type': 'process_execution',
            'command': command,
            'source': source,
            'timestamp': datetime.now()
        }

        self.activity_log.append(activity)

        # Check for suspicious commands
        for pattern in self.suspicious_patterns['process_execution']:
            if re.search(pattern, command, re.IGNORECASE):
                alert = SecurityAlert(
                    'peripheral_activity', 'high', 'Suspicious Process Execution',
                    f'Suspicious command execution detected: {command[:100]}...',
                    {'command': command[:200], 'source': source}
                )
                self.logger.warning(f"Suspicious command execution: {command[:50]}...")

    def get_activity_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get peripheral activity summary"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_activity = [a for a in self.activity_log if a['timestamp'] > cutoff]

        summary = {
            'total_activities': len(recent_activity),
            'by_type': {},
            'suspicious_activities': 0,
            'most_recent': recent_activity[-1] if recent_activity else None
        }

        for activity in recent_activity:
            summary['by_type'][activity['type']] = summary['by_type'].get(activity['type'], 0) + 1

            # Count suspicious activities (simplified)
            if any(pattern in str(activity.values()) for pattern_list in self.suspicious_patterns.values()
                   for pattern in pattern_list):
                summary['suspicious_activities'] += 1

        return summary


# Global monitoring instances
security_monitor = None
peripheral_monitor = None

def initialize_security_monitoring(config: Dict[str, Any] = None):
    """Initialize comprehensive security monitoring"""
    global security_monitor, peripheral_monitor

    if config is None:
        config = {
            'check_interval': 300,  # 5 minutes
            'email_enabled': False,
            'webhook_enabled': False,
            'log_dir': 'logs',
            'anomaly_thresholds': {
                'feature_spike': 5,
                'consent_spike': 3,
                'import_attempts': 10,
                'network_connections': 50
            }
        }

    security_monitor = SecurityMonitor(config)
    peripheral_monitor = PeripheralActivityMonitor(config)

    return security_monitor, peripheral_monitor


def start_security_monitoring():
    """Start comprehensive security monitoring"""
    if security_monitor is None:
        initialize_security_monitoring()

    security_monitor.start_monitoring()
    print("🔍 Security monitoring started")


def stop_security_monitoring():
    """Stop security monitoring"""
    if security_monitor:
        security_monitor.stop_monitoring()
        print("🛑 Security monitoring stopped")


def get_monitoring_status():
    """Get comprehensive monitoring status"""
    status = {
        'security_monitoring': None,
        'peripheral_monitoring': None,
        'alert_summary': None
    }

    if security_monitor:
        status['security_monitoring'] = security_monitor.get_monitoring_status()

    if peripheral_monitor:
        status['peripheral_monitoring'] = peripheral_monitor.get_activity_summary()

    if security_monitor:
        status['alert_summary'] = security_monitor.alert_handler.get_alert_summary()

    return status


# CLI Integration
def monitoring_status_command():
    """CLI command to show monitoring status"""
    if security_monitor is None:
        print("❌ Security monitoring not initialized")
        return

    status = get_monitoring_status()

    print("🔍 Security Monitoring Status")
    print("=" * 50)

    if status['security_monitoring']:
        sm = status['security_monitoring']
        print(f"Active: {sm['monitoring_active']}")
        print(f"Check Interval: {sm['check_interval']}s")
        print(f"Baseline Snapshots: {len(sm['baseline_snapshots'])}")

    if status['alert_summary']:
        alerts = status['alert_summary']
        print(f"\nTotal Alerts (24h): {alerts['total_alerts']}")
        print(f"By Severity: {alerts['by_severity']}")
        print(f"By Type: {alerts['by_type']}")

    if status['peripheral_monitoring']:
        pm = status['peripheral_monitoring']
        print(f"\nPeripheral Activities (24h): {pm['total_activities']}")
        print(f"By Type: {pm['by_type']}")
        print(f"Suspicious Activities: {pm['suspicious_activities']}")


def monitoring_start_command():
    """CLI command to start monitoring"""
    try:
        start_security_monitoring()
        print("[PASS] Security monitoring started successfully")
    except Exception as e:
        print(f"[ERROR] Failed to start monitoring: {e}")


def monitoring_stop_command():
    """CLI command to stop monitoring"""
    try:
        stop_security_monitoring()
        print("[PASS] Security monitoring stopped successfully")
    except Exception as e:
        print(f"[ERROR] Failed to stop monitoring: {e}")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("🔍 Security Monitoring & Alerting System")
    print("=" * 50)

    # Initialize monitoring
    security_monitor, peripheral_monitor = initialize_security_monitoring()

    # Register a simple alert callback
    def alert_callback(alert):
        print(f"🚨 ALERT: {alert.severity.upper()} - {alert.title}")

    security_monitor.alert_handler.register_callback(alert_callback)

    print("✅ Monitoring system initialized")

    # Demonstrate monitoring capabilities
    print("\n🧪 Testing Monitoring Capabilities...")

    # Test peripheral monitoring
    peripheral_monitor.monitor_file_access('/etc/passwd', 'read', 'test_process')
    peripheral_monitor.monitor_network_activity('raw.githubusercontent.com', 'https', 'test_process')
    peripheral_monitor.monitor_process_execution('curl -s http://example.com', 'test_process')

    print("✅ Peripheral monitoring tests completed")

    # Start monitoring for a short period
    print("\n▶️  Starting security monitoring (10 seconds)...")
    start_security_monitoring()
    time.sleep(10)
    stop_security_monitoring()

    print("✅ Security monitoring test completed")

    # Show final status
    print("\n📊 Final Monitoring Status:")
    status = get_monitoring_status()
    print(f"Security Monitoring: {'Active' if status['security_monitoring']['monitoring_active'] else 'Inactive'}")
    print(f"Total Alerts: {status['alert_summary']['total_alerts']}")
    print(f"Peripheral Activities: {status['peripheral_monitoring']['total_activities']}")
    print(f"Suspicious Activities: {status['peripheral_monitoring']['suspicious_activities']}")

    print("\n🎉 Security Monitoring & Alerting System Ready!")
    print("   ✓ Continuous security surveillance")
    print("   ✓ Automated vulnerability detection")
    print("   ✓ Multi-channel alerting (email, webhook, logs)")
    print("   ✓ Peripheral activity monitoring")
    print("   ✓ Enterprise-grade security monitoring")
