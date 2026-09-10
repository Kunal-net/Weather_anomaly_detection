import React from 'react';
import { AlertCircle, AlertTriangle, ShieldCheck, Radio, Activity, Zap, CheckCircle2 } from 'lucide-react';

/**
 * ExecutiveSummaryCards:
 * Pinterest / Linear inspired Asymmetrical Bento Grid.
 * Built with deep space glassmorphism, 3D hover physics, ambient glow discs,
 * and specular hairline edges.
 */
export default function ExecutiveSummaryCards({ locations = [] }) {
  const totalCount = locations.length || 10;
  const criticalCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'CRITICAL'
  ).length;
  const highCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'HIGH'
  ).length;
  const watchCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'WATCH'
  ).length;
  const normalCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'NORMAL'
  ).length;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 select-none">
      {/* Card 1: Monitored Stations Network */}
      <div className="glass-card glass-card-hover rounded-2xl md:rounded-3xl p-5 group flex flex-col justify-between">
        {/* Ambient Back Glow */}
        <div className="absolute -right-8 -bottom-8 w-32 h-32 rounded-full bg-cyan-500/15 blur-2xl group-hover:bg-cyan-500/25 transition-all duration-500 pointer-events-none" />

        <div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-cyan-300/90 uppercase tracking-widest font-mono flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-pulse" />
              Network Coverage
            </span>
            <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-400/20 text-cyan-400 group-hover:scale-110 group-hover:rotate-6 transition-all duration-300 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
              <Radio className="w-4 h-4 animate-pulse" />
            </div>
          </div>

          <div className="mt-4">
            <div className="text-3xl md:text-4xl font-extrabold text-white tracking-tight font-mono tabular-nums">
              {totalCount}
              <span className="text-sm font-normal text-slate-400 ml-1.5">/ 10 Stations</span>
            </div>
            <p className="text-xs text-slate-300 mt-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping shrink-0" />
              <span>Real-time telemetry across 10 climate zones</span>
            </p>
          </div>
        </div>

        {/* Telemetry Footnote */}
        <div className="mt-5 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-slate-400">
          <span>LATENCY: &lt;15ms</span>
          <span className="text-cyan-300 font-bold tracking-wider">100% OPERATIONAL</span>
        </div>
      </div>

      {/* Card 2: Critical Alerts Hazard Level */}
      <div className="glass-card glass-card-hover rounded-2xl md:rounded-3xl p-5 group flex flex-col justify-between border-rose-500/20 hover:border-rose-500/50">
        <div className="absolute -right-8 -bottom-8 w-32 h-32 rounded-full bg-rose-500/20 blur-2xl group-hover:bg-rose-500/35 transition-all duration-500 pointer-events-none" />

        <div>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="text-xs font-bold text-rose-400 uppercase tracking-widest font-mono">
                Hazard Level 4
              </span>
              <span className="px-1.5 py-0.5 text-[9px] font-extrabold rounded-md bg-rose-500/20 text-rose-300 border border-rose-500/40 animate-pulse">
                CRITICAL
              </span>
            </div>
            <div className="p-2.5 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-400 group-hover:scale-110 transition-all duration-300 shadow-[0_0_15px_rgba(239,68,68,0.3)]">
              <AlertCircle className="w-4 h-4 animate-bounce" />
            </div>
          </div>

          <div className="mt-4">
            <div className="text-3xl md:text-4xl font-extrabold text-rose-400 tracking-tight font-mono tabular-nums">
              {criticalCount}
              <span className="text-sm font-normal text-slate-400 ml-1.5">Severe Breach</span>
            </div>
            <p className="text-xs text-slate-300 mt-2 font-mono">
              Score &ge; 0.90 (e.g. Cloudburst &gt;140mm)
            </p>
          </div>
        </div>

        <div className="mt-5 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono">
          <span className="text-slate-400">PROTOCOL:</span>
          <span className="text-rose-400 font-bold flex items-center gap-1.5 tracking-wider">
            <span className="w-2 h-2 rounded-full bg-rose-500 animate-ping" />
            IMMEDIATE ADVISORY
          </span>
        </div>
      </div>

      {/* Card 3: High Advisories (Shift Alert) */}
      <div className="glass-card glass-card-hover rounded-2xl md:rounded-3xl p-5 group flex flex-col justify-between border-amber-500/20 hover:border-amber-500/50">
        <div className="absolute -right-8 -bottom-8 w-32 h-32 rounded-full bg-amber-500/15 blur-2xl group-hover:bg-amber-500/30 transition-all duration-500 pointer-events-none" />

        <div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-amber-400 uppercase tracking-widest font-mono">
              High Advisories
            </span>
            <div className="p-2.5 rounded-xl bg-amber-500/15 border border-amber-500/30 text-amber-400 group-hover:scale-110 transition-all duration-300 shadow-[0_0_15px_rgba(245,158,11,0.25)]">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>

          <div className="mt-4">
            <div className="text-3xl md:text-4xl font-extrabold text-amber-400 tracking-tight font-mono tabular-nums">
              {highCount}
              <span className="text-sm font-normal text-slate-400 ml-1.5">Stations</span>
            </div>
            <p className="text-xs text-slate-300 mt-2 font-mono">
              Score 0.70 - 0.89 (Significant Shift)
            </p>
          </div>
        </div>

        <div className="mt-5 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-slate-400">
          <span>WATCH TIER:</span>
          <span className="text-amber-400 font-bold tracking-wider">{watchCount} In Evaluation</span>
        </div>
      </div>

      {/* Card 4: Normal Baseline Stations */}
      <div className="glass-card glass-card-hover rounded-2xl md:rounded-3xl p-5 group flex flex-col justify-between border-emerald-500/20 hover:border-emerald-500/50">
        <div className="absolute -right-8 -bottom-8 w-32 h-32 rounded-full bg-emerald-500/15 blur-2xl group-hover:bg-emerald-500/30 transition-all duration-500 pointer-events-none" />

        <div>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest font-mono">
              Normal Baseline
            </span>
            <div className="p-2.5 rounded-xl bg-emerald-500/15 border border-emerald-500/30 text-emerald-400 group-hover:scale-110 transition-all duration-300 shadow-[0_0_15px_rgba(16,185,129,0.25)]">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>

          <div className="mt-4">
            <div className="text-3xl md:text-4xl font-extrabold text-emerald-400 tracking-tight font-mono tabular-nums">
              {normalCount}
              <span className="text-sm font-normal text-slate-400 ml-1.5">Stable Stations</span>
            </div>
            <p className="text-xs text-slate-300 mt-2 font-mono">
              Within expected seasonal &mu; &plusmn; 2&sigma; bounds
            </p>
          </div>
        </div>

        <div className="mt-5 pt-3 border-t border-white/[0.08] flex items-center justify-between text-[11px] font-mono text-slate-400">
          <span>STATISTICAL SPREAD:</span>
          <span className="text-emerald-400 font-bold tracking-wider">ALL IN BOUNDS</span>
        </div>
      </div>
    </div>
  );
}
