"""
AI Assistant Tool Wrapper
Integrates AI-powered assistance using licensed APIs (OpenAI/Anthropic).
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
import io

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


class AIAssistant:
    """AI-powered assistant using licensed APIs with colored output."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.conversation_history = []
        self.api_provider = self._detect_api_provider()

    def _detect_api_provider(self) -> str:
        """Detect available API provider."""
        # Check for API keys in environment or config
        if os.getenv('OPENAI_API_KEY'):
            return 'openai'
        elif os.getenv('ANTHROPIC_API_KEY'):
            return 'anthropic'
        else:
            return 'demo'  # Fallback to demo mode

    def _print_colored(self, message: str, color: str = Colors.GREEN, stream=None):
        """Print colored message."""
        output = f"{color}{message}{Colors.RESET}\n"
        if stream:
            stream.write(output)
        else:
            print(output, end='')

    def chat(self, message: str, model: str = "auto", output_stream=None) -> Dict[str, Any]:
        """Have a conversation with the AI assistant."""
        try:
            self._print_colored("🤖 AI Assistant", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)

            self._print_colored(f"\n💬 You: {message}", Colors.CYAN, output_stream)

            if self.api_provider == 'demo':
                return self._demo_response(message, output_stream)

            # Add user message to history
            self.conversation_history.append({"role": "user", "content": message})

            response = self._call_api(model)
            if response:
                self.conversation_history.append({"role": "assistant", "content": response})
                self._print_colored(f"\n🤖 Assistant: {response}", Colors.GREEN, output_stream)
                return {'success': True, 'response': response}
            else:
                return {'success': False, 'error': 'API call failed'}

        except Exception as e:
            self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
            return {'success': False, 'error': str(e)}

    def analyze_code(self, code: str, language: str = "python", output_stream=None) -> Dict[str, Any]:
        """Analyze code using AI."""
        try:
            self._print_colored("🔍 Code Analysis", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)

            prompt = f"Analyze this {language} code:\n\n{code}\n\nProvide insights on structure, potential improvements, and best practices."

            if self.api_provider == 'demo':
                return self._demo_code_analysis(code, language, output_stream)

            self.conversation_history = [{"role": "user", "content": prompt}]
            response = self._call_api()

            if response:
                self._print_colored(f"\n📊 Analysis:\n{response}", Colors.GREEN, output_stream)
                return {'success': True, 'analysis': response}
            else:
                return {'success': False, 'error': 'API call failed'}

        except Exception as e:
            self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
            return {'success': False, 'error': str(e)}

    def generate_code(self, description: str, language: str = "python", output_stream=None) -> Dict[str, Any]:
        """Generate code using AI."""
        try:
            self._print_colored("⚡ Code Generation", Colors.MAGENTA, output_stream)
            self._print_colored("=" * 50, Colors.CYAN, output_stream)

            prompt = f"Generate {language} code for: {description}\n\nProvide clean, well-documented code with comments."

            if self.api_provider == 'demo':
                return self._demo_code_generation(description, language, output_stream)

            self.conversation_history = [{"role": "user", "content": prompt}]
            response = self._call_api()

            if response:
                self._print_colored(f"\n💻 Generated Code:\n{response}", Colors.GREEN, output_stream)
                return {'success': True, 'code': response}
            else:
                return {'success': False, 'error': 'API call failed'}

        except Exception as e:
            self._print_colored(f"❌ Error: {e}", Colors.RED, output_stream)
            return {'success': False, 'error': str(e)}

    def _call_api(self, model: str = "auto") -> Optional[str]:
        """Call the appropriate API."""
        try:
            if self.api_provider == 'openai':
                return self._call_openai(model)
            elif self.api_provider == 'anthropic':
                return self._call_anthropic(model)
        except Exception as e:
            print(f"API call error: {e}")
            return None
        return None

    def _call_openai(self, model: str = "auto") -> Optional[str]:
        """Call OpenAI API."""
        try:
            import openai
            client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

            model_name = "gpt-4" if model == "auto" else model

            response = client.chat.completions.create(
                model=model_name,
                messages=self.conversation_history,
                max_tokens=1000,
                temperature=0.7
            )

            return response.choices[0].message.content
        except ImportError:
            print("OpenAI library not available")
            return None
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def _call_anthropic(self, model: str = "auto") -> Optional[str]:
        """Call Anthropic API."""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

            model_name = "claude-3-sonnet-20240229" if model == "auto" else model

            response = client.messages.create(
                model=model_name,
                max_tokens=1000,
                temperature=0.7,
                messages=self.conversation_history
            )

            return response.content[0].text
        except ImportError:
            print("Anthropic library not available")
            return None
        except Exception as e:
            print(f"Anthropic API error: {e}")
            return None

    def _demo_response(self, message: str, output_stream=None) -> Dict[str, Any]:
        """Demo response when no API available."""
        self._print_colored("\n🤖 Demo Mode - Assistant: This is a demo response.", Colors.GREEN, output_stream)
        self._print_colored("   To use real AI features, set OPENAI_API_KEY or ANTHROPIC_API_KEY", Colors.YELLOW, output_stream)
        self._print_colored("   Example response based on your message.", Colors.GRAY, output_stream)
        return {'success': True, 'response': 'Demo response', 'demo': True}

    def _demo_code_analysis(self, code: str, language: str, output_stream=None) -> Dict[str, Any]:
        """Demo code analysis."""
        self._print_colored("\n📊 Demo Analysis:", Colors.GREEN, output_stream)
        self._print_colored("   This is a demo analysis.", Colors.YELLOW, output_stream)
        self._print_colored(f"   Code appears to be {language}.", Colors.GRAY, output_stream)
        self._print_colored("   Basic structure looks good.", Colors.GRAY, output_stream)
        return {'success': True, 'analysis': 'Demo analysis', 'demo': True}

    def _demo_code_generation(self, description: str, language: str, output_stream=None) -> Dict[str, Any]:
        """Demo code generation."""
        self._print_colored("\n💻 Demo Generated Code:", Colors.GREEN, output_stream)
        self._print_colored(f"   # Demo {language} code for: {description}", Colors.YELLOW, output_stream)
        self._print_colored("   print('Hello, World!')", Colors.GRAY, output_stream)
        return {'success': True, 'code': 'Demo code', 'demo': True}

    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current API provider."""
        return {
            'provider': self.api_provider,
            'has_key': bool(os.getenv(f'{self.api_provider.upper()}_API_KEY')) if self.api_provider != 'demo' else False
        }


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='AI Assistant Tool')
    parser.add_argument('command', choices=['chat', 'analyze', 'generate'], help='Command to run')
    parser.add_argument('--message', '-m', help='Message for chat')
    parser.add_argument('--code', '-c', help='Code to analyze')
    parser.add_argument('--description', '-d', help='Description for code generation')
    parser.add_argument('--language', '-l', default='python', help='Programming language')

    args = parser.parse_args()

    assistant = AIAssistant()

    if args.command == 'chat':
        if not args.message:
            print("Error: --message required for chat")
            return
        assistant.chat(args.message)
    elif args.command == 'analyze':
        if not args.code:
            print("Error: --code required for analyze")
            return
        assistant.analyze_code(args.code, args.language)
    elif args.command == 'generate':
        if not args.description:
            print("Error: --description required for generate")
            return
        assistant.generate_code(args.description, args.language)


if __name__ == "__main__":
    main()
