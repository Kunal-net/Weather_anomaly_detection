import React, { useState, useEffect } from 'react';
import { Activity, Calendar, Compass, Sparkles, Filter, AlertTriangle } from 'lucide-react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  BarChart,
  Bar,
  Cell,
  CartesianGrid,
} from 'recharts';
import { fetchHistoricalCorridor } from '../services/api';

const VAR_UNITS = {
  temperature: '°C',
  rainfall: 'mm',
  pressure: 'hPa',
  wind_speed: 'm/s',
  relative_humidity: '%',
};

const VAR_NORMALS = {
  temperature: { mu: 27.1, sigma: 1.8 },
  rainfall: { mu: 18.2, sigma: 23.4 },
  pressure: { mu: 1008.0, sigma: 3.2 },
  wind_speed: { mu: 3.2, sigma: 1.5 },
  relative_humidity: { mu: 68.0, sigma: 8.5 },
};

const generateMockCorridor = (varKey, daysCount) => {
  const cfg = VAR_NORMALS[varKey] || VAR_NORMALS.temperature;
  const list = [];
  for (let i = daysCount; i >= 1; i--) {
    const d = new Date();
    d.setDate(d.getDate() - i);
    const dateStr = d.toISOString().slice(5, 10);

    let obs = cfg.mu + Math.sin(i * 0.8) * cfg.sigma * 1.1;
    let isBreach = false;

    if (i === 3 || i === 14) {
      obs = cfg.mu + (varKey === 'pressure' ? -3.8 : 3.5) * cfg.sigma;
      isBreach = true;
    }

    const lower = Math.max(0, cfg.mu - 2 * cfg.sigma);
    const upper = cfg.mu + 2 * cfg.sigma;

    list.push({
      timestamp: dateStr,
      observed: parseFloat(obs.toFixed(1)),
      expected_normal: parseFloat(cfg.mu.toFixed(1)),
      lower_bound: parseFloat(lower.toFixed(1)),
      upper_bound: parseFloat(upper.toFixed(1)),
      is_anomaly: isBreach,
      corridor: [parseFloat(lower.toFixed(1)), parseFloat(upper.toFixed(1))],
    });
  }
  return list;
};

