from __future__ import annotations

from typing import List
import numpy as np

from .nodes import AudioNode, ProcessingContext


class AudioPipeline:
	def __init__(self, nodes: List[AudioNode] | None = None, sample_rate: int = 44100):
		self.nodes: List[AudioNode] = list(nodes or [])
		self.context = ProcessingContext(sample_rate=sample_rate)

	def add(self, node: AudioNode) -> "AudioPipeline":
		self.nodes.append(node)
		return self

	def process(self, buffer: np.ndarray) -> np.ndarray:
		output = buffer
		for node in self.nodes:
			output = node.process(output, self.context)
		return output


