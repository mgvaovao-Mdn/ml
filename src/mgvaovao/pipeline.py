# -*- coding: utf-8 -*-
"""
MalagasyPipeline — orchestrates VAD → ASR → Translation → TTS.

All four model classes are instantiated once at construction and reused
across every call.  Two entry points are provided:

    run_audio(audio, sr, src_lang)  — full pipeline including VAD + Whisper
    run_text(text, src_lang)        — skip VAD/ASR, translate text directly
"""
from __future__ import annotations
import time
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import scipy.io.wavfile

from .models.vad        import SileroVAD
from .models.asr        import WhisperASR, ASRResult
from .models.translator import NLLBTranslator, TranslationResult
from .models.tts        import MalagasyTTS, TTSResult


@dataclass
class PipelineResult:
    source_text:   str
    detected_lang: str
    malagasy_text: str
    dialect:       str
    audio:         np.ndarray
    sample_rate:   int
    audio_path:    str                        # temp WAV file for HTTP response
    latency_ms:    dict = field(default_factory=dict)


class MalagasyPipeline:
    """
    Stateful pipeline for one dialect.  Instantiate once, call many times.
    Thread-safety: models are inference-only (no shared mutable state).

    Pass pre-built model objects to share GPU memory across dialect pipelines.
    Any argument left as None will be constructed here (standalone use).
    """

    def __init__(
        self,
        dialect: str,
        vad: SileroVAD | None = None,
        asr: WhisperASR | None = None,
        translator: NLLBTranslator | None = None,
        tts: MalagasyTTS | None = None,
    ):
        from .core.config import settings
        self.dialect    = dialect
        self.vad        = vad or SileroVAD(
            threshold=settings.vad_threshold,
            min_speech_ms=settings.vad_min_speech_ms,
            min_silence_ms=settings.vad_min_silence_ms,
            speech_pad_ms=settings.vad_speech_pad_ms,
        )
        self.asr        = asr or WhisperASR()
        self.translator = translator or NLLBTranslator(dialect)
        self.tts        = tts or MalagasyTTS(dialect)

    # ── public API ────────────────────────────────────────────────────────

    def run_audio(
        self,
        audio: np.ndarray,
        sr: int,
        src_lang: str | None = None,
    ) -> PipelineResult:
        """Audio → Malagasy text + WAV.  src_lang=None → Whisper auto-detects."""
        t_start = time.perf_counter()

        # 1. VAD — remove silence, keep only speech
        t0      = time.perf_counter()
        speech  = self.vad.apply(audio, sr)
        vad_ms  = round((time.perf_counter() - t0) * 1000)

        # 2. ASR — speech → text + detected language
        asr: ASRResult = self.asr.transcribe(speech, language=src_lang)

        # 3. Translation — source text → Malagasy
        tr: TranslationResult = self.translator.translate(asr.text, asr.language)

        # 4. TTS — Malagasy text → waveform
        tts: TTSResult = self.tts.synthesize(tr.text)

        audio_path = _save_wav(tts.audio, tts.sample_rate)
        total_ms   = round((time.perf_counter() - t_start) * 1000)

        return PipelineResult(
            source_text=asr.text,
            detected_lang=asr.language,
            malagasy_text=tr.text,
            dialect=self.dialect,
            audio=tts.audio,
            sample_rate=tts.sample_rate,
            audio_path=audio_path,
            latency_ms={
                "vad":         vad_ms,
                "asr":         asr.latency_ms,
                "translation": tr.latency_ms,
                "tts":         tts.latency_ms,
                "total":       total_ms,
            },
        )

    def run_text(self, text: str, src_lang: str = "fr") -> PipelineResult:
        """Text → Malagasy text + WAV.  Skips VAD and ASR."""
        t_start = time.perf_counter()

        tr:  TranslationResult = self.translator.translate(text, src_lang)
        tts: TTSResult         = self.tts.synthesize(tr.text)

        audio_path = _save_wav(tts.audio, tts.sample_rate)
        total_ms   = round((time.perf_counter() - t_start) * 1000)

        return PipelineResult(
            source_text=text,
            detected_lang=src_lang,
            malagasy_text=tr.text,
            dialect=self.dialect,
            audio=tts.audio,
            sample_rate=tts.sample_rate,
            audio_path=audio_path,
            latency_ms={
                "translation": tr.latency_ms,
                "tts":         tts.latency_ms,
                "total":       total_ms,
            },
        )


# ── helpers ───────────────────────────────────────────────────────────────

def _save_wav(audio: np.ndarray, sr: int) -> str:
    wav_i16 = (np.clip(audio, -1.0, 1.0) * 32767).astype(np.int16)
    tmp     = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", prefix="mgv_")
    scipy.io.wavfile.write(tmp.name, sr, wav_i16)
    return tmp.name
