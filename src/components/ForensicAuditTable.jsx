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
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Table className="w-4 h-4 text-blue-700" />
          <span className="text-xs font-bold text-slate-800 tracking-wider">
            SEC // 06 · SESSION FORENSIC AUDIT LEDGER
          </span>
          <span className="text-[10px] text-slate-500 font-semibold">
            ({packets.length} RECORDS EMITTED)
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={exportCSV}
            disabled={packets.length === 0}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 hover:text-slate-900 text-xs font-semibold transition-colors shadow-xs disabled:opacity-40"
          >
            <FileSpreadsheet className="w-3.5 h-3.5 text-emerald-600" />
            <span>EXPORT CSV</span>
          </button>

          <button
            onClick={exportJSON}
            disabled={packets.length === 0}
            className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 hover:text-slate-900 text-xs font-semibold transition-colors shadow-xs disabled:opacity-40"
          >
            <Download className="w-3.5 h-3.5 text-blue-700" />
            <span>EXPORT JSON</span>
          </button>

          {packets.length > 0 && (
            <button
              onClick={onClear}
              className="p-1 rounded text-slate-400 hover:text-red-600 hover:bg-slate-100 transition-colors"
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
            <tr className="border-b border-slate-200 text-[10px] text-slate-600 uppercase tracking-wider bg-slate-50 font-bold">
              <th className="p-2.5">#</th>
              <th className="p-2.5">TIME</th>
              <th className="p-2.5 min-w-[200px]">TRANSCRIPT (WHISPER)</th>
              <th className="p-2.5">DEEPFAKE</th>
              <th className="p-2.5">BIOMARKERS (JITTER/HNR)</th>
              <th className="p-2.5 min-w-[150px]">SCAM INTENT</th>
              <th className="p-2.5">RISK %</th>
              <th className="p-2.5">DIRECTIVE</th>
              <th className="p-2.5 text-right">LATENCY</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-200/80">
            {packets.length === 0 ? (
              <tr>
                <td colSpan="9" className="p-6 text-center text-slate-400 text-xs font-medium">
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
                    className="hover:bg-slate-50/80 transition-colors text-slate-800"
                  >
                    <td className="p-2.5 text-slate-400 font-bold">{idx + 1}</td>
                    <td className="p-2.5 text-slate-500 font-mono text-[11px]">
                      {(p.call_duration_seconds || 0).toFixed(1)}s
                    </td>
                    <td className="p-2.5 text-slate-900 font-sans text-xs font-medium">
                      {p.transcript ? `"${p.transcript}"` : <span className="text-slate-400 italic">No speech</span>}
                    </td>
                    <td className="p-2.5 font-mono">
                      <span
                        className={
                          p.deepfake_score > 0.65
                            ? 'text-red-700 font-bold'
                            : p.deepfake_score > 0.35
                            ? 'text-amber-700 font-bold'
                            : 'text-emerald-700 font-bold'
                        }
                      >
                        {(p.deepfake_score * 100).toFixed(1)}%
                      </span>
                    </td>
                    <td className="p-2.5 font-mono text-[11px] text-slate-600">
                      J: {(b.pitch_jitter_pct ?? 1.2).toFixed(2)}% | H: {(b.hnr_db ?? 18).toFixed(1)}dB
                    </td>
                    <td className="p-2.5">
                      <div className="text-xs text-slate-900 font-bold">
                        {p.scam_intent_label || 'Legitimate Dialogue'}
                      </div>
                      <div className="text-[10px] text-slate-500 font-medium">
                        Prob: {(p.scam_intent_score * 100).toFixed(0)}%
                      </div>
                    </td>
                    <td className="p-2.5 font-mono font-black">
                      <span
                        className={
                          isCritical
                            ? 'text-red-700'
                            : isWarning
                            ? 'text-amber-700'
                            : 'text-emerald-700'
                        }
                      >
                        {(p.overall_risk_pct || 0).toFixed(0)}%
                      </span>
                    </td>
                    <td className="p-2.5">
                      <span
                        className={`inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase shadow-xs border ${
                          isCritical
                            ? 'bg-red-50 text-red-800 border-red-200'
                            : isWarning
                            ? 'bg-amber-50 text-amber-800 border-amber-200'
                            : 'bg-emerald-50 text-emerald-800 border-emerald-200'
                        }`}
                      >
                        {isCritical ? (
                          <AlertTriangle className="w-2.5 h-2.5 text-red-600" />
                        ) : isWarning ? (
                          <ShieldAlert className="w-2.5 h-2.5 text-amber-600" />
                        ) : (
                          <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />
                        )}
                        <span>{p.decision || 'Monitoring'}</span>
                      </span>
                    </td>
                    <td className="p-2.5 text-right font-mono text-slate-600 text-[11px] font-semibold">
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
