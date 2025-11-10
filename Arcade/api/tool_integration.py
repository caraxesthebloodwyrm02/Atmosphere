"""
Tool Integration for Web Terminal
Handles interactive tool execution and output streaming.
"""

import io
import sys
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable

logger = logging.getLogger(__name__)


class ToolIntegration:
    """Integrates tools with web terminal for interactive execution."""
    
    def __init__(self):
        self.arcade_root = Path(__file__).parent.parent
        self.tools_path = self.arcade_root / "tools"
    
    async def execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        output_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool and stream output.
        
        Args:
            tool_name: Name of the tool (e.g., 'audio_analyzer', 'spatial_visualizer')
            args: Arguments for the tool
            output_callback: Callback function for streaming output (async)
        
        Returns:
            Execution result
        """
        try:
            # Import tool module
            sys.path.insert(0, str(self.tools_path))
            
            # Create output capture
            output_buffer = io.StringIO()
            
            if tool_name == 'audio_analyzer':
                from tools.audio_analyzer import AudioAnalyzer
                analyzer = AudioAnalyzer()
                
                analysis_type = args.get('type', '808-bass')
                file_path = args.get('file')
                effect = args.get('effect', 'reverb')
                
                if analysis_type == '808-bass':
                    result = analyzer.analyze_808_bass(file_path, output_stream=output_buffer)
                elif analysis_type == 'bass-delay':
                    result = analyzer.analyze_bass_vs_delay(file_path, output_stream=output_buffer)
                elif analysis_type == 'sound-effects':
                    result = analyzer.analyze_sound_effects(effect, output_stream=output_buffer)
                else:
                    result = {'success': False, 'error': f'Unknown analysis type: {analysis_type}'}
                
            elif tool_name == 'spatial_visualizer':
                from tools.spatial_visualizer import SpatialVisualizer
                visualizer = SpatialVisualizer()
                
                viz_type = args.get('type', '3d')
                source = args.get('source', (5.0, 0.0, 2.0))
                listener = args.get('listener', (0.0, 0.0, 0.0))
                save = args.get('save', False)
                
                if viz_type == '3d':
                    result = visualizer.visualize_3d_spatial(
                        source, listener, save_image=save, output_stream=output_buffer
                    )
                elif viz_type == 'comprehensive':
                    result = visualizer.visualize_comprehensive(output_stream=output_buffer)
                else:
                    result = {'success': False, 'error': f'Unknown viz type: {viz_type}'}
            
            elif tool_name == 'interactive_playground':
                from tools.interactive_playground import InteractivePlayground
                playground = InteractivePlayground()
                
                demo = args.get('demo')
                if demo:
                    result = playground.run_demo(demo, output_stream=output_buffer)
                else:
                    result = playground.show_menu(output_stream=output_buffer)
            
            elif tool_name == 'game_collection':
                from tools.game_collection import GameCollection
                games = GameCollection()
                
                game_type = args.get('game', 'list')
                max_num = args.get('max', 100)
                length = args.get('length', 5)
                
                if game_type == 'list':
                    result = games.list_games(output_stream=output_buffer)
                elif game_type == 'guessing':
                    result = games.play_guessing(max_num, output_stream=output_buffer)
                elif game_type == 'quiz':
                    result = games.play_quiz(output_stream=output_buffer)
                elif game_type == 'memory':
                    result = games.play_memory(length, output_stream=output_buffer)
                elif game_type == 'challenge':
                    result = games.play_challenge(output_stream=output_buffer)
                else:
                    result = {'success': False, 'error': f'Unknown game: {game_type}'}
            
            else:
                result = {'success': False, 'error': f'Unknown tool: {tool_name}'}
            
            # Get output
            output = output_buffer.getvalue()
            
            # Stream output if callback provided
            if output_callback and output:
                # Split output into lines and send each
                for line in output.split('\n'):
                    if line.strip():
                        await output_callback(line)
            
            # Add output to result
            result['output'] = output
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                'success': False,
                'error': str(e),
                'output': f"❌ Error: {str(e)}\n"
            }
        finally:
            if str(self.tools_path) in sys.path:
                sys.path.remove(str(self.tools_path))
    
    def parse_tool_command(self, command: str) -> Optional[Dict[str, Any]]:
        """
        Parse a command to determine if it's a tool command.
        
        Returns:
            Dict with tool_name and args if it's a tool command, None otherwise
        """
        command = command.strip()
        
        # Audio analysis commands
        if command.startswith('analyze'):
            parts = command.split()
            if len(parts) >= 2:
                analysis_type = parts[1]
                file_path = None
                effect = 'reverb'
                
                # Parse options
                if '--file' in parts or '-f' in parts:
                    opt = '--file' if '--file' in parts else '-f'
                    file_idx = parts.index(opt)
                    if file_idx + 1 < len(parts):
                        file_path = parts[file_idx + 1]
                
                if '--effect' in parts or '-e' in parts:
                    opt = '--effect' if '--effect' in parts else '-e'
                    effect_idx = parts.index(opt)
                    if effect_idx + 1 < len(parts):
                        effect = parts[effect_idx + 1]
                
                return {
                    'tool_name': 'audio_analyzer',
                    'args': {
                        'type': analysis_type,
                        'file': file_path,
                        'effect': effect
                    }
                }
        
        # Visualization commands
        elif command.startswith('visualize'):
            parts = command.split()
            viz_type = '3d'
            source = (5.0, 0.0, 2.0)
            listener = (0.0, 0.0, 0.0)
            save = False
            
            if len(parts) >= 2:
                viz_type = parts[1]
            
            # Parse position options
            if '--source' in parts:
                idx = parts.index('--source')
                if idx + 3 < len(parts):
                    try:
                        source = (float(parts[idx+1]), float(parts[idx+2]), float(parts[idx+3]))
                    except (ValueError, IndexError):
                        pass
            
            if '--listener' in parts:
                idx = parts.index('--listener')
                if idx + 3 < len(parts):
                    try:
                        listener = (float(parts[idx+1]), float(parts[idx+2]), float(parts[idx+3]))
                    except (ValueError, IndexError):
                        pass
            
            if '--save' in parts:
                save = True
            
            return {
                'tool_name': 'spatial_visualizer',
                'args': {
                    'type': viz_type,
                    'source': source,
                    'listener': listener,
                    'save': save
                }
            }
        
        # Playground commands
        elif command.startswith('playground') or command.startswith('demo'):
            parts = command.split()
            demo = None
            if len(parts) >= 2:
                demo = parts[1]
            
            return {
                'tool_name': 'interactive_playground',
                'args': {
                    'demo': demo
                }
            }
        
        # Game commands
        elif command.startswith('game'):
            parts = command.split()
            game_type = 'list'
            max_num = 100
            length = 5
            
            if len(parts) >= 2:
                game_type = parts[1]
            
            # Parse options
            if '--max' in parts:
                idx = parts.index('--max')
                if idx + 1 < len(parts):
                    try:
                        max_num = int(parts[idx + 1])
                    except (ValueError, IndexError):
                        pass
            
            if '--length' in parts:
                idx = parts.index('--length')
                if idx + 1 < len(parts):
                    try:
                        length = int(parts[idx + 1])
                    except (ValueError, IndexError):
                        pass
            
            return {
                'tool_name': 'game_collection',
                'args': {
                    'game': game_type,
                    'max': max_num,
                    'length': length
                }
            }
        
        return None

