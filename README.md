# TrueDhwani: Real-Time Enterprise Voice Stream Scam & Deepfake Detection Backend

TrueDhwani is a real-time cybersecurity pipeline designed to ingest live voice streams (microphone, VoIP, or uploaded recordings) and continuously estimate scam probability and biometric deepfake manipulation during an active conversation.

---

## System Architecture

```
Incoming Microphone / Audio Stream (PCM 16kHz Mono)
       │
       ▼
Voice Activity Detection (Silero VAD - 32ms frames)
       │
       ▼
Sliding Speech Buffer (2.0 – 3.5s speech chunks)
       │
       ├──► Branch A: Deepfake Detection (Pretrained AASIST / ASVspoof 2019 LA)
       │
       └──► Branch B: Speech Recognition (Faster Whisper Multilingual)
                 │
                 ▼
            Scam Intent Analysis (Transformer Zero-Shot NLI)
                 │
                 ▼
       Adaptive Risk Fusion Engine (Dynamic Weighting: Deepfake early -> Intent late)
                 │
                 ▼
       Temporal Smoothing (Asymmetric Exponential Moving Average)
                 │
                 ▼
       Decision Engine (0-40: Monitoring | 41-70: Warning | 71-100: High Risk)
                 │
                 ▼
       Real-Time WebSocket JSON Stream Output
```

---

## Operational Modules

1. **Module 1: Voice Activity Detection (Silero VAD)**
   - Continuous frame-by-frame (512 samples / 32ms at 16kHz) analysis.
   - Filters silence, background noise, and non-vocal acoustic artifacts.
   - Accumulates speech into continuous 2.0–3.5s speech segments with sliding overlap.

2. **Module 2: Speech Recognition (Faster Whisper)**
   - CTranslate2 INT8 quantized execution for sub-second transcription.
   - Automatic language detection (including Indian languages: Hindi, Tamil, Telugu, etc.).
   - Automatic English translation for downstream NLP when non-English is spoken.

3. **Module 3: Deepfake Detection (AASIST)**
   - Full PyTorch implementation of the **AASIST** graph-attention neural architecture.
   - Loaded with official weights pretrained on the **ASVspoof 2019 LA** benchmark.
   - Operates on raw 16kHz waveform chunks, returning spoof probabilities in ~290ms.

4. **Module 4: Scam Intent Analysis**
   - Zero-shot Natural Language Inference (NLI) transformer.
   - Evaluates 10 target categories:
     - OTP Scams
     - Bank Verification Scams
     - KYC Scams
     - Identity Impersonation
     - Remote Access Scams
     - Payment Requests
     - Social Engineering
     - Gift Card Scams
     - Investment Scams
     - Threat / Urgency Manipulation
   - Combines semantic hypothesis testing with lexical authority markers to generate human-readable explanations.

5. **Module 5: Adaptive Risk Fusion**
   - **Dynamic Weighting**:
     - Early in the call ($t \le 12s$): Deepfake detection carries high weight ($W_{df} \approx 0.70-0.75$, $W_{intent} \approx 0.25-0.30$) because voice cloning is an immediate biometric tell.
     - Mature conversation ($t \ge 35s$): Scam intent carries high weight ($W_{intent} \approx 0.75-0.80$, $W_{df} \approx 0.20-0.25$) as conversational demands unfold.
   - **Confidence Modulation**: Each component's weight is modulated by the model's confidence.
   - **Synergy Multiplier**: When both biometric spoofing and scam intent are elevated, applies non-linear cross-term boost.

6. **Module 6: Temporal Smoothing**
   - Asymmetric Exponential Moving Average (EMA).
   - Fast-rise ($\alpha_{rise} = 0.40$) for rapid detection of imminent fraud.
   - Slow-decay ($\alpha_{fall} = 0.20$) to maintain alertness during pauses.
   - Prevents isolated anomalous words from triggering sudden false positive alarms.

7. **Module 7: Decision Engine**
   - **0–40**: **Monitoring** (Normal benign dialogue, continue conversation).
   - **41–70**: **Warning** (Exercise caution, do not disclose sensitive details).
   - **71–100**: **High Risk** (Terminate call immediately, cyber scam / voice cloning alert).

---

## Quick Start

### 1. Activate Environment
```powershell
.\venv\Scripts\Activate.ps1
$env:PYTHONPATH = (Get-Location).Path
```

### 2. Run Automated Verification Tests
Each module has been verified incrementally:
```powershell
# Module 1: Silero VAD & Sliding Speech Buffer
.\venv\Scripts\python.exe tests/test_vad.py

# Module 2: Faster Whisper Speech Recognition
.\venv\Scripts\python.exe tests/test_asr.py

# Module 3: AASIST Pretrained Deepfake Detection
.\venv\Scripts\python.exe tests/test_deepfake.py

# Module 4: Transformer Scam Intent Analysis
.\venv\Scripts\python.exe tests/test_scam_intent.py

# Modules 5 & 6: Adaptive Fusion & Temporal Smoothing
.\venv\Scripts\python.exe tests/test_fusion.py

# Complete End-to-End Pipeline
.\venv\Scripts\python.exe tests/test_pipeline.py

# WebSocket & REST API Integration
.\venv\Scripts\python.exe tests/test_websocket.py
```

### 3. Launch FastAPI Server
```powershell
.\venv\Scripts\python.exe -m uvicorn truedhwani.server.app:app --host 0.0.0.0 --port 8000
```
- API Health Check: `http://localhost:8000/api/health`
- WebSocket Stream: `ws://localhost:8000/ws/stream`
- File Upload Endpoint: `POST http://localhost:8000/api/analyze-audio`

### 4. Stream Live Audio
#### Live Microphone Streaming
```powershell
.\venv\Scripts\python.exe truedhwani/client/mic_streamer.py
```
#### Audio File VoIP Call Simulation
```powershell
.\venv\Scripts\python.exe truedhwani/client/file_streamer.py sample_audio/otp_scam_call.wav
```

---

## WebSocket JSON Output Format

```json
{
  "transcript": "Please share the 6-digit OTP code immediately to unblock your account.",
  "language": "en",
  "deepfake_score": 0.98,
  "scam_intent_score": 0.89,
  "overall_risk": 0.98,
  "decision": "High Risk",
  "reason": "Synthetic / cloned voice detected (confidence: 98%) combined with elevated OTP Scams demands.",
  "recommended_action": "TERMINATE CALL IMMEDIATELY. High probability of fraudulent cyber scam or biometric spoofing. Do NOT transfer funds or grant remote access under any circumstance.",
  "latency_ms": 1850,
  "call_duration_seconds": 16.3,
  "weights": {
    "deepfake": 0.61,
    "scam_intent": 0.39
  }
}
```
