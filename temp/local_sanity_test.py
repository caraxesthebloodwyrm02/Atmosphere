import sys
sys.path.insert(0, 'src')

import numpy as np
import atmosphere_audio as aa
import atmosphere_audio.cli as cli
import atmosphere_audio.pipeline as pl

print('VERSION', aa.__version__)
exit_code = cli.main(['--version'])
print('CLI_EXIT', exit_code)

class GainNode:
    def __init__(self, gain: float):
        self.gain = gain
    def process(self, buffer: np.ndarray, ctx):
        return buffer * self.gain

signal = np.ones(8, dtype=float)
pipe = pl.AudioPipeline().add(GainNode(0.5)).add(GainNode(2.0))
out = pipe.process(signal)
print('PIPE_EQ', bool(np.allclose(out, signal)))


