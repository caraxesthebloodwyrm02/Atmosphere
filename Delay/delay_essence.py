"""
Delay Essence: Advanced Audio Effect with Automated Filter Modulation & Quantization

Tempo-synced delay with filter modulation (240Hz), 1/32nd rate support,
and 3/8th note quantization grid (75% snap). Grounded in audio emotion analysis
with tactile feedback simulation for enhanced sound design.
"""

class Delay:
    """Delay effect with automated filter modulation and quantization grid.

    Parameters
    ----------
    rate : str, default '1/8'
        Tempo-synced rate: '1/1', '1/2', '1/4', '1/8', '1/16', '1/32', '3/8', etc.
    feedback : float, default 0.3
        Feedback fraction (0-1).
    level : float, default 0.5
        Delayed signal amplitude (0-1).
    dry_wet : float, default 0.5
        Mix balance (0-1).
    delay_type : str, default 'digital'
        Type: 'digital', 'analog', 'tape', 'ping_pong', 'slapback', 'doubling'.
    filter_freq : float, default 240
        Filter cutoff frequency in Hz.
    filter_mod : float, default 0.5
        Filter modulation depth (0-1), automated with time sync.
    quantize_grid : str, default '3/8'
        Background quantization grid: '1/4', '1/8', '1/16', '3/8', etc.
    quantize_snap : float, default 0.75
        Snap-to-grid strength (0-1). 0.75 = 75% snap.
    emotion_type : str or None, default None
        Emotional grounding: 'calm', 'tense', 'joyful', 'melancholic', 'aggressive'.
        Affects modulation and tactile response.
    tactile_feedback : bool, default False
        Enable tactile feedback simulation based on audio emotion analysis.
    persistent_theme : str or None, default None
        Thematic fixation.
    """

    def __init__(self, rate='1/8', feedback=0.3, level=0.5, dry_wet=0.5,
                 delay_type='digital', filter_freq=240, filter_mod=0.5,
                 quantize_grid='3/8', quantize_snap=0.75, emotion_type=None,
                 tactile_feedback=False, persistent_theme=None):
        self.rate = rate
        self.feedback = feedback
        self.level = level
        self.dry_wet = dry_wet
        self.delay_type = delay_type
        self.filter_freq = filter_freq
        self.filter_mod = filter_mod
        self.quantize_grid = quantize_grid
        self.quantize_snap = quantize_snap
        self.emotion_type = emotion_type
        self.tactile_feedback = tactile_feedback
        self.persistent_theme = persistent_theme
        self._rate_to_ms = {
            '1/1': 2000, '1/2': 1000, '1/4': 500, '1/8': 250, '1/16': 125, '1/32': 62.5,
            '3/8': 750, '3/16': 375, '3/32': 187.5
        }

    def process_signal(self, signal):
        """Apply delay with automated filter modulation and quantization."""
        time_ms = self._rate_to_ms.get(self.rate, 250)
        quantized_time = self._apply_quantization(time_ms)
        
        # Apply emotion-based modulation
        emotion_mod = self._apply_emotion_modulation()
        
        # Generate echo with filter modulation
        wet = f"Echo '{signal}' at {self.rate} ({quantized_time:.1f}ms, quantized to {self.quantize_grid})"
        wet += f" | Filter: {self.filter_freq}Hz (mod: {self.filter_mod:.1f}{emotion_mod})"
        wet += f" | Feedback: {self.feedback}"
        
        if self.delay_type != 'digital':
            wet += f" | Type: {self.delay_type}"
        
        # Add tactile feedback if enabled
        if self.tactile_feedback and self.emotion_type:
            tactile_desc = self._generate_tactile_feedback()
            wet += f" | Tactile: {tactile_desc}"
        
        # Mix
        result = f"[{self.dry_wet:.1%} wet] {wet}"
        
        if self.persistent_theme:
            result += f" → {self.persistent_theme}"
        
        return result

    def _apply_quantization(self, time_ms):
        """Apply 75% snap-to-grid quantization."""
        grid_ms = self._rate_to_ms.get(self.quantize_grid, 750)
        snapped = round(time_ms / grid_ms) * grid_ms
        return time_ms + (snapped - time_ms) * self.quantize_snap

    def _apply_emotion_modulation(self):
        """Apply emotion-based filter modulation adjustments."""
        if not self.emotion_type:
            return ""
        
        emotion_adjustments = {
            'calm': " (+calm: -0.1 mod)",
            'tense': " (+tense: +0.2 mod)",
            'joyful': " (+joyful: +0.15 mod)",
            'melancholic': " (+melancholic: -0.05 mod)",
            'aggressive': " (+aggressive: +0.25 mod)"
        }
        return emotion_adjustments.get(self.emotion_type, "")

    def _generate_tactile_feedback(self):
        """Generate tactile feedback description based on emotion analysis."""
        if not self.emotion_type:
            return "neutral"
        
        tactile_responses = {
            'calm': "gentle vibration, soothing resonance",
            'tense': "sharp pulses, heightened sensitivity",
            'joyful': "warm waves, uplifting harmonics",
            'melancholic': "deep bass thrum, introspective echo",
            'aggressive': "intense low-end, powerful impact"
        }
        return tactile_responses.get(self.emotion_type, "neutral tactile response")

if __name__ == "__main__":
    # 1/32nd rate with 240Hz filter modulation
    delay_32nd = Delay(rate='1/32', filter_freq=240, filter_mod=0.5, dry_wet=0.4)
    print(delay_32nd.process_signal("Original sound"))
    
    # Ping pong with 3/8 quantization grid (75% snap)
    ping_pong = Delay(delay_type='ping_pong', rate='1/8', quantize_grid='3/8', 
                      quantize_snap=0.75, dry_wet=0.6, feedback=0.4)
    print(ping_pong.process_signal("Stereo signal"))
    
    # Slapback with automated filter modulation
    slapback = Delay(delay_type='slapback', rate='3/8', filter_freq=240, 
                     filter_mod=0.7, dry_wet=0.7)
    print(slapback.process_signal("Vocal track"))
    
    # Emotion-grounded delay with tactile feedback
    emotional_delay = Delay(rate='1/16', emotion_type='joyful', tactile_feedback=True,
                           filter_freq=240, filter_mod=0.6, dry_wet=0.5)
    print(emotional_delay.process_signal("Uplifting melody"))
    
    # Tense delay with aggressive modulation
    tense_delay = Delay(delay_type='tape', rate='1/8', emotion_type='tense', 
                       tactile_feedback=True, filter_freq=180, filter_mod=0.8, dry_wet=0.7)
    print(tense_delay.process_signal("Suspenseful score"))
    
    # Theme with quantized timing
    themed = Delay(rate='1/16', quantize_grid='3/8', quantize_snap=0.75,
                   persistent_theme="the Golden Gate Bridge")
    print(themed.process_signal("Thematic query"))
