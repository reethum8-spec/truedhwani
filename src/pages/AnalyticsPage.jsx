import React, { useState } from 'react';
import { Upload, FileAudio, AlertTriangle, ShieldCheck, Download, Play, CheckCircle2, FileText, Activity, Clock } from 'lucide-react';
import { analyzeAudioFile } from '@/services/api';
import BiomarkerPanel from '@/components/BiomarkerPanel';
import ScamIntentPanel from '@/components/ScamIntentPanel';
import DecisionPostureCard from '@/components/DecisionPostureCard';
import ForensicAuditTable from '@/components/ForensicAuditTable';

export default function AnalyticsPage() {
  const [file, setFile] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [selectedTimelineIndex, setSelectedTimelineIndex] = useState(0);

  const handleDrop = (e) => {
    e.preventDefault();
    const droppedFile = e.dataTransfer?.files?.[0];
    if (droppedFile) {
      setFile(droppedFile);
      runAnalysis(droppedFile);
    }
  };

  const handleFileSelect = (e) => {
    const selected = e.target.files?.[0];
    if (selected) {
      setFile(selected);
      runAnalysis(selected);
    }
  };

  const runAnalysis = async (audioFile) => {
    setIsAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const data = await analyzeAudioFile(audioFile);
      setAnalysisResult(data);
      if (data.stream_timeline && data.stream_timeline.length > 0) {
        // Default to packet with peak risk
        let peakIdx = 0;
        let maxRisk = -1;
        data.stream_timeline.forEach((p, idx) => {
          if (p.overall_risk > maxRisk) {
            maxRisk = p.overall_risk;
            peakIdx = idx;
          }
        });
        setSelectedTimelineIndex(peakIdx);
      }
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(err.message || 'Analysis encountered an error.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const selectedPacket = analysisResult?.stream_timeline?.[selectedTimelineIndex] || null;

  return (
    <div className="space-y-4 font-mono">
      {/* Page Title Strip */}
      <div className="tactical-card p-4 rounded flex items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-blue-400" />
            <span className="text-sm font-bold tracking-wider text-white uppercase">
              FORENSIC LAB // OFFLINE DEEP-TRACE INVESTIGATION
            </span>
          </div>
          <p className="text-xs text-slate-400 mt-0.5">
            Full-bandwidth file ingestion, acoustic biomarker extraction, and temporal threat reconstruction.
          </p>
        </div>

        {file && (
          <div className="text-right text-xs">
            <span className="text-slate-500">TARGET:</span>{' '}
            <span className="text-blue-300 font-semibold">{file.name}</span>
            <div className="text-[10px] text-slate-500">
              {(file.size / (1024 * 1024)).toFixed(2)} MB
            </div>
          </div>
        )}
      </div>

      {/* File Upload Zone */}
      {!analysisResult && !isAnalyzing && (
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          className="tactical-card p-12 rounded border-2 border-dashed border-slate-700 hover:border-blue-500/80 transition-colors flex flex-col items-center justify-center cursor-pointer text-center group"
          onClick={() => document.getElementById('file-upload-input').click()}
        >
          <input
            id="file-upload-input"
            type="file"
            accept="audio/*,.wav,.mp3,.flac,.ogg,.m4a"
            className="hidden"
            onChange={handleFileSelect}
          />
          <div className="w-16 h-16 rounded-full bg-slate-800/60 border border-slate-700 flex items-center justify-center text-blue-400 group-hover:scale-105 transition-transform">
            <Upload className="w-8 h-8" />
          </div>
          <h3 className="text-base font-bold text-slate-200 mt-4">
            DRAG & DROP AUDIO FILE OR CLICK TO BROWSE
          </h3>
          <p className="text-xs text-slate-400 mt-1 max-w-md">
            Supports standard PCM 16/24-bit .WAV, .MP3, .FLAC, .M4A. The pipeline will automatically resample, apply Silero VAD segmentation, and generate an ASVspoof biomarker trace.
          </p>
        </div>
      )}

      {/* Loading Analysis State */}
      {isAnalyzing && (
        <div className="tactical-card p-12 rounded flex flex-col items-center justify-center text-center space-y-4">
          <div className="w-12 h-12 rounded-full border-4 border-slate-800 border-t-blue-500 animate-spin" />
          <div>
            <div className="text-sm font-bold text-white tracking-wide">
              PIPELINE INFERENCE IN PROGRESS...
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Extracting F0 jitter, harmonics-to-noise ratio, vocoder flatness, and transcribing speech.
            </div>
          </div>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="p-4 rounded bg-red-950/40 border border-red-800 text-red-300 text-xs flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
          <div>
            <div className="font-bold">ANALYSIS ERROR</div>
            <div>{error}</div>
          </div>
        </div>
      )}

      {/* Analysis Results View */}
      {analysisResult && (
        <div className="space-y-4">
          {/* Executive Dossier Summary Card */}
          <div className="tactical-card p-4 rounded">
            <div className="flex flex-col md:flex-row md:items-center justify-between pb-3 border-b border-slate-800 gap-3">
              <div>
                <span className="text-[10px] text-slate-500 tracking-wider">
                  FORENSIC INVESTIGATION REPORT // DOSSIER #TD-{Date.now().toString().slice(-6)}
                </span>
                <h2 className="text-base font-bold text-white">
                  {analysisResult.filename}
                </h2>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => {
                    setAnalysisResult(null);
                    setFile(null);
                  }}
                  className="px-3 py-1.5 rounded bg-slate-800 text-slate-300 hover:text-white text-xs border border-slate-700"
                >
                  ANALYZE ANOTHER FILE
                </button>
              </div>
            </div>

            {/* Quick Metrics Bar */}
            <div className="mt-3 grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-2.5 rounded tactical-well">
                <span className="text-[10px] text-slate-400">AUDIO DURATION</span>
                <div className="text-lg font-bold text-slate-200 mt-0.5">
                  {analysisResult.duration_seconds}s
                </div>
              </div>

              <div className="p-2.5 rounded tactical-well">
                <span className="text-[10px] text-slate-400">PEAK RISK RATING</span>
                <div
                  className={`text-lg font-bold mt-0.5 ${
                    analysisResult.peak_overall_risk > 0.65
                      ? 'text-red-400'
                      : analysisResult.peak_overall_risk > 0.35
                      ? 'text-amber-400'
                      : 'text-emerald-400'
                  }`}
                >
                  {(analysisResult.peak_overall_risk * 100).toFixed(1)}%
                </div>
              </div>

              <div className="p-2.5 rounded tactical-well">
                <span className="text-[10px] text-slate-400">FINAL DIRECTIVE</span>
                <div
                  className={`text-sm font-bold uppercase mt-1 ${
                    analysisResult.final_decision?.toLowerCase().includes('high')
                      ? 'text-red-400'
                      : analysisResult.final_decision?.toLowerCase().includes('warn')
                      ? 'text-amber-400'
                      : 'text-emerald-400'
                  }`}
                >
                  {analysisResult.final_decision}
                </div>
              </div>

              <div className="p-2.5 rounded tactical-well">
                <span className="text-[10px] text-slate-400">SPEECH SEGMENTS</span>
                <div className="text-lg font-bold text-slate-200 mt-0.5">
                  {analysisResult.total_emitted_chunks}
                </div>
              </div>
            </div>

            {/* Consolidated Transcript Box */}
            <div className="mt-3 p-3 rounded bg-[#080d14] border border-slate-800/80">
              <div className="text-[10px] text-slate-400 font-semibold mb-1">
                CONSOLIDATED ASR TRANSCRIPT (WHISPER)
              </div>
              <p className="text-xs text-slate-200 font-sans leading-relaxed">
                "{analysisResult.consolidated_transcript || 'No continuous speech recognized.'}"
              </p>
            </div>
          </div>

          {/* Temporal Timeline Scrubber */}
          {analysisResult.stream_timeline && analysisResult.stream_timeline.length > 0 && (
            <div className="tactical-card p-4 rounded">
              <div className="flex items-center justify-between pb-2 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <Clock className="w-4 h-4 text-blue-400" />
                  <span className="text-xs font-semibold text-slate-200 tracking-wider">
                    TEMPORAL THREAT SCRUBBER (CLICK SEGMENT TO INSPECT)
                  </span>
                </div>
                <span className="text-[10px] text-slate-400">
                  SELECTED: SEGMENT #{selectedTimelineIndex + 1}
                </span>
              </div>

              <div className="mt-3 flex gap-1 h-16 w-full bg-[#080c11] p-1 rounded border border-slate-800 overflow-x-auto">
                {analysisResult.stream_timeline.map((p, idx) => {
                  const risk = p.overall_risk || 0;
                  const isSelected = idx === selectedTimelineIndex;
                  return (
                    <button
                      key={idx}
                      onClick={() => setSelectedTimelineIndex(idx)}
                      className={`flex-1 min-w-[20px] h-full flex flex-col justify-end p-0.5 rounded transition-all ${
                        isSelected ? 'ring-2 ring-blue-400 bg-slate-800' : 'hover:bg-slate-800/40'
                      }`}
                      title={`Turn #${idx + 1}: ${(p.overall_risk_pct || 0).toFixed(0)}% Risk`}
                    >
                      <div
                        className={`w-full rounded-t ${
                          risk > 0.65
                            ? 'bg-red-500'
                            : risk > 0.35
                            ? 'bg-amber-500'
                            : 'bg-emerald-500'
                        }`}
                        style={{ height: `${Math.max(10, risk * 100)}%` }}
                      />
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Detailed Selected Segment Breakdown */}
          {selectedPacket && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              <BiomarkerPanel
                deepfakeScore={selectedPacket.deepfake_score ?? 0.0}
                deepfakePrediction={selectedPacket.deepfake_prediction ?? 'Bonafide'}
                aasistSpoofProb={selectedPacket.aasist_spoof_prob ?? 0.0}
                biomarkers={selectedPacket.biomarkers ?? {}}
              />

              <ScamIntentPanel
                scamScore={selectedPacket.scam_intent_score ?? 0.0}
                topLabel={selectedPacket.scam_intent_label ?? 'Legitimate Dialogue'}
                intentProbabilities={selectedPacket.distilbert_intent_probabilities ?? {}}
              />

              <DecisionPostureCard
                overallRiskPct={selectedPacket.overall_risk_pct ?? 0.0}
                decision={selectedPacket.decision ?? 'Monitoring'}
                reason={selectedPacket.reason}
                recommendedAction={selectedPacket.recommended_action}
                weights={selectedPacket.weights}
                durationSeconds={selectedPacket.call_duration_seconds ?? 0.0}
                latencyMs={selectedPacket.latency_ms ?? 0}
              />
            </div>
          )}

          {/* Full Session Audit Ledger */}
          <ForensicAuditTable
            packets={analysisResult.stream_timeline || []}
            onClear={() => {}}
          />
        </div>
      )}
    </div>
  );
}
