import collections
import logging
from truedhwani.config import settings

logger = logging.getLogger(__name__)


class TemporalSmoother:
    """
    Temporal Smoothing Engine using Asymmetric Exponential Moving Average (EMA)
    and Rolling Window statistics.

    - Mitigates momentary acoustic artifacts or isolated ambiguous keywords.
    - Prevents single sentences from immediately triggering false positive alarms.
    - Fast-rise (alpha_rise=0.40) ensures responsiveness to real, sustained threats.
    - Slow-decay (alpha_fall=0.20) ensures persistence of caution during conversation pauses.
    """

    def __init__(
        self,
        alpha_rise: float | None = None,
        alpha_fall: float | None = None,
        window_size: int | None = None,
    ):
        self.alpha_rise = alpha_rise or settings.smoothing.alpha_rise
        self.alpha_fall = alpha_fall or settings.smoothing.alpha_fall
        self.window_size = window_size or settings.smoothing.window_size

        self.current_smoothed_risk: float | None = None
        self.history: collections.deque[float] = collections.deque(maxlen=self.window_size)

    def reset(self):
        """Reset state for a new call stream."""
        self.current_smoothed_risk = None
        self.history.clear()

    def update(self, raw_risk: float) -> float:
        """
        Update the smoother with a new raw risk score [0.0, 100.0].
        Returns the updated smoothed risk score [0.0, 100.0].
        """
        clamped_raw = min(100.0, max(0.0, float(raw_risk)))
        self.history.append(clamped_raw)

        if self.current_smoothed_risk is None:
            # Initialize with first observation
            self.current_smoothed_risk = clamped_raw
            return round(self.current_smoothed_risk, 2)

        # Asymmetric EMA selection
        if clamped_raw >= self.current_smoothed_risk:
            alpha = self.alpha_rise
        else:
            alpha = self.alpha_fall

        self.current_smoothed_risk = (
            alpha * clamped_raw + (1.0 - alpha) * self.current_smoothed_risk
        )

        return round(self.current_smoothed_risk, 2)

    @property
    def rolling_mean(self) -> float:
        """Mean of recent window."""
        return round(float(sum(self.history) / len(self.history)), 2) if self.history else 0.0

    @property
    def peak_risk(self) -> float:
        """Maximum risk observed in the recent window."""
        return round(float(max(self.history)), 2) if self.history else 0.0

    @property
    def trend(self) -> str:
        """Assess whether risk is currently rising, falling, or stable."""
        if len(self.history) < 3:
            return "stable"
        recent = list(self.history)[-3:]
        diff = recent[-1] - recent[0]
        if diff > 5.0:
            return "increasing"
        elif diff < -5.0:
            return "decreasing"
        return "stable"
