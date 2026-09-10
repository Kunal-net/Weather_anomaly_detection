import React, { useState, useEffect } from 'react';
import { Cpu, Radio, Shield, Zap, Sparkles } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, systemHealth }) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const istTime = currentTime.toLocaleTimeString('en-IN', {
    timeZone: 'Asia/Kolkata',
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  const utcTime = currentTime.toISOString().slice(11, 19) + 'Z';

  const tabs = [
    { id: 'overview', code: '1', label: 'NATIONAL RADAR', desc: 'MAP & HUD' },
    { id: 'deepdive', code: '2', label: 'STATION TELEMETRY', desc: 'CORRIDORS' },
    { id: 'prediction', code: '3', label: 'WHAT-IF STUDIO', desc: 'SIMULATION' },
    { id: 'trends', code: '4', label: 'TIME-SERIES', desc: 'TELEMETRY' },
  ];

  const isBackendLive = systemHealth?.status === 'ok';

  return (
    <header className="sticky top-3 z-50 px-3 md:px-6 w-full max-w-[1780px] mx-auto select-none">
      {/* Floating Glassmorphic Container */}
      <div className="relative backdrop-blur-2xl bg-[#0b0f19]/85 border border-white/[0.12] rounded-2xl md:rounded-3xl shadow-[0_8px_32px_0_rgba(0,0,0,0.5)] px-4 py-2.5 flex items-center justify-between gap-4 overflow-hidden before:absolute before:inset-x-0 before:top-0 before:h-px before:bg-gradient-to-r before:from-transparent before:via-white/25 before:to-transparent">
        {/* Subtle Ambient Back-Glow */}
        <div className="absolute -left-10 -top-10 w-36 h-36 rounded-full bg-cyan-500/15 blur-2xl pointer-events-none" />

        {/* 1. Brand Identity & Satellite Telemetry Pill */}
        <div className="flex items-center gap-3 shrink-0">
          <div className="flex items-center gap-2.5">
            {/* Pulsing Satellite Radar Orb */}
            <div className="relative flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-br from-cyan-500/20 to-indigo-500/20 border border-cyan-400/30 shadow-[0_0_15px_rgba(6,182,212,0.3)]">
              <span className="absolute w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
              <Radio className="w-4 h-4 text-cyan-400 animate-pulse relative z-10" />
            </div>

            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="text-sm md:text-base font-extrabold tracking-tight text-white font-sans">
                  AeroSense<span className="text-cyan-400">.AI</span>
                </h1>
                <span className="px-1.5 py-0.5 text-[9px] font-bold rounded-md bg-cyan-500/10 text-cyan-300 border border-cyan-500/30 tracking-wider">
                  PS-1642
                </span>
              </div>
              <p className="text-[10px] text-slate-400 font-mono tracking-widest hidden sm:block">
                SIH-2026 // DUAL-ENGINE INTELLIGENCE
              </p>
            </div>
          </div>

          <div className="hidden 2xl:flex items-center gap-1.5 pl-3 border-l border-white/10 text-[10px] text-slate-400 font-mono">
            <span className="text-slate-500">UNIT:</span>
            <span className="text-slate-200 font-semibold">TEAM ILLUMINATI</span>
          </div>
        </div>

        {/* 2. Segmented Glass Pill Navigation Tabs */}
        <nav className="flex items-center bg-black/40 p-1 rounded-xl md:rounded-2xl border border-white/[0.08] backdrop-blur-md overflow-x-auto no-scrollbar">
          {tabs.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-3 md:px-4 py-1.5 text-xs font-mono font-bold tracking-wider transition-all duration-300 rounded-lg md:rounded-xl whitespace-nowrap flex items-center gap-2 ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-400/40 shadow-[0_0_20px_rgba(6,182,212,0.25)]'
                    : 'text-slate-400 hover:text-white hover:bg-white/[0.05] border border-transparent'
                }`}
              >
                <span
                  className={`text-[10px] font-bold px-1 py-0.2 rounded ${
                    isActive ? 'bg-cyan-400/20 text-cyan-300 border border-cyan-400/30' : 'text-slate-500'
                  }`}
                >
                  [{tab.code}]
                </span>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* 3. Live Digital Monospace Clocks & Sat-Link LED */}
        <div className="flex items-center gap-3 shrink-0 font-mono">
          {/* Dual Digital Clock (IST + UTC) */}
          <div className="hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08] tabular-nums text-xs shadow-inner">
            <div className="flex items-center gap-1 text-slate-300">
              <span className="text-[10px] text-slate-500 font-bold">IST:</span>
              <span className="font-bold text-white">{istTime}</span>
            </div>
            <span className="text-slate-600">|</span>
            <div className="flex items-center gap-1 text-slate-300">
              <span className="text-[10px] text-slate-500 font-bold">UTC:</span>
              <span className="font-bold text-cyan-400">{utcTime}</span>
            </div>
          </div>

          {/* Backend Connectivity Status Pill */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-white/[0.03] border border-white/[0.08] text-xs">
            <div className="relative flex items-center justify-center">
              <span
                className={`w-2 h-2 rounded-full ${
                  isBackendLive ? 'bg-emerald-400 animate-ping' : 'bg-emerald-400 animate-pulse'
                }`}
              />
              <span
                className={`absolute w-1.5 h-1.5 rounded-full ${
                  isBackendLive ? 'bg-emerald-400' : 'bg-emerald-400'
                }`}
              />
            </div>
            <span className="text-[11px] font-bold text-slate-200 hidden sm:inline">
              SAT-LINK
            </span>
            <span className="text-[10px] text-emerald-400 font-bold">
              {isBackendLive ? 'ONLINE' : 'ACTIVE'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
