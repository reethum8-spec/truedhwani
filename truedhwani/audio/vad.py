import os
import urllib.request
import logging
from pathlib import Path
import numpy as np
import torch

from truedhwani.config import settings, WEIGHTS_DIR

logger = logging.getLogger(__name__)


class SileroVAD:
    """
    Silero Voice Activity Detection engine.
    Supports low-latency streaming inference on 512-sample (32ms at 16kHz) frames.
    Filters out background noise, breathing, and silence.
    """

    SILERO_ONNX_URL = (
        "https://github.com/snakers4/silero-vad/raw/master/src/silero_vad/data/silero_vad.onnx"
    )

    def __init__(self, sample_rate: int = 16000, threshold: float = 0.5):
        self.sample_rate = sample_rate
        self.threshold = threshold
        self.neg_threshold = settings.vad.neg_threshold
        self.model = None
        self.session = None
        self.use_onnx = False
        self._state = None
        self._load_model()
        self.reset_state()

    def _load_model(self):
        """
        Load Silero VAD model via torch.hub or direct ONNX Runtime.
        """
        onnx_path = WEIGHTS_DIR / "silero_vad.onnx"
        
        # Try PyTorch Hub first (fast and robust native state handling)
        try:
            logger.info("Loading Silero VAD via PyTorch Hub...")
            torch.set_num_threads(1)
            model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                trust_repo=True,
                onnx=False
            )
            self.model = model
            self.model.eval()
            self.use_onnx = False
            logger.info("Silero VAD loaded successfully via PyTorch Hub.")
            return
        except Exception as e:
            logger.warning(f"PyTorch Hub load failed ({e}). Falling back to ONNX...")

        # Fallback to PyTorch Hub
        try:
            logger.info("Attempting to load Silero VAD via torch.hub...")
            torch.set_num_threads(1)
            model, _ = torch.hub.load(
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                trust_repo=True,
                onnx=False
            )
            self.model = model
            self.model.eval()
            self.use_onnx = False
            logger.info("Silero VAD loaded successfully via PyTorch Hub.")
            return
        except Exception as e:
            logger.error(f"PyTorch Hub load failed: {e}")
            raise RuntimeError(f"Could not initialize Silero VAD: {e}")


    def reset_state(self):
        """Reset the internal recurrent state for a new audio stream."""
        if self.use_onnx:
            # Silero V5 ONNX state tensor shape: (2, 1, 128)
            self._state = np.zeros((2, 1, 128), dtype=np.float32)
        else:
            if hasattr(self.model, "reset_states"):
                self.model.reset_states()
            self._state = None

    def process_frame(self, frame: np.ndarray) -> float:
        """
        Process a single audio frame (typically 512 samples at 16kHz).
        Returns speech probability [0.0, 1.0].
        """
        if frame.size != 512:
            # Pad or trim to 512 if slightly off
            if frame.size < 512:
                frame = np.pad(frame, (0, 512 - frame.size), mode="constant")
            else:
                frame = frame[:512]

        if self.use_onnx:
            # ONNX inference
            input_tensor = frame[np.newaxis, :].astype(np.float32)
            sr_tensor = np.array(self.sample_rate, dtype=np.int64)

            # Silero v5 accepts input, state, sr
            inputs = {
                self.session.get_inputs()[0].name: input_tensor,
                self.session.get_inputs()[1].name: self._state,
                self.session.get_inputs()[2].name: sr_tensor,
            }
            outputs = self.session.run(None, inputs)
            prob = float(outputs[0][0, 0])
            self._state = outputs[1]
            return prob
        else:
            # PyTorch inference
            tensor_chunk = torch.from_numpy(frame).float()
            if tensor_chunk.ndim == 1:
                tensor_chunk = tensor_chunk.unsqueeze(0)
            with torch.no_grad():
                prob = float(self.model(tensor_chunk, self.sample_rate).item())
            return prob

    def is_speech(self, frame: np.ndarray) -> tuple[bool, float]:
        """
        Evaluate if a frame contains speech.
        Returns: (is_speech_bool, speech_probability)
        """
        prob = self.process_frame(frame)
        return (prob >= self.threshold), prob
