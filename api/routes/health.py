from fastapi import APIRouter, Request
from mgvaovao.core.schemas import HealthResponse, ReadyResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
def health():
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse, summary="Readiness probe — are models loaded?")
def ready(request: Request):
    pipelines = getattr(request.app.state, "pipelines", {})
    return ReadyResponse(
        ready=len(pipelines) > 0,
        loaded_dialects=list(pipelines.keys()),
    )
