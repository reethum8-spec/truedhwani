import sys
import json
import asyncio
import numpy as np
from pathlib import Path
import websockets
import sounddevice as sd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from truedhwani.audio.audio_utils import float32_to_pcm16


async def stream_live_microphone(ws_url: str = "ws://localhost:8000/ws/stream"):
    """
    Capture live microphone audio continuously and stream to TrueDhwani WebSocket server.
    """
    sample_rate = 16000
    channels = 1
    chunk_size = 512  # 32ms frames

    print(f"Connecting to TrueDhwani streaming server at {ws_url}...")
    try:
        ws = await websockets.connect(ws_url)
    except Exception as e:
        print(f"Error connecting to WebSocket server: {e}")
        print("Please ensure the FastAPI server is running (`uvicorn truedhwani.server.app:app`).")
        return

    print("Connected to TrueDhwani pipeline!")
    print("Microphone active: Speak into your microphone to monitor scam risk in real-time.")
    print("Press Ctrl+C to stop.\n")
    print("=" * 80)
    print(f"{'TIME':<6} | {'DECISION':<12} | {'RISK':<6} | {'DF_SCORE':<8} | {'INTENT':<22} | {'LATENCY':<7}")
    print("=" * 80)

    loop = asyncio.get_running_loop()
    audio_queue: asyncio.Queue[bytes] = asyncio.Queue()

    def audio_callback(indata, frames, time_info, status):
        if status:
            print(f"Audio status: {status}", file=sys.stderr)
        if indata.ndim > 1 and indata.shape[1] > 1:
            mono_chunk = np.mean(indata, axis=-1, dtype=np.float32)
        elif indata.ndim > 1:
            mono_chunk = indata[:, 0].copy()
        else:
            mono_chunk = indata.copy()
        pcm = float32_to_pcm16(mono_chunk)
        loop.call_soon_threadsafe(audio_queue.put_nowait, pcm)

    async def sender():
        while True:
            pcm = await audio_queue.get()
            await ws.send(pcm)

    async def receiver():
        try:
            while True:
                msg = await ws.recv()
                data = json.loads(msg)
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

                # Top 3 intent categories sorted by probability
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
            pass

    # Open microphone audio stream
    stream = sd.InputStream(
        samplerate=sample_rate,
        channels=channels,
        dtype="float32",
        blocksize=chunk_size,
        callback=audio_callback,
    )

    send_task = asyncio.create_task(sender())
    recv_task = asyncio.create_task(receiver())

    try:
        with stream:
            await asyncio.gather(send_task, recv_task)
    except KeyboardInterrupt:
        print("\nStopping microphone stream...")
    finally:
        send_task.cancel()
        recv_task.cancel()
        await ws.close()
        print("Microphone stream closed.")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "ws://localhost:8000/ws/stream"
    try:
        asyncio.run(stream_live_microphone(url))
    except KeyboardInterrupt:
        pass
