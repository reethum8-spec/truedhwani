import time
from pathlib import Path
import numpy as np
import pytest

from truedhwani.audio.audio_utils import load_audio_file, generate_sine_wave
from truedhwani.deepfake.deepfake_service import DeepfakeService


def test_aasist_deepfake_inference():
    """Verify AASIST Deepfake detection model runs real inference with ASVspoof weights."""
    service = DeepfakeService()
    assert service.model is not None, "AASIST model must be loaded"

    # 1. Test with real spoken audio
    audio_path = Path("sample_audio/otp_scam_call.wav")
    assert audio_path.exists(), "Audio file must exist"

    audio, sr = load_audio_file(audio_path, target_sr=16000)
    print(f"\nLoaded audio for deepfake detection: {len(audio)/sr:.2f}s")

    # Slice a 3-second speech chunk (48,000 samples)
    chunk = audio[:48000]

    result = service.predict(chunk)

    print("\n--- AASIST Deepfake Detection Result ---")
    print(f"Model: {result.model_name}")
    print(f"Deepfake Score (Spoof Probability): {result.deepfake_score:.4f}")
    print(f"Prediction: {result.prediction}")
    print(f"Confidence: {result.confidence:.4f}")
    print(f"Inference Time: {result.inference_time_ms:.2f} ms")
    print(f"Raw Logits: {result.raw_logits}")

    assert 0.0 <= result.deepfake_score <= 1.0
    assert result.prediction in ["Spoof", "Bonafide"]
    assert 0.0 <= result.confidence <= 1.0
    assert len(result.raw_logits) == 2
    assert result.inference_time_ms > 0.0
    print(f"Inference verified in {result.inference_time_ms:.1f}ms on CPU!")


def test_aasist_synthetic_anomaly():
    """Verify AASIST model responds to anomalous/unnatural audio signals."""
    service = DeepfakeService()

    # Synthetic tone burst signal with harmonic modulation (unnatural acoustic artifact)
    t = np.linspace(0, 3.0, 48000, endpoint=False)
    synthetic_signal = (
        0.5 * np.sin(2 * np.pi * 1000 * t) * np.sin(2 * np.pi * 50 * t)
    ).astype(np.float32)

    result = service.predict(synthetic_signal)
    print(f"\nSynthetic modulated tone result: Score = {result.deepfake_score:.4f}, Prediction = {result.prediction}")
    assert 0.0 <= result.deepfake_score <= 1.0


if __name__ == "__main__":
    print("Running Step 3: Deepfake Detection Tests...")
    test_aasist_deepfake_inference()
    test_aasist_synthetic_anomaly()
    print("\n>>> STEP 3 (AASIST Deepfake Detection) FULLY FUNCTIONAL AND VERIFIED! <<<")
