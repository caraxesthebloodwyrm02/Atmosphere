#!/usr/bin/env python3
"""
Tests for Delay Essence with Audio Emotion Analysis
"""

import unittest
from delay_essence import Delay


class TestDelayEmotion(unittest.TestCase):
    """Test emotion-based delay functionality."""

    def test_emotion_modulation_calm(self):
        """Test calm emotion reduces modulation."""
        delay = Delay(emotion_type='calm', filter_mod=0.5)
        result = delay.process_signal("test")
        self.assertIn("(+calm: -0.1 mod)", result)

    def test_emotion_modulation_tense(self):
        """Test tense emotion increases modulation."""
        delay = Delay(emotion_type='tense', filter_mod=0.5)
        result = delay.process_signal("test")
        self.assertIn("(+tense: +0.2 mod)", result)

    def test_emotion_modulation_joyful(self):
        """Test joyful emotion adjusts modulation positively."""
        delay = Delay(emotion_type='joyful', filter_mod=0.5)
        result = delay.process_signal("test")
        self.assertIn("(+joyful: +0.15 mod)", result)

    def test_tactile_feedback_joyful(self):
        """Test tactile feedback for joyful emotion."""
        delay = Delay(emotion_type='joyful', tactile_feedback=True)
        result = delay.process_signal("test")
        self.assertIn("Tactile: warm waves, uplifting harmonics", result)

    def test_tactile_feedback_tense(self):
        """Test tactile feedback for tense emotion."""
        delay = Delay(emotion_type='tense', tactile_feedback=True)
        result = delay.process_signal("test")
        self.assertIn("Tactile: sharp pulses, heightened sensitivity", result)

    def test_tactile_feedback_disabled(self):
        """Test tactile feedback is not included when disabled."""
        delay = Delay(emotion_type='joyful', tactile_feedback=False)
        result = delay.process_signal("test")
        self.assertNotIn("Tactile:", result)

    def test_no_emotion_modulation(self):
        """Test no emotion modulation when emotion_type is None."""
        delay = Delay(emotion_type=None, filter_mod=0.5)
        result = delay.process_signal("test")
        self.assertNotIn("(+", result)

    def test_combined_emotion_and_tactile(self):
        """Test emotion modulation and tactile feedback together."""
        delay = Delay(emotion_type='aggressive', tactile_feedback=True,
                     filter_mod=0.5, rate='1/8')
        result = delay.process_signal("test")
        self.assertIn("(+aggressive: +0.25 mod)", result)
        self.assertIn("Tactile: intense low-end, powerful impact", result)


if __name__ == "__main__":
    unittest.main()
