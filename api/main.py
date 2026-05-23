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
import os
from contextlib import asynccontextmanager
from pathlib import Path

# ── Redirect HuggingFace and torch caches BEFORE any library imports ──────────
# Must happen here so that transformers, torch.hub, datasets all pick up the
# correct cache root (important when C: is full and caches live on D:).
def _set_cache_env() -> None:
    from mgvaovao.core.config import Settings
    s = Settings()
    hf = str(s.hf_cache_dir)
    os.environ.setdefault("HF_HOME", hf)
    os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(s.hf_cache_dir / "hub"))
    os.environ.setdefault("TORCH_HOME", str(s.torch_hub_dir.parent))
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")
    Path(hf).mkdir(parents=True, exist_ok=True)
    Path(s.torch_hub_dir).mkdir(parents=True, exist_ok=True)

_set_cache_env()
# ─────────────────────────────────────────────────────────────────────────────

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


def _load_models_bg(app: FastAPI) -> None:
    """Load all ML models in a background thread so uvicorn opens port 8080 immediately."""
    import threading
    try:
        from mgvaovao.core.config import DIALECTS, settings
        from mgvaovao.models.vad import SileroVAD
        from mgvaovao.models.asr import WhisperASR
        from mgvaovao.models.translator import NLLBTranslator
        from mgvaovao.models.tts import MalagasyTTS
        from mgvaovao.pipeline import MalagasyPipeline

        log.info("Loading shared VAD (CPU)…")
        shared_vad = SileroVAD(
            threshold=settings.vad_threshold,
            min_speech_ms=settings.vad_min_speech_ms,
            min_silence_ms=settings.vad_min_silence_ms,
            speech_pad_ms=settings.vad_speech_pad_ms,
        )

        log.info(f"Loading shared Whisper ({settings.whisper_model_size}) on {settings.device}…")
        shared_asr = WhisperASR()

        log.info(f"Loading shared NLLB on {settings.device}…")
        shared_translator = NLLBTranslator("plt_latn")

        _loaded_tts: dict[str, MalagasyTTS] = {}
        for dialect in DIALECTS:
            ckpt = settings.tts_checkpoint(dialect) / "final"
            if ckpt.is_dir():
                log.info(f"  TTS [{dialect}] — loading fine-tuned checkpoint…")
                tts = MalagasyTTS(dialect)
            else:
                if "base" not in _loaded_tts:
                    log.info("  TTS [base] — loading facebook/mms-tts-mlg…")
                    _loaded_tts["base"] = MalagasyTTS("plt_latn")
                tts = _loaded_tts["base"]
                log.info(f"  TTS [{dialect}] — sharing base model (no checkpoint yet)")

            app.state.pipelines[dialect] = MalagasyPipeline(
                dialect,
                vad=shared_vad,
                asr=shared_asr,
                translator=shared_translator,
                tts=tts,
            )
            log.info(f"  Pipeline [{dialect}] ready")

        app.state.models_ready = True
        log.info("All pipelines loaded — API is ready.")
    except Exception:
        log.exception("Model loading failed")
        app.state.models_ready = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    import threading
    # Initialise state immediately so /health responds before models are loaded
    app.state.pipelines = {}
    app.state.models_ready = False

    # Load models in a daemon thread — uvicorn opens port 8080 without waiting
    t = threading.Thread(target=_load_models_bg, args=(app,), daemon=True)
    t.start()
    log.info("Model loading started in background thread — port 8080 is open.")

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
