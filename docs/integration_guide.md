# Integration Guide: Arcade Optimizer + API Client

This guide describes how to integrate the `arcade_optimizer` and `api_client` domains inside Atmosphere, including environment setup, imports, and running the real integration test.

## 1. Environment Setup

### 1.1. Project Layout

- Monorepo root: `Atmosphere/`
- Domains root: `Atmosphere/atmosphere_domains/`
- Relevant domains:
  - `atmosphere_domains/arcade_optimizer/`
  - `atmosphere_domains/api_client/`

### 1.2. Python Path

For standalone scripts (outside pytest), ensure `atmosphere_domains` is on `sys.path`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "atmosphere_domains"))
```

Pytest-based tests in each domain already configure `sys.path` via domain-level `conftest.py`.

### 1.3. Environment Variables

The API Client domain requires an OpenAI API key for real HTTP calls:

- `OPENAI_API_KEY` – OpenAI secret key.

In development, load from a `.env` file or your shell environment. CI tests are fully mocked and must **not** hit the real API.

## 2. Imports and Public APIs

### 2.1. Arcade Optimizer

Key types and engine:

```python
from atmosphere_domains.arcade_optimizer.src.core.arcade_optimizer import (
    ArcadeOptimizer,
)
from atmosphere_domains.arcade_optimizer.types import (
    Skill,
    UserProfile,
    OptimizationRequest,
)
```

Core usage pattern:

```python
optimizer = ArcadeOptimizer()
request = OptimizationRequest(
    target_data={
        "available_skills": [...],
        "user_profile": user_profile,
        "goal_skills": ["async-python"],
    },
)
response = optimizer.optimize(request)

# response.learning_path is a LearningPathResult or None
```

### 2.2. API Client

Engine and request/response types:

```python
from atmosphere_domains.api_client.src.core.engine import APIClientEngine
from atmosphere_domains.api_client.types import APIRequest
```

Basic usage pattern (async):

```python
request = APIRequest(
    method="POST",
    endpoint="/chat",
    data={
        "prompt": "Explain this learning path...",
        "system": "You are a concise educational advisor.",
        "max_tokens": 100,
    },
)

async with APIClientEngine(provider="openai") as engine:
    response = await engine.process_request(request)
```

## 3. Real Integration Test

A reference integration script lives at the repo root:

- `test_real_integration.py`

### 3.1. What It Does

1. Builds a small curriculum graph using `Skill` and `UserProfile`.
1. Calls `ArcadeOptimizer.optimize(...)` to compute an optimized learning path.
1. Builds a prompt summarizing the path.
1. Uses `APIClientEngine` to call OpenAI and generate a short explanation.
1. Prints:
   - Optimization strategy and convergence status.
   - Learning path steps (if generated).
   - AI explanation and token usage.

### 3.2. Running the Integration Test

From the repo root (`Atmosphere/`):

```bash
python test_real_integration.py
```

Expected behavior:

- If `OPENAI_API_KEY` is set correctly:
  - You see a real AI explanation and token usage.
- If the key is missing or invalid:
  - The script prints an API configuration warning.
  - Arcade optimization still runs locally.

## 4. Testing Domains Individually

### 4.1. Arcade Optimizer Tests

From `Atmosphere/atmosphere_domains/arcade_optimizer`:

```bash
python -m pytest
```

### 4.2. API Client Tests

From `Atmosphere/atmosphere_domains/api_client`:

```bash
python -m pytest
```

All API Client tests are fully mocked; they do not require an OpenAI key.

## 5. Integration in an Orchestrator

To integrate these domains into a higher-level orchestrator:

1. Collect user goal and context.
1. Construct `Skill` graph and `UserProfile`.
1. Call `ArcadeOptimizer` to compute an optimal learning path.
1. Summarize the path into a concise prompt.
1. Call `APIClientEngine` to generate explanations, tips, or next actions.

This pattern serves as the blueprint for future domains (RAG, Echoes, routing) to plug into the orchestrator.
