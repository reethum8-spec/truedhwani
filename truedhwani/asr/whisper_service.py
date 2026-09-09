import time
import logging
from dataclasses import dataclass
import numpy as np
from faster_whisper import WhisperModel

from truedhwani.config import settings, MODELS_CACHE_DIR

logger = logging.getLogger(__name__)


@dataclass
class ASRResult:
    """Structured result from Faster Whisper transcription."""
    transcript: str
    detected_language: str
    language_probability: float
    english_translation: str
    confidence: float
    latency_ms: float


class WhisperService:
    """
    Faster Whisper transcription service.
    Transcribes audio in real-time, auto-detects language (with full Indian languages support),
    and translates non-English speech to English for downstream Scam Intent analysis.
    """

    def __init__(
        self,
        model_size: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
        translate_to_english: bool | None = None,
    ):
        self.model_size = model_size or settings.asr.model_size
        self.device = device or settings.asr.device
        self.compute_type = compute_type or settings.asr.compute_type
        self.translate_to_english = (
            translate_to_english
            if translate_to_english is not None
            else settings.asr.translate_to_english
        )

        logger.info(
            f"Initializing Faster Whisper (model={self.model_size}, device={self.device}, compute_type={self.compute_type})..."
        )
        self.model = WhisperModel(
            model_size_or_path=self.model_size,
            device=self.device,
            compute_type=self.compute_type,
            download_root=str(MODELS_CACHE_DIR),
        )
        logger.info("Faster Whisper model loaded successfully.")

    INITIAL_PROMPT = (
        "A live telephone phone call discussing banking, security, OTP verification, Aadhaar KYC, "
        "customer support, transactions, or everyday conversation."
    )
    HALLUCINATION_PATTERNS = [
        "[BLANK_AUDIO]", "[blank_audio]", "[Silence]", "[silence]",
        "[Music]", "[music]", "[Applause]", "[applause]",
        "Thank you for watching", "Thanks for watching",
        "Subtitles by", "Subscribe to our channel",
    ]

    def _clean_transcript(self, text: str) -> str:
        """Strip Whisper silence hallucinations and repeated artifact tokens."""
        clean = text.strip()
        for pat in self.HALLUCINATION_PATTERNS:
            clean = clean.replace(pat, "").strip()
        return clean

    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> ASRResult:
        """
        Transcribe audio chunk (1D float32 normalized).
        Automatically detects language, transcribes, and optionally translates to English.
        """
        start_time = time.perf_counter()

        if audio.ndim > 1:
            audio = audio.flatten()

        if len(audio) == 0:
            return ASRResult(
                transcript="",
                detected_language="en",
                language_probability=1.0,
                english_translation="",
                confidence=1.0,
                latency_ms=0.0,
            )

        # Run transcription with streaming anti-hallucination parameters
        segments, info = self.model.transcribe(
            audio,
            beam_size=settings.asr.beam_size,
            task="transcribe",
            language=settings.asr.language,
            vad_filter=False,  # We use Silero VAD upstream
            condition_on_previous_text=False,  # Essential for independent streaming chunks
            initial_prompt=self.INITIAL_PROMPT,
            temperature=(0.0, 0.2),
            compression_ratio_threshold=2.4,
            log_prob_threshold=-1.0,
            no_speech_threshold=0.50,
        )

        # Collect segments and compute average confidence
        transcript_parts = []
        confidences = []
        for segment in segments:
            text = self._clean_transcript(segment.text)
            if text:
                transcript_parts.append(text)
                # avg_logprob is log probability (e.g. -0.2). Convert to ~0-1 range
                conf = float(np.exp(segment.avg_logprob))
                confidences.append(min(1.0, max(0.0, conf)))

        full_transcript = " ".join(transcript_parts).strip()
        avg_confidence = float(np.mean(confidences)) if confidences else (info.language_probability if full_transcript else 0.0)

        # Check if translation to English is needed
        detected_lang = info.language
        lang_prob = float(info.language_probability)
        english_translation = full_transcript

        # Only translate if detected language is confidently non-English and contains meaningful text
        if (
            self.translate_to_english
            and detected_lang != "en"
            and lang_prob >= 0.60
            and len(full_transcript.split()) >= 2
        ):
            logger.debug(f"Translating detected language '{detected_lang}' (p={lang_prob:.2f}) to English...")
            trans_segments, _ = self.model.transcribe(
                audio,
                beam_size=settings.asr.beam_size,
                task="translate",
                language=detected_lang,
                vad_filter=False,
                condition_on_previous_text=False,
                initial_prompt=self.INITIAL_PROMPT,
                temperature=0.0,
            )
            trans_parts = [self._clean_transcript(s.text) for s in trans_segments if self._clean_transcript(s.text)]
            if trans_parts:
                english_translation = " ".join(trans_parts).strip()

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return ASRResult(
            transcript=full_transcript,
            detected_language=detected_lang,
            language_probability=lang_prob,
            english_translation=english_translation,
            confidence=round(avg_confidence, 4),
            latency_ms=round(latency_ms, 2),
        )

