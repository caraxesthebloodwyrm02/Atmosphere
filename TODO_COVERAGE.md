# 🧭 Coverage Quest Log — Atmosphere Audio

This file tracks fixes and testing milestones needed to reach **80%+ coverage** across the codebase.

_Last updated: 2025-11-11_


## 🎯 Immediate Fixes (Blocking Bugs)
These must be resolved before new tests can pass.

- [ ] **visualization.py** — fix `min(delays)` precedence bug.
- [ ] **visualization.py / spatial_audio_visualizer.py** — add `matplotlib.use("Agg")` for headless testing.
- [ ] **EchoesAssistantV2** — support injected `client` parameter.
- [ ] **Security.create_user** — handle both dict and model inputs.
- [ ] **JWT TokenData** — add `type` field, fix expiration check.
- [ ] **FastAPI dependencies** — correct `Depends` and `require_role` usage.
- [ ] **APIKeyManager** — prevent seeding defaults on init.
- [ ] **RateLimiter** — fix `remaining` calculation (use `limit - used`).


## 🧪 Priority 1 — Fix + Retest
Once the above are green, re-run `pytest` and ensure all failing tests pass.

- [ ] `tests/test_security_module.py` 
- [ ] `tests/test_reverb.py` 
- [ ] `tests/test_delay.py` 
- [ ] `tests/test_visualization.py` 


## 🧬 Priority 2 — Add Targeted Unit Tests
Focus on large or low-coverage modules.

| Module | Current | Goal | Notes |
|--------|----------|------|-------|
| `core/security.py` | 59% | 85% | Users, JWTs, API keys, rate limits |
| `echo/core/core.py` | 23% | 75% | Assistant flows, RAG logic, error paths |
| `delay/core/delay_essence.py` | 22% | 70% | Param boundaries, mocked DSP paths |
| `reverb/core/spatial_audio_visualizer.py` | 31% | 75% | HRTF, delay matrix, plot generation |
| `routing/core/visualization.py` | 11% | 60% | Edge creation, density scaling |


## 🌐 Priority 3 — Integration & Pipeline Tests
Broader coverage from connecting the audio subsystems.

- [ ] End-to-end audio pipeline (Echo → Delay → Reverb)
- [ ] Error handling and recovery scenarios
- [ ] Configurable pipeline parameters (sample rate, buffer size)


## 🪄 Automation & Tools
Integrate these utilities for long-term coverage tracking.

- [ ] **Coverage Map** (`coverage_map.py show/update`)
- [ ] **Coverage Compass** (`compass.py dashboard`)
- [ ] Add `matplotlib.use("Agg")` in `tests/conftest.py` 
- [ ] Automate `pytest --cov` run in CI


## 🧘‍♂️ Coverage Milestones
Track progress visually and celebrate wins.

- [ ] 50% — Core tests fixed
- [ ] 60% — Security + Delay solid
- [ ] 70% — Visualizations stable
- [ ] 80% — Echo pipeline complete 🏔️ Summit reached
- [ ] 85% — Bonus goal: mutation-safe


---

🗺️ *Keep this file alive:* update it after each `pytest --cov` run.  
When you reach the Summit, consider adding mutation testing or fuzzing as the next frontier.