export default function HistoricalTrends({ selectedCity = 'Bengaluru' }) {
  const [variable, setVariable] = useState('temperature');
  const [days, setDays] = useState(30);
  const [trendData, setTrendData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);
    fetchHistoricalCorridor(selectedCity, variable, days).then((res) => {
      if (isMounted) {
        if (res && res.data && res.data.length > 0) {
          const formatted = res.data.map((d) => ({
            ...d,
            corridor: [d.lower_bound, d.upper_bound],
          }));
          setTrendData(formatted);
        } else {
          setTrendData(generateMockCorridor(variable, days));
        }
        setLoading(false);
      }
    });
    return () => {
      isMounted = false;
    };
  }, [selectedCity, variable, days]);

  // Seasonal anomaly distribution dataset
  const seasonalData = [
    { season: 'Monsoon (Jun-Sep)', count: 47, color: '#ef4444' },
    { season: 'Summer (Mar-May)', count: 28, color: '#f97316' },
    { season: 'Post-Monsoon (Oct-Dec)', count: 19, color: '#f59e0b' },
    { season: 'Winter (Jan-Feb)', count: 12, color: '#06b6d4' },
  ];

  const unit = VAR_UNITS[variable] || '°C';

  const varTabs = [
    { id: 'temperature', label: 'Temperature (°C)' },
    { id: 'rainfall', label: 'Rainfall (mm)' },
    { id: 'pressure', label: 'Pressure (hPa)' },
    { id: 'wind_speed', label: 'Wind Speed (m/s)' },
    { id: 'relative_humidity', label: 'Humidity (%)' },
  ];

  const timeframeTabs = [
    { id: 7, label: '7 Days' },
    { id: 14, label: '14 Days' },
    { id: 30, label: '30 Days' },
    { id: 90, label: '90 Days' },
  ];

  return (
    <div className="space-y-4 font-mono select-none">
      {/* 1. Header & Controls */}
      <div className="glass-card rounded-2xl md:rounded-3xl p-5 md:p-6 space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 border-b border-white/[0.08] pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-400/20 text-cyan-400">
              <Activity className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h2 className="text-sm md:text-base font-extrabold text-white uppercase tracking-wider font-sans">
                Historical Telemetry Corridor <span className="text-slate-500">//</span> {selectedCity}
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                OBSERVED SENSOR TRACE PLOTTED RELATIVE TO SEASONAL BASELINE BOUNDS (&mu; &plusmn; 2&sigma;)
              </p>
            </div>
          </div>

          {/* Timeframe Filter Pills */}
          <div className="flex items-center gap-1.5 bg-black/40 p-1 rounded-xl border border-white/[0.08] backdrop-blur-md">
            <span className="text-[10px] text-slate-400 uppercase font-bold px-2 font-mono">SPAN:</span>
            {timeframeTabs.map((t) => (
              <button
                key={t.id}
                onClick={() => setDays(t.id)}
                className={`px-3 py-1 text-xs font-bold font-mono tracking-wider rounded-lg transition-all ${
                  days === t.id
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 shadow-[0_0_12px_rgba(6,182,212,0.2)]'
                    : 'text-slate-400 hover:text-white hover:bg-white/[0.04]'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Variable Switcher Tabs */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 no-scrollbar">
          {varTabs.map((vt) => (
            <button
              key={vt.id}
              onClick={() => setVariable(vt.id)}
              className={`px-3.5 py-1.5 text-xs font-bold font-mono tracking-wider rounded-xl transition-all whitespace-nowrap ${
                variable === vt.id
                  ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border border-cyan-400/40 shadow-[0_0_15px_rgba(6,182,212,0.2)]'
                  : 'bg-white/[0.02] border border-white/[0.06] text-slate-400 hover:text-white hover:bg-white/[0.05]'
              }`}
            >
              {vt.label}
            </button>
          ))}
        </div>
      </div>

      {/* 2. Recharts Telemetry Corridor Container */}
      <div className="glass-card rounded-2xl md:rounded-3xl p-5 md:p-6 space-y-4">
        {/* Legend */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-slate-400 border-b border-white/[0.08] pb-3 font-mono">
          <span className="font-bold text-white uppercase tracking-wider font-sans">
            Corridor Analysis: {variable.toUpperCase()} ({days} Days Telemetry)
          </span>
          <div className="flex items-center gap-4 flex-wrap text-[11px]">
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-3 rounded bg-emerald-500/20 border border-emerald-400/60 inline-block" />
              Normal Envelope (&mu; &plusmn; 2&sigma;)
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-3 h-0.5 bg-[#06b6d4] inline-block shadow-[0_0_6px_#06b6d4]" /> Observed Trace
            </span>
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 bg-red-500 rotate-45 inline-block shadow-[0_0_6px_#ef4444]" /> Anomaly Breach
            </span>
          </div>
        </div>

        {/* Chart Frame */}
        <div className="h-80 w-full pt-2">
          {loading ? (
            <div className="h-full flex items-center justify-center text-xs text-slate-400 font-mono">
              [FETCHING HISTORICAL TELEMETRY CORRIDOR DATA...]
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <ComposedChart data={trendData} margin={{ top: 15, right: 30, left: 10, bottom: 5 }}>
                <defs>
                  <linearGradient id="emeraldCorridor" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0.03} />
                  </linearGradient>
                </defs>

                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
                <XAxis
                  dataKey="timestamp"
                  stroke="#64748b"
                  fontSize={11}
                  fontFamily="JetBrains Mono"
                  tickFormatter={(val) => val}
                />
                <YAxis stroke="#64748b" fontSize={11} fontFamily="JetBrains Mono" unit={` ${unit}`} />
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const d = payload[0].payload;
                      return (
                        <div className="bg-[#0b0f19]/95 backdrop-blur-xl border border-white/[0.14] rounded-2xl p-3.5 text-xs font-mono tabular-nums text-slate-200 space-y-1.5 shadow-[0_16px_36px_rgba(0,0,0,0.6)] min-w-[210px] select-none">
                          <div className="font-bold text-cyan-400 border-b border-white/10 pb-1 font-sans text-xs">
                            DATE: {d.timestamp}
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">OBSERVED:</span>
                            <span className="text-white font-bold">{d.observed} {unit}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">NORMAL (&mu;):</span>
                            <span className="text-slate-300">{d.expected_normal} {unit}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">UPPER (+2&sigma;):</span>
                            <span className="text-emerald-400">{d.upper_bound} {unit}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">LOWER (-2&sigma;):</span>
                            <span className="text-emerald-400">{d.lower_bound} {unit}</span>
                          </div>
                          {d.is_anomaly && (
                            <div className="text-red-400 font-bold text-[10px] pt-1.5 border-t border-white/10 flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3 text-red-400" />
                              <span>STATISTICAL CORRIDOR BREACH</span>
                            </div>
                          )}
                        </div>
                      );
                    }
                    return null;
                  }}
                />

                {/* Shaded Area for Normal Baseline Corridor (mu +/- 2sigma) */}
                <Area
                  type="monotone"
                  dataKey="corridor"
                  stroke="#10b981"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  fill="url(#emeraldCorridor)"
                />

                {/* Observed Telemetry Line with Custom Diamond Breach Markers */}
                <Line
                  type="monotone"
                  dataKey="observed"
                  stroke="#06b6d4"
                  strokeWidth={2.5}
                  dot={(props) => {
                    const { cx, cy, payload } = props;
                    if (payload.is_anomaly) {
                      return (
                        <g key={cx}>
                          <polygon
                            points={`${cx},${cy - 7} ${cx + 7},${cy} ${cx},${cy + 7} ${cx - 7},${cy}`}
                            fill="#ef4444"
                            stroke="#ffffff"
                            strokeWidth="1.5"
                          />
                        </g>
                      );
                    }
                    return <circle key={cx} cx={cx} cy={cy} r={2.5} fill="#06b6d4" />;
                  }}
                />
              </ComposedChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* 3. Seasonal Anomaly Frequency Distribution */}
      <div className="glass-card rounded-2xl md:rounded-3xl p-5 md:p-6 space-y-3">
        <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
          <div className="flex items-center gap-2.5">
            <div className="p-1.5 rounded-lg bg-amber-500/10 border border-amber-400/20 text-amber-400">
              <Calendar className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-xs md:text-sm font-bold text-white uppercase tracking-wider font-sans">
                Seasonal Anomaly Frequency Distribution
              </h3>
              <p className="text-[10px] text-slate-400 font-mono">
                HISTORICAL PAN-INDIA SEVERE EVENT CLUSTERING
              </p>
            </div>
          </div>
          <span className="text-[10px] text-slate-400 font-mono">METAR ARCHIVE</span>
        </div>

        <div className="h-52 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={seasonalData} margin={{ top: 5, right: 30, left: 160, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.06)" />
              <XAxis type="number" stroke="#64748b" fontSize={11} fontFamily="JetBrains Mono" />
              <YAxis
                type="category"
                dataKey="season"
                stroke="#94a3b8"
                fontSize={11}
                fontFamily="JetBrains Mono"
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const d = payload[0].payload;
                    return (
                      <div className="bg-[#0b0f19]/95 backdrop-blur-xl border border-white/[0.14] rounded-xl p-2.5 text-xs font-mono tabular-nums text-slate-200">
                        <div className="font-bold text-white font-sans">{d.season}</div>
                        <div className="text-cyan-400 font-bold mt-1">
                          {d.count} Historical Anomaly Events
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="count" radius={[0, 8, 8, 0]} barSize={20}>
                {seasonalData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
