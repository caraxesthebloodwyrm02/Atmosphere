#!/usr/bin/env python3
"""
Project Boundary Manager
========================

Security boundary system that prevents cross-project integration unless
explicit user consent is granted. Acts as a firewall for project boundaries,
similar to feature flags but for inter-project communication.

Features managed:
- Cross-project imports
- Shared data access
- API endpoint exposure
- Tool integration sharing
- Path traversal permissions

All cross-project interactions DENIED by default. Only explicit consent enables them.
"""

import json
import hashlib
import time
import sys
from .boundary_security import BoundarySecurityEnforcer
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
import re

# Unique sys scoping with hash-based identifier
_sys_scope_boundary_manager = hash(id(sys)) % 1000000

class BoundaryViolation(Exception):
    """Raised when boundary rules are violated"""
    pass


class ProjectBoundaryManager:
    """Manages project boundary permissions and consent"""

    def __init__(self, project_root: Path, boundary_config: str = "config/project_boundary.json"):
        self.project_root = project_root.resolve()
        self.boundary_config = project_root / boundary_config
        self.boundary_config.parent.mkdir(parents=True, exist_ok=True)

        # Security enforcer for advanced threat detection
        self.security_enforcer = BoundarySecurityEnforcer()

        # Boundary rules - DENY ALL by default
        self.allowed_projects: Set[str] = set()
        self.allowed_paths: Set[str] = set()
        self.allowed_imports: Set[str] = set()
        self.consent_records: Dict[str, Dict] = {}

        # Load existing boundaries
        self._load_boundaries()

    def _load_boundaries(self):
        """Load boundary configuration"""
        if self.boundary_config.exists():
            try:
                with open(self.boundary_config, 'r') as f:
                    data = json.load(f)
                    self.allowed_projects = set(data.get('allowed_projects', []))
                    self.allowed_paths = set(data.get('allowed_paths', []))
                    self.allowed_imports = set(data.get('allowed_imports', []))
                    self.consent_records = data.get('consent_records', {})
            except (json.JSONDecodeError, FileNotFoundError):
                pass

    def _save_boundaries(self):
        """Save boundary configuration"""
        data = {
            'allowed_projects': list(self.allowed_projects),
            'allowed_paths': list(self.allowed_paths),
            'allowed_imports': list(self.allowed_imports),
            'consent_records': self.consent_records,
            'last_updated': time.time()
        }
        try:
            with open(self.boundary_config, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def grant_consent(self, project_name: str, project_path: str,
                     permissions: List[str], reason: str = "") -> str:
        """
        Grant explicit consent for cross-project integration

        Args:
            project_name: Name of the external project
            project_path: Path to the external project
            permissions: List of permissions to grant
            reason: Reason for granting consent

        Returns:
            consent_id: Unique identifier for this consent
        """
        consent_id = f"{project_name}_{int(time.time())}_{hashlib.md5(project_path.encode()).hexdigest()[:8]}"

        # Validate project path exists and is outside our boundary
        external_path = Path(project_path).resolve()
        if not external_path.exists():
            raise BoundaryViolation(f"External project path does not exist: {project_path}")

        if self._is_within_boundary(external_path):
            raise BoundaryViolation(f"Project path is within current boundary: {project_path}")

        # Record consent
        self.consent_records[consent_id] = {
            'project_name': project_name,
            'project_path': str(external_path),
            'permissions': permissions,
            'reason': reason,
            'granted_at': time.time(),
            'granted_by': self._get_current_user(),
            'consent_hash': self._generate_consent_hash(project_name, external_path, permissions)
        }

        # Apply permissions
        if 'project_access' in permissions:
            self.allowed_projects.add(project_name)
        if 'path_access' in permissions:
            self.allowed_paths.add(str(external_path))
        if 'import_access' in permissions:
            # Allow imports from this project
            self.allowed_imports.add(f"{project_name}.*")

        self._save_boundaries()

        print(f"🔓 Boundary consent granted: {consent_id}")
        print(f"   Project: {project_name}")
        print(f"   Permissions: {', '.join(permissions)}")

        return consent_id

    def revoke_consent(self, consent_id: str) -> bool:
        """Revoke consent and remove associated permissions"""
        if consent_id not in self.consent_records:
            return False

        consent = self.consent_records[consent_id]
        project_name = consent['project_name']
        project_path = consent['project_path']
        permissions = consent['permissions']

        # Remove permissions
        if 'project_access' in permissions:
            self.allowed_projects.discard(project_name)
        if 'path_access' in permissions:
            self.allowed_paths.discard(project_path)
        if 'import_access' in permissions:
            self.allowed_imports.discard(f"{project_name}.*")

        # Remove consent record
        del self.consent_records[consent_id]
        self._save_boundaries()

        print(f"🔒 Boundary consent revoked: {consent_id}")
        return True

    def check_boundary(self, operation: str, target: str, source_project: str = "unknown") -> bool:
        """
        Check if an operation across boundary is allowed with security validation

        Args:
            operation: Type of operation ('import', 'path_access', 'api_call', etc.)
            target: Target of the operation (module path, file path, etc.)
            source_project: Source project requesting the operation

        Returns:
            bool: True if allowed, False if denied
        """
        # First perform basic boundary check
        basic_allowed = False
        if operation == 'import':
            basic_allowed = self._check_import_boundary(target)
        elif operation == 'path_access':
            basic_allowed = self._check_path_boundary(target)
        elif operation == 'api_call':
            basic_allowed = self._check_api_boundary(target)
        else:
            return False

        if not basic_allowed:
            return False

        # Now perform advanced security validation
        try:
            if operation == 'import':
                return self.security_enforcer.enforce_import_security(target, source_project)
            elif operation == 'path_access':
                return self.security_enforcer.enforce_path_security(target, operation, source_project)
            elif operation == 'api_call':
                # Parse endpoint and method from target if it's a combined string
                if isinstance(target, str) and ' ' in target:
                    parts = target.split(' ', 1)
                    endpoint = parts[0]
                    method = parts[1] if len(parts) > 1 else 'GET'
                    data = None
                else:
                    endpoint = target
                    method = 'GET'
                    data = None
                return self.security_enforcer.enforce_api_security(endpoint, method, data, source_project)
            else:
                return False
        except Exception:
            # If security validation fails, deny access
            return False

    def _check_import_boundary(self, module_path: str) -> bool:
        """Check if importing from external module is allowed"""
        # Check if module matches allowed patterns
        for allowed_pattern in self.allowed_imports:
            if re.match(allowed_pattern.replace('*', '.*'), module_path):
                return True
        return False

    def _check_path_boundary(self, file_path: str) -> bool:
        """Check if accessing external path is allowed"""
        target_path = Path(file_path).resolve()

        # Check if path is within allowed external paths
        for allowed_path in self.allowed_paths:
            allowed_path_obj = Path(allowed_path)
            try:
                target_path.relative_to(allowed_path_obj)
                return True
            except ValueError:
                continue
        return False

    def _check_api_boundary(self, endpoint: str) -> bool:
        """Check if API calls to external projects are allowed"""
        # For now, deny all external API calls
        # Could be extended to allow specific endpoints
        return False

    def _is_within_boundary(self, path: Path) -> bool:
        """Check if a path is within the current project's boundary"""
        try:
            path.relative_to(self.project_root)
            return True
        except ValueError:
            return False

    def _get_current_user(self) -> str:
        """Get current user identifier"""
        import getpass
        try:
            return getpass.getuser()
        except:
            return "unknown"

    def _generate_consent_hash(self, project_name: str, project_path: Path, permissions: List[str]) -> str:
        """Generate hash for consent verification"""
        content = f"{project_name}:{project_path}:{','.join(sorted(permissions))}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get_boundary_status(self) -> Dict[str, Any]:
        """Get comprehensive boundary status"""
        return {
            'project_root': str(self.project_root),
            'allowed_projects': list(self.allowed_projects),
            'allowed_paths': list(self.allowed_paths),
            'allowed_imports': list(self.allowed_imports),
            'active_consents': len(self.consent_records),
            'consent_records': self.consent_records
        }

    def emergency_lockdown(self) -> int:
        """Emergency: revoke all consents and lock down boundary"""
        consent_count = len(self.consent_records)
        self.allowed_projects.clear()
        self.allowed_paths.clear()
        self.allowed_imports.clear()
        self.consent_records.clear()
        self._save_boundaries()

        print(f"🚨 EMERGENCY BOUNDARY LOCKDOWN: {consent_count} consents revoked")
        return consent_count


# Global boundary manager instance
boundary_manager = None

def initialize_boundary_manager(project_root: Path = None):
    """Initialize the global boundary manager"""
    global boundary_manager
    if project_root is None:
        # Try to find project root
        current = Path.cwd()
        for parent in [current] + list(current.parents):
            if (parent / 'pyproject.toml').exists() or (parent / 'setup.py').exists():
                project_root = parent
                break
        if project_root is None:
            project_root = Path.cwd()

    boundary_manager = ProjectBoundaryManager(project_root)
    return boundary_manager


def check_cross_project_import(module_name: str, source_project: str = "unknown") -> bool:
    """
    Check if importing from external project is allowed.
    This function is meant to be called from import hooks.
    """
    if boundary_manager is None:
        initialize_boundary_manager()

    # Allow internal imports
    if not module_name.startswith(('atmosphere.', 'network_visualizer.')):
        return boundary_manager.check_boundary('import', module_name, source_project)

    return True  # Internal imports always allowed


def protected_import(module_name: str, source_project: str = "unknown"):
    """
    Protected import that checks boundary permissions with security validation

    Usage:
        from boundary_manager import protected_import
        my_module = protected_import('external_project.module')
    """
    if not check_cross_project_import(module_name, source_project):
        raise BoundaryViolation(
            f"Cross-project import denied: {module_name}. "
            "Use 'network-visualizer boundary consent' to grant permission."
        )

    return __import__(module_name)


# CLI Integration functions
def boundary_consent_command(project_name: str, project_path: str,
                           permissions: List[str], reason: str = ""):
    """CLI command to grant boundary consent"""
    if boundary_manager is None:
        initialize_boundary_manager()

    try:
        consent_id = boundary_manager.grant_consent(project_name, project_path, permissions, reason)
        print(f"✅ Consent granted with ID: {consent_id}")
        return True
    except BoundaryViolation as e:
        print(f"❌ Boundary violation: {e}")
        return False


def boundary_revoke_command(consent_id: str):
    """CLI command to revoke boundary consent"""
    if boundary_manager is None:
        initialize_boundary_manager()

    if boundary_manager.revoke_consent(consent_id):
        print(f"✅ Consent revoked: {consent_id}")
        return True
    else:
        print(f"❌ Consent not found: {consent_id}")
        return False


def boundary_status_command():
    """CLI command to show boundary status"""
    if boundary_manager is None:
        initialize_boundary_manager()

    status = boundary_manager.get_boundary_status()

    print("🔒 Project Boundary Status")
    print("=" * 50)
    print(f"Project Root: {status['project_root']}")
    print(f"Allowed Projects: {', '.join(status['allowed_projects']) or 'None'}")
    print(f"Allowed Paths: {len(status['allowed_paths'])}")
    print(f"Allowed Imports: {len(status['allowed_imports'])}")
    print(f"Active Consents: {status['active_consents']}")

    if status['consent_records']:
        print("\nActive Consents:")
        for consent_id, record in status['consent_records'].items():
            print(f"  📋 {consent_id}: {record['project_name']} ({', '.join(record['permissions'])})")


def boundary_emergency_command():
    """CLI command for emergency boundary lockdown"""
    if boundary_manager is None:
        initialize_boundary_manager()

    revoked = boundary_manager.emergency_lockdown()
    print(f"🚨 Emergency boundary lockdown completed. {revoked} consents revoked.")


if __name__ == "__main__":
    # Demo usage
    print("🔒 Project Boundary Manager Demo")
    initialize_boundary_manager()

    # Show initial status
    boundary_status_command()

    print("\nAttempting protected import...")
    try:
        # This should fail without consent
        protected_import('atmosphere.api.learning_companion_api')
    except BoundaryViolation as e:
        print(f"Expected boundary violation: {e}")

    print("\nGranting consent...")
    consent_id = boundary_consent_command(
        'Atmosphere',
        str(Path.cwd().parent / 'Atmosphere'),
        ['import_access', 'path_access'],
        'Demo integration'
    )

    print("\nNew boundary status:")
    boundary_status_command()

    print(f"\nTesting import after consent...")
    try:
        # This should now work
        module = protected_import('atmosphere.api.learning_companion_api')
        print("✅ Protected import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")

    print(f"\nRevoking consent {consent_id}...")
    boundary_revoke_command(consent_id)

    print("\nFinal boundary status:")
    boundary_status_command()
