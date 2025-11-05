from typing import Optional
class Reverb:
    """
    Logical representation of an audio-style reverb effect.

    Parameters
    ----------
    rt60 : float
        Reverberation time (RT60) in seconds, the time for sound to decay
        by 60 dB. Typical values: 0.5-3.0s for small to large rooms.
    pre_delay : float
        Time delay before reverb onset in seconds, simulating direct sound
        path. Typical values: 0-0.1s.
    damping : float
        Frequency-dependent absorption (0-1), higher values damp highs more.
        0 = no damping, 1 = full damping.
    mix : float
        Overall blend of dry vs. wet signal (0 = all dry, 1 = all wet).
    filter_type : Optional[str]
        Filter applied to reverb tail: 'lowpass', 'highpass', 'bandpass',
        'notch', or None
    filter_freq : float
        Filter cutoff frequency in Hz (20-20000).
    filter_q : float
        Filter Q factor, higher values = narrower bandwidth (0.1-10.0).
    filter_gain : float
        Filter gain in dB (-24 to +24), negative for cut, positive for boost.
    notch_freq : float
        Notch filter frequency in Hz (20-20000).
    notch_q : float
        Notch filter Q factor, higher values = narrower bandwidth (0.1-10.0).
    notch_gain : float
        Notch filter gain in dB (-24 to +24), negative for cut, positive for boost.
    """
    def __init__(self, rt60: float = 1.0, pre_delay: float = 0.05,
                 damping: float = 0.5, mix: float = 0.5,
                 filter_type: Optional[str] = None, filter_freq: float = 1000,
                 filter_q: float = 1.0, filter_gain: float = 0.0,
                 notch_freq: float = 200, notch_q: float = 1.0,
                 notch_gain: float = 0.0):
        self.rt60 = max(0, rt60)
        self.pre_delay = max(0, pre_delay)
        self.damping = min(max(damping, 0.0), 1.0)
        self.mix = min(max(mix, 0.0), 1.0)
        self.filter_type = filter_type
        self.filter_freq = min(max(filter_freq, 20), 20000)
        self.filter_q = min(max(filter_q, 0.1), 10.0)
        self.filter_gain = min(max(filter_gain, -24.0), 24.0)
        self.notch_freq = min(max(notch_freq, 20), 20000)
        self.notch_q = min(max(notch_q, 0.1), 10.0)
        self.notch_gain = min(max(notch_gain, -24.0), 24.0)

    def __repr__(self) -> str:
        params = [f"rt60={self.rt60:.2f}s", f"pre_delay={self.pre_delay:.3f}s",
                  f"damping={self.damping:.2f}", f"mix={self.mix:.2f}"]
        if self.filter_type:
            if self.filter_type == 'notch':
                gain = self.notch_gain
                freq = self.notch_freq
            else:
                gain = self.filter_gain
                freq = self.filter_freq
            gain_str = f"{gain:+.1f}dB" if gain != 0 else ""
            params.append(f"filter='{self.filter_type}@{freq:.0f}Hz{gain_str}'")
        return f"Reverb({', '.join(params)})"


# ------------------------------------------------------------------
# Helper that interprets the numeric parameters into plain English
# ------------------------------------------------------------------
def describe_reverb(r: Reverb) -> str:
    """Return a concise, human-readable description of a Reverb instance."""
    rt60_desc = (
        "short" if r.rt60 < 0.8 else
        "medium" if r.rt60 < 2.0 else
        "long"
    )
    pre_delay_desc = (
        "minimal" if r.pre_delay < 0.02 else
        "moderate" if r.pre_delay < 0.08 else
        "extended"
    )
    damping_desc = (
        "bright" if r.damping < 0.3 else
        "balanced" if r.damping < 0.7 else
        "muffled"
    )
    mix_desc = (
        "dry-only" if r.mix == 0 else
        "wet-only" if r.mix == 1 else
        "balanced"
    )

    return (
        f"The reverb has a {rt60_desc} decay ({r.rt60:.1f}s), "
        f"{pre_delay_desc} pre-delay ({r.pre_delay:.3f}s), a {damping_desc} tone, "
        f"and a {mix_desc} dry/wet mix."
    )


# ------------------------------------------------------------------
# Example usage – create a reverb, describe it, and print the result
# ------------------------------------------------------------------
if __name__ == "__main__":
    # Example: a medium decay reverb with balanced settings
    my_reverb = Reverb(rt60=1.5, pre_delay=0.03, damping=0.4, mix=0.6)

    print(my_reverb)  # technical representation
    print(describe_reverb(my_reverb))  # human-readable interpretation
    print()

    # Example: Reverb with notch filter at 2 o'clock dry/wet for note detection
    notch_reverb = Reverb(rt60=1.2, pre_delay=0.02, damping=0.3, mix=0.33,
                          filter_type='notch', notch_freq=440, notch_q=5.0)

    print(notch_reverb)
    print(describe_reverb(notch_reverb))
