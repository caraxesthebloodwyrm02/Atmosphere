import numpy as np
from atmosphere_audio.pipeline import AudioPipeline, AudioNode, ProcessingContext


class GainNode(AudioNode):
    def __init__(self, gain: float):
        self.gain = gain

    def process(self, buffer: np.ndarray, context: ProcessingContext) -> np.ndarray:
        return buffer * self.gain


class TestAudioPipeline:
    """Test AudioPipeline functionality"""

    def test_init_empty(self):
        pipeline = AudioPipeline()
        assert len(pipeline.nodes) == 0
        assert pipeline.context.sample_rate == 44100

    def test_init_with_nodes(self):
        node1 = GainNode(0.5)
        node2 = GainNode(2.0)
        pipeline = AudioPipeline([node1, node2])
        assert len(pipeline.nodes) == 2
        assert pipeline.nodes[0] is node1
        assert pipeline.nodes[1] is node2

    def test_init_custom_sample_rate(self):
        pipeline = AudioPipeline(sample_rate=48000)
        assert pipeline.context.sample_rate == 48000

    def test_add_node(self):
        pipeline = AudioPipeline()
        node = GainNode(0.5)
        result = pipeline.add(node)
        assert result is pipeline  # Should return self for chaining
        assert len(pipeline.nodes) == 1
        assert pipeline.nodes[0] is node

    def test_process_empty_pipeline(self):
        pipeline = AudioPipeline()
        signal = np.array([1.0, 2.0, 3.0])
        result = pipeline.process(signal)
        np.testing.assert_array_equal(result, signal)

    def test_process_single_node(self):
        pipeline = AudioPipeline()
        pipeline.add(GainNode(0.5))
        signal = np.array([2.0, 4.0, 6.0])
        result = pipeline.process(signal)
        expected = np.array([1.0, 2.0, 3.0])
        np.testing.assert_array_equal(result, expected)

    def test_process_multiple_nodes(self):
        pipeline = AudioPipeline()
        pipeline.add(GainNode(0.5)).add(GainNode(4.0))
        signal = np.ones(8, dtype=float)
        result = pipeline.process(signal)
        # 0.5 * 4.0 = 2.0, so ones become 2.0
        expected = np.full(8, 2.0)
        np.testing.assert_array_equal(result, expected)

    def test_process_different_buffer_sizes(self):
        pipeline = AudioPipeline()
        pipeline.add(GainNode(2.0))

        # Test various buffer sizes
        for size in [1, 16, 1024, 44100]:
            signal = np.ones(size, dtype=float)
            result = pipeline.process(signal)
            expected = np.full(size, 2.0)
            np.testing.assert_array_equal(result, expected)

    def test_process_stereo_signal(self):
        pipeline = AudioPipeline()
        pipeline.add(GainNode(0.5))

        # Stereo signal (2 channels)
        signal = np.array([[1.0, 2.0], [3.0, 4.0]])  # Shape: (2, 2)
        result = pipeline.process(signal)
        expected = np.array([[0.5, 1.0], [1.5, 2.0]])
        np.testing.assert_array_equal(result, expected)

    def test_process_with_context_preservation(self):
        pipeline = AudioPipeline(sample_rate=48000)
        pipeline.add(GainNode(1.0))  # No-op gain

        signal = np.array([1.0, 2.0, 3.0])
        result = pipeline.process(signal)

        # Context should be preserved
        assert pipeline.context.sample_rate == 48000
        np.testing.assert_array_equal(result, signal)

    def test_pipeline_reuse(self):
        pipeline = AudioPipeline()
        pipeline.add(GainNode(2.0))

        signal1 = np.array([1.0, 2.0])
        result1 = pipeline.process(signal1)
        expected1 = np.array([2.0, 4.0])
        np.testing.assert_array_equal(result1, expected1)

        # Process again with different signal
        signal2 = np.array([3.0, 4.0, 5.0])
        result2 = pipeline.process(signal2)
        expected2 = np.array([6.0, 8.0, 10.0])
        np.testing.assert_array_equal(result2, expected2)


class TestProcessingContext:
    """Test ProcessingContext dataclass"""

    def test_default_values(self):
        context = ProcessingContext()
        assert context.sample_rate == 44100
        assert context.extra == {}

    def test_custom_sample_rate(self):
        context = ProcessingContext(sample_rate=96000)
        assert context.sample_rate == 96000
        assert context.extra == {}

    def test_extra_data(self):
        extra = {"gain": 0.8, "delay": 100}
        context = ProcessingContext(extra=extra)
        assert context.extra == extra
        # Note: dataclass assigns the passed dict directly, not a copy
        assert context.extra is extra


class TestGainNode:
    """Test the GainNode example implementation"""

    def test_gain_application(self):
        node = GainNode(0.5)
        context = ProcessingContext()
        signal = np.array([2.0, 4.0, 6.0])
        result = node.process(signal, context)
        expected = np.array([1.0, 2.0, 3.0])
        np.testing.assert_array_equal(result, expected)

    def test_zero_gain(self):
        node = GainNode(0.0)
        context = ProcessingContext()
        signal = np.array([1.0, 2.0, 3.0])
        result = node.process(signal, context)
        expected = np.array([0.0, 0.0, 0.0])
        np.testing.assert_array_equal(result, expected)

    def test_negative_gain(self):
        node = GainNode(-1.0)
        context = ProcessingContext()
        signal = np.array([1.0, 2.0, 3.0])
        result = node.process(signal, context)
        expected = np.array([-1.0, -2.0, -3.0])
        np.testing.assert_array_equal(result, expected)

    def test_context_unused(self):
        node = GainNode(2.0)
        context = ProcessingContext(sample_rate=48000, extra={"test": "value"})
        signal = np.array([1.0])
        result = node.process(signal, context)
        # GainNode doesn't use context, so it should work regardless
        assert result[0] == 2.0


