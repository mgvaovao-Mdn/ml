"""
Pull all dialect checkpoints from GCS into /mgvaovao/checkpoints/ at container startup.

GCS layout (mirrors settings.tts_checkpoint / settings.nllb_checkpoint):
  gs://<bucket>/tts_plt_latn/final/       ← VitsModel save_pretrained output
  gs://<bucket>/tts_betsileo/final/
  gs://<bucket>/tts_betsimisaraka/final/
  gs://<bucket>/tts_sakalava/final/
  gs://<bucket>/nllb_plt_latn/final/      ← LoRA adapter_config.json + weights
  gs://<bucket>/nllb_betsileo/final/
  gs://<bucket>/nllb_betsimisaraka/final/
  gs://<bucket>/nllb_sakalava/final/

If the bucket env var is not set or bucket is empty, skips silently
(container falls back to baked base models).
"""
from __future__ import annotations
import os
import sys
from pathlib import Path

BUCKET  = os.environ.get("MGVAOVAO_CHECKPOINTS_BUCKET", "")
LOCAL   = Path(os.environ.get("MGVAOVAO_CHECKPOINTS_DIR", "/mgvaovao/checkpoints"))


def pull() -> None:
    if not BUCKET:
        print("pull_checkpoints: MGVAOVAO_CHECKPOINTS_BUCKET not set — skipping.", flush=True)
        return

    try:
        from google.cloud import storage
    except ImportError:
        print("pull_checkpoints: google-cloud-storage not installed — skipping.", flush=True)
        return

    print(f"pull_checkpoints: syncing gs://{BUCKET}/ → {LOCAL}", flush=True)
    client = storage.Client()
    bucket = client.bucket(BUCKET)

    blobs = list(bucket.list_blobs())
    if not blobs:
        print("pull_checkpoints: bucket is empty — using baked base models.", flush=True)
        return

    for blob in blobs:
        dest = LOCAL / blob.name
        if dest.exists():
            # Skip if already present and same size (avoids re-download on warm restart)
            if dest.stat().st_size == blob.size:
                continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(str(dest))
        print(f"  ↓ {blob.name}  ({blob.size // 1024} KB)", flush=True)

    print("pull_checkpoints: done.", flush=True)


if __name__ == "__main__":
    pull()
