# AGENTS.md

## Cursor Cloud specific instructions

### Codebase Overview

Atmosphere Audio & Learning System: a Python monorepo combining audio DSP processing (`src/atmosphere_audio/`), an Arcade Terminal with a Learning Companion API (FastAPI on port 7681, `Arcade/`), and supporting tools. No database — file-based JSON storage.

### Known Issues

- **Unresolved merge conflicts**: Many files across the repo contain unresolved git merge conflict markers (`<<<<<<< HEAD` / `=======` / `>>>>>>>`). Affected files include `config/requirements.txt`, `config/requirements-dev.txt`, several test files, source files in `src/delay/`, `src/echo/`, `api/`, `Routing/`, `Reverb/`, and `spatial_audio_visualizer.py`. Use `config/requirements_clean.txt` as the clean reference for core dependencies.
- **pyproject.toml TOML syntax**: The `[tool.coverage.report].exclude_lines` entries contain regex backslashes that must be escaped for valid TOML (e.g., `\\b` not `\b`). This has been fixed on the setup branch.
- **AdaptiveContentEngine incomplete**: `Arcade/learning_companion/adaptive_content_engine.py` references undefined methods (`_route_emotional_content_path`, `_generate_adaptation_reasoning`, etc.), so `POST /learning/session/start` returns a 500 error. Other Learning Companion endpoints (status, topics, progress, interact) work.
- **PowerShell not available**: The terminal handler expects `pwsh`. On Linux dev environments, a symlink `Arcade/terminal/pwsh -> /bin/bash` is created as a workaround.

### Running the Application

```bash
# Start the Arcade Terminal server (from Arcade/api/ directory)
cd Arcade/api && python -m uvicorn server:app --host 0.0.0.0 --port 7681 --log-level info
```

Key API endpoints:
- `GET /arcade/status` — server status
- `GET /learning/status` — learning companion status
- `GET /learning/topics` — available topics
- `GET /learning/progress/{learner_id}` — learner progress
- `GET /docs` — Swagger UI

### Running Tests

```bash
# Run tests (excluding files with merge conflicts)
python -m pytest tests/ \
  --ignore=tests/test_basic.py \
  --ignore=tests/test_network_basic.py \
  --ignore=tests/test_delay_demo.py \
  --ignore=tests/test_security_property_simple.py \
  --ignore=tests/test_security.py \
  -q --tb=short
```

Note: Some test files import from source files with merge conflicts and will fail to collect. The Arcade tests can be run separately: `python -m pytest Arcade/tests/ -q`.

### Lint Commands

See `README.md` "Code Quality" section. Run from workspace root:
- `python -m flake8 src/atmosphere_audio/ --max-line-length=120`
- `python -m black --check src/atmosphere_audio/`
- `python -m isort --check-only src/atmosphere_audio/`
- `PYTHONPATH="" python -m mypy src/atmosphere_audio/ --ignore-missing-imports --no-strict-optional --explicit-package-bases`

### Environment Notes

- Python 3.12 is used. `PYTHONPATH` must include `/workspace/src` for `atmosphere_audio` imports when not using `pip install -e .`.
- User-installed binaries go to `~/.local/bin` — ensure it's on `PATH`.
- The editable install (`pip install -e .`) requires the pyproject.toml TOML escaping fix.
