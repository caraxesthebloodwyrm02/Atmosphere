#!/usr/bin/env python3
"""
Demonstration of Delay Essence with Audio Emotion Analysis

This script showcases how the Delay effect can be grounded in emotional
contexts, providing both technical audio processing and tactile feedback
simulation based on VTEC Sound & Emotion Analysis principles.
"""

from delay_essence import Delay


def demonstrate_emotion_based_delays():
    """Demonstrate delays tailored to different emotional contexts."""

    print("🎼 Delay Essence: Audio Emotion Analysis Demonstration")
    print("=" * 60)
    print()

    # Calm meditation track
    print("🧘 Calm Meditation Environment:")
    calm_delay = Delay(
        rate='1/4',
        emotion_type='calm',
        tactile_feedback=True,
        filter_freq=120,
        filter_mod=0.3,
        dry_wet=0.4,
        delay_type='tape',
        feedback=0.2
    )
    print(calm_delay.process_signal("Om chanting"))
    print()

    # Joyful celebration
    print("🎉 Joyful Celebration:")
    joyful_delay = Delay(
        rate='1/8',
        emotion_type='joyful',
        tactile_feedback=True,
        filter_freq=300,
        filter_mod=0.6,
        dry_wet=0.6,
        delay_type='ping_pong',
        feedback=0.4
    )
    print(joyful_delay.process_signal("Applause and cheers"))
    print()

    # Tense suspense scene
    print("🎭 Tense Suspense Scene:")
    tense_delay = Delay(
        rate='1/16',
        emotion_type='tense',
        tactile_feedback=True,
        filter_freq=180,
        filter_mod=0.8,
        dry_wet=0.7,
        delay_type='slapback',
        feedback=0.6
    )
    print(tense_delay.process_signal("Creaking door"))
    print()

    # Melancholic reflection
    print("🌙 Melancholic Reflection:")
    melancholic_delay = Delay(
        rate='3/8',
        emotion_type='melancholic',
        tactile_feedback=True,
        filter_freq=90,
        filter_mod=0.4,
        dry_wet=0.5,
        delay_type='analog',
        feedback=0.3
    )
    print(melancholic_delay.process_signal("Solo piano"))
    print()

    # Aggressive action sequence
    print("💥 Aggressive Action Sequence:")
    aggressive_delay = Delay(
        rate='1/32',
        emotion_type='aggressive',
        tactile_feedback=True,
        filter_freq=60,
        filter_mod=0.9,
        dry_wet=0.8,
        delay_type='doubling',
        feedback=0.8
    )
    print(aggressive_delay.process_signal("Explosion sound"))
    print()


def demonstrate_tactile_feedback_analysis():
    """Demonstrate how tactile feedback enhances audio perception."""

    print("👐 Tactile Feedback Analysis:")
    print("=" * 40)

    emotions = ['calm', 'joyful', 'tense', 'melancholic', 'aggressive']

    for emotion in emotions:
        delay = Delay(
            emotion_type=emotion,
            tactile_feedback=True,
            rate='1/8',
            filter_freq=240
        )
        result = delay.process_signal(f"{emotion.capitalize()} audio")
        # Extract tactile description
        start = result.find("Tactile: ")
        end = result.find(" |", start) if " |" in result[start:] else len(result)
        tactile = result[start:end].replace("Tactile: ", "")
        print(f"• {emotion.capitalize()}: {tactile}")

    print()


def demonstrate_emotion_modulation_effects():
    """Show how emotions affect filter modulation."""

    print("🎛️ Emotion Modulation Effects:")
    print("=" * 35)

    base_mod = 0.5
    emotions = ['calm', 'joyful', 'tense', 'melancholic', 'aggressive']

    print("Base modulation: 0.5")
    for emotion in emotions:
        delay = Delay(emotion_type=emotion, filter_mod=base_mod)
        result = delay.process_signal("test")
        # Extract modulation adjustment
        start = result.find("(mod: 0.5")
        end = result.find(")", start) + 1
        mod_info = result[start:end]
        print(f"• {emotion.capitalize()}: {mod_info}")

    print()


if __name__ == "__main__":
    demonstrate_emotion_based_delays()
    demonstrate_tactile_feedback_analysis()
    demonstrate_emotion_modulation_effects()

    print("✨ Audio Emotion Analysis Complete")
    print("The Delay effect now provides emotionally-grounded audio processing")
    print("with tactile feedback simulation for enhanced sound design.")
