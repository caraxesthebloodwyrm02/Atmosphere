"""
Game Controller
Manages game state and navigation.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import uuid

# Import game engine
api_path = Path(__file__).parent.parent.parent / "api"
if str(api_path) not in sys.path:
    sys.path.insert(0, str(api_path))
from game_engine import GameEngine, GameSession
from routing_integration import RoutingIntegration


class GameController:
    """Controls game state and navigation."""
    
    def __init__(self):
        routing = RoutingIntegration()
        self.game_engine = GameEngine(routing_integration=routing)
        self.session_id = str(uuid.uuid4())
        self.session = self.game_engine.create_session(self.session_id)
    
    def process_command(self, command: str) -> Dict[str, Any]:
        """Process a navigation/game command."""
        result = self.game_engine.process_navigation_command(
            self.session_id,
            command
        )
        return result
    
    def get_state(self) -> Dict[str, Any]:
        """Get current game state."""
        if not self.session:
            return {}
        
        return {
            'location': self.session.current_location,
            'score': self.session.score,
            'level': self.session.level,
            'speed': self.session.speed,
            'history': self.session.location_history[-5:]  # Last 5 locations
        }
    
    def navigate_to(self, location: str) -> Dict[str, Any]:
        """Navigate to a location."""
        result = self.process_command(f"cd {location}")
        if result.get('success'):
            self.session = self.game_engine.get_session(self.session_id)
        return result

