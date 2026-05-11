/**
 * MGVaovao — real-time audio streaming client.
 *
 * Architecture:
 *   getUserMedia → AudioContext (16 kHz) → AudioWorklet
 *   → accumulate 512-sample chunks → WebSocket binary frames
 *   ← VAD state JSON ← processing JSON ← result JSON
 */

"use strict";

// ── Config ────────────────────────────────────────────────────────────────────
const CHUNK_SAMPLES = 512;   // Silero VAD requirement
const TARGET_SR     = 16000; // Hz — must match server

// ── State ─────────────────────────────────────────────────────────────────────
let ws        = null;
let audioCtx  = null;
let micStream = null;
let worklet   = null;
let recording = false;
let sampleBuf = new Float32Array(0); // inter-chunk accumulator

// ── DOM refs (populated in init()) ───────────────────────────────────────────
let btnToggle, selDialect, selSrcLang;
let elState, elProb, elTranscript, elTranslation, elLatency, elLog;

// ── WebSocket ──────────────────────────────────────────────────────────────────

function wsUrl(dialect, srcLang) {
  const proto = location.protocol === "https:" ? "wss" : "ws";
  const lang  = srcLang !== "auto" ? `?src_lang=${srcLang}` : "";
  return `${proto}://${location.host}/ws/stream/${dialect}${lang}`;
}

function connect() {
  const dialect = selDialect.value;
  const srcLang = selSrcLang.value;

  log(`Connecting [dialect=${dialect} src=${srcLang}]…`);
  ws = new WebSocket(wsUrl(dialect, srcLang));

  ws.onopen    = () => { log("Connected ✓"); startMic(); };
  ws.onmessage = (e) => handleMessage(JSON.parse(e.data));
  ws.onclose   = (e) => { log(`Disconnected (${e.code})`); stopMic(); setBtn(false); };
  ws.onerror   = ()  => log("WebSocket error");
}

function disconnect() {
  ws?.close();
}

// ── Message handler ───────────────────────────────────────────────────────────

function handleMessage(msg) {
  switch (msg.type) {
    case "vad":
      updateVAD(msg.state, msg.prob);
      break;

    case "processing":
      elState.textContent = "Processing…";
      elState.className   = "state processing";
      break;

    case "result":
      elTranscript.textContent  = msg.source_text  || "—";
      elTranslation.textContent = msg.malagasy_text || "—";
      renderLatency(msg.latency_ms);
      playAudio(msg.audio_b64);
      elState.textContent = "Listening…";
      elState.className   = "state listening";
      log(`Done — ${msg.latency_ms.total} ms total`);
      break;

    case "error":
      log(`Error: ${msg.message}`);
      elState.textContent = "Error";
      elState.className   = "state error";
      break;
  }
}

// ── VAD indicator ─────────────────────────────────────────────────────────────

function updateVAD(state, prob) {
  elProb.style.width = `${Math.round(prob * 100)}%`;
  elProb.style.background = prob > 0.5 ? "#22c55e" : "#64748b";

  switch (state) {
    case "speaking":
      elState.textContent = "Speaking…";
      elState.className   = "state speaking";
      break;
    case "trailing":
      elState.textContent = "…";
      elState.className   = "state trailing";
      break;
    default:
      if (elState.className !== "state processing") {
        elState.textContent = "Listening…";
        elState.className   = "state listening";
      }
  }
}

// ── Microphone / AudioWorklet ─────────────────────────────────────────────────

async function startMic() {
  try {
    micStream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true },
      video: false,
    });

    // Request 16 kHz; browser may not honour it — server handles resampling if needed
    audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: TARGET_SR });

    await audioCtx.audioWorklet.addModule("/live/audio-processor.js");
    worklet = new AudioWorkletNode(audioCtx, "mgvaovao-audio-processor");

    worklet.port.onmessage = (e) => sendChunk(new Float32Array(e.data));

    const source = audioCtx.createMediaStreamSource(micStream);
    source.connect(worklet);
    // Do NOT connect worklet to destination — avoid mic feedback

    recording = true;
    setBtn(true);
    elState.textContent = "Listening…";
    elState.className   = "state listening";
    log(`Mic started (${audioCtx.sampleRate} Hz)`);
  } catch (err) {
    log(`Mic error: ${err.message}`);
    disconnect();
  }
}

