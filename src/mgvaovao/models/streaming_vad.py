# -*- coding: utf-8 -*-
"""
Streaming VAD — stateful, chunk-by-chunk voice activity detection.

Silero VAD requires exactly 512 samples per chunk at 16 kHz (32 ms).
This class buffers incoming bytes, feeds aligned chunks to the model,
and emits a speech-end event (returning the accumulated audio) once
sustained silence follows a valid speech segment.

State machine:
    IDLE  →  (speech detected)  →  SPEAKING
    SPEAKING  →  (silence for ≥ min_silence_frames)  →  IDLE  (+ emit audio)
    SPEAKING  →  (max_speech_s exceeded)  →  IDLE  (+ emit audio)
"""
from __future__ import annotations

import numpy as np
import torch

from mgvaovao.core.config import Settings

SILERO_REPO = "snakers4/silero-vad"
CHUNK_SAMPLES = 512   # Silero requirement at 16 kHz
TARGET_SR = 16_000


class StreamingVAD:
    """
    Feed raw PCM float32 bytes chunk by chunk via `push_bytes()`.

    Returns a tuple (state, prob, audio_or_None) on each call:
      - state  : "idle" | "speaking" | "trailing" | "end"
      - prob   : speech probability for the latest 512-sample frame (0–1)
      - audio  : np.ndarray (float32, 16 kHz) when state == "end", else None
    """

    IDLE = "idle"
    SPEAKING = "speaking"
    TRAILING = "trailing"  # speech then silence, counting down

    def __init__(self, cfg: Settings) -> None:
        self._threshold = cfg.vad_threshold
        # Convert time-based thresholds to frame counts (1 frame = 32 ms)
        self._min_speech_frames  = max(1, round(cfg.vad_min_speech_ms / 32))
        self._min_silence_frames = max(1, round(cfg.vad_stream_min_silence_ms / 32))
        self._max_speech_frames = round(30_000 / 32)  # hard cap: 30 s

        model, _ = torch.hub.load(
            SILERO_REPO, "silero_vad", force_reload=False, trust_repo=True
        )
        model.eval()
        self._model = model

        self._reset()

    # ── public API ────────────────────────────────────────────────────────────

    def push_bytes(
        self, raw: bytes
    ) -> tuple[str, float, np.ndarray | None]:
        """
        Accept raw bytes (float32 LE PCM, 16 kHz).
        May produce zero, one, or multiple model evaluations internally.
        Returns the state / prob / audio for the LAST processed chunk.
        """
        new_samples = np.frombuffer(raw, dtype=np.float32)
        self._byte_buf = np.concatenate([self._byte_buf, new_samples])

        last_state, last_prob, audio = self.IDLE, 0.0, None

        while len(self._byte_buf) >= CHUNK_SAMPLES:
            chunk = self._byte_buf[:CHUNK_SAMPLES]
            self._byte_buf = self._byte_buf[CHUNK_SAMPLES:]
            last_state, last_prob, audio = self._process_chunk(chunk)
            if last_state == "end":
                break  # caller handles result; leftover stays in buf

        return last_state, last_prob, audio

    def reset(self) -> None:
        """Call between utterances if you want to manually reset state."""
        self._reset()

    # ── internals ─────────────────────────────────────────────────────────────

    def _reset(self) -> None:
        self._state = self.IDLE
        self._speech_buf: list[np.ndarray] = []
        self._speech_frames = 0
        self._silence_frames = 0
        self._byte_buf = np.empty(0, dtype=np.float32)
        if hasattr(self, "_model"):
            self._model.reset_states()

    def _process_chunk(
        self, chunk: np.ndarray
    ) -> tuple[str, float, np.ndarray | None]:
        tensor = torch.from_numpy(chunk).unsqueeze(0)
        with torch.no_grad():
            prob: float = self._model(tensor, TARGET_SR).item()

        is_speech = prob >= self._threshold

        if self._state == self.IDLE:
            if is_speech:
                self._state = self.SPEAKING
                self._speech_buf = [chunk]
                self._speech_frames = 1
                self._silence_frames = 0
            return self.IDLE, prob, None

        if self._state == self.SPEAKING:
            self._speech_buf.append(chunk)
            if is_speech:
                self._speech_frames += 1
                self._silence_frames = 0
                # Hard cap: force emit after 30 s
                if self._speech_frames >= self._max_speech_frames:
                    return self._emit()
                return self.SPEAKING, prob, None
            else:
                self._silence_frames += 1
                if self._silence_frames >= self._min_silence_frames:
                    if self._speech_frames >= self._min_speech_frames:
                        return self._emit()
                    # Too short — discard
                    self._reset()
                    return self.IDLE, prob, None
                return self.TRAILING, prob, None

        if self._state == self.TRAILING:
            self._speech_buf.append(chunk)
            if is_speech:
                # Resumed speech — go back to SPEAKING
                self._state = self.SPEAKING
                self._speech_frames += 1
                self._silence_frames = 0
                return self.SPEAKING, prob, None
            else:
                self._silence_frames += 1
                if self._silence_frames >= self._min_silence_frames:
                    if self._speech_frames >= self._min_speech_frames:
                        return self._emit()
                    self._reset()
                    return self.IDLE, prob, None
                return self.TRAILING, prob, None

        return self.IDLE, prob, None

    def _emit(self) -> tuple[str, float, np.ndarray]:
        audio = np.concatenate(self._speech_buf).astype(np.float32)
        self._reset()
        return "end", 0.0, audio
