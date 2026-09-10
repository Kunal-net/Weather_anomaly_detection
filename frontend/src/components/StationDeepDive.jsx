import React from 'react';
import { Thermometer, CloudRain, Compass, Wind, Layers, Cpu, ShieldAlert, Sparkles, Activity } from 'lucide-react';
import AnimatedWeatherOrb from './AnimatedWeatherOrb';

const CLIMATE_ZONES = {
  Bengaluru: 'DECCAN PLATEAU',
  Delhi: 'INDO-GANGETIC PLAIN',
  Mumbai: 'WESTERN KONKAN COAST',
  Chennai: 'COROMANDEL COAST',
  Kolkata: 'GANGES DELTA',
  Hyderabad: 'TELANGANA PLATEAU',
  Ahmedabad: 'SEMI-ARID GUJARAT',
  Jaipur: 'THAR DESERT MARGIN',
  Shillong: 'KHASI HILLS HIGH-ALTITUDE',
  Srinagar: 'KASHMIR INTERMONTANE VALLEY',
  Shimla: 'WESTERN HIMALAYAN ALPINE',
  Bhubaneswar: 'EASTERN COASTAL PLAIN',
};

export default function StationDeepDive({ stationData, selectedCity, locations = [] }) {
  const data =
    stationData ||
    locations.find(
      (l) => (l.city || l.location).toLowerCase() === (selectedCity || 'bengaluru').toLowerCase()
    ) ||
    locations[0] || {
      city: 'Bengaluru',
      location: 'Bengaluru',
      lat: 12.9716,
      lon: 77.5946,
      elevation: '920m',
      temperature: 37.0,
      rainfall: 145.0,
      relative_humidity: 92.0,
      pressure: 994.0,
      wind_speed: 14.5,
      severity: 'CRITICAL',
      anomaly_score: 0.94,
    };

  const cityName = data.city || data.location || 'Bengaluru';
  const lat = (data.lat ?? 12.9716).toFixed(4);
  const lon = (data.lon ?? 77.5946).toFixed(4);
  const elevation = data.elevation ? String(data.elevation).toUpperCase() : '920M';
  const zone = CLIMATE_ZONES[cityName] || 'PENINSULAR INDIA';
  const severity = data.severity || data.current_severity || 'CRITICAL';
  const score = data.anomaly_score ?? data.current_score ?? 0.94;

  const isCritical = severity === 'CRITICAL';
  const isHigh = severity === 'HIGH';
  const isWatch = severity === 'WATCH';

  let hazardBadge = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
  let hazardText = 'HAZARD LEVEL 1 // NORMAL';
  if (isCritical) {
    hazardBadge = 'bg-red-500/20 text-red-300 border-red-500/50 shadow-[0_0_20px_rgba(239,68,68,0.3)] animate-pulse';
    hazardText = 'HAZARD LEVEL 4 // CRITICAL BREACH';
  } else if (isHigh) {
    hazardBadge = 'bg-orange-500/20 text-orange-300 border-orange-500/40 shadow-[0_0_15px_rgba(249,115,22,0.25)]';
    hazardText = 'HAZARD LEVEL 3 // HIGH ADVISORY';
  } else if (isWatch) {
    hazardBadge = 'bg-amber-500/20 text-amber-300 border-amber-500/40 shadow-[0_0_15px_rgba(245,158,11,0.2)]';
    hazardText = 'HAZARD LEVEL 2 // WATCH TIER';
  }

  // Derive anomaly type for AnimatedWeatherOrb
  let detectedType = 'Normal';
  if (data.rainfall > 80) detectedType = 'Cloudburst / Storm';
  else if (data.temperature > 38) detectedType = 'Severe Heatwave';
  else if (data.wind_speed > 16 || data.pressure < 990) detectedType = 'Cyclone Vortex';
  else if (isCritical || isHigh) detectedType = 'Compound Anomaly';

  // 5 Variable baseline metrics
  const metrics = [
    {
      id: 'temperature',
      label: 'TEMPERATURE',
      icon: Thermometer,
      observed: data.temperature ?? 37.0,
      normal: data.normals?.temperature ?? 27.1,
      sigma: 1.8,
      unit: '°C',
      format: (val) => `${val.toFixed(1)}°C`,
    },
    {
      id: 'rainfall',
      label: 'RAINFALL',
      icon: CloudRain,
      observed: data.rainfall ?? 145.0,
      normal: data.normals?.rainfall ?? 18.2,
      sigma: 23.4,
      unit: 'mm',
      format: (val) => `${val.toFixed(1)} mm`,
    },
    {
      id: 'pressure',
      label: 'PRESSURE',
      icon: Compass,
      observed: data.pressure ?? 994.0,
      normal: data.normals?.pressure ?? 1008.0,
      sigma: 3.2,
      unit: 'hPa',
      format: (val) => `${val.toFixed(1)} hPa`,
    },
    {
      id: 'wind_speed',
      label: 'WIND SPEED',
      icon: Wind,
      observed: data.wind_speed ?? 14.5,
      normal: data.normals?.wind_speed ?? 3.2,
      sigma: 1.5,
      unit: 'm/s',
      format: (val) => `${val.toFixed(1)} m/s`,
    },
    {
      id: 'relative_humidity',
      label: 'HUMIDITY',
      icon: Layers,
      observed: data.relative_humidity ?? 92.0,
      normal: data.normals?.relative_humidity ?? 68.0,
      sigma: 8.5,
      unit: '%',
      format: (val) => `${val.toFixed(0)}%`,
    },
  ];

  return (
    <div className="space-y-4 font-mono select-none">
      {/* 1. Station Hero Header Compartment with Integrated 3D Weather Orb */}
      <div className="glass-card rounded-2xl md:rounded-3xl p-5 md:p-6 flex flex-col lg:flex-row items-center justify-between gap-6">
        <div className="space-y-3 max-w-2xl">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="px-2.5 py-1 rounded-lg bg-cyan-500/10 border border-cyan-400/20 text-cyan-300 text-xs font-bold font-mono">
              STATION: {cityName.toUpperCase()}
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-slate-300 text-xs font-mono">
              ELEV: {elevation}
            </span>
            <span className="px-2.5 py-1 rounded-lg bg-white/[0.04] border border-white/[0.08] text-slate-300 text-xs font-mono">
              ZONE: {zone}
            </span>
          </div>

          <div>
            <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight font-sans">
              {cityName} Meteorological Observatory
            </h2>
            <p className="text-xs md:text-sm text-slate-400 mt-1 font-mono">
              COORDINATES: {lat}°N, {lon}°E &bull; LOCATION- &amp; SEASON-SPECIFIC DUAL-ENGINE STATISTICAL MATRIX
            </p>
          </div>

          <div className="flex items-center gap-3 pt-1">
            <div className={`px-3 py-1.5 rounded-xl border text-xs font-bold tracking-wider ${hazardBadge}`}>
              [ {hazardText} ]
            </div>
            <div className="px-3 py-1.5 rounded-xl border border-white/[0.08] bg-black/40 text-xs font-bold text-white tabular-nums">
              ANOMALY SCORE: <span className="text-cyan-400">{(score * 100).toFixed(0)}%</span>
            </div>
          </div>
        </div>

        {/* Integrated Animated Weather Hero Orb */}
        <div className="w-full lg:w-72 flex justify-center border-t lg:border-t-0 lg:border-l border-white/[0.08] pt-4 lg:pt-0 lg:pl-6">
          <AnimatedWeatherOrb
            anomalyType={detectedType}
            severity={severity}
            score={score}
            compact={true}
          />
        </div>
      </div>

      {/* 2. 5 Variable Baseline Corridor Instrument Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3.5">
        {metrics.map((m) => {
          const Icon = m.icon;
          const delta = m.observed - m.normal;
          const pctDeparture = m.normal !== 0 ? (delta / m.normal) * 100 : 0;
          const zScoreVal = delta / m.sigma;
          const zScore = zScoreVal.toFixed(1);
          const isBreach = Math.abs(zScoreVal) >= 2.0;

          const lowerLimit = m.normal - 2 * m.sigma;
          const upperLimit = m.normal + 2 * m.sigma;

          // Scale range for visualization [-4sigma to +4sigma around mu]
          const rangeMin = m.normal - 4 * m.sigma;
          const rangeMax = m.normal + 4 * m.sigma;
          const totalSpan = rangeMax - rangeMin || 1;

          const normalStartPct = Math.max(0, Math.min(100, ((lowerLimit - rangeMin) / totalSpan) * 100));
          const normalEndPct = Math.max(0, Math.min(100, ((upperLimit - rangeMin) / totalSpan) * 100));
          const normalWidthPct = normalEndPct - normalStartPct;

          const needlePct = Math.max(0, Math.min(100, ((m.observed - rangeMin) / totalSpan) * 100));

          return (
            <div
              key={m.id}
              className={`glass-card glass-card-hover rounded-2xl p-4 flex flex-col justify-between ${
                isBreach ? 'border-red-500/40 hover:border-red-500/60 shadow-[0_8px_24px_rgba(239,68,68,0.15)]' : ''
              }`}
            >
              <div>
                {/* Metric Header */}
                <div className="flex items-center justify-between text-[11px] text-slate-400 tracking-wider mb-2">
                  <span className="flex items-center gap-1.5 font-bold text-slate-200">
                    <Icon className="w-3.5 h-3.5 text-cyan-400" />
                    {m.label}
                  </span>
                  <span
                    className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                      isBreach
                        ? 'bg-red-500/20 text-red-400 border border-red-500/40 animate-pulse'
                        : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40'
                    }`}
                  >
                    {isBreach ? 'BREACH' : 'IN-BOUNDS'}
                  </span>
                </div>

                {/* Large Monospace Observed Value */}
                <div className="text-3xl font-extrabold text-white tabular-nums tracking-tight my-1.5">
                  {m.format(m.observed)}
                </div>

                {/* Statistical Details */}
                <div className="space-y-1 text-[10px] text-slate-300 border-t border-white/[0.08] pt-2.5 mt-2 tabular-nums">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Normal (&mu;):</span>
                    <span className="text-slate-200 font-bold">{m.format(m.normal)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Std Dev (&sigma;):</span>
                    <span className="text-slate-200">{m.format(m.sigma)}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Departure (&Delta;):</span>
                    <span className={isBreach ? 'text-red-400 font-bold' : 'text-emerald-400 font-bold'}>
                      {delta >= 0 ? '+' : ''}{m.format(delta)}
                    </span>
                  </div>
                  <div className="flex justify-between text-[9px]">
                    <span className="text-slate-500">Z-Score:</span>
                    <span className={isBreach ? 'text-red-400 font-bold' : 'text-cyan-400'}>
                      {zScoreVal > 0 ? '+' : ''}{zScore}&sigma; ({delta >= 0 ? '+' : ''}{pctDeparture.toFixed(1)}%)
                    </span>
                  </div>
                </div>
              </div>

              {/* Visual Corridor Bar Gauge */}
              <div className="mt-4 pt-2.5 border-t border-white/[0.08] space-y-1.5">
                <div className="flex items-center justify-between text-[8.5px] text-slate-400 tracking-tight font-mono">
                  <span>-2&sigma; ({lowerLimit.toFixed(1)})</span>
                  <span className="text-slate-500 font-bold">[&mu;&plusmn;2&sigma;]</span>
                  <span>+2&sigma; ({upperLimit.toFixed(1)})</span>
                </div>

                {/* Corridor Track */}
                <div className="relative w-full h-3.5 bg-black/60 rounded-full border border-white/[0.08] overflow-hidden">
                  {/* Normal Seasonal Bracket Range */}
                  <div
                    className="absolute top-0 bottom-0 bg-emerald-500/25 border-x border-emerald-400/50"
                    style={{
                      left: `${normalStartPct}%`,
                      width: `${normalWidthPct}%`,
                    }}
                  />

                  {/* Observed Value Precision Vertical Needle */}
                  <div
                    className={`absolute top-0 bottom-0 w-[2.5px] transition-all duration-500 ${
                      isBreach
                        ? 'bg-red-500 shadow-[0_0_10px_#ef4444]'
                        : 'bg-cyan-400 shadow-[0_0_8px_#06b6d4]'
                    }`}
                    style={{ left: `${needlePct}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 3. High-Density Tabular Observation Matrix */}
      <div className="glass-card rounded-2xl md:rounded-3xl p-5 space-y-3">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-400/20 text-cyan-400">
              <Cpu className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs md:text-sm font-bold text-white uppercase tracking-wider font-sans">
                Telemetry Observation Matrix &amp; Departure Analysis
              </h3>
              <p className="text-[10px] text-slate-400 font-mono">
                PRECISION MULTIVARIABLE FORENSIC COMPARISON
              </p>
            </div>
          </div>
          <span className="text-[10px] text-cyan-400 font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/10 border border-cyan-500/20">
            5/5 VARIABLES MONITORED
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs tabular-nums font-mono border-collapse">
            <thead>
              <tr className="bg-white/[0.02] border-b border-white/[0.08] text-[10px] text-slate-400 uppercase tracking-wider">
                <th className="p-3">VARIABLE</th>
                <th className="p-3">OBSERVED VALUE</th>
                <th className="p-3">EXPECTED NORMAL (&mu;)</th>
                <th className="p-3">STD DEV (&sigma;)</th>
                <th className="p-3">DEPARTURE (&Delta;)</th>
                <th className="p-3">Z-SCORE (&sigma;-DEV)</th>
                <th className="p-3">EVALUATION</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.05]">
              {metrics.map((m) => {
                const delta = m.observed - m.normal;
                const pctDeparture = m.normal !== 0 ? (delta / m.normal) * 100 : 0;
                const zScoreVal = delta / m.sigma;
                const zScore = zScoreVal.toFixed(2);
                const absZ = Math.abs(zScoreVal);

                let statusText = 'NORMAL';
                let statusBadge = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
                if (absZ >= 4.0) {
                  statusText = 'CRITICAL BREACH';
                  statusBadge = 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse';
                } else if (absZ >= 2.5) {
                  statusText = 'HIGH ADVISORY';
                  statusBadge = 'bg-orange-500/20 text-orange-400 border-orange-500/40';
                } else if (absZ >= 1.5) {
                  statusText = 'WATCH STATE';
                  statusBadge = 'bg-amber-500/20 text-amber-400 border-amber-500/40';
                }

                return (
                  <tr key={m.id} className="hover:bg-white/[0.03] transition-colors">
                    <td className="p-3 font-bold text-white">{m.label}</td>
                    <td className="p-3 text-slate-100 font-bold">{m.format(m.observed)}</td>
                    <td className="p-3 text-slate-300">{m.format(m.normal)}</td>
                    <td className="p-3 text-slate-400">{m.format(m.sigma)}</td>
                    <td className={`p-3 font-semibold ${absZ >= 2.0 ? 'text-red-400' : 'text-emerald-400'}`}>
                      {delta >= 0 ? '+' : ''}{m.format(delta)} ({delta >= 0 ? '+' : ''}{pctDeparture.toFixed(1)}%)
                    </td>
                    <td className={`p-3 font-bold ${absZ >= 2.0 ? 'text-red-400' : 'text-slate-300'}`}>
                      {zScoreVal > 0 ? '+' : ''}{zScore}&sigma;
                    </td>
                    <td className="p-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${statusBadge}`}>
                        {statusText}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
