import React from 'react';
import { NavLink } from 'react-router-dom';
import { Shield, Radio, Activity, Cpu } from 'lucide-react';

export default function Header({ wsStatus = 'disconnected', latency = 0, isStreaming = false }) {
  const getStatusBadge = () => {
    switch (wsStatus) {
      case 'connected':
        return (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-mono shadow-xs">
            <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse"></span>
            <span className="font-semibold">WS: SECURE // CONNECTED</span>
            {latency > 0 && (
              <span className="text-emerald-700/80 border-l border-emerald-300 pl-2 font-mono">
                {latency}ms
              </span>
            )}
          </div>
        );
      case 'connecting':
        return (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-amber-50 border border-amber-200 text-amber-800 text-xs font-mono shadow-xs">
            <span className="w-2 h-2 rounded-full bg-amber-600 animate-pulse"></span>
            <span className="font-semibold">WS: HANDSHAKE...</span>
          </div>
        );
      default:
        return (
          <div className="flex items-center gap-2 px-2.5 py-1 rounded bg-slate-100 border border-slate-200 text-slate-600 text-xs font-mono">
            <span className="w-2 h-2 rounded-full bg-slate-400"></span>
            <span>WS: STANDBY</span>
          </div>
        );
    }
  };

  return (
    <header className="border-b border-slate-200 bg-white select-none sticky top-0 z-40 shadow-xs">
      {/* Tactical Top Classification Strip */}
      <div className="bg-slate-100/80 border-b border-slate-200 px-4 py-1 flex justify-between items-center text-[10px] tracking-wider text-slate-600 font-mono">
        <div className="flex items-center gap-3">
          <span className="text-slate-900 font-bold uppercase">SECURITY CLEARANCE: PUBLIC // FORENSIC TELEMETRY</span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-600">PIPELINE: VAD-SILERO · ASR-WHISPER · AASIST-ENSEMBLE</span>
        </div>
        <div className="flex items-center gap-4">
          <span className="text-slate-600">SAMPLING: 16,000 HZ PCM</span>
          <span className="text-slate-300">|</span>
          <span className="text-slate-600">LATENCY TARGET: &lt; 400MS</span>
        </div>
      </div>

      {/* Main Bar */}
      <div className="px-6 py-3 flex items-center justify-between">
        {/* Left: Brand Identity with Prussian Blue & Warm Amber */}
        <div className="flex items-center gap-3.5">
          <div className="w-10 h-10 rounded border border-blue-900/10 bg-gradient-to-br from-blue-900 to-slate-900 flex items-center justify-center text-white shadow-xs">
            <Shield className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="text-base font-bold tracking-tight text-slate-900 uppercase font-mono">
                TrueDhwani
              </span>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-blue-50 border border-blue-200 text-blue-800 font-semibold">
                v1.2.0-FORENSIC
              </span>
            </div>
            <p className="text-xs text-slate-500 font-mono tracking-tight">
              Acoustic Clone Biomarkers & Scam Threat Intercept Station
            </p>
          </div>
        </div>

        {/* Center: Navigation Tabs with clean laboratory styling */}
        <nav className="flex items-center gap-1 bg-slate-100 p-1 rounded-md border border-slate-200 text-xs font-mono">
          <NavLink
            to="/live-monitor"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-1.5 rounded transition-all ${
                isActive
                  ? 'bg-white text-slate-900 font-bold shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
              }`
            }
          >
            <Radio className="w-3.5 h-3.5 text-red-600" />
            <span>LIVE INTERCEPT</span>
            {isStreaming && (
              <span className="w-1.5 h-1.5 rounded-full bg-red-600 animate-ping"></span>
            )}
          </NavLink>

          <NavLink
            to="/analytics"
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-1.5 rounded transition-all ${
                isActive
                  ? 'bg-white text-slate-900 font-bold shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
              }`
            }
          >
            <Activity className="w-3.5 h-3.5 text-blue-700" />
            <span>FORENSIC LAB</span>
          </NavLink>

          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `flex items-center gap-2 px-3 py-1.5 rounded transition-all ${
                isActive
                  ? 'bg-white text-slate-900 font-bold shadow-xs border border-slate-200/80'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-white/60'
              }`
            }
          >
            <Cpu className="w-3.5 h-3.5 text-amber-700" />
            <span>SYSTEM BRIEFING</span>
          </NavLink>
        </nav>

        {/* Right: Status Telemetry Badge */}
        <div className="flex items-center gap-3">
          {getStatusBadge()}
        </div>
      </div>
    </header>
  );
}
