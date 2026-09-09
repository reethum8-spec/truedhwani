import sys
import time
import json
import asyncio
from pathlib import Path
import websockets

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from truedhwani.audio.audio_utils import load_audio_file, float32_to_pcm16


async def stream_audio_file(
    file_path: str | Path,
    ws_url: str = "ws://localhost:8000/ws/stream",
    real_time_playback: bool = True,
):
    """
    Stream an audio file to TrueDhwani WebSocket endpoint in real-time chunks,
    simulating an active VoIP phone call.
    """
    path = Path(file_path)
    if not path.exists():
        print(f"Error: Audio file not found at {path}")
        return

    print(f"Loading '{path.name}' for real-time streaming...")
    audio, sr = load_audio_file(path, target_sr=16000)
    duration_sec = len(audio) / sr
    print(f"Total audio duration: {duration_sec:.2f} seconds ({len(audio)} samples @ 16kHz)")
    print(f"Connecting to {ws_url}...")

    async with websockets.connect(ws_url) as ws:
        print("Connected to TrueDhwani streaming server!\n")
        print("=" * 80)
        print(f"{'SEC':<6} | {'DECISION':<12} | {'RISK':<6} | {'DF_SCORE':<8} | {'INTENT':<22} | {'LATENCY':<7}")
        print("=" * 80)

        chunk_size = 512  # 32ms frames
        frame_interval_sec = chunk_size / sr  # ~0.032s

        flushed_event = asyncio.Event()

        async def receive_packets():
            try:
                while True:
                    msg = await ws.recv()
                    data = json.loads(msg)
                    if data.get("status") == "stream_flushed":
                        flushed_event.set()
                        break
                    if "decision" not in data and "transcript" not in data:
                        continue

                    sec = data.get("call_duration_seconds", 0.0)
                    decision = data.get("decision", "")
                    silero_p = data.get("silero_speech_prob", 0.0)
                    transcript = data.get("transcript", "")
                    lang = data.get("language", "unknown")
                    lang_conf = data.get("whisper_language_confidence", 0.0)
                    df_score = data.get("aasist_spoof_prob", data.get("deepfake_score", 0.0))
                    df_pred = data.get("deepfake_prediction", "")
                    intent_label = data.get("scam_intent_label", "")
                    intent_score = data.get("scam_intent_score", 0.0)
                    intent_probs = data.get("distilbert_intent_probabilities", {})
                    weights = data.get("adaptive_fusion_weights", data.get("weights", {}))
                    ema_risk = data.get("ema_smoothed_risk", data.get("overall_risk_pct", 0.0))
                    lat = data.get("latency_ms", 0)
                    reason = data.get("reason", "")
                    action = data.get("recommended_action", "")

                    sorted_intents = sorted(intent_probs.items(), key=lambda x: x[1], reverse=True)[:3]
                    intents_summary = ", ".join(f"{k}: {v*100:.1f}%" for k, v in sorted_intents)

                    print(f"\n==================== [CHUNK AT {sec:.1f}s | Latency: {lat}ms] ====================")
                    print(f"  * Silero Speech Probability     : {silero_p:.4f}")
                    print(f"  * Whisper Transcript            : \"{transcript}\"")
                    print(f"  * Whisper Language Confidence   : {lang.upper()} ({lang_conf*100:.1f}%)")
                    print(f"  * AASIST Spoof Probability      : {df_score:.4f} ({df_pred})")
                    print(f"  * DistilBERT Intent Probability : {intent_label} ({intent_score*100:.1f}%)")
                    if intents_summary:
                        print(f"    -> Category Distribution     : {intents_summary}")
                    print(f"  * Adaptive Fusion Weights       : Deepfake={weights.get('deepfake', 0.0):.2f}, Intent={weights.get('scam_intent', 0.0):.2f}")
                    print(f"  * EMA-Smoothed Risk             : {ema_risk:.1f}/100")
                    print(f"  * Final Decision                : [{decision.upper()}] - {reason}")
                    if decision == "High Risk":
                        print(f"  * RECOMMENDED ACTION            : {action}")
                    print("=" * 76)
            except asyncio.CancelledError:
                pass
            except websockets.exceptions.ConnectionClosed:
                flushed_event.set()

        recv_task = asyncio.create_task(receive_packets())

        # Stream frames
        for i in range(0, len(audio), chunk_size):
            frame = audio[i : i + chunk_size]
            pcm_bytes = float32_to_pcm16(frame)
            await ws.send(pcm_bytes)

            if real_time_playback:
                await asyncio.sleep(frame_interval_sec * 0.95)

        # Flush remaining buffer at stream end
        await ws.send(json.dumps({"action": "flush"}))
        try:
            await asyncio.wait_for(flushed_event.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            pass
        recv_task.cancel()
        print("\nStreaming completed successfully.")


if __name__ == "__main__":
    target_file = sys.argv[1] if len(sys.argv) > 1 else "sample_audio/otp_scam_call.wav"
    url = sys.argv[2] if len(sys.argv) > 2 else "ws://localhost:8000/ws/stream"
    asyncio.run(stream_audio_file(target_file, ws_url=url))
