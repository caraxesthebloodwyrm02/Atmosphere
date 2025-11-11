import numpy as np
import pytest
from src.delay.core.delay_essence import DelayEngine

def test_delay_engine_basic():
    engine = DelayEngine(sample_rate=44100, max_delay_ms=2000)
    signal = np.ones(1024, dtype=np.float32)
    # 50 ms delay, 0.5 feedback, 0.5 wet mix
    out = engine.process(signal, delay_time_ms=50, feedback=0.5, mix=0.5)
    assert out.shape == signal.shape
    # The first few samples should be attenuated (dry/wet mix)
    assert not np.allclose(out[:10], signal[:10])
