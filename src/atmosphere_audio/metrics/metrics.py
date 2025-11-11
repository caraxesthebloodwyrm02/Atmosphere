from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TimerResult:
	elapsed_ms: float


def time_block(func):
	def wrapper(*args, **kwargs):
		start = time.time()
		try:
			return func(*args, **kwargs)
		finally:
			elapsed = (time.time() - start) * 1000.0
			# In a real deployment, export to metrics backend
			getattr(func, "__dict__", {}).setdefault("_last_elapsed_ms", elapsed)
	return wrapper


