#!/usr/bin/env python3
"""
Immutable Audit Log
Cryptographically linked, append-only audit logging for compliance and safety monitoring.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional


class ImmutableAuditLog:
    """Append-only cryptographic audit log"""

    def __init__(self, log_path: str = "data/audit.chain"):
        # Use relative path for Windows compatibility
        self.log_path = Path(log_path).resolve()
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        self.chain = []  # In-memory recent entries
        self.last_hash = self._load_last_hash()

    def _load_last_hash(self) -> str:
        """Load the hash of the last entry from the audit log file"""
        if not self.log_path.exists():
            return "genesis"  # Genesis hash for new log

        try:
            with open(self.log_path, 'rb') as f:
                last_hash = "genesis"
                for line in f:
                    try:
                        entry = json.loads(line.decode().strip())
                        last_hash = entry.get('merkle_root', last_hash)
                    except (json.JSONDecodeError, KeyError):
                        continue
                return last_hash
        except Exception:
            return "genesis"  # Fallback for corrupted log

    def submit(self, event_type: str, payload: Dict) -> str:
        """
        Append-only, cryptographically linked audit entry
        """
        # Create payload hash for integrity
        payload_hash = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()
        ).hexdigest()

        # Create linked entry
        entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'payload_hash': payload_hash,
            'previous_hash': self.last_hash,
            'merkle_root': self._compute_merkle_root(payload_hash, self.last_hash),
            'sequence_number': len(self.chain) + 1
        }

        # Sign with simple hash-based signature (in production, use proper crypto)
        entry['signature'] = self._sign(entry)

        # Append to file (append-only)
        try:
            with open(self.log_path, 'a+b') as f:
                entry_bytes = json.dumps(entry, sort_keys=True).encode() + b'\n'
                f.write(entry_bytes)
                f.flush()
                # Force write to disk
                os.fsync(f.fileno())
        except Exception as e:
            print(f"CRITICAL: Failed to write audit log: {e}")
            raise

        # Update chain
        self.chain.append(entry)
        self.last_hash = entry['merkle_root']

        # **Governance**: Prune in-memory chain to prevent memory leaks
        if len(self.chain) > 1000:
            self.chain = self.chain[-100:]

        return entry['merkle_root']

    def _compute_merkle_root(self, payload_hash: str, previous_hash: str) -> str:
        """Compute Merkle root for chain integrity"""
        combined = f"{previous_hash}:{payload_hash}"
        return hashlib.sha256(combined.encode()).hexdigest()

    def _sign(self, entry: Dict) -> str:
        """Create signature for entry (simplified for demo)"""
        # In production, use proper cryptographic signing
        entry_str = json.dumps(entry, sort_keys=True)
        return hashlib.sha256(entry_str.encode()).hexdigest()

    def verify_chain(self) -> bool:
        """
        **Governance Checkpoint**: Verify log integrity on startup
        """
        if not self.log_path.exists():
            return True  # Empty log is valid

        try:
            with open(self.log_path, 'rb') as f:
                prev_hash = None
                for line_num, line in enumerate(f, 1):
                    try:
                        entry = json.loads(line.decode().strip())

                        # Verify signature
                        expected_sig = self._sign(entry)
                        if entry.get('signature') != expected_sig:
                            print(f"Signature verification failed at line {line_num}")
                            return False

                        # Verify hash chain
                        if prev_hash and entry['previous_hash'] != prev_hash:
                            print(f"Hash chain broken at line {line_num}")
                            return False

                        prev_hash = entry['merkle_root']

                    except json.JSONDecodeError:
                        print(f"Invalid JSON at line {line_num}")
                        return False

        except Exception as e:
            print(f"Error verifying chain: {e}")
            return False

        return True

    def get_entries_for_learner(self, learner_id_hash: str) -> List[Dict]:
        """
        **Privacy**: Export all data about a learner for GDPR "right to access"
        """
        entries = []
        try:
            with open(self.log_path, 'rb') as f:
                for line in f:
                    entry = json.loads(line.decode().strip())
                    # In practice, you'd need to search payload hashes
                    # For demo, we'll return all entries (not privacy-compliant)
                    entries.append(entry)
        except Exception as e:
            print(f"Error reading audit log: {e}")

        return entries

    def export_for_regulator(self, start_time: float, end_time: float) -> str:
        """
        **Compliance**: Export cryptographically signed audit trail
        """
        # Filter entries by time range
        entries = [e for e in self.chain if start_time <= e['timestamp'] <= end_time]

        # Create signed export package
        export = {
            'entries': entries,
            'export_timestamp': time.time(),
            'regulator_signature': self._sign({'entries': entries}),
            'hash_chain_valid': self.verify_chain(),
            'export_metadata': {
                'total_entries': len(entries),
                'time_range': f"{start_time} to {end_time}",
                'export_version': '1.0'
            }
        }

        # Write to regulator-accessible path (use relative path for Windows)
        export_path = Path(f"regulator_export_{int(time.time())}.json").resolve()
        try:
            with open(export_path, 'w') as f:
                json.dump(export, f, indent=2, sort_keys=True)
        except Exception as e:
            print(f"Error writing regulator export: {e}")
            return ""

        return str(export_path)

    def count_events(self, level: str = None, event_type: str = None,
                    since_hours: float = 24) -> int:
        """Count events matching criteria"""
        cutoff_time = time.time() - (since_hours * 3600)
        count = 0

        for entry in self.chain:
            if entry['timestamp'] < cutoff_time:
                continue

            if level and entry.get('log_level') != level:
                continue

            if event_type and entry.get('event_type') != event_type:
                continue

            count += 1

        return count

    def get_recent_events(self, hours: float = 1) -> List[Dict]:
        """Get events from the last N hours"""
        cutoff_time = time.time() - (hours * 3600)
        return [e for e in self.chain if e['timestamp'] >= cutoff_time]


# Initialize global audit log
audit_log = ImmutableAuditLog("data/audit.chain")
