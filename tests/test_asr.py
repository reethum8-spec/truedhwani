import time
from pathlib import Path
import pytest

from truedhwani.audio.audio_utils import load_audio_file
from truedhwani.asr.whisper_service import WhisperService


def test_whisper_transcription():
    """Verify Faster Whisper transcribes real spoken audio accurately."""
    audio_path = Path("sample_audio/otp_scam_call.wav")
    assert audio_path.exists(), "Audio file must exist"

    audio, sr = load_audio_file(audio_path, target_sr=16000)
    print(f"\nLoaded audio: {len(audio)/sr:.2f}s")

    whisper = WhisperService(model_size="base", device="cpu", compute_type="int8")

    # Transcribe audio
    start = time.perf_counter()
    result = whisper.transcribe(audio)
    elapsed_ms = (time.perf_counter() - start) * 1000.0

    print("\n--- Faster Whisper ASR Results ---")
    print(f"Transcript: '{result.transcript}'")
    print(f"Detected Language: {result.detected_language} (prob: {result.language_probability:.3f})")
    print(f"English Translation: '{result.english_translation}'")
    print(f"Confidence: {result.confidence:.3f}")
    print(f"Reported Latency: {result.latency_ms} ms (Wall clock: {elapsed_ms:.1f} ms)")

    assert len(result.transcript) > 10, "Expected non-empty transcript"
    assert result.detected_language in ["en"], f"Expected English language, got {result.detected_language}"
    assert result.confidence > 0.5, f"Expected confidence > 0.5, got {result.confidence}"
    
    # Check that key spoken words were recognized
    transcript_lower = result.transcript.lower()
    assert any(term in transcript_lower for term in ["otp", "bank", "verification", "card", "mobile", "code"]), \
        f"Transcript did not contain expected terms: {result.transcript}"


def test_whisper_chunk_latency():
    """Verify transcription on 2.5 second chunk completes within acceptable real-time window."""
    audio_path = Path("sample_audio/benign_call.wav")
    audio, sr = load_audio_file(audio_path, target_sr=16000)

    # Slice a 2.5 second chunk (40,000 samples)
    chunk = audio[:40000]

    whisper = WhisperService(model_size="base", device="cpu", compute_type="int8")
    result = whisper.transcribe(chunk)

    print(f"\nChunk transcription ({len(chunk)/sr:.2f}s): '{result.transcript}' in {result.latency_ms} ms")
    assert result.latency_ms < 2500, f"Latency {result.latency_ms}ms exceeded real-time 2.5s duration"


if __name__ == "__main__":
    print("Running Step 2: Faster Whisper Integration Tests...")
    test_whisper_transcription()
    test_whisper_chunk_latency()
    print("\n>>> STEP 2 (Faster Whisper ASR) FULLY FUNCTIONAL AND VERIFIED! <<<")
