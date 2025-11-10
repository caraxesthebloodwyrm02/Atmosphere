"""
Tool Executor
Executes tools and streams output to TUI.
"""

import sys
import io
from pathlib import Path
from typing import Dict, Any, Optional, Callable
import asyncio

# Import tool integration
api_path = Path(__file__).parent.parent.parent / "api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))
from tool_integration import ToolIntegration


class ToolExecutor:
    """Executes tools with output streaming."""
    
    def __init__(self):
        self.tool_integration = ToolIntegration()
    
    async def execute(
        self,
        tool_name: str,
        args: Dict[str, Any],
        output_callback: Optional[Callable[[str], None]] = None
    ) -> Dict[str, Any]:
        """
        Execute a tool and stream output.
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            output_callback: Callback for output lines
        
        Returns:
            Execution result
        """
        async def stream_callback(line: str):
            if output_callback:
                output_callback(line)
        
        result = await self.tool_integration.execute_tool(
            tool_name,
            args,
            output_callback=stream_callback
        )
        
        return result
    
    def parse_command(self, command: str) -> Optional[Dict[str, Any]]:
        """Parse command to determine if it's a tool command."""
        return self.tool_integration.parse_tool_command(command)

