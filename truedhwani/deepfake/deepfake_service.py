import math
import time
import logging
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import torch
import torch.nn.functional as F

from truedhwani.config import settings, WEIGHTS_DIR
from truedhwani.deepfake.aasist_model import Model as AASISTModel

logger = logging.getLogger(__name__)


@dataclass
class DeepfakeResult:
    """Structured result from Deepfake Detection."""
    deepfake_score: float  # [0.0, 1.0] probability of spoof / synthetic audio
    prediction: str  # "Spoof" | "Bonafide"
    confidence: float  # Model certainty in the prediction
    inference_time_ms: float
    raw_logits: list[float]
    model_name: str


class DeepfakeService:
    """
    Audio Anti-Spoofing and Deepfake Detection Service.
    Powered by official pretrained AASIST (ASVspoof 2019 LA benchmark).
    """

    AASIST_CONFIG = {
        "architecture": "AASIST",
        "nb_samp": 64600,
        "first_conv": 128,
        "filts": [70, [1, 32], [32, 32], [32, 64], [64, 64]],
        "gat_dims": [64, 32],
        "pool_ratios": [0.5, 0.7, 0.5, 0.5],
        "temperatures": [2.0, 2.0, 100.0, 100.0],
    }

    def __init__(
        self,
        weights_path: Path | str | None = None,
        device: str | None = None,
    ):
        self.device = device or settings.deepfake.device
        self.weights_path = Path(weights_path or settings.deepfake.weights_path)
        self.target_samples = settings.deepfake.target_samples  # 64,600 samples
        self.model = None

        self._load_model()

    def _load_model(self):
        """Initialize AASIST architecture and load ASVspoof 2019 LA pretrained weights."""
        logger.info("Initializing AASIST Deepfake Detector...")
        if not self.weights_path.exists():
            logger.info(f"Downloading AASIST weights from {settings.deepfake.aasist_weights_url}...")
            import urllib.request
            self.weights_path.parent.mkdir(parents=True, exist_ok=True)
            urllib.request.urlretrieve(settings.deepfake.aasist_weights_url, str(self.weights_path))
            logger.info(f"Saved AASIST weights to {self.weights_path}")

        try:
            self.model = AASISTModel(self.AASIST_CONFIG)
            state_dict = torch.load(str(self.weights_path), map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"AASIST loaded successfully on {self.device}.")
        except Exception as e:
            logger.error(f"Failed to load AASIST weights: {e}")
            raise RuntimeError(f"AASIST initialization error: {e}")

    def _pad_or_trim(self, audio: np.ndarray) -> np.ndarray:
        """
        Pad (circular repetition with edge tapering) or trim audio to exact target length
        (64,600 samples) following ASVspoof protocol without transient boundary clicks.
        """
        num_samples = len(audio)
        if num_samples == self.target_samples:
            return audio
        elif num_samples < self.target_samples:
            # Smooth 10ms edge taper before tiling to eliminate step discontinuities
            fade_len = min(160, num_samples // 4)
            tapered = audio.copy()
            if fade_len > 0:
                window = np.hanning(fade_len * 2)
                tapered[:fade_len] *= window[:fade_len]
                tapered[-fade_len:] *= window[fade_len:]
            repeat_factor = math.ceil(self.target_samples / max(1, num_samples))
            repeated = np.tile(tapered, repeat_factor)
            return repeated[:self.target_samples]
        else:
            # Preserve natural acoustic onset and pre-roll context from the start
            return audio[:self.target_samples]

    def predict(self, audio: np.ndarray) -> DeepfakeResult:
        """
        Run deepfake detection on an audio chunk.
        Returns: DeepfakeResult with score, prediction, confidence, and inference time.
        """
        start_time = time.perf_counter()

        if audio.ndim > 1:
            audio = audio.flatten()

        # Prepare 64,600 samples tensor
        proc_audio = self._pad_or_trim(audio).astype(np.float32)
        tensor = torch.from_numpy(proc_audio).unsqueeze(0).to(self.device)

        with torch.no_grad():
            _, logits = self.model(tensor)
            # Logits shape: (1, 2) where index 0 = Spoof, index 1 = Bonafide
            logit_spoof = float(logits[0, 0].item())
            logit_bonafide = float(logits[0, 1].item())

        # ASVspoof 2019 LA logit calibration:
        # AASIST was trained with CrossEntropyLoss(weight=[0.1, 0.9]) creating an inherent ~ +2.2 prior shift.
        # The official Clova AI AASIST evaluation metric uses Δ = logit_spoof - logit_bonafide.
        # We apply prior bias correction (bias = 2.0) and temperature scaling (T = 1.8) into a calibrated probability [0, 1].
        diff = logit_spoof - logit_bonafide
        calibrated_z = (diff - 2.0) / 1.8
        clamped_z = max(-20.0, min(20.0, calibrated_z))
        p_spoof = 1.0 / (1.0 + math.exp(-clamped_z))
        p_bonafide = 1.0 - p_spoof

        # Prediction threshold at 0.50
        is_spoof = p_spoof >= 0.50
        prediction = "Spoof" if is_spoof else "Bonafide"
        confidence = p_spoof if is_spoof else p_bonafide

        inference_time_ms = (time.perf_counter() - start_time) * 1000.0

        return DeepfakeResult(
            deepfake_score=round(p_spoof, 4),
            prediction=prediction,
            confidence=round(confidence, 4),
            inference_time_ms=round(inference_time_ms, 2),
            raw_logits=[round(logit_spoof, 4), round(logit_bonafide, 4)],
            model_name="AASIST",
        )
