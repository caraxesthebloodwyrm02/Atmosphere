# Test Coverage Improvement Plan

## Current Status
- **Overall Coverage**: 31.72%
- **CI Gate**: 30% (temporary)
- **Target**: 80% overall coverage

## Module Coverage Breakdown

| Module | Current | Target | Priority | Status |
|--------|---------|--------|----------|---------|
| echo/core/core.py | 0% | 80% | 🔴 Critical | 🔄 In Progress |
| echo/core/knowledge.py | 0% | 80% | 🔴 Critical | ⏳ Pending |
| echo/core/knowledge_graph.py | 0% | 80% | 🔴 Critical | ⏳ Pending |
| reverb/services/delay_service.py | 28% | 80% | 🟡 High | ⏳ Pending |
| reverb/services/echo_service.py | 24% | 80% | 🟡 High | ⏳ Pending |
| reverb/services/reverb_service.py | 42% | 80% | 🟡 High | ⏳ Pending |
| delay/core/delay_essence.py | 40% | 90% | 🟡 High | ⏳ Pending |
| delay/core/echoes_essence.py | 58% | 90% | 🟡 High | ⏳ Pending |

## Phase 1: Foundation (Weeks 1-2)
- [x] Set up coverage tracking
- [ ] Focus on echo/core modules (highest impact)
- [ ] Add basic unit tests for all public functions
- [ ] Mock external dependencies

## Phase 2: Core Coverage (Weeks 3-6)
- [ ] Improve reverb/services coverage
- [ ] Add integration tests
- [ ] Property-based testing with hypothesis

## Phase 3: Advanced Testing (Weeks 7-10)
- [ ] Performance testing
- [ ] Edge case coverage
- [ ] Raise CI gate to 80%

## Quick Wins Strategy

### 1. Start with Pure Functions
- Functions without external dependencies
- Easy to test with simple inputs/outputs
- Highest ROI for coverage

### 2. Mock Complex Dependencies
- Network calls
- File I/O operations
- External APIs

### 3. Test Error Paths
- Exception handling
- Invalid inputs
- Edge cases

## Daily Checklist
- [ ] Run tests locally before pushing
- [ ] Check coverage report after each PR
- [ ] Update this tracking document
- [ ] Address any coverage regressions

## Tools & Commands
```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Check specific module coverage
pytest --cov=src.echo.core --cov-report=term

# Generate HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

## Success Metrics
- All new code has 90%+ coverage
- Overall project coverage ≥ 80%
- Zero failing tests in CI
- All PRs show coverage improvement

---
*Last updated: 2025-11-05*
*Next review: 2025-11-06*
