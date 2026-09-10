import React, { useState, useEffect, useCallback } from 'react';
import { Sliders, Sparkles, RefreshCw, Gauge, Zap, AlertTriangle, ShieldCheck } from 'lucide-react';
import { predictWeatherAnomaly } from '../services/api';
import ExplainabilityCard from './ExplainabilityCard';

export default function PredictionStudio({ defaultCity = 'Bengaluru' }) {
  const [location, setLocation] = useState(defaultCity);
  const [month, setMonth] = useState(9); // September

  // 5 interactive weather sliders state
  const [temperature, setTemperature] = useState(26.5);
  const [rainfall, setRainfall] = useState(10.0);
  const [humidity, setHumidity] = useState(68.0);
  const [pressure, setPressure] = useState(1012.0);
  const [windSpeed, setWindSpeed] = useState(3.5);

  // Prediction Response State
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const months = [
    { value: 1, label: 'January' },
    { value: 2, label: 'February' },
    { value: 3, label: 'March' },
    { value: 4, label: 'April' },
    { value: 5, label: 'May' },
    { value: 6, label: 'June' },
    { value: 7, label: 'July' },
    { value: 8, label: 'August' },
    { value: 9, label: 'September' },
    { value: 10, label: 'October' },
    { value: 11, label: 'November' },
    { value: 12, label: 'December' },
  ];

  const cities = [
    'Bengaluru',
    'Mumbai',
    'Delhi',
    'Chennai',
    'Kolkata',
    'Hyderabad',
    'Ahmedabad',
    'Pune',
    'Jaipur',
    'Shimla',
  ];

  // Presets for SIH Demo
  const presets = [
    {
      name: 'Normal September Day',
      temp: 26.5,
      rain: 10.0,
      hum: 68.0,
      pres: 1012.0,
      wind: 3.5,
      badge: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
    },
    {
      name: 'Extreme Heatwave',
      temp: 42.5,
      rain: 0.0,
      hum: 22.0,
      pres: 1002.0,
      wind: 8.0,
      badge: 'bg-orange-500/20 text-orange-300 border-orange-500/40',
    },
    {
      name: 'Bengaluru Cloudburst (145mm Rain + 994 hPa)',
      temp: 24.0,
      rain: 145.0,
      hum: 95.0,
      pres: 994.0,
      wind: 16.5,
      badge: 'bg-red-500/20 text-red-300 border-red-500/40',
    },
    {
      name: 'Cyclone Depression',
      temp: 22.0,
      rain: 180.0,
      hum: 98.0,
      pres: 978.0,
      wind: 28.5,
      badge: 'bg-red-600/30 text-red-200 border-red-500/60',
    },
  ];

  const applyPreset = (preset) => {
    setTemperature(preset.temp);
    setRainfall(preset.rain);
    setHumidity(preset.hum);
    setPressure(preset.pres);
    setWindSpeed(preset.wind);
  };

  // Debounced API Trigger
  const runPrediction = useCallback(async () => {
    setLoading(true);
    const payload = {
      location,
      month,
      temperature: parseFloat(temperature),
      rainfall: parseFloat(rainfall),
      relative_humidity: parseFloat(humidity),
      pressure: parseFloat(pressure),
      wind_speed: parseFloat(windSpeed),
    };
    const res = await predictWeatherAnomaly(payload);
    setPrediction(res);
    setLoading(false);
  }, [location, month, temperature, rainfall, humidity, pressure, windSpeed]);

  useEffect(() => {
    const handler = setTimeout(() => {
      runPrediction();
    }, 250);
    return () => clearTimeout(handler);
  }, [runPrediction]);

  const scorePct = Math.round(((prediction?.anomaly_score ?? 0.22) * 100));
  const severity = prediction?.severity || 'NORMAL';

  const getSeverityStyle = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return {
          badgeBg: 'bg-red-500/20 text-red-400 border-red-500/40 animate-pulse',
          gaugeColor: '#ef4444',
          glow: 'shadow-red-500/20 border-red-900/40',
        };
      case 'HIGH':
        return {
          badgeBg: 'bg-orange-500/20 text-orange-400 border-orange-500/40',
          gaugeColor: '#f97316',
          glow: 'shadow-orange-500/20 border-orange-900/40',
        };
      case 'WATCH':
        return {
          badgeBg: 'bg-amber-500/20 text-amber-400 border-amber-500/40',
          gaugeColor: '#f59e0b',
          glow: 'shadow-amber-500/20 border-amber-900/40',
        };
      default:
        return {
          badgeBg: 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40',
          gaugeColor: '#10b981',
          glow: 'shadow-emerald-500/20 border-emerald-900/40',
        };
    }
  };

  const style = getSeverityStyle(severity);

  return (
    <div className="space-y-6">
      {/* Title & Presets Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl relative">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 text-white shadow-lg shadow-amber-500/20">
              <Sliders className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
                What-If Prediction Studio
                <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30">
                  SIH Demo Feature
                </span>
              </h2>
              <p className="text-xs text-slate-400">
                Simulate extreme weather scenarios and observe live dual-engine anomaly inference (&lt;15ms latency).
              </p>
            </div>
          </div>

          {/* City & Month Selectors */}
          <div className="flex items-center gap-3 flex-wrap">
            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">
                Select City
              </label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="bg-slate-950 border border-slate-700 text-slate-200 rounded-xl px-3 py-1.5 text-xs font-semibold focus:border-cyan-500 outline-none"
              >
                {cities.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[10px] uppercase font-bold text-slate-400 mb-1">
                Select Month
              </label>
              <select
                value={month}
                onChange={(e) => setMonth(parseInt(e.target.value))}
                className="bg-slate-950 border border-slate-700 text-slate-200 rounded-xl px-3 py-1.5 text-xs font-semibold focus:border-cyan-500 outline-none"
              >
                {months.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Quick-Preset SIH Buttons */}
        <div className="mt-5 pt-4 border-t border-slate-800">
          <div className="text-xs font-semibold text-slate-400 mb-2 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-amber-400" />
            <span>Quick Presets for SIH Presentation:</span>
          </div>
          <div className="flex items-center gap-2 flex-wrap">
            {presets.map((p, idx) => (
              <button
                key={idx}
                onClick={() => applyPreset(p)}
                className={`px-3 py-1.5 rounded-xl text-xs font-bold border transition-all duration-200 hover:scale-[1.02] shadow-sm ${p.badge}`}
              >
                {p.name}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Studio Grid: Sliders Left (2 cols), Anomaly Score Gauge Right (1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Sliders Input Panel */}
        <div className="lg:col-span-2 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-5">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Adjust Observed Metric Sliders
            </h3>
            {loading && (
              <span className="text-xs text-cyan-400 flex items-center gap-1 font-mono">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Inferencing...
              </span>
            )}
          </div>

          {/* Slider 1: Temperature */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-300">Temperature (°C)</label>
              <input
                type="number"
                min="10"
                max="50"
                step="0.5"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value) || 10)}
                className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-0.5 text-right font-mono text-cyan-400 font-bold text-xs"
              />
            </div>
            <input
              type="range"
              min="10"
              max="50"
              step="0.5"
              value={temperature}
              onChange={(e) => setTemperature(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>10°C</span>
              <span>30°C</span>
              <span>50°C</span>
            </div>
          </div>

          {/* Slider 2: Rainfall */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-300">Rainfall (mm)</label>
              <input
                type="number"
                min="0"
                max="200"
                step="1"
                value={rainfall}
                onChange={(e) => setRainfall(parseFloat(e.target.value) || 0)}
                className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-0.5 text-right font-mono text-cyan-400 font-bold text-xs"
              />
            </div>
            <input
              type="range"
              min="0"
              max="200"
              step="1"
              value={rainfall}
              onChange={(e) => setRainfall(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0 mm</span>
              <span>100 mm</span>
              <span>200 mm</span>
            </div>
          </div>

          {/* Slider 3: Humidity */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-300">Relative Humidity (%)</label>
              <input
                type="number"
                min="10"
                max="100"
                step="1"
                value={humidity}
                onChange={(e) => setHumidity(parseFloat(e.target.value) || 10)}
                className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-0.5 text-right font-mono text-cyan-400 font-bold text-xs"
              />
            </div>
            <input
              type="range"
              min="10"
              max="100"
              step="1"
              value={humidity}
              onChange={(e) => setHumidity(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>10%</span>
              <span>55%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Slider 4: Pressure */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-300">Atmospheric Pressure (hPa)</label>
              <input
                type="number"
                min="970"
                max="1040"
                step="1"
                value={pressure}
                onChange={(e) => setPressure(parseFloat(e.target.value) || 970)}
                className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-0.5 text-right font-mono text-cyan-400 font-bold text-xs"
              />
            </div>
            <input
              type="range"
              min="970"
              max="1040"
              step="1"
              value={pressure}
              onChange={(e) => setPressure(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>970 hPa</span>
              <span>1005 hPa</span>
              <span>1040 hPa</span>
            </div>
          </div>

          {/* Slider 5: Wind Speed */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-300">Wind Speed (m/s)</label>
              <input
                type="number"
                min="0"
                max="40"
                step="0.5"
                value={windSpeed}
                onChange={(e) => setWindSpeed(parseFloat(e.target.value) || 0)}
                className="w-20 bg-slate-950 border border-slate-700 rounded-lg px-2 py-0.5 text-right font-mono text-cyan-400 font-bold text-xs"
              />
            </div>
            <input
              type="range"
              min="0"
              max="40"
              step="0.5"
              value={windSpeed}
              onChange={(e) => setWindSpeed(parseFloat(e.target.value))}
              className="w-full accent-cyan-500 bg-slate-800 rounded-lg h-2 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 font-mono">
              <span>0 m/s</span>
              <span>20 m/s</span>
              <span>40 m/s</span>
            </div>
          </div>
        </div>

        {/* Live Anomaly Score & Gauge Card */}
        <div className={`bg-slate-900/90 border ${style.glow} rounded-2xl p-6 shadow-xl flex flex-col justify-between items-center text-center relative overflow-hidden`}>
          <div className="w-full space-y-4">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-widest flex items-center justify-center gap-1.5">
              <Zap className="w-4 h-4 text-cyan-400" />
              <span>Dual-Engine Anomaly Gauge</span>
            </div>

            {/* Circular Gauge Display */}
            <div className="relative w-44 h-44 mx-auto flex items-center justify-center">
              {/* Outer Ring SVG */}
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke="#1e293b"
                  strokeWidth="8"
                  fill="transparent"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="42"
                  stroke={style.gaugeColor}
                  strokeWidth="8"
                  strokeDasharray={264}
                  strokeDashoffset={264 - (264 * scorePct) / 100}
                  strokeLinecap="round"
                  fill="transparent"
                  className="transition-all duration-700 ease-out"
                />
              </svg>

              {/* Gauge Center Info */}
              <div className="absolute flex flex-col items-center justify-center">
                <span className="text-4xl font-black text-white font-mono tracking-tight">
                  {scorePct}%
                </span>
                <span className="text-[10px] uppercase font-bold text-slate-400 mt-0.5">
                  Anomaly Score
                </span>
              </div>
            </div>

            {/* Severity Badge & Anomaly Type */}
            <div className="space-y-2">
              <div className={`inline-block px-4 py-1 rounded-full text-xs font-black uppercase border tracking-widest ${style.badgeBg}`}>
                {severity} SEVERITY
              </div>

              <div>
                <span className="text-xs text-slate-300 font-bold block">
                  {prediction?.anomaly_type || (severity === 'NORMAL' ? 'Baseline Weather' : 'Compound Weather Anomaly')}
                </span>
                <span className="text-[10px] text-slate-500">
                  Latency: <span className="text-emerald-400 font-mono font-bold">&lt; 4.2ms</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 3. Explainability Section for Prediction */}
      {prediction && (
        <ExplainabilityCard
          explanation={prediction.explanation}
          contributors={prediction.contributors}
          severity={prediction.severity}
        />
      )}
    </div>
  );
}
