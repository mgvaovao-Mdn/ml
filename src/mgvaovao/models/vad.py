# -*- coding: utf-8 -*-
"""
SileroVAD — strips silence from raw audio before ASR.

Silero VAD is ~2 MB, CPU-fast, and dramatically reduces Whisper
hallucinations on silent/noisy segments.
"""
from __future__ import annotations
import numpy as np
import torch


class SileroVAD:
    """
    Voice Activity Detection using Silero VAD.
    Resamples to 16 kHz internally; returns concatenated speech segments.
    """

    TARGET_SR = 16_000  # Silero only supports 8 000 or 16 000 Hz

    def __init__(
        self,
        threshold: float = 0.5,
        min_speech_ms: int = 250,
        min_silence_ms: int = 100,
        speech_pad_ms: int = 30,
    ):
        self.threshold      = threshold
        self.min_speech_ms  = min_speech_ms
        self.min_silence_ms = min_silence_ms
        self.speech_pad_ms  = speech_pad_ms

        self._model, utils = torch.hub.load(
            "snakers4/silero-vad",
            "silero_vad",
            trust_repo=True,
            force_reload=False,
        )
        (
            self._get_speech_timestamps,
            _save_audio,
            _read_audio,
            _VADIterator,
            self._collect_chunks,
        ) = utils

    # ── public API ────────────────────────────────────────────────────────

    def get_speech_timestamps(self, audio_16k: np.ndarray) -> list[dict]:
        """Return [{start, end}] in samples at 16 kHz."""
        wav = _to_tensor(audio_16k)
        return self._get_speech_timestamps(
            wav,
            self._model,
            threshold=self.threshold,
            sampling_rate=self.TARGET_SR,
            min_speech_duration_ms=self.min_speech_ms,
            min_silence_duration_ms=self.min_silence_ms,
            speech_pad_ms=self.speech_pad_ms,
        )

    def apply(self, audio: np.ndarray, sr: int) -> np.ndarray:
        """
        Strip silence from *audio* (any sample rate, mono/stereo).
        Returns concatenated speech-only segments at 16 kHz.
        Falls back to the full (resampled) audio if no speech is found.
        """
        wav16 = _resample(audio, sr, self.TARGET_SR)
        timestamps = self.get_speech_timestamps(wav16)
        if not timestamps:
            return wav16  # no VAD applied — caller gets full audio
        chunks = self._collect_chunks(timestamps, _to_tensor(wav16))
        return chunks.numpy()


# ── helpers ───────────────────────────────────────────────────────────────

def _to_tensor(audio: np.ndarray) -> torch.Tensor:
    wav = torch.from_numpy(audio).float()
    if wav.dim() == 2:
        wav = wav.mean(0)
    return wav


def _resample(audio: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    if src_sr == dst_sr:
        wav = torch.from_numpy(audio).float()
        if wav.dim() == 2:
            wav = wav.mean(0)
        return wav.numpy()
    import torchaudio.functional as AF
    wav = torch.from_numpy(audio).float()
    if wav.dim() == 1:
        wav = wav.unsqueeze(0)
    if wav.shape[0] > 1:
        wav = wav.mean(0, keepdim=True)
    wav = AF.resample(wav, src_sr, dst_sr)
    return wav.squeeze().numpy()
