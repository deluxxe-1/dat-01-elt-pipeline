"""FastAPI entry point exposing health and pipeline trigger endpoints."""

from fastapi import FastAPI, Query

from .config import settings
from .pipeline import run_pipeline

app = FastAPI(title=settings.api_title, version="0.1.0")


@app.get("/health")
def health() -> dict:
    """Liveness probe used by Docker health checks and orchestrators."""

    return {"status": "ok", "service": "elt-pipeline"}


@app.post("/api/pipeline/run")
def trigger_pipeline(
    count: int | None = Query(default=None, ge=0, description="Records to generate"),
    seed: int | None = Query(default=None, description="Deterministic source seed"),
) -> dict:
    """Trigger one in-process ELT run and return per-layer row counts."""

    return run_pipeline(count=count, seed=seed)
