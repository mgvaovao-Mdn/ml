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
import json
import base64
import logging
from functools import partial

import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from mgvaovao.core.config import Settings
from mgvaovao.models.streaming_vad import StreamingVAD

from .turn_state import TurnController

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

    Text messages (JSON) :
      {"type": "ping"}                 maintien de connexion
      {"type": "playback_finished"}    le client a fini de jouer l'audio
                                       synthétisé — reprendre l'écoute
      {"type": "barge_in", "enabled": true}
                                       autorise l'interruption pendant la
                                       lecture. À n'activer QUE si le client
                                       applique une annulation d'écho : sans
                                       elle, le micro capte la voix du modèle
                                       et la boucle se rouvre.

    Messages émis en plus des résultats :
      {"type": "turn", "state": "listening" | "processing" | "speaking"}

    Le client DOIT envoyer `playback_finished` à la fin de la lecture. À défaut,
    un délai de garde rétablit l'écoute pour ne pas laisser la session sourde.
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
    turn = TurnController()

    async def set_turn(new_state_fn, *args) -> None:
        """Applique une transition et en informe le client."""
        new_state_fn(*args)
        await websocket.send_json({"type": "turn", "state": turn.state.value})

    log.info(f"WS open — dialect={dialect} src_lang={src_lang}")

    try:
        while True:
            msg = await websocket.receive()

            # ── trames de contrôle ────────────────────────────────────────
            if "text" in msg:
                try:
                    ctrl = json.loads(msg["text"])
                except (ValueError, TypeError):
                    continue

                kind = ctrl.get("type")
                if kind == "playback_finished":
                    # Le client a fini de jouer l'audio : on peut réécouter.
                    # Le VAD est vidé pour ne pas repartir sur des restes captés
                    # pendant la lecture.
                    vad.reset()
                    await set_turn(turn.resume_listening)
                elif kind == "barge_in":
                    turn._allow_barge_in = bool(ctrl.get("enabled"))
                    log.info(f"barge-in {'activé' if turn._allow_barge_in else 'désactivé'}")
                continue

            # ── disconnect frame (uvicorn sends this before raising WebSocketDisconnect)
            if msg.get("type") == "websocket.disconnect":
                break

            # ── audio binary frame ────────────────────────────────────────
            raw: bytes = msg.get("bytes") or b""
            if not raw:
                continue

            # Un client muet pendant la lecture finirait par bloquer la
            # session : le délai de garde rétablit l'écoute de force.
            if turn.expired():
                log.warning("fin de lecture non signalée — écoute rétablie")
                vad.reset()
                await set_turn(turn.resume_listening)

            if not turn.accepts_audio():
                # Trames ignorées pendant le traitement et la lecture. Le VAD est
                # réinitialisé à chaque fois : sans cela son tampon accumulerait
                # la voix du modèle et l'émettrait au retour à l'écoute — c'est
                # exactement la boucle qu'on cherche à éviter.
                vad.reset()
                continue

            state, prob, audio = vad.push_bytes(raw)

            # Retour VAD continu, pour l'indicateur visuel du client
            await websocket.send_json({
                "type": "vad",
                "state": state,
                "prob": round(prob, 3),
            })

            if state == "end" and audio is not None:
                await set_turn(turn.begin_processing)
                try:
                    fn = partial(_run_pipeline_sync, pipeline, audio, src_lang)
                    result = await loop.run_in_executor(None, fn)
                    await websocket.send_json(result)

                    # La durée de l'audio synthétisé borne l'attente avant de
                    # réécouter, si le client ne signale rien.
                    duration = None
                    if isinstance(result, dict):
                        duration = result.get("audio_duration_s") or result.get("duration_s")
                    vad.reset()
                    await set_turn(turn.begin_speaking, duration)
                except Exception as exc:
                    log.exception("Pipeline error")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(exc),
                    })
                    # En cas d'échec on réécoute : rester bloqué en traitement
                    # rendrait la session inutilisable jusqu'à reconnexion.
                    vad.reset()
                    await set_turn(turn.resume_listening)

    except WebSocketDisconnect:
        log.info(f"WS closed — dialect={dialect}")
