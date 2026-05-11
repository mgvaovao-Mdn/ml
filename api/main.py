# -*- coding: utf-8 -*-
"""
FastAPI application entry point.

Startup loads all dialect pipelines (models pinned to GPU memory).
Each request reuses the pre-loaded pipeline — zero cold start per request.

Run:
    uvicorn api.main:app --host 0.0.0.0 --port 8000
"""
from __future__ import annotations
import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("mgvaovao.api")

_STATIC_DIR = Path(__file__).parent.parent / "ui" / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    from mgvaovao.core.config import DIALECTS
    from mgvaovao.pipeline import MalagasyPipeline

    log.info("Loading pipelines for all dialects…")
    app.state.pipelines: dict[str, MalagasyPipeline] = {}

    for dialect in DIALECTS:
        log.info(f"  Loading [{dialect}]…")
        app.state.pipelines[dialect] = MalagasyPipeline(dialect)
        log.info(f"  [{dialect}] ready")

    log.info("All pipelines loaded — API is ready.")
    yield
    app.state.pipelines.clear()
    log.info("Pipelines released.")


app = FastAPI(
    title="MGVaovao API",
    description=(
        "Malagasy multilingual audio translation pipeline.\n\n"
        "**REST flow**: POST audio/text → Malagasy speech\n\n"
        "**WebSocket flow**: `ws://<host>/ws/stream/{dialect}` → "
        "stream Float32 PCM → real-time VAD → pipeline → result JSON\n\n"
        "Supports 4 Malagasy dialects: `plt_latn`, `betsileo`, `betsimisaraka`, `sakalava`."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from .routes import health, dialects, translate, stream  # noqa: E402

app.include_router(health.router,    tags=["Health"])
app.include_router(dialects.router,  prefix="/dialects",  tags=["Dialects"])
app.include_router(translate.router, prefix="/translate",  tags=["Translate"])
app.include_router(stream.router,    prefix="/ws",         tags=["Stream"])

# Serve the real-time UI at /live (index.html + JS)
if _STATIC_DIR.is_dir():
    app.mount("/live", StaticFiles(directory=str(_STATIC_DIR), html=True), name="static")
