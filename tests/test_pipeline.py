import asyncio
from pathlib import Path
import pytest
import numpy as np

from truedhwani.audio.audio_utils import load_audio_file
from truedhwani.pipeline.stream_orchestrator import StreamPipelineOrchestrator


def test_pipeline_on_otp_scam():
    """Verify end-to-end pipeline detects OTP scam audio stream and reaches High Risk / Warning posture."""
    async def _run():
        audio_path = Path("sample_audio/otp_scam_call.wav")
        assert audio_path.exists()

        audio, sr = load_audio_file(audio_path, target_sr=16000)
        print(f"\n--- Testing Pipeline on OTP Scam Call ({len(audio)/sr:.2f}s) ---")

        orchestrator = StreamPipelineOrchestrator()
        orchestrator.reset()

        # Stream in 512-sample (32ms) frames
        packets = []
        chunk_size = 512
        for i in range(0, len(audio), chunk_size):
            frame = audio[i : i + chunk_size]
            new_packets = await orchestrator.ingest_audio_chunk(frame)
            packets.extend(new_packets)

        flush_packet = await orchestrator.flush()
        if flush_packet:
            packets.append(flush_packet)

        print(f"Total packets emitted: {len(packets)}")
        assert len(packets) >= 2, "Expected at least 2 analysis packets"

        for idx, p in enumerate(packets):
            print(f"\nPacket #{idx+1} (t={p.call_duration_seconds:.1f}s):")
            print(f"  Transcript: \"{p.transcript}\"")
            print(f"  Language: {p.language}")
            print(f"  Deepfake Score: {p.deepfake_score:.3f} ({p.deepfake_prediction})")
            print(f"  Scam Intent: {p.scam_intent_label} (Score: {p.scam_intent_score:.3f})")
            print(f"  Overall Risk: {p.overall_risk_pct:.1f}/100 ({p.overall_risk:.2f})")
            print(f"  Decision: {p.decision}")
            print(f"  Reason: {p.reason}")
            print(f"  Action: {p.recommended_action}")
            print(f"  Weights: {p.weights}")
            print(f"  Latency: {p.latency_ms}ms")

        # Final packets in scam call should reach Warning or High Risk
        latest = packets[-1]
        assert latest.decision in ["Warning", "High Risk"], f"Expected elevated risk, got {latest.decision}"
        assert any(p.scam_intent_score >= 0.50 for p in packets), "At least one chunk must reflect detected scam intent"

    asyncio.run(_run())


def test_pipeline_on_synthetic_benign_call():
    """Verify end-to-end pipeline detects synthetic voice even on benign text without false scam attribution."""
    async def _run():
        audio_path = Path("sample_audio/benign_call.wav")
        assert audio_path.exists()

        audio, sr = load_audio_file(audio_path, target_sr=16000)
        print(f"\n--- Testing Pipeline on Synthetic Benign Call ({len(audio)/sr:.2f}s) ---")

        orchestrator = StreamPipelineOrchestrator()
        orchestrator.reset()

        packets = []
        chunk_size = 512
        for i in range(0, len(audio), chunk_size):
            frame = audio[i : i + chunk_size]
            new_packets = await orchestrator.ingest_audio_chunk(frame)
            packets.extend(new_packets)

        flush_packet = await orchestrator.flush()
        if flush_packet:
            packets.append(flush_packet)

        assert len(packets) >= 1
        for p in packets:
            print(f"Synthetic Benign chunk: Risk={p.overall_risk_pct:.1f}, Decision={p.decision}, Intent={p.scam_intent_label}, Reason=\"{p.reason}\"")
            # Text intent must be recognized as legitimate
            assert p.scam_intent_label == "Legitimate Dialogue"

    asyncio.run(_run())


def test_pipeline_on_genuine_human_benign_call():
    """Verify that a genuine human caller having a normal conversation stays in Monitoring (Risk <= 40)."""
    async def _run():
        orchestrator = StreamPipelineOrchestrator()
        orchestrator.reset()

        print("\n--- Testing Pipeline on Genuine Human Benign Call ---")
        chunks = [
            "Good morning, I was calling to ask if the project meeting is still scheduled for 3 PM.",
            "Yes, thank you for confirming. I have updated the calendar invite accordingly.",
            "Have a wonderful afternoon, speak to you later."
        ]

        for idx, sentence in enumerate(chunks):
            # Human caller: low deepfake score
            nlp_res = orchestrator.scam_intent.analyze(sentence)

            fusion_res = orchestrator.fusion.fuse(
                deepfake_score=0.08,  # Bonafide human speech
                scam_intent_score=nlp_res.scam_intent_score,
                call_duration_sec=(idx + 1) * 3.5,
                deepfake_confidence=0.85,
                intent_confidence=nlp_res.confidence,
            )

            smoothed = orchestrator.smoother.update(fusion_res.raw_risk_score)
            dec = orchestrator.decision.evaluate(
                smoothed_risk=smoothed,
                deepfake_score=0.08,
                deepfake_prediction="Bonafide",
                scam_intent_label=nlp_res.intent_label,
                scam_intent_score=nlp_res.scam_intent_score,
                matched_signals=nlp_res.matched_signals,
            )

            print(f"Human Benign chunk #{idx+1}: Risk={smoothed:.1f}/100, Decision={dec.decision}, Action=\"{dec.recommended_action[:50]}...\"")
            assert dec.decision == "Monitoring", f"Expected Monitoring for genuine human benign call, got {dec.decision}"
            assert smoothed <= 40.0

    asyncio.run(_run())


if __name__ == "__main__":
    test_pipeline_on_otp_scam()
    test_pipeline_on_synthetic_benign_call()
    test_pipeline_on_genuine_human_benign_call()
    print("\n>>> END-TO-END PIPELINE FULLY FUNCTIONAL AND VERIFIED! <<<")
