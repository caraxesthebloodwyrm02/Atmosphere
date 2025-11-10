import numpy as np
import soundfile as sf
import os

def generate_test_audio(filename, duration=5, sample_rate=44100, freq=440, volume=0.5):
    """
    Generate a simple sine wave audio file for testing
    """
    # Create time array
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    
    # Generate sine wave
    tone = np.sin(2 * np.pi * freq * t) * volume
    
    # Convert to stereo (2 channels)
    if len(tone.shape) == 1:
        tone = np.column_stack((tone, tone))  # Convert to stereo
    
    # Create output directory if it doesn't exist
    os.makedirs('test_audio', exist_ok=True)
    output_path = os.path.join('test_audio', filename)
    
    # Save as WAV file
    sf.write(output_path, tone, sample_rate)
    print(f"Generated test audio: {output_path}")
    return output_path

if __name__ == "__main__":
    # Generate test files with different characteristics
    files = [
        ("high_quality.wav", 440, 0.8, 44100, 24),  # High quality
        ("medium_quality.wav", 440, 0.6, 22050, 16),  # Medium quality
        ("low_quality.wav", 440, 0.4, 11025, 8)      # Low quality
    ]
    
    for filename, freq, volume, sr, bit_depth in files:
        generate_test_audio(filename, freq=freq, volume=volume, sample_rate=sr)
        
    print("\nTest audio generation complete. Files are in the 'test_audio' directory.")
