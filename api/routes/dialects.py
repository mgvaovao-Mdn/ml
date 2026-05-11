from fastapi import APIRouter, Request
from mgvaovao.core.config import DIALECTS, DIALECT_META
from mgvaovao.core.schemas import DialectInfo

router = APIRouter()


@router.get("/", response_model=list[DialectInfo], summary="List available dialects and model status")
def list_dialects(request: Request):
    pipelines = getattr(request.app.state, "pipelines", {})
    return [
        DialectInfo(
            code=d,
            name=DIALECT_META[d]["name"],
            region=DIALECT_META[d]["region"],
            population=DIALECT_META[d]["population"],
            phase=DIALECT_META[d]["phase"],
            model_ready=(d in pipelines),
        )
        for d in DIALECTS
    ]
