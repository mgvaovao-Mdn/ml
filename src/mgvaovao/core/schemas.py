# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class TranslateTextRequest(BaseModel):
    text:    str = Field(..., description="Source text to translate")
    src_lang:str = Field("fr", description="Source language: fr en de es it pt")
    dialect: str = Field("betsileo", description="Target Malagasy dialect code")


class LatencyBreakdown(BaseModel):
    vad:         Optional[int] = None
    asr:         Optional[int] = None
    translation: int
    tts:         int
    total:       int


class TranslateTextResponse(BaseModel):
    source_text:   str
    source_lang:   str
    malagasy_text: str
    dialect:       str
    audio_url:     str
    latency_ms:    LatencyBreakdown


class TranslateAudioResponse(BaseModel):
    source_text:   str
    detected_lang: str
    malagasy_text: str
    dialect:       str
    audio_url:     str
    latency_ms:    LatencyBreakdown


class DialectInfo(BaseModel):
    code:        str
    name:        str
    region:      str
    population:  str
    phase:       int
    model_ready: bool


class HealthResponse(BaseModel):
    status: str


class ReadyResponse(BaseModel):
    ready:           bool
    loaded_dialects: list[str]


# ── WebSocket streaming messages ──────────────────────────────────────────────

class WsVadEvent(BaseModel):
    """Sent by server on every VAD frame to give live feedback."""
    type:  str = "vad"
    state: str          # idle | speaking | trailing
    prob:  float        # speech probability 0–1


class WsProcessingEvent(BaseModel):
    """Sent immediately when speech-end detected and pipeline starts."""
    type: str = "processing"


class WsResultEvent(BaseModel):
    """Final result after full pipeline completes."""
    type:          str = "result"
    source_text:   str
    detected_lang: str
    malagasy_text: str
    dialect:       str
    audio_b64:     str           # base64-encoded WAV bytes
    latency_ms:    dict[str, int | None]


class WsErrorEvent(BaseModel):
    type:    str = "error"
    message: str
