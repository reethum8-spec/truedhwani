import time
import asyncio
import logging
from dataclasses import dataclass, asdict, field
from concurrent.futures import ThreadPoolExecutor
import numpy as np

from truedhwani.config import settings
from truedhwani.audio.vad import SileroVAD
from truedhwani.audio.buffer import SlidingSpeechBuffer, SpeechChunk
from truedhwani.audio.audio_utils import pcm16_to_float32
from truedhwani.asr.whisper_service import WhisperService, ASRResult
from truedhwani.deepfake.deepfake_service import DeepfakeService, DeepfakeResult
from truedhwani.nlp.scam_intent_service import ScamIntentService, ScamIntentResult
from truedhwani.fusion.adaptive_fusion import AdaptiveRiskFusionEngine, FusionResult
from truedhwani.fusion.temporal_smoothing import TemporalSmoother
from truedhwani.fusion.decision_engine import DecisionEngine, DecisionResult

logger = logging.getLogger(__name__)


@dataclass
class StreamPacket:
    """Real-time JSON packet emitted to WebSocket clients."""
    transcript: str
    language: str
    deepfake_score: float
    scam_intent_score: float
    overall_risk: float  # [0.0, 1.0]
    overall_risk_pct: float  # [0.0, 100.0]
    decision: str
    reason: str
    recommended_action: str
    latency_ms: int
    call_duration_seconds: float
    scam_intent_label: str
    weights: dict[str, float]
    deepfake_prediction: str
    # Granular raw model fields
    silero_speech_prob: float = 0.0
    whisper_language_confidence: float = 0.0
    aasist_spoof_prob: float = 0.0
    distilbert_intent_probabilities: dict[str, float] = field(default_factory=dict)
    adaptive_fusion_weights: dict[str, float] = field(default_factory=dict)
    ema_smoothed_risk: float = 0.0
    biomarkers: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)



