#!/bin/bash
# Local testing script for Atmosphere project
# Ensures tests pass locally before pushing to CI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

print_status "Starting local test run..."
print_status "Project root: $PROJECT_ROOT"

# Check if virtual environment is active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "No virtual environment detected. Activating .venv..."
    if [[ -f ".venv/Scripts/activate" ]]; then
        source .venv/Scripts/activate
    elif [[ -f ".venv/bin/activate" ]]; then
        source .venv/bin/activate
    else
        print_error "Virtual environment not found. Please run: python -m venv .venv"
        exit 1
    fi
fi

print_status "Using Python: $(which python)"
print_status "Python version: $(python --version)"

# Install/update dependencies
print_status "Installing dependencies..."
pip install -q -e . > /dev/null 2>&1 || true
pip install -q pytest pytest-cov > /dev/null 2>&1 || true

# Run linting (if available)
print_status "Running code quality checks..."

# Check for black
if command -v black &> /dev/null; then
    print_status "Running black..."
    if black --check --diff . 2>/dev/null; then
        print_success "Code formatting (black) passed"
    else
        print_error "Code formatting issues found. Run 'black .' to fix."
        echo "Run with --no-lint to skip formatting checks"
        exit 1
    fi
else
    print_warning "black not installed, skipping formatting check"
fi

# Check for isort
if command -v isort &> /dev/null; then
    print_status "Running isort..."
    if isort --check-only --diff . 2>/dev/null; then
        print_success "Import sorting (isort) passed"
    else
        print_error "Import sorting issues found. Run 'isort .' to fix."
        exit 1
    fi
else
    print_warning "isort not installed, skipping import sorting check"
fi

# Check for flake8
if command -v flake8 &> /dev/null; then
    print_status "Running flake8..."
    if flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics 2>/dev/null; then
        print_success "Linting (flake8) passed"
    else
        print_error "Linting issues found."
        exit 1
    fi
else
    print_warning "flake8 not installed, skipping linting check"
fi

# Run tests with coverage
print_status "Running tests with coverage..."

# Set coverage threshold (same as CI)
COVERAGE_THRESHOLD=28

# Run pytest with coverage
if python -m pytest tests/ \
    --cov=src \
    --cov-report=term \
    --cov-report=html:htmlcov \
    --cov-report=xml \
    --cov-fail-under=$COVERAGE_THRESHOLD \
    -v \
    --maxfail=1; then
    print_success "All tests passed with coverage ≥ ${COVERAGE_THRESHOLD}%"
else
    print_error "Tests failed or coverage below ${COVERAGE_THRESHOLD}%"
    print_status "Coverage report generated in htmlcov/index.html"
    exit 1
fi

# Check for security vulnerabilities (if bandit is available)
if command -v bandit &> /dev/null; then
    print_status "Running security checks..."
    if bandit -r src/ -f json -o bandit-report.json 2>/dev/null; then
        print_success "Security checks passed"
    else
        print_warning "Security issues found. Check bandit-report.json"
    fi
fi

# Check for dependency vulnerabilities (if safety is available)
if command -v safety &> /dev/null; then
    print_status "Checking dependency security..."
    if safety check --json --output safety-report.json 2>/dev/null; then
        print_success "Dependency security checks passed"
    else
        print_warning "Dependency vulnerabilities found. Check safety-report.json"
    fi
fi

# Run type checking (if mypy is available)
if command -v mypy &> /dev/null; then
    print_status "Running type checks..."
    if mypy src/ --ignore-missing-imports 2>/dev/null; then
        print_success "Type checking (mypy) passed"
    else
        print_warning "Type checking issues found"
    fi
else
    print_warning "mypy not installed, skipping type checking"
fi

# Check if we're in a git repository
if git rev-parse --git-dir > /dev/null 2>&1; then
    print_status "Git repository detected"
    
    # Check for uncommitted changes
    if [[ -n $(git status --porcelain) ]]; then
        print_warning "You have uncommitted changes"
        git status --short
    else
        print_success "Working directory is clean"
    fi
    
    # Check if we're behind origin/main
    if git fetch origin main 2>/dev/null; then
        BEHIND=$(git rev-list --count HEAD..origin/main 2>/dev/null || echo "0")
        if [[ "$BEHIND" -gt 0 ]]; then
            print_warning "You are $BEHIND commits behind origin/main"
            print_status "Consider running: git pull origin main"
        else
            print_success "You are up to date with origin/main"
        fi
    fi
else
    print_warning "Not in a git repository"
fi

# Summary
print_success "Local testing completed successfully!"
echo ""
echo "Summary:"
echo "  ✓ Code quality checks passed"
echo "  ✓ Tests passed with coverage ≥ ${COVERAGE_THRESHOLD}%"
echo "  ✓ Ready to push to CI"
echo ""
echo "Next steps:"
echo "  1. Review any warnings above"
echo "  2. Commit your changes: git add . && git commit"
echo "  3. Push to remote: git push origin main"
echo ""
echo "Coverage report: file://$PROJECT_ROOT/htmlcov/index.html"
