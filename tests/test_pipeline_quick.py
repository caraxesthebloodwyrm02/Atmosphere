"""
Quick coverage tests for audio pipeline module.
These tests focus on core pipeline functionality to boost coverage quickly.
"""

import pytest
import numpy as np
from src.atmosphere_audio.pipeline import AudioPipeline, AudioNode, ProcessingContext


class GainNode(AudioNode):
    """Simple gain node for testing"""
    def __init__(self, gain: float = 1.0):
        self.gain = gain

    def process(self, buffer: np.ndarray, context: ProcessingContext) -> np.ndarray:
        return buffer * self.gain


def test_pipeline_linear_gain():
    """Test basic linear gain application"""
    signal = np.ones(1024)
    pipeline = AudioPipeline().add(GainNode(2.0))
    output = pipeline.process(signal)
    assert np.allclose(output, signal * 2.0)


def test_pipeline_initialization():
    """Test pipeline initialization"""
    pipeline = AudioPipeline()
    assert len(pipeline.nodes) == 0


def test_gain_node_initialization():
    """Test gain node creation"""
    gain_node = GainNode(1.5)
    assert gain_node.gain == 1.5


def test_pipeline_multiple_nodes():
    """Test pipeline with multiple nodes"""
    signal = np.ones(100)

    # Create pipeline with two gain stages
    pipeline = AudioPipeline()
    pipeline.add(GainNode(2.0))
    pipeline.add(GainNode(0.5))

    output = pipeline.process(signal)

    # Expected: signal * 2.0 * 0.5 = signal * 1.0
    assert np.allclose(output, signal)


def test_zero_gain():
    """Test zero gain (silence)"""
    signal = np.ones(100)
    pipeline = AudioPipeline().add(GainNode(0.0))
    output = pipeline.process(signal)
    assert np.allclose(output, np.zeros(100))


def test_negative_gain():
    """Test negative gain (phase inversion)"""
    signal = np.ones(100)
    pipeline = AudioPipeline().add(GainNode(-1.0))
    output = pipeline.process(signal)
    assert np.allclose(output, -signal)
