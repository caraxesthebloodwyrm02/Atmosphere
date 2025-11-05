@echo off
REM Local testing script for Atmosphere project (Windows)
REM Ensures tests pass locally before pushing to CI

setlocal enabledelayedexpansion

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..

cd /d "%PROJECT_ROOT%"

echo [INFO] Starting local test run...
echo [INFO] Project root: %PROJECT_ROOT%

REM Check if virtual environment is active
if "%VIRTUAL_ENV%"=="" (
    echo [WARNING] No virtual environment detected. Activating .venv...
    if exist ".venv\Scripts\activate.bat" (
        call .venv\Scripts\activate.bat
    ) else if exist ".venv\bin\activate.bat" (
        call .venv\bin\activate.bat
    ) else (
        echo [ERROR] Virtual environment not found. Please run: python -m venv .venv
        exit /b 1
    )
)

echo [INFO] Using Python: %PYTHON%
python --version

REM Install/update dependencies
echo [INFO] Installing dependencies...
pip install -q -e . >nul 2>&1
pip install -q pytest pytest-cov >nul 2>&1

REM Run linting (if available)
echo [INFO] Running code quality checks...

REM Check for black
where black >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Running black...
    black --check --diff . >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Code formatting ^(black^) passed
    ) else (
        echo [ERROR] Code formatting issues found. Run 'black .' to fix.
        echo Run with --no-lint to skip formatting checks
        exit /b 1
    )
) else (
    echo [WARNING] black not installed, skipping formatting check
)

REM Check for isort
where isort >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Running isort...
    isort --check-only --diff . >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Import sorting ^(isort^) passed
    ) else (
        echo [ERROR] Import sorting issues found. Run 'isort .' to fix.
        exit /b 1
    )
) else (
    echo [WARNING] isort not installed, skipping import sorting check
)

REM Check for flake8
where flake8 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Running flake8...
    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Linting ^(flake8^) passed
    ) else (
        echo [ERROR] Linting issues found.
        exit /b 1
    )
) else (
    echo [WARNING] flake8 not installed, skipping linting check
)

REM Run tests with coverage
echo [INFO] Running tests with coverage...

REM Set coverage threshold (same as CI)
set COVERAGE_THRESHOLD=50

REM Run pytest with coverage
python -m pytest tests/ --cov=src --cov-report=term --cov-report=html:htmlcov --cov-report=xml --cov-fail-under=%COVERAGE_THRESHOLD% -v --maxfail=1
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] All tests passed with coverage ^≥ %COVERAGE_THRESHOLD%%%
) else (
    echo [ERROR] Tests failed or coverage below %COVERAGE_THRESHOLD%%%
    echo [INFO] Coverage report generated in htmlcov\index.html
    exit /b 1
)

REM Check for security vulnerabilities (if bandit is available)
where bandit >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Running security checks...
    bandit -r src/ -f json -o bandit-report.json >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo [SUCCESS] Security checks passed
    ) else (
        echo [WARNING] Security issues found. Check bandit-report.json
    )
) else (
    echo [WARNING] bandit not installed, skipping security check
)

REM Check if we're in a git repository
git rev-parse --git-dir >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [INFO] Git repository detected
    
    REM Check for uncommitted changes
    git status --porcelain | findstr /r "." >nul
    if %ERRORLEVEL% EQU 0 (
        echo [WARNING] You have uncommitted changes
        git status --short
    ) else (
        echo [SUCCESS] Working directory is clean
    )
) else (
    echo [WARNING] Not in a git repository
)

REM Summary
echo.
echo [SUCCESS] Local testing completed successfully!
echo.
echo Summary:
echo   ✓ Code quality checks passed
echo   ✓ Tests passed with coverage ^≥ %COVERAGE_THRESHOLD%%%
echo   ✓ Ready to push to CI
echo.
echo Next steps:
echo   1. Review any warnings above
echo   2. Commit your changes: git add . ^&^& git commit
echo   3. Push to remote: git push origin main
echo.
echo Coverage report: file:///%PROJECT_ROOT%/htmlcov/index.html

pause
