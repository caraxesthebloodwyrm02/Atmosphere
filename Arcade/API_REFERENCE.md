# Atmosphere Arcade - Complete API Reference

## Table of Contents
1. [Overview](#overview)
2. [Core Components](#core-components)
3. [Terminal API](#terminal-api)
4. [AI Services API](#ai-services-api)
5. [File System API](#file-system-api)
6. [Session Management API](#session-management-api)
7. [Security API](#security-api)
8. [Monitoring API](#monitoring-api)
9. [Web Interface API](#web-interface-api)
10. [Error Handling](#error-handling)
11. [Examples](#examples)

## Overview

Atmosphere Arcade provides a comprehensive API ecosystem for AI-powered terminal interactions, multilingual support, and secure file operations. The system is built with FastAPI and supports both WebSocket and REST endpoints.

**Base URL**: `http://localhost:7681`
**WebSocket URL**: `ws://localhost:7681/arcade/ws`

## Core Components

### 1. Enhanced Terminal Handler
Manages natural language processing and command interpretation.

### 2. AI Assistant
Provides intelligent responses and command suggestions.

### 3. ChatGPT Manager
Handles multilingual translation and conversation management.

### 4. File System Manager
Secure file operations with sandboxing.

### 5. Session Manager
Persistent user sessions and context management.

## Terminal API

### Interactive Terminal

#### Start Terminal Session
```http
POST /terminal/start
Content-Type: application/json

{
  "user_id": "string",
  "language": "en",
  "working_directory": "/path/to/dir"
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "active",
  "current_directory": "/path/to/dir",
  "supported_languages": ["en", "es", "fr", "de", "bn", "hi"]
}
```

#### Execute Command
```http
POST /terminal/execute
Content-Type: application/json

{
  "session_id": "uuid",
  "command": "show me the files",
  "language": "en"
}
```

**Response:**
```json
{
  "response": "Here are the files in your directory:\n- file1.txt\n- file2.py",
  "command_type": "file_list",
  "execution_time": 0.123,
  "ai_used": true
}
```

#### Get Terminal Status
```http
GET /terminal/status/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "status": "active",
  "current_directory": "/current/path",
  "last_activity": "2024-01-15T10:30:00Z",
  "command_history_count": 25
}
```

## AI Services API

### ChatGPT Manager

#### Process Multilingual Message
```http
POST /ai/chatgpt/process
Content-Type: application/json

{
  "conversation_id": "uuid",
  "message": "Hello, how are you?",
  "language": "en",
  "context": {
    "terminal_session": "uuid",
    "current_directory": "/path"
  }
}
```

**Response:**
```json
{
  "response": "Hello! I'm doing well, thank you. How can I help you with your development tasks today?",
  "detected_language": "en",
  "translated_response": null,
  "conversation_context": {
    "message_count": 1,
    "last_activity": "2024-01-15T10:30:00Z"
  }
}
```

#### Translate Text
```http
POST /ai/chatgpt/translate
Content-Type: application/json

{
  "text": "Hello world",
  "target_language": "es",
  "source_language": "en"
}
```

**Response:**
```json
{
  "original_text": "Hello world",
  "translated_text": "Hola mundo",
  "source_language": "en",
  "target_language": "es",
  "confidence": 0.98
}
```

#### Get Conversation History
```http
GET /ai/chatgpt/conversation/{conversation_id}
```

**Response:**
```json
{
  "conversation_id": "uuid",
  "messages": [
    {
      "role": "user",
      "content": "Hello",
      "timestamp": "2024-01-15T10:29:00Z",
      "language": "en"
    },
    {
      "role": "assistant",
      "content": "Hello! How can I help?",
      "timestamp": "2024-01-15T10:29:05Z",
      "language": "en"
    }
  ],
  "total_messages": 2,
  "created_at": "2024-01-15T10:29:00Z"
}
```

### AI Assistant

#### Generate Response
```http
POST /ai/assistant/generate
Content-Type: application/json

{
  "prompt": "What can you help me with?",
  "context": {
    "session_id": "uuid",
    "current_directory": "/path",
    "command_history": ["ls", "cd projects"]
  },
  "language": "en"
}
```

**Response:**
```json
{
  "response": "I can help you with various development tasks including file operations, code analysis, and general assistance. You can ask me in natural language!",
  "response_type": "general_help",
  "suggested_commands": ["show me files", "read README.md", "create new file"],
  "processing_time": 0.234
}
```

## File System API

### File Operations

#### List Directory
```http
GET /fs/list/{path}
Query Parameters:
- recursive: boolean (default: false)
- include_hidden: boolean (default: false)
```

**Response:**
```json
{
  "path": "/current/directory",
  "contents": [
    {
      "name": "file1.txt",
      "type": "file",
      "size": 1024,
      "modified": "2024-01-15T10:00:00Z",
      "permissions": "rw-r--r--"
    },
    {
      "name": "subdir",
      "type": "directory",
      "size": 4096,
      "modified": "2024-01-15T09:00:00Z",
      "permissions": "rwxr-xr-x"
    }
  ],
  "total_items": 2
}
```

#### Read File
```http
GET /fs/read/{path}
Query Parameters:
- encoding: string (default: utf-8)
- limit: integer (max lines to read)
```

**Response:**
```json
{
  "path": "/path/to/file.txt",
  "content": "File content here...",
  "encoding": "utf-8",
  "size": 1024,
  "line_count": 25,
  "truncated": false
}
```

#### Write File
```http
POST /fs/write
Content-Type: application/json

{
  "path": "/path/to/file.txt",
  "content": "New file content",
  "encoding": "utf-8",
  "backup": true
}
```

**Response:**
```json
{
  "path": "/path/to/file.txt",
  "bytes_written": 1024,
  "backup_created": "/path/to/file.txt.bak",
  "modified": "2024-01-15T10:30:00Z"
}
```

#### Create Directory
```http
POST /fs/mkdir
Content-Type: application/json

{
  "path": "/path/to/new/directory",
  "parents": true,
  "mode": "755"
}
```

**Response:**
```json
{
  "path": "/path/to/new/directory",
  "created": true,
  "mode": "755"
}
```

## Session Management API

### Session Operations

#### Create Session
```http
POST /session/create
Content-Type: application/json

{
  "user_id": "string",
  "initial_directory": "/home/user",
  "language": "en",
  "preferences": {
    "ai_personality": "helpful",
    "file_operations": "safe"
  }
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user_id": "string",
  "created_at": "2024-01-15T10:00:00Z",
  "status": "active",
  "settings": {
    "language": "en",
    "working_directory": "/home/user"
  }
}
```

#### Get Session
```http
GET /session/{session_id}
```

**Response:**
```json
{
  "session_id": "uuid",
  "user_id": "string",
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z",
  "last_activity": "2024-01-15T10:30:00Z",
  "command_count": 15,
  "ai_interactions": 8,
  "file_operations": 7,
  "current_directory": "/current/path",
  "language": "en"
}
```

#### Update Session
```http
PUT /session/{session_id}
Content-Type: application/json

{
  "current_directory": "/new/path",
  "language": "es",
  "preferences": {
    "theme": "dark"
  }
}
```

**Response:**
```json
{
  "session_id": "uuid",
  "updated_fields": ["current_directory", "language", "preferences"],
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Security API

### Access Control

#### Check Permissions
```http
POST /security/check
Content-Type: application/json

{
  "session_id": "uuid",
  "operation": "file_read",
  "path": "/path/to/file",
  "user_id": "string"
}
```

**Response:**
```json
{
  "allowed": true,
  "operation": "file_read",
  "path": "/path/to/file",
  "restrictions": [],
  "audit_log_id": "uuid"
}
```

#### Get Security Status
```http
GET /security/status
```

**Response:**
```json
{
  "security_level": "high",
  "sandbox_enabled": true,
  "audit_logging": true,
  "allowed_paths": ["/home/user", "/tmp"],
  "blocked_operations": ["system", "network"],
  "active_sessions": 5,
  "security_events_today": 12
}
```

## Monitoring API

### System Metrics

#### Get System Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": "2 days, 4 hours",
  "cpu_usage": 15.2,
  "memory_usage": 234.5,
  "active_sessions": 8,
  "total_requests": 15420,
  "error_rate": 0.001,
  "last_backup": "2024-01-15T02:00:00Z"
}
```

#### Get Performance Metrics
```http
GET /metrics
```

**Response:**
```json
{
  "response_times": {
    "average": 0.234,
    "p95": 0.567,
    "p99": 1.234
  },
  "ai_processing": {
    "total_requests": 15420,
    "average_time": 0.345,
    "success_rate": 0.998
  },
  "file_operations": {
    "reads": 1234,
    "writes": 567,
    "errors": 2
  },
  "multilingual_support": {
    "languages_used": ["en", "es", "fr", "de"],
    "translation_requests": 2340,
    "average_translation_time": 0.123
  }
}
```

## Web Interface API

### Web Dashboard

#### Get Dashboard Data
```http
GET /web/dashboard
```

**Response:**
```json
{
  "user_info": {
    "name": "John Doe",
    "sessions_today": 3,
    "commands_executed": 45
  },
  "recent_activity": [
    {
      "timestamp": "2024-01-15T10:29:00Z",
      "action": "file_read",
      "details": "Read README.md"
    }
  ],
  "system_status": {
    "ai_services": "operational",
    "file_system": "healthy",
    "security": "active"
  }
}
```

## Error Handling

All API endpoints follow consistent error response format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "command",
      "issue": "Command cannot be empty"
    },
    "timestamp": "2024-01-15T10:30:00Z",
    "request_id": "uuid"
  }
}
```

### Common Error Codes

- `VALIDATION_ERROR`: Invalid request parameters
- `AUTHENTICATION_ERROR`: Invalid or missing credentials
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error
- `AI_SERVICE_ERROR`: AI service unavailable
- `FILE_SYSTEM_ERROR`: File operation failed
- `SECURITY_VIOLATION`: Security policy violation

## Examples

### Complete Conversation Flow

```python
import requests
import json

# 1. Start a session
session_response = requests.post('http://localhost:7681/session/create', json={
    "user_id": "demo_user",
    "language": "en"
})
session_data = session_response.json()
session_id = session_data['session_id']

# 2. Execute a natural language command
command_response = requests.post('http://localhost:7681/terminal/execute', json={
    "session_id": session_id,
    "command": "show me the files in the current directory",
    "language": "en"
})
print(command_response.json())

# 3. Use AI assistant
ai_response = requests.post('http://localhost:7681/ai/assistant/generate', json={
    "prompt": "How do I create a Python function?",
    "context": {"session_id": session_id}
})
print(ai_response.json())

# 4. Multilingual support
translation_response = requests.post('http://localhost:7681/ai/chatgpt/translate', json={
    "text": "Hello world",
    "target_language": "es"
})
print(translation_response.json())
```

### File Operations Example

```python
# List directory
list_response = requests.get('http://localhost:7681/fs/list/home/user/Documents')
print("Directory contents:", list_response.json())

# Read a file
read_response = requests.get('http://localhost:7681/fs/read/home/user/Documents/notes.txt')
print("File content:", read_response.json())

# Write to a file
write_response = requests.post('http://localhost:7681/fs/write', json={
    "path": "/home/user/Documents/new_file.txt",
    "content": "This is new content",
    "backup": True
})
print("Write result:", write_response.json())
```

### WebSocket Terminal Example

```javascript
const ws = new WebSocket('ws://localhost:7681/arcade/ws');

ws.onopen = function() {
    console.log('Connected to Arcade Terminal');
};

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
};

// Send a command
ws.send(JSON.stringify({
    type: 'command',
    command: 'What can you help me with?',
    language: 'en'
}));
```

---

## Authentication

For production deployments, include API key in request headers:

```
Authorization: Bearer your-api-key
X-API-Key: your-api-key
```

## Rate Limiting

- AI requests: 100 per minute
- File operations: 1000 per minute
- Terminal commands: 500 per minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1640995200
```

## Versioning

API versioning follows semantic versioning. Current version: `v2.0.0`

Include version in Accept header:
```
Accept: application/vnd.arcade.v2+json
```
