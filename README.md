# MGVaovao — Malagasy Multilingual Audio Translation Pipeline

Real-time speech-to-speech translation into Malagasy dialects.  
**Input:** spoken audio in FR · EN · DE · ES · IT · PT  
**Output:** Malagasy speech, dialect-specific, streamed back automatically via WebSocket.

Built for [Maison du Numérique](https://mgvaovao.com) — a non-profit bringing digital inclusion to Madagascar.

> Full technical architecture (French): [`MGVaovao_Architecture_Complete.md`](MGVaovao_Architecture_Complete.md)

---

## Table of Contents

1. [What This Is](#1-what-this-is)
2. [Supported Dialects](#2-supported-dialects)
3. [Model Stack](#3-model-stack)
4. [Architecture Overview](#4-architecture-overview)
5. [Project Structure](#5-project-structure)
6. [Prerequisites](#6-prerequisites)
7. [Local Development (no Docker)](#7-local-development-no-docker)
8. [Docker — CPU (CI / no GPU)](#8-docker--cpu-ci--no-gpu)
9. [Docker — GPU (primary)](#9-docker--gpu-primary)
10. [API Reference](#10-api-reference)
11. [WebSocket Streaming](#11-websocket-streaming)
12. [Real-Time Browser UI](#12-real-time-browser-ui)
13. [Training Pipeline](#13-training-pipeline)
14. [Fine-Tuning Guide](#14-fine-tuning-guide)
15. [GCP Deployment](#15-gcp-deployment)
16. [Environment Variables](#16-environment-variables)
17. [MLOps & Monitoring](#17-mlops--monitoring)
18. [Cost Reference](#18-cost-reference)
19. [Roadmap](#19-roadmap)
20. [License](#20-license)

---

## 1. What This Is

MGVaovao translates foreign-language audio (YouTube videos, podcasts, live speech) into spoken Malagasy automatically — no button required. The user selects a dialect; the system detects speech, transcribes it, translates it, and synthesizes the audio in the chosen dialect.

The pipeline is a **four-stage cascade**:

```
Audio in  →  [VAD]  →  [ASR]  →  [NLLB MT]  →  [TTS]  →  WAV out
              Silero    Whisper    NLLB-200       MMS-TTS
              VAD v5    turbo      distilled-600M  MLG (VITS)
```

Every stage is independently fine-tuneable. The architecture is intentionally modular: swap out any component without touching the others.

---

## 2. Supported Dialects

| Dialect key | Display name | Region | Population |
|---|---|---|---|
| `plt_latn` | Malagasy Officiel | Hautes Terres — Antananarivo | National reference |
| `betsileo` | Betsileo | Fianarantsoa — Southern Highlands | ~1.5 M |
| `betsimisaraka` | Betsimisaraka | East Coast — Toamasina | ~1.5 M |
| `sakalava` | Sakalava | West Coast — Mahajanga / Toliara | ~1 M |

Source languages supported: `fr`, `en`, `de`, `es`, `it`, `pt` (auto-detected by Whisper if not specified).

---

## 3. Model Stack

| Stage | Model | Licence | VRAM (INT8) | Fine-tunable |
|---|---|---|---|---|
| VAD | Silero VAD v5 | MIT | 0 (CPU only) | Not needed |
| ASR | Whisper large-v3-turbo | Apache 2.0 | ~1.7 GB | Optional |
| Translation | NLLB-200-distilled-600M | CC-BY-NC 4.0 | ~0.7 GB | **Yes — high priority** |
| TTS | MMS-TTS-MLG (VITS) | CC-BY-NC 4.0 | ~0.5 GB / checkpoint | **Yes — per dialect** |

Total VRAM on L4 (24 GB): **~6.2 GB used**, 17.8 GB free — room for 3–5 concurrent WebSocket sessions.

### Why these models

- **Silero VAD v5**: 2 MB, MIT, CPU-only. Requires exactly 512 samples (32 ms) at 16 kHz. Universal — no language dependency.
- **Whisper turbo**: best open-source multilingual ASR, 99 languages, runs INT8 via CTranslate2 at ~1.7 GB VRAM.
- **NLLB-200-distilled-600M**: only open-source MT model with `plt_Latn` (Malagasy) in its tokenizer. LoRA fine-tuneable. CC-BY-NC is compatible with non-commercial NGO use.
- **MMS-TTS-MLG (VITS)**: the **only** viable open-source TTS model for Malagasy as of 2026. Fine-tuneable with as few as 80–150 sentences via [`ylacombe/finetune-hf-vits`](https://github.com/ylacombe/finetune-hf-vits).

All major commercial alternatives (Google TTS, Azure Neural TTS, ElevenLabs, Amazon Polly, SeamlessM4T) have no Malagasy support. See `MGVaovao_Architecture_Complete.md` §2 for a full exclusion table.

---

## 4. Architecture Overview

### Inference pipeline (request-time)

```
Browser / Client
    │  Float32 PCM (16 kHz) via WebSocket binary frames
    ▼
StreamingVAD         (512-sample chunks, state machine: IDLE→SPEAKING→TRAILING→END)
    │  on silence ≥ 500 ms: emit audio buffer
    ▼
WhisperASR           (openai-whisper, model loaded at startup)
    │  source text + detected language
    ▼
NLLBTranslator       (facebook/nllb-200-distilled-600M + optional LoRA adapter)
    │  Malagasy text (plt_Latn)
    ▼
MalagasyTTS          (facebook/mms-tts-mlg + optional dialect checkpoint)
    │  WAV bytes (16 kHz mono)
    ▼
WebSocket result     {source_text, malagasy_text, audio_b64, latency_ms}
```

### Google Cloud Platform (production)

```
Client Web (Next.js / Vercel)
    │ WebRTC / WebSocket
    ▼
Cloud Run GPU (NVIDIA L4 24 GB)        ← images from Artifact Registry
    │ loads checkpoints at startup
    ├─► GCS gs://mgvaovao-models/       (NLLB LoRA adapters, TTS checkpoints)
    └─► GCS gs://mgvaovao-datasets/     (training data, eval references)

GCS upload event
    │ via Cloud Pub/Sub
    ▼
Vertex AI Pipeline (Kubeflow DAG)
    └─ train-nllb → train-tts → evaluate → register → deploy

Cloud Scheduler (weekly)
    └─ Vertex AI Monitoring → drift alert → re-trigger pipeline
```

Latency breakdown (L4, warm):

| Stage | Time |
|---|---|
| Silero VAD (end-of-speech detection) | 1–50 ms |
| Whisper turbo INT8 (3 s audio) | 250–500 ms |
| NLLB-200-600M INT8 (short sentence) | 80–350 ms |
| MMS-TTS VITS (short sentence) | 150–450 ms |
| **Total (first audio chunk)** | **~700–1 500 ms** |

---

## 5. Project Structure

```
mgvaovao/
├── api/                        FastAPI application
│   ├── main.py                 App factory, lifespan (model loading), StaticFiles
│   ├── serve.py                CLI entry: uvicorn via Settings
│   └── routes/
│       ├── health.py           GET /health  GET /ready
│       ├── dialects.py         GET /dialects/
│       ├── translate.py        POST /translate/audio  POST /translate/text
│       └── stream.py           WS  /ws/stream/{dialect}
│
├── src/mgvaovao/               Installable Python package (pip install -e .)
│   ├── core/
│   │   ├── config.py           Settings (pydantic-settings, MGVAOVAO_ prefix)
│   │   └── schemas.py          Pydantic request/response + WebSocket schemas
│   ├── models/
│   │   ├── vad.py              SileroVAD  — batch, used in /translate/audio
│   │   ├── streaming_vad.py    StreamingVAD — stateful, used in /ws/stream
│   │   ├── asr.py              WhisperASR  (openai-whisper)
│   │   ├── translator.py       NLLBTranslator + optional LoRA adapter
│   │   └── tts.py              MalagasyTTS (MMS-TTS-MLG VITS)
│   └── pipeline.py             MalagasyPipeline — orchestrates all four stages
│
├── training/
│   ├── seed.py                 Create dataset folder structure + example pairs
│   ├── preprocess.py           JSONL/WAV → train/val/test splits
│   ├── train_nllb.py           NLLB LoRA fine-tuning (HuggingFace Trainer)
│   ├── train_tts.py            MMS-TTS VITS fine-tuning
│   └── evaluate.py             chrF++ (NLLB) + listening-test WAVs (TTS)
│
├── ui/
│   ├── demo.py                 Gradio UI (thin API client, no models)
│   └── static/
│       ├── index.html          Real-time WebSocket UI (served at /live)
│       ├── app.js              AudioWorklet consumer, WebSocket client, VAD bar
│       └── audio-processor.js  AudioWorklet processor (audio render thread)
│
├── deploy/
│   ├── vertex_training.yaml    Vertex AI Custom Training Job spec
│   └── cloudrun_inference.yaml Cloud Run GPU service spec
│
├── Dockerfile                  CPU image  (python:3.10-slim)  — CI only
├── Dockerfile.cuda             GPU image  (pytorch/pytorch:2.1.2-cuda11.8) — primary
├── docker-compose.yml          GPU-first compose (references Dockerfile.cuda)
├── docker-compose.cpu.yml      CPU override (merge with -f)
├── cloudbuild.yaml             Cloud Build: build + push CUDA image to Artifact Registry
├── pyproject.toml              Package metadata, dependencies, CLI entry points
└── .env.example                All configurable environment variables with defaults
```

---

## 6. Prerequisites

### Local development (no Docker)

- Python 3.10+
- CUDA-capable GPU recommended (GTX 1050 minimum; L4 for production parity)
- CUDA 11.8+ and matching cuDNN (if using GPU)
- `git`

### Docker GPU path

- Docker Desktop with WSL2 backend (Windows) or Docker Engine (Linux)
- NVIDIA Container Toolkit (`nvidia-ctk`)
- `docker compose` v2

### Cloud deployment

- Google Cloud project with billing enabled
- `gcloud` CLI authenticated
- APIs enabled: Cloud Run, Vertex AI, Cloud Build, Artifact Registry, Cloud Storage, Pub/Sub

---

## 7. Local Development (no Docker)

This is the recommended workflow for iterating on model code locally, especially on a machine with a GPU.

```bash
# 1. Clone
git clone https://github.com/mgvaovao/ml.git
cd ml

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac

# 3. Install PyTorch with CUDA (GPU) — adjust cu118 to match your CUDA version
pip install torch==2.1.2 torchaudio==2.1.2 --index-url https://download.pytorch.org/whl/cu118

# 4. Install the package and all dependencies
pip install -e .

# 5. Copy and configure env (optional — defaults work for local GPU)
cp .env.example .env
# Edit .env to override MGVAOVAO_DEVICE, MGVAOVAO_WHISPER_MODEL_SIZE, etc.

# 6. Seed the dataset folder structure
python -m training.seed --dialect betsileo

# 7. Start the API server
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Verify:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/dialects/
```

Open the real-time UI: http://localhost:8000/live

---

## 8. Docker — CPU (CI / no GPU)

Used in CI pipelines and on machines without an NVIDIA GPU. Image: `python:3.10-slim` with PyTorch CPU wheels (~200 MB final image).

```bash
# Build CPU image
docker build -f Dockerfile -t mgvaovao:cpu-latest .

# Start API (CPU only)
docker-compose -f docker-compose.yml -f docker-compose.cpu.yml up -d api

# Start Gradio demo
docker-compose -f docker-compose.yml -f docker-compose.cpu.yml up -d gradio
```

---

## 9. Docker — GPU (primary)

The primary image is `pytorch/pytorch:2.1.2-cuda11.8-cudnn8-runtime` (~3.75 GB). **First pull takes time** — use Cloud Build for CI to avoid extracting the CUDA layer locally.

```bash
# Build GPU image locally (requires NVIDIA Container Toolkit)
docker build -f Dockerfile.cuda -t mgvaovao:cuda-latest .

# Or build via Google Cloud Build (faster, avoids WSL2 layer extraction)
gcloud builds submit --config cloudbuild.yaml .

# Start API server (GPU)
docker-compose up -d api

# Start Gradio demo (no GPU needed — uses api:8000 over Docker network)
docker-compose up -d gradio

# Training jobs (run-and-exit containers)
docker-compose run --rm seed          # initialize dataset structure
docker-compose run --rm preprocess    # raw → train/val/test splits
docker-compose run --rm train-nllb    # fine-tune NLLB
docker-compose run --rm train-tts     # fine-tune TTS
docker-compose run --rm evaluate      # evaluate models
```

**Override dialect or Whisper size at runtime:**
```bash
DIALECT=sakalava docker-compose run --rm train-nllb
MGVAOVAO_WHISPER_MODEL_SIZE=medium docker-compose up api
```

**Check logs:**
```bash
docker-compose logs -f api
docker-compose logs -f gradio
```

---

## 10. API Reference

Base URL (local): `http://localhost:8000`

### Health

```
GET /health     →  {"status": "ok"}
GET /ready      →  {"status": "ready", "dialects_loaded": [...]}
```

`/ready` returns 503 until all dialect pipelines are loaded (models downloaded on first run).

### Dialects

```
GET /dialects/
```

Response:
```json
[
  {
    "key": "plt_latn",
    "name": "Malagasy Officiel",
    "region": "Hautes Terres — Antananarivo",
    "nllb_target": "plt_Latn",
    "has_nllb_lora": false,
    "has_tts_checkpoint": false
  },
  ...
]
```

### Audio translation (batch)

```
POST /translate/audio?dialect=betsileo&src_lang=fr
Content-Type: multipart/form-data
Body: file=<WAV or MP3>
```

Response:
```json
{
  "source_text": "Bonjour tout le monde",
  "malagasy_text": "Miarahaba anareo rehetra",
  "audio_url": "/translate/audio/abc123.wav",
  "latency_ms": 1240
}
```

### Text translation (batch)

```
POST /translate/text
Content-Type: application/json
Body: {"text": "Hello world", "dialect": "betsileo", "src_lang": "en"}
```

Response:
```json
{
  "source_text": "Hello world",
  "malagasy_text": "Miarahaba izao tontolo izao",
  "audio_url": "/translate/audio/def456.wav",
  "latency_ms": 890
}
```

### Download synthesized audio

```
GET /translate/audio/{filename}    →  WAV file (16 kHz mono)
```

---

## 11. WebSocket Streaming

Endpoint: `ws://localhost:8000/ws/stream/{dialect}?src_lang=fr`

`dialect`: one of `plt_latn`, `betsileo`, `betsimisaraka`, `sakalava`  
`src_lang` (optional): `fr`, `en`, `de`, `es`, `it`, `pt` — auto-detected if omitted

### Protocol

**Client → Server:** binary frames, Float32 PCM, 16 kHz, mono, 512 samples per frame (32 ms).

**Server → Client:** JSON text frames:

```jsonc
// Every 512-sample chunk:
{"type": "vad", "state": "SPEAKING", "prob": 0.94}

// When end-of-speech detected (silence ≥ 500 ms):
{"type": "processing"}

// After pipeline completes:
{
  "type": "result",
  "source_text": "Good morning",
  "malagasy_text": "Manao ahoana ny maraina",
  "audio_b64": "<base64-encoded WAV>",
  "latency_ms": 1100
}

// On error:
{"type": "error", "detail": "..."}
```

### VAD state machine

```
IDLE ──► SPEAKING ──► TRAILING ──► (emit audio) ──► IDLE
              │                         │
              └─ silence < 500 ms ──────┘
              └─ speech > 30 s (hard cap) → force emit
```

### Minimal JavaScript client

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/stream/betsileo?src_lang=fr");
ws.binaryType = "arraybuffer";

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  if (msg.type === "result") {
    const audio = new Audio("data:audio/wav;base64," + msg.audio_b64);
    audio.play();
  }
};

// Send Float32 PCM at 16 kHz, 512 samples per frame
function sendChunk(float32Array) {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(float32Array.buffer);
  }
}
```

---

## 12. Real-Time Browser UI

Open http://localhost:8000/live after starting the API server.

Features:
- Dialect selector (populated from `/dialects/`)
- Source language selector
- VAD probability bar (animates in real-time)
- VAD state chip (IDLE / SPEAKING / TRAILING)
- Source transcript panel
- Malagasy translation panel
- Latency breakdown table
- Activity log

The UI uses the AudioWorklet API for low-latency microphone capture (128-sample blocks forwarded to a 512-sample accumulator before sending over WebSocket). No file upload — VAD triggers processing automatically on silence.

**Browser requirements:** Chrome or Edge (AudioWorklet support required). Firefox partial support.

---

## 13. Training Pipeline

All training scripts are in `training/`. They can be run directly, via the installed CLI entry points, or as Docker Compose one-shot containers.

### Step 0 — Seed dataset structure

Creates the expected folder layout and a few demo translation pairs:

```bash
# Direct
python -m training.seed --dialect betsileo

# CLI entry point (after pip install -e .)
mgvaovao-seed --dialect betsileo

# Docker
docker-compose run --rm seed
```

Creates:
```
dataset/
├── nllb_finetune/betsileo/
│   ├── raw/fr/         ← drop JSONL files here: {"src": "...", "tgt": "..."}
│   ├── raw/en/
│   ├── processed/
│   └── reference/eval_fixed_200.csv
└── tts_finetune/betsileo/
    ├── raw_audio/       ← drop WAV files + metadata.csv here
    └── processed_audio/
```

### Step 1 — Preprocess

Converts raw annotator data into train/val/test splits:

```bash
python -m training.preprocess --dialect betsileo

# Or: download from GCS first (if data is remote)
docker-compose run --rm preprocess-download
docker-compose run --rm preprocess
```

NLLB input format (`raw/fr/*.jsonl`, one JSON object per line):
```json
{"src": "Bonjour tout le monde", "tgt": "Miarahaba anareo rehetra"}
```

TTS input: WAV files (16 kHz mono) in `raw_audio/` + a `metadata.csv`:
```
filename,text
phrase_001.wav,Miarahaba anareo rehetra
phrase_002.wav,Misaotra betsaka
```

Split ratio: 80% train / 10% val / 10% test. Minimum 80 samples for TTS.

### Step 2a — Fine-tune NLLB

LoRA fine-tuning on NLLB-200-distilled-600M:

```bash
python -m training.train_nllb --dialect betsileo

# Override hyperparameters
python -m training.train_nllb \
  --dialect betsileo \
  --epochs 10 \
  --batch 2 \
  --lr 3e-4
```

Key hyperparameters (configurable via env vars or CLI):

| Parameter | Default | Env var |
|---|---|---|
| LoRA rank | 16 | `MGVAOVAO_NLLB_LORA_R` |
| LoRA alpha | 32 | `MGVAOVAO_NLLB_LORA_ALPHA` |
| Target modules | `q_proj, v_proj` | `MGVAOVAO_NLLB_LORA_TARGET_MODULES` |
| Epochs | 5 | `MGVAOVAO_NLLB_TRAIN_EPOCHS` |
| Batch size | 1 | `MGVAOVAO_NLLB_BATCH_SIZE` |
| Gradient accumulation | 8 | `MGVAOVAO_NLLB_GRAD_ACCUM` |
| Learning rate | 5e-4 | `MGVAOVAO_NLLB_LR` |
| FP16 | true | `MGVAOVAO_NLLB_FP16` |

Checkpoint saved to: `checkpoints/nllb_{dialect}/`

### Step 2b — Fine-tune TTS

VITS fine-tuning on MMS-TTS-MLG:

```bash
python -m training.train_tts --dialect betsileo

# Override
python -m training.train_tts \
  --dialect betsileo \
  --epochs 100 \
  --lr 5e-5
```

Checkpoint saved to: `checkpoints/tts_{dialect}/`

### Step 3 — Evaluate

```bash
python -m training.evaluate --dialect betsileo
```

Outputs:
- `eval_results.csv` — chrF++ scores (NLLB), listening-test WAVs (TTS)
- Console report comparing baseline vs fine-tuned model
- WAVs saved to `eval_audio/`

---

## 14. Fine-Tuning Guide

### NLLB — what to expect

- Baseline chrF++ (en→plt_Latn): ~47–52 before fine-tuning
- Expected gain with 3 000 sentence pairs: +2 to +8 chrF++ points
- Fine-tuning time on L4 Spot (5 epochs, batch=1, grad_accum=8): ~$1.68–$3.48

### TTS — what to expect

- Minimum viable dataset: **80 sentences** (per `ylacombe/finetune-hf-vits` README)
- Target: 200+ sentences for robust dialect adaptation
- Fine-tuning time on L4 Spot (50 epochs): ~$0.56–$1.16
- UTMOS improvement typically +0.3–0.8 points

### Using fine-tuned checkpoints

The inference pipeline loads fine-tuned adapters automatically at startup if the checkpoint directory exists:

```
checkpoints/nllb_betsileo/      ← NLLB LoRA adapter files
checkpoints/tts_betsileo/       ← TTS VITS checkpoint
```

If the directory is absent, the base pre-trained model is used. No code change needed.

### Uploading checkpoints to GCS (for Cloud Run)

```bash
gsutil -m cp -r checkpoints/nllb_betsileo/ gs://mgvaovao-models/nllb_lora_v1/
gsutil -m cp -r checkpoints/tts_betsileo/  gs://mgvaovao-models/mms_tts_betsileo_v1/
```

The Cloud Run container must mount or download these at startup (configure in `cloudrun_inference.yaml`).

---

## 15. GCP Deployment

### Build and push CUDA image (Cloud Build)

```bash
gcloud builds submit --config cloudbuild.yaml .
```

This builds `Dockerfile.cuda` and pushes two tags to Artifact Registry:
- `cuda-{SHORT_SHA}` (immutable, per-commit)
- `cuda-latest` (rolling)

Machine: `E2_HIGHCPU_8` (~8 min build). No local Docker required.

### Deploy to Cloud Run GPU

```bash
gcloud run services replace deploy/cloudrun_inference.yaml \
  --region us-central1
```

Key specs (`cloudrun_inference.yaml`):
- Machine: `g2-standard-8` (8 vCPU, 32 GB RAM)
- GPU: NVIDIA L4, `--no-gpu-zonal-redundancy`
- Scaling: min 1 instance, max 4 instances
- Startup probe: 60 s timeout (model loading)
- WebSocket support: `--session-affinity`

**Cold start** is ~20–30 s (models loaded from GCS). Cloud Scheduler pings every 15 min to keep it warm.

### Launch a Vertex AI training job

```bash
gcloud ai custom-jobs create \
  --region=us-central1 \
  --display-name="nllb-finetune-betsileo" \
  --config=deploy/vertex_training.yaml
```

Specs (`vertex_training.yaml`):
- Machine: `n1-standard-8` + NVIDIA Tesla T4
- Spot: yes (~60% cheaper)
- GCS bucket mounted at `/mgvaovao/dataset` and `/mgvaovao/checkpoints`
- Checkpoint auto-saved to GCS every 30 min

### GCS bucket layout

```
gs://mgvaovao-models/
├── nllb_lora_v1/           NLLB LoRA adapter (~200 MB)
├── nllb_lora_betsileo_v1/
├── mms_tts_plt_latn_v1/    TTS checkpoint (~145 MB)
└── mms_tts_betsileo_v1/

gs://mgvaovao-datasets/
├── raw/                    Annotator uploads (JSONL + WAV)
├── processed/              Train/val/test splits
├── reference/
│   └── eval_fixed_200.csv  Fixed evaluation set (drift monitoring)
└── eval_fixed/
```

---

## 16. Environment Variables

All variables use the `MGVAOVAO_` prefix. Copy `.env.example` and override as needed.

| Variable | Default | Description |
|---|---|---|
| `MGVAOVAO_DEVICE` | `cuda` | `cuda` or `cpu` |
| `MGVAOVAO_WHISPER_MODEL_SIZE` | `small` | `tiny` `base` `small` `medium` `large` |
| `MGVAOVAO_API_HOST` | `0.0.0.0` | Uvicorn bind host |
| `MGVAOVAO_API_PORT` | `8000` | Uvicorn bind port |
| `MGVAOVAO_API_WORKERS` | `1` | Uvicorn workers (keep 1 with GPU) |
| `MGVAOVAO_NLLB_MODEL_NAME` | `facebook/nllb-200-distilled-600M` | HuggingFace model ID |
| `MGVAOVAO_NLLB_LORA_R` | `16` | LoRA rank |
| `MGVAOVAO_NLLB_TRAIN_EPOCHS` | `5` | Training epochs |
| `MGVAOVAO_NLLB_BATCH_SIZE` | `1` | Per-device batch size |
| `MGVAOVAO_NLLB_LR` | `5e-4` | Learning rate |
| `MGVAOVAO_TTS_MODEL_NAME` | `facebook/mms-tts-mlg` | HuggingFace TTS model ID |
| `MGVAOVAO_TTS_TRAIN_EPOCHS` | `50` | TTS fine-tuning epochs |
| `MGVAOVAO_VAD_THRESHOLD` | `0.5` | Silero VAD speech probability threshold |
| `MGVAOVAO_VAD_MIN_SPEECH_MS` | `250` | Min speech duration (batch VAD) |
| `MGVAOVAO_VAD_MIN_SILENCE_MS` | `100` | Min silence between segments (batch VAD) |
| `MGVAOVAO_VAD_STREAM_MIN_SILENCE_MS` | `500` | Silence needed to trigger end-of-utterance (streaming VAD) |
| `DIALECT` | `betsileo` | Default dialect for Docker Compose training commands |

Paths (override only if not using Docker volumes):

| Variable | Default |
|---|---|
| `MGVAOVAO_ROOT_DIR` | `/mgvaovao` |
| `MGVAOVAO_CHECKPOINTS_DIR` | `/mgvaovao/checkpoints` |
| `MGVAOVAO_DATASET_DIR` | `/mgvaovao/dataset` |
| `MGVAOVAO_HF_CACHE_DIR` | `/mgvaovao/.cache/huggingface` |

---

## 17. MLOps & Monitoring

### Automated training trigger

A GCS upload event to `gs://mgvaovao-datasets/processed/` triggers a Cloud Pub/Sub message (`dataset-ready` topic), which launches a Vertex AI Kubeflow pipeline with these steps:

1. `data_validation` — schema check, min-sample guard
2. `nllb_finetune` — LoRA training on L4 Spot
3. `tts_finetune` — VITS fine-tuning per dialect on L4 Spot
4. `evaluate` — chrF++ vs champion model; UTMOS vs baseline
5. `register` — push to Vertex AI Model Registry (candidate → staging → prod)
6. `deploy` — Cloud Build blue/green deploy to Cloud Run GPU; auto-rollback on health-check failure

### Drift monitoring

Cloud Scheduler triggers weekly evaluation against `eval_fixed_200.csv` (fixed 200-sentence reference set, never changes). Thresholds:

| Metric | Alert threshold | Automatic action |
|---|---|---|
| chrF++ (NLLB) | Drop > 2 points | Trigger NLLB re-fine-tuning via Pub/Sub |
| UTMOS (TTS) | Drop > 0.3 | Trigger TTS re-fine-tuning via Pub/Sub |
| Pipeline error rate | > 5% | Email alert + infra investigation |
| P95 latency | > 2 000 ms | Email alert + Cloud Monitoring investigation |

All training runs are tracked in **Vertex AI Experiments** (free).

### Pre-warming

Cloud Scheduler pings the Cloud Run GPU service every 15 min to prevent cold starts during active hours. Scale-to-zero is preserved during nights/weekends.

---

## 18. Cost Reference

Beta phase (< 100 users/day):

| Item | Monthly cost |
|---|---|
| Cloud Run GPU L4 (50 h active) | $33.60 |
| Vertex AI Monitoring | $3.00 |
| Vertex AI Training (2 runs/month) | $2.24 |
| Cloud Run CPU (signaling) | $2.00 |
| Google Cloud Storage (50 GB) | $1.00 |
| Vertex AI Pipelines | $0.12 |
| Artifact Registry | $0.50 |
| Vertex Experiments + Registry | $0.00 |
| Cloud Build CI/CD | $0.00 |
| **Total** | **~$42/month** |

Cost scales with usage. Migration to Vertex AI Endpoint recommended above 500 users/day.

---

## 19. Roadmap

| Phase | Status | Deliverables |
|---|---|---|
| Phase 1 — Baseline | Done | VAD→ASR→NLLB→TTS pipeline · WebSocket streaming · Real-time browser UI · Docker images |
| Phase 2 — Cloud Deploy | In progress (Q2 2026) | Cloud Run GPU L4 · GCS buckets · Vertex AI Pipeline first run · Model Registry |
| Phase 3 — Fine-Tuning v1 | Planned Q2–Q3 2026 | 3 000 FR/EN↔MG sentence pairs · NLLB LoRA fine-tuned · 200 audio sentences · MMS-TTS Officiel fine-tuned · chrF++ and UTMOS published |
| Phase 4 — Multi-dialect | Planned Q3–Q4 2026 | 200 sentences × 3 dialects · 3 dialect TTS checkpoints · Drift monitoring live · Flutter mobile app v1 |
| Phase 5 — Scale | 2027 | Public REST API · 6 full dialects · NLLB-200 1.3B (if budget) · Vertex AI Endpoint migration |

---

## 20. License

Model licenses:
- **NLLB-200** and **MMS-TTS-MLG**: CC-BY-NC 4.0 — free for non-commercial use (compatible with NGO/association use)
- **Whisper**: Apache 2.0
- **Silero VAD**: MIT

Application code: contact tsanta@mgvaovao.com

---

*MGVaovao — Maison du Numérique · Ambatonakanga, Antananarivo · mgvaovao.com*
