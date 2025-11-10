"""
Cable Assistant - Modern OpenAI Chat Interface

A type-safe chat interface using Pydantic models for request/response handling.
Provides a clean, maintainable API for interacting with OpenAI's chat completions.
"""
from enum import Enum
import os
import json
import requests
from typing import List, Dict, Optional, Union, Generator, Any, Literal
from pydantic import BaseModel, Field, HttpUrl
from openai import OpenAI, OpenAIError
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam

# Try to set up readline for better input handling
try:
    import readline  # Unix-like systems
except ImportError:
    try:
        import pyreadline3 as readline  # Windows
    except ImportError:
        pass  # Fall back to basic input()

class MessageRole(str, Enum):
    """Role of the message sender in the conversation."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"

class Message(BaseModel):
    """A message in the conversation."""
    role: MessageRole
    content: str
    name: Optional[str] = None

    def to_api_format(self) -> ChatCompletionMessageParam:
        """Convert to OpenAI API format."""
        return {
            "role": self.role.value,
            "content": self.content,
            **({"name": self.name} if self.name else {})
        }

class ChatRequest(BaseModel):
    """Request model for chat completions."""
    messages: List[Message]
    model: str = "gpt-4-1106-preview"
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    stream: bool = False
    max_tokens: Optional[int] = None

class TokenUsage(BaseModel):
    """Token usage information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class ChatResponse(BaseModel):
    """Response model for chat completions."""
    content: str
    model: str
    usage: Optional[TokenUsage] = None

class HTTPClientConfig(BaseModel):
    """Configuration for direct HTTP requests to the OpenAI API."""
    base_url: HttpUrl = "https://api.openai.com/v1"
    api_key: str
    timeout: int = 30
    max_retries: int = 3


