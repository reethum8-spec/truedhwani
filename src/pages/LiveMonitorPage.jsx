import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useStreamContext } from '@/layouts/RootLayout';
import WaveformVisualizer from '@/components/WaveformVisualizer';
import BiomarkerPanel from '@/components/BiomarkerPanel';
import ScamIntentPanel from '@/components/ScamIntentPanel';
import DecisionPostureCard from '@/components/DecisionPostureCard';
import TranscriptStream from '@/components/TranscriptStream';
import ForensicAuditTable from '@/components/ForensicAuditTable';
import AudioInputController from '@/components/AudioInputController';
import { AudioResampler } from '@/services/audioResampler';

export default function LiveMonitorPage() {
  const { streamClient, setLatency, isStreaming, setIsStreaming } = useStreamContext();

  const [latestPacket, setLatestPacket] = useState(null);
  const [packets, setPackets] = useState([]);
  const [turns, setTurns] = useState([]);
  const [speechProb, setSpeechProb] = useState(0.0);
  const [analyserNode, setAnalyserNode] = useState(null);

  // Audio refs
  const audioContextRef = useRef(null);
  const mediaStreamRef = useRef(null);
  const processorNodeRef = useRef(null);
  const sourceNodeRef = useRef(null);
  const resamplerRef = useRef(null);
  const presetIntervalRef = useRef(null);
  const presetSourceNodeRef = useRef(null);

  // Packet receiver handler
  const handleIncomingPacket = useCallback((pkt) => {
    setLatestPacket(pkt);
    setPackets((prev) => [...prev, pkt]);

    if (pkt.latency_ms) {
      setLatency(pkt.latency_ms);
    }
    if (pkt.silero_speech_prob !== undefined) {
      setSpeechProb(pkt.silero_speech_prob);
    }

    if (pkt.transcript && pkt.transcript.trim().length > 0) {
      setTurns((prev) => [
        ...prev,
        {
          transcript: pkt.transcript,
          language: pkt.language,
          deepfake_score: pkt.deepfake_score,
          overall_risk_pct: pkt.overall_risk_pct,
          scam_intent_label: pkt.scam_intent_label,
          call_duration_seconds: pkt.call_duration_seconds,
        },
      ]);
    }
  }, [setLatency]);

  // Hook packet handler to streamClient
  useEffect(() => {
    if (!streamClient) return;
    streamClient.onPacket = handleIncomingPacket;
  }, [streamClient, handleIncomingPacket]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopStreaming();
    };
  }, []);

  // Stop any active streaming
  const stopStreaming = useCallback(() => {
    if (presetIntervalRef.current) {
      clearInterval(presetIntervalRef.current);
      presetIntervalRef.current = null;
    }
    if (presetSourceNodeRef.current) {
      try {
        presetSourceNodeRef.current.stop();
      } catch (e) {}
      presetSourceNodeRef.current = null;
    }
    if (processorNodeRef.current) {
      try {
        processorNodeRef.current.disconnect();
      } catch (e) {}
      processorNodeRef.current = null;
    }
    if (sourceNodeRef.current) {
      try {
        sourceNodeRef.current.disconnect();
      } catch (e) {}
      sourceNodeRef.current = null;
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      try {
        audioContextRef.current.close();
      } catch (e) {}
      audioContextRef.current = null;
    }

    if (streamClient) {
      streamClient.flushStream();
    }
    setIsStreaming(false);
    setSpeechProb(0.0);
  }, [streamClient, setIsStreaming]);

  // Start live microphone
  const startMicStream = async () => {
    stopStreaming();

    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });

      mediaStreamRef.current = stream;
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const audioCtx = new AudioCtx();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      setAnalyserNode(analyser);

      const source = audioCtx.createMediaStreamSource(stream);
      sourceNodeRef.current = source;
      source.connect(analyser);

      const resampler = new AudioResampler(audioCtx.sampleRate, 16000);
      resamplerRef.current = resampler;

      // ScriptProcessor for real-time PCM extraction
      const processor = audioCtx.createScriptProcessor(2048, 1, 1);
      processorNodeRef.current = processor;

      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        const pcm16 = resampler.resample(inputData);
        if (pcm16.length > 0 && streamClient) {
          streamClient.sendAudioChunk(pcm16);
        }
      };

      source.connect(processor);
      // Connect to destination to keep ScriptProcessor alive in modern browsers
      const silentGain = audioCtx.createGain();
      silentGain.gain.value = 0.0;
      processor.connect(silentGain);
      silentGain.connect(audioCtx.destination);

      if (streamClient) {
        streamClient.resetStream();
      }
      setIsStreaming(true);
    } catch (err) {
      console.error('Failed to open microphone stream:', err);
      alert(`Microphone access error: ${err.message}`);
    }
  };

  // Stream a benchmark preset audio file in real-time
  const streamPresetAudio = async (preset) => {
    stopStreaming();

    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      const audioCtx = new AudioCtx();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      setAnalyserNode(analyser);

      // Fetch the audio file
      const response = await fetch(preset.url);
      if (!response.ok) {
        throw new Error(`Failed to load preset file: ${response.statusText}`);
      }
      const arrayBuffer = await response.arrayBuffer();
      const decodedBuffer = await audioCtx.decodeAudioData(arrayBuffer);

      // Extract raw audio data for playback and streaming
      const rawChannelData = decodedBuffer.getChannelData(0);
      const resampler = new AudioResampler(decodedBuffer.sampleRate, 16000);
      const pcm16Full = resampler.resample(rawChannelData);

      // Setup audio playback through speakers so user can hear the call!
      const source = audioCtx.createBufferSource();
      source.buffer = decodedBuffer;
      source.connect(analyser);
      analyser.connect(audioCtx.destination);
      presetSourceNodeRef.current = source;
      source.start();

      source.onended = () => {
        stopStreaming();
      };

      if (streamClient) {
        streamClient.resetStream();
      }
      setIsStreaming(true);

      // Stream PCM chunks in real-time pace: 512 samples = 32ms
      const chunkSize = 512;
      let offset = 0;
      const intervalMs = 32;

      presetIntervalRef.current = setInterval(() => {
        if (offset >= pcm16Full.length) {
          clearInterval(presetIntervalRef.current);
          presetIntervalRef.current = null;
          if (streamClient) {
            streamClient.flushStream();
          }
          return;
        }

        const chunk = pcm16Full.subarray(offset, Math.min(offset + chunkSize, pcm16Full.length));
        if (streamClient) {
          streamClient.sendAudioChunk(chunk);
        }
        offset += chunkSize;
      }, intervalMs);
    } catch (err) {
      console.error('Failed to stream preset audio:', err);
      alert(`Preset audio playback error: ${err.message}`);
      stopStreaming();
    }
  };

  // Reset buffers
  const handleResetBuffers = () => {
    if (streamClient) {
      streamClient.resetStream();
    }
    setLatestPacket(null);
    setPackets([]);
    setTurns([]);
    setSpeechProb(0.0);
  };

  return (
    <div className="space-y-4">
      {/* Audio Ingestion Controls & Benchmark Presets */}
      <AudioInputController
        isStreaming={isStreaming}
        onStartMic={startMicStream}
        onStopMic={stopStreaming}
        onStreamPreset={streamPresetAudio}
        onResetStream={handleResetBuffers}
      />

      {/* Primary Oscilloscope & Pipeline Progress */}
      <WaveformVisualizer
        analyserNode={analyserNode}
        isActive={isStreaming}
        speechProb={speechProb}
        latencyMs={latestPacket?.latency_ms || 0}
      />

      {/* Main 3-Column Forensic Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Column 1: Acoustic Biomarker Matrix (Branch A) */}
        <BiomarkerPanel
          deepfakeScore={latestPacket?.deepfake_score ?? 0.0}
          deepfakePrediction={latestPacket?.deepfake_prediction ?? 'Bonafide'}
          aasistSpoofProb={latestPacket?.aasist_spoof_prob ?? 0.0}
          biomarkers={latestPacket?.biomarkers ?? {}}
        />

        {/* Column 2: Cognitive Linguistic Radar (Branch B) */}
        <ScamIntentPanel
          scamScore={latestPacket?.scam_intent_score ?? 0.0}
          topLabel={latestPacket?.scam_intent_label ?? 'Legitimate Dialogue'}
          intentProbabilities={latestPacket?.distilbert_intent_probabilities ?? {}}
        />

        {/* Column 3: Composite Directive & Adaptive Fusion */}
        <DecisionPostureCard
          overallRiskPct={latestPacket?.overall_risk_pct ?? 0.0}
          decision={latestPacket?.decision ?? 'Monitoring'}
          reason={latestPacket?.reason ?? 'Passively analyzing voice stream telemetry.'}
          recommendedAction={latestPacket?.recommended_action ?? 'Continue passive surveillance.'}
          weights={latestPacket?.weights ?? {}}
          durationSeconds={latestPacket?.call_duration_seconds ?? 0.0}
          latencyMs={latestPacket?.latency_ms ?? 0}
        />
      </div>

      {/* Lower Dual Grid: Live Multilingual Transcript & Session Audit Ledger */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div className="lg:col-span-1">
          <TranscriptStream
            turns={turns}
            onClear={() => setTurns([])}
          />
        </div>
        <div className="lg:col-span-2">
          <ForensicAuditTable
            packets={packets}
            onClear={() => setPackets([])}
          />
        </div>
      </div>
    </div>
  );
}
