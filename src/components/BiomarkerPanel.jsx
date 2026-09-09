import React from 'react';
import { Fingerprint, AlertTriangle, CheckCircle2 } from 'lucide-react';

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
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Fingerprint className="w-4 h-4 text-emerald-700" />
          <span className="text-xs font-bold text-slate-800 tracking-wider">
            SEC // 02 · ACOUSTIC BIOMARKER MATRIX (BRANCH A)
          </span>
        </div>

        {/* Prediction Status Badge */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-bold border shadow-xs ${
            isSpoof
              ? 'bg-red-50 border-red-200 text-red-800'
              : isWarning
              ? 'bg-amber-50 border-amber-200 text-amber-800'
              : 'bg-emerald-50 border-emerald-200 text-emerald-800'
          }`}
        >
          {isSpoof ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-red-600" />
              <span>SYNTHETIC CLONE DETECTED</span>
            </>
          ) : isWarning ? (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
              <span>ELEVATED ANOMALY</span>
            </>
          ) : (
            <>
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              <span>BONAFIDE HUMAN SPEECH</span>
            </>
          )}
        </div>
      </div>

      {/* Main Score & Ensemble Breakdown */}
      <div className="mt-3 grid grid-cols-2 gap-3">
        {/* Left: Combined Spoof Confidence */}
        <div className="tactical-well p-3 rounded">
          <div className="flex justify-between items-center text-[10px] text-slate-500 font-semibold">
            <span>CLONE PROBABILITY</span>
            <span className="text-slate-600">THRESHOLD: 0.65</span>
          </div>
          <div className="mt-1 flex items-baseline gap-2">
            <span
              className={`text-2xl font-extrabold ${
                isSpoof
                  ? 'text-red-700'
                  : isWarning
                  ? 'text-amber-700'
                  : 'text-emerald-700'
              }`}
            >
              {(deepfakeScore * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-slate-500 font-medium">
              [Raw: {deepfakeScore.toFixed(4)}]
            </span>
          </div>
          {/* Progress Bar */}
          <div className="mt-2 h-2 w-full bg-slate-200 rounded-full overflow-hidden relative">
            <div
              className={`h-full transition-all duration-300 ${
                isSpoof ? 'bg-red-600' : isWarning ? 'bg-amber-500' : 'bg-emerald-600'
              }`}
              style={{ width: `${Math.min(100, deepfakeScore * 100)}%` }}
            />
          </div>
        </div>

        {/* Right: AASIST vs Biomarker Split */}
        <div className="tactical-well p-3 rounded text-xs space-y-2.5">
          <div>
            <div className="flex justify-between text-[10px] text-slate-600 font-semibold">
              <span>AASIST GRAPH SPECTRAL (55%)</span>
              <span className="text-slate-900 font-bold">{(aasistSpoofProb * 100).toFixed(1)}%</span>
            </div>
            <div className="mt-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-700"
                style={{ width: `${aasistSpoofProb * 100}%` }}
              />
            </div>
          </div>
          <div>
            <div className="flex justify-between text-[10px] text-slate-600 font-semibold">
              <span>PHYSICAL BIOMARKERS (45%)</span>
              <span className="text-slate-900 font-bold">{(biomarkerSpoof * 100).toFixed(1)}%</span>
            </div>
            <div className="mt-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div
                className="h-full bg-amber-600"
                style={{ width: `${biomarkerSpoof * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Granular Physical Speaker Biomarker Gauges */}
      <div className="mt-3 pt-3 border-t border-slate-200">
        <div className="text-[10px] tracking-wider text-slate-600 font-bold mb-2 flex items-center justify-between">
          <span>PHYSICAL ACOUSTIC CHARACTERISTICS</span>
          <span className="text-[9px] text-slate-500">CONTENT-INDEPENDENT METRICS</span>
        </div>

        <div className="grid grid-cols-2 gap-2 text-[11px]">
          {/* Pitch Jitter */}
          <div className="p-2 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-600 font-medium">F0 PITCH JITTER</span>
              <span
                className={`font-bold ${
                  jitterAnomaly ? 'text-amber-700' : 'text-emerald-700'
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
          <div className="p-2 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-600 font-medium">HARMONICS-TO-NOISE (HNR)</span>
              <span className="text-slate-900 font-bold">
                {hnr.toFixed(1)} dB
              </span>
            </div>
            <div className="text-[9px] text-slate-500 mt-0.5">
              Target: 12 - 25 dB · Sub-band Harmonics
            </div>
          </div>

          {/* Vocoder Spectral Flatness */}
          <div className="p-2 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-600 font-medium">VOCODER HIGH-FREQ BALANCE</span>
              <span
                className={`font-bold ${
                  vocoderAnomaly ? 'text-red-700' : 'text-slate-800'
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
          <div className="p-2 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between items-center text-[10px]">
              <span className="text-slate-600 font-medium">BREATH & MICRO-PAUSES</span>
              <span
                className={`font-bold ${
                  breathAnomaly ? 'text-amber-700' : 'text-emerald-700'
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