function stopMic() {
  recording = false;
  worklet?.disconnect();
  worklet = null;
  micStream?.getTracks().forEach((t) => t.stop());
  micStream = null;
  audioCtx?.close();
  audioCtx  = null;
  sampleBuf = new Float32Array(0);
  elState.textContent = "Stopped";
  elState.className   = "state idle";
}

// ── Audio chunking ────────────────────────────────────────────────────────────

function sendChunk(samples) {
  if (!ws || ws.readyState !== WebSocket.OPEN) return;

  // Append to accumulator
  const merged = new Float32Array(sampleBuf.length + samples.length);
  merged.set(sampleBuf);
  merged.set(samples, sampleBuf.length);

  let offset = 0;
  while (offset + CHUNK_SAMPLES <= merged.length) {
    const chunk = merged.slice(offset, offset + CHUNK_SAMPLES);
    ws.send(chunk.buffer);
    offset += CHUNK_SAMPLES;
  }
  sampleBuf = merged.slice(offset); // keep remainder
}

// ── Audio playback ────────────────────────────────────────────────────────────

function playAudio(b64) {
  const bytes  = Uint8Array.from(atob(b64), (c) => c.charCodeAt(0));
  const blob   = new Blob([bytes], { type: "audio/wav" });
  const url    = URL.createObjectURL(blob);
  const player = new Audio(url);
  player.onended = () => URL.revokeObjectURL(url);
  player.play().catch((e) => log(`Playback error: ${e.message}`));
}

// ── Latency table ─────────────────────────────────────────────────────────────

function renderLatency(lms) {
  const rows = [
    ["VAD",         lms.vad],
    ["ASR",         lms.asr],
    ["Translation", lms.translation],
    ["TTS",         lms.tts],
    ["Total",       lms.total],
  ];
  elLatency.innerHTML = rows
    .filter(([, v]) => v != null)
    .map(([k, v]) => `<tr><td>${k}</td><td>${v} ms</td></tr>`)
    .join("");
}

// ── Button & log helpers ──────────────────────────────────────────────────────

function setBtn(active) {
  btnToggle.textContent = active ? "⏹ Stop" : "🎙 Start";
  btnToggle.classList.toggle("active", active);
  selDialect.disabled = active;
  selSrcLang.disabled = active;
}

function log(msg) {
  const ts = new Date().toLocaleTimeString();
  elLog.textContent = `[${ts}] ${msg}\n` + elLog.textContent.slice(0, 2000);
}

// ── Dialect list fetch ────────────────────────────────────────────────────────

async function loadDialects() {
  try {
    const res  = await fetch("/dialects/");
    const list = await res.json();
    selDialect.innerHTML = list.map(
      (d) => `<option value="${d.code}">${d.name} (${d.code})${d.model_ready ? "" : " — no model"}</option>`
    ).join("");
  } catch {
    // keep hardcoded fallback options already in HTML
  }
}

// ── Init ──────────────────────────────────────────────────────────────────────

function init() {
  btnToggle   = document.getElementById("btn-toggle");
  selDialect  = document.getElementById("sel-dialect");
  selSrcLang  = document.getElementById("sel-src-lang");
  elState     = document.getElementById("el-state");
  elProb      = document.getElementById("el-prob");
  elTranscript  = document.getElementById("el-transcript");
  elTranslation = document.getElementById("el-translation");
  elLatency   = document.getElementById("el-latency");
  elLog       = document.getElementById("el-log");

  btnToggle.addEventListener("click", () => {
    if (!recording) {
      connect();
    } else {
      disconnect();
    }
  });

  loadDialects();
}

document.addEventListener("DOMContentLoaded", init);
