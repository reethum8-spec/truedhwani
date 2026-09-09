import collections
import logging
from dataclasses import dataclass
import numpy as np

from truedhwani.config import settings
from truedhwani.audio.vad import SileroVAD

logger = logging.getLogger(__name__)


@dataclass
class SpeechChunk:
    """A slice of accumulated speech ready for downstream model processing."""
    audio: np.ndarray  # 1D float32 normalized speech
    sample_rate: int
    duration_sec: float
    start_sec: float
    end_sec: float
    speech_confidence: float


class SlidingSpeechBuffer:
    """
    Sliding audio buffer with real-time VAD filtering.
    Ingests continuous streaming frames, discards silence, and emits
    2.0–3.5 second speech chunks for parallel ASR and Deepfake processing.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        frame_size: int = 512,
        min_speech_sec: float = 2.0,
        max_speech_sec: float = 3.5,
        overlap_sec: float = 0.5,
        vad: SileroVAD | None = None
    ):
        self.sample_rate = sample_rate
        self.frame_size = frame_size
        self.min_speech_samples = int(min_speech_sec * sample_rate)
        self.max_speech_samples = int(max_speech_sec * sample_rate)
        self.overlap_samples = int(overlap_sec * sample_rate)

        self.vad = vad or SileroVAD(sample_rate=sample_rate)
        
        # Internal FIFO for raw incoming audio samples
        self._raw_queue = collections.deque()

        # Accumulated speech buffer
        self._speech_frames: list[np.ndarray] = []
        self._speech_probs: list[float] = []

        # Rolling pre-roll buffer of ambient/silence frames (~350ms lead-in)
        # Keeps acoustic room context to prevent SincNet boundary shock on speech onset
        self._preroll_capacity = max(10, int(0.35 * sample_rate / frame_size))  # ~11 frames (352ms)
        self._preroll_frames = collections.deque(maxlen=self._preroll_capacity)

        # Silence tracking
        self._silence_frames_count = 0
        self._max_silence_frames = int(
            (settings.vad.min_silence_duration_ms / 1000.0) * (sample_rate / frame_size)
        )

        # Stream timing
        self._total_samples_ingested = 0
        self._speech_chunk_start_sample = 0

    def reset(self):
        """Reset the buffer state for a fresh stream."""
        self._raw_queue.clear()
        self._speech_frames.clear()
        self._speech_probs.clear()
        self._preroll_frames.clear()
        self._silence_frames_count = 0
        self._total_samples_ingested = 0
        self._speech_chunk_start_sample = 0
        self.vad.reset_state()

    @property
    def total_duration_sec(self) -> float:
        """Total stream duration ingested so far in seconds."""
        return self._total_samples_ingested / self.sample_rate

    def ingest(self, audio_data: np.ndarray) -> list[SpeechChunk]:
        """
        Ingest an arbitrary chunk of 16kHz float32 audio.
        Returns a list of complete SpeechChunks (if threshold reached).
        """
        if audio_data.ndim > 1:
            audio_data = audio_data.flatten()

        # Extend incoming raw queue
        self._raw_queue.extend(audio_data.tolist())
        self._total_samples_ingested += len(audio_data)

        emitted_chunks: list[SpeechChunk] = []

        # Process frames of size 512
        while len(self._raw_queue) >= self.frame_size:
            frame = np.array([self._raw_queue.popleft() for _ in range(self.frame_size)], dtype=np.float32)
            is_voice, prob = self.vad.is_speech(frame)

            if is_voice:
                if not self._speech_frames:
                    # Start of a new speech utterance: prepend acoustic lead-in frames
                    if self._preroll_frames:
                        self._speech_frames.extend(list(self._preroll_frames))
                        self._speech_probs.extend([0.05] * len(self._preroll_frames))
                    self._speech_chunk_start_sample = max(
                        0, self._total_samples_ingested - len(self._raw_queue) - (len(self._speech_frames) * self.frame_size)
                    )
                self._speech_frames.append(frame)
                self._speech_probs.append(prob)
                self._silence_frames_count = 0
                # Pre-roll is incorporated into speech utterance
                self._preroll_frames.clear()
            else:
                # Silence frame
                if self._speech_frames:
                    self._silence_frames_count += 1
                    # Keep small trailing silence for natural acoustics (post-roll hangover)
                    if self._silence_frames_count <= 4:
                        self._speech_frames.append(frame)
                        self._speech_probs.append(prob)
                else:
                    # Rolling buffer of ambient frames while awaiting speech
                    self._preroll_frames.append(frame)

            # Check if accumulated speech has reached maximum duration (continuous speaking)
            curr_speech_samples = sum(len(f) for f in self._speech_frames)
            if curr_speech_samples >= self.max_speech_samples:
                chunk = self._build_chunk(curr_speech_samples)
                if chunk is not None:
                    emitted_chunks.append(chunk)
                # Keep sliding overlap for temporal continuity
                self._apply_overlap()

            # Or if speaker paused (silence threshold reached) and we have enough speech
            elif self._speech_frames and self._silence_frames_count >= self._max_silence_frames:
                # Minimum 0.7s of speech for a complete spoken utterance on natural pause
                if curr_speech_samples >= int(0.70 * self.sample_rate):
                    chunk = self._build_chunk(curr_speech_samples)
                    if chunk is not None:
                        emitted_chunks.append(chunk)
                # Seed rolling pre-roll buffer with recent silence frames for subsequent utterance
                trailing = self._speech_frames[-self._preroll_capacity:]
                self._speech_frames.clear()
                self._speech_probs.clear()
                self._silence_frames_count = 0
                self._preroll_frames.clear()
                self._preroll_frames.extend(trailing)


        return emitted_chunks

    def _build_chunk(self, total_samples: int) -> SpeechChunk | None:
        """Construct a SpeechChunk from currently accumulated frames with RMS energy validation."""
        if not self._speech_frames:
            return None
        audio = np.concatenate(self._speech_frames)
        # Verify non-trivial RMS energy so flat silence / pure mic hiss isn't emitted as speech
        rms = float(np.sqrt(np.mean(audio ** 2))) if len(audio) > 0 else 0.0
        if rms < 0.0015:  # Below acoustic vocal threshold
            return None

        duration_sec = total_samples / self.sample_rate
        start_sec = self._speech_chunk_start_sample / self.sample_rate
        end_sec = start_sec + duration_sec
        avg_confidence = float(np.mean(self._speech_probs)) if self._speech_probs else 0.0

        return SpeechChunk(
            audio=audio,
            sample_rate=self.sample_rate,
            duration_sec=duration_sec,
            start_sec=start_sec,
            end_sec=end_sec,
            speech_confidence=avg_confidence,
        )

    def _apply_overlap(self):
        """Preserve overlapping frames when cutting mid-speech."""
        if not self._speech_frames:
            return
        num_overlap_frames = max(1, self.overlap_samples // self.frame_size)
        self._speech_frames = self._speech_frames[-num_overlap_frames:]
        self._speech_probs = self._speech_probs[-num_overlap_frames:]
        self._speech_chunk_start_sample = (
            self._total_samples_ingested - len(self._raw_queue) - (len(self._speech_frames) * self.frame_size)
        )

    def flush(self) -> SpeechChunk | None:
        """Flush any remaining speech in the buffer when stream completes."""
        curr_samples = sum(len(f) for f in self._speech_frames)
        chunk = None
        if curr_samples >= int(0.30 * self.sample_rate):  # At least 0.3s of speech
            chunk = self._build_chunk(curr_samples)
        self._speech_frames.clear()
        self._speech_probs.clear()
        self._silence_frames_count = 0
        return chunk

