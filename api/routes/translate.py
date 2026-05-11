# -*- coding: utf-8 -*-
"""
Translation routes.

POST /translate/audio  — upload WAV/MP3, get Malagasy text + audio back
POST /translate/text   — send text, get Malagasy text + audio back
GET  /translate/audio/{filename} — fetch the synthesised WAV file
"""
from __future__ import annotations
import io
import os
import tempfile

import numpy as np
import torchaudio
import torchaudio.functional as AF
from fastapi import APIRouter, Form, File, HTTPException, Query, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse

from mgvaovao.core.schemas import (
    TranslateAudioResponse,
    TranslateTextRequest,
    TranslateTextResponse,
    LatencyBreakdown,
)
from mgvaovao.pipeline import PipelineResult

router = APIRouter()

TARGET_SR = 16_000


# ── helpers ───────────────────────────────────────────────────────────────

def _get_pipeline(request: Request, dialect: str):
    pipelines = getattr(request.app.state, "pipelines", {})
    if dialect not in pipelines:
        raise HTTPException(404, f"Dialect '{dialect}' not available. "
                                 f"Choose from: {list(pipelines.keys())}")
    return pipelines[dialect]


def _audio_from_bytes(raw: bytes) -> tuple[np.ndarray, int]:
    """Load any audio format → mono float32 numpy array at 16 kHz."""
    wf, sr = torchaudio.load(io.BytesIO(raw))
    if wf.shape[0] > 1:
        wf = wf.mean(0, keepdim=True)
    if sr != TARGET_SR:
        wf = AF.resample(wf, sr, TARGET_SR)
    return wf.squeeze().numpy().astype(np.float32), TARGET_SR


def _audio_url(request: Request, audio_path: str) -> str:
    filename = os.path.basename(audio_path)
    return str(request.url_for("get_audio", filename=filename))


def _latency(result: PipelineResult) -> LatencyBreakdown:
    lms = result.latency_ms
    return LatencyBreakdown(
        vad=lms.get("vad"),
        asr=lms.get("asr"),
        translation=lms["translation"],
        tts=lms["tts"],
        total=lms["total"],
    )


# ── routes ────────────────────────────────────────────────────────────────

@router.post(
    "/audio",
    response_model=TranslateAudioResponse,
    summary="Translate audio → Malagasy speech (VAD + ASR + NLLB + TTS)",
)
async def translate_audio(
    request:  Request,
    file:     UploadFile = File(..., description="Audio file (WAV, MP3, OGG, FLAC…)"),
    dialect:  str        = Form("betsileo", description="Target dialect key"),
    src_lang: str | None = Form(None,       description="Force source lang (fr/en/de/es/it/pt; auto-detect if omitted)"),
):
    pipeline   = _get_pipeline(request, dialect)
    raw        = await file.read()
    audio, sr  = await run_in_threadpool(_audio_from_bytes, raw)
    result     = await run_in_threadpool(pipeline.run_audio, audio, sr, src_lang)

    return TranslateAudioResponse(
        source_text=result.source_text,
        detected_lang=result.detected_lang,
        malagasy_text=result.malagasy_text,
        dialect=result.dialect,
        audio_url=_audio_url(request, result.audio_path),
        latency_ms=_latency(result),
    )


@router.post(
    "/text",
    response_model=TranslateTextResponse,
    summary="Translate text → Malagasy speech (NLLB + TTS, no ASR)",
)
def translate_text(request: Request, body: TranslateTextRequest):
    pipeline = _get_pipeline(request, body.dialect)
    result   = pipeline.run_text(body.text, body.src_lang)

    return TranslateTextResponse(
        source_text=result.source_text,
        source_lang=result.detected_lang,
        malagasy_text=result.malagasy_text,
        dialect=result.dialect,
        audio_url=_audio_url(request, result.audio_path),
        latency_ms=_latency(result),
    )


@router.get(
    "/audio/{filename}",
    response_class=FileResponse,
    summary="Fetch a synthesised WAV (one-time; file is auto-deleted by OS)",
)
def get_audio(filename: str):
    path = os.path.join(tempfile.gettempdir(), filename)
    if not os.path.isfile(path):
        raise HTTPException(404, "Audio file not found or already expired.")
    return FileResponse(path, media_type="audio/wav", filename=filename)
