from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Protocol
import numpy as np


@dataclass
class ProcessingContext:
	sample_rate: int = 44100
	extra: Dict[str, Any] = field(default_factory=dict)


class AudioNode(Protocol):
	def process(self, buffer: np.ndarray, context: ProcessingContext) -> np.ndarray: ...


