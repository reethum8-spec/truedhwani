import React, { useState, useEffect, useRef } from 'react';
import { Mic, MicOff, Play, Square, Upload, RefreshCw, Sparkles, Volume2 } from 'lucide-react';
import { fetchPresets } from '@/services/api';
import { AudioResampler } from '@/services/audioResampler';

export default function AudioInputController({
  isStreaming = false,
  onStartMic = () => {},
  onStopMic = () => {},
  onStreamPreset = () => {},
  onUploadFile = () => {},
  onResetStream = () => {},
}) {
  const [presets, setPresets] = useState([]);
  const [activePresetId, setActivePresetId] = useState(null);
  const [isLoadingPresets, setIsLoadingPresets] = useState(false);
  const fileInputRef = useRef(null);

  useEffect(() => {
    async function loadPresets() {
      setIsLoadingPresets(true);
      try {
        const data = await fetchPresets();
        setPresets(data);
      } catch (err) {
        console.warn('Could not load presets:', err);
      } finally {
        setIsLoadingPresets(false);
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

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      onUploadFile(file);
      e.target.value = '';
    }
  };

  return (
    <div className="tactical-card rounded p-4 font-mono select-none">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Volume2 className="w-4 h-4 text-blue-400" />
          <span className="text-xs font-semibold text-slate-200 tracking-wider">
            AUDIO INGESTION CONTROL & BENCHMARK PRESETS
          </span>
        </div>

        <button
          onClick={onResetStream}
          className="flex items-center gap-1.5 px-2 py-1 rounded bg-[#090d14] border border-slate-800 hover:border-slate-700 text-slate-400 hover:text-slate-200 text-xs transition-colors"
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
            <div className="flex justify-between items-center text-[10px] text-slate-400">
              <span className="font-semibold text-slate-300">LIVE MICROPHONE</span>
              <span className="text-slate-500">16kHz PCM RESAMPLED</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">
              Stream directly from local input device for real-time speech verification.
            </p>
          </div>

          <div className="mt-3">
            {isStreaming && !activePresetId ? (
              <button
                onClick={onStopMic}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-red-950/80 border border-red-700 text-red-300 font-bold text-xs hover:bg-red-900 transition-colors shadow-[0_0_10px_rgba(220,38,38,0.2)]"
              >
                <MicOff className="w-4 h-4 text-red-400" />
                <span>TERMINATE MIC STREAM</span>
              </button>
            ) : (
              <button
                onClick={onStartMic}
                disabled={isStreaming}
                className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded bg-blue-900/40 border border-blue-700 text-blue-300 font-semibold text-xs hover:bg-blue-800/60 transition-colors disabled:opacity-50"
              >
                <Mic className="w-4 h-4 text-blue-400" />
                <span>START LIVE MIC INTERCEPT</span>
              </button>
            )}
          </div>
        </div>

        {/* Option 2: Benchmark Presets */}
        <div className="tactical-well p-3 rounded md:col-span-2">
          <div className="flex justify-between items-center text-[10px] text-slate-400 mb-2">
            <span className="font-semibold text-slate-300">BENCHMARK TEST SUITE (ONE-CLICK)</span>
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
                      ? 'bg-blue-950/80 border-blue-600 text-white shadow-[0_0_10px_rgba(37,99,235,0.25)]'
                      : 'bg-[#080d14] border-slate-800/80 hover:border-slate-700 text-slate-300'
                  }`}
                >
                  <div className="flex items-center justify-between text-[10px] mb-1">
                    <span
                      className={`font-semibold px-1 rounded text-[9px] ${
                        isScam
                          ? 'bg-red-950 text-red-400 border border-red-900'
                          : isClone
                          ? 'bg-amber-950 text-amber-400 border border-amber-900'
                          : 'bg-emerald-950 text-emerald-400 border border-emerald-900'
                      }`}
                    >
                      {preset.id.toUpperCase()}
                    </span>
                    {isSelected ? (
                      <Square className="w-3 h-3 text-red-400 fill-red-400" />
                    ) : (
                      <Play className="w-3 h-3 text-slate-400 fill-slate-400" />
                    )}
                  </div>
                  <div className="text-xs font-semibold truncate text-slate-200">
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
