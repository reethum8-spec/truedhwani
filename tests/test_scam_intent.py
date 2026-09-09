import time
import pytest

from truedhwani.nlp.scam_intent_service import ScamIntentService


def test_scam_intent_analysis():
    """Verify ScamIntentService classifies scam transcripts vs legitimate dialogue accurately."""
    service = ScamIntentService()

    # 1. Test OTP Scam dialogue
    otp_text = (
        "Sir I am calling from State Bank verification unit. Your debit card has been blocked "
        "due to suspicious activity. I have sent a 6-digit OTP code to your registered mobile number. "
        "Please share the OTP code immediately to unblock your account."
    )
    res_otp = service.analyze(otp_text)
    print("\n--- OTP Scam Analysis ---")
    print(f"Text: '{otp_text[:70]}...'")
    print(f"Detected Intent: {res_otp.intent_label}")
    print(f"Scam Intent Score: {res_otp.scam_intent_score}")
    print(f"Confidence: {res_otp.confidence}")
    print(f"Explanation: {res_otp.explanation}")
    print(f"Matched Signals: {res_otp.matched_signals}")
    print(f"Latency: {res_otp.latency_ms} ms")

    assert res_otp.scam_intent_score > 0.65, f"Expected high scam score for OTP text, got {res_otp.scam_intent_score}"
    assert res_otp.intent_label in ["OTP Scams", "Bank Verification Scams"]
    assert len(res_otp.explanation) > 20

    # 2. Test KYC Impersonation dialogue
    kyc_text = (
        "This is customs department Mumbai airport. A parcel containing illegal items and passports "
        "registered under your Aadhaar number has been seized. An arrest warrant will be issued if "
        "you do not complete biometric KYC immediately."
    )
    res_kyc = service.analyze(kyc_text)
    print("\n--- KYC Impersonation Analysis ---")
    print(f"Text: '{kyc_text[:70]}...'")
    print(f"Detected Intent: {res_kyc.intent_label}")
    print(f"Scam Intent Score: {res_kyc.scam_intent_score}")
    print(f"Confidence: {res_kyc.confidence}")
    print(f"Explanation: {res_kyc.explanation}")
    print(f"Matched Signals: {res_kyc.matched_signals}")
    print(f"Latency: {res_kyc.latency_ms} ms")

    assert res_kyc.scam_intent_score > 0.65, f"Expected high scam score for KYC text, got {res_kyc.scam_intent_score}"
    assert res_kyc.intent_label in ["KYC Scams", "Identity Impersonation", "Threat/Urgency Manipulation"]

    # 3. Test Benign dialogue
    benign_text = (
        "Hi Rahul, hope you are doing well today. I was reviewing the notes from our team meeting "
        "and wanted to check if you have time for a quick project sync after lunch tomorrow."
    )
    res_benign = service.analyze(benign_text)
    print("\n--- Benign Dialogue Analysis ---")
    print(f"Text: '{benign_text[:70]}...'")
    print(f"Detected Intent: {res_benign.intent_label}")
    print(f"Scam Intent Score: {res_benign.scam_intent_score}")
    print(f"Confidence: {res_benign.confidence}")
    print(f"Explanation: {res_benign.explanation}")
    print(f"Latency: {res_benign.latency_ms} ms")

    assert res_benign.scam_intent_score < 0.35, f"Expected low scam score for benign text, got {res_benign.scam_intent_score}"
    assert res_benign.intent_label == "Legitimate Dialogue"


if __name__ == "__main__":
    print("Running Step 4: Scam Intent Analysis Tests...")
    test_scam_intent_analysis()
    print("\n>>> STEP 4 (Scam Intent Analysis) FULLY FUNCTIONAL AND VERIFIED! <<<")
