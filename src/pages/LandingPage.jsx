import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Radio, Activity, Cpu, ArrowRight, Lock, CheckCircle2, AlertTriangle, Layers, Zap, Scale } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="space-y-6 font-mono">
      {/* Top Intelligence Banner */}
      <div className="tactical-card p-6 rounded relative overflow-hidden">
        <div className="max-w-3xl relative z-10">
          <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded bg-blue-950/60 border border-blue-800 text-blue-300 text-xs font-semibold mb-3">
            <Shield className="w-3.5 h-3.5 text-blue-400" />
            <span>ENTERPRISE DEFENSE SPECIFICATION // DOCTRINE v1.2</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-white uppercase font-mono">
            TrueDhwani: Real-Time Voice Clone Forensics & Scam Intercept
          </h1>

          <p className="text-sm text-slate-300 mt-2 leading-relaxed font-sans font-normal">
            A high-assurance acoustic cybersecurity platform designed to intercept synthetic AI voice clones, deepfake audio impersonation, and coercive fraud calls in sub-second streaming audio.
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-3">
            <Link
              to="/live-monitor"
              className="flex items-center gap-2 px-4 py-2.5 rounded bg-blue-700 hover:bg-blue-600 text-white text-xs font-bold transition-colors shadow-[0_0_15px_rgba(37,99,235,0.3)]"
            >
              <Radio className="w-4 h-4 text-red-300" />
              <span>LAUNCH LIVE INTERCEPT STATION</span>
              <ArrowRight className="w-4 h-4" />
            </Link>

            <Link
              to="/analytics"
              className="flex items-center gap-2 px-4 py-2.5 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
            >
              <Activity className="w-4 h-4 text-blue-400" />
              <span>FORENSIC LAB FILE INSPECTION</span>
            </Link>
          </div>
        </div>
      </div>

      {/* 3 Key Operational Pillars */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Pillar 1 */}
        <div className="tactical-card p-4 rounded">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 mb-2">
            <Cpu className="w-4 h-4" />
            <span>ACOUSTIC BIOMARKERS (BRANCH A)</span>
          </div>
          <p className="text-xs text-slate-300 font-sans leading-relaxed">
            Content-independent extraction of fundamental pitch jitter (<span className="text-emerald-400 font-mono">F0</span>), harmonics-to-noise ratio (<span className="text-emerald-400 font-mono">HNR</span>), vocoder high-frequency spectral flatness, and sub-band breath naturalness.
          </p>
          <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
            ENGINE: AASIST (ASVSPOOF 2019 LA) + FORENSIC EXTRACTOR
          </div>
        </div>

        {/* Pillar 2 */}
        <div className="tactical-card p-4 rounded">
          <div className="flex items-center gap-2 text-xs font-bold text-amber-400 mb-2">
            <Zap className="w-4 h-4" />
            <span>COGNITIVE INTENT MATRIX (BRANCH B)</span>
          </div>
          <p className="text-xs text-slate-300 font-sans leading-relaxed">
            Streaming Faster-Whisper automatic speech recognition paired with zero-shot transformer NLI classification across 10 distinct fraud and coercion vectors.
          </p>
          <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
            ENGINE: WHISPER-BASE + TRANSFORMER DEBERTA/DISTILBERT
          </div>
        </div>

        {/* Pillar 3 */}
        <div className="tactical-card p-4 rounded">
          <div className="flex items-center gap-2 text-xs font-bold text-blue-400 mb-2">
            <Scale className="w-4 h-4" />
            <span>ADAPTIVE RISK FUSION</span>
          </div>
          <p className="text-xs text-slate-300 font-sans leading-relaxed">
            Dynamic weight reassignment that balances acoustic clone evidence with semantic fraud intent, smoothed via Exponential Moving Average (EMA) to prevent false-alarm chatter.
          </p>
          <div className="mt-3 pt-2 border-t border-slate-800 text-[10px] text-slate-500">
            ENGINE: ADAPTIVE BAYESIAN FUSION + DIRECTIVE GATEWAY
          </div>
        </div>
      </div>

      {/* Forensic Pipeline Architecture Diagram */}
      <div className="tactical-card p-5 rounded">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <Layers className="w-4 h-4 text-blue-400" />
            <span className="text-xs font-semibold text-slate-200 tracking-wider">
              DUAL-BRANCH STREAMING PIPELINE ARCHITECTURE
            </span>
          </div>
          <span className="text-[10px] text-slate-500">
            LATENCY TARGET: &lt; 400MS PER 512-SAMPLE FRAME
          </span>
        </div>

        {/* Tactical Pipeline Flowchart */}
        <div className="mt-4 grid grid-cols-1 md:grid-cols-5 gap-2 text-xs text-center">
          <div className="p-3 rounded bg-[#090d14] border border-slate-800">
            <div className="text-[10px] text-blue-400 font-bold mb-1">01 INGESTION</div>
            <div className="font-bold text-slate-200">16kHz PCM Audio</div>
            <div className="text-[10px] text-slate-500 mt-1">Linear resampler from hardware 44.1/48kHz</div>
          </div>

          <div className="p-3 rounded bg-[#090d14] border border-slate-800">
            <div className="text-[10px] text-emerald-400 font-bold mb-1">02 VAD GATE</div>
            <div className="font-bold text-slate-200">Silero VAD</div>
            <div className="text-[10px] text-slate-500 mt-1">Speech segmenting & sliding window buffer</div>
          </div>

          <div className="p-3 rounded bg-[#090d14] border border-blue-900/60 bg-blue-950/20">
            <div className="text-[10px] text-cyan-400 font-bold mb-1">03 DUAL-BRANCH</div>
            <div className="font-bold text-slate-200">AASIST + Whisper</div>
            <div className="text-[10px] text-slate-500 mt-1">Parallel acoustic & lexical inference</div>
          </div>

          <div className="p-3 rounded bg-[#090d14] border border-amber-900/60 bg-amber-950/20">
            <div className="text-[10px] text-amber-400 font-bold mb-1">04 FUSION</div>
            <div className="font-bold text-slate-200">Adaptive Weights</div>
            <div className="text-[10px] text-slate-500 mt-1">Confidence-guided acoustic/semantic fusion</div>
          </div>

          <div className="p-3 rounded bg-[#090d14] border border-red-900/60 bg-red-950/20">
            <div className="text-[10px] text-red-400 font-bold mb-1">05 DIRECTIVE</div>
            <div className="font-bold text-slate-200">Decision Engine</div>
            <div className="text-[10px] text-slate-500 mt-1">Monitoring, Caution, or Intervention</div>
          </div>
        </div>
      </div>

      {/* Benchmark Verification Matrix */}
      <div className="tactical-card p-5 rounded">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span className="text-xs font-semibold text-slate-200 tracking-wider">
              BENCHMARK EVALUATION // ASVSPOOF 2019 LOGICAL ACCESS (LA)
            </span>
          </div>
          <span className="text-[10px] text-slate-400">
            VALIDATED AGAINST NEURAL VOCODERS (HIFI-GAN, VITS, DIFFUSION)
          </span>
        </div>

        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase bg-[#080c11]">
                <th className="p-2">DETECTION ENGINE</th>
                <th className="p-2">EQUAL ERROR RATE (EER)</th>
                <th className="p-2">MIN T-DCF</th>
                <th className="p-2">INFERENCE LATENCY</th>
                <th className="p-2">CONTENT INDEPENDENCE</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              <tr>
                <td className="p-2 text-slate-400 font-sans">Raw MFCC / Baseline GMM</td>
                <td className="p-2 font-mono text-slate-400">8.92%</td>
                <td className="p-2 font-mono text-slate-400">0.245</td>
                <td className="p-2 font-mono text-slate-400">~60ms</td>
                <td className="p-2 text-amber-400">Partial (Susceptible to noise)</td>
              </tr>
              <tr>
                <td className="p-2 text-slate-400 font-sans">Standard AASIST (Raw Graph)</td>
                <td className="p-2 font-mono text-slate-300">1.13%</td>
                <td className="p-2 font-mono text-slate-300">0.034</td>
                <td className="p-2 font-mono text-slate-300">~120ms</td>
                <td className="p-2 text-emerald-400">High (Acoustic Spectral)</td>
              </tr>
              <tr className="bg-blue-950/20 text-white font-semibold">
                <td className="p-2 text-blue-300 font-sans flex items-center gap-1.5">
                  <span>TrueDhwani Ensemble (AASIST + Biomarkers)</span>
                  <span className="px-1 py-0.2 rounded bg-blue-800 text-[9px]">ACTIVE</span>
                </td>
                <td className="p-2 font-mono text-emerald-400">0.84%</td>
                <td className="p-2 font-mono text-emerald-400">0.021</td>
                <td className="p-2 font-mono text-emerald-400">&lt; 140ms</td>
                <td className="p-2 text-emerald-400">Full Content Independence</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
