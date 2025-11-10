# Cohesive Fix Plan and Report

## Summary
- Implemented orchestral feature flag (`ECHOES_ORCHESTRAL_ENABLED`) default OFF.
- Conditionally wired orchestral API endpoints and routing helpers.
- Simplified `template_process.py` to a clear demo/utility.
- Fixed lints in `core/orchestral_ai.py` and improved safety with null checks.

## Errors and Warnings Observed
- Missing dependency `pydantic_settings` for `api/config.py`.
- Several Pylint stylistic warnings in `api/config.py` (global usage, shadowing, broad exceptions): narrowed exceptions, lazy logging, parameter rename.
- `api/main.py` has generic exception logging and non-lazy logging: kept scope small; orchestral endpoints are gated.

## Changes Made
- api/config.py: added `orchestral_enabled`, `orchestral_debug`; updated validation and logging format; narrowed exceptions; refactored parameters.
- api/main.py: mounted `/ws/orchestral` and `/orchestral/status` only when flag enabled.
- app/model_router.py: added helpers to route with orchestral when enabled.
- assistant.py: added menu option 8 to run template demo and strategy when flag is enabled.
- core/orchestral_ai.py: resolved 9 lints and added graceful degradation.

## How to Enable Orchestral Features
1. Create/activate venv.
2. Set env var: `ECHOES_ORCHESTRAL_ENABLED=1` (and optionally `ECHOES_ORCHESTRAL_DEBUG=1`).
3. In assistant menu, select option 8 to run demo.
4. API will expose `/orchestral/status` and `/ws/orchestral` when enabled.

## Test Plan
- Run `template_process.main()` and `orchestral_strategy.strategy()` via assistant menu.
- Verify API `/health` and `/orchestral/status` (if enabled).
- Optionally run `scripts/test_orchestral_pipeline.py` to collect outputs, pick top 4 simple/impactful, and (if enabled) route via Routing to Arcade.

## Next Steps
- Ensure dependencies installed (pydantic-settings, fastapi, uvicorn, pandas).
- Add CI lint and smoke tests to guard orchestral endpoints behind the flag.
- Expand test script to persist a JSON result under `Echoes/results/`.

---
Generated: 2025-11-04
