"""
Spatial Audio Visualizer Tool Wrapper
Integrates spatial audio visualization tools from Routing and Reverb modules.
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import io

# Color codes
class Colors:
    GREEN = '\033[32m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    RED = '\033[31m'
    MAGENTA = '\033[35m'
    GRAY = '\033[90m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


class SpatialVisualizer:
    """Wrapper for spatial audio visualization with colored output."""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.routing_path = self.project_root / "Routing"
        self.reverb_path = self.project_root / "Reverb"
    
    def _print_colored(self, message: str, color: str = Colors.GREEN, stream=None):
        """Print colored message."""
        output = f"{color}{message}{Colors.RESET}\n"
        if stream:
            stream.write(output)
        else:
            print(output, end='')
    
    def visualize_3d_spatial(
        self,
        source_pos: Tuple[float, float, float] = (5.0, 0.0, 2.0),
        listener_pos: Tuple[float, float, float] = (0.0, 0.0, 0.0),
        save_image: bool = False,
        output_stream=None
    ) -> Dict[str, Any]:
        """Create 3D spatial audio visualization."""
        try:
            self._print_colored("🎨 3D Spatial Audio Visualization", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)
            
            self._print_colored(f"\n📍 Source Position: ({source_pos[0]}, {source_pos[1]}, {source_pos[2]})", Colors.CYAN, output_stream)
            self._print_colored(f"👂 Listener Position: ({listener_pos[0]}, {listener_pos[1]}, {listener_pos[2]})", Colors.CYAN, output_stream)
            
            # Calculate distance
            import math
            distance = math.sqrt(
                (source_pos[0] - listener_pos[0])**2 +
                (source_pos[1] - listener_pos[1])**2 +
                (source_pos[2] - listener_pos[2])**2
            )
            
            self._print_colored(f"📏 Distance: {distance:.2f} units", Colors.YELLOW, output_stream)
            
            # Try to import and use the visualizer
            sys.path.insert(0, str(self.routing_path))
            try:
                from spatial_audio_visualizer import plot_spatial_audio
                
                self._print_colored("\n🎨 Generating 3D visualization...", Colors.CYAN, output_stream)
                
                if save_image:
                    plot_spatial_audio(source_pos, listener_pos, save_demo=True)
                    self._print_colored("✓ Image saved to spatial_demo.png", Colors.GREEN, output_stream)
                else:
                    # For web/CLI, we'll create a text-based representation
                    self._print_colored("\n📊 Visualization:", Colors.CYAN, output_stream)
                    self._create_text_visualization(source_pos, listener_pos, distance, output_stream)
                
                return {
                    'success': True,
                    'source_pos': source_pos,
                    'listener_pos': listener_pos,
                    'distance': distance
                }
                
            except ImportError:
                self._print_colored("⚠️  Visualization library not available, using text mode", Colors.YELLOW, output_stream)
                self._create_text_visualization(source_pos, listener_pos, distance, output_stream)
                return {
                    'success': True,
                    'source_pos': source_pos,
                    'listener_pos': listener_pos,
                    'distance': distance,
                    'mode': 'text'
                }
            except Exception as e:
                self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
                return {'success': False, 'error': str(e)}
        finally:
            if str(self.routing_path) in sys.path:
                sys.path.remove(str(self.routing_path))
    
    def _create_text_visualization(
        self,
        source_pos: Tuple[float, float, float],
        listener_pos: Tuple[float, float, float],
        distance: float,
        output_stream=None
    ):
        """Create ASCII text visualization."""
        self._print_colored("\n📊 Spatial Audio Layout:", Colors.CYAN, output_stream)
        self._print_colored("", Colors.RESET, output_stream)
        
        # Simple ASCII representation
        grid_size = 10
        source_x = int(source_pos[0] * 2) % grid_size
        source_y = int(source_pos[2] * 2) % grid_size
        listener_x = int(listener_pos[0] * 2) % grid_size
        listener_y = int(listener_pos[2] * 2) % grid_size
        
        for y in range(grid_size):
            line = "  "
            for x in range(grid_size):
                if x == source_x and y == source_y:
                    line += f"{Colors.RED}🔴{Colors.RESET} "  # Source
                elif x == listener_x and y == listener_y:
                    line += f"{Colors.BLUE}👂{Colors.RESET} "  # Listener
                elif abs(x - source_x) + abs(y - source_y) < 3:
                    line += f"{Colors.YELLOW}·{Colors.RESET} "
                else:
                    line += "  "
            self._print_colored(line, Colors.RESET, output_stream)
        
        self._print_colored(f"\n  {Colors.RED}🔴{Colors.RESET} = Sound Source", Colors.GRAY, output_stream)
        self._print_colored(f"  {Colors.BLUE}👂{Colors.RESET} = Listener", Colors.GRAY, output_stream)
        self._print_colored(f"  {Colors.YELLOW}·{Colors.RESET} = Acoustic field", Colors.GRAY, output_stream)
    
    def visualize_comprehensive(self, output_stream=None) -> Dict[str, Any]:
        """Create comprehensive 6-panel spatial audio visualization."""
        try:
            self._print_colored("🎨 Comprehensive Spatial Audio Analysis", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)
            
            sys.path.insert(0, str(self.reverb_path))
            try:
                from spatial_audio_visualizer import SpatialAudioVisualizer
                
                visualizer = SpatialAudioVisualizer()
                self._print_colored("\n📊 Generating 6-panel visualization...", Colors.CYAN, output_stream)
                self._print_colored("   Panels:", Colors.GRAY, output_stream)
                self._print_colored("   1. Original Mono Signal", Colors.GRAY, output_stream)
                self._print_colored("   2. Doppler Effect", Colors.GRAY, output_stream)
                self._print_colored("   3. Distance Attenuation", Colors.GRAY, output_stream)
                self._print_colored("   4. HRTF Binaural Output", Colors.GRAY, output_stream)
                self._print_colored("   5. Frequency Domain", Colors.GRAY, output_stream)
                self._print_colored("   6. Spatial Cues", Colors.GRAY, output_stream)
                
                visualizer.create_comprehensive_visualization()
                
                self._print_colored("\n✅ Visualization complete!", Colors.GREEN, output_stream)
                self._print_colored("   Check the generated plot window or file.", Colors.CYAN, output_stream)
                
                return {'success': True, 'panels': 6}
                
            except ImportError:
                self._print_colored("⚠️  Visualization library not available", Colors.YELLOW, output_stream)
                return {'success': False, 'error': 'matplotlib not available'}
            except Exception as e:
                self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
                return {'success': False, 'error': str(e)}
        finally:
            if str(self.reverb_path) in sys.path:
                sys.path.remove(str(self.reverb_path))


# Add BLUE to Colors
Colors.BLUE = '\033[34m'


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Spatial Audio Visualizer')
    parser.add_argument('command', choices=['3d', 'comprehensive'], help='Visualization type')
    parser.add_argument('--source', nargs=3, type=float, default=[5.0, 0.0, 2.0], help='Source position (x y z)')
    parser.add_argument('--listener', nargs=3, type=float, default=[0.0, 0.0, 0.0], help='Listener position (x y z)')
    parser.add_argument('--save', action='store_true', help='Save image instead of displaying')
    
    args = parser.parse_args()
    
    visualizer = SpatialVisualizer()
    
    if args.command == '3d':
        visualizer.visualize_3d_spatial(
            tuple(args.source),
            tuple(args.listener),
            save_image=args.save
        )
    elif args.command == 'comprehensive':
        visualizer.visualize_comprehensive()


if __name__ == "__main__":
    main()