class StreamPipelineOrchestrator:
    """
    End-to-end real-time stream processing orchestrator.
    Ingests live audio frames, processes speech chunks in parallel across
    Branch A (Deepfake Detection) and Branch B (ASR + Scam Intent),
    applies Adaptive Risk Fusion, Temporal Smoothing, and Decision Engine.
    """

    def __init__(
        self,
        vad: SileroVAD | None = None,
        whisper: WhisperService | None = None,
        deepfake: DeepfakeService | None = None,
        scam_intent: ScamIntentService | None = None,
        fusion: AdaptiveRiskFusionEngine | None = None,
        smoother: TemporalSmoother | None = None,
        decision: DecisionEngine | None = None,
    ):
        logger.info("Initializing TrueDhwani Stream Pipeline Orchestrator...")
        self.vad = vad or SileroVAD()
        self.buffer = SlidingSpeechBuffer(vad=self.vad)
        self.whisper = whisper or WhisperService()
        self.deepfake = deepfake or DeepfakeService()
        self.scam_intent = scam_intent or ScamIntentService()
        self.fusion = fusion or AdaptiveRiskFusionEngine()
        self.smoother = smoother or TemporalSmoother()
        self.decision = decision or DecisionEngine()

        self._executor = ThreadPoolExecutor(max_workers=4)
        self._recent_transcripts: list[str] = []
        logger.info("Stream Pipeline Orchestrator ready.")

    def reset(self):
        """Reset internal states for a fresh call stream."""
        self.buffer.reset()
        self.smoother.reset()
        self._recent_transcripts.clear()

    async def ingest_pcm_chunk(self, pcm_bytes: bytes) -> list[StreamPacket]:
        """
        Ingest raw PCM 16-bit 16kHz audio bytes.
        Returns a list of StreamPackets if speech chunks triggered evaluation.
        """
        audio_float32 = pcm16_to_float32(pcm_bytes)
        return await self.ingest_audio_chunk(audio_float32)

    async def ingest_audio_chunk(self, audio_float32: np.ndarray) -> list[StreamPacket]:
        """
        Ingest normalized float32 audio chunk into the sliding buffer.
        """
        chunks = self.buffer.ingest(audio_float32)
        packets: list[StreamPacket] = []
        for chunk in chunks:
            packet = await self.process_speech_chunk(chunk)
            if packet is not None:
                packets.append(packet)
        return packets

    async def flush(self) -> StreamPacket | None:
        """Process any remaining speech when a stream terminates."""
        chunk = self.buffer.flush()
        if chunk is not None:
            return await self.process_speech_chunk(chunk)
        return None

    async def process_speech_chunk(self, chunk: SpeechChunk) -> StreamPacket | None:

        """
        Execute parallel Branch A (Deepfake) and Branch B (ASR + Intent) on a speech chunk.
        """
        start_ts = time.perf_counter()
        loop = asyncio.get_running_loop()

        # Acoustic energy check for deepfake safety
        rms_energy = float(np.sqrt(np.mean(chunk.audio ** 2))) if len(chunk.audio) > 0 else 0.0

        def run_deepfake() -> DeepfakeResult:
            if rms_energy < 0.003 or chunk.speech_confidence < 0.20:
                # Return calibrated bonafide default for ultra-quiet/ambient frames
                return DeepfakeResult(
                    deepfake_score=0.02,
                    prediction="Bonafide",
                    confidence=0.98,
                    inference_time_ms=0.0,
                    raw_logits=[-3.5, 2.0],
                    model_name="AASIST",
                )
            return self.deepfake.predict(chunk.audio)

        # Branch A: Deepfake Detection (runs in thread pool)
        task_deepfake = loop.run_in_executor(self._executor, run_deepfake)

        # Branch B: ASR + Scam Intent with rich multi-turn conversational context
        def run_branch_b() -> tuple[ASRResult, ScamIntentResult]:
            asr_res = self.whisper.transcribe(chunk.audio)
            cur_text = asr_res.english_translation.strip() or asr_res.transcript.strip()

            # Accumulate up to 5 recent turns for comprehensive conversational context
            context_sentences = self._recent_transcripts[-5:] + ([cur_text] if cur_text else [])
            context_text = " ".join(s for s in context_sentences if s.strip()).strip()

            nlp_res = self.scam_intent.analyze(context_text)
            if cur_text and (not self._recent_transcripts or cur_text != self._recent_transcripts[-1]):
                self._recent_transcripts.append(cur_text)
            return asr_res, nlp_res

        task_branch_b = loop.run_in_executor(self._executor, run_branch_b)

        # Wait for both branches to complete in parallel
        deepfake_res, (asr_res, nlp_res) = await asyncio.gather(
            task_deepfake, task_branch_b
        )

        # Drop fragments without meaningful transcript
        if not asr_res.transcript.strip():
            return None




        # Adaptive Risk Fusion
        duration_sec = self.buffer.total_duration_sec
        fusion_res = self.fusion.fuse(
            deepfake_score=deepfake_res.deepfake_score,
            scam_intent_score=nlp_res.scam_intent_score,
            call_duration_sec=duration_sec,
            deepfake_confidence=deepfake_res.confidence,
            intent_confidence=nlp_res.confidence,
        )

        # Temporal Smoothing
        smoothed_risk_pct = self.smoother.update(fusion_res.raw_risk_score)
        smoothed_risk_0_1 = round(smoothed_risk_pct / 100.0, 4)

        # Decision Engine
        decision_res = self.decision.evaluate(
            smoothed_risk=smoothed_risk_pct,
            deepfake_score=deepfake_res.deepfake_score,
            deepfake_prediction=deepfake_res.prediction,
            scam_intent_label=nlp_res.intent_label,
            scam_intent_score=nlp_res.scam_intent_score,
            matched_signals=nlp_res.matched_signals,
        )

        total_latency_ms = int((time.perf_counter() - start_ts) * 1000.0)

        packet = StreamPacket(
            transcript=asr_res.transcript,
            language=asr_res.detected_language,
            deepfake_score=deepfake_res.deepfake_score,
            scam_intent_score=nlp_res.scam_intent_score,
            overall_risk=smoothed_risk_0_1,
            overall_risk_pct=smoothed_risk_pct,
            decision=decision_res.decision,
            reason=decision_res.reason,
            recommended_action=decision_res.recommended_action,
            latency_ms=total_latency_ms,
            call_duration_seconds=round(duration_sec, 2),
            scam_intent_label=nlp_res.intent_label,
            weights=fusion_res.weights,
            deepfake_prediction=deepfake_res.prediction,
            silero_speech_prob=round(chunk.speech_confidence, 4),
            whisper_language_confidence=round(asr_res.language_probability, 4),
            aasist_spoof_prob=deepfake_res.deepfake_score,
            distilbert_intent_probabilities=nlp_res.category_scores,
            adaptive_fusion_weights=fusion_res.weights,
            ema_smoothed_risk=smoothed_risk_pct,
            biomarkers=deepfake_res.biomarkers,
        )

        return packet

