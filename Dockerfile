# MGVaovao — Malagasy Translation Pipeline (CPU build for local dev)
# For GPU/CUDA training use Dockerfile.cuda
#
# Build:
#   docker build -t mgvaovao:latest .
FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        ffmpeg \
        libsndfile1 \
        git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /mgvaovao

# PyTorch CPU-only (~200 MB vs 3.75 GB for CUDA build)
RUN pip install --no-cache-dir \
        torch==2.1.2 \
        torchaudio==2.1.2 \
        --index-url https://download.pytorch.org/whl/cpu

# HuggingFace + training stack
RUN pip install --no-cache-dir \
        transformers==4.51.3 \
        datasets==3.5.0 \
        evaluate==0.4.3 \
        accelerate==1.6.0 \
        huggingface_hub==0.30.2 \
        peft==0.14.0 \
        safetensors==0.4.5 \
        tokenizers==0.21.1

# Audio processing
RUN pip install --no-cache-dir \
        openai-whisper \
        soundfile \
        librosa \
        scipy \
        numpy \
        pandas

# Serving + UI
RUN pip install --no-cache-dir \
        fastapi==0.115.12 \
        "uvicorn[standard]==0.34.0" \
        pydantic-settings==2.9.1 \
        python-multipart==0.0.20 \
        requests==2.32.3 \
        "gradio==4.31.5" \
        tqdm

# Evaluation metrics
RUN pip install --no-cache-dir \
        sacrebleu \
        jiwer

COPY src/       ./src/
COPY api/       ./api/
COPY ui/        ./ui/
COPY training/  ./training/
COPY pyproject.toml .

RUN pip install --no-cache-dir -e .

ENV HF_HOME=/mgvaovao/.cache/huggingface
ENV TRANSFORMERS_CACHE=/mgvaovao/.cache/huggingface/transformers
ENV TORCH_HOME=/mgvaovao/.cache/torch
ENV PYTHONUNBUFFERED=1
ENV PYTHONIOENCODING=utf-8
ENV MGVAOVAO_ROOT_DIR=/mgvaovao
ENV MGVAOVAO_CHECKPOINTS_DIR=/mgvaovao/checkpoints
ENV MGVAOVAO_DATASET_DIR=/mgvaovao/dataset
ENV MGVAOVAO_HF_CACHE_DIR=/mgvaovao/.cache/huggingface
ENV MGVAOVAO_TORCH_HUB_DIR=/mgvaovao/.cache/torch/hub

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
