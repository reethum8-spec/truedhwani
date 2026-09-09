import io
import math
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy import signal


def pcm16_to_float32(pcm_bytes: bytes) -> np.ndarray:
    """
    Convert raw PCM 16-bit little-endian byte buffer to normalized float32 array in [-1.0, 1.0].
    """
    if not pcm_bytes:
        return np.empty(0, dtype=np.float32)
    # 16-bit signed integer
    int16_arr = np.frombuffer(pcm_bytes, dtype=np.int16)
    return (int16_arr.astype(np.float32) / 32768.0).copy()


def float32_to_pcm16(audio: np.ndarray) -> bytes:
    """
    Convert normalized float32 array to PCM 16-bit little-endian bytes.
    """
    clipped = np.clip(audio, -1.0, 1.0)
    int16_arr = (clipped * 32767.0).astype(np.int16)
    return int16_arr.tobytes()


def ensure_mono(audio: np.ndarray) -> np.ndarray:
    """
    Ensure the audio array is 1-dimensional mono. Downmixes if multichannel.
    """
    if audio.ndim == 1:
        return audio
    elif audio.ndim == 2:
        # Average across channels
        return np.mean(audio, axis=-1, dtype=np.float32)
    else:
        raise ValueError(f"Audio array has unsupported dimensions: {audio.ndim}")


def resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int = 16000) -> np.ndarray:
    """
    Resample 1D float32 audio to target sample rate using polyphase filtering.
    """
    if orig_sr == target_sr:
        return audio.astype(np.float32)
    gcd = math.gcd(orig_sr, target_sr)
    up = target_sr // gcd
    down = orig_sr // gcd
    resampled = signal.resample_poly(audio, up, down)
    return resampled.astype(np.float32)


def load_audio_file(file_source: str | Path | bytes | io.BytesIO, target_sr: int = 16000) -> tuple[np.ndarray, int]:
    """
    Load an audio file or raw audio bytes, convert to mono float32, and resample to target_sr.
    Returns: (audio_array, target_sr)
    """
    if isinstance(file_source, (str, Path)):
        audio, sr = sf.read(str(file_source), dtype="float32")
    elif isinstance(file_source, bytes):
        audio, sr = sf.read(io.BytesIO(file_source), dtype="float32")
    else:
        audio, sr = sf.read(file_source, dtype="float32")

    mono_audio = ensure_mono(audio)
    if sr != target_sr:
        resampled_audio = resample_audio(mono_audio, sr, target_sr)
        return resampled_audio, target_sr
    return mono_audio, target_sr


def generate_sine_wave(freq_hz: float, duration_sec: float, sample_rate: int = 16000) -> np.ndarray:
    """
    Generate a pure sine tone for testing audio pipelines.
    """
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    return (0.3 * np.sin(2 * np.pi * freq_hz * t)).astype(np.float32)
