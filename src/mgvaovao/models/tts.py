# -*- coding: utf-8 -*-
"""MalagasyTTS — MMS-TTS VITS with optional per-dialect fine-tuned checkpoint."""
from __future__ import annotations
import time
from dataclasses import dataclass
import numpy as np


@dataclass
class TTSResult:
    audio:       np.ndarray   # float32, values in [-1, 1]
    sample_rate: int
    latency_ms:  int


class MalagasyTTS:
    """
    Text → waveform synthesis using MMS-TTS (VITS).
    Loads the base facebook/mms-tts-mlg model, replacing it with the
    dialect-specific fine-tuned checkpoint when available.
    """

    def __init__(self, dialect: str, device: str | None = None):
        import torch
        from transformers import VitsModel, AutoTokenizer
        from ..core.config import settings

        _device = device or settings.device
        self.device = _device if torch.cuda.is_available() else "cpu"

        ckpt_final = settings.tts_checkpoint(dialect) / "final"
        model_id   = str(ckpt_final) if ckpt_final.is_dir() else settings.tts_model_name

        self.tokenizer  = AutoTokenizer.from_pretrained(model_id)
        self.model      = VitsModel.from_pretrained(model_id, torch_dtype=torch.float32)
        self.model      = self.model.to(self.device).eval()
        self.sample_rate = self.model.config.sampling_rate

    def synthesize(self, text: str) -> TTSResult:
        if not text.strip():
            silence = np.zeros(self.sample_rate // 4, dtype=np.float32)
            return TTSResult(silence, self.sample_rate, 0)

        import torch
        inputs = self.tokenizer(text, return_tensors="pt").to(self.device)

        t0 = time.perf_counter()
        with torch.no_grad():
            out = self.model(**inputs)
        latency_ms = round((time.perf_counter() - t0) * 1000)

        wav = out.waveform[0].cpu().float().numpy()
        return TTSResult(audio=wav, sample_rate=self.sample_rate, latency_ms=latency_ms)
