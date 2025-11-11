#!/usr/bin/env python3
"""
Privacy-Preserving Feature Extractor
Implements differential privacy, safety constraints, and audit logging for emotional features.
"""

import asyncio
import hashlib
import json
import os
import time
from collections import deque
from typing import Dict, List, Optional, Set
import numpy as np
from pathlib import Path

class VersionedFeatureState:
    """Immutable feature snapshot with versioning and privacy metadata"""
    def __init__(self, features: np.ndarray, source_path: str = "",
                 privacy_budget_consumed: float = 0.0):
        self.features = features.copy()  # Immutable copy
        self.version: int = int(time.time() * 1000)
        self.source_path: str = source_path
        self.privacy_budget_consumed: float = privacy_budget_consumed
        self.is_stable: bool = False
        self.was_noised: bool = False
        self.consent_verified: bool = False

    def is_compatible_with(self, other: 'VersionedFeatureState', max_drift_ms: int = 50) -> bool:
        """Ensure features are from the same temporal context"""
        return abs(self.version - other.version) < max_drift_ms


class PrivacyPreservingFeatureCache:
    """Feature cache with differential privacy and safety constraints"""

    def __init__(self, max_heat: int = 100, privacy_budget: float = 1.0):
        self.cache = {}
        self.lock = asyncio.Lock()
        self.max_heat = max_heat
        self.privacy_budget = privacy_budget
        self.budget_consumed = 0.0
        self.max_feature_age_ms = 100

        # **Governance**: Features that are inherently identifying are blocked
        self.blocked_features: Set[str] = {
            'exact_timestamp',
            'raw_audio_fingerprint',
            'ip_address',
            'learner_id_plaintext',
            'exact_location',
            'biometric_raw_data'
        }

        # Audit log for privacy violations
        self.privacy_audit_log = deque(maxlen=1000)

    async def extract_with_privacy(self, interaction: Dict) -> VersionedFeatureState:
        """
        Extract features with privacy preservation and safety constraints
        """
        # **Safety Checkpoint**: Block prohibited features before extraction
        blocked_detected = self.blocked_features & set(interaction.keys())
        if blocked_detected:
            await self._log_privacy_violation('blocked_features_detected', {
                'blocked_features': list(blocked_detected),
                'interaction_keys': list(interaction.keys())
            })
            raise PrivacyViolationException(
                f"Blocked features detected: {blocked_detected}"
            )

        # Extract features normally
        features = await self._extract_features(interaction)

        # **Privacy**: Add calibrated noise based on uncertainty
        if self.budget_consumed > self.privacy_budget * 0.8:
            # Budget nearly exhausted: inject maximum noise
            noise_scale = 1.0
        else:
            # Scale noise by interaction uncertainty (uncertain = more noise)
            noise_scale = interaction.get('model_uncertainty', 0.5)

        # Laplace mechanism for differential privacy
        private_features = self._add_laplace_noise(
            features,
            scale=noise_scale / max(self.privacy_budget - self.budget_consumed, 0.1)
        )

        # Track budget consumption
        self.budget_consumed += noise_scale

        # Create versioned state
        versioned = VersionedFeatureState(
            features=private_features,
            source_path='privacy_preserving_extractor',
            privacy_budget_consumed=self.budget_consumed
        )
        versioned.was_noised = True
        versioned.consent_verified = await self._verify_consent(interaction)

        return versioned

    async def _extract_features(self, interaction: Dict) -> np.ndarray:
        """Extract basic features (placeholder - extend with your actual feature extraction)"""
        # This would be your actual feature extraction logic
        # For now, create a simple feature vector
        features = []

        # Text-based features (if available)
        if 'text' in interaction:
            text = interaction['text']
            features.extend([
                len(text),  # Length
                text.count('?'),  # Questions
                text.count('!'),  # Exclamations
                sum(1 for c in text if c.isupper()) / len(text) if text else 0  # Capitalization ratio
            ])

        # Interaction timing features
        features.extend([
            interaction.get('response_time', 0),
            interaction.get('attempts', 1),
            interaction.get('correctness', 0.5)
        ])

        # Pad to fixed size
        while len(features) < 32:
            features.append(0.0)

        return np.array(features[:32], dtype=np.float32)

    def _add_laplace_noise(self, tensor: np.ndarray, scale: float) -> np.ndarray:
        """Add Laplace noise for differential privacy"""
        noise = np.random.laplace(0, scale, size=tensor.shape)
        return tensor + noise

    async def _verify_consent(self, interaction: Dict) -> bool:
        """Verify user consent for this interaction type"""
        # This would integrate with your PrivacyConsentManager
        # For now, assume consent is verified if learner_id is present
        return 'learner_id' in interaction

    async def _log_privacy_violation(self, violation_type: str, details: Dict):
        """Log privacy violations to audit trail"""
        entry = {
            'timestamp': time.time(),
            'violation_type': violation_type,
            'details': details,
            'budget_remaining': self.privacy_budget - self.budget_consumed
        }
        self.privacy_audit_log.append(entry)

    def get_privacy_stats(self) -> Dict:
        """Get privacy and safety statistics"""
        return {
            'privacy_budget_remaining': self.privacy_budget - self.budget_consumed,
            'privacy_budget_threshold_breached': self.budget_consumed > self.privacy_budget,
            'blocked_feature_requests_today': len([
                e for e in self.privacy_audit_log
                if e['timestamp'] > time.time() - 86400 and e['violation_type'] == 'blocked_features_detected'
            ]),
            'consent_verifications_today': len([
                e for e in self.privacy_audit_log
                if e['timestamp'] > time.time() - 86400 and 'consent' in e.get('violation_type', '')
            ])
        }


class PrivacyViolationException(Exception):
    """Exception raised when privacy constraints are violated"""
    pass


# Initialize global privacy-preserving cache
privacy_cache = PrivacyPreservingFeatureCache(privacy_budget=1.0)
