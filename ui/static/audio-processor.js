/**
 * AudioWorklet processor — runs in the dedicated audio rendering thread.
 * Forwards each 128-sample block to the main thread as a transferable buffer.
 * The main thread accumulates blocks into 512-sample chunks before sending
 * to the WebSocket (Silero VAD requirement: exactly 512 samples at 16 kHz).
 */
class AudioProcessor extends AudioWorkletProcessor {
  process(inputs) {
    const channel = inputs[0]?.[0];
    if (channel && channel.length > 0) {
      // Clone buffer so we can transfer it (avoids copy cost)
      const clone = channel.slice();
      this.port.postMessage(clone.buffer, [clone.buffer]);
    }
    return true; // keep processor alive
  }
}

registerProcessor("mgvaovao-audio-processor", AudioProcessor);
