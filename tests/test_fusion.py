import pytest

from truedhwani.fusion.adaptive_fusion import AdaptiveRiskFusionEngine
from truedhwani.fusion.temporal_smoothing import TemporalSmoother
from truedhwani.fusion.decision_engine import DecisionEngine


def test_adaptive_fusion_dynamic_weighting():
    """Verify weights change dynamically with call duration (not fixed)."""
    engine = AdaptiveRiskFusionEngine(early_sec=12.0, mature_sec=35.0)

    # 1. Beginning of call (t = 2 seconds)
    res_early = engine.fuse(
        deepfake_score=0.85,
        scam_intent_score=0.30,
        call_duration_sec=2.0,
        deepfake_confidence=0.9,
        intent_confidence=0.5,
    )
    w_df_early = res_early.weights["deepfake"]
    w_intent_early = res_early.weights["scam_intent"]

    print("\n--- Early Call Fusion (t = 2s) ---")
    print(f"Weights: Deepfake = {w_df_early:.3f}, Scam Intent = {w_intent_early:.3f}")
    print(f"Raw Risk Score: {res_early.raw_risk_score:.2f}")

    # Deepfake must dominate early in the call
    assert w_df_early > w_intent_early, "Deepfake weight should be higher than intent early in the call"
    assert w_df_early >= 0.60

    # 2. Mature call (t = 45 seconds)
    res_mature = engine.fuse(
        deepfake_score=0.30,
        scam_intent_score=0.85,
        call_duration_sec=45.0,
        deepfake_confidence=0.8,
        intent_confidence=0.9,
    )
    w_df_mature = res_mature.weights["deepfake"]
    w_intent_mature = res_mature.weights["scam_intent"]

    print("\n--- Mature Call Fusion (t = 45s) ---")
    print(f"Weights: Deepfake = {w_df_mature:.3f}, Scam Intent = {w_intent_mature:.3f}")
    print(f"Raw Risk Score: {res_mature.raw_risk_score:.2f}")

    # Scam intent must dominate later in the call
    assert w_intent_mature > w_df_mature, "Intent weight should be higher than deepfake in mature call"
    assert w_intent_mature >= 0.70

    # Verify weights are NOT fixed
    assert w_df_early != w_df_mature
    assert w_intent_early != w_intent_mature


def test_synergy_boost():
    """Verify non-linear amplification when BOTH deepfake and scam intent are high."""
    engine = AdaptiveRiskFusionEngine()

    # Both deepfake AND intent are high (e.g. 0.80 and 0.85)
    res_synergy = engine.fuse(
        deepfake_score=0.80,
        scam_intent_score=0.85,
        call_duration_sec=20.0,
    )
    print(f"\nSynergy bonus: {res_synergy.synergy_bonus:.2f} (Total risk: {res_synergy.raw_risk_score:.2f})")
    assert res_synergy.synergy_bonus > 0.0
    assert res_synergy.raw_risk_score >= 85.0


def test_temporal_smoothing_prevents_false_positive_spike():
    """Verify a single anomalous sentence does not immediately trigger High Risk."""
    smoother = TemporalSmoother(alpha_rise=0.40, alpha_fall=0.20)

    # Initial baseline benign call
    s1 = smoother.update(15.0)
    s2 = smoother.update(20.0)
    assert s2 <= 20.0

    # Single sudden spike to 90.0 (e.g. misrecognized word or transient noise)
    s3 = smoother.update(90.0)
    print(f"\nSingle frame spike from 20.0 to 90.0 -> Smoothed: {s3:.2f}")
    # Must NOT immediately jump into High Risk (> 70)
    assert s3 < 70.0, f"Expected smoothed risk < 70.0 after single spike, got {s3}"

    # Sustained threat: consecutive high-risk frames
    s4 = smoother.update(92.0)
    s5 = smoother.update(95.0)
    print(f"Sustained threat frames: {s4:.2f} -> {s5:.2f}")
    assert s5 > 70.0, f"Expected sustained threat to breach High Risk (> 70.0), got {s5}"


def test_decision_engine():
    """Verify DecisionEngine outputs correct categories, actions, and detailed reasons."""
    decision_engine = DecisionEngine()

    # 1. Monitoring (Risk: 25)
    d_mon = decision_engine.evaluate(
        smoothed_risk=25.0,
        deepfake_score=0.15,
        deepfake_prediction="Bonafide",
        scam_intent_label="Legitimate Dialogue",
        scam_intent_score=0.10,
    )
    assert d_mon.decision == "Monitoring"
    assert "normally" in d_mon.recommended_action.lower()

    # 2. Warning (Risk: 55)
    d_warn = decision_engine.evaluate(
        smoothed_risk=55.0,
        deepfake_score=0.35,
        deepfake_prediction="Bonafide",
        scam_intent_label="Bank Verification Scams",
        scam_intent_score=0.60,
        matched_signals=["account blocked"],
    )
    assert d_warn.decision == "Warning"
    assert "caution" in d_warn.recommended_action.lower()
    assert "Bank Verification Scams" in d_warn.reason

    # 3. High Risk (Risk: 82)
    d_high = decision_engine.evaluate(
        smoothed_risk=82.0,
        deepfake_score=0.92,
        deepfake_prediction="Spoof",
        scam_intent_label="OTP Scams",
        scam_intent_score=0.88,
        matched_signals=["otp", "verification code"],
    )
    assert d_high.decision == "High Risk"
    assert "TERMINATE CALL IMMEDIATELY" in d_high.recommended_action
    assert "Synthetic / cloned voice" in d_high.reason


if __name__ == "__main__":
    print("Running Step 5 & 6: Adaptive Fusion, Smoothing & Decision Engine Tests...")
    test_adaptive_fusion_dynamic_weighting()
    test_synergy_boost()
    test_temporal_smoothing_prevents_false_positive_spike()
    test_decision_engine()
    print("\n>>> STEPS 5 & 6 (Adaptive Fusion & Smoothing) FULLY FUNCTIONAL AND VERIFIED! <<<")
