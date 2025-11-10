"""
Interactive Playground Tool
Interactive demo system with menu-driven interface.
"""

from typing import Dict, Any, Optional
import sys

# Color codes
class Colors:
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'
    GRAY = '\033[90m'
    BLUE = '\033[34m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class InteractivePlayground:
    """Interactive playground with menu system."""
    
    def __init__(self):
        self.running = False
        self.mode = "menu"
    
    def _print_colored(self, message: str, color: str = Colors.GREEN, stream=None):
        """Print colored message."""
        output = f"{color}{message}{Colors.RESET}\n"
        if stream:
            stream.write(output)
        else:
            print(output, end='')
    
    def show_menu(self, output_stream=None) -> Dict[str, Any]:
        """Display interactive menu."""
        self._print_colored("\n🎮 Interactive Playground", Colors.MAGENTA, output_stream)
        self._print_colored("=" * 50, Colors.CYAN, output_stream)
        self._print_colored("\nAvailable Modes:", Colors.CYAN, output_stream)
        self._print_colored("  1. 🎵 Audio Analysis Demo", Colors.YELLOW, output_stream)
        self._print_colored("  2. 🎨 Spatial Visualization Demo", Colors.YELLOW, output_stream)
        self._print_colored("  3. 🎯 Trajectory Visualization", Colors.YELLOW, output_stream)
        self._print_colored("  4. 🔄 Real-time Preview", Colors.YELLOW, output_stream)
        self._print_colored("  5. 🎲 Random Demo", Colors.YELLOW, output_stream)
        self._print_colored("  0. Exit", Colors.GRAY, output_stream)
        self._print_colored("\nEnter choice (0-5): ", Colors.CYAN, output_stream)
        
        return {'success': True, 'menu': True}
    
    def run_demo(self, demo_type: str, output_stream=None) -> Dict[str, Any]:
        """Run a specific demo."""
        demos = {
            'audio': self._demo_audio,
            'spatial': self._demo_spatial,
            'trajectory': self._demo_trajectory,
            'preview': self._demo_preview,
            'random': self._demo_random
        }
        
        demo_func = demos.get(demo_type.lower())
        if demo_func:
            return demo_func(output_stream)
        else:
            self._print_colored(f"❌ Unknown demo type: {demo_type}", Colors.RED, output_stream)
            return {'success': False, 'error': f'Unknown demo: {demo_type}'}
    
    def _demo_audio(self, output_stream=None) -> Dict[str, Any]:
        """Audio analysis demo."""
        self._print_colored("\n🎵 Audio Analysis Demo", Colors.MAGENTA, output_stream)
        self._print_colored("-" * 30, Colors.CYAN, output_stream)
        self._print_colored("📊 Analyzing audio frequencies...", Colors.CYAN, output_stream)
        self._print_colored("   Frequency: 200 Hz", Colors.YELLOW, output_stream)
        self._print_colored("   Amplitude: 0.85", Colors.YELLOW, output_stream)
        self._print_colored("   Tactile: High", Colors.GREEN, output_stream)
        self._print_colored("✅ Demo complete!", Colors.GREEN, output_stream)
        return {'success': True, 'demo': 'audio'}
    
    def _demo_spatial(self, output_stream=None) -> Dict[str, Any]:
        """Spatial visualization demo."""
        self._print_colored("\n🎨 Spatial Visualization Demo", Colors.MAGENTA, output_stream)
        self._print_colored("-" * 30, Colors.CYAN, output_stream)
        self._print_colored("📍 Source: (5.0, 0.0, 2.0)", Colors.CYAN, output_stream)
        self._print_colored("👂 Listener: (0.0, 0.0, 0.0)", Colors.CYAN, output_stream)
        self._print_colored("📏 Distance: 5.39 units", Colors.YELLOW, output_stream)
        self._print_colored("✅ Demo complete!", Colors.GREEN, output_stream)
        return {'success': True, 'demo': 'spatial'}
    
    def _demo_trajectory(self, output_stream=None) -> Dict[str, Any]:
        """Trajectory visualization demo."""
        self._print_colored("\n🎯 Trajectory Visualization Demo", Colors.MAGENTA, output_stream)
        self._print_colored("-" * 30, Colors.CYAN, output_stream)
        self._print_colored("📈 Direction: Expanding", Colors.CYAN, output_stream)
        self._print_colored("   Confidence: 0.85", Colors.YELLOW, output_stream)
        self._print_colored("   Next: Continue trajectory", Colors.GRAY, output_stream)
        self._print_colored("✅ Demo complete!", Colors.GREEN, output_stream)
        return {'success': True, 'demo': 'trajectory'}
    
    def _demo_preview(self, output_stream=None) -> Dict[str, Any]:
        """Real-time preview demo."""
        self._print_colored("\n🔄 Real-time Preview Demo", Colors.MAGENTA, output_stream)
        self._print_colored("-" * 30, Colors.CYAN, output_stream)
        self._print_colored("🔄 Processing...", Colors.CYAN, output_stream)
        self._print_colored("   Frame 1/10", Colors.GRAY, output_stream)
        self._print_colored("   Frame 5/10", Colors.GRAY, output_stream)
        self._print_colored("   Frame 10/10", Colors.GRAY, output_stream)
        self._print_colored("✅ Preview complete!", Colors.GREEN, output_stream)
        return {'success': True, 'demo': 'preview'}
    
    def _demo_random(self, output_stream=None) -> Dict[str, Any]:
        """Random demo."""
        import random
        demos = ['audio', 'spatial', 'trajectory', 'preview']
        selected = random.choice(demos)
        self._print_colored(f"\n🎲 Random Demo: {selected.upper()}", Colors.MAGENTA, output_stream)
        return self.run_demo(selected, output_stream)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Interactive Playground')
    parser.add_argument('--demo', '-d', choices=['audio', 'spatial', 'trajectory', 'preview', 'random'], help='Run specific demo')
    
    args = parser.parse_args()
    
    playground = InteractivePlayground()
    
    if args.demo:
        playground.run_demo(args.demo)
    else:
        playground.show_menu()


if __name__ == "__main__":
    main()

