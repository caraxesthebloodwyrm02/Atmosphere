"""
Game Collection Tool
Mini-games for the Arcade Terminal.
"""

from typing import Dict, Any, Optional
import random
import time

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


class GameCollection:
    """Collection of mini-games."""
    
    def __init__(self):
        self.scores = {}
    
    def _print_colored(self, message: str, color: str = Colors.GREEN, stream=None):
        """Print colored message."""
        output = f"{color}{message}{Colors.RESET}\n"
        if stream:
            stream.write(output)
        else:
            print(output, end='')
    
    def list_games(self, output_stream=None) -> Dict[str, Any]:
        """List available games."""
        self._print_colored("\n🎮 Available Games", Colors.MAGENTA, output_stream)
        self._print_colored("=" * 50, Colors.CYAN, output_stream)
        self._print_colored("  1. 🎯 Number Guessing", Colors.YELLOW, output_stream)
        self._print_colored("  2. 🎵 Audio Frequency Quiz", Colors.YELLOW, output_stream)
        self._print_colored("  3. 🎨 Spatial Memory", Colors.YELLOW, output_stream)
        self._print_colored("  4. 🎲 Random Challenge", Colors.YELLOW, output_stream)
        self._print_colored("  0. Exit", Colors.GRAY, output_stream)
        return {'success': True, 'games': ['guessing', 'quiz', 'memory', 'challenge']}
    
    def play_guessing(self, max_number: int = 100, output_stream=None) -> Dict[str, Any]:
        """Number guessing game."""
        self._print_colored("\n🎯 Number Guessing Game", Colors.MAGENTA, output_stream)
        self._print_colored("=" * 50, Colors.CYAN, output_stream)
        self._print_colored(f"Guess a number between 1 and {max_number}!", Colors.CYAN, output_stream)
        
        target = random.randint(1, max_number)
        attempts = 0
        max_attempts = 7
        
        # For CLI, we'd need input, but for web/automated, we'll simulate
        self._print_colored(f"🎲 Target number generated!", Colors.GREEN, output_stream)
        self._print_colored(f"   You have {max_attempts} attempts", Colors.YELLOW, output_stream)
        
        return {
            'success': True,
            'game': 'guessing',
            'target': target,
            'max_attempts': max_attempts,
            'hint': f"Number is between 1 and {max_number}"
        }
    
    def play_quiz(self, output_stream=None) -> Dict[str, Any]:
        """Audio frequency quiz."""
        self._print_colored("\n🎵 Audio Frequency Quiz", Colors.MAGENTA, output_stream)
        self._print_colored("=" * 50, Colors.CYAN, output_stream)
        
        questions = [
            {
                'question': 'What frequency range is typical for 808 bass?',
                'options': ['50-100 Hz', '150-240 Hz', '500-1000 Hz', '2000-5000 Hz'],
                'correct': 1
            },
            {
                'question': 'What is the speed of sound in air?',
                'options': ['300 m/s', '343 m/s', '400 m/s', '500 m/s'],
                'correct': 1
            }
        ]
        
        question = random.choice(questions)
        self._print_colored(f"\n❓ {question['question']}", Colors.CYAN, output_stream)
        for i, option in enumerate(question['options']):
            self._print_colored(f"  {i+1}. {option}", Colors.YELLOW, output_stream)
        
        return {
            'success': True,
            'game': 'quiz',
            'question': question,
            'correct': question['correct']
        }
    
    def play_memory(self, sequence_length: int = 5, output_stream=None) -> Dict[str, Any]:
        """Spatial memory game."""
        self._print_colored("\n🎨 Spatial Memory Game", Colors.MAGENTA, output_stream)
        self._print_colored("=" * 50, Colors.CYAN, output_stream)
        
        # Generate random sequence
        positions = [(random.randint(0, 9), random.randint(0, 9)) for _ in range(sequence_length)]
        
        self._print_colored(f"Remember these {sequence_length} positions:", Colors.CYAN, output_stream)
        for i, pos in enumerate(positions):
            self._print_colored(f"  {i+1}. ({pos[0]}, {pos[1]})", Colors.YELLOW, output_stream)
        
        self._print_colored("\n⏱️  You have 5 seconds to memorize...", Colors.GRAY, output_stream)
        
        return {
            'success': True,
            'game': 'memory',
            'sequence': positions,
            'length': sequence_length
        }
    
    def play_challenge(self, output_stream=None) -> Dict[str, Any]:
        """Random challenge game."""
        self._print_colored("\n🎲 Random Challenge", Colors.MAGENTA, output_stream)
        self._print_colored("=" * 50, Colors.CYAN, output_stream)
        
        challenges = [
            {
                'name': 'Speed Test',
                'description': 'Type as many commands as you can in 10 seconds',
                'type': 'speed'
            },
            {
                'name': 'Pattern Match',
                'description': 'Match the audio frequency pattern',
                'type': 'pattern'
            },
            {
                'name': 'Spatial Navigation',
                'description': 'Navigate through 3D space coordinates',
                'type': 'navigation'
            }
        ]
        
        challenge = random.choice(challenges)
        self._print_colored(f"\n🎯 Challenge: {challenge['name']}", Colors.CYAN, output_stream)
        self._print_colored(f"📝 {challenge['description']}", Colors.YELLOW, output_stream)
        
        return {
            'success': True,
            'game': 'challenge',
            'challenge': challenge
        }


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Game Collection')
    parser.add_argument('game', choices=['list', 'guessing', 'quiz', 'memory', 'challenge'], help='Game to play')
    parser.add_argument('--max', type=int, default=100, help='Max number for guessing game')
    parser.add_argument('--length', type=int, default=5, help='Sequence length for memory game')
    
    args = parser.parse_args()
    
    games = GameCollection()
    
    if args.game == 'list':
        games.list_games()
    elif args.game == 'guessing':
        games.play_guessing(args.max)
    elif args.game == 'quiz':
        games.play_quiz()
    elif args.game == 'memory':
        games.play_memory(args.length)
    elif args.game == 'challenge':
        games.play_challenge()


if __name__ == "__main__":
    main()

