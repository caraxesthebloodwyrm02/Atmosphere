from __future__ import annotations

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class SecretSpec:
	env: str
	required: bool = False


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
	"""
	Centralized secret accessor. Reads from environment only.
	Extend here for keyring/secret managers as needed.
	"""
	val = os.getenv(name)
	if val is None:
		return default
	return val


def require_secret(name: str) -> str:
	val = get_secret(name)
	if not val:
		raise RuntimeError(f"Missing required secret: {name}")
	return val


