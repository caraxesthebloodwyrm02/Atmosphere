#!/usr/bin/env python3
"""
Import/Export Guardrail System
==============================

Security guardrails for data import and export operations requiring explicit user consent.
Prevents unauthorized data movement and enforces consent-based data governance.
"""

import json
import hashlib
import time
import json
import time
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

# Unique sys scoping with hash-based identifier
_sys_scope_guardrail = hash(id(sys)) % 1000000

import logging

# Add project path
sys.path.insert(0, str(Path(__file__).parent))

@dataclass
class ImportExportConsent:
    """Consent record for import/export operations"""
    consent_id: str
    operation_type: str  # 'import' or 'export'
    data_source: str
    data_destination: str
    data_format: str
    data_size: int
    purpose: str
    granted_at: float
    expires_at: float
    granted_by: str
    consent_hash: str
    restrictions: List[str] = field(default_factory=list)
    active: bool = True

class ImportExportViolation(Exception):
    """Raised when import/export guardrails are violated"""
    def __init__(self, operation: str, reason: str, details: Dict[str, Any] = None):
        self.operation = operation
        self.reason = reason
        self.details = details or {}
        super().__init__(f"Import/Export violation: {operation} - {reason}")

class ImportExportGuardrail:
    """Guardrail system for import/export operations"""

    def __init__(self, consent_store: str = "config/import_export_consents.json"):
        self.consent_store = Path(consent_store)
        self.consent_store.parent.mkdir(parents=True, exist_ok=True)
        self.consents: Dict[str, ImportExportConsent] = {}
        self.violation_callbacks: List[Callable] = []
        self.audit_log: List[Dict[str, Any]] = []

        self._load_consents()

        # Configure logging
        self.logger = logging.getLogger('import_export_guardrail')

    def _load_consents(self):
        """Load existing consents"""
        if self.consent_store.exists():
            try:
                with open(self.consent_store, 'r') as f:
                    data = json.load(f)
                    for consent_data in data.get('consents', []):
                        consent = ImportExportConsent(**consent_data)
                        self.consents[consent.consent_id] = consent
            except Exception as e:
                self.logger.error(f"Failed to load consents: {e}")

    def _save_consents(self):
        """Save consents to disk"""
        try:
            data = {
                'consents': [consent.__dict__ for consent in self.consents.values()],
                'last_updated': time.time()
            }
            with open(self.consent_store, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Failed to save consents: {e}")

    def grant_import_consent(self, data_source: str, data_format: str,
                           data_size: int, purpose: str,
                           restrictions: List[str] = None,
                           validity_hours: int = 24) -> str:
        """
        Grant consent for data import operation

        Args:
            data_source: Source of the data (URL, file path, etc.)
            data_format: Format of the data (json, csv, xml, etc.)
            data_size: Estimated size of data in bytes
            purpose: Purpose of the import
            restrictions: List of restrictions on the imported data
            validity_hours: How long the consent is valid

        Returns:
            consent_id: Unique identifier for the consent
        """
        return self._grant_consent('import', data_source, '', data_format,
                                 data_size, purpose, restrictions, validity_hours)

    def grant_export_consent(self, data_destination: str, data_format: str,
                           data_size: int, purpose: str,
                           restrictions: List[str] = None,
                           validity_hours: int = 24) -> str:
        """
        Grant consent for data export operation

        Args:
            data_destination: Destination for the data
            data_format: Format of the exported data
            data_size: Estimated size of exported data
            purpose: Purpose of the export
            restrictions: List of restrictions on the export
            validity_hours: How long the consent is valid

        Returns:
            consent_id: Unique identifier for the consent
        """
        return self._grant_consent('export', '', data_destination, data_format,
                                 data_size, purpose, restrictions, validity_hours)

    def _grant_consent(self, operation_type: str, data_source: str, data_destination: str,
                      data_format: str, data_size: int, purpose: str,
                      restrictions: List[str] = None, validity_hours: int = 24) -> str:

        consent_id = f"ie_{operation_type}_{int(time.time())}_{hashlib.md5(f'{data_source}{data_destination}{data_format}'.encode()).hexdigest()[:8]}"

        consent = ImportExportConsent(
            consent_id=consent_id,
            operation_type=operation_type,
            data_source=data_source,
            data_destination=data_destination,
            data_format=data_format,
            data_size=data_size,
            purpose=purpose,
            granted_at=time.time(),
            expires_at=time.time() + (validity_hours * 3600),
            granted_by=self._get_current_user(),
            consent_hash=self._generate_consent_hash(consent_id, operation_type, data_source, data_destination),
            restrictions=restrictions or []
        )

        self.consents[consent_id] = consent
        self._save_consents()

        self.logger.info(f"Import/Export consent granted: {consent_id} ({operation_type})")

        # Audit log entry
        self._audit_log('consent_granted', {
            'consent_id': consent_id,
            'operation_type': operation_type,
            'purpose': purpose
        })

        return consent_id

    def revoke_consent(self, consent_id: str) -> bool:
        """Revoke an import/export consent"""
        if consent_id in self.consents:
            consent = self.consents[consent_id]
            consent.active = False
            self._save_consents()

            self.logger.info(f"Import/Export consent revoked: {consent_id}")

            self._audit_log('consent_revoked', {
                'consent_id': consent_id,
                'operation_type': consent.operation_type
            })

            return True
        return False

    def check_import_guardrail(self, data_source: str, data_format: str = None,
                             data_size: int = 0) -> bool:
        """
        Check if an import operation is allowed by guardrails

        Args:
            data_source: Source of the data
            data_format: Format of the data (optional)
            data_size: Size of the data (optional)

        Returns:
            bool: True if allowed, False if blocked
        """
        return self._check_operation_guardrail('import', data_source, '',
                                             data_format, data_size)

    def check_export_guardrail(self, data_destination: str, data_format: str = None,
                             data_size: int = 0) -> bool:
        """
        Check if an export operation is allowed by guardrails

        Args:
            data_destination: Destination for the data
            data_format: Format of the data (optional)
            data_size: Size of the data (optional)

        Returns:
            bool: True if allowed, False if blocked
        """
        return self._check_operation_guardrail('export', '', data_destination,
                                             data_format, data_size)

    def _check_operation_guardrail(self, operation_type: str, data_source: str,
                                 data_destination: str, data_format: str = None,
                                 data_size: int = 0) -> bool:

        # Find matching active consents
        current_time = time.time()

        for consent in self.consents.values():
            if (consent.operation_type == operation_type and
                consent.active and
                consent.expires_at > current_time):

                # Check if consent matches the operation
                source_match = not data_source or consent.data_source == data_source
                dest_match = not data_destination or consent.data_destination == data_destination
                format_match = not data_format or consent.data_format == data_format

                # Size check (allow some tolerance)
                size_match = (data_size == 0 or
                            abs(data_size - consent.data_size) / consent.data_size < 0.5)

                if source_match and dest_match and format_match and size_match:
                    self._audit_log('guardrail_allowed', {
                        'operation_type': operation_type,
                        'data_source': data_source,
                        'data_destination': data_destination,
                        'consent_id': consent.consent_id
                    })
                    return True

        # No matching consent found
        self._audit_log('guardrail_blocked', {
            'operation_type': operation_type,
            'data_source': data_source,
            'data_destination': data_destination,
            'reason': 'no_matching_consent'
        })

        # Trigger violation callbacks
        for callback in self.violation_callbacks:
            try:
                callback(ImportExportViolation(
                    operation_type,
                    'No matching consent found',
                    {
                        'data_source': data_source,
                        'data_destination': data_destination,
                        'data_format': data_format,
                        'data_size': data_size
                    }
                ))
            except Exception as e:
                self.logger.error(f"Violation callback failed: {e}")

        return False

    def register_violation_callback(self, callback: Callable):
        """Register a callback for guardrail violations"""
        self.violation_callbacks.append(callback)

    def get_consent_status(self) -> Dict[str, Any]:
        """Get comprehensive consent status"""
        current_time = time.time()

        active_consents = []
        expired_consents = []
        revoked_consents = []

        for consent in self.consents.values():
            if not consent.active:
                revoked_consents.append(consent.consent_id)
            elif consent.expires_at <= current_time:
                expired_consents.append(consent.consent_id)
            else:
                active_consents.append({
                    'consent_id': consent.consent_id,
                    'operation_type': consent.operation_type,
                    'purpose': consent.purpose,
                    'expires_at': consent.expires_at,
                    'time_remaining': consent.expires_at - current_time
                })

        return {
            'total_consents': len(self.consents),
            'active_consents': active_consents,
            'expired_consents': expired_consents,
            'revoked_consents': revoked_consents,
            'current_time': current_time
        }

    def cleanup_expired_consents(self) -> int:
        """Clean up expired consents"""
        current_time = time.time()
        expired_count = 0

        for consent in list(self.consents.values()):
            if consent.expires_at <= current_time and consent.active:
                consent.active = False
                expired_count += 1

                self._audit_log('consent_expired', {
                    'consent_id': consent.consent_id,
                    'operation_type': consent.operation_type
                })

        if expired_count > 0:
            self._save_consents()
            self.logger.info(f"Cleaned up {expired_count} expired consents")

        return expired_count

    def _get_current_user(self) -> str:
        """Get current user identifier"""
        try:
            import getpass
            return getpass.getuser()
        except:
            return "unknown"

    def _generate_consent_hash(self, consent_id: str, operation_type: str,
                              data_source: str, data_destination: str) -> str:
        """Generate hash for consent verification"""
        content = f"{consent_id}:{operation_type}:{data_source}:{data_destination}"
        return hashlib.sha256(content.encode()).hexdigest()

    def _audit_log(self, event_type: str, details: Dict[str, Any]):
        """Add entry to audit log"""
        entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'details': details
        }
        self.audit_log.append(entry)

        # Keep audit log manageable (last 1000 entries)
        if len(self.audit_log) > 1000:
            self.audit_log = self.audit_log[-500:]

    def get_audit_trail(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get audit trail for specified time period"""
        cutoff = time.time() - (hours * 3600)
        return [entry for entry in self.audit_log if entry['timestamp'] > cutoff]


# Global guardrail instance
import_export_guardrail = ImportExportGuardrail()


# Protected import/export functions
def protected_import_data(data_source: str, data_format: str = None,
                         data_size: int = 0, **kwargs) -> Any:
    """
    Protected data import with guardrail enforcement

    Args:
        data_source: Source of the data
        data_format: Format of the data
        data_size: Size of the data
        **kwargs: Additional import parameters

    Returns:
        Imported data if consent granted

    Raises:
        ImportExportViolation: If no valid consent exists
    """
    if not import_export_guardrail.check_import_guardrail(data_source, data_format, data_size):
        raise ImportExportViolation(
            'import',
            f'No consent for importing from {data_source}',
            {'data_source': data_source, 'data_format': data_format, 'data_size': data_size}
        )

    # If consent granted, perform the actual import
    # This is where you would implement the actual import logic
    # For now, return a mock result
    return f"Imported data from {data_source}"


def protected_export_data(data: Any, data_destination: str, data_format: str = None,
                         data_size: int = 0, **kwargs) -> bool:
    """
    Protected data export with guardrail enforcement

    Args:
        data: Data to export
        data_destination: Destination for the data
        data_format: Format of the data
        data_size: Size of the data
        **kwargs: Additional export parameters

    Returns:
        True if export successful

    Raises:
        ImportExportViolation: If no valid consent exists
    """
    if not import_export_guardrail.check_export_guardrail(data_destination, data_format, data_size):
        raise ImportExportViolation(
            'export',
            f'No consent for exporting to {data_destination}',
            {'data_destination': data_destination, 'data_format': data_format, 'data_size': data_size}
        )

    # If consent granted, perform the actual export
    # This is where you would implement the actual export logic
    # For now, simulate success
    return True


# CLI Integration Functions
def guardrail_consent_command(operation_type: str, data_source: str = "", data_destination: str = "",
                            data_format: str = "json", data_size: int = 0,
                            purpose: str = "", validity_hours: int = 24):
    """CLI command to grant import/export consent"""
    try:
        if operation_type == 'import':
            consent_id = import_export_guardrail.grant_import_consent(
                data_source, data_format, data_size, purpose, validity_hours=validity_hours
            )
        elif operation_type == 'export':
            consent_id = import_export_guardrail.grant_export_consent(
                data_destination, data_format, data_size, purpose, validity_hours=validity_hours
            )
        else:
            print(f"❌ Invalid operation type: {operation_type}")
            return False

        print(f"✅ Import/Export consent granted: {consent_id}")
        print(f"   Operation: {operation_type}")
        print(f"   Purpose: {purpose}")
        print(f"   Valid for: {validity_hours} hours")
        return True

    except Exception as e:
        print(f"❌ Failed to grant consent: {e}")
        return False


def guardrail_revoke_command(consent_id: str):
    """CLI command to revoke import/export consent"""
    if import_export_guardrail.revoke_consent(consent_id):
        print(f"✅ Consent revoked: {consent_id}")
        return True
    else:
        print(f"❌ Consent not found: {consent_id}")
        return False


def guardrail_status_command():
    """CLI command to show guardrail status"""
    status = import_export_guardrail.get_consent_status()

    print("🔒 Import/Export Guardrail Status")
    print("=" * 50)
    print(f"Total Consents: {status['total_consents']}")
    print(f"Active Consents: {len(status['active_consents'])}")
    print(f"Expired Consents: {len(status['expired_consents'])}")
    print(f"Revoked Consents: {len(status['revoked_consents'])}")

    if status['active_consents']:
        print("\nActive Consents:")
        for consent in status['active_consents']:
            hours_remaining = consent['time_remaining'] / 3600
            print(f"  📋 {consent['consent_id']}: {consent['operation_type']} - {consent['purpose']}")
            print(f"     Expires in: {hours_remaining:.1f} hours")

    # Cleanup expired consents
    cleaned = import_export_guardrail.cleanup_expired_consents()
    if cleaned > 0:
        print(f"\n🧹 Cleaned up {cleaned} expired consents")


def guardrail_test_command(operation_type: str, target: str, data_format: str = "json", data_size: int = 0):
    """CLI command to test guardrail enforcement"""
    try:
        if operation_type == 'import':
            allowed = import_export_guardrail.check_import_guardrail(target, data_format, data_size)
        elif operation_type == 'export':
            allowed = import_export_guardrail.check_export_guardrail(target, data_format, data_size)
        else:
            print(f"❌ Invalid operation type: {operation_type}")
            return False

        if allowed:
            print(f"✅ Guardrail allows {operation_type} operation")
        else:
            print(f"❌ Guardrail blocks {operation_type} operation - consent required")

        return allowed

    except Exception as e:
        print(f"❌ Guardrail test failed: {e}")
        return False


# Enhanced guardrail functions with pattern awareness
def enhanced_import_guardrail(target: str, data_format: str = None,
                            data_size: int = 0, content_sample: str = None) -> bool:
    """
    Enhanced import guardrail combining consent and pattern checks
    """
    # First check existing consent-based guardrail
    consent_check = import_export_guardrail.check_import_guardrail(target, data_format or 'auto', data_size)
    if not consent_check:
        return False

    # Then check pattern-based guardrail
    try:
        from .pattern_guardrail import pattern_aware_import_check
        pattern_result = pattern_aware_import_check(target, data_format, data_size, content_sample)
        return pattern_result['action'] != 'block'
    except Exception as e:
        # If pattern checking fails, fall back to consent-only
        import_export_guardrail.logger.warning(f"Pattern check failed, using consent-only: {e}")
        return consent_check


def enhanced_export_guardrail(target: str, data_format: str = None,
                            data_size: int = 0, content_sample: str = None) -> bool:
    """
    Enhanced export guardrail combining consent and pattern checks
    """
    # First check existing consent-based guardrail
    consent_check = import_export_guardrail.check_export_guardrail(target, data_format or 'auto', data_size)
    if not consent_check:
        return False

    # Then check pattern-based guardrail
    try:
        from .pattern_guardrail import pattern_aware_export_check
        pattern_result = pattern_aware_export_check(target, data_format, data_size, content_sample)
        return pattern_result['action'] != 'block'
    except Exception as e:
        # If pattern checking fails, fall back to consent-only
        import_export_guardrail.logger.warning(f"Pattern check failed, using consent-only: {e}")
        return consent_check


if __name__ == "__main__":
    print("🔒 Import/Export Guardrail System Demo")
    print("=" * 50)

    # Register a violation callback
    def violation_alert(violation):
        print(f"🚨 GUARDRAIL VIOLATION: {violation.operation} - {violation.reason}")

    import_export_guardrail.register_violation_callback(violation_alert)

    # Show initial status
    guardrail_status_command()

    print("\n1. Testing blocked operations (should trigger violations):")
    try:
        protected_import_data("https://external-api.com/data", "json", 1024)
    except ImportExportViolation as e:
        print(f"   ✅ Import blocked: {e}")

    try:
        protected_export_data({"sensitive": "data"}, "https://external.com/upload", "json", 512)
    except ImportExportViolation as e:
        print(f"   ✅ Export blocked: {e}")

    print("\n2. Granting import consent:")
    consent_id = guardrail_consent_command(
        'import',
        'https://trusted-api.com/data',
        data_format='json',
        data_size=1024,
        purpose='Testing import functionality',
        validity_hours=1
    )

    print("\n3. Testing allowed operation:")
    try:
        result = protected_import_data("https://trusted-api.com/data", "json", 1024)
        print(f"   ✅ Import allowed: {result}")
    except ImportExportViolation as e:
        print(f"   ❌ Import still blocked: {e}")

    print("\n4. Revoking consent:")
    guardrail_revoke_command(consent_id)

    print("\n5. Testing blocked operation after revocation:")
    try:
        protected_import_data("https://trusted-api.com/data", "json", 1024)
    except ImportExportViolation as e:
        print(f"   ✅ Import blocked after revocation: {e}")

    print("\n6. Final status:")
    guardrail_status_command()

    print("\n🎉 Import/Export Guardrail System Ready!")
    print("   ✓ Consent-based import/export control")
    print("   ✓ Violation detection and alerting")
    print("   ✓ Time-limited consent validity")
    print("   ✓ Comprehensive audit trails")
    print("   ✓ CLI management interface")
