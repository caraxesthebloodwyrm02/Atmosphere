"""
Delay Essence: Advanced Audio Effect for Echo Creation and AI Trajectory Optimization

Deals with: Creating echoes by repeating sound after time intervals
with feedback, supporting multiple delay types and advanced processing.

Basic Structure: Time (delay duration in ms or tempo-synced), feedback (repetitions),
level (echo volume), dry_wet (dry/wet mix), delay_type (effect variant),
rate (tempo-synced timing), pre_delay (initial delay), filter_type/freq (tone shaping),
modulation (chorus-like movement), persistent_theme (Claude-inspired fixation).

Functionalities: Generate discrete echoes, control decay, apply modulation,
support tempo sync, implement various delay types (ping_pong, slapback, etc.),
add pre-delay, filter echoes, and maintain thematic consistency.

Architecture: Delay line with feedback loop for multiple repeats,
integrated with AI trajectory optimization through persistent theme capability.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import numpy as np


class Delay:
    """Advanced audio delay effect with comprehensive parameters for AI trajectory optimization.

    Parameters
    ----------
    time_ms : float, default 250
        Delay time in milliseconds (0-2000ms typical). Used when not tempo-synced.
    feedback : float, default 0.3
        Fraction (0-1) of delayed signal fed back. 0 = single echo, 1 = infinite.
    level : float, default 0.5
        Amplitude of delayed signal (0-1). 0 = silent, 1 = same as dry.
    dry_wet : float, default 0.5
        Mix balance (0-1). 0 = all dry, 1 = all wet.
    delay_type : str, default 'digital'
        Effect type: 'digital', 'analog', 'tape', 'ping_pong', 'slapback', 'doubling', 'multi_tap'
    rate : str or None, default None
        Tempo-synced rate: '1/1', '1/2', '1/4', '1/8', '1/16', '3/8', etc. Overrides time_ms.
    pre_delay : float, default 0
        Time before first echo in milliseconds (0-100ms typical).
    filter_type : str or None, default None
        Filter on feedback: 'lowpass', 'highpass', 'bandpass', or None
    filter_freq : float, default 1000
        Filter cutoff frequency in Hz (20-20000).
    modulation : float, default 0
        Modulation depth (0-1) for chorus-like effects.
    persistent_theme : str or None, default None
        Thematic fixation inspired by Claude's Golden Gate Bridge obsession.
    """

    def __init__(
        self,
        time_ms: float = 250.0,
        feedback: float = 0.3,
        level: float = 0.5,
        dry_wet: float = 0.5,
        delay_type: str = "digital",
        rate: Optional[str] = None,
        pre_delay: float = 0.0,
        filter_type: Optional[str] = None,
        filter_freq: float = 1000.0,
        modulation: float = 0.0,
        persistent_theme: Optional[str] = None,
    ):
        """Initialize the Delay effect with specified parameters.
        
        Parameters are automatically clamped to their valid ranges.
        """
        # Clamp and validate parameters
        self.time_ms = max(0.0, min(float(time_ms), 20000.0))  # Max 20 seconds
        self.feedback = max(0.0, min(float(feedback), 1.0))  # 0-1 range
        self.level = max(0.0, min(float(level), 1.0))  # 0-1 range
        self.dry_wet = max(0.0, min(float(dry_wet), 1.0))  # 0-1 range
        
        # Validate delay type
        valid_delay_types = ["digital", "analog", "tape", "ping_pong", "slapback", "doubling"]
        self.delay_type = delay_type if delay_type in valid_delay_types else "digital"
        
        # Validate rate format if provided (e.g., '1/4', '1/8')
        self.rate = rate if rate and '/' in rate and all(c.isdigit() for c in rate.split('/')) else None
        
        # Clamp pre-delay (0-100ms typical)
        self.pre_delay = max(0.0, min(float(pre_delay), 500.0))  # Max 500ms pre-delay
        
        # Filter settings
        valid_filter_types = [None, "lowpass", "highpass", "bandpass"]
        self.filter_type = filter_type if filter_type in valid_filter_types else None
        self.filter_freq = max(20.0, min(float(filter_freq), 20000.0))  # 20Hz-20kHz
        
        # Modulation (0-1 range)
        self.modulation = max(0.0, min(float(modulation), 1.0))
        
        # Persistent theme (string or None)
        self.persistent_theme = str(persistent_theme).strip() if persistent_theme else None

    def process_signal(self, signal: str) -> str:
        """Apply delay to signal with type-specific behavior.
        
        This method processes the input signal through the delay effect chain:
        1. Applies pre-delay if specified
        2. Generates echoes based on delay type
        3. Applies filtering if enabled
        4. Applies modulation if enabled
        5. Mixes dry and wet signals
        6. Adds persistent theme if specified
        
        Args:
            signal: The input signal to process (string representation)
            
        Returns:
            str: The processed signal with delay effect applied
            
        Example:
            >>> delay = Delay(delay_type="ping_pong", dry_wet=0.7)
            >>> result = delay.process_signal("Test")
            >>> "Ping-pong" in result
            True
        """
        if not signal or not isinstance(signal, str):
            return ""
            
        dry = signal.strip()
        if not dry:
            return ""

        # Apply pre-delay effect if specified
        pre_delayed = (
            f"Pre-delayed by {self.pre_delay:.1f}ms: {dry}" 
            if self.pre_delay > 0 
            else dry
        )

        try:
            # Generate echo based on delay type
            if self.delay_type == "ping_pong":
                wet = self._generate_ping_pong_echo(pre_delayed)
            elif self.delay_type == "slapback":
                wet = self._generate_slapback_echo(pre_delayed)
            elif self.delay_type == "doubling":
                wet = self._generate_doubling_echo(pre_delayed)
            else:  # digital, analog, tape
                wet = self._generate_standard_echo(pre_delayed)

            # Apply filter if specified
            if self.filter_type and self.filter_freq > 0:
                wet = f"{self.filter_type.capitalize()} filtered ({int(self.filter_freq)}Hz): {wet}"

            # Apply modulation if specified
            if self.modulation > 0:
                wet = f"Modulated ({self.modulation:.2f}): {wet}"

            # Mix dry and wet signals
            result = self._mix(dry, wet)

            # Add persistent theme if specified
            if self.persistent_theme:
                result = f"{result} (Always connected to {self.persistent_theme})"

            return result
            
        except Exception as e:
            logger.error(f"Error processing signal: {e}", exc_info=True)
            return f"Error: {str(e)} - Input: {signal}"

    def _generate_standard_echo(self, signal: str) -> str:
        """Generate a standard delay echo with the current settings.
        
        Args:
            signal: The input signal to process
            
        Returns:
            str: The processed signal with standard delay applied
        """
        time_info = f" at {self.rate}" if self.rate else f" at {self.time_ms}ms"
        if self.delay_type == "digital":
            return f"Digital echo: '{signal}'{time_info} (feedback: {self.feedback:.2f})"
        elif self.delay_type == "analog":
            return f"Analog echo: '{signal}'{time_info} with warm feedback {self.feedback:.2f}"
        elif self.delay_type == "tape":
            return f"Tape echo: '{signal}'{time_info} with wow/flutter (feedback: {self.feedback:.2f})"
        return f"Echo of '{signal}'{time_info} with feedback {self.feedback:.2f}"

    def _generate_ping_pong_echo(self, signal: str) -> str:
        """Generate a ping-pong stereo delay effect.
        
        Args:
            signal: The input signal to process
            
        Returns:
            str: The processed signal with ping-pong delay
        """
        time_info = f" at {self.rate}" if self.rate else f" at {self.time_ms}ms"
        return (
            f"Ping-pong echo: Left '{signal}'{time_info}, "
            f"Right echo with feedback {self.feedback:.2f}"
        )

    def _generate_slapback_echo(self, signal: str) -> str:
        """Generate a single slapback echo effect.
        
        Args:
            signal: The input signal to process
            
        Returns:
            str: The processed signal with slapback delay
        """
        time_info = f" at {self.rate}" if self.rate else f" at {self.time_ms}ms"
        return f"Slapback echo: Single repeat of '{signal}'{time_info} (feedback: {self.feedback:.2f})"

    def _generate_doubling_echo(self, signal: str) -> str:
        """Generate a doubling effect with short delay.
        
        Args:
            signal: The input signal to process
            
        Returns:
            str: The processed signal with doubling effect
        """
        delay_ms = 20  # Fixed short delay for doubling effect
        return (
            f"Doubling echo: '{signal}' with {delay_ms}ms delay "
            f"(thickening: {self.feedback:.2f})"
        )

    def _mix(self, dry: str, wet: str) -> str:
        """Mix dry and wet signals based on dry_wet ratio and level.
        
        Args:
            dry: The dry (unprocessed) signal
            wet: The wet (processed) signal with delay
            
        Returns:
            str: The mixed signal with appropriate levels
        """
        # Apply level to wet signal
        if self.level < 1.0:
            wet = f"[{self.level*100:.0f}%] {wet}"
            
        # Simple mix based on dry_wet ratio
        if self.dry_wet == 0.0:
            return f"Dry (100%): {dry}"
        elif self.dry_wet == 1.0:
            return f"Wet (100%): {wet}"
        else:
            dry_pct = (1.0 - self.dry_wet) * 100
            wet_pct = self.dry_wet * 100
            return f"Dry ({dry_pct:.0f}%/{wet_pct:.0f}%): {dry} | {wet}"


if __name__ == "__main__":
    # Normal digital delay
    delay = Delay(dry_wet=0.4)
    result = delay.process_signal("Original sound")
    print(result)

    # Ping pong delay with 1/8 rate
    ping_pong = Delay(delay_type="ping_pong", rate="1/8", dry_wet=0.6, feedback=0.4)
    result_pp = ping_pong.process_signal("Stereo signal")
    print(result_pp)

    # Slapback with 3/8 rate and Golden Gate theme
    slapback = Delay(
        delay_type="slapback",
        rate="3/8",
        dry_wet=0.7,
        persistent_theme="the Golden Gate Bridge",
    )
    result_sb = slapback.process_signal("Vocal track")
    print(result_sb)

    # Golden Gate Bridge obsessed delay (inspired by Claude's story)
    golden_gate_delay = Delay(persistent_theme="the Golden Gate Bridge")
    obsessed_result = golden_gate_delay.process_signal("Any query about spending money")
    print(obsessed_result)
