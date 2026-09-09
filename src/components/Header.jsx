import React from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, Radio, Activity, FileText, Cpu, AlertCircle } from 'lucide-react';

export default function Header({ wsStatus = 'disconnected', latency = 0, isStreaming = false }) {
  const getStatusBadge = () => {
    switch (wsStatus) {
      case 'connected':
        return (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-emerald-950/40 border border-emerald-800 text-emerald-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            <span>WS: SECURE // CONNECTED</span>
            {latency > 0 && <span className="text-emerald-300/70 border-l border-emerald-800/80 pl-2">{latency}ms</span>}
          </div>
        );
      case 'connecting':
        return (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-amber-950/40 border border-amber-800 text-amber-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></span>
            <span>WS: HANDSHAKE...</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-slate-900/80 border border-slate-800 text-slate-400 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-slate-500"></span>
            <span>WS: STANDBY</span>
          </div>
        );
    }
  };

  return (
    <header className="border-b border-slate-800/80 bg-[#080c12] select-none">
      {/* Tactical Top Security Classification Strip */}
      <div className="bg-[#05080c] border-b border-slate-800/60 px-4 py-0.5 flex justify-between items-center text-[10px] tracking-wider text-slate-400 font-mono">
        <div className="flex items-center gap-3">
          <span className="text-slate-300 font-semibold">SECURITY CLEARANCE: PUBLIC // FORENSIC TELEMETRY</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">PIPELINE: VAD-SILERO · ASR-WHISPER · AASIST-ENSEMBLE</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-slate-400">SAMPLING: 16,000 HZ PCM</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400">LATENCY TARGET: &lt; 400MS</span>
        </div>
      </div>

      {/* Main Bar */}
      <div className="px-6 py-3 flex items-center justify-between">
        {/* Left: Brand / System Identity */}
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 rounded border border-slate-700 bg-slate-900 flex items-center justify-center text-slate-100 shadow-inner">
            <Shield className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-tight text-white uppercase font-mono">TrueDhwani</span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-950/60 border border-blue-800 text-blue-300">
                v1.2.0-FORENSIC
              </span>
            </div>
            <p className="text-xs text-slate-400 font-mono tracking-tight">
              Acoustic Clone Biomarkers & Scam Threat Intercept Station
            </p>
          </div>
        </div>

        {/* Center: Navigation Controls */}
        <nav className="flex items-center gap-1 bg-[#0b1017] p-1 rounded border border-slate-800 text-xs font-mono">
          <NavLink
            to="/live-monitor"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
                isActive
                  ? 'bg-slate-800 text-white font-medium border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`
            }
          >
            <Radio className="w-3.5 h-3.5 text-red-400" />
            <span>LIVE INTERCEPT</span>
            {isStreaming && (
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-ping"></span>
            )}
          </NavLink>

          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
                isActive
                  ? 'bg-slate-800 text-white font-medium border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`
            }
          >
            <Activity className="w-3.5 h-3.5 text-blue-400" />
            <span>FORENSIC LAB</span>
          </NavLink>

          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-1.5 rounded transition-colors ${
                isActive
                  ? 'bg-slate-800 text-white font-medium border border-slate-700'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/40'
              }`
            }
          >
            <Cpu className="w-3.5 h-3.5 text-slate-400" />
            <span>SYSTEM BRIEFING</span>
          </NavLink>
        </nav>

        {/* Right: Status Telemetry */}
        <div className="flex items-center gap-3">
          {getStatusBadge()}
        </div>
      </div>
    </header>
  );
}
