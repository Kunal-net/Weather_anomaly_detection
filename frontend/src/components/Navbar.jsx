import React, { useState, useEffect } from 'react';
import { Radio, Activity, Clock, Map, BarChart3, Sliders, ShieldAlert } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, systemHealth }) {
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const formattedTime = currentTime.toLocaleTimeString('en-US', {
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  });

  const formattedDate = currentTime.toLocaleDateString('en-US', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  });

  const tabs = [
    { id: 'overview', label: 'National Map', icon: Map },
    { id: 'deepdive', label: 'Station Deep-Dive', icon: Activity },
    { id: 'prediction', label: 'What-If Studio', icon: Sliders },
    { id: 'trends', label: 'Historical Trends', icon: BarChart3 },
  ];

  return (
    <header className="border-b border-slate-800 bg-[#0f172a]/95 backdrop-blur-md sticky top-0 z-50 px-4 md:px-6 py-3 transition-all duration-300">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        {/* Brand & Badge */}
        <div className="flex items-center gap-3 w-full md:w-auto justify-between md:justify-start">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500 via-blue-600 to-indigo-700 shadow-lg shadow-cyan-500/25 border border-cyan-400/30">
              <Radio className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-cyan-200 bg-clip-text text-transparent">
                  AeroSense-AI
                </h1>
                <span className="text-[10px] uppercase font-extrabold tracking-widest px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-400 border border-cyan-500/30 shadow-sm">
                  SIH 2026
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Weather Anomaly Detection & Monitoring Platform
              </p>
            </div>
          </div>

          <div className="flex md:hidden items-center gap-2">
            <div className="flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg bg-slate-800/80 border border-slate-700 text-slate-300 font-mono">
              <Clock className="w-3.5 h-3.5 text-cyan-400" />
              <span>{formattedTime}</span>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav className="flex items-center gap-1 bg-slate-900/90 p-1.5 rounded-xl border border-slate-800 w-full md:w-auto overflow-x-auto">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-xs font-semibold transition-all duration-200 whitespace-nowrap ${
                  isActive
                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/20 text-cyan-300 border border-cyan-500/40 shadow-md shadow-cyan-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
                }`}
              >
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Right Info: Live Ticking Clock, Team ILLUMINATI, API Status Pill */}
        <div className="hidden lg:flex items-center gap-3">
          {/* Ticking Clock */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs font-mono text-slate-300 shadow-inner">
            <Clock className="w-3.5 h-3.5 text-cyan-400 animate-spin-slow" />
            <span className="text-white font-bold">{formattedTime}</span>
            <span className="text-slate-500">|</span>
            <span className="text-slate-400">{formattedDate}</span>
          </div>

          {/* Team Badge */}
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-slate-800/70 border border-slate-700/60 text-xs font-medium text-slate-300">
            <ShieldAlert className="w-3.5 h-3.5 text-indigo-400" />
            <span>Team ILLUMINATI</span>
          </div>

          {/* API Status Pill */}
          <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-xl bg-slate-900/80 border border-slate-800">
            <span
              className={`w-2 h-2 rounded-full ${
                systemHealth?.status === 'ok'
                  ? 'bg-emerald-400 animate-pulse shadow-sm shadow-emerald-400'
                  : 'bg-amber-400 animate-ping'
              }`}
            />
            <span className="text-slate-400">Backend:</span>
            <span
              className={`font-semibold ${
                systemHealth?.status === 'ok' ? 'text-emerald-400' : 'text-amber-400'
              }`}
            >
              {systemHealth?.status === 'ok' ? 'FastAPI Live' : 'Local Mock'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}
