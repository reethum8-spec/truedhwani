import React from 'react';
import { Fingerprint, AlertTriangle, CheckCircle2, Cpu, HelpCircle } from 'lucide-react';

export default function BiomarkerPanel({
  deepfakeScore = 0.0,
  deepfakePrediction = 'Bonafide',
  aasistSpoofProb = 0.0,
  biomarkers = {},
}) {
  const isSpoof = deepfakeScore >= 0.65;
  const isWarning = deepfakeScore >= 0.35 && deepfakeScore < 0.65;

  // Extract biomarkers with safe fallbacks
  const pitchJitter = biomarkers.pitch_jitter_pct ?? 1.25;
  const hnr = biomarkers.hnr_db ?? 18.5;
  const flatness = biomarkers.spectral_flatness ?? 0.025;
  const vocoderScore = biomarkers.vocoder_artifact_score ?? 0.15;
  const breathScore = biomarkers.breath_naturalness_score ?? 0.85;
  const coarticulation = biomarkers.coarticulation_fluidity ?? 0.78;
  const biomarkerSpoof = biomarkers.biomarker_spoof_prob ?? 0.12;

  // Evaluation flags
  const jitterAnomaly = pitchJitter < 0.75;
  const vocoderAnomaly = vocoderScore > 0.45;
  const breathAnomaly = breathScore < 0.40;

  return (
    <div className="tactical-card rounded p-4 font-mono select-none">
      {/* Panel Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Fingerprint className="w-4 h-4 text-emerald-400" />
          <span className="text-xs font-semibold text-slate-200 tracking-wider">
            SEC // 02 · ACOUSTIC BIOMARKER MATRIX (BRANCH A)
          </span>
        </div>

        {/* Prediction Status Badge */}
        <div
          className={`flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-semibold border ${
            isSpoof
              ? 'bg-red-950/60 border-red-800 text-red-400'
              : isWarning
              ? 'bg-amber-950/60 border-amber-800 text-amber-400'
              : 'bg-emerald-950/60 border-emerald-800 text-emerald-400'
          }`}
        >
          {isSpoof ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>SYNTHETIC CLONE DETECTED</span>
            </>
          ) : isWarning ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5" />
              <span>ELEVATED ANOMALY</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>BONAFIDE HUMAN SPEECH</span>
            </>
          )}
        </div>
      </div>

      {/* Main Score & Ensemble Breakdown */}
      <div className="mt-3 grid grid-cols-2 gap-3">
        {/* Left: Combined Spoof Confidence */}
        <div className="tactical-well p-3 rounded">
          <div className="flex justify-between items-center text-[10px] text-slate-400">
            <span>CLONE PROBABILITY</span>
            <span className="text-slate-300">THRESHOLD: 0.65</span>
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span
              className={`text-2xl font-bold ${
                isSpoof
                  ? 'text-red-400'
                  : isWarning
                  ? 'text-amber-400'
                  : 'text-emerald-400'
              }`}
            >
              {(deepfakeScore * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-slate-500">
              [Raw: {deepfakeScore.toFixed(4)}]
            </span>
          </div>
          {/* Progress Bar */}
          <div className="mt-2 h-1.5 w-full bg-slate-800 rounded-full overflow-hidden relative">
            <div
              className={`h-full transition-all duration-300 ${
                isSpoof ? 'bg-red-500' : isWarning ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${Math.min(100, deepfakeScore * 100)}%` }}
            />
          </div>
        </div>

        {/* Right: AASIST vs Biomarker Split */}
        <div className="tactical-well p-3 rounded text-xs space-y-2">
          <div>
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>AASIST GRAPH SPECTRAL (55%)</span>
              <span className="text-slate-200">{(aasistSpoofProb * 100).toFixed(1)}%</span>
            </div>
            <div className="mt-1 h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-500"
                style={{ width: `${aasistSpoofProb * 100}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-[10px] text-slate-400">
              <span>PHYSICAL BIOMARKERS (45%)</span>
              <span className="text-slate-200">{(biomarkerSpoof * 100).toFixed(1)}%</span>
            </div>
            <div className="mt-1 h-1 bg-slate-800 rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-500"
                style={{ width: `${biomarkerSpoof * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Granular Physical Speaker Biomarker Gauges */}
      <div className="mt-3 pt-3 border-t border-slate-800/80">
        <div className="text-[10px] tracking-wider text-slate-400 font-semibold mb-2 flex items-center justify-between">
          <span>PHYSICAL ACOUSTIC CHARACTERISTICS</span>
          <span className="text-[9px] text-slate-500">CONTENT-INDEPENDENT METRICS</span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-[11px]">
          {/* Pitch Jitter */}
          <div className="p-2 rounded bg-[#090d14] border border-slate-800">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400">F0 PITCH JITTER</span>
              <span
                className={`font-semibold ${
                  jitterAnomaly ? 'text-amber-400' : 'text-emerald-400'
                }`}
              >
                {pitchJitter.toFixed(2)}%
              </span>
            </div>
            <div className="text-[9px] text-slate-500 mt-0.5">
              Normal: 1.0 - 2.5% {jitterAnomaly && '· Too Rigid/Vocoded'}
            </div>
          </div>

          {/* Harmonics to Noise Ratio */}
          <div className="p-2 rounded bg-[#090d14] border border-slate-800">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400">HARMONICS-TO-NOISE (HNR)</span>
              <span className="text-slate-200 font-semibold">
                {hnr.toFixed(1)} dB
              </span>
            </div>
            <div className="text-[9px] text-slate-500 mt-0.5">
              Target: 12 - 25 dB · Sub-band Harmonics
            </div>
          </div>

          {/* Vocoder Spectral Flatness */}
          <div className="p-2 rounded bg-[#090d14] border border-slate-800">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400">VOCODER HIGH-FREQ BALANCE</span>
              <span
                className={`font-semibold ${
                  vocoderAnomaly ? 'text-red-400' : 'text-slate-300'
                }`}
              >
                {(vocoderScore * 100).toFixed(0)}%
              </span>
            </div>
            <div className="text-[9px] text-slate-500 mt-0.5">
              Flatness: {flatness.toFixed(4)} {vocoderAnomaly && '· Neural Artifact'}
            </div>
          </div>

          {/* Breath & Micro-pause Naturalness */}
          <div className="p-2 rounded bg-[#090d14] border border-slate-800">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-400">BREATH & MICRO-PAUSES</span>
              <span
                className={`font-semibold ${
                  breathAnomaly ? 'text-amber-400' : 'text-emerald-400'
                }`}
              >
                {(breathScore * 100).toFixed(0)}%
              </span>
            </div>
            <div className="text-[9px] text-slate-500 mt-0.5">
              Continuous Flow: {coarticulation.toFixed(2)} Fluidity
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