class CableAssistant:
    """Handles chat interactions with OpenAI's API using Pydantic models.
    
    Supports both the official OpenAI client and direct HTTP requests.
    """

    def __init__(
        self, 
        model: str = "gpt-4-1106-preview", 
        temperature: float = 0.7,
        use_http: bool = False,
        http_config: Optional[HTTPClientConfig] = None
    ):
        """Initialize the chat assistant.

        Args:
            model: The OpenAI model to use (default: gpt-4-1106-preview)
            temperature: Controls response randomness (0.0 to 2.0)
            use_http: If True, use direct HTTP requests instead of the official client
            http_config: Configuration for HTTP client (required if use_http is True)
        """
        self.model = model
        self.temperature = temperature
        self.messages: List[Message] = []
        self.use_http = use_http
        
        if use_http:
            if http_config is None:
                api_key = os.getenv('OPENAI_API_KEY')
                if not api_key:
                    raise ValueError("OPENAI_API_KEY environment variable not set")
                self.http_config = HTTPClientConfig(api_key=api_key)
            else:
                self.http_config = http_config
        else:
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        """Initialize the chat assistant.

        Args:
            model: The OpenAI model to use (default: gpt-4-1106-preview)
            temperature: Controls response randomness (0.0 to 2.0)
        """
        self.model = model
        self.temperature = temperature
        self.messages: List[Message] = []
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

    def _make_http_request(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
        **kwargs
    ) -> Union[Dict[str, Any], Generator[Dict[str, Any], None, None]]:
        """Make a direct HTTP request to the OpenAI API.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response
            **kwargs: Additional parameters for the API request
            
        Returns:
            The API response as a dictionary or a generator for streaming
        """
        url = f"{self.http_config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.http_config.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            **kwargs
        }
        
        if stream:
            data["stream"] = True
            response = requests.post(
                url,
                headers=headers,
                json=data,
                stream=True,
                timeout=self.http_config.timeout
            )
            
            if response.status_code != 200:
                error = response.json().get('error', {})
                raise RuntimeError(
                    f"API request failed with status {response.status_code}: "
                    f"{error.get('message', 'Unknown error')}"
                )
                
            def generate():
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            line = line[6:]  # Remove 'data: ' prefix
                            if line == '[DONE]':
                                break
                            try:
                                yield json.loads(line)
                            except json.JSONDecodeError:
                                continue
            
            return generate()
        else:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.http_config.timeout
            )
            
            if response.status_code != 200:
                error = response.json().get('error', {})
                raise RuntimeError(
                    f"API request failed with status {response.status_code}: "
                    f"{error.get('message', 'Unknown error')}"
                )
                
            return response.json()

    def chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> ChatResponse:
        """Generate a chat completion and maintain conversation history.

        Args:
            message: User's message text
            system_prompt: Optional system message to set the assistant's behavior
            **kwargs: Additional arguments for the API call

        Returns:
            ChatResponse containing the assistant's response and metadata
        """
        # Add user message to history
        user_msg = Message(role=MessageRole.USER, content=message)
        self.messages.append(user_msg)

        # Prepare messages with optional system prompt
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend([{"role": msg.role.value, "content": msg.content} for msg in self.messages])

        try:
            if self.use_http:
                # Use direct HTTP request
                response = self._make_http_request(messages, stream=False, **kwargs)
                
                # Process response
                choice = response["choices"][0]
                assistant_content = choice["message"]["content"]
                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    content=assistant_content
                )
                self.messages.append(assistant_msg)
                
                # Convert usage to a simpler format if it exists
                usage = None
                if "usage" in response:
                    usage_data = response["usage"]
                    usage = TokenUsage(
                        prompt_tokens=usage_data.get("prompt_tokens", 0),
                        completion_tokens=usage_data.get("completion_tokens", 0),
                        total_tokens=usage_data.get("total_tokens", 0)
                    )
                
                return ChatResponse(
                    content=assistant_content,
                    model=response.get("model", "unknown"),
                    usage=usage
                )
            else:
                # Use official client
                api_messages = [
                    msg.to_api_format() if isinstance(msg, Message) else msg
                    for msg in messages
                ]
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=api_messages,
                    temperature=self.temperature,
                    **kwargs
                )
                
                assistant_content = response.choices[0].message.content or ""
                assistant_msg = Message(
                    role=MessageRole.ASSISTANT,
                    content=assistant_content
                )
                self.messages.append(assistant_msg)
                
                # Convert usage to a simpler format if it exists
                usage = None
                if response.usage:
                    usage = TokenUsage(
                        prompt_tokens=response.usage.prompt_tokens,
                        completion_tokens=response.usage.completion_tokens,
                        total_tokens=response.usage.total_tokens
                    )
                
                return ChatResponse(
                    content=assistant_content,
                    model=response.model,
                    usage=usage
                )

        except OpenAIError as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")
        except (ValueError, TypeError) as e:
            raise RuntimeError(f"Invalid input parameter: {str(e)}")
        except ConnectionError as e:
            raise RuntimeError(f"Network error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error in chat completion: {str(e)}") from e

    def stream_chat(
        self,
        message: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> Generator[str, None, None]:
        """Stream chat completion response with conversation history.

        Args:
            message: User's message text
            system_prompt: Optional system message to set the assistant's behavior
            **kwargs: Additional arguments for the API call

        Yields:
            Chunks of the assistant's response
        """
        # Add user message to history
        user_msg = Message(role=MessageRole.USER, content=message)
        self.messages.append(user_msg)

        # Prepare messages with optional system prompt
        messages: List[Dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history
        messages.extend([{"role": msg.role.value, "content": msg.content} for msg in self.messages])

        try:
            if self.use_http:
                # Use direct HTTP request with streaming
                stream = self._make_http_request(messages, stream=True, **kwargs)
                full_response = []
                
                for chunk in stream:
                    if not chunk.get('choices'):
                        continue
                        
                    delta = chunk['choices'][0].get('delta', {})
                    content = delta.get('content', '')
                    
                    if content:
                        full_response.append(content)
                        yield content
                
                # Store complete assistant response
                if full_response:
                    assistant_msg = Message(
                        role=MessageRole.ASSISTANT,
                        content="".join(full_response)
                    )
                    self.messages.append(assistant_msg)
            else:
                # Use official client
                api_messages = [
                    msg.to_api_format() if isinstance(msg, Message) else msg
                    for msg in messages
                ]
                
                stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=api_messages,
                    temperature=self.temperature,
                    stream=True,
                    **kwargs
                )

                full_response = []
                for chunk in stream:
                    content = chunk.choices[0].delta.content or ""
                    if content:
                        full_response.append(content)
                        yield content

                # Store complete assistant response
                if full_response:
                    assistant_msg = Message(
                        role=MessageRole.ASSISTANT,
                        content="".join(full_response)
                    )
                    self.messages.append(assistant_msg)

        except OpenAIError as e:
            yield f"OpenAI API error: {str(e)}"
        except (ValueError, TypeError) as e:
            yield f"Invalid input parameter: {str(e)}"
        except ConnectionError as e:
            yield f"Network error: {str(e)}"
        except Exception as e:
            yield f"Unexpected error in streaming chat: {str(e)}"

def interactive_chat():
    """Start an interactive chat session with the assistant."""
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment variables.")
        print("Please set it in the .env file or as an environment variable.")
        return
    
    print("Initializing Cable Assistant...")
    print("Type 'exit' or press Ctrl+C to quit\n")
    
    try:
        assistant = CableAssistant()
        
        while True:
            try:
                user_input = input("You: ").strip()
                if not user_input:
                    continue
                    
                if user_input.lower() in ('exit', 'quit'):
                    print("\nGoodbye!")
                    break
                
                print("\nAssistant: ", end="", flush=True)
                
                # Stream the response
                full_response = []
                for chunk in assistant.stream_chat(user_input):
                    print(chunk, end="", flush=True)
                    full_response.append(chunk)
                print("\n")
                
            except KeyboardInterrupt:
                print("\n\nType 'exit' to quit or press Ctrl+C again to exit immediately.")
                continue
            except RuntimeError as e:
                print(f"\nError: {str(e)}")
                continue
                
    except Exception as e:
        print(f"\nAn unexpected error occurred: {str(e)}")
    finally:
        print("\nSession ended.")

def main():
    """Entry point for the command-line interface."""
    try:
        interactive_chat()
    except KeyboardInterrupt:
        print("\nSession terminated by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nFatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
