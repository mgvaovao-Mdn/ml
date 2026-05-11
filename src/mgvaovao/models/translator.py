# -*- coding: utf-8 -*-
"""NLLBTranslator — NLLB-200 with optional per-dialect LoRA checkpoint."""
from __future__ import annotations
import time
from dataclasses import dataclass


@dataclass
class TranslationResult:
    text:         str
    src_lang_code:str
    tgt_lang_code:str
    latency_ms:   int


class NLLBTranslator:
    """
    Translates from any supported source language to Malagasy (plt_Latn).
    Loads the shared NLLB-200 base model, then applies LoRA adapters from
    the dialect-specific checkpoint if available.
    """

    def __init__(self, dialect: str, device: str | None = None):
        import torch
        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
        from ..core.config import settings, DIALECT_META, SRC_LANGS

        self._src_langs   = SRC_LANGS
        self.nllb_target  = DIALECT_META[dialect]["nllb_target"]
        self.max_src_len  = settings.nllb_max_src_len
        self.max_tgt_len  = settings.nllb_max_tgt_len
        self.num_beams    = settings.nllb_num_beams

        _device = device or settings.device
        self.device = _device if torch.cuda.is_available() else "cpu"

        use_fp16   = settings.nllb_fp16 and self.device == "cuda"
        dtype      = torch.float16 if use_fp16 else torch.float32
        base_name  = settings.nllb_model_name
        ckpt_final = settings.nllb_checkpoint(dialect) / "final"

        # Tokenizer: prefer fine-tuned checkpoint (may have updated vocab)
        tok_path = str(ckpt_final) if ckpt_final.is_dir() else base_name
        self.tokenizer = AutoTokenizer.from_pretrained(tok_path)

        # Base model is always NLLB-200; LoRA adapters are applied on top
        base = AutoModelForSeq2SeqLM.from_pretrained(
            base_name, torch_dtype=dtype, low_cpu_mem_usage=True
        )
        if ckpt_final.is_dir() and (ckpt_final / "adapter_config.json").is_file():
            from peft import PeftModel
            base = PeftModel.from_pretrained(base, str(ckpt_final))

        self.model = base.to(self.device).eval()

        # Cache forced_bos once — same for all calls
        self._forced_bos = self.tokenizer.convert_tokens_to_ids(self.nllb_target)

    def translate(self, text: str, src_lang: str = "fr") -> TranslationResult:
        src_code = self._src_langs.get(src_lang, "fra_Latn")
        self.tokenizer.src_lang = src_code

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=self.max_src_len,
        ).to(self.device)

        t0 = time.perf_counter()
        import torch
        with torch.no_grad():
            tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=self._forced_bos,
                max_length=self.max_tgt_len,
                num_beams=self.num_beams,
            )
        latency_ms = round((time.perf_counter() - t0) * 1000)

        translated = self.tokenizer.batch_decode(tokens, skip_special_tokens=True)[0]
        return TranslationResult(
            text=translated,
            src_lang_code=src_code,
            tgt_lang_code=self.nllb_target,
            latency_ms=latency_ms,
        )
