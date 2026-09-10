import React from 'react';
import {
  Thermometer,
  CloudRain,
  Compass,
  Wind,
  Layers,
  Gauge,
  MapPin,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Minus,
} from 'lucide-react';

export default function StationDeepDive({ stationData, selectedCity, locations = [] }) {
  // Use stationData or fallback to looking up selectedCity in locations
  const data =
    stationData ||
    locations.find(
      (l) => (l.city || l.location).toLowerCase() === (selectedCity || 'bengaluru').toLowerCase()
    ) ||
    locations[0] || {
      city: 'Bengaluru',
      location: 'Bengaluru',
      lat: 12.97,
      lon: 77.59,
      elevation: '920m',
      temperature: 27.0,
      rainfall: 12.0,
      relative_humidity: 68.0,
      pressure: 1012.0,
      wind_speed: 3.8,
      severity: 'NORMAL',
      anomaly_score: 0.22,
    };

  const cityName = data.city || data.location || 'Bengaluru';
  const lat = data.lat ?? 12.97;
  const lon = data.lon ?? 77.59;
  const elevation = data.elevation || '920m ASL';
  const severity = data.severity || data.current_severity || 'NORMAL';
  const score = data.anomaly_score ?? data.current_score ?? 0.22;

  // Historical Seasonal Normals for comparison (Bengaluru September defaults if missing)
  const metrics = [
    {
      id: 'temperature',
      label: 'Temperature',
      icon: Thermometer,
      observed: data.temperature ?? 27.0,
      normal: data.normals?.temperature ?? 26.5,
      sigma: 2.2,
      unit: '°C',
      format: (val) => `${val.toFixed(1)}°C`,
    },
    {
      id: 'rainfall',
      label: 'Rainfall',
      icon: CloudRain,
      observed: data.rainfall ?? 12.0,
      normal: data.normals?.rainfall ?? 15.0,
      sigma: 18.0,
      unit: 'mm',
      format: (val) => `${val.toFixed(1)} mm`,
    },
    {
      id: 'relative_humidity',
      label: 'Humidity',
      icon: Layers,
      observed: data.relative_humidity ?? 68.0,
      normal: data.normals?.relative_humidity ?? 72.0,
      sigma: 10.0,
      unit: '%',
      format: (val) => `${val.toFixed(0)}%`,
    },
    {
      id: 'pressure',
      label: 'Pressure',
      icon: Compass,
      observed: data.pressure ?? 1012.0,
      normal: data.normals?.pressure ?? 1013.5,
      sigma: 4.5,
      unit: 'hPa',
      format: (val) => `${val.toFixed(1)} hPa`,
    },
    {
      id: 'wind_speed',
      label: 'Wind Speed',
      icon: Wind,
      observed: data.wind_speed ?? 3.8,
      normal: data.normals?.wind_speed ?? 3.2,
      sigma: 1.5,
      unit: 'm/s',
      format: (val) => `${val.toFixed(1)} m/s`,
    },
  ];

  const getSeverityBadge = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40 shadow-red-500/20';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40 shadow-orange-500/20';
      case 'WATCH':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40 shadow-amber-500/20';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40 shadow-emerald-500/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Header Banner & Location Identity */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-900 to-slate-800 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-2">
            <div className="flex items-center gap-3 flex-wrap">
              <div className="p-2.5 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
                <MapPin className="w-6 h-6" />
              </div>
              <h2 className="text-2xl md:text-3xl font-black text-white tracking-tight">
                {cityName} Station
              </h2>
              <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-300">
                [{lat.toFixed(2)}°N, {lon.toFixed(2)}°E]
              </span>
              <span className="text-xs font-mono px-2.5 py-1 rounded-md bg-slate-800 border border-slate-700 text-slate-400">
                Elev: {elevation}
              </span>
            </div>
            <p className="text-xs md:text-sm text-slate-400 max-w-3xl leading-relaxed">
              Detailed observation matrix comparing current readings against location- and season-specific historical baseline normals ($\mu \pm 2\sigma$).
            </p>
          </div>

          {/* Anomaly Score Badge */}
          <div className="flex items-center gap-4 bg-slate-950/80 border border-slate-800 rounded-xl p-4 shadow-inner">
            <div className="p-3 rounded-full bg-slate-800/80 border border-slate-700">
              <Gauge className="w-7 h-7 text-cyan-400" />
            </div>
            <div>
              <div className="text-[10px] uppercase font-bold text-slate-400 tracking-widest">
                Anomaly Severity
              </div>
              <div className="flex items-center gap-2 mt-0.5">
                <span className={`px-3 py-0.5 rounded-full text-xs font-extrabold border ${getSeverityBadge(severity)}`}>
                  {severity}
                </span>
                <span className="text-xl font-bold font-mono text-white">
                  {(score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 2. 5 Metric Gauge Cards with Expected Normals & Mini-Corridors */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {metrics.map((m) => {
          const Icon = m.icon;
          const delta = m.observed - m.normal;
          const isHighDelta = Math.abs(delta) > m.sigma * 1.5;
          const lowerBound = Math.max(0, m.normal - 2 * m.sigma);
          const upperBound = m.normal + 2 * m.sigma;
          
          // Calculate percentage position inside [mu - 3sigma, mu + 3sigma] window
          const minRange = Math.max(0, m.normal - 3 * m.sigma);
          const maxRange = m.normal + 3 * m.sigma;
          const totalSpan = maxRange - minRange || 1;
          const currentPct = Math.min(100, Math.max(0, ((m.observed - minRange) / totalSpan) * 100));
          const corridorStartPct = Math.min(100, Math.max(0, ((lowerBound - minRange) / totalSpan) * 100));
          const corridorWidthPct = Math.min(100 - corridorStartPct, Math.max(0, (((upperBound - lowerBound) / totalSpan) * 100)));

          return (
            <div
              key={m.id}
              className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-md hover:border-slate-700 transition-all duration-300 flex flex-col justify-between"
            >
              <div>
                {/* Metric Title & Icon */}
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-wider">
                    {m.label}
                  </span>
                  <div className="p-2 rounded-xl bg-slate-800 text-cyan-400 border border-slate-700">
                    <Icon className="w-4 h-4" />
                  </div>
                </div>

                {/* Observed Value */}
                <div className="text-2xl font-black text-white font-mono tracking-tight">
                  {m.format(m.observed)}
                </div>

                {/* Expected Normal & Delta */}
                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800 text-xs">
                  <div className="text-slate-400">
                    Expected Normal: <span className="text-slate-200 font-medium">{m.format(m.normal)}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between mt-1 text-xs">
                  <span className="text-slate-400">Departure ($\Delta$):</span>
                  <span
                    className={`font-mono font-bold flex items-center gap-0.5 ${
                      isHighDelta ? 'text-red-400' : delta > 0 ? 'text-amber-400' : 'text-emerald-400'
                    }`}
                  >
                    {delta > 0 ? '+' : ''}
                    {m.format(delta)}
                  </span>
                </div>
              </div>

              {/* Mini-Corridor Visual Progress Bar */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 space-y-1.5">
                <div className="flex items-center justify-between text-[10px] text-slate-500 font-mono">
                  <span>-2&sigma; ({lowerBound.toFixed(0)})</span>
                  <span>Normal Corridor</span>
                  <span>+2&sigma; ({upperBound.toFixed(0)})</span>
                </div>

                {/* Corridor Track */}
                <div className="relative w-full h-3 bg-slate-950 rounded-full border border-slate-800 overflow-hidden">
                  {/* Normal Band Highlight (mu +/- 2sigma) */}
                  <div
                    className="absolute top-0 bottom-0 bg-emerald-500/20 border-x border-emerald-500/40"
                    style={{
                      left: `${corridorStartPct}%`,
                      width: `${corridorWidthPct}%`,
                    }}
                  />
                  {/* Observed Pointer Indicator */}
                  <div
                    className={`absolute top-0 bottom-0 w-2.5 -ml-1 rounded-full shadow-md transition-all duration-500 ${
                      m.observed > upperBound || m.observed < lowerBound
                        ? 'bg-red-500 shadow-red-500/80 animate-pulse'
                        : 'bg-cyan-400 shadow-cyan-400/80'
                    }`}
                    style={{ left: `${currentPct}%` }}
                  />
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
