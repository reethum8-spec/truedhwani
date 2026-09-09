import React from 'react';
import { ShieldAlert, ShieldCheck, AlertOctagon, Scale, Zap, Info } from 'lucide-react';

export default function DecisionPostureCard({
  overallRiskPct = 0.0,
  decision = 'Monitoring',
  reason = 'Normal conversation telemetry.',
  recommendedAction = 'Continue passive surveillance.',
  weights = {},
  durationSeconds = 0.0,
  latencyMs = 0,
}) {
  const isCritical = decision.toLowerCase().includes('high') || overallRiskPct > 65;
  const isWarning = decision.toLowerCase().includes('warn') || (overallRiskPct >= 35 && overallRiskPct <= 65);

  const dfWeight = (weights.w_deepfake ?? 0.5) * 100;
  const scamWeight = (weights.w_scam ?? 0.5) * 100;

  return (
    <div className="tactical-card rounded p-4 font-mono select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-200 tracking-wider">
            SEC // 04 · DECISION DIRECTIVE & FUSION ENGINE
          </span>
        </div>

        <div className="text-[10px] text-slate-400">
          DURATION: <span className="text-slate-200 font-semibold">{durationSeconds.toFixed(1)}s</span>
        </div>
      </div>

      {/* Main Posture Display */}
      <div className="mt-3 p-3 rounded tactical-well border border-slate-800 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-400 uppercase tracking-wide">
            SYSTEM COMPOSITE RISK
          </span>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span
              className={`text-3xl font-extrabold tracking-tight ${
                isCritical
                  ? 'text-red-400'
                  : isWarning
                  ? 'text-amber-400'
                  : 'text-emerald-400'
              }`}
            >
              {overallRiskPct.toFixed(1)}
            </span>
            <span className="text-xs text-slate-500 font-semibold">/ 100</span>
          </div>
        </div>

        {/* Tactical Directive Badge */}
        <div
          className={`px-3 py-2 rounded text-xs font-bold uppercase tracking-wider flex items-center gap-2 border ${
            isCritical
              ? 'bg-red-950/70 border-red-700 text-red-300 shadow-[0_0_15px_rgba(220,38,38,0.2)]'
              : isWarning
              ? 'bg-amber-950/70 border-amber-700 text-amber-300 shadow-[0_0_15px_rgba(217,119,6,0.15)]'
              : 'bg-emerald-950/70 border-emerald-700 text-emerald-300'
          }`}
        >
          {isCritical ? (
            <AlertOctagon className="w-4 h-4 text-red-400" />
          ) : isWarning ? (
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          ) : (
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
          )}
          <span>{decision ? decision.toUpperCase() : 'MONITORING'}</span>
        </div>
      </div>

      {/* Recommended Action Box */}
      <div className="mt-3 p-2.5 rounded bg-[#0b121b] border border-slate-800/80">
        <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-semibold mb-1">
          <Zap className="w-3.5 h-3.5 text-amber-400" />
          <span>ACTION DIRECTIVE</span>
        </div>
        <p className="text-xs text-slate-200 font-medium leading-snug">
          {recommendedAction || 'Continue passive surveillance.'}
        </p>
      </div>

      {/* Root Cause Reason */}
      <div className="mt-2 p-2.5 rounded bg-[#080d14] border border-slate-800/60">
        <div className="flex items-center gap-1.5 text-[10px] text-slate-400 font-semibold mb-1">
          <Info className="w-3.5 h-3.5 text-blue-400" />
          <span>FORENSIC ASSESSMENT RATIONALE</span>
        </div>
        <p className="text-[11px] text-slate-300 leading-normal">
          {reason || 'Acoustic metrics and linguistic intent indicate authentic dialogue.'}
        </p>
      </div>

      {/* Adaptive Fusion Weights Breakdown */}
      <div className="mt-3 pt-3 border-t border-slate-800/80 text-[10px]">
        <div className="flex justify-between text-slate-400 font-semibold mb-1">
          <span>DYNAMIC ADAPTIVE WEIGHTS</span>
          <span>
            LATENCY: <span className="text-emerald-400">{latencyMs}ms</span>
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-1">
          <div className="p-1.5 rounded bg-[#090d14] border border-slate-800">
            <div className="flex justify-between text-slate-400">
              <span>W_DEEPFAKE</span>
              <span className="text-slate-200 font-bold">{dfWeight.toFixed(0)}%</span>
            </div>
            <div className="mt-1 h-1 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-500" style={{ width: `${dfWeight}%` }} />
            </div>
          </div>
          <div className="p-1.5 rounded bg-[#090d14] border border-slate-800">
            <div className="flex justify-between text-slate-400">
              <span>W_SCAM_INTENT</span>
              <span className="text-slate-200 font-bold">{scamWeight.toFixed(0)}%</span>
            </div>
            <div className="mt-1 h-1 bg-slate-800 rounded-full overflow-hidden">
              <div className="h-full bg-amber-500" style={{ width: `${scamWeight}%` }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
