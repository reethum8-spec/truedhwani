import React, { useState, useEffect } from 'react';
import { Mic, MicOff, Play, Square, RefreshCw, Volume2 } from 'lucide-react';
import { fetchPresets } from '@/services/api';

export default function AudioInputController({
  isStreaming = false,
  onStartMic = () => {},
  onStopMic = () => {},
  onStreamPreset = () => {},
  onResetStream = () => {},
}) {
  const [presets, setPresets] = useState([]);
  const [activePresetId, setActivePresetId] = useState(null);

  useEffect(() => {
    async function loadPresets() {
      try {
        const data = await fetchPresets();
        setPresets(data);
      } catch (err) {
        console.warn('Could not load presets:', err);
      }
    }
    loadPresets();
  }, []);

  const handlePresetClick = (preset) => {
    if (activePresetId === preset.id && isStreaming) {
      onStopMic();
      setActivePresetId(null);
    } else {
      setActivePresetId(preset.id);
      onStreamPreset(preset);
    }
  };

  return (
    <div className="tactical-card rounded p-4 font-mono select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-200">
        <div className="flex items-center gap-2">
          <Volume2 className="w-4 h-4 text-blue-700" />
          <span className="text-xs font-bold text-slate-800 tracking-wider">
            AUDIO INGESTION CONTROL & BENCHMARK PRESETS
          </span>
        </div>

        <button
          onClick={onResetStream}
          className="flex items-center gap-1.5 px-2.5 py-1 rounded bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 text-xs font-semibold transition-colors shadow-xs"
          title="Reset Pipeline Buffers"
        >
          <RefreshCw className="w-3 h-3" />
          <span>RESET BUFFERS</span>
        </button>
      </div>

      <div className="mt-3 grid grid-cols-1 md:grid-cols-3 gap-3">
        {/* Option 1: Live Hardware Mic */}
        <div className="tactical-well p-3 rounded flex flex-col justify-between">
          <div>
            <div className="flex justify-between items-center text-[10px] text-slate-500 font-bold">
              <span className="text-slate-900">LIVE MICROPHONE</span>
              <span className="text-blue-800">16kHz PCM RESAMPLED</span>
            </div>
            <p className="text-[11px] text-slate-600 mt-1 leading-snug">
              Stream directly from local input device for real-time speech verification.
            </p>
          </div>

          <div className="mt-3">
            {isStreaming && !activePresetId ? (
              <button
                onClick={onStopMic}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-red-600 hover:bg-red-700 text-white font-bold text-xs transition-colors shadow-xs"
              >
                <MicOff className="w-4 h-4" />
                <span>TERMINATE MIC STREAM</span>
              </button>
            ) : (
              <button
                onClick={onStartMic}
                disabled={isStreaming}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-blue-900 hover:bg-blue-800 text-white font-bold text-xs transition-colors shadow-xs disabled:opacity-50"
              >
                <Mic className="w-4 h-4 text-amber-400" />
                <span>START LIVE MIC INTERCEPT</span>
              </button>
            )}
          </div>
        </div>

        {/* Option 2: Benchmark Presets */}
        <div className="tactical-well p-3 rounded md:col-span-2">
          <div className="flex justify-between items-center text-[10px] text-slate-500 font-bold mb-2">
            <span className="text-slate-900 uppercase">BENCHMARK TEST SUITE (ONE-CLICK)</span>
            <span className="text-slate-500">ASVspoof 2019 / OTP LABS</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-2">
            {presets.map((preset) => {
              const isSelected = activePresetId === preset.id && isStreaming;
              const isScam = preset.id === 'scam';
              const isClone = preset.id === 'cloned';

              return (
                <button
                  key={preset.id}
                  onClick={() => handlePresetClick(preset)}
                  className={`p-2.5 rounded text-left border transition-all ${
                    isSelected
                      ? 'bg-blue-50 border-blue-600 text-blue-950 shadow-xs ring-1 ring-blue-500'
                      : 'bg-white border-slate-200 hover:border-slate-300 text-slate-800 shadow-xs'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] mb-1">
                    <span
                      className={`font-bold px-1.5 py-0.2 rounded text-[9px] ${
                        isScam
                          ? 'bg-red-50 text-red-800 border border-red-200'
                          : isClone
                          ? 'bg-amber-50 text-amber-800 border border-amber-200'
                          : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      }`}
                    >
                      {preset.id.toUpperCase()}
                    </span>
                    {isSelected ? (
                      <Square className="w-3 h-3 text-red-600 fill-red-600" />
                    ) : (
                      <Play className="w-3 h-3 text-slate-500 fill-slate-500" />
                    )}
                  </div>
                  <div className="text-xs font-bold truncate text-slate-900">
                    {preset.name}
                  </div>
                  <div className="text-[10px] text-slate-500 mt-1 line-clamp-2 leading-tight">
                    {preset.description}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
