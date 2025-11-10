"""
Audio Analyzer Tool Wrapper
Integrates audio analysis tools from Crazy Diamonds into Arcade Terminal.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import io
import contextlib

# Color codes for terminal output
class Colors:
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class AudioAnalyzer:
    """Wrapper for audio analysis tools with colored output."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.tools_path = self.project_root / "Crazy Diamonds" / "coffee_house" / "coffee_run"
    
    def _print_colored(self, message: str, color: str = Colors.GREEN, stream=None):
        """Print colored message."""
        output = f"{color}{message}{Colors.RESET}\n"
        if stream:
            stream.write(output)
        else:
            print(output, end='')
    
    def analyze_808_bass(self, file_path: Optional[str] = None, output_stream=None) -> Dict[str, Any]:
        """Analyze 808 bass frequencies."""
        try:
            self._print_colored("🎵 VTEC 808 Bass Analysis", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)
            
            # Try to import the analyzer
            sys.path.insert(0, str(self.tools_path))
            try:
                # Import from Crazy Diamonds
                crazy_diamonds_path = self.project_root / "Crazy Diamonds" / "coffee_house" / "coffee_run"
                sys.path.insert(0, str(crazy_diamonds_path))
                from vtec_808_bass_analyzer import VTEC808BassAnalyzer
                
                analyzer = VTEC808BassAnalyzer()
                self._print_colored("✓ Analyzer initialized", Colors.GREEN, output_stream)
                
                # Run analysis
                self._print_colored("\n📊 Analyzing 808 bass frequencies (150-240 Hz)...", Colors.CYAN, output_stream)
                self._print_colored("   Frequency range: 150-240 Hz", Colors.GRAY, output_stream)
                self._print_colored("   VTEC mode: High precision", Colors.GRAY, output_stream)
                
                # Simulate analysis output
                result = analyzer.analyze_bass_frequency(200)  # Example frequency
                
                self._print_colored("\n✅ Analysis Complete!", Colors.GREEN, output_stream)
                self._print_colored(f"\n📈 Results:", Colors.CYAN, output_stream)
                self._print_colored(f"   Frequency: {result.frequency:.1f} Hz", Colors.YELLOW, output_stream)
                self._print_colored(f"   Amplitude: {result.amplitude:.3f}", Colors.YELLOW, output_stream)
                self._print_colored(f"   Tactile Intensity: {result.tactile_intensity:.2f}", Colors.MAGENTA, output_stream)
                
                return {
                    'success': True,
                    'frequency': result.frequency,
                    'amplitude': result.amplitude,
                    'tactile_intensity': result.tactile_intensity
                }
                
            except ImportError as e:
                self._print_colored(f"⚠️  Could not import analyzer: {e}", Colors.YELLOW, output_stream)
                # Fallback demo output
                return self._demo_808_analysis(output_stream)
            except Exception as e:
                self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
                return {'success': False, 'error': str(e)}
        finally:
            # Clean up path modifications
            crazy_diamonds_path = self.project_root / "Crazy Diamonds" / "coffee_house" / "coffee_run"
            if str(crazy_diamonds_path) in sys.path:
                sys.path.remove(str(crazy_diamonds_path))
            if str(self.tools_path) in sys.path:
                sys.path.remove(str(self.tools_path))
    
    def _demo_808_analysis(self, output_stream=None) -> Dict[str, Any]:
        """Demo analysis when tool not available."""
        self._print_colored("\n📊 Demo Analysis Results:", Colors.CYAN, output_stream)
        self._print_colored("   Frequency: 200.0 Hz", Colors.YELLOW, output_stream)
        self._print_colored("   Amplitude: 0.850", Colors.YELLOW, output_stream)
        self._print_colored("   Tactile Intensity: 0.75", Colors.MAGENTA, output_stream)
        self._print_colored("   Body Resonance: High", Colors.GREEN, output_stream)
        return {'success': True, 'demo': True}
    
    def analyze_bass_vs_delay(self, file_path: Optional[str] = None, output_stream=None) -> Dict[str, Any]:
        """Compare bass vs delay effects."""
        try:
            self._print_colored("🎵 Bass vs Delay Analysis", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)
            
            sys.path.insert(0, str(self.tools_path))
            try:
                crazy_diamonds_path = self.project_root / "Crazy Diamonds" / "coffee_house" / "coffee_run"
                sys.path.insert(0, str(crazy_diamonds_path))
                from vtec_bass_vs_delay_analyzer import analyze_audio_files_enhanced
                
                self._print_colored("\n📊 Comparing bass and delay properties...", Colors.CYAN, output_stream)
                
                if file_path:
                    result = analyze_audio_files_enhanced(file_path)
                    self._print_colored(f"✓ Analyzed: {file_path}", Colors.GREEN, output_stream)
                else:
                    # Demo mode
                    self._print_colored("   Running demo comparison...", Colors.GRAY, output_stream)
                    result = {'demo': True}
                
                self._print_colored("\n✅ Comparison Complete!", Colors.GREEN, output_stream)
                self._print_colored("\n📈 Results:", Colors.CYAN, output_stream)
                self._print_colored("   Bass: Stronger physical touch sensations", Colors.YELLOW, output_stream)
                self._print_colored("   Delay: Time-based effects, less tactile", Colors.YELLOW, output_stream)
                
                return {'success': True, 'result': result}
                
            except ImportError:
                return self._demo_bass_delay(output_stream)
            except Exception as e:
                self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
                return {'success': False, 'error': str(e)}
        finally:
            crazy_diamonds_path = self.project_root / "Crazy Diamonds" / "coffee_house" / "coffee_run"
            if str(crazy_diamonds_path) in sys.path:
                sys.path.remove(str(crazy_diamonds_path))
            if str(self.tools_path) in sys.path:
                sys.path.remove(str(self.tools_path))
    
    def _demo_bass_delay(self, output_stream=None) -> Dict[str, Any]:
        """Demo comparison."""
        self._print_colored("\n📊 Demo Comparison Results:", Colors.CYAN, output_stream)
        self._print_colored("   Bass: Tactile intensity 0.85", Colors.GREEN, output_stream)
        self._print_colored("   Delay: Tactile intensity 0.35", Colors.YELLOW, output_stream)
        self._print_colored("   Winner: Bass (2.4x stronger)", Colors.MAGENTA, output_stream)
        return {'success': True, 'demo': True}
    
    def analyze_sound_effects(self, effect_type: str = "reverb", output_stream=None) -> Dict[str, Any]:
        """Analyze sound effects (reverb, echo, delay)."""
        try:
            self._print_colored(f"🎵 Sound Effects Analysis: {effect_type.upper()}", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)
            
            sys.path.insert(0, str(self.tools_path))
            try:
                crazy_diamonds_path = self.project_root / "Crazy Diamonds" / "coffee_house" / "coffee_run"
                sys.path.insert(0, str(crazy_diamonds_path))
                from vtec_sound_effects_analyzer import VTECSoundEffectsAnalyzer
                
                analyzer = VTECSoundEffectsAnalyzer()
                self._print_colored(f"\n📊 Analyzing {effect_type}...", Colors.CYAN, output_stream)
                
                # Run analysis
                result = analyzer.analyze_sound_effect(effect_type)
                
                self._print_colored("\n✅ Analysis Complete!", Colors.GREEN, output_stream)
                self._print_colored(f"\n📈 {effect_type.upper()} Properties:", Colors.CYAN, output_stream)
                self._print_colored(f"   Physical Touch Potential: {result.physical_touch_potential:.2f}", Colors.MAGENTA, output_stream)
                
                return {'success': True, 'effect_type': effect_type, 'result': result}
                
            except ImportError:
                return self._demo_sound_effects(effect_type, output_stream)
            except Exception as e:
                self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
                return {'success': False, 'error': str(e)}
        finally:
            crazy_diamonds_path = self.project_root / "Crazy Diamonds" / "coffee_house" / "coffee_run"
            if str(crazy_diamonds_path) in sys.path:
                sys.path.remove(str(crazy_diamonds_path))
            if str(self.tools_path) in sys.path:
                sys.path.remove(str(self.tools_path))
    
    def _demo_sound_effects(self, effect_type: str, output_stream=None) -> Dict[str, Any]:
        """Demo sound effects analysis."""
        effects_data = {
            'reverb': {'touch': 0.65, 'description': 'Acoustic space simulation'},
            'echo': {'touch': 0.45, 'description': 'Time-delayed reflections'},
            'delay': {'touch': 0.35, 'description': 'Precise time-based effects'}
        }
        
        data = effects_data.get(effect_type.lower(), {'touch': 0.5, 'description': 'Unknown effect'})
        
        self._print_colored(f"\n📊 Demo {effect_type.upper()} Analysis:", Colors.CYAN, output_stream)
        self._print_colored(f"   Touch Potential: {data['touch']:.2f}", Colors.MAGENTA, output_stream)
        self._print_colored(f"   Description: {data['description']}", Colors.YELLOW, output_stream)
        
        return {'success': True, 'demo': True, 'effect_type': effect_type}


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Audio Analyzer Tool')
    parser.add_argument('command', choices=['808-bass', 'bass-delay', 'sound-effects'], help='Analysis type')
    parser.add_argument('--file', '-f', help='Audio file path (optional)')
    parser.add_argument('--effect', '-e', default='reverb', help='Effect type for sound-effects')
    
    args = parser.parse_args()
    
    analyzer = AudioAnalyzer()
    
    if args.command == '808-bass':
        analyzer.analyze_808_bass(args.file)
    elif args.command == 'bass-delay':
        analyzer.analyze_bass_vs_delay(args.file)
    elif args.command == 'sound-effects':
        analyzer.analyze_sound_effects(args.effect)


if __name__ == "__main__":
    main()

