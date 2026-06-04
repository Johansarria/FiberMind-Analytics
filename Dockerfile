# ─────────────────────────────────────────────
# FiberMind Analytics - Dockerfile (Multi-ISP)
# Multi-stage build: dev → full → production
# ─────────────────────────────────────────────

# === Stage 1: Base ===
FROM python:3.13-slim-bookworm AS base

LABEL maintainer="Johan Sarria <johansarria59@gmail.com>"
LABEL description="FiberMind Analytics - FTTH Network Intelligence Platform"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl sqlite3 gosu && \
    rm -rf /var/lib/apt/lists/*

# Python deps (sin dependencias pesadas)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# === Stage 2: Full (API + Dashboard) ===
FROM base AS full

# Web deps (FastAPI + Streamlit)
RUN pip install --no-cache-dir \
    "fastapi>=0.115.0" \
    "uvicorn[standard]>=0.32.0" \
    "streamlit>=1.40.0" \
    "pydantic>=2.0.0" \
    "python-multipart>=0.0.18"

# Código fuente
COPY . .

# Instalar el paquete
RUN pip install -e .

# Directorio de datos multi-ISP
RUN mkdir -p /data

EXPOSE 8000 8501
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]


# === Stage 3: Production (solo API, más liviano) ===
FROM base AS production

COPY src/ ./src/
COPY scripts/ ./scripts/
COPY fibermind.yml ./ 2>/dev/null || true

# Metadata del paquete
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

RUN mkdir -p /data

EXPOSE 8000
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
