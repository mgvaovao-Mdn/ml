# -*- coding: utf-8 -*-
"""
WebSocket streaming endpoint for real-time audio translation.

Flow:
  1. Client opens ws://<host>/ws/stream/{dialect}?src_lang=fr
  2. Client streams Float32 PCM audio at 16 kHz as binary WebSocket messages
  3. Server feeds chunks to StreamingVAD
     - On every VAD frame → sends {"type":"vad","state":...,"prob":...}
  4. When VAD detects end-of-speech → sends {"type":"processing"}
     → runs pipeline (VAD→ASR→NLLB→TTS) in a thread-pool
     → sends {"type":"result", ...} with base64 WAV
  5. Connection stays open; client can speak multiple times per session
"""
from __future__ import annotations

import asyncio
import base64
import logging
from functools import partial

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from mgvaovao.core.config import Settings
from mgvaovao.models.streaming_vad import StreamingVAD

log = logging.getLogger("mgvaovao.stream")
router = APIRouter()
_settings = Settings()


def _get_pipeline(app, dialect: str):
    pipelines = getattr(app.state, "pipelines", {})
    if dialect not in pipelines:
        raise KeyError(dialect)
    return pipelines[dialect]


def _run_pipeline_sync(pipeline, audio: np.ndarray, src_lang: str | None) -> dict:
    result = pipeline.run_audio(audio, 16_000, src_lang)
    with open(result.audio_path, "rb") as f:
        audio_bytes = f.read()
    return {
        "type": "result",
        "source_text": result.source_text,
        "detected_lang": result.detected_lang,
        "malagasy_text": result.malagasy_text,
        "dialect": result.dialect,
        "audio_b64": base64.b64encode(audio_bytes).decode(),
        "latency_ms": result.latency_ms,
    }


@router.websocket("/stream/{dialect}")
async def stream_audio(
    websocket: WebSocket,
    dialect: str,
    src_lang: str | None = None,
):
    """
    Real-time audio translation via WebSocket.

    Binary messages:  float32 PCM at 16 kHz (any chunk size)
    Text messages:    JSON — {"type": "ping"} to keep alive
    """
    await websocket.accept()

    try:
        pipeline = _get_pipeline(websocket.app, dialect)
    except KeyError:
        await websocket.send_json({
            "type": "error",
            "message": f"Dialect '{dialect}' not loaded. "
                       f"Available: {list(getattr(websocket.app.state, 'pipelines', {}).keys())}",
        })
        await websocket.close(code=1008)
        return

    vad = StreamingVAD(_settings)
    loop = asyncio.get_event_loop()
    processing = False  # guard: don't overlap pipeline runs

    log.info(f"WS open — dialect={dialect} src_lang={src_lang}")

    try:
        while True:
            msg = await websocket.receive()

            # ── ping / control text frames ────────────────────────────────
            if "text" in msg:
                # currently only "ping" is recognised; extend as needed
                continue

            # ── disconnect frame (uvicorn sends this before raising WebSocketDisconnect)
            if msg.get("type") == "websocket.disconnect":
                break

            # ── audio binary frame ────────────────────────────────────────
            raw: bytes = msg.get("bytes") or b""
            if not raw:
                continue

            state, prob, audio = vad.push_bytes(raw)
            log.info(f"VAD state={state} prob={prob:.3f}")

            # Always send VAD feedback so the UI can show a live indicator
            await websocket.send_json({
                "type": "vad",
                "state": state,
                "prob": round(prob, 3),
            })

            if state == "end" and audio is not None and not processing:
                processing = True
                await websocket.send_json({"type": "processing"})
                try:
                    fn = partial(_run_pipeline_sync, pipeline, audio, src_lang)
                    result = await loop.run_in_executor(None, fn)
                    await websocket.send_json(result)
                except Exception as exc:
                    log.exception("Pipeline error")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(exc),
                    })
                finally:
                    processing = False

    except WebSocketDisconnect:
        log.info(f"WS closed — dialect={dialect}")
