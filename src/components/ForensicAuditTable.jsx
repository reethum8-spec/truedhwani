import React from 'react';
import { Table, Download, Trash2, FileSpreadsheet, ShieldAlert, CheckCircle2, AlertTriangle } from 'lucide-react';

export default function ForensicAuditTable({
  packets = [],
  onClear = () => {},
}) {
  const exportJSON = () => {
    if (packets.length === 0) return;
    const blob = new Blob([JSON.stringify(packets, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `truedhwani-forensic-audit-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const exportCSV = () => {
    if (packets.length === 0) return;
    const headers = [
      'Turn',
      'Time_Sec',
      'Transcript',
      'Language',
      'Deepfake_Score',
      'AASIST_Spoof',
      'Pitch_Jitter_Pct',
      'HNR_dB',
      'Vocoder_Artifact',
      'Scam_Intent_Label',
      'Scam_Intent_Score',
      'Overall_Risk_Pct',
      'Decision',
      'Latency_ms',
    ];

    const rows = packets.map((p, idx) => {
      const b = p.biomarkers || {};
      return [
        idx + 1,
        (p.call_duration_seconds || 0).toFixed(2),
        `"${(p.transcript || '').replace(/"/g, '""')}"`,
        p.language || 'en',
        (p.deepfake_score || 0).toFixed(4),
        (p.aasist_spoof_prob || 0).toFixed(4),
        (b.pitch_jitter_pct ?? 0).toFixed(3),
        (b.hnr_db ?? 0).toFixed(2),
        (b.vocoder_artifact_score ?? 0).toFixed(3),
        `"${p.scam_intent_label || 'Legitimate Dialogue'}"`,
        (p.scam_intent_score || 0).toFixed(4),
        (p.overall_risk_pct || 0).toFixed(1),
        p.decision || 'Monitoring',
        p.latency_ms || 0,
      ].join(',');
    });

    const csvContent = [headers.join(','), ...rows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `truedhwani-forensic-audit-${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="tactical-card rounded p-4 font-mono select-none">
      {/* Table Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-200 tracking-wider">
            SEC // 06 · SESSION FORENSIC AUDIT LEDGER
          </span>
          <span className="text-[10px] text-slate-400">
            ({packets.length} RECORDS EMITTED)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={exportCSV}
            disabled={packets.length === 0}
            className="flex items-center gap-1.5 px-2 py-1 rounded bg-[#090d14] border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white text-xs transition-colors disabled:opacity-40"
          >
            <FileSpreadsheet className="w-3 h-3 text-emerald-400" />
            <span>EXPORT CSV</span>
          </button>

          <button
            onClick={exportJSON}
            disabled={packets.length === 0}
            className="flex items-center gap-1.5 px-2 py-1 rounded bg-[#090d14] border border-slate-800 hover:border-slate-700 text-slate-300 hover:text-white text-xs transition-colors disabled:opacity-40"
          >
            <Download className="w-3 h-3 text-blue-400" />
            <span>EXPORT JSON</span>
          </button>

          {packets.length > 0 && (
            <button
              onClick={onClear}
              className="p-1 rounded text-slate-500 hover:text-red-400 hover:bg-slate-800 transition-colors"
              title="Clear audit ledger"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Table Content */}
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left text-xs border-collapse">
          <thead>
            <tr className="border-b border-slate-800 text-[10px] text-slate-400 uppercase tracking-wider bg-[#080c11]">
              <th className="p-2">#</th>
              <th className="p-2">TIME</th>
              <th className="p-2 min-w-[200px]">TRANSCRIPT (WHISPER)</th>
              <th className="p-2">DEEPFAKE</th>
              <th className="p-2">BIOMARKERS (JITTER/HNR)</th>
              <th className="p-2 min-w-[150px]">SCAM INTENT</th>
              <th className="p-2">RISK %</th>
              <th className="p-2">DIRECTIVE</th>
              <th className="p-2 text-right">LATENCY</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60">
            {packets.length === 0 ? (
              <tr>
                <td colSpan="9" className="p-6 text-center text-slate-500 text-xs">
                  NO AUDIT PACKETS LOGGED YET. INITIATE STREAM TO POPULATE FORENSIC LEDGER.
                </td>
              </tr>
            ) : (
              packets.map((p, idx) => {
                const isCritical = (p.overall_risk_pct || 0) > 65;
                const isWarning = (p.overall_risk_pct || 0) >= 35 && !isCritical;
                const b = p.biomarkers || {};

                return (
                  <tr
                    key={idx}
                    className="hover:bg-slate-800/30 transition-colors text-slate-300"
                  >
                    <td className="p-2 text-slate-500 font-semibold">{idx + 1}</td>
                    <td className="p-2 text-slate-400 font-mono text-[11px]">
                      {(p.call_duration_seconds || 0).toFixed(1)}s
                    </td>
                    <td className="p-2 text-slate-200 font-sans text-xs">
                      {p.transcript ? `"${p.transcript}"` : <span className="text-slate-600 italic">No speech</span>}
                    </td>
                    <td className="p-2 font-mono">
                      <span
                        className={
                          p.deepfake_score > 0.65
                            ? 'text-red-400 font-bold'
                            : p.deepfake_score > 0.35
                            ? 'text-amber-400 font-bold'
                            : 'text-emerald-400'
                        }
                      >
                        {(p.deepfake_score * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="p-2 font-mono text-[11px] text-slate-400">
                      J: {(b.pitch_jitter_pct ?? 1.2).toFixed(2)}% | H: {(b.hnr_db ?? 18).toFixed(1)}dB
                    </td>
                    <td className="p-2">
                      <div className="text-xs text-slate-200">
                        {p.scam_intent_label || 'Legitimate Dialogue'}
                      </div>
                      <div className="text-[10px] text-slate-500">
                        Prob: {(p.scam_intent_score * 100).toFixed(0)}%
                      </div>
                    </td>
                    <td className="p-2 font-mono font-bold">
                      <span
                        className={
                          isCritical
                            ? 'text-red-400'
                            : isWarning
                            ? 'text-amber-400'
                            : 'text-emerald-400'
                        }
                      >
                        {(p.overall_risk_pct || 0).toFixed(0)}%
                      </span>
                    </td>
                    <td className="p-2">
                      <span
                        className={`inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-semibold uppercase ${
                          isCritical
                            ? 'bg-red-950/80 text-red-300 border border-red-800'
                            : isWarning
                            ? 'bg-amber-950/80 text-amber-300 border border-amber-800'
                            : 'bg-emerald-950/80 text-emerald-300 border border-emerald-800'
                        }`}
                      >
                        {isCritical ? (
                          <AlertTriangle className="w-2.5 h-2.5 text-red-400" />
                        ) : isWarning ? (
                          <ShieldAlert className="w-2.5 h-2.5 text-amber-400" />
                        ) : (
                          <CheckCircle2 className="w-2.5 h-2.5 text-emerald-400" />
                        )}
                        <span>{p.decision || 'Monitoring'}</span>
                      </span>
                    </td>
                    <td className="p-2 text-right font-mono text-slate-400 text-[11px]">
                      {p.latency_ms || 0}ms
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
