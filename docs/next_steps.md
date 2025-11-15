# Next Steps: Routing and Hardening Roadmap

This document outlines the roadmap after completing real implementations for `arcade_optimizer` and `api_client`.

## 1. Tier 4 Completion: Routing Domain (Phase 3A)

### 1.1. Goal

Introduce a simple, robust routing layer that decides which domain(s) to call for a given user request.

### 1.2. Minimal Feature Set

- Map high-level intents to domains, e.g.:
  - Learning path optimization → `arcade_optimizer`
  - AI explanation / chat → `api_client`
  - Knowledge lookup → RAG (mock for now)
  - Memory operations → Echoes (mock for now)
- Implement a small, explicit routing table or rules engine.

### 1.3. Implementation Sketch

- Define a `RouteRequest` type capturing:
  - User query text
  - Optional context (user profile, history, channel)
- Implement a `RoutingEngine` that:
  - Applies simple rules or scores to choose a domain.
  - Returns a `RouteDecision` (target domain + parameters).
- Keep Phase 3A non-acoustic and non-ML (deterministic rules only).

## 2. Optional: Acoustic / Advanced Routing (Phase 3B)

This can be deferred.

Potential enhancements:

- Use speech features or audio metadata for routing decisions.
- Incorporate confidence scores and multi-domain fan-out.
- Add learning-based routing models.

Only tackle this once Tier 4 and Tier 5 are stable.

## 3. Tier 5: Hardening and Quality

Once Arcade + API Client + Routing are in place, focus on making the system production-grade.

### 3.1. Testing and Coverage

- Increase test coverage for:
  - Cross-domain orchestration paths.
  - Failure modes and timeouts.
- Add integration tests that:
  - Exercise routing → arcade → api_client sequences.
  - Verify behavior when one domain fails.

### 3.2. Performance and Observability

- Add timing metrics (e.g. `response_time_ms`) consistently.
- Log domain decisions and key parameters (without sensitive data).
- Measure p95 latency for end-to-end flows.

### 3.3. Type Safety and Tooling

- Introduce stricter type checking (e.g. `mypy`) across domains.
- Enforce consistent enums and dataclasses for shared concepts.
- Add CI checks for style, typing, and tests.

## 4. RAG and Echoes Enhancements

With core compute (Arcade) and communication (API Client) online, the next focus areas are knowledge and memory.

### 4.1. RAG (Retrieval-Augmented Generation)

- Replace mock RAG analyzer with a real vector store and retriever.
- Define clear contracts for:
  - Document ingestion.
  - Query → context retrieval.
  - Metadata and scoring.

### 4.2. Echoes (Memory)

- Evolve from mock storage to a structured memory system.
- Support:
  - Session memory.
  - Long-term user profiles.
  - Domain-specific memory (e.g. routing hints).

## 5. Documentation and Onboarding

- Keep `docs/` updated as architecture evolves.
- Add high-level diagrams for:
  - Domain structure.
  - Orchestrator + routing.
  - Data flow between Arcade, API Client, RAG, and Echoes.

## 6. Guiding Principle

Advance in small, well-tested increments:

1. Make one domain or feature truly solid.
1. Prove integration with a focused test.
1. Document patterns.
1. Only then layer on complexity (routing, RAG, advanced memory).

This keeps the system stable while velocity remains high.
