import io
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from truedhwani.config import settings
from truedhwani.pipeline.stream_orchestrator import StreamPipelineOrchestrator
from truedhwani.server.websocket_handler import handle_websocket_stream
from truedhwani.audio.audio_utils import load_audio_file

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("truedhwani")

orchestrator: StreamPipelineOrchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Pre-warm models on startup to ensure sub-second inference on first incoming stream."""
    global orchestrator
    logger.info("Starting TrueDhwani Server - Initializing AI pipeline engines...")
    orchestrator = StreamPipelineOrchestrator()
    logger.info("All TrueDhwani models pre-warmed and ready.")
    yield
    logger.info("Shutting down TrueDhwani Server...")


app = FastAPI(
    title="TrueDhwani - Voice Stream Scam & Deepfake Detection Backend",
    version="1.0.0",
    description="Real-time enterprise cybersecurity pipeline for live voice stream analysis.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DIST_DIR = Path(__file__).resolve().parent.parent.parent / "dist"
if (DIST_DIR / "assets").exists():
    app.mount("/assets", StaticFiles(directory=str(DIST_DIR / "assets")), name="assets")

SAMPLE_AUDIO_DIR = Path(__file__).resolve().parent.parent.parent / "sample_audio"
if SAMPLE_AUDIO_DIR.exists():
    app.mount("/sample-audio", StaticFiles(directory=str(SAMPLE_AUDIO_DIR)), name="sample-audio")


@app.get("/api/presets")
async def get_presets():
    """List benchmark preset audio files for one-click testing."""
    return [
        {
            "id": "human",
            "name": "Genuine Human Conversation",
            "filename": "human_conversation.wav",
            "url": "/sample-audio/human_conversation.wav",
            "description": "Natural human conversation with zero synthetic artifacts and benign dialogue.",
            "expected": "Bonafide (DF < 0.10) · Legitimate Dialogue · Monitoring Posture",
        },
        {
            "id": "cloned",
            "name": "AI-Generated Cloned Voice",
            "filename": "cloned_synthetic_voice.wav",
            "url": "/sample-audio/cloned_synthetic_voice.wav",
            "description": "Neural synthetic voice clone speaking neutral text to verify acoustic anti-spoofing.",
            "expected": "Spoof (DF > 0.95) · Legitimate Dialogue · High Risk Anomaly",
        },
        {
            "id": "scam",
            "name": "Real OTP Scam Call",
            "filename": "otp_scam_call.wav",
            "url": "/sample-audio/otp_scam_call.wav",
            "description": "Coercive bank verification scam demanding urgent 6-digit mobile OTP code.",
            "expected": "Bank Verification Scams (100%) · High Risk / Warning Posture",
        },
    ]


SIMPLE_HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TrueDhwani - Voice Stream Scam & Deepfake Detection</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #07090e;
            --card-bg: #0e1422;
            --card-border: #1b253b;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.15);
            --text: #f1f5f9;
            --text-muted: #94a3b8;
            --green: #22c55e;
            --amber: #f59e0b;
            --red: #ef4444;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); padding: 24px 16px; line-height: 1.5; }
        .container { max-width: 1060px; margin: 0 auto; }
        
        header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid var(--card-border); }
        .brand { display: flex; align-items: center; gap: 12px; }
        .logo-badge { background: linear-gradient(135deg, #0284c7, #38bdf8); color: white; font-weight: 800; font-size: 16px; padding: 8px 12px; border-radius: 8px; letter-spacing: 0.5px; }
        .brand h1 { font-size: 20px; font-weight: 700; color: #fff; }
        .brand p { font-size: 13px; color: var(--text-muted); }
        .connection-badge { font-size: 12px; padding: 6px 12px; border-radius: 9999px; background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); color: var(--green); font-weight: 600; }
        .connection-badge.disconnected { background: rgba(239, 68, 68, 0.1); border-color: rgba(239, 68, 68, 0.3); color: var(--red); }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
        @media (max-width: 768px) { .grid-2 { grid-template-columns: 1fr; } }
        
        .card { background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 12px; padding: 20px; }
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .card-title { font-size: 15px; font-weight: 600; color: #fff; display: flex; align-items: center; gap: 8px; }
        
        .btn-row { display: flex; gap: 10px; align-items: center; margin-bottom: 16px; flex-wrap: wrap; }
        .btn { padding: 9px 18px; font-weight: 600; border-radius: 8px; border: none; cursor: pointer; font-size: 13px; display: inline-flex; align-items: center; gap: 6px; transition: all 0.2s; }
        .btn-start { background: #0284c7; color: white; }
        .btn-start:hover { background: #0369a1; }
        .btn-stop { background: #dc2626; color: white; }
        .btn-stop:hover { background: #b91c1c; }
        .btn-reset { background: #1e293b; color: #cbd5e1; border: 1px solid #334155; }
        .btn-reset:hover { background: #334155; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        
        .waveform-canvas { width: 100%; height: 54px; background: #070a12; border-radius: 6px; border: 1px solid var(--card-border); display: block; margin-bottom: 16px; }
        
        .alert-posture { padding: 14px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 13px; }
        .alert-posture.monitoring { background: rgba(34, 197, 94, 0.12); border: 1px solid var(--green); color: #86efac; }
        .alert-posture.warning { background: rgba(245, 158, 11, 0.12); border: 1px solid var(--amber); color: #fde68a; }
        .alert-posture.highrisk { background: rgba(239, 68, 68, 0.16); border: 1px solid var(--red); color: #fca5a5; }
        .posture-header { font-weight: 700; font-size: 14px; text-transform: uppercase; margin-bottom: 4px; display: flex; justify-content: space-between; }
        
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; margin-bottom: 16px; }
        .metric-box { background: #070a12; border: 1px solid var(--card-border); border-radius: 8px; padding: 12px; }
        .metric-lbl { font-size: 11px; text-transform: uppercase; font-weight: 700; color: var(--text-muted); margin-bottom: 4px; }
        .metric-val { font-size: 18px; font-weight: 700; color: var(--accent); }
        .metric-sub { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
        
        .transcript-container { background: #070a12; border: 1px solid var(--card-border); border-radius: 8px; padding: 14px; min-height: 120px; max-height: 200px; overflow-y: auto; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: #e2e8f0; line-height: 1.6; }
        .transcript-entry { margin-bottom: 6px; padding-bottom: 6px; border-bottom: 1px solid #131b2e; }
        .transcript-tag { font-size: 10px; padding: 2px 6px; border-radius: 4px; background: #1e293b; color: var(--accent); margin-right: 6px; }
        
        .chip-container { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
        .chip { font-size: 11px; padding: 3px 8px; border-radius: 4px; background: rgba(56, 189, 248, 0.1); border: 1px solid rgba(56, 189, 248, 0.25); color: var(--accent); }
        
        .preset-btn { width: 100%; text-align: left; padding: 12px; background: #070a12; border: 1px solid var(--card-border); border-radius: 8px; color: #f8fafc; cursor: pointer; margin-bottom: 8px; transition: all 0.2s; font-size: 13px; }
        .preset-btn:hover { border-color: var(--accent); background: #0f172a; }
        .preset-name { font-weight: 600; color: #fff; margin-bottom: 2px; }
        .preset-desc { font-size: 11px; color: var(--text-muted); }
        
        .dropzone { border: 2px dashed var(--card-border); border-radius: 8px; padding: 24px; text-align: center; cursor: pointer; background: #070a12; transition: all 0.2s; }
        .dropzone:hover { border-color: var(--accent); background: #0d1527; }
        .progress-bar { height: 6px; background: #1e293b; border-radius: 3px; overflow: hidden; margin-top: 6px; }
        .progress-fill { height: 100%; background: var(--accent); width: 0%; transition: width 0.3s; }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="brand">
                <div class="logo-badge">TRUE·DHWANI</div>
                <div>
                    <h1>TrueDhwani Cybersecurity Pipeline</h1>
                    <p>Live Real-Time Voice Stream Scam & Deepfake Detection</p>
                </div>
            </div>
            <div id="wsBadge" class="connection-badge disconnected">● Connecting...</div>
        </header>

        <div class="grid-2">
            <!-- Live Audio Streamer -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🎙️ Live Microphone Stream</span>
                    <span id="micStatus" style="font-size: 12px; color: var(--text-muted);">Ready</span>
                </div>

                <div class="btn-row">
                    <button id="startBtn" class="btn btn-start" onclick="startMic()">▶ Start Microphone</button>
                    <button id="stopBtn" class="btn btn-stop" onclick="stopMic()" disabled>⏹ Stop Microphone</button>
                    <button id="resetBtn" class="btn btn-reset" onclick="resetSession()">🔄 Reset Call</button>
                </div>

                <canvas id="waveform" class="waveform-canvas"></canvas>

                <div id="postureBox" class="alert-posture monitoring">
                    <div class="posture-header">
                        <span id="postureTitle">POSTURE: MONITORING</span>
                        <span id="postureRisk">0.0 / 100</span>
                    </div>
                    <div id="postureReason">Speech patterns and conversational intent remain within benign thresholds.</div>
                    <div id="postureAction" style="margin-top: 6px; font-size: 11px; opacity: 0.85;">Continue conversation normally. Background acoustic monitoring active.</div>
                </div>

                <div class="metrics-grid">
                    <div class="metric-box">
                        <div class="metric-lbl">AASIST Voice Cloning</div>
                        <div id="dfScore" class="metric-val">0.0%</div>
                        <div id="dfPred" class="metric-sub">Bonafide</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-lbl">Scam Intent Analysis</div>
                        <div id="intentScore" class="metric-val">0.0%</div>
                        <div id="intentLabel" class="metric-sub">Legitimate Dialogue</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-lbl">Silero Voice Activity</div>
                        <div id="vadScore" class="metric-val">0.0%</div>
                        <div id="vadStatus" class="metric-sub">Awaiting Speech</div>
                    </div>
                    <div class="metric-box">
                        <div class="metric-lbl">Language & Latency</div>
                        <div id="langMetric" class="metric-val">EN</div>
                        <div id="latencyMetric" class="metric-sub">0ms latency</div>
                    </div>
                </div>

                <div class="metric-lbl" style="margin-top: 14px;">Identified Scam Signals / Triggers</div>
                <div id="signalsContainer" class="chip-container">
                    <span class="chip" style="opacity: 0.6;">No suspicious indicators detected</span>
                </div>
            </div>

            <!-- Live Transcript & Benchmark -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📝 Real-Time Live Transcript</span>
                    <span id="callDuration" style="font-size: 12px; color: var(--text-muted);">Duration: 0.0s</span>
                </div>

                <div id="transcriptBox" class="transcript-container">
                    <div style="color: #64748b; font-style: italic;">Awaiting voice stream input...</div>
                </div>

                <div style="margin-top: 20px;">
                    <div class="card-title" style="margin-bottom: 12px;">⚡ Benchmark Presets</div>
                    <button class="preset-btn" onclick="runPreset('/sample-audio/human_conversation.wav', 'Human Conversation')">
                        <div class="preset-name">🟢 Genuine Human Conversation</div>
                        <div class="preset-desc">Benign natural speech (Bonafide, 0% Scam Intent)</div>
                    </button>
                    <button class="preset-btn" onclick="runPreset('/sample-audio/cloned_synthetic_voice.wav', 'Cloned Voice')">
                        <div class="preset-name">🔴 AI-Generated Cloned Voice</div>
                        <div class="preset-desc">Neural TTS voice clone (Spoof, High Risk Anomaly)</div>
                    </button>
                    <button class="preset-btn" onclick="runPreset('/sample-audio/otp_scam_call.wav', 'OTP Scam Call')">
                        <div class="preset-name">⚠️ State Bank OTP Scam Call</div>
                        <div class="preset-desc">Urgent debit card block & 6-digit OTP extortion</div>
                    </button>
                    <button class="preset-btn" onclick="runPreset('/sample-audio/kyc_scam_call.wav', 'KYC Customs Scam')">
                        <div class="preset-name">🚨 Customs & Aadhaar KYC Scam</div>
                        <div class="preset-desc">Customs illegal parcel threat & Aadhaar KYC coercion</div>
                    </button>
                </div>

                <div style="margin-top: 16px;">
                    <div class="card-title" style="margin-bottom: 8px;">📂 Audio File Analyzer</div>
                    <div class="dropzone" onclick="document.getElementById('fileInput').click()">
                        <input type="file" id="fileInput" accept="audio/*" style="display: none;" onchange="uploadAudioFile(this.files[0])">
                        <div style="font-size: 13px; font-weight: 600; color: #fff;">Click or Drag Audio File (.wav, .mp3, .flac)</div>
                        <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Performs full chunk-by-chunk session trace</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // High-precision stateful continuous audio resampler (guarantees exact 16kHz PCM with 0% sample drop)
        class AudioResampler {
            constructor(inputSampleRate, targetSampleRate = 16000) {
                this.inputSampleRate = inputSampleRate;
                this.targetSampleRate = targetSampleRate;
                this.ratio = inputSampleRate / targetSampleRate;
                this.lastSample = 0;
                this.fraction = 0;
            }

            resample(inputBuffer) {
                if (this.inputSampleRate === this.targetSampleRate) {
                    return inputBuffer;
                }
                const outputLength = Math.floor((inputBuffer.length - this.fraction) / this.ratio);
                const output = new Float32Array(outputLength);
                let inOffset = this.fraction;
                let outOffset = 0;

                while (outOffset < outputLength) {
                    const index = Math.floor(inOffset);
                    const nextIndex = index + 1;
                    const subSampleOffset = inOffset - index;

                    const s0 = index < 0 ? this.lastSample : inputBuffer[index];
                    const s1 = nextIndex < inputBuffer.length ? inputBuffer[nextIndex] : (inputBuffer[inputBuffer.length - 1] || 0);

                    output[outOffset++] = s0 + subSampleOffset * (s1 - s0);
                    inOffset += this.ratio;
                }

                this.fraction = inOffset - inputBuffer.length;
                this.lastSample = inputBuffer[inputBuffer.length - 1] || 0;
                return output;
            }
        }

        let ws = null, audioCtx = null, mediaStream = null, proc = null, resampler = null;
        let analyser = null, animFrame = null;
        const canvas = document.getElementById('waveform');
        const ctx = canvas.getContext('2d');

        function drawVisualizer() {
            if (!analyser) return;
            const bufferLength = analyser.frequencyBinCount;
            const dataArray = new Uint8Array(bufferLength);
            analyser.getByteTimeDomainData(dataArray);

            ctx.fillStyle = '#070a12';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.lineWidth = 2;
            ctx.strokeStyle = '#38bdf8';
            ctx.beginPath();

            const sliceWidth = canvas.width * 1.0 / bufferLength;
            let x = 0;
            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * (canvas.height / 2);
                if (i === 0) ctx.moveTo(x, y);
                else ctx.lineTo(x, y);
                x += sliceWidth;
            }
            ctx.lineTo(canvas.width, canvas.height / 2);
            ctx.stroke();

            animFrame = requestAnimationFrame(drawVisualizer);
        }

        function connectWS() {
            const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${proto}//${window.location.host}/ws/stream`);
            const badge = document.getElementById('wsBadge');
            
            ws.onopen = () => {
                badge.textContent = '● WebSocket Connected';
                badge.className = 'connection-badge';
            };
            ws.onclose = () => {
                badge.textContent = '● Disconnected (Retrying...)';
                badge.className = 'connection-badge disconnected';
                setTimeout(connectWS, 2000);
            };
            ws.onmessage = (e) => {
                const d = JSON.parse(e.data);
                handlePacket(d);
            };
        }

        function handlePacket(d) {
            if (!d.decision && !d.transcript) return;

            const risk = d.ema_smoothed_risk !== undefined ? d.ema_smoothed_risk : d.overall_risk_pct;
            document.getElementById('postureRisk').textContent = `${risk.toFixed(1)} / 100`;
            document.getElementById('postureTitle').textContent = `POSTURE: ${d.decision.toUpperCase()}`;
            document.getElementById('postureReason').textContent = d.reason || '';
            document.getElementById('postureAction').textContent = d.recommended_action || '';

            const pBox = document.getElementById('postureBox');
            pBox.className = 'alert-posture ' + (d.decision === 'High Risk' ? 'highrisk' : (d.decision === 'Warning' ? 'warning' : 'monitoring'));

            const dfScore = d.aasist_spoof_prob !== undefined ? d.aasist_spoof_prob : d.deepfake_score;
            document.getElementById('dfScore').textContent = `${((dfScore || 0)*100).toFixed(1)}%`;
            document.getElementById('dfPred').textContent = `${d.deepfake_prediction || 'Bonafide'}`;
            document.getElementById('dfPred').style.color = d.deepfake_prediction === 'Spoof' ? 'var(--red)' : 'var(--green)';

            const iScore = d.scam_intent_score !== undefined ? d.scam_intent_score : 0.0;
            document.getElementById('intentScore').textContent = `${(iScore*100).toFixed(1)}%`;
            document.getElementById('intentLabel').textContent = d.scam_intent_label || 'Legitimate Dialogue';

            const vad = d.silero_speech_prob !== undefined ? d.silero_speech_prob : 0.0;
            document.getElementById('vadScore').textContent = `${(vad*100).toFixed(1)}%`;
            document.getElementById('vadStatus').textContent = vad >= 0.5 ? 'Active Speech Detected' : 'Ambient / Silence';

            document.getElementById('langMetric').textContent = (d.language || 'en').toUpperCase();
            document.getElementById('latencyMetric').textContent = `${d.latency_ms || 0}ms latency`;
            document.getElementById('callDuration').textContent = `Duration: ${(d.call_duration_seconds || 0).toFixed(1)}s`;

            // Append transcript
            if (d.transcript && d.transcript.trim()) {
                const tBox = document.getElementById('transcriptBox');
                if (tBox.textContent.includes('Awaiting') || tBox.textContent.includes('Listening')) {
                    tBox.innerHTML = '';
                }
                const entry = document.createElement('div');
                entry.className = 'transcript-entry';
                entry.innerHTML = `<span class="transcript-tag">${(d.language || 'en').toUpperCase()} ${d.call_duration_seconds || 0}s</span> ${d.transcript}`;
                tBox.appendChild(entry);
                tBox.scrollTop = tBox.scrollHeight;
            }

            // Signals
            const signalsBox = document.getElementById('signalsContainer');
            if (d.distilbert_intent_probabilities || d.reason) {
                const signals = [];
                if (d.scam_intent_label && d.scam_intent_label !== 'Legitimate Dialogue') {
                    signals.push(`Category: ${d.scam_intent_label}`);
                }
                if (d.deepfake_prediction === 'Spoof') {
                    signals.push('AASIST: Voice Spoof Anomaly');
                }
                if (signals.length > 0) {
                    signalsBox.innerHTML = signals.map(s => `<span class="chip">${s}</span>`).join('');
                }
            }
        }

        async function startMic() {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                connectWS();
                await new Promise(r => setTimeout(r, 400));
            }
            try {
                mediaStream = await navigator.mediaDevices.getUserMedia({
                    audio: {
                        channelCount: 1,
                        echoCancellation: true,
                        noiseSuppression: false,
                        autoGainControl: true
                    }
                });

                audioCtx = new (window.AudioContext || window.webkitAudioContext)();
                resampler = new AudioResampler(audioCtx.sampleRate, 16000);

                const src = audioCtx.createMediaStreamSource(mediaStream);
                analyser = audioCtx.createAnalyser();
                analyser.fftSize = 256;
                src.connect(analyser);

                proc = audioCtx.createScriptProcessor(2048, 1, 1);
                proc.onaudioprocess = (e) => {
                    if (!ws || ws.readyState !== WebSocket.OPEN) return;
                    const inp = e.inputBuffer.getChannelData(0);
                    const resampled = resampler.resample(inp);
                    if (resampled.length === 0) return;

                    const buf = new ArrayBuffer(resampled.length * 2);
                    const view = new DataView(buf);
                    for (let i = 0; i < resampled.length; i++) {
                        let s = Math.max(-1, Math.min(1, resampled[i]));
                        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
                    }
                    ws.send(buf);
                };

                src.connect(proc);
                proc.connect(audioCtx.destination);

                canvas.width = canvas.clientWidth;
                canvas.height = canvas.clientHeight;
                drawVisualizer();

                document.getElementById('startBtn').disabled = true;
                document.getElementById('stopBtn').disabled = false;
                document.getElementById('micStatus').textContent = 'Microphone Active';
                document.getElementById('transcriptBox').innerHTML = '<div style="color: var(--accent);">Listening... Speak naturally into your microphone.</div>';
            } catch(e) {
                alert('Microphone initialization error: ' + e.message);
            }
        }

        function stopMic() {
            if (mediaStream) {
                mediaStream.getTracks().forEach(t => t.stop());
                mediaStream = null;
            }
            if (proc) { proc.disconnect(); proc = null; }
            if (audioCtx && audioCtx.state !== 'closed') { audioCtx.close(); audioCtx = null; }
            if (animFrame) { cancelAnimationFrame(animFrame); animFrame = null; }

            ctx.fillStyle = '#070a12';
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            document.getElementById('startBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('micStatus').textContent = 'Stopped';
        }

        function resetSession() {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ action: "reset" }));
            }
            document.getElementById('postureRisk').textContent = '0.0 / 100';
            document.getElementById('postureTitle').textContent = 'POSTURE: MONITORING';
            document.getElementById('postureReason').textContent = 'Session reset. Monitoring active.';
            document.getElementById('postureBox').className = 'alert-posture monitoring';
            document.getElementById('dfScore').textContent = '0.0%';
            document.getElementById('dfPred').textContent = 'Bonafide';
            document.getElementById('intentScore').textContent = '0.0%';
            document.getElementById('intentLabel').textContent = 'Legitimate Dialogue';
            document.getElementById('vadScore').textContent = '0.0%';
            document.getElementById('transcriptBox').innerHTML = '<div style="color: #64748b; font-style: italic;">Awaiting voice stream input...</div>';
            document.getElementById('signalsContainer').innerHTML = '<span class="chip" style="opacity: 0.6;">No suspicious indicators detected</span>';
        }

        async function runPreset(url, name) {
            stopMic();
            resetSession();
            document.getElementById('transcriptBox').innerHTML = `<div style="color: var(--accent);">Streaming preset benchmark: ${name}...</div>`;
            try {
                const res = await fetch(url);
                const blob = await res.blob();
                const file = new File([blob], name + '.wav', { type: 'audio/wav' });
                await uploadAudioFile(file);
            } catch(e) {
                alert('Preset load error: ' + e.message);
            }
        }

        async function uploadAudioFile(file) {
            if (!file) return;
            document.getElementById('transcriptBox').innerHTML = `<div style="color: var(--accent);">Analyzing audio file: ${file.name}...</div>`;
            const formData = new FormData();
            formData.append('file', file);
            try {
                const res = await fetch('/api/analyze-audio', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.stream_timeline && data.stream_timeline.length > 0) {
                    document.getElementById('transcriptBox').innerHTML = '';
                    for (const pkt of data.stream_timeline) {
                        handlePacket(pkt);
                        await new Promise(r => setTimeout(r, 60));
                    }
                }
            } catch(e) {
                alert('Analysis failed: ' + e.message);
            }
        }

        window.onload = () => {
            connectWS();
            canvas.width = canvas.clientWidth;
            canvas.height = canvas.clientHeight;
            ctx.fillStyle = '#070a12';
            ctx.fillRect(0, 0, canvas.width, canvas.height);
        };
    </script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
@app.get("/test", response_class=HTMLResponse)
@app.get("/simple", response_class=HTMLResponse)
async def index():
    """Serve the real-time AI testing dashboard."""
    return HTMLResponse(content=SIMPLE_HTML_PAGE)



@app.get("/api/health")
async def health():
    """Health check and model readiness status."""
    return {
        "status": "online",
        "service": "TrueDhwani AI Pipeline",
        "version": "1.0.0",
        "models": {
            "vad": "Silero VAD (snakers4/silero-vad)",
            "asr": f"Faster Whisper ({settings.asr.model_size})",
            "deepfake": "AASIST (ASVspoof 2019 LA)",
            "scam_intent": f"Transformer Zero-Shot NLI ({settings.scam_intent.model_name})",
        },
        "thresholds": {
            "monitoring": f"0 - {settings.decision.monitoring_max}",
            "warning": f"{settings.decision.monitoring_max + 1} - {settings.decision.warning_max}",
            "high_risk": f"> {settings.decision.warning_max}",
        }
    }


@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    """
    Live real-time bidirectional streaming endpoint.
    Accepts raw PCM 16-bit 16kHz audio chunks.
    Streams back real-time JSON packets with risk scores, decisions, and transcripts.
    """
    if orchestrator is None:
        await websocket.close(code=1011, reason="Orchestrator not initialized")
        return
    await handle_websocket_stream(websocket, orchestrator)


@app.post("/api/analyze-audio")
async def analyze_audio_file(file: UploadFile = File(...)):
    """
    Analyze an uploaded audio file (.wav, .mp3, .flac, etc.).
    Simulates real-time chunk-by-chunk streaming through the exact pipeline
    and returns a complete session trace and final risk assessment.
    """
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Pipeline orchestrator not ready")

    content = await file.read()
    try:
        audio, sr = load_audio_file(io.BytesIO(content), target_sr=16000)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to decode audio file: {e}")

    orchestrator.reset()
    duration_sec = len(audio) / sr

    # Stream through the buffer in 512-sample (32ms) frames
    packets = []
    frame_size = 512
    for i in range(0, len(audio), frame_size):
        frame = audio[i : i + frame_size]
        new_packets = await orchestrator.ingest_audio_chunk(frame)
        packets.extend([p.to_dict() for p in new_packets])

    # Flush tail
    last_packet = await orchestrator.flush()
    if last_packet:
        packets.append(last_packet.to_dict())

    # Compile session summary
    if packets:
        peak_risk = max(p["overall_risk"] for p in packets)
        latest_decision = packets[-1]["decision"]
        full_transcript = " ".join(p["transcript"] for p in packets if p["transcript"])
    else:
        peak_risk = 0.0
        latest_decision = "Monitoring"
        full_transcript = ""

    return {
        "filename": file.filename,
        "duration_seconds": round(duration_sec, 2),
        "total_emitted_chunks": len(packets),
        "peak_overall_risk": peak_risk,
        "final_decision": latest_decision,
        "consolidated_transcript": full_transcript,
        "stream_timeline": packets,
    }
