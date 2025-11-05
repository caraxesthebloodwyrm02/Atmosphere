# Direct OpenAI API Integration

Clean, simple integration with official OpenAI API. No middlewares, no complex linting - just direct API calls.

## 🚀 Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Setup
```bash
# Set your OpenAI API key
export OPENAI_API_KEY="your-api-key-here"

# Or create .env file
echo "OPENAI_API_KEY=your-api-key-here" > .env
```

### Usage

#### Simple Chat
```python
from api.client import chat

response = await chat("Hello! How are you?")
print(response)
```

#### Advanced Chat
```python
from api.client import DirectOpenAIClient

client = DirectOpenAIClient()
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Explain AI in simple terms."}
]
response = await client.chat_completion(messages, model="gpt-3.5-turbo")
print(response["content"])
```

#### Start Server
```bash
python -m api.server
```

## 📚 API Endpoints

### `POST /chat`
Chat completion with full parameters.

**Request:**
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "model": "gpt-3.5-turbo",
  "max_tokens": 100,
  "temperature": 0.7
}
```

**Response:**
```json
{
  "content": "Hello! How can I help you today?",
  "model": "gpt-3.5-turbo",
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 9,
    "total_tokens": 19
  },
  "finish_reason": "stop"
}
```

### `POST /chat/simple`
Simple chat with just a prompt.

**Request:**
```json
{
  "prompt": "What is Python?",
  "model": "gpt-3.5-turbo"
}
```

**Response:**
```json
{
  "response": "Python is a high-level programming language..."
}
```

### `GET /models`
Get available OpenAI models.

**Response:**
```json
{
  "models": ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo-preview", ...]
}
```

### `GET /health`
Check API health and connection status.

**Response:**
```json
{
  "status": "healthy",
  "openai": "connected"
}
```

## 🛠️ Examples

### Run Examples
```bash
# Basic examples
python example.py

# Test connection
python -m api.client

# Start server
python -m api.server
```

### Environment Setup
```bash
# Copy example environment file
cp .env.example .env

# Edit with your API key
nano .env
```

## 📖 Documentation

Based on official OpenAI API documentation:
- https://platform.openai.com/docs/overview
- https://platform.openai.com/docs/api-reference/chat

## 🔧 Configuration

### Environment Variables
- `OPENAI_API_KEY`: Your OpenAI API key (required)

### Default Settings
- Model: `gpt-3.5-turbo`
- Temperature: `0.7`
- Max Tokens: `None` (model default)

## 🚨 Important Notes

- No middleware or complex abstraction layers
- Direct calls to OpenAI API
- Simple error handling
- Minimal dependencies
- Clean, readable code

## 📝 License

MIT License - see LICENSE file for details.
