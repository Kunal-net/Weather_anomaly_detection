import React, { useState, useEffect } from 'react';
import {
  Activity,
  AlertTriangle,
  CheckCircle2,
  CloudRain,
  Compass,
  Gauge,
  Layers,
  Radio,
  Sliders,
  Sparkles,
  Thermometer,
  Wind,
} from 'lucide-react';
import { MOCK_LOCATIONS, MOCK_PREDICTION_RESPONSE } from './services/mockData';
import { fetchLocations, checkHealth } from './services/api';

export default function App() {
  const [locations, setLocations] = useState(MOCK_LOCATIONS);
  const [selectedCity, setSelectedCity] = useState('Bengaluru');
  const [systemHealth, setSystemHealth] = useState({ status: 'checking', model_loaded: true });
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    // Load monitored stations on startup
    fetchLocations().then((data) => {
      if (data && data.length > 0) setLocations(data);
    });
    checkHealth().then((h) => setSystemHealth(h));
  }, []);

  const selectedData = locations.find(
    (l) => (l.city || l.location).toLowerCase() === selectedCity.toLowerCase()
  ) || locations[0];

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

  const getSeverityBadgeClass = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-red-500/20 text-red-400 border-red-500/40';
      case 'HIGH':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/40';
      case 'WATCH':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      default:
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
    }
  };

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans">
      {/* 1. Command Center Navbar */}
      <header className="border-b border-slate-800 bg-[#0f172a]/90 backdrop-blur-md sticky top-0 z-50 px-6 py-3">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg shadow-cyan-500/20">
              <Radio className="w-6 h-6 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  AeroSense-AI
                </h1>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30">
                  SIH 2026
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Weather Anomaly Detection, Monitoring & Explainability Platform
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              <span className="text-slate-300 font-medium">Dual-Engine Active</span>
              <span className="text-slate-500">|</span>
              <span className="text-slate-400">Team ILLUMINATI</span>
            </div>

            <div className="flex items-center gap-2 text-xs px-3 py-1.5 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>Backend:</span>
              <span className={systemHealth.status === 'ok' ? 'text-emerald-400' : 'text-amber-400'}>
                {systemHealth.status === 'ok' ? 'Online' : 'Mock Mode'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* 2. Main Command Center View */}
      <main className="max-w-7xl mx-auto w-full px-6 py-6 space-y-6 flex-1">
        {/* Executive Summary Counters */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-sm">
            <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              Monitored Stations
            </div>
            <div className="text-3xl font-extrabold text-white mt-1">{locations.length}</div>
            <div className="text-xs text-slate-500 mt-1">Across 10 Indian climate zones</div>
          </div>

          <div className="bg-slate-900/80 border border-red-900/30 rounded-xl p-4 shadow-sm">
            <div className="text-xs font-semibold text-red-400 uppercase tracking-wider flex items-center justify-between">
              <span>Critical Alerts</span>
              <span className="w-2 h-2 rounded-full bg-red-500 animate-pulse"></span>
            </div>
            <div className="text-3xl font-extrabold text-red-400 mt-1">{criticalCount}</div>
            <div className="text-xs text-slate-500 mt-1">Score &ge; 0.90 (Immediate Hazard)</div>
          </div>

          <div className="bg-slate-900/80 border border-orange-900/30 rounded-xl p-4 shadow-sm">
            <div className="text-xs font-semibold text-orange-400 uppercase tracking-wider">
              High Advisories
            </div>
            <div className="text-3xl font-extrabold text-orange-400 mt-1">{highCount}</div>
            <div className="text-xs text-slate-500 mt-1">Score 0.70 - 0.89</div>
          </div>

          <div className="bg-slate-900/80 border border-emerald-900/30 rounded-xl p-4 shadow-sm">
            <div className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
              Normal Stations
            </div>
            <div className="text-3xl font-extrabold text-emerald-400 mt-1">{normalCount}</div>
            <div className="text-xs text-slate-500 mt-1">Within seasonal &plusmn;2&sigma; corridor</div>
          </div>
        </div>

        {/* City Selector Bar */}
        <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2 border-b border-slate-800">
          <div className="text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">
            Select Station:
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {locations.map((loc) => {
              const name = loc.city || loc.location;
              const sev = loc.severity || loc.current_severity;
              const isSelected = name.toLowerCase() === selectedCity.toLowerCase();
              return (
                <button
                  key={name}
                  onClick={() => setSelectedCity(name)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all duration-200 flex items-center gap-2 border ${
                    isSelected
                      ? 'bg-cyan-500/20 border-cyan-500 text-cyan-200 shadow-md shadow-cyan-500/20'
                      : 'bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <span>{name}</span>
                  <span
                    className={`w-2 h-2 rounded-full ${
                      sev === 'CRITICAL'
                        ? 'bg-red-500'
                        : sev === 'HIGH'
                        ? 'bg-orange-500'
                        : sev === 'WATCH'
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                  ></span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Selected Station Banner & Anomaly Spotlight */}
        {selectedData && (
          <div className="bg-gradient-to-r from-slate-900 via-slate-900/90 to-slate-800/80 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="space-y-2">
                <div className="flex items-center gap-3">
                  <h2 className="text-2xl font-black text-white tracking-tight">
                    {selectedData.city || selectedData.location}
                  </h2>
                  <span className="text-xs text-slate-400 font-mono">
                    [{selectedData.lat?.toFixed(2)}°N, {selectedData.lon?.toFixed(2)}°E]
                  </span>
                  <span
                    className={`px-3 py-1 rounded-full text-xs font-bold border ${getSeverityBadgeClass(
                      selectedData.severity || selectedData.current_severity
                    )}`}
                  >
                    {selectedData.severity || selectedData.current_severity}
                  </span>
                </div>
                <p className="text-sm text-slate-300 max-w-2xl leading-relaxed">
                  {selectedData.city === 'Bengaluru' || selectedData.location === 'Bengaluru'
                    ? MOCK_PREDICTION_RESPONSE.explanation
                    : `Station ${selectedData.city || selectedData.location} is being monitored across multivariable departures from historical baseline.`}
                </p>
              </div>

              {/* Anomaly Score Gauge Card */}
              <div className="bg-[#0b0f19]/80 border border-slate-800 rounded-xl p-4 flex items-center gap-4 min-w-[240px]">
                <div className="relative flex items-center justify-center w-16 h-16 rounded-full bg-slate-800/60 border border-slate-700">
                  <Gauge className="w-8 h-8 text-cyan-400" />
                </div>
                <div>
                  <div className="text-[11px] uppercase font-semibold text-slate-400 tracking-wider">
                    Calibrated Score
                  </div>
                  <div className="text-2xl font-black text-white font-mono">
                    {(selectedData.anomaly_score || selectedData.current_score)?.toFixed(2)}
                    <span className="text-xs text-slate-500 font-normal"> / 1.00</span>
                  </div>
                  <div className="text-[10px] text-slate-400">
                    Dual-Engine (Stat 40% + ML 60%)
                  </div>
                </div>
              </div>
            </div>

            {/* Current Weather Metric Cards */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 mt-6 pt-6 border-t border-slate-800/80">
              <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <Thermometer className="w-3.5 h-3.5 text-amber-400" />
                  <span>Temperature</span>
                </div>
                <div className="text-lg font-bold text-white mt-1">
                  {selectedData.temperature ?? 27.0}°C
                </div>
              </div>

              <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <CloudRain className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Rainfall</span>
                </div>
                <div className="text-lg font-bold text-white mt-1">
                  {selectedData.rainfall ?? 0.0} mm
                </div>
              </div>

              <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <Compass className="w-3.5 h-3.5 text-blue-400" />
                  <span>Pressure</span>
                </div>
                <div className="text-lg font-bold text-white mt-1">
                  {selectedData.pressure ?? 1010.0} hPa
                </div>
              </div>

              <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <Wind className="w-3.5 h-3.5 text-teal-400" />
                  <span>Wind Speed</span>
                </div>
                <div className="text-lg font-bold text-white mt-1">
                  {selectedData.wind_speed ?? 3.5} m/s
                </div>
              </div>

              <div className="bg-slate-800/40 rounded-lg p-3 border border-slate-800">
                <div className="flex items-center gap-1.5 text-xs text-slate-400">
                  <Layers className="w-3.5 h-3.5 text-indigo-400" />
                  <span>Humidity</span>
                </div>
                <div className="text-lg font-bold text-white mt-1">
                  {selectedData.relative_humidity ?? 65.0}%
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Member 4 Component Placement Area */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Map & Trends Slot (2 cols) */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center text-center min-h-[300px]">
              <div className="p-3 rounded-full bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 mb-3">
                <Radio className="w-8 h-8 animate-pulse" />
              </div>
              <h3 className="text-lg font-bold text-white">
                Member 4: India Leaflet Anomaly Map & Trends Area
              </h3>
              <p className="text-sm text-slate-400 max-w-md mt-1">
                This area is ready for <code>IndiaAnomalyMap.jsx</code> and{' '}
                <code>HistoricalTrends.jsx</code>. All dependencies, Tailwind styles, and API endpoints are wired and ready.
              </p>
            </div>
          </div>

          {/* Prediction Studio & Explainability Slot (1 col) */}
          <div className="space-y-6">
            <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex flex-col items-center justify-center text-center min-h-[300px]">
              <div className="p-3 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-400 mb-3">
                <Sliders className="w-8 h-8" />
              </div>
              <h3 className="text-lg font-bold text-white">
                Member 4: Prediction Studio & Explainability
              </h3>
              <p className="text-sm text-slate-400 max-w-sm mt-1">
                Ready for <code>PredictionStudio.jsx</code> sliders and{' '}
                <code>ExplainabilityCard.jsx</code>. Test real-time POST /predict under 15ms.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 bg-[#0f172a]/60 px-6 py-4 mt-auto text-xs text-slate-500 text-center">
        AeroSense-AI &copy; 2026 Team ILLUMINATI &bull; Smart India Hackathon &bull; Problem SIH1642 &bull; Weather Anomaly Detection & Monitoring Platform
      </footer>
    </div>
  );
}
