# -*- coding: utf-8 -*-
"""
Minimal mock inference server for local UI testing.
Run: python scripts/mock_server.py
Then: python ui/serve_local.py --local
Open: http://localhost:8765
"""
import asyncio
import base64
import io
import struct
import wave

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()
DIALECTS = ["plt_latn", "betsileo", "betsimisaraka", "sakalava"]

# ── REST ──────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/ready")
def ready():
    return {"ready": True, "loaded_dialects": DIALECTS}

@app.get("/dialects")
def dialects():
    return {"dialects": DIALECTS}

@app.post("/translate/text")
async def translate_text(request: Request):
    body = await request.json()
    return {"source_text": body.get("text", ""), "malagasy_text": "[MOCK]", "dialect": body.get("dialect", "plt_latn")}

# ── Silent WAV ────────────────────────────────────────────────────────────────

def _silent_wav(duration_s: float = 0.5, sr: int = 16_000) -> str:
    buf = io.BytesIO()
    n = int(sr * duration_s)
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(struct.pack(f"<{n}h", *([0] * n)))
    return base64.b64encode(buf.getvalue()).decode()

_WAV_B64 = _silent_wav()

# ── WebSocket ─────────────────────────────────────────────────────────────────

CHUNK_BYTES  = 512 * 4          # 512 float32 samples per chunk
TRIGGER_CHUNKS = 20             # trigger result after 20 chunks (~640 ms)

@app.websocket("/ws/stream/{dialect}")
async def stream_audio(websocket: WebSocket, dialect: str, src_lang: str | None = None):
    await websocket.accept()
    print(f"[WS] open  dialect={dialect} src_lang={src_lang}")

    chunks = 0
    result_sent = False

    try:
        while True:
            try:
                msg = await asyncio.wait_for(websocket.receive(), timeout=30.0)
            except asyncio.TimeoutError:
                print("[WS] timeout — no audio received for 30 s, closing")
                break

            msg_type = msg.get("type", "")
            print(f"[WS] msg type={msg_type} keys={list(msg.keys())}")

            if msg_type == "websocket.disconnect":
                print(f"[WS] disconnect code={msg.get('code')}")
                break

            # Skip text/control frames
            if msg.get("text") is not None:
                print(f"[WS] text frame: {msg['text']}")
                continue

            raw = msg.get("bytes")
            if not raw:
                print("[WS] empty bytes frame, skipping")
                continue

            chunks += 1
            print(f"[WS] audio chunk #{chunks}  {len(raw)} bytes")

            # Send VAD feedback
            prob = min(0.95, chunks / TRIGGER_CHUNKS)
            state = "speaking" if chunks > 3 else "idle"
            try:
                await websocket.send_json({"type": "vad", "state": state, "prob": round(prob, 3)})
            except Exception as e:
                print(f"[WS] send_json(vad) failed: {e}")
                break

            # Trigger result after TRIGGER_CHUNKS
            if chunks >= TRIGGER_CHUNKS and not result_sent:
                result_sent = True
                print("[WS] triggering mock result...")
                try:
                    await websocket.send_json({"type": "processing"})
                    await asyncio.sleep(0.4)
                    await websocket.send_json({
                        "type":         "result",
                        "source_text":  "Bonjour, comment allez-vous ?",
                        "detected_lang": src_lang or "fr",
                        "malagasy_text": "[MOCK] Manao ahoana ianareo ?",
                        "dialect":      dialect,
                        "audio_b64":    _WAV_B64,
                        "latency_ms":   {"vad": 10, "asr": 120, "translation": 80, "tts": 90, "total": 300},
                    })
                    print("[WS] result sent — reset for next utterance")
                except Exception as e:
                    print(f"[WS] send result failed: {e}")
                    break
                # Reset for next utterance
                chunks = 0
                result_sent = False

    except Exception as e:
        print(f"[WS] unhandled exception: {type(e).__name__}: {e}")

    print(f"[WS] closed  dialect={dialect}")


if __name__ == "__main__":
    print("Mock server  ->  http://localhost:8080")
    print("Run UI with: python ui/serve_local.py --local")
    print("Open:        http://localhost:8765\n")
    uvicorn.run(app, host="0.0.0.0", port=8080, log_level="warning")
