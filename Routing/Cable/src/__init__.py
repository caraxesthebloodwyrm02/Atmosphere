"""
Cable Assistant - OpenAI Integration
"""
# Import only the OpenAI-related components
from .openai_diagnostics import verify_openai_integration, verify_openai_certificate, run_openai_smoke_test
from .assistant import CableAssistant, Message, MessageRole, ChatResponse

__all__ = [
    'CableAssistant',
    'Message',
    'MessageRole',
    'ChatResponse',
    'verify_openai_integration',
    'verify_openai_certificate',
    'run_openai_smoke_test'
]
