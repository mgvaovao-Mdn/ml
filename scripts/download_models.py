"""
Pre-download all inference models into the baked image cache.
Run once at Docker build time — no network access needed at runtime.
"""
import os
import sys

HF_HOME   = "/mgvaovao/.cache/huggingface"
HUB_DIR   = "/mgvaovao/.cache/torch/hub"
WHISPER_CACHE = f"{HF_HOME}/whisper"

os.makedirs(HF_HOME, exist_ok=True)
os.makedirs(HUB_DIR, exist_ok=True)
os.makedirs(WHISPER_CACHE, exist_ok=True)

# ── 1. Silero VAD (~2 MB, CPU) ────────────────────────────────────────────────
print(">>> Downloading Silero VAD...", flush=True)
import torch
torch.hub.set_dir(HUB_DIR)
model, _ = torch.hub.load(
    "snakers4/silero-vad", "silero_vad",
    trust_repo=True, force_reload=False,
)
del model
print(">>> Silero VAD done.", flush=True)

# ── 2. Whisper small (~460 MB) ────────────────────────────────────────────────
print(">>> Downloading Whisper small...", flush=True)
import whisper
model = whisper.load_model("small", device="cpu", download_root=WHISPER_CACHE)
del model
print(">>> Whisper small done.", flush=True)

# ── 3. NLLB-200-distilled-600M (~1.2 GB) ─────────────────────────────────────
print(">>> Downloading NLLB-200-distilled-600M...", flush=True)
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
NLLB = "facebook/nllb-200-distilled-600M"
AutoTokenizer.from_pretrained(NLLB)
AutoModelForSeq2SeqLM.from_pretrained(NLLB, low_cpu_mem_usage=True)
print(">>> NLLB done.", flush=True)

# ── 4. MMS-TTS base Malagasy (~300 MB, shared by all 4 dialects) ─────────────
print(">>> Downloading MMS-TTS-mlg...", flush=True)
from transformers import VitsModel, AutoTokenizer as AT
MMS = "facebook/mms-tts-mlg"
AT.from_pretrained(MMS)
VitsModel.from_pretrained(MMS)
print(">>> MMS-TTS done.", flush=True)

print(">>> All models downloaded successfully.", flush=True)
