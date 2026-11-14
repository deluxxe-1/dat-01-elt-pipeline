# syntax=docker/dockerfile:1
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first so the layer is cached across source changes.
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

# Run as a non-root user (security baseline).
RUN useradd --create-home --uid 10001 appuser \
    && mkdir -p /data \
    && chown -R appuser:appuser /data /app
USER appuser

ENV ELT_DATABASE_PATH=/data/elt.db
VOLUME ["/data"]

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

CMD ["uvicorn", "elt_pipeline.main:app", "--host", "0.0.0.0", "--port", "8000"]
