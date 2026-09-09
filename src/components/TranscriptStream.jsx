import React, { useEffect, useRef } from 'react';
import { MessageSquare, Languages, Clock, Volume2, Trash2 } from 'lucide-react';

export default function TranscriptStream({
  turns = [],
  currentTurn = null,
  onClear = () => {},
}) {
  const containerRef = useRef(null);

  // Auto-scroll to latest turn
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [turns, currentTurn]);

  return (
    <div className="tactical-card rounded p-4 font-mono select-none flex flex-col h-full min-h-[260px]">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-200 tracking-wider">
            SEC // 05 · ASR TRANSCRIPTION & LEXICAL LEDGER
          </span>
          <span className="text-[10px] px-1.5 py-0.5 rounded bg-blue-950/60 border border-blue-800 text-blue-300">
            FASTER-WHISPER BASE
          </span>
        </div>

        <div className="flex items-center gap-3">
          <span className="text-[10px] text-slate-400">
            TURNS: <span className="text-slate-200 font-semibold">{turns.length}</span>
          </span>
          {turns.length > 0 && (
            <button
              onClick={onClear}
              className="text-slate-500 hover:text-red-400 text-xs p-1 rounded hover:bg-slate-800 transition-colors"
              title="Clear transcript"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Transcript Log Container */}
      <div
        ref={containerRef}
        className="mt-3 flex-1 overflow-y-auto space-y-2 pr-1 text-xs"
        style={{ maxHeight: '280px' }}
      >
        {turns.length === 0 && !currentTurn && (
          <div className="h-full min-h-[160px] flex flex-col items-center justify-center text-slate-500 text-xs gap-2">
            <Volume2 className="w-6 h-6 text-slate-600" />
            <span>AWAITING SPEECH INGESTION...</span>
            <span className="text-[10px] text-slate-600">
              Silero VAD will automatically segment incoming speech chunks.
            </span>
          </div>
        )}

        {/* Completed Turns */}
        {turns.map((t, idx) => {
          const isThreat = (t.overall_risk_pct ?? 0) > 65 || t.deepfake_score > 0.65;
          const isWarning = (t.overall_risk_pct ?? 0) >= 35 && !isThreat;

          return (
            <div
              key={idx}
              className={`p-2.5 rounded border transition-colors ${
                isThreat
                  ? 'bg-red-950/20 border-red-900/60 text-slate-200'
                  : isWarning
                  ? 'bg-amber-950/20 border-amber-900/60 text-slate-200'
                  : 'bg-[#090d14] border-slate-800/80 text-slate-300'
              }`}
            >
              <div className="flex items-center justify-between text-[10px] text-slate-400 mb-1 border-b border-slate-800/60 pb-1">
                <div className="flex items-center gap-2">
                  <span className="font-semibold text-slate-300">
                    TURN #{idx + 1}
                  </span>
                  <span className="text-slate-500">|</span>
                  <span className="px-1 py-0.2 rounded bg-slate-800 text-slate-300 uppercase font-mono">
                    {t.language || 'EN'}
                  </span>
                  <span className="text-slate-500">
                    {t.call_duration_seconds ? `${t.call_duration_seconds.toFixed(1)}s` : ''}
                  </span>
                </div>

                <div className="flex items-center gap-2">
                  <span className={`font-semibold ${isThreat ? 'text-red-400' : isWarning ? 'text-amber-400' : 'text-emerald-400'}`}>
                    RISK: {t.overall_risk_pct ? t.overall_risk_pct.toFixed(0) : '0'}%
                  </span>
                  <span className="text-slate-500">|</span>
                  <span className="text-slate-400">
                    DF: {(t.deepfake_score * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Text content */}
              <div className="text-xs leading-relaxed font-sans text-slate-100 font-medium">
                "{t.transcript}"
              </div>

              {/* Turn classification tag */}
              <div className="mt-1.5 flex items-center gap-2 text-[10px]">
                <span className="text-slate-500">INTENT:</span>
                <span className="text-blue-300 font-semibold">{t.scam_intent_label || 'Legitimate Dialogue'}</span>
              </div>
            </div>
          );
        })}

        {/* Active streaming interim turn */}
        {currentTurn && (
          <div className="p-2.5 rounded border border-blue-800/60 bg-blue-950/20 text-slate-200 animate-pulse">
            <div className="flex items-center gap-2 text-[10px] text-blue-400 mb-1">
              <span className="font-semibold">STREAMING INGESTION IN PROGRESS...</span>
            </div>
            <div className="text-xs leading-relaxed font-sans text-blue-200">
              "{currentTurn.transcript}"
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
