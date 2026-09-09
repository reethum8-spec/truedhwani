# TrueDhwani: Real-Time Enterprise Voice Stream Scam & Deepfake Detection Platform

TrueDhwani is a real-time voice cybersecurity and counter-fraud intelligence platform designed to ingest live voice streams (microphone, VoIP, or uploaded recordings), extract content-independent acoustic anti-spoofing biomarkers, transcribe speech in multiple languages, classify fraudulent intent, and render live telemetry via a defense-grade forensic workstation interface.

---

## Key Features

- **Content-Independent Acoustic Biomarkers**: Cycle-to-cycle F0 pitch jitter, Harmonics-to-Noise Ratio (HNR in dB), vocoder high-frequency spectral flatness, and sub-band breath turbulence.
- **ASVspoof 2019 LA AASIST Engine**: Raw waveform graph spectral attention network detecting neural vocoders (HiFi-GAN, VITS, Diffusion, ElevenLabs) independent of keywords or language.
- **Multilingual Speech Recognition**: Faster-Whisper Base with CTranslate2 INT8 quantization and automatic English translation for Indian and regional languages.
- **10-Category Cognitive Intent Radar**: Zero-shot transformer NLI assessing financial coercion, OTP theft, impersonation, and urgency manipulation.
- **Adaptive Risk Fusion & Temporal Smoothing**: Dynamic confidence-guided weight balance ($W_{df} \leftrightarrow W_{intent}$) with asymmetric Exponential Moving Average.
- **Defense Forensics Workstation UI**: Real-time oscilloscope, 32-band FFT spectrum analyzer, live ASR transcript stream, biomarker matrix gauges, and exportable session audit ledgers (JSON/CSV).

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
       ├──► Branch A: Deepfake Detection Ensemble
       │       ├── AASIST Graph Spectral Network (Pretrained ASVspoof 2019 LA)
       │       └── Physical Acoustic Biomarkers (F0 Jitter, HNR dB, Vocoder Flatness)
       │
       └──► Branch B: Multilingual Speech Recognition (Faster Whisper)
                 │
                 ▼
            Scam Intent Analysis (Transformer Zero-Shot NLI - 10 Fraud Vectors)
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
       Bidirectional WebSocket JSON Stream & Forensic Workstation UI
```

---

## Forensic Workstation Interface

The TrueDhwani frontend is designed as an investigative signals intelligence workstation:
- **Live Intercept Station (`/live-monitor`)**: Live microphone intercept or 1-click benchmark test suite (Genuine Human, Cloned AI Voice, Real OTP Scam) with real-time audio playback through speakers, live waveform oscilloscope, biomarker matrix, and turn-by-turn transcript ledger.
- **Forensic Lab (`/analytics`)**: Full-file offline inspection (.wav, .mp3, .flac, .ogg, .m4a) with interactive temporal threat scrubber and incident dossier export.
- **System Briefing (`/`)**: Operational doctrine, dual-branch architecture flowcharts, and ASVspoof LA benchmark comparisons.

---

## Quick Start

### 1. Launch Backend Server & Forensic UI
The FastAPI backend serves both the API endpoints and the pre-built React/Vite forensic frontend:

```powershell
# Activate Python virtual environment
.\venv\Scripts\activate

# Start server
python -m uvicorn truedhwani.server.app:app --host 127.0.0.1 --port 8000
```

Open your browser to:
- **Live Intercept Station**: [http://localhost:8000/live-monitor](http://localhost:8000/live-monitor)
- **Forensic Lab**: [http://localhost:8000/analytics](http://localhost:8000/analytics)
- **System Briefing**: [http://localhost:8000/](http://localhost:8000/)

### 2. Frontend Development (Hot-Reloading)
To modify or develop frontend components with instant hot reload:
```powershell
cmd.exe /c "npm run dev"
```
Runs at [http://localhost:5173/](http://localhost:5173/) (automatically proxies `/api` and `/ws` to port 8000).

To create a production build:
```powershell
cmd.exe /c "npm run build"
```

---

## Automated Verification Tests

Run the complete 18-test pytest verification suite:
```powershell
.\venv\Scripts\python.exe -m pytest tests/
```

Individual test modules:
- `tests/test_vad.py`: Silero VAD energy gating & sliding speech buffer
- `tests/test_asr.py`: Faster-Whisper transcription & language identification
- `tests/test_deepfake.py`: AASIST model inference & Forensic Biomarker extraction
- `tests/test_scam_intent.py`: 10-class transformer zero-shot NLI
- `tests/test_fusion.py`: Adaptive risk fusion & temporal smoothing
- `tests/test_pipeline.py`: End-to-end pipeline verification on real audio samples
- `tests/test_websocket.py`: WebSocket binary PCM streaming & REST upload endpoint

---

## WebSocket JSON Output Format

```json
{
  "transcript": "Please share the 6-digit OTP code immediately to unblock your account.",
  "language": "en",
  "deepfake_score": 0.78,
  "aasist_spoof_prob": 0.81,
  "biomarkers": {
    "pitch_jitter_pct": 21.37,
    "hnr_db": -0.2,
    "spectral_flatness": 0.082,
    "vocoder_artifact_score": 0.65,
    "breath_naturalness_score": 0.32,
    "coarticulation_fluidity": 0.45,
    "biomarker_spoof_prob": 0.74
  },
  "scam_intent_score": 0.89,
  "scam_intent_label": "Bank Verification Scams",
  "overall_risk": 0.84,
  "overall_risk_pct": 84.0,
  "decision": "High Risk",
  "reason": "Synthetic voice clone detected combined with high-coercion bank verification scam.",
  "recommended_action": "TERMINATE CALL IMMEDIATELY. Imminent credential theft risk.",
  "latency_ms": 280,
  "call_duration_seconds": 6.4,
  "weights": {
    "deepfake": 0.55,
    "scam_intent": 0.45
  }
}
```

---

## Repository
GitHub: [https://github.com/reethum8-spec/truedhwani](https://github.com/reethum8-spec/truedhwani)
