# -*- coding: utf-8 -*-
"""WhisperASR — speech recognition. Expects 16 kHz mono float32 audio."""
from __future__ import annotations
import time
from dataclasses import dataclass
import numpy as np


@dataclass
class ASRResult:
    text:       str
    language:   str
    latency_ms: int


class WhisperASR:
    """
    Thin wrapper around openai-whisper.
    Loaded once and reused across requests.
    """

    def __init__(self, model_size: str | None = None, device: str | None = None):
        import torch
        import whisper
        from ..core.config import settings

        _size   = model_size or settings.whisper_model_size
        _device = device or settings.device
        if _device == "cuda" and not torch.cuda.is_available():
            _device = "cpu"

        self.device = _device
        whisper_cache = str(settings.hf_cache_dir / "whisper")
        self.model  = whisper.load_model(_size, device=_device, download_root=whisper_cache)

    def transcribe(
        self,
        audio: np.ndarray,
        language: str | None = None,
    ) -> ASRResult:
        """
        Transcribe *audio* (16 kHz mono float32 numpy array).
        Pass *language* to skip auto-detection (e.g. "fr").
        """
        t0     = time.perf_counter()
        result = self.model.transcribe(
            audio.astype(np.float32),
            language=language if language else None,
            task="transcribe",
            fp16=(self.device == "cuda"),
        )
        latency_ms = round((time.perf_counter() - t0) * 1000)
        return ASRResult(
            text=result["text"].strip(),
            language=result["language"],
            latency_ms=latency_ms,
        )
