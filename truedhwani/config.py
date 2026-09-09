import os
from pathlib import Path
from pydantic import BaseModel, Field

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
WEIGHTS_DIR = BASE_DIR / "weights"
MODELS_CACHE_DIR = BASE_DIR / "models_cache"

WEIGHTS_DIR.mkdir(parents=True, exist_ok=True)
MODELS_CACHE_DIR.mkdir(parents=True, exist_ok=True)


class AudioConfig(BaseModel):
    """Audio streaming configuration."""
    sample_rate: int = 16000
    channels: int = 1  # Mono
    bytes_per_sample: int = 2  # 16-bit PCM
    vad_frame_size: int = 512  # 32ms at 16kHz
    min_speech_duration_sec: float = 2.0  # Min duration before emitting chunk
    max_speech_duration_sec: float = 3.5  # Max duration of chunk for models
    speech_buffer_overlap_sec: float = 0.5  # Sliding overlap


class VADConfig(BaseModel):
    """Silero VAD configuration."""
    threshold: float = 0.5
    neg_threshold: float = 0.35
    min_speech_duration_ms: int = 250
    min_silence_duration_ms: int = 300
    speech_pad_ms: int = 60


class ASRConfig(BaseModel):
    """Faster Whisper configuration."""
    model_size: str = "base"
    device: str = "cpu"
    compute_type: str = "int8"
    beam_size: int = 2
    language: str | None = None  # None for auto-detect
    translate_to_english: bool = True


class DeepfakeConfig(BaseModel):
    """Deepfake detection configuration."""
    model_name: str = "AASIST"
    weights_path: Path = WEIGHTS_DIR / "AASIST.pth"
    aasist_weights_url: str = (
        "https://github.com/clovaai/aasist/raw/main/models/weights/AASIST.pth"
    )
    fallback_hf_model: str = "MelodyMachine/Deepfake-audio-detection-V2"
    target_samples: int = 64600  # Standard AASIST input duration (~4.03s at 16kHz)
    device: str = "cpu"


class ScamIntentConfig(BaseModel):
    """Scam intent analysis configuration."""
    model_name: str = str(WEIGHTS_DIR / "scam_intent_model")
    device: str = "cpu"
    hypothesis_template: str = "This phone call excerpt is an example of {}."
    multilabel: bool = True


class FusionConfig(BaseModel):
    """Adaptive risk fusion configuration."""
    # Dynamic weighting phase thresholds (seconds of speech)
    early_phase_sec: float = 12.0
    mature_phase_sec: float = 35.0

    # Weights at beginning of call
    early_deepfake_weight: float = 0.70
    early_intent_weight: float = 0.30

    # Weights as conversational context increases
    mature_deepfake_weight: float = 0.20
    mature_intent_weight: float = 0.80

    # Non-linear synergy boost when both deepfake and intent are high
    synergy_boost_weight: float = 0.20


class TemporalSmoothingConfig(BaseModel):
    """Temporal smoothing configuration (Asymmetric EMA)."""
    # Fast rise to catch sudden threats quickly
    alpha_rise: float = 0.40
    # Slower decay to maintain caution even during brief pauses
    alpha_fall: float = 0.20
    # Sliding window capacity
    window_size: int = 10


class DecisionConfig(BaseModel):
    """Decision Engine thresholds and actions."""
    monitoring_max: float = 40.0
    warning_max: float = 70.0
    # High Risk: > 70.0


class Settings(BaseModel):
    audio: AudioConfig = Field(default_factory=AudioConfig)
    vad: VADConfig = Field(default_factory=VADConfig)
    asr: ASRConfig = Field(default_factory=ASRConfig)
    deepfake: DeepfakeConfig = Field(default_factory=DeepfakeConfig)
    scam_intent: ScamIntentConfig = Field(default_factory=ScamIntentConfig)
    fusion: FusionConfig = Field(default_factory=FusionConfig)
    smoothing: TemporalSmoothingConfig = Field(default_factory=TemporalSmoothingConfig)
    decision: DecisionConfig = Field(default_factory=DecisionConfig)

    server_host: str = "0.0.0.0"
    server_port: int = 8000


settings = Settings()
