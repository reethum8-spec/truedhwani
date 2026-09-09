import logging
from dataclasses import dataclass
import numpy as np

from truedhwani.config import settings

logger = logging.getLogger(__name__)


@dataclass
class FusionResult:
    """Structured result from Adaptive Risk Fusion Engine."""
    raw_risk_score: float  # Scale [0.0, 100.0]
    weights: dict[str, float]  # Current dynamic weights e.g. {"deepfake": 0.7, "intent": 0.3}
    overall_confidence: float  # [0.0, 1.0]
    call_duration_sec: float
    deepfake_contribution: float
    intent_contribution: float
    synergy_bonus: float


class AdaptiveRiskFusionEngine:
    """
    Adaptive Risk Fusion Engine.
    Dynamically fuses Deepfake biometric scores and Scam Intent semantic scores
    based on conversation duration and individual model confidences.

    - Beginning of call: Deepfake detection dominates (voice cloning is immediate).
    - As conversation progresses: Scam intent dominates (dialogue context unfolds).
    - Non-linear synergy amplification when both detectors trigger.
    """

    def __init__(
        self,
        early_sec: float | None = None,
        mature_sec: float | None = None,
        early_df_weight: float | None = None,
        early_intent_weight: float | None = None,
        mature_df_weight: float | None = None,
        mature_intent_weight: float | None = None,
        synergy_boost: float | None = None,
    ):
        self.early_sec = early_sec or settings.fusion.early_phase_sec
        self.mature_sec = mature_sec or settings.fusion.mature_phase_sec
        self.early_df_w = early_df_weight or settings.fusion.early_deepfake_weight
        self.early_intent_w = early_intent_weight or settings.fusion.early_intent_weight
        self.mature_df_w = mature_df_weight or settings.fusion.mature_deepfake_weight
        self.mature_intent_w = mature_intent_weight or settings.fusion.mature_intent_weight
        self.synergy_boost = synergy_boost or settings.fusion.synergy_boost_weight

    def calculate_weights(self, duration_sec: float) -> tuple[float, float]:
        """
        Calculate dynamic baseline weights for (deepfake, scam_intent)
        as a smooth continuous function of call duration.
        """
        # Clamped progress in [0.0, 1.0]
        if duration_sec <= 0.0:
            progress = 0.0
        elif duration_sec >= self.mature_sec:
            progress = 1.0
        else:
            progress = duration_sec / self.mature_sec

        # Smooth cubic hermite interpolation (smoothstep)
        smooth_p = progress * progress * (3.0 - 2.0 * progress)

        # Interpolate weights
        w_df = self.early_df_w + smooth_p * (self.mature_df_w - self.early_df_w)
        w_intent = self.early_intent_w + smooth_p * (self.mature_intent_w - self.early_intent_w)

        # Normalize to ensure sum == 1.0
        total_w = w_df + w_intent
        return (w_df / total_w, w_intent / total_w)

    def fuse(
        self,
        deepfake_score: float,
        scam_intent_score: float,
        call_duration_sec: float,
        deepfake_confidence: float = 0.8,
        intent_confidence: float = 0.8,
    ) -> FusionResult:
        """
        Fuse acoustic deepfake scores and textual scam intent scores dynamically.
        """
        # Ensure inputs are in [0.0, 1.0]
        s_df = min(1.0, max(0.0, float(deepfake_score)))
        s_intent = min(1.0, max(0.0, float(scam_intent_score)))
        c_df = min(1.0, max(0.1, float(deepfake_confidence)))
        c_intent = min(1.0, max(0.1, float(intent_confidence)))

        # 1. Compute time-dependent dynamic baseline weights
        base_w_df, base_w_intent = self.calculate_weights(call_duration_sec)

        # 2. Modulate weights by model confidences
        # A confident model gets higher authority; uncertain output is downweighted
        adj_w_df = base_w_df * (0.5 + 0.5 * c_df)
        adj_w_intent = base_w_intent * (0.5 + 0.5 * c_intent)
        sum_adj = adj_w_df + adj_w_intent

        final_w_df = adj_w_df / sum_adj
        final_w_intent = adj_w_intent / sum_adj

        # 3. Compute base weighted risk
        df_contribution = final_w_df * s_df
        intent_contribution = final_w_intent * s_intent
        base_risk = df_contribution + intent_contribution

        # 4. Synergy bonus: If both deepfake AND intent are elevated (> 0.4), apply compound multiplier
        synergy_term = 0.0
        if s_df > 0.40 and s_intent > 0.40:
            synergy_term = self.synergy_boost * (s_df * s_intent)

        raw_risk_0_1 = min(1.0, base_risk + synergy_term)
        raw_risk_score = round(raw_risk_0_1 * 100.0, 2)

        # 5. Composite overall confidence
        overall_conf = round(final_w_df * c_df + final_w_intent * c_intent, 4)

        return FusionResult(
            raw_risk_score=raw_risk_score,
            weights={
                "deepfake": round(final_w_df, 4),
                "scam_intent": round(final_w_intent, 4),
            },
            overall_confidence=overall_conf,
            call_duration_sec=round(call_duration_sec, 2),
            deepfake_contribution=round(df_contribution * 100.0, 2),
            intent_contribution=round(intent_contribution * 100.0, 2),
            synergy_bonus=round(synergy_term * 100.0, 2),
        )
