from fastapi import APIRouter, HTTPException, Request
from mgvaovao.core.schemas import HealthResponse, ReadyResponse

from ..quotas import COMPTEURS

router = APIRouter()


@router.get("/health", response_model=HealthResponse, summary="Liveness probe")
def health():
    return HealthResponse(status="ok")


@router.get("/ready", response_model=ReadyResponse, summary="Readiness probe — are models loaded?")
def ready(request: Request):
    pipelines = getattr(request.app.state, "pipelines", {})
    models_ready = getattr(request.app.state, "models_ready", False)
    if not models_ready:
        raise HTTPException(status_code=503, detail="Models still loading")
    return ReadyResponse(
        ready=True,
        loaded_dialects=list(pipelines.keys()),
    )


@router.get("/quotas", summary="Usage de la demonstration et limites en vigueur")
def quotas():
    """
    Etat des quotas du processus.

    Sert a deux choses : verifier depuis l'exterieur que les garde-fous sont
    bien actifs avec les valeurs attendues, et voir venir l'epuisement du
    budget avant que la demonstration ne ferme au nez d'un partenaire.

    Le decompte est celui de ce processus seul — voir `api/quotas.py`.
    """
    return COMPTEURS.etat()
