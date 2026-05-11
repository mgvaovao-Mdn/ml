#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gradio demo — thin client that calls the MGVaovao FastAPI.

The UI itself has zero model dependencies: it uploads audio to the API
and plays back the returned WAV.  This keeps the demo lightweight and
decoupled from the GPU server.

Usage:
    # Start the API first:
    uvicorn api.main:app --host 0.0.0.0 --port 8000

    # Then launch the UI:
    python ui/demo.py                           # connects to localhost:8000
    MGVAOVAO_API_URL=http://gpu-box:8000 python ui/demo.py
"""
from __future__ import annotations
import os
import tempfile
import requests
import gradio as gr

API_BASE = os.getenv("MGVAOVAO_API_URL", "http://localhost:8000")


# ── API helpers ───────────────────────────────────────────────────────────

def _fetch_dialects() -> dict[str, str]:
    """Returns {display_name: dialect_code}."""
    try:
        resp = requests.get(f"{API_BASE}/dialects/", timeout=5)
        resp.raise_for_status()
        return {d["name"]: d["code"] for d in resp.json() if d["model_ready"]}
    except Exception:
        return {
            "Malagasy Officiel": "plt_latn",
            "Betsileo":          "betsileo",
            "Betsimisaraka":     "betsimisaraka",
            "Sakalava":          "sakalava",
        }


def _download_audio(audio_url: str) -> str:
    """Download WAV from API and save to a temp file for Gradio."""
    url  = audio_url if audio_url.startswith("http") else f"{API_BASE}{audio_url}"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".wav", prefix="mgv_ui_")
    tmp.write(resp.content)
    tmp.flush()
    return tmp.name


# ── pipeline function ─────────────────────────────────────────────────────

def run_pipeline(
    audio_mic,
    audio_file,
    dialect_name: str,
    src_lang_override: str,
) -> tuple[str, str | None, str]:
    dialect_map = _fetch_dialects()
    dialect     = dialect_map.get(dialect_name, "betsileo")
    audio_src   = audio_mic or audio_file

    if audio_src is None:
        return "Aucun audio fourni.", None, ""

    with open(audio_src, "rb") as f:
        audio_bytes = f.read()

    form_data: dict = {"dialect": dialect}
    if src_lang_override != "auto":
        form_data["src_lang"] = src_lang_override

    try:
        resp = requests.post(
            f"{API_BASE}/translate/audio",
            files={"file": ("audio.wav", audio_bytes, "audio/wav")},
            data=form_data,
            timeout=60,
        )
        resp.raise_for_status()
    except requests.RequestException as exc:
        return f"Erreur API : {exc}", None, ""

    data      = resp.json()
    wav_path  = _download_audio(data["audio_url"])
    lat       = data["latency_ms"]

    info = (
        f"[{data['detected_lang'].upper()} → {dialect}]  \"{data['source_text']}\"\n"
        f"VAD: {lat.get('vad', 0)} ms  |  ASR: {lat.get('asr', 0)} ms  |  "
        f"NLLB: {lat.get('translation', 0)} ms  |  TTS: {lat.get('tts', 0)} ms  |  "
        f"Total: {lat.get('total', 0)} ms"
    )
    return data["malagasy_text"], wav_path, info


# ── Gradio UI ─────────────────────────────────────────────────────────────

def build_demo() -> gr.Blocks:
    dialect_map   = _fetch_dialects()
    dialect_names = list(dialect_map.keys())

    with gr.Blocks(title="MGVaovao — Traducteur Malagasy") as demo:
        gr.Markdown(
            "## MGVaovao — Traducteur Audio Multilingue → Dialectes Malgaches\n"
            "**Pipeline** : VAD → Whisper ASR → NLLB-200 (fine-tuné) → MMS-TTS (fine-tuné)\n\n"
            "Parlez en **français**, **anglais**, **allemand**, **espagnol**, **italien** ou **portugais**."
        )

        with gr.Row():
            dialect_dd = gr.Dropdown(
                choices=dialect_names,
                value=dialect_names[1] if len(dialect_names) > 1 else dialect_names[0],
                label="Dialecte cible",
                info="Chaque dialecte utilise son propre modèle TTS fine-tuné",
            )
            src_lang_dd = gr.Dropdown(
                choices=["auto", "fr", "en", "de", "es", "it", "pt"],
                value="auto",
                label="Langue source  (auto = détection Whisper)",
            )

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Entrée audio")
                micro  = gr.Audio(sources=["microphone"], type="filepath", label="Microphone")
                upload = gr.Audio(sources=["upload"],     type="filepath", label="Upload WAV / MP3")
                btn    = gr.Button("Traduire →", variant="primary", size="lg")

            with gr.Column():
                gr.Markdown("### Sortie")
                out_text  = gr.Textbox(label="Texte Malagasy traduit", lines=3)
                out_audio = gr.Audio(label="Audio synthétisé", type="filepath")
                out_info  = gr.Textbox(label="Latences pipeline", lines=2)

        btn.click(
            fn=run_pipeline,
            inputs=[micro, upload, dialect_dd, src_lang_dd],
            outputs=[out_text, out_audio, out_info],
        )

        gr.Markdown(
            "---\n"
            f"MGVaovao — Maison du Numérique Antananarivo  |  API: `{API_BASE}`"
        )

    return demo


def main():
    build_demo().launch(
        server_name="0.0.0.0",
        server_port=int(os.getenv("GRADIO_PORT", "7860")),
        show_api=False,
    )


if __name__ == "__main__":
    main()
