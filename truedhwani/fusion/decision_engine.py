import logging
from dataclasses import dataclass
from truedhwani.config import settings

logger = logging.getLogger(__name__)


@dataclass
class DecisionResult:
    """Structured decision output from Decision Engine."""
    decision: str  # "Monitoring" | "Warning" | "High Risk"
    recommended_action: str
    reason: str
    risk_level: str  # "low" | "medium" | "high"


class DecisionEngine:
    """
    Enterprise Cybersecurity Decision Engine.
    Maps smoothed risk scores to tiered cybersecurity postures:
    - 0–40: Monitoring
    - 41–70: Warning
    - 71–100: High Risk
    """

    def __init__(
        self,
        monitoring_max: float | None = None,
        warning_max: float | None = None,
    ):
        self.monitoring_max = monitoring_max or settings.decision.monitoring_max
        self.warning_max = warning_max or settings.decision.warning_max

    def evaluate(
        self,
        smoothed_risk: float,
        deepfake_score: float,
        deepfake_prediction: str,
        scam_intent_label: str,
        scam_intent_score: float,
        matched_signals: list[str] | None = None,
    ) -> DecisionResult:
        """
        Evaluate smoothed risk and generate decision, action, and detailed operational reason.
        """
        risk = min(100.0, max(0.0, float(smoothed_risk)))
        signals = matched_signals or []

        if risk <= self.monitoring_max:
            decision = "Monitoring"
            risk_level = "low"
            recommended_action = (
                "Continue conversation normally. Acoustic and semantic monitoring active in background."
            )
            reason = (
                "Speech patterns and conversational intent remain within benign thresholds."
            )

        elif risk <= self.warning_max:
            decision = "Warning"
            risk_level = "medium"
            recommended_action = (
                "Exercise caution. Do NOT disclose OTPs, banking credentials, or personal identity details. "
                "Verify caller identity through an official external channel."
            )
            reason = self._synthesize_reason(
                risk=risk,
                decision=decision,
                deepfake_score=deepfake_score,
                deepfake_pred=deepfake_prediction,
                intent_label=scam_intent_label,
                intent_score=scam_intent_score,
                signals=signals,
            )

        else:
            decision = "High Risk"
            risk_level = "high"
            recommended_action = (
                "TERMINATE CALL IMMEDIATELY. High probability of fraudulent cyber scam or biometric spoofing. "
                "Do NOT transfer funds or grant remote access under any circumstance."
            )
            reason = self._synthesize_reason(
                risk=risk,
                decision=decision,
                deepfake_score=deepfake_score,
                deepfake_pred=deepfake_prediction,
                intent_label=scam_intent_label,
                intent_score=scam_intent_score,
                signals=signals,
            )

        return DecisionResult(
            decision=decision,
            recommended_action=recommended_action,
            reason=reason,
            risk_level=risk_level,
        )

    def _synthesize_reason(
        self,
        risk: float,
        decision: str,
        deepfake_score: float,
        deepfake_pred: str,
        intent_label: str,
        intent_score: float,
        signals: list[str],
    ) -> str:
        """Dynamically formulate a concise, informative cybersecurity reason."""
        is_synthetic = deepfake_pred.lower() == "spoof" or deepfake_score > 0.60
        has_scam_intent = intent_score > 0.45 and intent_label != "Legitimate Dialogue"

        if is_synthetic and has_scam_intent:
            reason = (
                f"Synthetic / cloned voice detected (confidence: {int(deepfake_score * 100)}%) "
                f"combined with elevated {intent_label} demands."
            )
        elif is_synthetic:
            reason = (
                f"Synthetic voice anomaly detected (confidence: {int(deepfake_score * 100)}%). "
                "Acoustic spectral patterns indicate AI-generated speech."
            )
        elif has_scam_intent:
            if signals:
                signals_preview = ", ".join(f"'{s}'" for s in signals[:3])
                reason = (
                    f"{intent_label} detected with coercive intent markers: {signals_preview}."
                )
            else:
                reason = f"{intent_label} detected with elevated semantic scam intent."
        else:
            reason = (
                f"Elevated risk score ({int(risk)}) driven by accumulating conversational anomalies."
            )

        return reason
