# ─────────────────────────────────────────────
# FiberMind Analytics - Dockerfile
# Multi-stage build: dev → prod
# ─────────────────────────────────────────────

# === Stage 1: Base ===
FROM python:3.13-slim AS base
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System dependencies for matplotlib and pyotdr
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# === Stage 2: Dependencies ===
FROM base AS deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# === Stage 3: Production ===
FROM base AS production
COPY --from=deps /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application
COPY pyproject.toml .
COPY src/ src/
COPY scripts/ scripts/

# Install the package
RUN pip install --no-cache-dir -e .

# Default entrypoint: MCP Server
CMD ["python", "-m", "src.infrastructure.mcp.server"]

# === Stage 4: Full (API + Dashboard) ===
FROM base AS full
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir fastapi uvicorn[standard] pydantic streamlit

COPY pyproject.toml .
COPY src/ src/
COPY scripts/ scripts/
RUN pip install --no-cache-dir -e .
