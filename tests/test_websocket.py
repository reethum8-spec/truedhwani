import json
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

from truedhwani.server.app import app
from truedhwani.audio.audio_utils import load_audio_file, float32_to_pcm16


def test_health_endpoint():
    """Verify GET /api/health returns online status and registered models."""
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    print("\n--- Health Endpoint Response ---")
    print(json.dumps(data, indent=2))
    assert data["status"] == "online"
    assert "vad" in data["models"]
    assert "asr" in data["models"]
    assert "deepfake" in data["models"]
    assert "scam_intent" in data["models"]


def test_analyze_audio_file_endpoint():
    """Verify POST /api/analyze-audio processes uploaded WAV file."""
    audio_path = Path("sample_audio/otp_scam_call.wav")
    assert audio_path.exists()

    with TestClient(app) as client:
        with open(audio_path, "rb") as f:
            response = client.post(
                "/api/analyze-audio",
                files={"file": ("otp_scam_call.wav", f, "audio/wav")}
            )
        assert response.status_code == 200
        data = response.json()
        print("\n--- Analyze Audio File Response Summary ---")
        print(f"File: {data['filename']}")
        print(f"Duration: {data['duration_seconds']}s")
        print(f"Emitted Chunks: {data['total_emitted_chunks']}")
        print(f"Peak Risk: {data['peak_overall_risk']}")
        print(f"Final Decision: {data['final_decision']}")
        print(f"Consolidated Transcript: \"{data['consolidated_transcript']}\"")
        assert data["total_emitted_chunks"] >= 2
        assert data["final_decision"] in ["Warning", "High Risk"]


def test_websocket_stream_integration():
    """Verify real-time WebSocket stream returns structured JSON packets."""
    audio_path = Path("sample_audio/otp_scam_call.wav")
    audio, sr = load_audio_file(audio_path, target_sr=16000)

    with TestClient(app) as client:
        with client.websocket_connect("/ws/stream") as websocket:
            print("\nConnected to WebSocket /ws/stream via TestClient!")

            # Send first 4 seconds of audio (64,000 samples) in 512 chunks
            chunk_size = 512
            received_packets = []
            
            for i in range(0, 64000, chunk_size):
                frame = audio[i : i + chunk_size]
                pcm_bytes = float32_to_pcm16(frame)
                websocket.send_bytes(pcm_bytes)

            # Flush
            websocket.send_text(json.dumps({"action": "flush"}))

            # Receive packets
            while True:
                try:
                    data = websocket.receive_json()
                    if "overall_risk" in data:
                        received_packets.append(data)
                        print(f"WS Packet received: Decision={data['decision']}, Risk={data['overall_risk']}, Latency={data['latency_ms']}ms")
                    elif data.get("status") == "stream_flushed":
                        break
                except Exception:
                    break

            print(f"Total packets received over WebSocket: {len(received_packets)}")
            assert len(received_packets) >= 1

            pkt = received_packets[0]
            # Verify exact required JSON schema
            required_keys = [
                "transcript", "language", "deepfake_score", "scam_intent_score",
                "overall_risk", "decision", "reason", "latency_ms"
            ]
            for k in required_keys:
                assert k in pkt, f"Missing required key in JSON output: {k}"

            print("WebSocket JSON format verified perfectly!")


if __name__ == "__main__":
    test_health_endpoint()
    test_analyze_audio_file_endpoint()
    test_websocket_stream_integration()
    print("\n>>> WEBSOCKET & REST API FULLY FUNCTIONAL AND VERIFIED! <<<")
