"""
One-time script: save base model weights as placeholder checkpoints for all
4 dialects and upload to GCS.

Run once from your local PC (needs gcloud auth + google-cloud-storage):
    pip install google-cloud-storage transformers torch
    python scripts/init_gcs_checkpoints.py

After this, each dialect has its own slot on GCS:
  tts_plt_latn/final/       ← copy of facebook/mms-tts-mlg
  tts_betsileo/final/       ← copy of facebook/mms-tts-mlg  (replace with fine-tuned)
  tts_betsimisaraka/final/  ← copy of facebook/mms-tts-mlg  (replace with fine-tuned)
  tts_sakalava/final/       ← copy of facebook/mms-tts-mlg  (replace with fine-tuned)

NLLB slots start empty (no LoRA yet); code falls back to base NLLB automatically.
When a dialect's LoRA is trained, use push_checkpoint.py to upload it.
"""
from __future__ import annotations
import tempfile
from pathlib import Path

BUCKET   = "mgvaovao-ia-checkpoints"
PROJECT  = "mgvaovao-ia"
DIALECTS = ["plt_latn", "betsileo", "betsimisaraka", "sakalava"]
TTS_BASE = "facebook/mms-tts-mlg"


def upload_dir(local_dir: Path, gcs_prefix: str, bucket) -> None:
    for f in local_dir.rglob("*"):
        if f.is_file():
            blob_name = gcs_prefix + str(f.relative_to(local_dir))
            blob = bucket.blob(blob_name)
            # Skip if already exists with same size
            blob.reload() if blob.exists() else None
            blob.upload_from_filename(str(f))
            print(f"  ↑ {blob_name}", flush=True)


def main() -> None:
    from google.cloud import storage
    from transformers import VitsModel, AutoTokenizer

    client = storage.Client(project=PROJECT)
    bkt    = client.bucket(BUCKET)

    print(f"Downloading base TTS model {TTS_BASE}…", flush=True)
    tokenizer = AutoTokenizer.from_pretrained(TTS_BASE)
    model     = VitsModel.from_pretrained(TTS_BASE)

    with tempfile.TemporaryDirectory() as tmp:
        save_path = Path(tmp) / "final"
        print(f"Saving to {save_path}…", flush=True)
        model.save_pretrained(str(save_path))
        tokenizer.save_pretrained(str(save_path))

        for dialect in DIALECTS:
            gcs_prefix = f"tts_{dialect}/final/"
            print(f"\nUploading tts_{dialect} → gs://{BUCKET}/{gcs_prefix}", flush=True)
            upload_dir(save_path, gcs_prefix, bkt)

    print("\nAll TTS placeholder checkpoints uploaded.")
    print("NLLB slots are intentionally empty — upload LoRA adapters with push_checkpoint.py after training.")


if __name__ == "__main__":
    main()
