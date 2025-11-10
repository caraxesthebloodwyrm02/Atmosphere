"""
Game Engine for Arcade Terminal
Implements "bumper car" game mechanics with navigation and time travel.
"""

import time
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class GameState(Enum):
    """Game state enumeration"""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    NAVIGATING = "navigating"


@dataclass
class GameSession:
    """Represents a game session"""
    session_id: str
    state: GameState = GameState.MENU
    score: int = 0
    level: int = 1
    current_location: str = "Arcade"
    location_history: List[str] = field(default_factory=list)
    speed: float = 0.0
    created_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)


class GameEngine:
    """Game engine for bumper car mechanics"""
    
    def __init__(self, routing_integration: Optional[Any] = None):
        self.routing = routing_integration
        self.sessions: Dict[str, GameSession] = {}
        self.cities = {
            'Echoes': {
                'name': 'Echoes',
                'description': 'The city of echoes, where sound reverberates through time',
                'coordinates': {'x': 0, 'y': 0, 'z': 0}
            },
            'Reverb': {
                'name': 'Reverb',
                'description': 'The city of reverb, where acoustic spaces define reality',
                'coordinates': {'x': 100, 'y': 0, 'z': 0}
            },
            'Delay': {
                'name': 'Delay',
                'description': 'The city of delay, where time flows differently',
                'coordinates': {'x': 0, 'y': 100, 'z': 0}
            },
            'Arcade': {
                'name': 'Arcade',
                'description': 'The central entertainment hub',
                'coordinates': {'x': 0, 'y': 0, 'z': 0}
            }
        }
    
    def create_session(self, session_id: str) -> GameSession:
        """Create a new game session"""
        if session_id in self.sessions:
            return self.sessions[session_id]
        
        session = GameSession(session_id=session_id)
        session.location_history.append("Arcade")
        self.sessions[session_id] = session
        
        logger.info(f"Created game session {session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[GameSession]:
        """Get a game session"""
        return self.sessions.get(session_id)
    
    def process_navigation_command(self, session_id: str, command: str) -> Dict[str, Any]:
        """
        Process navigation commands (cd, cd .., cd ...)
        Returns game state update
        """
        session = self.get_session(session_id)
        if not session:
            session = self.create_session(session_id)
        
        command_lower = command.strip().lower()
        
        # Handle cd commands
        if command_lower.startswith('cd'):
            parts = command_lower.split()
            
            if len(parts) == 1 or (len(parts) == 2 and parts[1] == '.'):
                # cd or cd . - stay in place
                return {
                    'success': True,
                    'message': f'You are at {session.current_location}',
                    'location': session.current_location,
                    'speed': session.speed
                }
            
            elif len(parts) == 2 and parts[1] == '..':
                # cd .. - go back one level (time travel backward)
                return self._navigate_backward(session)
            
            elif len(parts) == 2 and parts[1] == '...':
                # cd ... - go back two levels (further time travel)
                return self._navigate_backward(session, steps=2)
            
            elif len(parts) == 2:
                # cd <location> - navigate to location
                target = parts[1]
                return self._navigate_to(session, target)
        
        # Handle other navigation commands
        elif command_lower in ['pwd', 'get-location']:
            return {
                'success': True,
                'message': f'Current location: {session.current_location}',
                'location': session.current_location,
                'history': session.location_history[-5:]  # Last 5 locations
            }
        
        elif command_lower in ['ls', 'dir', 'get-childitem']:
            return {
                'success': True,
                'message': 'Available destinations:',
                'locations': list(self.cities.keys()),
                'current': session.current_location
            }
        
        elif command_lower == 'help':
            return {
                'success': True,
                'message': 'Arcade Navigation Commands:',
                'commands': {
                    'cd <location>': 'Navigate to a location',
                    'cd ..': 'Go back in time (previous location)',
                    'cd ...': 'Go further back in time',
                    'pwd': 'Show current location',
                    'ls': 'List available destinations',
                    'help': 'Show this help',
                    'speed': 'Check your speed',
                    'status': 'Show game status',
                    'analyze 808-bass': 'Analyze 808 bass frequencies',
                    'analyze bass-delay': 'Compare bass vs delay effects',
                    'analyze sound-effects': 'Analyze sound effects',
                    'visualize 3d': '3D spatial audio visualization',
                    'visualize comprehensive': 'Comprehensive 6-panel visualization',
                    'game list': 'List available games',
                    'game guessing': 'Play number guessing game',
                    'game quiz': 'Play audio frequency quiz',
                    'game memory': 'Play spatial memory game',
                    'playground': 'Interactive playground menu',
                    'demo audio': 'Run audio demo',
                    'demo spatial': 'Run spatial demo'
                }
            }
        
        elif command_lower == 'speed':
            return {
                'success': True,
                'message': f'Current speed: {session.speed:.2f} (liminal space - no speed limit!)',
                'speed': session.speed
            }
        
        elif command_lower == 'status':
            return {
                'success': True,
                'game_state': {
                    'state': session.state.value,
                    'score': session.score,
                    'level': session.level,
                    'location': session.current_location,
                    'speed': session.speed,
                    'time_played': time.time() - session.created_at
                }
            }
        
        # Unknown command - let terminal handle it
        return {
            'success': False,
            'message': 'Command not recognized as game command'
        }
    
    def _navigate_backward(self, session: GameSession, steps: int = 1) -> Dict[str, Any]:
        """Navigate backward in location history (time travel)"""
        if len(session.location_history) <= steps:
            return {
                'success': False,
                'message': 'Cannot go back further - you are at the beginning of time!',
                'location': session.current_location
            }
        
        # Go back in history
        for _ in range(steps):
            if len(session.location_history) > 1:
                session.location_history.pop()
        
        previous_location = session.location_history[-1]
        session.current_location = previous_location
        
        # Increase speed (time travel effect)
        session.speed += 10.0
        
        return {
            'success': True,
            'message': f'Time travel! You went back to {previous_location}',
            'location': previous_location,
            'speed': session.speed,
            'effect': 'time_travel_backward'
        }
    
    def _navigate_to(self, session: GameSession, target: str) -> Dict[str, Any]:
        """Navigate to a target location"""
        # Check if target is a known city
        target_normalized = target.capitalize()
        
        if target_normalized not in self.cities:
            return {
                'success': False,
                'message': f'Unknown destination: {target}. Use "ls" to see available locations.',
                'location': session.current_location
            }
        
        # Update location
        previous_location = session.current_location
        session.current_location = target_normalized
        session.location_history.append(target_normalized)
        
        # Update speed (simulate movement)
        session.speed = min(session.speed + 5.0, 100.0)  # Cap at 100
        
        # Get city info
        city_info = self.cities[target_normalized]
        
        # If routing is available, try to connect to city
        routing_result = None
        if self.routing:
            try:
                # Create a task for the async routing call since we're in a sync method
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                routing_result = loop.run_until_complete(self.routing.navigate_to_city(target_normalized))
                loop.close()
            except Exception as e:
                logger.debug(f"Routing integration error: {e}")
        
        return {
            'success': True,
            'message': f'Navigating to {target_normalized}... {city_info["description"]}',
            'location': target_normalized,
            'previous_location': previous_location,
            'speed': session.speed,
            'city_info': city_info,
            'routing': routing_result,
            'effect': 'navigation'
        }
    
    def update_score(self, session_id: str, points: int) -> None:
        """Update game score"""
        session = self.get_session(session_id)
        if session:
            session.score += points
            # Level up every 100 points
            session.level = (session.score // 100) + 1
    
    def get_game_state(self, session_id: str) -> Dict[str, Any]:
        """Get current game state"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        return {
            'session_id': session_id,
            'state': session.state.value,
            'score': session.score,
            'level': session.level,
            'location': session.current_location,
            'speed': session.speed,
            'location_history': session.location_history[-10:],  # Last 10
            'time_played': time.time() - session.created_at
        }
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a game session and return final stats"""
        session = self.sessions.pop(session_id, None)
        if not session:
            return {}
        
        return {
            'session_id': session_id,
            'final_score': session.score,
            'final_level': session.level,
            'locations_visited': len(set(session.location_history)),
            'time_played': time.time() - session.created_at
        }

