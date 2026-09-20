# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
from typing import List
from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

# ── Detection d'activite vocale ─────────────────────────────────────────────
#
# Reference EPINGLEE du depot Silero VAD, et non `master`.
#
# torch.hub.load telecharge par defaut la branche master du depot amont : la
# construction de l'image dependait donc de l'etat de GitHub le jour ou elle
# tournait. Elle a fini par casser sans qu'une ligne de ce depot change, le
# jour ou Silero a ajoute un module important onnxruntime au niveau module.
#
# v5.1.2 expose exactement le 5-uplet d'utilitaires que ce code deballe, et
# n'exige pas onnxruntime. Relever cette version est un choix delibere, a
# faire en verifiant ces deux points.
SILERO_VAD_REF: str = "snakers4/silero-vad:v5.1.2"


# ── Dialect registry ────────────────────────────────────────────────────────

DIALECTS: List[str] = ["plt_latn", "betsileo", "betsimisaraka", "sakalava"]

# Chaque dialecte porte son PROPRE jeton cible.
#
# Auparavant les quatre partageaient "plt_Latn" : le modèle n'avait alors aucun
# moyen de distinguer « traduire en betsileo » de « traduire en officiel », et
# chaque dialecte était entraîné isolément — donc sans profiter des données de
# l'officiel, de loin les plus nombreuses. Avec des jetons distincts et un
# entraînement conjoint, les dialectes peu dotés bénéficient du transfert depuis
# le malgache officiel, ce dont le sakalava a un besoin vital.
#
# Codes : `plt`, `bzc` et `skg` sont de vrais codes ISO 639-3. Le betsileo n'a
# pas de code propre — ISO le rattache au plateau (`plt`) — d'où un jeton dérivé
# explicite. À faire valider par un linguiste avant de figer le corpus.
DIALECT_META: dict = {
    "plt_latn": {
        "name":       "Malagasy Officiel",
        "region":     "Hautes Terres — Antananarivo",
        "population": "référence nationale",
        "nllb_target":"plt_Latn",
        "iso639_3":   "plt",
        "phase":      1,
    },
    "betsileo": {
        "name":       "Betsileo",
        "region":     "Fianarantsoa — Hautes Terres Sud",
        "population": "~1.5 million",
        # Pas de code ISO 639-3 distinct : rattaché à `plt`. Jeton dérivé.
        "nllb_target":"pltbts_Latn",
        "iso639_3":   None,
        "phase":      4,
    },
    "betsimisaraka": {
        "name":       "Betsimisaraka",
        "region":     "Côte Est — Toamasina",
        "population": "~1.5 million",
        "nllb_target":"bzc_Latn",
        "iso639_3":   "bzc",
        "phase":      4,
    },
    "sakalava": {
        "name":       "Sakalava",
        "region":     "Côte Ouest — Mahajanga, Toliara",
        "population": "~1 million",
        "nllb_target":"skg_Latn",
        "iso639_3":   "skg",
        "phase":      4,
    },
}

# Jetons à ajouter au tokenizer NLLB : ceux qui ne font pas déjà partie des 200
# langues du modèle. `plt_Latn` en fait partie, les trois autres non.
NEW_LANG_TOKENS: List[str] = [
    meta["nllb_target"]
    for key, meta in DIALECT_META.items()
    if key != "plt_latn"
]

# ── Registre dynamique ──────────────────────────────────────────────────────
#
# DIALECT_META ci-dessus n'est qu'un repli. La source de verite est la
# plateforme de collecte, dont le CRUD porte deja les dialectes et, depuis
# l'ajout de leur configuration de modele, leurs jetons de langue.
#
# `npm run db:export:training` y depose un `dialects.json` ; le chemin se regle
# par MGVAOVAO_DIALECT_REGISTRY. Sans ce fichier, on retombe sur la table en dur
# — le pipeline reste donc utilisable hors ligne, mais un dialecte ajoute dans
# la plateforme n'apparait ici qu'une fois l'export rejoue.
#
# Interet concret : ajouter un dialecte ne demande plus de toucher au Python.
# Les noms de points de controle (`nllb_<id>`, `tts_<id>`) se deduisent de
# l'identifiant, donc ils suivent automatiquement.

def _load_dialect_registry() -> tuple[List[str], dict, List[str]]:
    """
    Retourne (DIALECTS, DIALECT_META, NEW_LANG_TOKENS) depuis le registre
    exporte s'il existe, sinon depuis la table en dur.

    Toute anomalie de lecture retombe silencieusement sur le repli : un registre
    illisible ne doit pas empecher un entrainement de demarrer, il doit juste
    ne pas etre pris en compte.
    """
    import json
    import os

    path = os.environ.get("MGVAOVAO_DIALECT_REGISTRY", "")
    if not path:
        for candidate in ("dialects.json", "dataset/dialects.json", "export/dialects.json"):
            if os.path.exists(candidate):
                path = candidate
                break

    if not path or not os.path.exists(path):
        return _FALLBACK_DIALECTS, _FALLBACK_META, _FALLBACK_TOKENS

    try:
        with open(path, "r", encoding="utf-8") as fh:
            entries = json.load(fh)
        if not isinstance(entries, list) or not entries:
            return _FALLBACK_DIALECTS, _FALLBACK_META, _FALLBACK_TOKENS

        ids: List[str] = []
        meta: dict = {}
        for entry in entries:
            key = entry.get("id")
            target = entry.get("nllb_target")
            if not key or not target:
                continue
            ids.append(key)
            base = _FALLBACK_META.get(key, {})
            meta[key] = {
                "name": entry.get("name", base.get("name", key)),
                "region": base.get("region", ""),
                "population": base.get("population", ""),
                "nllb_target": target,
                "iso639_3": entry.get("iso639_3", base.get("iso639_3")),
                "is_translation_target": entry.get("is_translation_target", False),
                "nllb_checkpoint": entry.get("nllb_checkpoint", "nllb_" + key),
                "tts_checkpoint": entry.get("tts_checkpoint", "tts_" + key),
                "phase": base.get("phase", 4),
            }

        if not ids:
            return _FALLBACK_DIALECTS, _FALLBACK_META, _FALLBACK_TOKENS

        # Les jetons a ajouter sont ceux que NLLB ne connait pas : tout sauf
        # `plt_Latn`, qui fait partie de ses 200 langues.
        tokens = [m["nllb_target"] for m in meta.values() if m["nllb_target"] != "plt_Latn"]
        return ids, meta, sorted(set(tokens))
    except Exception:
        return _FALLBACK_DIALECTS, _FALLBACK_META, _FALLBACK_TOKENS


_FALLBACK_DIALECTS = DIALECTS
_FALLBACK_META = DIALECT_META
_FALLBACK_TOKENS = NEW_LANG_TOKENS

DIALECTS, DIALECT_META, NEW_LANG_TOKENS = _load_dialect_registry()


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
    # q_proj/v_proj seuls ne suffisent pas pour absorber une nouvelle variete :
    # on elargit a l ensemble des projections d attention et au feed-forward.
    nllb_lora_target_modules:  List[str] = [
        "q_proj", "k_proj", "v_proj", "out_proj", "fc1", "fc2",
    ]
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
    vad_threshold:      float = 0.3
    vad_min_speech_ms:  int   = 250
    vad_min_silence_ms: int   = 100
    vad_speech_pad_ms:  int   = 30

    # ── VAD (streaming — used by StreamingVAD in WebSocket endpoint) ──────
    # Longer silence needed to reliably detect end-of-utterance in a stream.
    vad_stream_min_silence_ms: int = 400   # 400 ms pause = done speaking

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
