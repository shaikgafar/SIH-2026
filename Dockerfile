# ==============================================================================
# Multi-Stage Production Dockerfile for LunaAlign (SIH26166)
# Stage 1: Build React/Vite Frontend
# Stage 2: Python FastAPI Backend + Headless OpenCV
# ==============================================================================

# --- Stage 1: Build Frontend ---
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# --- Stage 2: Production Python Backend & Static Serving ---
FROM python:3.11-slim AS production

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8001

# Install system dependencies required by OpenCV headless and SciPy
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python requirements
COPY lunar_align/backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application code
COPY lunar_align/backend/app ./app

# Copy built frontend assets from Stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Expose server port
EXPOSE 8001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/health || exit 1

# Start unified FastAPI server (serves both API & Frontend SPA)
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
