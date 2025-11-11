# Atmosphere Test Suite

This document outlines the comprehensive test suite for the Atmosphere project, including what tests exist, what should be added, and how to configure pytest properly.

## Current Test Coverage

### ✅ Existing Tests (Comprehensive)

1. **Delay Module** (`Delay/test_delay_comprehensive.py`)
   - Data model validation
   - Parameter clamping and validation
   - Signal processing with all delay types
   - Edge cases and error handling
   - Integration tests for complex configurations

2. **i_o Module** (`i_o/test_io_comprehensive.py`, `i_o/test_smart_optimizer.py`)
   - FastAPI endpoint testing
   - Data transmission workflows
   - Background processing
   - Error handling
   - Smart code optimization

3. **Mental Load Balancer** (`mental-load-balancer/test_mental_load_balancer.py`)
   - Metrics collection and analysis
   - Joke engine functionality
   - Load monitoring logic
   - Configuration management
   - GUI component mocking

### ❌ Missing Tests (High Priority - ADD)

1. **Compass Tools** (`test_compass_tools.py`) - *NEW*
   - Data model testing (Module, Phase, OracularState)
   - CLI argument parsing
   - JSON loading and merging
   - Rendering functions
   - Interactive mode logic

2. **Core Atmosphere Audio** (`src/atmosphere_audio/`)
   - Main audio processing pipeline
   - Network integration
   - Security modules
   - Echo and reverb algorithms

3. **Scripts** (`scripts/`)
   - Data collection utilities
   - Configuration helpers
   - CLI tools

### 🟡 Tests to Review/Remove (Low Priority)

1. **Legacy Tests** - Check for outdated or redundant tests
2. **Flaky Tests** - Identify and fix tests that fail intermittently
3. **Slow Tests** - Mark with `@pytest.mark.slow` and allow skipping

## Recommended Test Structure

```
tests/
├── test_compass_tools.py          # NEW - Compass CLI tools
├── test_core_audio.py             # NEW - Core audio processing
├── test_scripts.py                # NEW - Utility scripts
└── existing_tests/
    ├── Delay/test_delay_comprehensive.py
    ├── i_o/test_io_comprehensive.py
    ├── i_o/test_smart_optimizer.py
    └── mental-load-balancer/test_mental_load_balancer.py

# Module-specific tests alongside code
Delay/test_delay_comprehensive.py
i_o/test_*.py
mental-load-balancer/test_*.py
```

## Pytest Configuration

### pytest.ini (Root Level)
```ini
[tool:pytest]
testpaths = tests Delay i_o mental-load-balancer
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --verbose
    --tb=short
    --cov=src
    --cov=Delay
    --cov=i_o
    --cov=mental-load-balancer
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=50
    --strict-markers
    --disable-warnings
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    smoke: marks tests as smoke tests
    e2e: end-to-end tests
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    ignore::UserWarning
```

### pyproject.toml (Modern Alternative)
```toml
[tool.pytest.ini_options]
minversion = "6.0"
addopts = [
    "--verbose", "--tb=short",
    "--cov=src", "--cov=Delay", "--cov=i_o", "--cov=mental-load-balancer",
    "--cov-report=term-missing", "--cov-report=html:htmlcov",
    "--cov-fail-under=50", "--strict-markers"
]
testpaths = ["tests", "Delay", "i_o", "mental-load-balancer"]
markers = [
    "slow: slow tests", "integration: integration tests",
    "unit: unit tests", "smoke: smoke tests", "e2e: end-to-end tests"
]
```

## Running Tests

### All Tests
```bash
pytest
```

### Specific Modules
```bash
pytest Delay/test_delay_comprehensive.py
pytest i_o/
pytest mental-load-balancer/
```

### Coverage Only
```bash
pytest --cov=src --cov-report=html
```

### Skip Slow Tests
```bash
pytest -m "not slow"
```

### Only Smoke Tests
```bash
pytest -m smoke
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)
- Test individual functions/classes
- Mock external dependencies
- Fast execution (< 100ms each)

### Integration Tests (`@pytest.mark.integration`)
- Test component interactions
- May use real dependencies
- Medium execution time

### Smoke Tests (`@pytest.mark.smoke`)
- Basic functionality verification
- Run after deployments
- Fast execution

### End-to-End Tests (`@pytest.mark.e2e`)
- Full workflow testing
- May require external services
- Slow execution

### Slow Tests (`@pytest.mark.slow`)
- Performance tests
- Complex integrations
- Can be skipped in CI

## Best Practices

### Test Organization
- One test class per module/feature
- Descriptive test method names: `test_should_do_something_when_condition`
- Use fixtures for common setup
- Group related tests in classes

### Mocking Strategy
- Mock external APIs and services
- Use `unittest.mock` for patching
- Mock GUI components for headless testing
- Mock file I/O for deterministic tests

### Coverage Goals
- **Statements**: > 80%
- **Branches**: > 70%
- **Functions**: > 90%
- Focus on critical paths

### CI/CD Integration
- Run smoke tests on every commit
- Run full suite on PRs
- Generate coverage reports
- Fail build if coverage < 50%

## Immediate Action Items

### HIGH PRIORITY - ADD
1. **Compass Tools Tests** - Complete test suite for CLI tools
2. **Core Audio Tests** - Test main audio processing pipeline
3. **Script Tests** - Test utility scripts and data collection

### MEDIUM PRIORITY - IMPROVE
1. **Mock Strategy** - Better mocking for GUI/file operations
2. **Test Performance** - Optimize slow tests
3. **Coverage Reports** - Set up automated coverage tracking

### LOW PRIORITY - MAINTAIN
1. **Test Cleanup** - Remove duplicate/redundant tests
2. **Documentation** - Update test documentation
3. **CI Integration** - Improve automated testing pipeline

## Example Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock

class TestCompassTools:
    """Test Compass CLI functionality."""

    @pytest.fixture
    def sample_state(self):
        """Fixture providing sample OracularState."""
        return OracularState(coverage=50, target=80, ...)

    def test_data_model_creation(self, sample_state):
        """Test data model instantiation."""
        assert sample_state.coverage == 50

    @patch('compass.console')
    def test_rendering_functions(self, mock_console, sample_state):
        """Test rendering with mocked console."""
        render_header(sample_state)
        mock_console.print.assert_called()

    @pytest.mark.integration
    def test_json_workflow(self, tmp_path):
        """Test complete JSON load/save workflow."""
        # Test implementation
        pass

    @pytest.mark.slow
    def test_large_data_processing(self):
        """Test processing of large datasets."""
        # Test implementation
        pass
```

This comprehensive test suite ensures the Atmosphere project maintains high code quality and reliability across all modules.
