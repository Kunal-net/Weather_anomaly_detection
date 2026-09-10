import React from 'react';
import { CloudRain, Sun, Wind, CloudLightning, Activity, CloudSun, Zap, Waves } from 'lucide-react';

/**
 * AnimatedWeatherOrb:
 * Award-Winning 3D-styled meteorological display widget inspired by Awwwards & Apple Weather.
 * Dynamically renders custom choreographed weather physics matching the active station condition:
 * - Cloudburst / Extreme Rain: Layered storm cloud with animated lightning discharges & cascading raindrop streaks
 * - Heatwave: Pulsing corona sun with dual-ring rotating solar rays and thermal distortion wave
 * - Cyclone / Deep Depression: Atmospheric vortex spiral with sweeping wind streams and rotating radar scanline
 * - Baseline Normal: Floating tranquil cumulus cloud with sunbeams and ambient micro-particles
 */
export default function AnimatedWeatherOrb({
  anomalyType = 'Normal',
  severity = 'NORMAL',
  score = 0.18,
  compact = false,
}) {
  const isCritical = severity === 'CRITICAL';
  const isHigh = severity === 'HIGH';
  const isWatch = severity === 'WATCH';

  const typeLower = (anomalyType || '').toLowerCase();
  const isRain =
    typeLower.includes('rain') ||
    typeLower.includes('cloudburst') ||
    typeLower.includes('precipitation') ||
    typeLower.includes('storm');
  const isHeat =
    typeLower.includes('heat') ||
    typeLower.includes('temperature') ||
    typeLower.includes('warm');
  const isCyclone =
    typeLower.includes('depression') ||
    typeLower.includes('cyclone') ||
    typeLower.includes('wind') ||
    typeLower.includes('gale');

  // Calibrated atmospheric glow colors
  let ambientGlowClass = 'bg-emerald-500/25';
  let badgeColor = 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30';
  let dotColor = 'bg-emerald-400';

  if (isCritical) {
    ambientGlowClass = 'bg-rose-600/40 animate-pulse';
    badgeColor = 'bg-rose-500/20 text-rose-300 border-rose-500/40';
    dotColor = 'bg-rose-500 animate-ping';
  } else if (isHigh) {
    ambientGlowClass = 'bg-orange-500/35 animate-pulse-glow';
    badgeColor = 'bg-orange-500/20 text-orange-300 border-orange-500/40';
    dotColor = 'bg-orange-400';
  } else if (isWatch || isHeat) {
    ambientGlowClass = 'bg-amber-500/30 animate-pulse-glow';
    badgeColor = 'bg-amber-500/20 text-amber-300 border-amber-500/40';
    dotColor = 'bg-amber-400';
  }

  return (
    <div className={`relative flex flex-col items-center justify-center select-none ${compact ? 'min-h-[130px] p-2' : 'min-h-[190px] p-4'}`}>
      {/* 1. Ambient Aurora Atmospheric Glow Disc */}
      <div
        className={`absolute inset-0 m-auto w-32 h-32 md:w-40 md:h-40 rounded-full blur-3xl opacity-75 transition-all duration-700 pointer-events-none ${ambientGlowClass}`}
      />

      {/* 2. Precision Dual Orbit Rings */}
      <div className="absolute inset-0 m-auto w-32 h-32 md:w-40 md:h-40 rounded-full border border-dashed border-white/10 animate-[spin_24s_linear_infinite] pointer-events-none" />
      <div className="absolute inset-0 m-auto w-40 h-40 md:w-48 md:h-48 rounded-full border border-white/5 animate-[spin_40s_linear_infinite_reverse] pointer-events-none" />

      {/* 3. Floating 3D Meteorological Entity */}
      <div className="relative z-10 animate-float flex flex-col items-center justify-center">
        {/* SCENARIO 1: CLOUDBURST / EXTREME RAIN */}
        {isRain && (
          <div className="relative flex flex-col items-center">
            {/* Multi-layered Storm Cloud with Specular Rim */}
            <div className="relative z-20 p-4 rounded-3xl bg-gradient-to-b from-slate-700/80 via-slate-800/90 to-slate-950/95 backdrop-blur-xl border border-cyan-400/30 shadow-[0_12px_36px_rgba(6,182,212,0.25)]">
              <CloudRain className="w-12 h-12 md:w-14 md:h-14 text-cyan-300 filter drop-shadow-[0_0_12px_rgba(6,182,212,0.9)]" />
              {/* Lightning Discharge Flashes */}
              <div className="absolute -top-1.5 -right-1.5 p-1 bg-amber-400/20 border border-amber-400/40 rounded-full shadow-[0_0_10px_rgba(251,191,36,0.6)]">
                <CloudLightning className="w-4 h-4 text-amber-300 animate-ping" />
              </div>
            </div>

            {/* Cascading Animated Raindrop Streams */}
            <div className="absolute -bottom-7 flex gap-2.5 text-cyan-400 pointer-events-none">
              <span className="w-1 h-3.5 bg-gradient-to-b from-cyan-200 to-transparent rounded-full animate-rain-1" />
              <span className="w-1 h-4.5 bg-gradient-to-b from-cyan-300 to-transparent rounded-full animate-rain-2" />
              <span className="w-1 h-3.5 bg-gradient-to-b from-cyan-100 to-transparent rounded-full animate-rain-3" />
              <span className="w-1 h-4 bg-gradient-to-b from-cyan-400 to-transparent rounded-full animate-rain-1" />
              <span className="w-1 h-3 bg-gradient-to-b from-cyan-200 to-transparent rounded-full animate-rain-2" />
            </div>
          </div>
        )}

        {/* SCENARIO 2: EXTREME HEATWAVE */}
        {isHeat && !isRain && (
          <div className="relative flex items-center justify-center">
            {/* Outer Rotating Corona Rays */}
            <div className="absolute w-28 h-28 md:w-32 md:h-32 rounded-full border-2 border-dashed border-amber-400/40 animate-[spin_12s_linear_infinite]" />
            <div className="absolute w-36 h-36 rounded-full border border-orange-500/20 animate-[spin_18s_linear_infinite_reverse]" />

            {/* Shimmering Sun Core with Thermal Distortion */}
            <div className="relative z-20 p-4 rounded-full bg-gradient-to-br from-amber-300 via-orange-500 to-rose-600 shadow-[0_0_40px_rgba(249,115,22,0.6)] border border-amber-200/50 animate-heat-wave">
              <Sun className="w-12 h-12 md:w-14 md:h-14 text-white filter drop-shadow-[0_0_16px_rgba(251,191,36,1)]" />
            </div>
          </div>
        )}

        {/* SCENARIO 3: CYCLONE / DEEP DEPRESSION */}
        {isCyclone && !isRain && !isHeat && (
          <div className="relative flex items-center justify-center">
            {/* Atmospheric Vortex Sweep Radar */}
            <div className="absolute w-32 h-32 md:w-36 md:h-36 rounded-full border-2 border-indigo-500/30 border-t-cyan-400 animate-radar-sweep" />
            <div className="absolute w-28 h-28 rounded-full border border-dashed border-teal-400/40 animate-[spin_8s_linear_infinite]" />

            {/* Central Vortex Eye */}
            <div className="relative z-20 p-4 rounded-3xl bg-gradient-to-br from-indigo-950/90 via-slate-900/90 to-teal-950/90 border border-teal-400/40 shadow-[0_12px_36px_rgba(20,184,166,0.3)]">
              <Wind className="w-12 h-12 md:w-14 md:h-14 text-teal-300 filter drop-shadow-[0_0_12px_rgba(45,212,191,0.9)] animate-pulse" />
            </div>
          </div>
        )}

        {/* SCENARIO 4: TRANQUIL BASELINE NORMAL */}
        {!isRain && !isHeat && !isCyclone && (
          <div className="relative flex flex-col items-center">
            <div className="relative z-20 p-4 rounded-3xl bg-gradient-to-b from-slate-800/80 via-slate-900/90 to-slate-950/95 backdrop-blur-xl border border-emerald-400/30 shadow-[0_12px_36px_rgba(16,185,129,0.2)]">
              <CloudSun className="w-12 h-12 md:w-14 md:h-14 text-emerald-300 filter drop-shadow-[0_0_12px_rgba(16,185,129,0.8)]" />
            </div>
            {/* Ambient Peaceful Micro-Particles */}
            <div className="flex gap-2 mt-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400/80 animate-ping" />
              <span className="text-[10px] uppercase font-mono tracking-widest text-emerald-400 font-bold">
                Corridor In-Bounds
              </span>
            </div>
          </div>
        )}

        {/* Dynamic Condition Glass Pill */}
        <div className={`mt-4 px-3 py-1 rounded-full glass-pill flex items-center gap-2 border ${badgeColor} shadow-lg backdrop-blur-md`}>
          <span className={`w-2 h-2 rounded-full ${dotColor}`} />
          <span className="text-xs font-bold font-mono tracking-tight text-white uppercase">
            {anomalyType}
          </span>
          <span className="text-[10px] text-slate-300 font-mono font-semibold tabular-nums">
            [{(score * 100).toFixed(0)}%]
          </span>
        </div>
      </div>
    </div>
  );
}
