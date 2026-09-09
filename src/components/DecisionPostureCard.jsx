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
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Scale className="w-4 h-4 text-blue-700" />
          <span className="text-xs font-bold text-slate-800 tracking-wider">
            SEC // 04 · DECISION DIRECTIVE & FUSION ENGINE
          </span>
        </div>

        <div className="text-[10px] text-slate-500 font-medium">
          DURATION: <span className="text-slate-900 font-bold">{durationSeconds.toFixed(1)}s</span>
        </div>
      </div>

      {/* Main Posture Display */}
      <div className="mt-3 p-3 rounded tactical-well border border-slate-200 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-500 uppercase font-bold tracking-wide">
            SYSTEM COMPOSITE RISK
          </span>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span
              className={`text-3xl font-black tracking-tight ${
                isCritical
                  ? 'text-red-700'
                  : isWarning
                  ? 'text-amber-700'
                  : 'text-emerald-700'
              }`}
            >
              {overallRiskPct.toFixed(1)}
            </span>
            <span className="text-xs text-slate-500 font-bold">/ 100</span>
          </div>
        </div>

        {/* Tactical Directive Badge */}
        <div
          className={`px-3 py-2 rounded text-xs font-extrabold uppercase tracking-wider flex items-center gap-2 border shadow-xs ${
            isCritical
              ? 'bg-red-50 border-red-300 text-red-800'
              : isWarning
              ? 'bg-amber-50 border-amber-300 text-amber-800'
              : 'bg-emerald-50 border-emerald-300 text-emerald-800'
          }`}
        >
          {isCritical ? (
            <AlertOctagon className="w-4 h-4 text-red-600" />
          ) : isWarning ? (
            <ShieldAlert className="w-4 h-4 text-amber-600" />
          ) : (
            <ShieldCheck className="w-4 h-4 text-emerald-600" />
          )}
          <span>{decision ? decision.toUpperCase() : 'MONITORING'}</span>
        </div>
      </div>

      {/* Recommended Action Box */}
      <div className="mt-3 p-2.5 rounded bg-amber-50/60 border border-amber-200/80">
        <div className="flex items-center gap-1.5 text-[10px] text-amber-800 font-bold mb-1">
          <Zap className="w-3.5 h-3.5 text-amber-600" />
          <span>ACTION DIRECTIVE</span>
        </div>
        <p className="text-xs text-slate-900 font-semibold leading-snug">
          {recommendedAction || 'Continue passive surveillance.'}
        </p>
      </div>

      {/* Root Cause Reason */}
      <div className="mt-2 p-2.5 rounded bg-slate-50 border border-slate-200">
        <div className="flex items-center gap-1.5 text-[10px] text-slate-600 font-bold mb-1">
          <Info className="w-3.5 h-3.5 text-blue-700" />
          <span>FORENSIC ASSESSMENT RATIONALE</span>
        </div>
        <p className="text-[11px] text-slate-700 leading-normal">
          {reason || 'Acoustic metrics and linguistic intent indicate authentic dialogue.'}
        </p>
      </div>

      {/* Adaptive Fusion Weights Breakdown */}
      <div className="mt-3 pt-3 border-t border-slate-200 text-[10px]">
        <div className="flex justify-between text-slate-600 font-bold mb-1">
          <span>DYNAMIC ADAPTIVE WEIGHTS</span>
          <span>
            LATENCY: <span className="text-emerald-700 font-bold">{latencyMs}ms</span>
          </span>
        </div>
        <div className="grid grid-cols-2 gap-2 mt-1">
          <div className="p-1.5 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between text-slate-600 font-semibold">
              <span>W_DEEPFAKE</span>
              <span className="text-slate-900 font-bold">{dfWeight.toFixed(0)}%</span>
            </div>
            <div className="mt-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-emerald-600" style={{ width: `${dfWeight}%` }} />
            </div>
          </div>
          <div className="p-1.5 rounded bg-slate-50 border border-slate-200">
            <div className="flex justify-between text-slate-600 font-semibold">
              <span>W_SCAM_INTENT</span>
              <span className="text-slate-900 font-bold">{scamWeight.toFixed(0)}%</span>
            </div>
            <div className="mt-1 h-1.5 bg-slate-200 rounded-full overflow-hidden">
              <div className="h-full bg-amber-600" style={{ width: `${scamWeight}%` }} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
