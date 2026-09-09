import React from 'react';
import { AlertCircle, ShieldAlert, Target } from 'lucide-react';

export default function ScamIntentPanel({
  scamScore = 0.0,
  topLabel = 'Legitimate Dialogue',
  intentProbabilities = {},
}) {
  const isHighRisk = scamScore >= 0.70;
  const isWarning = scamScore >= 0.40 && scamScore < 0.70;

  // Standard 10 fraud categories
  const defaultCategories = [
    'Legitimate Dialogue',
    'Bank Verification Scams',
    'OTP / 2FA Theft',
    'Law Enforcement Impersonation',
    'Tech Support Scams',
    'Lottery & Prize Scams',
    'Urgent Family Emergency',
    'Investment & Crypto Fraud',
    'Job Offer / Task Scams',
    'Courier & Customs Scams',
  ];

  // Merge provided probabilities
  const entries = defaultCategories.map((name) => {
    let prob = 0.0;
    for (const [key, val] of Object.entries(intentProbabilities)) {
      if (key.toLowerCase().includes(name.toLowerCase().slice(0, 8))) {
        prob = val;
        break;
      }
    }
    if (name === topLabel && prob === 0) prob = scamScore;
    if (name === 'Legitimate Dialogue' && prob === 0 && scamScore < 0.2) prob = 1 - scamScore;
    return { name, prob };
  });

  // Sort descending
  entries.sort((a, b) => b.prob - a.prob);

  return (
    <div className="tactical-card rounded p-4 font-mono select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4 text-amber-700" />
          <span className="text-xs font-bold text-slate-800 tracking-wider">
            SEC // 03 · COGNITIVE LINGUISTIC RADAR (BRANCH B)
          </span>
        </div>

        {/* Top intent badge */}
        <div
          className={`flex items-center gap-1.5 px-2.5 py-0.5 rounded text-[11px] font-bold border shadow-xs ${
            isHighRisk
              ? 'bg-red-50 border-red-200 text-red-800'
              : isWarning
              ? 'bg-amber-50 border-amber-200 text-amber-800'
              : 'bg-slate-100 border-slate-200 text-slate-800'
          }`}
        >
          <Target className="w-3.5 h-3.5" />
          <span>{topLabel ? topLabel.toUpperCase() : 'ANALYZING...'}</span>
        </div>
      </div>

      {/* Primary Score readout */}
      <div className="mt-3 flex items-center justify-between p-3 rounded tactical-well">
        <div>
          <div className="text-[10px] text-slate-500 font-semibold">MALICIOUS INTENT CONFIDENCE</div>
          <div className="flex items-baseline gap-2 mt-0.5">
            <span
              className={`text-2xl font-extrabold ${
                isHighRisk
                  ? 'text-red-700'
                  : isWarning
                  ? 'text-amber-700'
                  : 'text-slate-800'
              }`}
            >
              {(scamScore * 100).toFixed(1)}%
            </span>
            <span className="text-xs text-slate-500 font-medium">
              [Zero-Shot Transformer NLI]
            </span>
          </div>
        </div>

        {/* Threat Level Badge */}
        <div className="text-right">
          <span className="text-[10px] text-slate-500 font-medium">COERCION LEVEL</span>
          <div
            className={`text-xs font-bold mt-0.5 ${
              isHighRisk
                ? 'text-red-700'
                : isWarning
                ? 'text-amber-700'
                : 'text-emerald-700'
            }`}
          >
            {isHighRisk ? 'HIGH COERCION' : isWarning ? 'ELEVATED PRESSURE' : 'NORMAL / BENIGN'}
          </div>
        </div>
      </div>

      {/* 10-Intent Distribution Bars */}
      <div className="mt-3 pt-3 border-t border-slate-200">
        <div className="flex justify-between text-[10px] text-slate-600 font-bold mb-2">
          <span>THREAT CATEGORY DISTRIBUTION (NLI EMBEDDINGS)</span>
          <span>PROBABILITY</span>
        </div>

        <div className="space-y-1.5 max-h-44 overflow-y-auto pr-1">
          {entries.map(({ name, prob }) => {
            const isTop = name.toLowerCase() === topLabel.toLowerCase() || prob > 0.4;
            const isMalicious = name !== 'Legitimate Dialogue' && prob > 0.25;

            return (
              <div key={name} className="text-[10px]">
                <div className="flex justify-between items-center mb-0.5">
                  <span
                    className={`truncate pr-2 ${
                      isTop
                        ? isMalicious
                          ? 'text-red-700 font-bold'
                          : 'text-blue-900 font-bold'
                        : 'text-slate-600 font-medium'
                    }`}
                  >
                    {name}
                  </span>
                  <span
                    className={`font-bold ${
                      isTop
                        ? isMalicious
                          ? 'text-red-700'
                          : 'text-blue-900'
                        : 'text-slate-500'
                    }`}
                  >
                    {(prob * 100).toFixed(0)}%
                  </span>
                </div>
                {/* Meter Bar */}
                <div className="h-1.5 w-full bg-slate-200 rounded-full overflow-hidden">
                  <div
                    className={`h-full transition-all duration-300 ${
                      name === 'Legitimate Dialogue'
                        ? 'bg-slate-400'
                        : prob > 0.6
                        ? 'bg-red-600'
                        : prob > 0.3
                        ? 'bg-amber-500'
                        : 'bg-blue-700'
                    }`}
                    style={{ width: `${Math.min(100, prob * 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
