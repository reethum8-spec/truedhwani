"""
Scam categories, hypotheses, indicators, and explanations for TrueDhwani.
"""

from dataclasses import dataclass, field


@dataclass
class ScamCategory:
    id: str
    label: str
    description: str
    hypothesis: str
    severity_weight: float  # Multiplier for raw risk impact
    keywords_and_phrases: list[str] = field(default_factory=list)


SCAM_CATEGORIES: dict[str, ScamCategory] = {
    "otp_scam": ScamCategory(
        id="otp_scam",
        label="OTP Scams",
        description="Soliciting one-time passwords, verification codes, or SMS pins to compromise accounts.",
        hypothesis="soliciting a one-time password (OTP), security PIN, or authentication code sent to the victim's phone",
        severity_weight=1.0,
        keywords_and_phrases=[
            "otp", "one time password", "verification code", "6 digit code", "6-digit code", "share the code",
            "sms code", "pin number", "read the digits", "forward the message", "security code", "cvv",
            "authentication code", "enter pin", "tell me the otp", "share otp"
        ]
    ),
    "bank_verification": ScamCategory(
        id="bank_verification",
        label="Bank Verification Scams",
        description="Fraudulent alerts regarding bank account suspension, expired cards, or fake security alerts.",
        hypothesis="fraudulent bank verification claiming an account or debit/credit card is blocked, suspended, or expiring",
        severity_weight=0.95,
        keywords_and_phrases=[
            "bank verification", "account blocked", "card suspended", "cvv", "expiry date",
            "state bank", "sbi", "hdfc", "icici", "axis bank", "rbi alert", "unauthorized transaction",
            "card renewal", "debit card blocked", "credit card limit", "net banking locked",
            "account suspended", "security department"
        ]
    ),
    "kyc_scam": ScamCategory(
        id="kyc_scam",
        label="KYC Scams",
        description="Coercive requests to update Aadhaar, PAN, or SIM KYC immediately under threat of service termination.",
        hypothesis="demanding immediate KYC document update, Aadhaar link, or PAN card submission to avoid deactivation",
        severity_weight=0.90,
        keywords_and_phrases=[
            "kyc", "aadhaar", "pan card", "kyc update", "sim block", "document verification",
            "deactivation notice", "link aadhaar", "update kyc immediately", "sim card will be blocked",
            "ekyc", "biometric kyc", "telecom department", "trai"
        ]
    ),
    "identity_impersonation": ScamCategory(
        id="identity_impersonation",
        label="Identity Impersonation",
        description="Impersonating law enforcement, police, customs, CBI, tax department, or senior bank officials.",
        hypothesis="impersonating police officers, customs officials, CBI, government agencies, or law enforcement",
        severity_weight=0.95,
        keywords_and_phrases=[
            "police officer", "customs department", "cbi officer", "crime branch", "arrest warrant",
            "trai", "supreme court", "telecom department", "narcotics bureau", "illegal parcel",
            "digital arrest", "customs mumbai", "fedex parcel", "passport seized", "inspector",
            "cyber crime cell", "enforcement directorate"
        ]
    ),
    "remote_access": ScamCategory(
        id="remote_access",
        label="Remote Access Scams",
        description="Instructing victims to download remote desktop applications like AnyDesk, TeamViewer, or QuickSupport.",
        hypothesis="instructing the victim to install remote desktop access software like AnyDesk, TeamViewer, or QuickSupport",
        severity_weight=1.0,
        keywords_and_phrases=[
            "anydesk", "teamviewer", "quicksupport", "rustdesk", "screen share", "remote access",
            "download application", "apk file", "grant permission", "install app", "download apk",
            "share screen", "allow remote", "9 digit code"
        ]
    ),
    "payment_request": ScamCategory(
        id="payment_request",
        label="Payment Requests",
        description="Demanding UPI transfers, QR code scanning, or direct funds transfer under pretext.",
        hypothesis="requesting immediate money transfer, UPI payment, or scanning a QR code to receive funds",
        severity_weight=0.85,
        keywords_and_phrases=[
            "upi transfer", "send money", "scan qr code", "google pay", "gpay", "phonepe", "paytm",
            "processing fee", "refundable deposit", "transfer amount", "pay now", "enter upi pin",
            "scan code to receive", "request money", "send 5000", "send 1000", "send amount"
        ]
    ),
    "social_engineering": ScamCategory(
        id="social_engineering",
        label="Social Engineering",
        description="Manipulating emotional states through fake lotteries, distress claims, or counterfeit refunds.",
        hypothesis="social engineering manipulation via fake lottery prizes, relative in distress, or counterfeit refunds",
        severity_weight=0.80,
        keywords_and_phrases=[
            "lottery winner", "congratulations", "cash prize", "accident emergency", "hospital bill",
            "relative in trouble", "refund processed", "exclusive reward", "won 25 lakh", "kbc lottery",
            "emergency fund", "customs fee"
        ]
    ),
    "gift_card": ScamCategory(
        id="gift_card",
        label="Gift Card Scams",
        description="Coercing victim to purchase Apple, Google Play, or Amazon gift cards to settle penalties.",
        hypothesis="demanding payment or penalty settlement via retail gift cards like Apple, Google Play, or Amazon cards",
        severity_weight=0.90,
        keywords_and_phrases=[
            "gift card", "apple card", "google play voucher", "amazon gift card", "scratch card",
            "read back the code", "buy vouchers", "apple gift card", "redeem code"
        ]
    ),
    "investment_scam": ScamCategory(
        id="investment_scam",
        label="Investment Scams",
        description="Promising guaranteed abnormal returns, crypto schemes, or Telegram task scams.",
        hypothesis="fraudulent investment offering guaranteed high returns, crypto schemes, or part-time task earnings",
        severity_weight=0.85,
        keywords_and_phrases=[
            "guaranteed return", "double your money", "crypto investment", "telegram task",
            "daily profit", "part time job", "youtube like task", "deposit profit", "high return",
            "passive income", "trading group"
        ]
    ),
    "threat_urgency": ScamCategory(
        id="threat_urgency",
        label="Threat/Urgency Manipulation",
        description="Creating severe artificial urgency, threats of immediate arrest, prosecution, or financial ruin.",
        hypothesis="creating intense urgency, psychological pressure, threats of immediate arrest, or legal prosecution",
        severity_weight=0.90,
        keywords_and_phrases=[
            "immediate action", "within 10 minutes", "arrest warrant", "legal action", "do not disconnect",
            "court summons", "police will arrive", "jail", "urgent matter", "last warning",
            "power cut tonight", "electricity disconnected", "penalty will be charged", "strictly confidential"
        ]
    ),
    "legitimate_dialogue": ScamCategory(
        id="legitimate_dialogue",
        label="Legitimate Dialogue",
        description="Normal, benign conversation without malicious intent or financial demands.",
        hypothesis="a completely normal, benign, and legitimate phone conversation",
        severity_weight=0.0,
        keywords_and_phrases=[
            "hello", "how are you", "good morning", "see you later", "meeting tomorrow",
            "weather", "lunch", "family", "project update", "grocery", "office", "dinner"
        ]
    ),
}
