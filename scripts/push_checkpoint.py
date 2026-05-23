"""
Upload a fine-tuned checkpoint from your local PC to GCS model registry.

Usage:
    python scripts/push_checkpoint.py tts betsileo ./checkpoints/tts_betsileo/final
    python scripts/push_checkpoint.py nllb sakalava ./checkpoints/nllb_sakalava/final

After upload, the next Cloud Run cold start will automatically pull and use
the new checkpoint — no Cloud Build or redeployment needed.
"""
from __future__ import annotations
import sys
from pathlib import Path


def push(model_type: str, dialect: str, local_path: str,
         bucket: str = "mgvaovao-ia-checkpoints", project: str = "mgvaovao-ia") -> None:
    from google.cloud import storage

    local = Path(local_path).resolve()
    if not local.is_dir():
        print(f"ERROR: {local} is not a directory.", file=sys.stderr)
        sys.exit(1)

    gcs_prefix = f"{model_type}_{dialect}/final/"
    client = storage.Client(project=project)
    bkt = client.bucket(bucket)

    files = [f for f in local.rglob("*") if f.is_file()]
    print(f"Uploading {len(files)} file(s) to gs://{bucket}/{gcs_prefix}", flush=True)

    for f in files:
        blob_name = gcs_prefix + str(f.relative_to(local))
        blob = bkt.blob(blob_name)
        blob.upload_from_filename(str(f))
        print(f"  ↑ {blob_name}", flush=True)

    print(f"\nDone. Cloud Run will use this checkpoint on next cold start.")
    print(f"To force immediate pickup: redeploy with")
    print(f"  gcloud run services update mgvaovao-inference --region=us-central1 \\")
    print(f"    --project={project}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python push_checkpoint.py <tts|nllb> <dialect> <local_path>")
        print("  dialect: plt_latn | betsileo | betsimisaraka | sakalava")
        sys.exit(1)
    push(sys.argv[1], sys.argv[2], sys.argv[3])
