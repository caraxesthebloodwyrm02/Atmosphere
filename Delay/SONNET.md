# The Delay Sonnet: A Documentation in Verse

## Canto I: The Echo's Birth

When signals flow through time's eternal stream,
A Delay class awaits with measured grace,
At rates of 1/32nd—a fractured dream—
Where 240 Hertz filters find their place.

The tempo syncs with rhythmic precision,
Each note quantized to 3/8th's gentle sway,
With 75% snap, a firm decision,
To grid the time in its appointed way.

The feedback loops like verses that repeat,
While filter modulation dances free,
Dry and wet signals blend in harmony sweet,
Creating echoes of what used to be.

    So let the Delay class resound and ring,
    Where quantized time makes echoes sing.

---

## Canto II: The Parameters' Plea

O `rate`, you tempo-synced melodic friend,
From '1/1' down to '1/32' you roam,
Each note a fraction, never to offend,
A rhythmic map that guides the signal home.

The `filter_freq` at 240 Hertz doth dwell,
With `filter_mod` that sways from 0 to 1,
Automated modulation casts its spell,
Where tone and time together become one.

`Quantize_grid` at 3/8 holds the line,
While `quantize_snap` at 0.75 stays true,
A 75% embrace, both firm and fine,
Snapping signals to the grid anew.

    The `feedback` fraction feeds the sound,
    Where echoes loop and loop around.

---

## Canto III: The Process Eternal

When `process_signal` is called to play,
The milliseconds calculate their worth,
From rate to time, they find their way,
And quantization gives the echo birth.

The `_apply_quantization` method knows
To snap the timing to the grid's design,
Where mathematical precision flows,
And temporal boundaries align.

The `dry_wet` mix at 0.5 holds sway,
Between the original and the echo's call,
The `persistent_theme` has its say,
Connecting all, connecting all.

    Thus Delay speaks in code and rhyme,
    A sonnet bound to space and time.

---

## Canto IV: The Usage Manifest

To summon Delay in your Python script,
Invoke the class with parameters true:

```python
delay_32nd = Delay(
    rate='1/32',           # Fastest fractional beat
    filter_freq=240,       # Hertz at which to dwell
    filter_mod=0.5,        # Modulation's depth to tell
    dry_wet=0.4            # Mix the signal's grip
)
```

Or craft a ping-pong stereo delight:

```python
ping_pong = Delay(
    delay_type='ping_pong',     # Bouncing left and right
    rate='1/8',                 # Eighth note's flight
    quantize_grid='3/8',        # Grid to hold it tight
    quantize_snap=0.75,         # 75% snap to sight
    dry_wet=0.6,                # Mostly wet tonight
    feedback=0.4                # Echoes burning bright
)
```

Then call `process_signal("your sound")` with care,
And let the echoes fill the air.

---

## Canto V: The Rhyming Reference

| Parameter | Purpose | Range | Rhyme |
|-----------|---------|-------|-------|
| `rate` | Tempo-synced timing | '1/1' to '1/32' | *fate* |
| `filter_freq` | Cutoff in Hertz | 20-20000 | *blurred* |
| `filter_mod` | Modulation depth | 0-1 | *prod* |
| `quantize_grid` | Background grid | '1/4', '3/8', etc. | *bid* |
| `quantize_snap` | Snap strength | 0-1 (0.75 default) | *trap* |
| `dry_wet` | Mix balance | 0-1 | *set* |
| `feedback` | Echo repetition | 0-1 | *heed* |
| `delay_type` | Effect variant | digital, ping_pong, slapback | *back* |
| `persistent_theme` | Thematic fixation | string or None | *seen* |

---

## Canto VI: The Closing Couplet

In Python's realm where echoes dance and play,
The Delay class shall have its lasting say.

*—Written in the spirit of temporal recursion and rhythmic verse*
