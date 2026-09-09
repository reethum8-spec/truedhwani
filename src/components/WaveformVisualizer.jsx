import React, { useEffect, useRef, useState } from 'react';
import { Radio, Activity, Volume2, Waves } from 'lucide-react';

export default function WaveformVisualizer({
  analyserNode,
  isActive = false,
  speechProb = 0.0,
  latencyMs = 0,
}) {
  const canvasRef = useRef(null);
  const [viewMode, setViewMode] = useState('oscilloscope'); // 'oscilloscope' | 'spectrum'
  const [rmsDb, setRmsDb] = useState(-60);
  const [peakFreq, setPeakFreq] = useState(0);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    const render = () => {
      animationFrameId = requestAnimationFrame(render);
      const width = canvas.width;
      const height = canvas.height;

      // Crisp laboratory background
      ctx.fillStyle = '#f8fafc';
      ctx.fillRect(0, 0, width, height);

      // Draw subtle architectural calibration grid
      ctx.strokeStyle = '#e2e8f0';
      ctx.lineWidth = 1;
      // Horizontal grid lines
      for (let y = height / 4; y < height; y += height / 4) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(width, y);
        ctx.stroke();
      }
      // Vertical grid lines
      for (let x = width / 8; x < width; x += width / 8) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
      }

      if (!analyserNode || !isActive) {
        // Flat baseline line
        ctx.strokeStyle = '#cbd5e1';
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(0, height / 2);
        ctx.lineTo(width, height / 2);
        ctx.stroke();
        return;
      }

      if (viewMode === 'oscilloscope') {
        const bufferLength = analyserNode.fftSize;
        const dataArray = new Uint8Array(bufferLength);
        analyserNode.getByteTimeDomainData(dataArray);

        // Calculate RMS
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          const val = (dataArray[i] - 128) / 128;
          sum += val * val;
        }
        const rms = Math.sqrt(sum / bufferLength);
        const db = Math.round(20 * Math.log10(Math.max(rms, 0.0001)));
        setRmsDb(db);

        // Draw waveform ink line (Prussian Blue & Copper)
        ctx.lineWidth = 2;
        ctx.strokeStyle = speechProb > 0.5 ? '#1d4ed8' : '#64748b';
        ctx.beginPath();

        const sliceWidth = width / bufferLength;
        let x = 0;

        for (let i = 0; i < bufferLength; i++) {
          const v = dataArray[i] / 128.0;
          const y = (v * height) / 2;

          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
          x += sliceWidth;
        }
        ctx.stroke();
      } else {
        // Spectrum Analyzer View
        const bufferLength = analyserNode.frequencyBinCount;
        const dataArray = new Uint8Array(bufferLength);
        analyserNode.getByteFrequencyData(dataArray);

        // Find peak frequency
        let maxVal = 0;
        let maxIdx = 0;
        for (let i = 0; i < bufferLength; i++) {
          if (dataArray[i] > maxVal) {
            maxVal = dataArray[i];
            maxIdx = i;
          }
        }
        const nyquist = analyserNode.context.sampleRate / 2;
        const peakHz = Math.round((maxIdx / bufferLength) * nyquist);
        setPeakFreq(peakHz);

        const barCount = 48;
        const barWidth = (width / barCount) - 2;
        const step = Math.floor(bufferLength / barCount);

        for (let i = 0; i < barCount; i++) {
          let sum = 0;
          for (let j = 0; j < step; j++) {
            sum += dataArray[i * step + j] || 0;
          }
          const avg = sum / step;
          const barHeight = (avg / 255) * (height - 8);

          const x = i * (barWidth + 2);
          const y = height - barHeight;

          // Complementary gradient: Prussian Blue into Burnished Copper in vocoder zone
          if (i > 34) {
            // High frequency vocoder critical zone
            ctx.fillStyle = avg > 130 ? '#d97706' : '#b45309';
          } else {
            ctx.fillStyle = '#1e40af';
          }
          ctx.fillRect(x, y, barWidth, barHeight);
        }
      }
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [analyserNode, isActive, viewMode, speechProb]);

  // Adjust canvas pixel density
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * window.devicePixelRatio;
    canvas.height = rect.height * window.devicePixelRatio;
    const ctx = canvas.getContext('2d');
    ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
  }, []);

  return (
    <div className="tactical-card rounded p-4 font-mono select-none">
      {/* Visualizer Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-blue-700" />
          <span className="text-xs font-bold text-slate-800 tracking-wider">
            RAW ACOUSTIC TELEMETRY // OSCILLOSCOPE
          </span>
          {isActive && (
            <span className="px-1.5 py-0.2 text-[10px] bg-blue-50 text-blue-800 border border-blue-200 rounded font-semibold">
              LIVE 16kS/s
            </span>
          )}
        </div>

        <div className="flex items-center gap-3 text-xs">
          {/* View mode toggle */}
          <div className="flex bg-slate-100 border border-slate-200 rounded p-0.5">
            <button
              onClick={() => setViewMode('oscilloscope')}
              className={`px-2 py-0.5 text-[10px] rounded transition-all ${
                viewMode === 'oscilloscope'
                  ? 'bg-white text-slate-900 font-bold shadow-xs'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              WAVEFORM
            </button>
            <button
              onClick={() => setViewMode('spectrum')}
              className={`px-2 py-0.5 text-[10px] rounded transition-all ${
                viewMode === 'spectrum'
                  ? 'bg-white text-slate-900 font-bold shadow-xs'
                  : 'text-slate-500 hover:text-slate-800'
              }`}
            >
              SPECTRUM
            </button>
          </div>

          <div className="text-[11px] text-slate-500">
            RMS: <span className="text-slate-800 font-bold">{rmsDb} dBFS</span>
          </div>
          {viewMode === 'spectrum' && (
            <div className="text-[11px] text-slate-500">
              PEAK: <span className="text-blue-800 font-bold">{peakFreq} Hz</span>
            </div>
          )}
        </div>
      </div>

      {/* Canvas Screen */}
      <div className="mt-3 relative h-28 w-full rounded border border-slate-200 overflow-hidden bg-slate-50 shadow-inner">
        <canvas
          ref={canvasRef}
          className="w-full h-full block"
          style={{ width: '100%', height: '100%' }}
        />

        {/* Center overlay when idle */}
        {!isActive && (
          <div className="absolute inset-0 flex items-center justify-center text-xs text-slate-400 bg-slate-50/80 backdrop-blur-[1px]">
            <span>SIGNAL INGESTION IDLE — ENGAGE INTERCEPT MIC OR PRESET</span>
          </div>
        )}
      </div>

      {/* Stage Progression Pipeline Status */}
      <div className="mt-3 pt-3 border-t border-slate-200 grid grid-cols-5 gap-2 text-[10px]">
        <div className={`p-1.5 rounded border ${isActive ? 'border-blue-300 bg-blue-50 text-blue-900' : 'border-slate-200 bg-slate-50 text-slate-500'}`}>
          <div className="font-bold">01 INGEST</div>
          <div className="text-[9px] opacity-80">{isActive ? '16kHz PCM' : 'Idle'}</div>
        </div>
        <div className={`p-1.5 rounded border ${speechProb > 0.5 ? 'border-emerald-300 bg-emerald-50 text-emerald-900' : 'border-slate-200 bg-slate-50 text-slate-500'}`}>
          <div className="font-bold">02 SILERO VAD</div>
          <div className="text-[9px] opacity-80">Prob: {(speechProb * 100).toFixed(0)}%</div>
        </div>
        <div className={`p-1.5 rounded border ${isActive ? 'border-blue-300 bg-blue-50 text-blue-900' : 'border-slate-200 bg-slate-50 text-slate-500'}`}>
          <div className="font-bold">03 BIOMARKERS</div>
          <div className="text-[9px] opacity-80">F0 / HNR / AASIST</div>
        </div>
        <div className={`p-1.5 rounded border ${isActive ? 'border-amber-300 bg-amber-50 text-amber-900' : 'border-slate-200 bg-slate-50 text-slate-500'}`}>
          <div className="font-bold">04 WHISPER+NLI</div>
          <div className="text-[9px] opacity-80">10-Intent Matrix</div>
        </div>
        <div className={`p-1.5 rounded border ${latencyMs > 0 ? 'border-emerald-300 bg-emerald-50 text-emerald-900' : 'border-slate-200 bg-slate-50 text-slate-500'}`}>
          <div className="font-bold">05 FUSION</div>
          <div className="text-[9px] opacity-80">{latencyMs ? `${latencyMs}ms` : 'Ready'}</div>
        </div>
      </div>
    </div>
  );
}
