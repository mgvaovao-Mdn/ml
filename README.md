# MGVaovao — Malagasy Multilingual Speech-to-Speech Translation Pipeline

Real-time speech-to-speech translation from six international languages into Malagasy dialects.  
**Input:** spoken audio in FR · EN · DE · ES · IT · PT  
**Output:** Malagasy speech, dialect-specific, streamed back automatically via WebRTC / WebSocket.

Built for [Maison du Numérique](https://mgvaovao.com) — a non-profit bringing digital inclusion to Madagascar.  
Architecture and engineering: tsanta@mgvaovao.com

---

## Table of Contents

1. [What This Is](#1-what-this-is)
2. [Supported Dialects & Use Cases](#2-supported-dialects--use-cases)
3. [Model Stack](#3-model-stack)
4. [Why These Specific Models — Full Exclusion Tables](#4-why-these-specific-models--full-exclusion-tables)
5. [Architecture Overview](#5-architecture-overview)
6. [Cascade Architecture: Design Rationale](#6-cascade-architecture-design-rationale)
7. [WebRTC Real-Time Transport](#7-webrtc-real-time-transport)
8. [Project Structure](#8-project-structure)
9. [Prerequisites](#9-prerequisites)
10. [Local Development (no Docker)](#10-local-development-no-docker)
11. [Docker — CPU (CI / no GPU)](#11-docker--cpu-ci--no-gpu)
12. [Docker — GPU (primary)](#12-docker--gpu-primary)
13. [API Reference](#13-api-reference)
14. [WebSocket Streaming](#14-websocket-streaming)
15. [Real-Time Browser UI](#15-real-time-browser-ui)
16. [Training Pipeline](#16-training-pipeline)
17. [Fine-Tuning Guide](#17-fine-tuning-guide)
18. [GCP Deployment — Complete Step-by-Step Guide](#18-gcp-deployment--complete-step-by-step-guide)
    - [18.0 Infrastructure Overview](#180--gcp-infrastructure-overview)
    - [18.1 One-Time Project Setup](#181--one-time-gcp-project-setup)
    - [18.2 Build the Inference Image](#182--build-the-inference-docker-image)
    - [18.3 Deploy to Cloud Run GPU](#183--deploy-to-cloud-run-gpu)
    - [18.4 Logs & Debugging](#184--cloud-run-logs--debugging)
    - [18.5 Managing Checkpoints](#185--managing-fine-tuned-checkpoints)
    - [18.6 Vertex AI Training Jobs](#186--vertex-ai-custom-training-jobs)
    - [18.7 GitHub Auto-Trigger](#187--github--cloud-build-automatic-trigger-optional)
    - [18.8 Local Testing with Mock Server](#188--local-testing-with-mock-server-before-building)
    - [18.9 Known Issues & Fixes](#189--known-issues--fixes-applied)
    - [18.10 Variables & Migration Checklist](#1810--complete-variables--migration-checklist)
    - [18.11 Migration to New GCP Project](#1811--migration-to-a-new-gcp-project)
19. [Environment Variables](#19-environment-variables)
20. [MLOps & Monitoring](#20-mlops--monitoring)
21. [Cost Reference](#21-cost-reference)
22. [Roadmap](#22-roadmap)
23. [Feasibility & Risk Matrix](#23-feasibility--risk-matrix)
24. [Technical References](#24-technical-references)
25. [License](#25-license)

---

## 1. What This Is

MGVaovao translates foreign-language audio (YouTube videos, podcasts, live speech) into spoken Malagasy automatically — no button required. The user selects a source language and target dialect; the system detects speech, transcribes it, translates it, and synthesizes the audio in the chosen dialect.

**Primary use case:** a YouTube video in English is inaccessible to the majority of Malagasy speakers. This system translates and delivers the audio automatically in the chosen dialect — the user simply selects language and dialect, and translation happens without clicking any button.

The pipeline is a **four-stage cascade**:

```
Audio in  →  [VAD]  →  [ASR]  →  [NLLB MT]  →  [TTS]  →  WAV out
              Silero    Whisper    NLLB-200       MMS-TTS
              VAD v5    turbo      distilled-600M  MLG (VITS)
```

Every stage is independently fine-tuneable. The architecture is intentionally modular: swap out any component without touching the others.

> No end-to-end speech-to-speech system for Malagasy existed publicly as of April 2026. Comprehensive exclusion tables for all evaluated alternatives are in [§4](#4-why-these-specific-models--full-exclusion-tables).

---

## 2. Supported Dialects & Use Cases

| Dialect key | Display name | Region | Est. speakers |
|---|---|---|---|
| `plt_latn` | Malagasy Officiel | Hautes Terres — Antananarivo | National reference |
| `betsileo` | Betsileo | Fianarantsoa — Southern Highlands | ~1.5 M |
| `betsimisaraka` | Betsimisaraka | East Coast — Toamasina | ~1.5 M |
| `sakalava` | Sakalava | West Coast — Mahajanga / Toliara | ~1 M |
| `antandroy` | Antandroy | Grand Sud — Ambovombe | ~800 K |
| `merina` | Merina | Imerina — Central Highlands | ~4 M |

Source languages supported: `fr`, `en`, `de`, `es`, `it`, `pt` (auto-detected by Whisper if not specified).

**Representative use cases:**

- English documentary → redelivered in Betsimisaraka (East Coast)
- French online course → accessible in Betsileo (Fianarantsoa)
- International speech in real-time → translated into Sakalava (West Coast)
- Foreign news content → in Malagasy Officiel for nationwide access

**Prototyping platforms:** dedicated web app in Next.js + Python (user validation), and Kaggle (T4 × 2 GPU, 30 h/week free) for hyperparameter exploration during fine-tuning.

---

## 3. Model Stack

| Stage | Model | Licence | VRAM (INT8) | Fine-tunable |
|---|---|---|---|---|
| VAD | Silero VAD v5 | MIT | 0 (CPU only) | Not needed |
| ASR | Whisper large-v3-turbo | Apache 2.0 | ~1.7 GB | Optional |
| Translation | NLLB-200-distilled-600M | CC-BY-NC 4.0 | ~0.7 GB | **Yes — high priority** |
| TTS | MMS-TTS-MLG (VITS) | CC-BY-NC 4.0 | ~0.5 GB / checkpoint | **Yes — per dialect** |

### VRAM allocation — NVIDIA L4 24 GB

| Component | VRAM |
|---|---|
| Whisper large-v3-turbo INT8 | 1.7 GB |
| NLLB-200-distilled-600M INT8 | 0.7 GB |
| 6 × TTS dialect checkpoints | 3.0 GB |
| CUDA overhead | 0.8 GB |
| **Total used** | **6.2 GB** |
| **Free headroom** | **17.8 GB** |

> 3–5 concurrent WebRTC/WebSocket sessions per instance · L4 Spot ~$0.28/h · fine-tuning via Vertex AI Training

### Fine-tunability summary

| Component | Model | Fine-tunable | Priority | Licence | Cost per run |
|---|---|---|---|---|---|
| VAD | Silero VAD v5 | Not needed | — | MIT | — |
| ASR | Whisper turbo | Yes (optional) | Low | Apache 2.0 | ~$2–5 |
| Translation | NLLB-200-600M | **Yes** | **High** | CC-BY-NC | ~$1.68–3.48 |
| TTS | MMS-TTS-MLG | **Yes** | **High** | CC-BY-NC | ~$0.56–1.16 |

### Model details

**Silero VAD v5** — 2 MB, MIT, CPU-only. Requires exactly 512 samples (32 ms) at 16 kHz. Universal, no language dependency. ~1 ms/chunk latency.

**Whisper large-v3-turbo** — best open-source multilingual ASR, 99 languages, INT8 via CTranslate2 at ~1.7 GB VRAM. WER on French (FLEURS): ~4–6%. `vad_filter=True` runs VAD and ASR in parallel to reduce latency.

**NLLB-200-distilled-600M** — only open-source MT model with `plt_Latn` (Malagasy) in its tokenizer and FLORES-200 test set. LoRA fine-tuneable (rank 16). chrF++ baseline: `en→plt_Latn` ~47–52, `fr→plt_Latn` ~42–48. CC-BY-NC is compatible with non-commercial NGO use.

**MMS-TTS-MLG (VITS)** — the **only** viable open-source TTS model for Malagasy as of 2026. ~83 M parameters, 16 kHz output. Fine-tuneable with as few as 80–150 sentences via [`ylacombe/finetune-hf-vits`](https://github.com/ylacombe/finetune-hf-vits). ~0.5 GB VRAM per dialect checkpoint.

---

## 4. Why These Specific Models — Full Exclusion Tables

No system was chosen by default. Every major commercial and open-source alternative was evaluated. The tables below document the full exclusion rationale.

### 4.1 — Speech-to-Speech systems (S2S)

| System | Developer | Malagasy status | Exclusion reason |
|---|---|---|---|
| SeamlessM4T v2 | Meta AI | Absent | `plt_Latn` absent from 96 target languages — `ValueError` confirmed |
| SeamlessM4T-medium | Meta AI | Absent | Same NLLB backbone — same limitation |
| SeamlessExpressive | Meta AI | Absent | 6 languages only (FR/EN/ES/DE/ZH/PT) |
| AudioPaLM | Google | Absent | Not publicly available — internal research |
| Translatotron 2/3 | Google | Absent | Not publicly available — internal research |
| SpeechX | Microsoft | Absent | Not publicly available |
| USM (Universal Speech Model) | Google | ASR only | ASR only — no Malagasy TTS integrated |

### 4.2 — Text-to-Speech systems (TTS)

| System | Developer | Malagasy | Fine-tuneable | Primary limitation |
|---|---|---|---|---|
| Google Cloud TTS | Google | Absent | No (closed API) | No Malagasy voice in GCP catalog |
| Amazon Polly | Amazon | Absent | No (closed API) | Malagasy absent — no published roadmap |
| Azure Neural TTS | Microsoft | Absent | No (closed API) | Absent from Azure catalog (140+ languages) |
| OpenAI TTS | OpenAI | Absent | No | 6 multilingual voices — no Malagasy |
| ElevenLabs | ElevenLabs | Absent | Voice clone only | 32 languages — Malagasy absent |
| Bark (Suno AI) | Suno AI | Partial, unstable | Not published | Uncontrolled outputs — no stable MG support |
| XTTS v2 (Coqui) | Coqui AI | Absent | Yes (if data) | 17 languages only — requires ~6 h audio |
| Parler-TTS | HuggingFace | Absent | Yes, Apache 2.0 | Requires 5–10 h Malagasy audio — long-term alternative |
| **MMS-TTS-MLG (Meta)** | Meta AI | **Present** | **Yes, CC-BY-NC** | ✅ **Selected — only viable system** |

### 4.3 — Machine Translation systems (MT)

| System | Licence | Malagasy | Primary limitation |
|---|---|---|---|
| **NLLB-200-600M / 1.3B / 3.3B (Meta)** | CC-BY-NC 4.0 | Yes — `plt_Latn` | ✅ **Selected — LoRA fine-tuneable, NGO-compatible** |
| MADLAD-400 7B (Google) | Apache 2.0 | Yes — `mdy` | 7B params — VRAM ~14 GB — too heavy for L4 |
| Google Cloud Translation API | Paid API | Yes | $20/1 M chars — fine-tuning impossible — vendor lock-in |
| DeepL API | Paid API | Absent | 32 languages only — Malagasy absent |
| M2M-100 (Meta) | MIT | Yes — `mg` | Less accurate than NLLB on low-resource languages |
| mBART-50 (Meta) | MIT | Absent | 50 languages — Malagasy absent |
| Gemini / GPT-4 | Paid API | Partial | Variable quality on MG — high cost — no fine-tuning |

### 4.4 — Automatic Speech Recognition systems (ASR)

| System | Licence | Languages | Status and limitation |
|---|---|---|---|
| **Whisper large-v3-turbo (OpenAI)** | Apache 2.0 | 99 | ✅ **Selected — multilingual, open-source, INT8, fine-tuneable** |
| Whisper distil-fr (bofenghuang) | MIT | FR only | WER FR 5.40% FLEURS — for French-only demo |
| Google Chirp 3 (GCP API) | GCP API — $0.96/hr | 125 | Native Vertex AI — no dedicated ASR GPU — full-GCP alternative |
| NVIDIA Canary 1B v2 | Apache 2.0 | 4 | Best open-source WER FR 4.86% — but 4 languages only |
| Deepgram Nova-3 | Paid API — $0.31/hr | 36 | Option if L4 GPU cost exceeds API cost |
| MMS ASR (`facebook/mms-300m`) | CC-BY-NC | 1162 incl. `mlg` | Useful if source audio is Malagasy (future use) — not retained v1 |
| Azure Speech | Paid API | 100+ | Performant — expensive — vendor lock-in |

> **Conclusion:** The cascaded ASR → Translation → TTS architecture is the only viable path for Malagasy in 2026. It is also the most modular for component-by-component fine-tuning.

---

## 5. Architecture Overview

### 5.1 — AI inference pipeline

```mermaid
flowchart TD
    INPUT["🎙️ AUDIO INPUT\nFR · EN · DE · ES · IT · PT\nMicrophone · YouTube · Uploaded file\nAuto language detection — 99 languages"]

    subgraph STAGE0["STAGE 0 — Voice Activity Detection"]
        VAD["Silero VAD v5\n32 ms chunks · MIT · CPU only\n~2 MB · ~1 ms/chunk\nNo fine-tuning required"]
    end

    subgraph STAGE1["STAGE 1 — Automatic Speech Recognition"]
        ASR["Whisper large-v3-turbo INT8\nApache 2.0 · 99 languages\nVRAM ~1.7 GB · CTranslate2\nOptional fine-tuning"]
    end

    subgraph STAGE2["STAGE 2 — Neural Machine Translation"]
        MT["NLLB-200-distilled-600M INT8\nCC-BY-NC 4.0 · 600M parameters\nVRAM ~0.7 GB · chrF++ baseline 42–52\nLoRA rank=16 — HIGH PRIORITY"]
    end

    subgraph STAGE3["STAGE 3 — Dialectal Text-to-Speech"]
        TTS["MMS-TTS-MLG VITS · Meta\nCC-BY-NC 4.0 · ~83M parameters\nVRAM ~0.5 GB/checkpoint · 16 kHz\nFine-tuning per dialect — HIGH PRIORITY"]
    end

    subgraph DIALECTS["Dialect checkpoints (up to 18)"]
        D1["🗣️ Malagasy Officiel\nplt_Latn"]
        D2["🗣️ Merina\nHighlands"]
        D3["🗣️ Betsileo\nFianarantsoa"]
        D4["🗣️ Betsimisaraka\nEast Coast"]
        D5["🗣️ Sakalava\nWest Coast"]
        D6["🗣️ Antandroy\nGrand Sud"]
    end

    OUTPUT["🔊 WAV 16 kHz\nAutomatic playback on client"]

    INPUT --> STAGE0
    STAGE0 -->|"Speech segments"| STAGE1
    STAGE1 -->|"Source text"| STAGE2
    STAGE2 -->|"Malagasy text plt_Latn"| STAGE3
    STAGE3 --> D1 & D2 & D3 & D4 & D5 & D6
    D1 & D2 & D3 & D4 & D5 & D6 --> OUTPUT

    classDef inputOutput fill:#1a3a5c,color:#fff,stroke:#0d2035
    classDef vadStyle fill:#e67e22,color:#fff,stroke:#d35400
    classDef asrStyle fill:#2980b9,color:#fff,stroke:#1a5276
    classDef mtStyle fill:#27ae60,color:#fff,stroke:#1d7a44
    classDef ttsStyle fill:#8e44ad,color:#fff,stroke:#6c3483
    classDef dialectStyle fill:#16a085,color:#fff,stroke:#0e6655

    class INPUT,OUTPUT inputOutput
    class VAD vadStyle
    class ASR asrStyle
    class MT mtStyle
    class TTS ttsStyle
    class D1,D2,D3,D4,D5,D6 dialectStyle
```

### 5.2 — Google Cloud Platform (production)

```mermaid
flowchart LR
    CLIENT["💻 Client Web / Mobile\nNext.js + Python\nVercel Deploy"]

    subgraph GCP["Google Cloud Platform"]

        subgraph SIGNALING["Cloud Run CPU — WebRTC Signaling"]
            SIG["WebRTC Signaling\nFastAPI · Scale-to-zero\n~$2/month\nPOST /offer → Answer SDP"]
        end

        subgraph GPU_BLOCK["Cloud Run GPU — NVIDIA L4 24 GB"]
            PIPE["Inference Pipeline\nVAD + ASR + MT + TTS\n~$33/month · Scale-to-zero\ng2-standard-8 · 8 vCPU · 32 GB RAM\nCold start ~20–30s · pre-warmed"]
        end

        subgraph STORAGE["Google Cloud Storage"]
            GCS_MOD["gs://mgvaovao-models/\nnllb_lora_v* · ~200 MB\nmms_tts_{dialect}_v* · ~145 MB\nVersioning enabled"]
            GCS_DATA["gs://mgvaovao-datasets/\nraw/ · processed/ · reference/\neval_fixed_200.csv"]
        end

        subgraph MLOPS_BLOCK["MLOps — Vertex AI"]
            PUBSUB["Cloud Pub/Sub\nEvent bus · At-least-once\ntopic: dataset-ready"]
            PIPELINE["Vertex AI Pipeline\nKubeflow DAG · $0.03/run\n6 steps: validate→FT→eval→register→deploy"]
            TRAINING["Vertex Custom Training\nL4 Spot ~$0.28/hr\nNLLB LoRA r=16 · TTS VITS"]
            REGISTRY["Model Registry\ncandidate → staging → prod\nFree · 1-click rollback"]
            MONITORING["Vertex AI Monitoring\n~$3/month · weekly\nchrF++ & UTMOS drift"]
            CLOUDBUILD["Cloud Build\nBlue/Green Deploy\nZero downtime · auto-rollback"]
        end

        SCHEDULER["⏰ Cloud Scheduler\nPre-warm ping every 15 min\nWeekly drift evaluation"]
    end

    STUN["🌐 STUN/TURN\nCloudflare"]

    CLIENT -->|"POST /offer SDP"| SIG
    SIG -->|"Answer SDP + session_id"| CLIENT
    CLIENT <-->|"ICE candidates"| STUN
    SIG <-->|"Opus audio 32 ms"| PIPE
    PIPE <-->|"WAV 16 kHz + MG text"| CLIENT
    PIPE <-->|"Load models / save checkpoints"| GCS_MOD
    GCS_DATA -->|"upload event"| PUBSUB
    PUBSUB -->|"trigger pipeline"| PIPELINE
    PIPELINE --> TRAINING --> REGISTRY --> CLOUDBUILD --> PIPE
    SCHEDULER -->|"trigger eval"| MONITORING
    MONITORING -->|"drift detected"| PUBSUB

    classDef clientStyle fill:#ea4335,color:#fff,stroke:#c62828
    classDef gcpService fill:#4285f4,color:#fff,stroke:#2d6bd6
    classDef storageStyle fill:#fbbc04,color:#333,stroke:#f9ab00
    classDef mlopsStyle fill:#34a853,color:#fff,stroke:#249345
    classDef stunStyle fill:#607d8b,color:#fff,stroke:#455a64
    classDef schedStyle fill:#ff9800,color:#333,stroke:#e65100

    class CLIENT clientStyle
    class SIG,PIPE gcpService
    class GCS_MOD,GCS_DATA storageStyle
    class PUBSUB,PIPELINE,TRAINING,REGISTRY,MONITORING,CLOUDBUILD mlopsStyle
    class STUN stunStyle
    class SCHEDULER schedStyle
```

### 5.3 — Latency breakdown (L4 GPU, warm)

| Stage | Latency |
|---|---|
| Silero VAD (end-of-speech detection) | 1–50 ms |
| Whisper large-v3-turbo INT8 (3 s audio) | 250–500 ms |
| NLLB-200-600M INT8 (short sentence) | 80–350 ms |
| MMS-TTS VITS (short sentence) | 150–450 ms |
| WebRTC / WebSocket encode + transport | 50–150 ms |
| **Total — first audio chunk (warm)** | **~700–1 500 ms** |

**Optimizations active:** `vad_filter=True` (VAD + ASR in parallel), `num_beams=2`, TTS checkpoints pre-loaded in VRAM, 32 ms chunks.

---

## 6. Cascade Architecture: Design Rationale

A cascade architecture decomposes a complex task into a series of specialized steps, each processing the output of the previous one. Every component is a separate AI model trained independently for a specific function.

| Stage | Component | Role | Input → Output |
|---|---|---|---|
| 0 — Voice detection | Silero VAD v5 | Detect active speech segments, ignore silence and noise | Continuous audio → Speech segments |
| 1 — Transcription | Whisper large-v3-turbo | Transcribe source audio to text in its original language | Audio segment → Source text |
| 2 — Translation | NLLB-200-distilled-600M | Translate source text to Official Malagasy (`plt_Latn`) | Source text → Malagasy text |
| 3 — Voice synthesis | MMS-TTS-MLG (VITS) | Synthesize Malagasy text as audio in the chosen dialect | Malagasy text → WAV 16 kHz |

### Advantages for MGVaovao

- **Modularity**: each component replaceable independently without touching the others
- **Targeted fine-tuning**: improve only the weakest link based on available data
- **Low-cost dialect expansion**: one additional TTS checkpoint per dialect
- **L4 GPU compatible**: total footprint ~6.2 GB — 17.8 GB headroom free
- **Observability**: chrF++ (translation) and UTMOS (TTS) metrics per component

### Known limitations

- **Error accumulation**: an ASR error propagates into MT then TTS — mitigation: `vad_filter=True`
- **Additive latency**: ~700–1 500 ms total — mitigation: 32 ms streaming chunks, `num_beams=2`, INT8
- **Fixed TTS voice**: output voice is that of the TTS model, not the original speaker

> These limitations are acceptable: the priority is content intelligibility and accessibility, not preserving the source speaker's timbre.

---

## 7. WebRTC Real-Time Transport

```mermaid
sequenceDiagram
    participant C as 💻 Client Web/Mobile
    participant SIG as ☁️ Cloud Run CPU<br/>WebRTC Signaling
    participant STUN as 🌐 STUN/TURN<br/>Cloudflare
    participant GPU as 🖥️ Cloud Run GPU L4<br/>VAD + ASR + MT + TTS

    C->>SIG: POST /offer {sdp, src_lang:'fr', dialect:'betsileo'}
    SIG->>GPU: Forward WebRTC offer
    GPU-->>SIG: Answer SDP
    SIG-->>C: Answer SDP + session_id
    C->>STUN: ICE candidates
    STUN->>GPU: ICE candidates
    Note over C,GPU: ✅ WebRTC established · transport latency ~80–200 ms

    C->>GPU: DataChannel config {src_lang:'en', dialect:'betsimisaraka'}
    Note over GPU: Pipeline reconfigured instantly — no reconnection

    loop Real-time streaming (VAD automatic — no button)
        C->>GPU: RTP Audio Opus — 32 ms chunks
        Note over GPU: Silero VAD → accumulation → end of sentence
        Note over GPU: Whisper INT8 → source text
        Note over GPU: NLLB INT8 {src}_Latn → plt_Latn
        Note over GPU: MMS-TTS {dialect} → WAV 16 kHz
        GPU-->>C: DataChannel: {malagasy_text, audio_b64, latencies}
        Note over C: 🔊 Automatic playback
    end
```

### GCP architecture flows — summary table

| Flow | Represented path | Key components |
|---|---|---|
| 2a | WebRTC connection | Client Web → Cloud Run CPU (Signaling) |
| 2b | Inference pipeline | Cloud Run CPU → Cloud Run GPU L4 (VAD+ASR+MT+TTS) |
| 2c | Model storage | Cloud Run GPU ↔ Google Cloud Storage |
| 2d | Training trigger | GCS Dataset → Pub/Sub → Vertex Pipeline |
| 2e | Model lifecycle | Vertex Training → Model Registry → Cloud Build → Deploy |
| 2f | Drift monitoring | Cloud Scheduler → Vertex Monitoring → Pub/Sub → Re-FT |

---

## 8. Project Structure

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

## 9. Prerequisites

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

## 10. Local Development (no Docker)

This is the recommended workflow for iterating on model code locally, especially on a machine with a GPU.

```bash
# 1. Clone
git clone https://github.com/mgvaovao-Mdn/ml.git
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

## 11. Docker — CPU (CI / no GPU)

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

## 12. Docker — GPU (primary)

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

## 13. API Reference

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
  }
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

## 14. WebSocket Streaming

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

```mermaid
flowchart LR
    IDLE(["⬜ IDLE"])
    SPEAKING(["🟢 SPEAKING"])
    TRAILING(["🟡 TRAILING"])
    EMIT(["🔵 EMIT\naudio buffer"])

    IDLE -->|"speech prob > 0.5"| SPEAKING
    SPEAKING -->|"silence < 500 ms"| TRAILING
    TRAILING -->|"speech resumes"| SPEAKING
    TRAILING -->|"silence ≥ 500 ms"| EMIT
    SPEAKING -->|"hard cap 30 s"| EMIT
    EMIT --> IDLE

    classDef idleStyle fill:#90a4ae,color:#fff,stroke:#607d8b
    classDef speakStyle fill:#43a047,color:#fff,stroke:#2e7d32
    classDef trailStyle fill:#fb8c00,color:#fff,stroke:#e65100
    classDef emitStyle fill:#1e88e5,color:#fff,stroke:#1565c0

    class IDLE idleStyle
    class SPEAKING speakStyle
    class TRAILING trailStyle
    class EMIT emitStyle
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

## 15. Real-Time Browser UI

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

## 16. Training Pipeline

All training scripts are in `training/`. They can be run directly, via CLI entry points, or as Docker Compose one-shot containers.

### Step 0 — Seed dataset structure

```bash
python -m training.seed --dialect betsileo
mgvaovao-seed --dialect betsileo        # CLI entry point
docker-compose run --rm seed            # Docker
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

```bash
python -m training.preprocess --dialect betsileo
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

```bash
python -m training.train_nllb --dialect betsileo

python -m training.train_nllb \
  --dialect betsileo \
  --epochs 10 \
  --batch 2 \
  --lr 3e-4
```

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

```bash
python -m training.train_tts --dialect betsileo

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

## 17. Fine-Tuning Guide

### NLLB — what to expect

- Baseline chrF++ (`en→plt_Latn`): ~47–52 before fine-tuning
- Expected gain with 3 000 sentence pairs: **+2 to +8 chrF++ points**
- Fine-tuning time on L4 Spot (5 epochs, batch=1, grad_accum=8): **~$1.68–$3.48**

### TTS — what to expect

- Minimum viable dataset: **80 sentences** (per `ylacombe/finetune-hf-vits` README — verified)
- Target: 200+ sentences for robust dialect adaptation
- Fine-tuning time on L4 Spot (50 epochs): **~$0.56–$1.16**
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

---

## 18. GCP Deployment — Complete Step-by-Step Guide

This section documents every step required to deploy MGVaovao from zero on Google Cloud Platform. It covers infrastructure setup, building the Docker image, deploying Cloud Run GPU, running training jobs on Vertex AI, and migrating to a new GCP project.

> **Audience:** ML engineers new to GCP. Every command is explained. No steps are skipped.

---

### 18.0 — GCP Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  Google Cloud Project: mgvaovao-ia  (region: us-central1)       │
│                                                                  │
│  ┌─────────────────┐    ┌──────────────────────────────────┐    │
│  │ Artifact Registry│    │  Cloud Run GPU (mgvaovao-inference)│   │
│  │  mgvaovao/       │───▶│  NVIDIA L4 · 8 vCPU · 32 GB RAM │    │
│  │  inference:latest│    │  min=0 / max=2 · port 8080       │    │
│  └─────────────────┘    └──────────────────────────────────┘    │
│                                         │                        │
│  ┌──────────────────┐                   ▼                        │
│  │  Cloud Build     │    ┌──────────────────────────────────┐    │
│  │  cloudbuild-     │    │  GCS: mgvaovao-ia-checkpoints    │    │
│  │  inference.yaml  │    │  tts_{dialect}/final/            │    │
│  └──────────────────┘    │  nllb_{dialect}/final/           │    │
│                          └──────────────────────────────────┘    │
│  ┌──────────────────┐                                            │
│  │  Vertex AI       │    ┌──────────────────────────────────┐    │
│  │  Custom Training │    │  GCS: mgvaovao-ia_cloudbuild     │    │
│  │  (NLLB + TTS FT) │    │  (Cloud Build source archives)   │    │
│  └──────────────────┘    └──────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

**What happens at deploy time:**
1. `cloudbuild-inference.yaml` builds `Dockerfile.cloudrun` — all 4 models are downloaded inside the image (~8 GB)
2. Image is pushed to Artifact Registry
3. Cloud Run is updated to the new image revision
4. On cold start, Cloud Run pulls checkpoints from GCS and loads all pipelines into GPU memory (~60–120 s)
5. `/ready` returns HTTP 200 — the UI unlocks

---

### 18.1 — One-Time GCP Project Setup

Run these commands **once** when creating a new project. Skip any step you have already done.

#### Step 1 — Install and initialize gcloud CLI

```bash
# Install: https://cloud.google.com/sdk/docs/install
# After installation, authenticate:
gcloud auth login                          # opens browser
gcloud auth application-default login      # for SDK libraries (Python)
```

#### Step 2 — Create or select a GCP project

```bash
# Option A: create a new project
gcloud projects create mgvaovao-ia --name="MGVaovao IA"

# Option B: use existing project
gcloud config set project mgvaovao-ia

# Verify
gcloud config get-value project            # should print: mgvaovao-ia
```

> **Note:** Billing must be enabled on the project before Cloud Run GPU can be used.  
> GCP Console → Billing → Link billing account to project.

#### Step 3 — Save your project number (needed for IAM)

```bash
gcloud projects describe mgvaovao-ia --format="value(projectNumber)"
# Expected output: 97374817504
```

Save this value — you need it in Step 6.

#### Step 4 — Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  storage.googleapis.com \
  aiplatform.googleapis.com \
  pubsub.googleapis.com \
  cloudscheduler.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  iam.googleapis.com \
  --project=mgvaovao-ia
```

This takes 1–3 minutes. Verify:

```bash
gcloud services list --enabled --project=mgvaovao-ia | grep -E "run|build|artifact|aiplatform"
```

#### Step 5 — Create Artifact Registry repository

Docker images are stored here (not in old Container Registry).

```bash
gcloud artifacts repositories create mgvaovao \
  --repository-format=docker \
  --location=us-central1 \
  --description="MGVaovao Docker images" \
  --project=mgvaovao-ia

# Verify
gcloud artifacts repositories list --project=mgvaovao-ia
# Expected: REPOSITORY=mgvaovao  FORMAT=DOCKER  LOCATION=us-central1
```

Image path convention:
```
us-central1-docker.pkg.dev/mgvaovao-ia/mgvaovao/inference:latest
us-central1-docker.pkg.dev/mgvaovao-ia/mgvaovao/inference:{SHORT_SHA}
```

#### Step 6 — Create GCS buckets

```bash
# Bucket for fine-tuned model checkpoints (pulled by Cloud Run at cold start)
gcloud storage buckets create gs://mgvaovao-ia-checkpoints \
  --location=us-central1 \
  --project=mgvaovao-ia

# Cloud Build uses its own bucket automatically (mgvaovao-ia_cloudbuild)
# It is created by Cloud Build on first use — no manual creation needed

# Verify
gcloud storage buckets list --project=mgvaovao-ia
# Expected: mgvaovao-ia-checkpoints  mgvaovao-ia_cloudbuild
```

GCS layout inside `mgvaovao-ia-checkpoints`:

```
gs://mgvaovao-ia-checkpoints/
├── tts_plt_latn/final/         ← VitsModel.save_pretrained() output
│   ├── config.json
│   ├── model.safetensors
│   └── tokenizer_config.json
├── tts_betsileo/final/
├── tts_betsimisaraka/final/
├── tts_sakalava/final/
├── nllb_plt_latn/final/        ← PEFT LoRA adapter output
│   ├── adapter_config.json
│   └── adapter_model.safetensors
├── nllb_betsileo/final/
├── nllb_betsimisaraka/final/
└── nllb_sakalava/final/
```

At startup, Cloud Run calls `scripts/pull_checkpoints.py` which downloads only checkpoints that do not already exist locally. If the bucket is empty, base models (baked into the image) are used.

#### Step 7 — Create service account for Cloud Build

Cloud Build needs permission to deploy to Cloud Run.

```bash
PROJECT_NUMBER=97374817504    # replace with your project number from Step 3

# Create dedicated service account
gcloud iam service-accounts create cloudbuild-runner \
  --display-name="Cloud Build — inference deploy" \
  --project=mgvaovao-ia

# Grant Cloud Run Admin (to create/update services)
gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:cloudbuild-runner@mgvaovao-ia.iam.gserviceaccount.com" \
  --role="roles/run.admin"

# Grant Service Account User (to run Cloud Run as compute SA)
gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:cloudbuild-runner@mgvaovao-ia.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Grant Artifact Registry Writer (to push images)
gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:cloudbuild-runner@mgvaovao-ia.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Grant Storage Object Admin (to read/write checkpoints)
gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:cloudbuild-runner@mgvaovao-ia.iam.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Also grant the DEFAULT Cloud Build SA (used by gcloud builds submit)
gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Verify
gcloud iam service-accounts list --project=mgvaovao-ia
```

#### Step 8 — Configure local gcloud profile

Save a named configuration so you never have to type the project every time.

```bash
# Create a named config (e.g. "mgvaovao")
gcloud config configurations create mgvaovao

# Set all values
gcloud config set account YOUR_EMAIL@gmail.com
gcloud config set project mgvaovao-ia
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a

# Verify
gcloud config configurations describe mgvaovao

# Switch between configs
gcloud config configurations activate mgvaovao
```

---

### 18.2 — Build the Inference Docker Image

The inference image bakes all 4 models (Silero VAD, Whisper small, NLLB-200, MMS-TTS) directly into the image so cold starts require no network downloads.

**Image size:** ~8 GB  
**First build time:** ~45–60 min (model downloads)  
**Subsequent builds:** ~5–10 min (Docker layer cache skips model downloads)

#### Files involved

| File | Purpose |
|---|---|
| `Dockerfile.cloudrun` | Multi-stage image spec — installs deps, copies code, runs `download_models.py` |
| `cloudbuild-inference.yaml` | Cloud Build pipeline — build → push → deploy to Cloud Run |
| `scripts/download_models.py` | Downloads all 4 models at build time (runs inside Docker) |

#### Manual build command (used when there is no GitHub trigger)

```bash
# Linux / macOS / WSL
gcloud builds submit \
  --config=cloudbuild-inference.yaml \
  --project=mgvaovao-ia \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD) \
  .

# PowerShell (Windows) — $() does not work inline in gcloud args
$SHA = git rev-parse --short HEAD
gcloud builds submit `
  --config=cloudbuild-inference.yaml `
  --project=mgvaovao-ia `
  "--substitutions=SHORT_SHA=$SHA" `
  .
```

> **Why `SHORT_SHA` must be explicit?**  
> `$SHORT_SHA` is automatically populated only when a Cloud Build *trigger* fires (e.g. GitHub push). When using `gcloud builds submit` manually, it is empty — causing `invalid image name` errors. Always pass it explicitly as shown above.

#### What `cloudbuild-inference.yaml` does step by step

```yaml
Step 1 — build-inference:
  docker build -f Dockerfile.cloudrun \
    --tag inference:{SHORT_SHA}   # immutable tag — one per commit
    --tag inference:latest        # rolling latest
    --cache-from inference:latest # reuse layers from previous build

Step 2 — push-sha:     push inference:{SHORT_SHA} to Artifact Registry
Step 3 — push-latest:  push inference:latest to Artifact Registry

Step 4 — deploy:
  gcloud run deploy mgvaovao-inference \
    --image=inference:{SHORT_SHA}    # uses immutable tag, not latest
    --gpu=1 --gpu-type=nvidia-l4
    --cpu=8 --memory=32Gi
    --concurrency=1
    --min-instances=0 --max-instances=2
    --timeout=300
    --allow-unauthenticated
```

#### Monitor a running build

```bash
# List recent builds (with status)
gcloud builds list --limit=5 --project=mgvaovao-ia

# Stream logs of a specific build
gcloud builds log BUILD_ID --project=mgvaovao-ia --stream

# Or open in Cloud Console
# https://console.cloud.google.com/cloud-build/builds?project=mgvaovao-ia
```

---

### 18.3 — Deploy to Cloud Run GPU

Cloud Run GPU is generally available since June 2025. NVIDIA L4 (24 GB VRAM) is used.

#### The deploy command (run automatically by Cloud Build Step 4)

```bash
gcloud run deploy mgvaovao-inference \
  --image=us-central1-docker.pkg.dev/mgvaovao-ia/mgvaovao/inference:{SHA} \
  --region=us-central1 \
  --project=mgvaovao-ia \
  --platform=managed \
  --gpu=1 \
  --gpu-type=nvidia-l4 \
  --cpu=8 \
  --memory=32Gi \
  --no-cpu-throttling \
  --no-gpu-zonal-redundancy \
  --concurrency=1 \
  --min-instances=0 \
  --max-instances=2 \
  --timeout=300 \
  --port=8080 \
  --set-env-vars=MGVAOVAO_DEVICE=cuda,MGVAOVAO_WHISPER_MODEL_SIZE=small \
  --allow-unauthenticated
```

**Flag explanations:**

| Flag | Value | Why |
|---|---|---|
| `--gpu=1` | 1 GPU | One L4 per instance |
| `--gpu-type=nvidia-l4` | L4 | 24 GB VRAM, GA since June 2025 |
| `--cpu=8` | 8 vCPU | Required minimum for L4 on Cloud Run |
| `--memory=32Gi` | 32 GB RAM | Required minimum for L4 on Cloud Run |
| `--no-cpu-throttling` | — | CPU always at 100% even when idle (needed for GPU scheduling) |
| `--no-gpu-zonal-redundancy` | — | Reduces cost — single zone only |
| `--concurrency=1` | 1 request | One WebSocket session per instance — prevents GPU memory conflicts |
| `--min-instances=0` | 0 | Scale to zero when idle — saves money |
| `--max-instances=2` | 2 | Max 2 parallel sessions |
| `--timeout=300` | 5 min | Max request duration (WebSocket sessions can be long) |
| `--port=8080` | 8080 | Cloud Run always uses 8080 — FastAPI listens on 8080 |
| `--allow-unauthenticated` | — | Public access — no token required |
| `--set-env-vars=MGVAOVAO_DEVICE=cuda` | cuda | Force GPU inference |
| `MGVAOVAO_WHISPER_MODEL_SIZE=small` | small | Balance speed/accuracy |

#### Verify the deployment

```bash
# Get the service URL
gcloud run services describe mgvaovao-inference \
  --region=us-central1 --project=mgvaovao-ia \
  --format="value(status.url)"
# Expected: https://mgvaovao-inference-fzrhcfjzjq-uc.a.run.app

# Test health endpoint
curl https://mgvaovao-inference-fzrhcfjzjq-uc.a.run.app/health
# Expected: {"status": "ok"}

# Test ready endpoint (returns 503 while models load, 200 when ready)
curl https://mgvaovao-inference-fzrhcfjzjq-uc.a.run.app/ready
# Returns 503 for ~60-120 s, then: {"status": "ready", "dialects_loaded": [...]}

# Open the real-time UI
# https://mgvaovao-inference-fzrhcfjzjq-uc.a.run.app/live
```

#### Cold start behavior

When `min-instances=0` and no request has come in for a while, Cloud Run shuts down the instance. The next request triggers a **cold start**:

1. Container starts, CUDA driver initializes (~10–15 s)
2. `api/main.py` opens port 8080 immediately — `/health` responds
3. Background thread starts loading models:
   - `pull_checkpoints.py` — downloads from GCS (if any fine-tuned checkpoints exist)
   - Silero VAD loaded on CPU
   - Whisper loaded on GPU
   - NLLB-200 per dialect loaded on GPU
   - MMS-TTS per dialect loaded on GPU
4. `/ready` returns `200` — UI unlocks and mic starts automatically
5. Total cold start: **60–120 seconds**

The UI handles this with a loading overlay (`#loading-overlay`) that polls `/ready` every 3 seconds and fades away when models are ready.

---

### 18.4 — Cloud Run Logs & Debugging

```bash
# Stream live logs from Cloud Run
gcloud logging read \
  "resource.type=cloud_run_revision \
   AND resource.labels.service_name=mgvaovao-inference" \
  --project=mgvaovao-ia \
  --limit=50 \
  --freshness=1h \
  --format="table(timestamp,textPayload)"

# Filter by severity
gcloud logging read \
  "resource.type=cloud_run_revision \
   AND resource.labels.service_name=mgvaovao-inference \
   AND severity>=ERROR" \
  --project=mgvaovao-ia --limit=20

# View via Cloud Console (easier for browsing)
# https://console.cloud.google.com/run/detail/us-central1/mgvaovao-inference/logs?project=mgvaovao-ia
```

**Common log patterns to look for:**

| Log line | Meaning |
|---|---|
| `Model loading started in background thread` | Cold start began — port is open |
| `All pipelines loaded — API is ready.` | All 4 dialects ready — `/ready` now returns 200 |
| `WS open — dialect=plt_latn src_lang=None` | WebSocket session started |
| `VAD state=idle prob=0.023` | Audio received, VAD active, no speech detected |
| `VAD state=speaking prob=0.847` | Speech detected |
| `VAD state=end` | End of utterance — pipeline will run |
| `WS closed — dialect=plt_latn` | Normal client disconnect |
| `KeyError: 'bytes'` | **BUG** — old code: check that stream.py uses `msg.get("bytes")` |

---

### 18.5 — Managing Fine-Tuned Checkpoints

Fine-tuned models live in GCS and are pulled at every cold start. No Docker rebuild needed to update a model.

#### Upload a new checkpoint after fine-tuning

```bash
# Upload a TTS checkpoint
python scripts/push_checkpoint.py tts betsileo ./checkpoints/tts_betsileo/final
# → uploads to gs://mgvaovao-ia-checkpoints/tts_betsileo/final/

# Upload an NLLB LoRA adapter
python scripts/push_checkpoint.py nllb betsileo ./checkpoints/nllb_betsileo/final
# → uploads to gs://mgvaovao-ia-checkpoints/nllb_betsileo/final/

# Or manually with gsutil
gsutil -m cp -r ./checkpoints/tts_betsileo/final \
  gs://mgvaovao-ia-checkpoints/tts_betsileo/
```

#### Force Cloud Run to pick up the new checkpoint immediately

Cloud Run only pulls checkpoints on cold start. Force a restart:

```bash
gcloud run services update mgvaovao-inference \
  --region=us-central1 \
  --project=mgvaovao-ia
```

Or wait for the next natural cold start (min-instances=0, instance will shut down after ~15 min idle).

#### Verify what's in GCS

```bash
gcloud storage ls --recursive gs://mgvaovao-ia-checkpoints/
```

---

### 18.6 — Vertex AI Custom Training Jobs

Vertex AI is used to run NLLB and TTS fine-tuning on cloud GPUs (NVIDIA T4 or L4 Spot).

#### One-time Vertex AI setup

```bash
# Vertex AI requires the Artifact Registry image to exist first
# (already done if you completed 18.2)

# Grant Vertex AI access to GCS
PROJECT_NUMBER=97374817504
gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"

# Grant Vertex AI access to pull Docker images from Artifact Registry
gcloud projects add-iam-policy-binding mgvaovao-ia \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/artifactregistry.reader"
```

#### Launch a training job

```bash
# Fine-tune NLLB for betsileo dialect
gcloud ai custom-jobs create \
  --region=us-central1 \
  --project=mgvaovao-ia \
  --display-name="nllb-finetune-betsileo-$(date +%Y%m%d)" \
  --worker-pool-spec=\
machine-type=n1-standard-8,\
replica-count=1,\
accelerator-type=NVIDIA_TESLA_T4,\
accelerator-count=1,\
executor-image-uri=us-central1-docker.pkg.dev/mgvaovao-ia/mgvaovao/mgvaovao:cuda-latest,\
local-package-path=.,\
python-module=training.train_nllb \
  --args="--dialect=betsileo" \
  --enable-web-access

# Fine-tune TTS for betsileo dialect
gcloud ai custom-jobs create \
  --region=us-central1 \
  --project=mgvaovao-ia \
  --display-name="tts-finetune-betsileo-$(date +%Y%m%d)" \
  --worker-pool-spec=\
machine-type=n1-standard-8,\
replica-count=1,\
accelerator-type=NVIDIA_TESLA_T4,\
accelerator-count=1,\
executor-image-uri=us-central1-docker.pkg.dev/mgvaovao-ia/mgvaovao/mgvaovao:cuda-latest,\
local-package-path=.,\
python-module=training.train_tts \
  --args="--dialect=betsileo"
```

#### Monitor training jobs

```bash
# List jobs
gcloud ai custom-jobs list --region=us-central1 --project=mgvaovao-ia

# Stream logs
gcloud ai custom-jobs stream-logs JOB_ID --region=us-central1 --project=mgvaovao-ia

# Or in Cloud Console:
# https://console.cloud.google.com/vertex-ai/training/custom-jobs?project=mgvaovao-ia
```

**Cost reference (T4 Spot, us-central1):**

| Job | Duration | Approx cost |
|---|---|---|
| NLLB LoRA (5 epochs, 3 000 pairs) | ~4–6 h | ~$1.68–$2.52 |
| TTS VITS (50 epochs, 200 samples) | ~2–3 h | ~$0.84–$1.26 |

> **Tip:** Add `--scheduling=spot` to enable Spot instances (~60% cheaper, but may be preempted). Always checkpoint to GCS every 30 min (`scripts/pull_checkpoints.py` handles resumption).

---

### 18.7 — GitHub → Cloud Build Automatic Trigger (optional)

This connects your GitHub repository to Cloud Build so every push to `main` automatically triggers a build and deploy.

```bash
# 1. Connect GitHub repository via Cloud Console first:
# https://console.cloud.google.com/cloud-build/triggers/connect?project=mgvaovao-ia
# → Select GitHub → Authorize → Choose repository mgvaovao-Mdn/ml

# 2. Create the trigger from trigger.yaml
gcloud builds triggers create github \
  --project=mgvaovao-ia \
  --region=global \
  --name="deploy-inference-on-push" \
  --repo-owner=mgvaovao-Mdn \
  --repo-name=ml \
  --branch-pattern="^main$" \
  --build-config=cloudbuild-inference.yaml \
  --description="Auto-deploy inference on push to main"

# 3. Verify
gcloud builds triggers list --project=mgvaovao-ia
```

With this trigger, every `git push origin main` automatically:
1. Builds the inference image using Docker layer cache (~5–10 min)
2. Pushes to Artifact Registry
3. Deploys to Cloud Run GPU
4. `$SHORT_SHA` is set automatically by the trigger (no manual `--substitutions` needed)

**Without the trigger** (manual workflow), always use:
```bash
# Linux/macOS
gcloud builds submit --config=cloudbuild-inference.yaml \
  --project=mgvaovao-ia \
  --substitutions=SHORT_SHA=$(git rev-parse --short HEAD) .

# PowerShell (Windows) — must use intermediate variable
$SHA = git rev-parse --short HEAD
gcloud builds submit --config=cloudbuild-inference.yaml `
  --project=mgvaovao-ia "--substitutions=SHORT_SHA=$SHA" .
```

---

### 18.8 — Local Testing with Mock Server (before building)

Before spending 45+ min on a Cloud Build, test the UI locally with a mock inference server.

```bash
# Terminal 1 — start the mock server (port 8080)
python scripts/mock_server.py

# Terminal 2 — serve the UI pointing to localhost
python ui/serve_local.py --local
# Opens at http://localhost:8081/live

# The mock server simulates the full WebSocket protocol:
# - Sends VAD state frames on every audio chunk
# - Triggers a fake result after ~20 audio chunks (~640 ms of audio)
# - Returns MOCK translation and MOCK audio
# - Handles disconnect cleanly without crashing
```

This lets you validate the entire browser → WebSocket → response → audio playback flow
without deploying to GCP.

---

### 18.9 — Known Issues & Fixes Applied

These bugs were encountered and fixed during the initial deployment. Document them here so future engineers do not repeat the debugging cycle.

#### Bug 1 — `KeyError: 'bytes'` on client disconnect

**Symptom:** Cloud Run logs show `KeyError: 'bytes'` immediately after a browser tab is closed or the Stop button is clicked. Traceback points to `api/routes/stream.py`.

**Root cause:** When a WebSocket client disconnects, ASGI delivers a frame `{"type": "websocket.disconnect", "code": 1000}`. This frame has **no `"bytes"` key**. Old code accessed `msg["bytes"]` unconditionally — crashing on disconnect.

**Fix applied** (`api/routes/stream.py`):
```python
# OLD (crashes on disconnect):
raw: bytes = msg["bytes"]

# NEW (safe):
if msg.get("type") == "websocket.disconnect":
    break
raw: bytes = msg.get("bytes") or b""
if not raw:
    continue
```

#### Bug 2 — Silero VAD never triggers (threshold too strict)

**Symptom:** Audio arrives (visible in logs as `VAD state=idle prob=0.12`), but speech is never detected. Pipeline never runs. No results appear in the UI.

**Root cause:** The VAD threshold was `0.5`. Browser microphone audio over WebSocket has variable amplitude — many legitimate speech frames score below `0.5` on Silero VAD v5.

**Fix applied** (`src/mgvaovao/core/config.py`):
```python
# OLD:
vad_threshold: float = 0.5
vad_stream_min_silence_ms: int = 500

# NEW:
vad_threshold: float = 0.3          # more sensitive to real mic audio
vad_stream_min_silence_ms: int = 400 # detect end of phrase faster
```

#### Bug 3 — `SHORT_SHA` empty on manual `gcloud builds submit`

**Symptom:** `ERROR: invalid image name "...inference:"` — image tag ends with `:` (empty SHA).

**Root cause:** `$SHORT_SHA` is a Cloud Build built-in substitution that is only set automatically when a *trigger* fires. Manual `gcloud builds submit` leaves it empty.

**Fix:** Always pass `--substitutions=SHORT_SHA=$(git rev-parse --short HEAD)` on manual builds. On Windows PowerShell, use an intermediate variable (inline `$()` does not expand inside gcloud args on PowerShell 5.1).

---

### 18.10 — Complete Variables & Migration Checklist

This section lists every value that must be saved when migrating to a new machine or a new GCP project.

#### GCP Project variables

| Variable | Current value | Where used |
|---|---|---|
| `GCP_PROJECT_ID` | `mgvaovao-ia` | Every `gcloud` command |
| `GCP_PROJECT_NUMBER` | `97374817504` | IAM member strings (`serviceAccount:N@cloudbuild...`) |
| `GCP_REGION` | `us-central1` | Cloud Run, Vertex AI, Artifact Registry |
| `GCP_ZONE` | `us-central1-a` | Vertex AI training VMs |
| `GCP_ACCOUNT` | `atr.guillaume@gmail.com` | `gcloud auth login` |
| `GCP_CONFIG_NAME` | `tsantaconfig` | `gcloud config configurations activate` |

#### Cloud Run service

| Variable | Current value |
|---|---|
| `CLOUDRUN_SERVICE` | `mgvaovao-inference` |
| `CLOUDRUN_URL` | `https://mgvaovao-inference-fzrhcfjzjq-uc.a.run.app` |
| `CLOUDRUN_REGION` | `us-central1` |

> **Note:** The URL suffix (`fzrhcfjzjq`) is generated by GCP and cannot be chosen. If you delete and recreate the service, you get a new URL. Use a custom domain via Cloud Run domain mapping to make it stable.

#### Artifact Registry

| Variable | Current value |
|---|---|
| `AR_REPO` | `mgvaovao` |
| `AR_IMAGE_INFERENCE` | `us-central1-docker.pkg.dev/mgvaovao-ia/mgvaovao/inference` |
| `AR_IMAGE_CUDA` | `us-central1-docker.pkg.dev/mgvaovao-ia/mgvaovao/mgvaovao` |

#### GCS Buckets

| Variable | Current value | Purpose |
|---|---|---|
| `GCS_BUCKET_MODELS` | `mgvaovao-ia-checkpoints` | Fine-tuned model checkpoints |
| `GCS_BUCKET_CLOUDBUILD` | `mgvaovao-ia_cloudbuild` | Cloud Build source archives (auto-managed) |

#### Service accounts

| Variable | Current value | Roles |
|---|---|---|
| `SA_CLOUDBUILD` | `cloudbuild-runner@mgvaovao-ia.iam.gserviceaccount.com` | `run.admin`, `iam.serviceAccountUser`, `artifactregistry.writer`, `storage.objectAdmin` |
| `SA_COMPUTE` | `97374817504-compute@developer.gserviceaccount.com` | Default compute SA — `storage.objectAdmin`, `artifactregistry.reader` |

#### GitHub

| Variable | Current value |
|---|---|
| `GITHUB_REPO` | `https://github.com/mgvaovao-Mdn/ml.git` |
| `GITHUB_USER` | `guillaume1146` |

#### Application environment variables (set on Cloud Run)

| Variable | Value | Description |
|---|---|---|
| `MGVAOVAO_DEVICE` | `cuda` | Force GPU inference |
| `MGVAOVAO_WHISPER_MODEL_SIZE` | `small` | ASR model size |
| `MGVAOVAO_CHECKPOINTS_BUCKET` | `mgvaovao-ia-checkpoints` | GCS bucket for checkpoints |
| `MGVAOVAO_VAD_THRESHOLD` | `0.3` | VAD speech detection threshold |
| `MGVAOVAO_VAD_STREAM_MIN_SILENCE_MS` | `400` | Silence duration to trigger pipeline |

---

### 18.11 — Migration to a New GCP Project

Follow this checklist when migrating the entire system to a new GCP account or project.

```
STEP 1 — New project
  □ Create new GCP project with billing enabled
  □ Note new PROJECT_ID and PROJECT_NUMBER

STEP 2 — Enable APIs (§18.1 Step 4)
  □ Run: gcloud services enable run.googleapis.com artifactregistry.googleapis.com
         cloudbuild.googleapis.com storage.googleapis.com aiplatform.googleapis.com ...

STEP 3 — Artifact Registry (§18.1 Step 5)
  □ Create repo: gcloud artifacts repositories create mgvaovao --format=docker --location=us-central1

STEP 4 — GCS Buckets (§18.1 Step 6)
  □ Create bucket: gcloud storage buckets create gs://{NEW_PROJECT}-checkpoints --location=us-central1
  □ Update MGVAOVAO_CHECKPOINTS_BUCKET in Dockerfile.cloudrun (line: ENV MGVAOVAO_CHECKPOINTS_BUCKET=...)
  □ Update GCS_BUCKET_MODELS in .env

STEP 5 — Service accounts & IAM (§18.1 Step 7)
  □ Create cloudbuild-runner SA
  □ Grant roles: run.admin, iam.serviceAccountUser, artifactregistry.writer, storage.objectAdmin
  □ Grant default Cloud Build SA: run.admin, iam.serviceAccountUser

STEP 6 — Transfer checkpoints
  □ Download from old bucket: gsutil -m cp -r gs://mgvaovao-ia-checkpoints/ ./checkpoints-backup/
  □ Upload to new bucket:     gsutil -m cp -r ./checkpoints-backup/ gs://{NEW_PROJECT}-checkpoints/

STEP 7 — Update code references
  □ Search and replace old PROJECT_ID in: cloudbuild.yaml, cloudbuild-inference.yaml
  □ Update .env with new GCP variables
  □ Commit: git add -A && git commit -m "chore: migrate to new GCP project {NEW_PROJECT_ID}"

STEP 8 — First build (§18.2)
  □ Run: gcloud builds submit --config=cloudbuild-inference.yaml
         --project={NEW_PROJECT_ID} --substitutions=SHORT_SHA=$(git rev-parse --short HEAD) .
  □ Wait ~45-60 min for first build (model downloads — layer cache empty)
  □ Verify build SUCCESS in Cloud Console

STEP 9 — Verify deployment (§18.3)
  □ Get new Cloud Run URL: gcloud run services describe mgvaovao-inference ...
  □ Test: curl {NEW_URL}/health
  □ Wait for /ready: curl {NEW_URL}/ready (may take 60-120 s on first cold start)
  □ Open UI: {NEW_URL}/live — speak a phrase — verify translation appears

STEP 10 — Update saved variables
  □ Update .env with new CLOUDRUN_URL
  □ Update any frontend/client code that hardcodes the Cloud Run URL
  □ Update GitHub trigger if used (§18.7)
```

---

## 19. Environment Variables

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
| `MGVAOVAO_VAD_STREAM_MIN_SILENCE_MS` | `500` | Silence to trigger end-of-utterance (streaming VAD) |
| `DIALECT` | `betsileo` | Default dialect for Docker Compose training commands |

Paths (override only if not using Docker volumes):

| Variable | Default |
|---|---|
| `MGVAOVAO_ROOT_DIR` | `/mgvaovao` |
| `MGVAOVAO_CHECKPOINTS_DIR` | `/mgvaovao/checkpoints` |
| `MGVAOVAO_DATASET_DIR` | `/mgvaovao/dataset` |
| `MGVAOVAO_HF_CACHE_DIR` | `/mgvaovao/.cache/huggingface` |

---

## 20. MLOps & Monitoring

### Automated training pipeline

```mermaid
flowchart TD
    DS["📂 New validated dataset\nin GCS processed/"]
    PS["☁️ Cloud Pub/Sub\nEvent bus · topic: dataset-ready"]

    subgraph VP["Vertex AI Pipeline — Kubeflow DAG · $0.03/run"]
        S1["Step 1\ndata_validation\nCloud Run · $0"]
        S2["Step 2\nnllb_finetune\nLoRA rank=16\nL4 Spot ~$1.7–3.5"]
        S3["Step 3\ntts_finetune\nper dialect\nL4 Spot ~$0.84"]
        S4["Step 4\nevaluate\nCandidate vs Champion\nchrF++ · UTMOS"]
        S5["Step 5\nregister\nModel Registry\nFree"]
        S6["Step 6\ndeploy\nCloud Build\nCloud Run GPU"]
    end

    REGR{"Regression\ndetected?"}
    ROLLBACK["⚠️ ROLLBACK\nPrevious version restored\nImmediate email alert"]
    DEPLOY["✅ Deployment\nBlue/Green · Zero downtime"]
    EXPERIMENTS["📊 Vertex AI Experiments\nchrF++ · UTMOS · Free\nAll runs compared"]

    DS --> PS --> S1 --> S2 & S3 --> S4 --> REGR
    REGR -->|"YES"| ROLLBACK
    REGR -->|"NO"| S5 --> S6 --> DEPLOY
    S4 --> EXPERIMENTS

    classDef triggerStyle fill:#1a3a5c,color:#fff,stroke:#0d2035
    classDef stepStyle fill:#4285f4,color:#fff,stroke:#2d6bd6
    classDef decisionStyle fill:#fb8c00,color:#333,stroke:#e65100
    classDef goodStyle fill:#34a853,color:#fff,stroke:#249345
    classDef badStyle fill:#ea4335,color:#fff,stroke:#c62828
    classDef trackStyle fill:#9c27b0,color:#fff,stroke:#7b1fa2

    class DS,PS triggerStyle
    class S1,S2,S3,S4,S5,S6 stepStyle
    class REGR decisionStyle
    class DEPLOY,EXPERIMENTS goodStyle
    class ROLLBACK badStyle
```

### Drift monitoring thresholds

| Metric | Alert threshold | Automatic action |
|---|---|---|
| chrF++ on 200 fixed reference sentences | Drop > 2 points | Trigger NLLB re-fine-tuning via Pub/Sub |
| UTMOS on 50 audio test sentences | Drop > 0.3 | Trigger TTS re-fine-tuning via Pub/Sub |
| Pipeline WebRTC error rate | > 5% | Email alert + immediate infra investigation |
| P95 pipeline latency | > 2 000 ms | Email alert + Cloud Monitoring investigation |

All training runs tracked in **Vertex AI Experiments** (free).

### Pre-warming strategy

Cloud Scheduler pings Cloud Run GPU every 15 min to prevent cold starts during active hours. Scale-to-zero preserved during nights and weekends.

---

## 21. Cost Reference

### Beta phase budget — ~$42/month (< 100 users/day)

| Item | Monthly cost |
|---|---|
| Cloud Run GPU L4 (50 h active) | $33.60 |
| Vertex AI Monitoring | $3.00 |
| Vertex AI Custom Training (2 runs/month) | $2.24 |
| Cloud Run CPU (WebRTC signaling) | $2.00 |
| Google Cloud Storage (50 GB) | $1.00 |
| Vertex AI Pipelines | $0.12 |
| Artifact Registry | $0.50 |
| Vertex Experiments + Registry | $0.00 |
| Cloud Build CI/CD | $0.00 |
| **Total** | **~$42/month** |

### Budget evolution by phase

| Phase | Users | Estimated budget |
|---|---|---|
| Beta | < 100 users/day | ~$42/month |
| Growth | 100–500 users/day | ~$100/month |
| Production | > 500 users/day | ~$500+/month |
| Vertex AI Endpoint migration threshold | > 500 users/day | Migrate to Endpoint |

### Active optimizations

| Optimization | Saving |
|---|---|
| Scale-to-zero (Cloud Run) | $0.00 outside active hours |
| Spot instances for fine-tuning | –60% to –91% vs on-demand |
| INT8 quantization (CTranslate2) | –50% VRAM · ×2 speed |
| Kaggle free T4 × 2 | 30 h/week at no cost |
| LoRA fine-tuning (vs full FT) | Only a fraction of parameters retrained |

---

## 22. Roadmap

```mermaid
gantt
    title MGVaovao — Technical Roadmap 2025–2027
    dateFormat  YYYY-MM
    axisFormat  %b %Y

    section Phase 1 — Baseline ✅
        ASR→MT→TTS pipeline validated        :done,    p1a, 2025-10, 2026-02
        Next.js + Python web interface       :done,    p1b, 2025-10, 2026-02
        WebRTC prototype (aiortc)            :done,    p1c, 2026-01, 2026-04

    section Phase 2 — Cloud Deploy 🔄
        Cloud Run GPU L4 deployed            :active,  p2a, 2026-04, 2026-06
        GCS buckets + GitHub repos           :active,  p2b, 2026-04, 2026-06
        Vertex AI Pipelines first run        :active,  p2c, 2026-05, 2026-06
        Model Registry — first models        :active,  p2d, 2026-05, 2026-06

    section Phase 3 — Fine-Tuning v1 ⏳
        3 000 FR/EN↔MG sentence pairs        :         p3a, 2026-06, 2026-08
        NLLB LoRA fine-tuned on Vertex AI    :         p3b, 2026-07, 2026-09
        200 official Malagasy audio phrases  :         p3c, 2026-07, 2026-09
        MMS-TTS Officiel fine-tuned          :         p3d, 2026-08, 2026-09

    section Phase 4 — Multi-dialect ⏳
        200 sentences × 3 dialects           :         p4a, 2026-09, 2026-11
        3 dialect TTS checkpoints fine-tuned :         p4b, 2026-09, 2026-11
        Weekly drift monitoring live         :         p4c, 2026-10, 2026-12
        Flutter mobile app v1                :         p4d, 2026-10, 2026-12

    section Phase 5 — Scale ⏳
        Public REST API · 6 full dialects    :         p5a, 2027-01, 2027-06
        NLLB-200 1.3B (if budget)            :         p5b, 2027-03, 2027-09
        Vertex AI Endpoint migration         :         p5c, 2027-06, 2027-12
```

| Phase | Status | Key deliverables |
|---|---|---|
| Phase 1 — Baseline | ✅ Done | VAD→ASR→NLLB→TTS pipeline · WebSocket streaming · Real-time browser UI · Docker images |
| Phase 2 — Cloud Deploy | 🔄 In progress (Q2 2026) | Cloud Run GPU L4 · GCS buckets · Vertex AI Pipeline first run · Model Registry |
| Phase 3 — Fine-Tuning v1 | ⏳ Q2–Q3 2026 | 3 000 FR/EN↔MG pairs · NLLB LoRA fine-tuned · 200 audio phrases · MMS-TTS Officiel fine-tuned · chrF++ and UTMOS published |
| Phase 4 — Multi-dialect | ⏳ Q3–Q4 2026 | 200 sentences × 3 dialects · 3 TTS checkpoints · Drift monitoring live · Flutter mobile app v1 |
| Phase 5 — Scale | 2027 | Public REST API · 6 full dialects · NLLB-200 1.3B (if budget) · Vertex AI Endpoint migration |

---

## 23. Feasibility & Risk Matrix

### Technically validated points

- ASR → MT → TTS pipeline functional in Malagasy: demonstrated in prototype
- `plt_Latn` confirmed in NLLB-200 tokenizer and FLORES-200 test set
- MMS-TTS-MLG fine-tuneable from 80–150 samples: verified in `ylacombe/finetune-hf-vits` official README
- Cloud Run GPU L4 GA since June 2, 2025: source Google Cloud Blog (official)
- Vertex AI Model Registry free: confirmed in GCP official documentation
- LoRA NLLB-200 validated on low-resource languages: arXiv 2602.04442
- Silero VAD v5 MIT ~2 MB CPU-only: github.com/snakers4/silero-vad
- `aiortc` supports audio tracks + DataChannel simultaneously (WebRTC)
- Kaggle T4 × 2 30 h/week free: confirmed
- CTranslate2 INT8 supports CUDA CC 6.1+ for Whisper and NLLB

### Risk matrix

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Cold start 20–30s on Cloud Run GPU | High | Medium | Cloud Scheduler pre-warm ping every 15 min |
| Translation baseline quality insufficient | Medium | High | LoRA fine-tuning on conversational Malagasy data |
| Dialect data collection difficult | High | Medium | Start with Officiel only — dialects in phases 2/3 |
| Latency > 700ms on mobile networks in MG | High | Medium | Opus codec + chunked streaming + TURN Cloudflare |
| Spot VM interruption during fine-tuning | Medium | Low | Auto-checkpoint to GCS every 30 min |
| Monthly budget overrun | Low | Medium | Cloud Billing alerts at 80% and 95% |

---

## 24. Technical References

| Reference | Source |
|---|---|
| Cloud Run GPU GA (June 2, 2025) | cloud.google.com/blog/products/serverless/cloud-run-gpus-are-now-generally-available |
| Cloud Run pricing | cloud.google.com/run/pricing |
| Vertex AI pricing | cloud.google.com/vertex-ai/pricing |
| NLLB-200-distilled-600M | huggingface.co/facebook/nllb-200-distilled-600M |
| MMS-TTS-MLG | huggingface.co/facebook/mms-tts-mlg |
| ylacombe/finetune-hf-vits | github.com/ylacombe/finetune-hf-vits |
| Silero VAD v5 | github.com/snakers4/silero-vad |
| faster-whisper (CTranslate2) | github.com/SYSTRAN/faster-whisper |
| UTMOS metric | arxiv.org/abs/2204.02152 (Saeki et al., Interspeech 2022) |
| Whisper distil-fr | huggingface.co/bofenghuang/whisper-large-v3-french-distil-dec8 |
| NLLB LoRA on low-resource languages | arXiv:2602.04442 · arXiv:2505.14423 |
| aiortc WebRTC Python | github.com/aiortc/aiortc |
| CTranslate2 | github.com/OpenNMT/CTranslate2 |

---

## 25. License

### Application code — Apache 2.0

All source code in this repository (API, training scripts, pipeline, UI) is released under the **Apache License 2.0**.

```
Copyright 2026 Madagasikara Vaovao — MGVaovao Maison du Numérique
Licensed under the Apache License, Version 2.0
http://www.apache.org/licenses/LICENSE-2.0
```

See [`LICENSE`](LICENSE) for the full text.

### Third-party model weights

The model weights loaded at runtime are **not** included in this repository and carry their own licenses:

| Model | License | Non-commercial restriction |
|---|---|---|
| NLLB-200-distilled-600M (Meta) | CC-BY-NC 4.0 | ✅ Free for NGO / research use |
| MMS-TTS-MLG VITS (Meta) | CC-BY-NC 4.0 | ✅ Free for NGO / research use |
| Whisper large-v3-turbo (OpenAI) | Apache 2.0 | None |
| Silero VAD v5 | MIT | None |

**Fine-tuned LoRA adapters** (derived from NLLB) and **dialect TTS checkpoints** (derived from MMS-TTS) produced by this project inherit CC-BY-NC 4.0 and are published under that license. Non-commercial use — including all NGO, academic, and LINGUA Africa grant activities — is fully permitted.

### Collected speech data — CC BY 4.0

All dialectal audio corpora collected and produced under this project are released under **Creative Commons Attribution 4.0 International (CC BY 4.0)**, published on HuggingFace and contributed to Mozilla Common Voice.

### Summary

| Asset | License |
|---|---|
| Code (this repository) | **Apache 2.0** |
| Fine-tuned NLLB LoRA weights | CC-BY-NC 4.0 |
| Fine-tuned MMS-TTS dialect checkpoints | CC-BY-NC 4.0 |
| Collected dialectal speech corpora | **CC BY 4.0** |
| Whisper weights (third-party) | Apache 2.0 |
| Silero VAD weights (third-party) | MIT |

---

*MGVaovao — Maison du Numérique · Ambatonakanga, Antananarivo · mgvaovao.com*  
