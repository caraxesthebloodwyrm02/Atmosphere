# Atmosphere Arcade - Docker Configuration
# =======================================

# Multi-stage Dockerfile for production deployment
FROM python:3.10-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd --create-home --shell /bin/bash arcade

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM base as production

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/sandbox && \
    chown -R arcade:arcade /app

# Switch to non-root user
USER arcade

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV ARCADE_HOST=0.0.0.0
ENV ARCADE_PORT=7681
ENV ARCADE_SANDBOX_PATH=/app/sandbox

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7681/health || exit 1

# Expose port
EXPOSE 7681

# Start application
CMD ["python", "start_arcade.py"]

# Development stage
FROM base as development

# Install development dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    isort \
    flake8 \
    mypy

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/sandbox && \
    chown -R arcade:arcade /app

# Switch to non-root user
USER arcade

# Environment variables for development
ENV PYTHONUNBUFFERED=1
ENV ARCADE_HOST=0.0.0.0
ENV ARCADE_PORT=7681
ENV ARCADE_DEBUG=true
ENV ARCADE_SANDBOX_PATH=/app/sandbox

# Expose port
EXPOSE 7681

# Start application in development mode
CMD ["python", "start_arcade.py", "--debug"]
