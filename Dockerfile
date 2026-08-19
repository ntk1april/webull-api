# syntax=docker/dockerfile:1
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY server.py .
# conf/ dir is NOT copied – token is managed at runtime via env vars

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Gunicorn with Uvicorn workers – production-grade ASGI
# Shell form is required so $PORT env var (set by Render) expands at runtime
CMD gunicorn server:app \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 2 \
    --timeout 120 \
    --log-level info

