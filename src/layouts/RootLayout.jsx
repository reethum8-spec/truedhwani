import React, { createContext, useContext, useState, useEffect } from 'react';
import { Outlet } from 'react-router-dom';
import Header from '@/components/Header';
import { StreamClient } from '@/services/streamClient';

export const StreamContext = createContext(null);

export function useStreamContext() {
  return useContext(StreamContext);
}

export default function RootLayout() {
  const [wsStatus, setWsStatus] = useState('disconnected');
  const [latency, setLatency] = useState(0);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamClient, setStreamClient] = useState(null);

  useEffect(() => {
    const client = new StreamClient({
      onStatusChange: (status) => setWsStatus(status),
      onError: (err) => console.warn('[RootLayout] StreamClient error:', err),
    });

    client.connect();
    setStreamClient(client);

    return () => {
      client.disconnect();
    };
  }, []);

  return (
    <StreamContext.Provider
      value={{
        streamClient,
        wsStatus,
        latency,
        setLatency,
        isStreaming,
        setIsStreaming,
      }}
    >
      <div className="min-h-screen bg-[#f8fafc] text-slate-900 flex flex-col tactical-grid antialiased">
        <Header wsStatus={wsStatus} latency={latency} isStreaming={isStreaming} />

        <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 py-5">
          <Outlet />
        </main>

        {/* Forensic Footer Strip */}
        <footer className="border-t border-slate-200 bg-white px-6 py-3 text-[10px] text-slate-500 font-mono flex flex-col sm:flex-row items-center justify-between gap-2 shadow-xs">
          <div className="flex items-center gap-3">
            <span className="text-slate-900 font-bold">TRUEDHWANI INTELLIGENCE ENGINE</span>
            <span>·</span>
            <span>DUAL-BRANCH ADAPTIVE FUSION (AASIST + ZERO-SHOT NLI)</span>
          </div>
          <div className="flex items-center gap-4">
            <span>MODEL: SILERO-VAD · WHISPER-BASE · AASIST-ASVSPOOF</span>
            <span>·</span>
            <span className="text-emerald-700 font-bold">SYSTEMS NORMAL</span>
          </div>
        </footer>
      </div>
    </StreamContext.Provider>
  );
}
