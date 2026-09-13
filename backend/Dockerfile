# Multi-stage / Production Dockerfile for FastAPI Backend
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies into wheels
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip wheel --no-cache-dir --no-deps --wheel-dir /app/wheels -r requirements.txt

# Final Runtime Image
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN groupadd -r ecoroute && useradd -r -g ecoroute ecoroute

# Install runtime dependencies from builder
COPY --from=builder /app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --no-cache-dir /wheels/* && rm -rf /wheels

# Copy application source code
COPY . .

# Ensure uploads directory exists with correct permissions
RUN mkdir -p /app/uploads && chown -R ecoroute:ecoroute /app

USER ecoroute

# Expose FastAPI port
EXPOSE 8000

# Health check
# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1# Start Uvicorn ASGI Server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]