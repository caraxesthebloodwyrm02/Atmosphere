import numpy as np
import pytest

from atmosphere_audio.pipeline import AudioPipeline, ProcessingContext


class GainNode:
    def __init__(self, gain: float):
        self.gain = gain
    def process(self, buffer: np.ndarray, ctx: ProcessingContext) -> np.ndarray:
        return buffer * self.gain


@pytest.mark.e2e
def test_end_to_end_linear_pipeline():
    signal = np.ones(1024, dtype=float)
    p = AudioPipeline().add(GainNode(0.25)).add(GainNode(4.0))
    output = p.process(signal)
    assert np.allclose(output, signal)


