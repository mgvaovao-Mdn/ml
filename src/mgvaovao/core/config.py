# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import List
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ── Dialect registry ────────────────────────────────────────────────────────

DIALECTS: List[str] = ["plt_latn", "betsileo", "betsimisaraka", "sakalava"]

DIALECT_META: dict = {
    "plt_latn": {
        "name":       "Malagasy Officiel",
        "region":     "Hautes Terres — Antananarivo",
        "population": "référence nationale",
        "nllb_target":"plt_Latn",
        "phase":      1,
    },
    "betsileo": {
        "name":       "Betsileo",
        "region":     "Fianarantsoa — Hautes Terres Sud",
        "population": "~1.5 million",
        "nllb_target":"plt_Latn",
        "phase":      4,
    },
    "betsimisaraka": {
        "name":       "Betsimisaraka",
        "region":     "Côte Est — Toamasina",
        "population": "~1.5 million",
        "nllb_target":"plt_Latn",
        "phase":      4,
    },
    "sakalava": {
        "name":       "Sakalava",
        "region":     "Côte Ouest — Mahajanga, Toliara",
        "population": "~1 million",
        "nllb_target":"plt_Latn",
        "phase":      4,
    },
}

SRC_LANGS: dict[str, str] = {
    "fr": "fra_Latn",
    "en": "eng_Latn",
    "de": "deu_Latn",
    "es": "spa_Latn",
    "it": "ita_Latn",
    "pt": "por_Latn",
}

# ── Settings ────────────────────────────────────────────────────────────────

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="MGVAOVAO_",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Runtime ──────────────────────────────────────────────────────────
    device: str = Field("cuda", description="cuda or cpu")

    # ── Paths ─────────────────────────────────────────────────────────────
    root_dir:        Path = Path("/mgvaovao")
    checkpoints_dir: Path = Path("/mgvaovao/checkpoints")
    dataset_dir:     Path = Path("/mgvaovao/dataset")
    hf_cache_dir:    Path = Path("/mgvaovao/.cache/huggingface")
    torch_hub_dir:   Path = Path("/mgvaovao/.cache/torch/hub")

    # ── Whisper ───────────────────────────────────────────────────────────
    whisper_model_size: str = Field("small", description="tiny|base|small|medium|large")

    # ── NLLB ─────────────────────────────────────────────────────────────
    nllb_model_name:           str   = "facebook/nllb-200-distilled-600M"
    nllb_lora_r:               int   = 16
    nllb_lora_alpha:           int   = 32
    nllb_lora_target_modules:  List[str] = ["q_proj", "v_proj"]
    nllb_lora_dropout:         float = 0.1
    nllb_max_src_len:          int   = 128
    nllb_max_tgt_len:          int   = 128
    nllb_train_epochs:         int   = 5
    nllb_batch_size:           int   = 1
    nllb_grad_accum:           int   = 8
    nllb_lr:                   float = 5e-4
    nllb_warmup_ratio:         float = 0.06
    nllb_fp16:                 bool  = True
    nllb_gradient_checkpointing: bool = True
    nllb_save_total_limit:     int   = 3
    nllb_eval_steps:           int   = 50
    nllb_logging_steps:        int   = 10
    nllb_num_beams:            int   = 4
    nllb_chrf_threshold:       float = 2.0

    # ── TTS ───────────────────────────────────────────────────────────────
    tts_model_name:      str   = "facebook/mms-tts-mlg"
    tts_train_epochs:    int   = 50
    tts_batch_size:      int   = 1
    tts_lr:              float = 1e-4
    tts_save_steps:      int   = 100
    tts_logging_steps:   int   = 10
    tts_save_total_limit:int   = 3
    tts_min_samples:     int   = 80
    tts_utmos_threshold: float = 0.3

    # ── VAD (batch — used by SileroVAD in pipeline) ──────────────────────
    vad_threshold:      float = 0.5
    vad_min_speech_ms:  int   = 250
    vad_min_silence_ms: int   = 100
    vad_speech_pad_ms:  int   = 30

    # ── VAD (streaming — used by StreamingVAD in WebSocket endpoint) ──────
    # Longer silence needed to reliably detect end-of-utterance in a stream.
    vad_stream_min_silence_ms: int = 500   # 500 ms pause = done speaking

    # ── API ───────────────────────────────────────────────────────────────
    api_host:    str = "0.0.0.0"
    api_port:    int = 8000
    api_workers: int = 1

    # ── Helpers ───────────────────────────────────────────────────────────

    def nllb_checkpoint(self, dialect: str) -> Path:
        return self.checkpoints_dir / f"nllb_{dialect}"

    def tts_checkpoint(self, dialect: str) -> Path:
        return self.checkpoints_dir / f"tts_{dialect}"

    def nllb_paths(self, dialect: str) -> dict[str, Path]:
        base = self.dataset_dir / "nllb_finetune" / dialect
        return {
            "raw_fr":    base / "raw" / "fr",
            "raw_en":    base / "raw" / "en",
            "processed": base / "processed",
            "train":     base / "processed" / "train.jsonl",
            "val":       base / "processed" / "val.jsonl",
            "test":      base / "processed" / "test.jsonl",
            "reference": base / "reference" / "eval_fixed_200.csv",
            "ckpt":      self.checkpoints_dir / f"nllb_{dialect}",
        }

    def tts_paths(self, dialect: str) -> dict[str, Path]:
        base = self.dataset_dir / "tts_finetune" / dialect
        return {
            "raw_audio":       base / "raw_audio",
            "processed_audio": base / "processed_audio",
            "metadata":        base / "metadata.csv",
            "ckpt":            self.checkpoints_dir / f"tts_{dialect}",
        }


settings = Settings()
