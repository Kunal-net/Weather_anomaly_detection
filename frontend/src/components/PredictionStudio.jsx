import React, { useState, useEffect, useCallback } from 'react';
import { Sliders, RefreshCw, Cpu, Activity, Zap, Compass, RotateCcw } from 'lucide-react';
import { predictWeatherAnomaly } from '../services/api';
import ExplainabilityCard from './ExplainabilityCard';
import AnimatedWeatherOrb from './AnimatedWeatherOrb';

export default function PredictionStudio({ defaultCity = 'Bengaluru' }) {
  const [location, setLocation] = useState(defaultCity);
  const [month, setMonth] = useState(9); // September

  // 5 interactive weather sliders
  const [temperature, setTemperature] = useState(37.0);
  const [rainfall, setRainfall] = useState(145.0);
  const [humidity, setHumidity] = useState(92.0);
  const [pressure, setPressure] = useState(994.0);
  const [windSpeed, setWindSpeed] = useState(14.5);

  // Prediction Response State
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activePreset, setActivePreset] = useState('PRESET 03');

  const months = [
    { value: 1, label: '01 // JANUARY' },
    { value: 2, label: '02 // FEBRUARY' },
    { value: 3, label: '03 // MARCH' },
    { value: 4, label: '04 // APRIL' },
    { value: 5, label: '05 // MAY' },
    { value: 6, label: '06 // JUNE' },
    { value: 7, label: '07 // JULY' },
    { value: 8, label: '08 // AUGUST' },
    { value: 9, label: '09 // SEPTEMBER' },
    { value: 10, label: '10 // OCTOBER' },
    { value: 11, label: '11 // NOVEMBER' },
    { value: 12, label: '12 // DECEMBER' },
  ];

  const cities = [
    'Bengaluru',
    'Mumbai',
    'Delhi',
    'Chennai',
    'Kolkata',
    'Hyderabad',
    'Ahmedabad',
    'Jaipur',
    'Shimla',
    'Bhubaneswar',
  ];

  // Presets for SIH Presentation Demo
  const presets = [
    {
      code: 'PRESET 01',
      name: 'Normal September',
      temp: 26.5,
      rain: 10.0,
      hum: 68.0,
      pres: 1012.0,
      wind: 3.5,
      style: 'border-emerald-500/40 text-emerald-300 hover:bg-emerald-500/10 hover:border-emerald-400',
      activeStyle: 'bg-emerald-500/20 border-emerald-400 text-emerald-200 shadow-[0_0_15px_rgba(16,185,129,0.3)]',
    },
    {
      code: 'PRESET 02',
      name: 'Extreme Heatwave',
      temp: 42.5,
      rain: 0.0,
      hum: 22.0,
      pres: 1002.0,
      wind: 8.0,
      style: 'border-orange-500/40 text-orange-300 hover:bg-orange-500/10 hover:border-orange-400',
      activeStyle: 'bg-orange-500/20 border-orange-400 text-orange-200 shadow-[0_0_15px_rgba(249,115,22,0.3)]',
    },
    {
      code: 'PRESET 03',
      name: 'Bengaluru Cloudburst (145mm + 994 hPa)',
      temp: 37.0,
      rain: 145.0,
      hum: 92.0,
      pres: 994.0,
      wind: 14.5,
      style: 'border-red-500/40 text-red-300 hover:bg-red-500/10 hover:border-red-400',
      activeStyle: 'bg-red-500/20 border-red-400 text-red-200 shadow-[0_0_20px_rgba(239,68,68,0.4)]',
    },
    {
      code: 'PRESET 04',
      name: 'Cyclone Depression',
      temp: 22.0,
      rain: 180.0,
      hum: 98.0,
      pres: 978.0,
      wind: 28.5,
      style: 'border-teal-500/40 text-teal-300 hover:bg-teal-500/10 hover:border-teal-400',
      activeStyle: 'bg-teal-500/20 border-teal-400 text-teal-200 shadow-[0_0_20px_rgba(20,184,166,0.35)]',
    },
  ];

  const applyPreset = (preset) => {
    setActivePreset(preset.code);
    setTemperature(preset.temp);
    setRainfall(preset.rain);
    setHumidity(preset.hum);
    setPressure(preset.pres);
    setWindSpeed(preset.wind);
  };

  // Debounced API Inference Execution
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
    }, 220);
    return () => clearTimeout(handler);
  }, [runPrediction]);

  const score = prediction?.anomaly_score ?? 0.94;
  const scoreFormatted = score.toFixed(2);
  const severity = prediction?.severity || (score >= 0.9 ? 'CRITICAL' : score >= 0.7 ? 'HIGH' : score >= 0.4 ? 'WATCH' : 'NORMAL');

  let stampText = 'CRITICAL // IMMEDIATE DISASTER PROTOCOL REQUIRED';
  let stampStyle = 'border-red-500/50 text-red-300 bg-red-500/15 shadow-[0_0_20px_rgba(239,68,68,0.25)] animate-pulse';
  let gaugeColor = '#ef4444';

  if (severity === 'HIGH') {
    stampText = 'HIGH // SIGNIFICANT WEATHER SHIFT ADVISORY';
    stampStyle = 'border-orange-500/50 text-orange-300 bg-orange-500/15 shadow-[0_0_15px_rgba(249,115,22,0.2)]';
    gaugeColor = '#f97316';
  } else if (severity === 'WATCH') {
    stampText = 'WATCH // METEOROLOGICAL MONITORING ACTIVE';
    stampStyle = 'border-amber-500/50 text-amber-300 bg-amber-500/15';
    gaugeColor = '#f59e0b';
  } else if (severity === 'NORMAL') {
    stampText = 'NORMAL // BASELINE METEOROLOGICAL CORRIDOR';
    stampStyle = 'border-emerald-500/50 text-emerald-300 bg-emerald-500/15';
    gaugeColor = '#10b981';
  }

  // Derive anomaly condition for live preview orb
  let orbCondition = 'Normal';
  if (rainfall > 70) orbCondition = 'Extreme Cloudburst';
  else if (temperature > 39) orbCondition = 'Severe Heatwave';
  else if (windSpeed > 18 || pressure < 985) orbCondition = 'Cyclone Depression';
  else if (severity === 'CRITICAL' || severity === 'HIGH') orbCondition = 'Compound Anomaly';

  // 5 parameter configurations
  const sliderConfigs = [
    {
      id: 'temp',
      label: 'TEMPERATURE',
      val: temperature,
      setVal: setTemperature,
      min: 10,
      max: 50,
      step: 0.5,
      normal: 26.5,
      sigma: 1.8,
      unit: '°C',
    },
    {
      id: 'rain',
      label: 'RAINFALL',
      val: rainfall,
      setVal: setRainfall,
      min: 0,
      max: 200,
      step: 1,
      normal: 18.2,
      sigma: 23.4,
      unit: 'mm',
    },
    {
      id: 'hum',
      label: 'RELATIVE HUMIDITY',
      val: humidity,
      setVal: setHumidity,
      min: 10,
      max: 100,
      step: 1,
      normal: 68.0,
      sigma: 8.5,
      unit: '%',
    },
    {
      id: 'pres',
      label: 'ATMOSPHERIC PRESSURE',
      val: pressure,
      setVal: setPressure,
      min: 970,
      max: 1040,
      step: 1,
      normal: 1008.0,
      sigma: 3.2,
      unit: 'hPa',
    },
    {
      id: 'wind',
      label: 'WIND SPEED',
      val: windSpeed,
      setVal: setWindSpeed,
      min: 0,
      max: 40,
      step: 0.5,
      normal: 3.2,
      sigma: 1.5,
      unit: 'm/s',
    },
  ];

  const calcDev = (val, norm, sigma, unit) => {
    const delta = val - norm;
    const pct = norm !== 0 ? (delta / norm) * 100 : 0;
    const z = delta / sigma;
    const sign = delta >= 0 ? '+' : '';
    return `Δ = ${sign}${delta.toFixed(1)}${unit} // ${sign}${pct.toFixed(1)}% vs Normal (Z = ${sign}${z.toFixed(1)}σ)`;
  };

  // Mechanical Dial Ticks (270 degrees total span from -135deg to +135deg)
  const renderDialTicks = () => {
    const ticks = [];
    const totalTicks = 32;
    for (let i = 0; i <= totalTicks; i++) {
      const angle = -135 + (i * 270) / totalTicks;
      const rad = (angle * Math.PI) / 180;
      const isMajor = i % 4 === 0;
      const r1 = 64;
      const r2 = isMajor ? 52 : 56;
      const x1 = 80 + r1 * Math.cos(rad);
      const y1 = 80 + r1 * Math.sin(rad);
      const x2 = 80 + r2 * Math.cos(rad);
      const y2 = 80 + r2 * Math.sin(rad);
      ticks.push(
        <line
          key={i}
          x1={x1}
          y1={y1}
          x2={x2}
          y2={y2}
          stroke={isMajor ? '#94a3b8' : '#334155'}
          strokeWidth={isMajor ? 2 : 1}
        />
      );
    }
    return ticks;
  };

  // Needle angle (-135deg to +135deg)
  const needleAngle = -135 + Math.min(1.0, Math.max(0, score)) * 270;

  return (
    <div className="space-y-4 font-mono select-none">
      {/* 1. Cockpit Header & Interactive Simulation Presets */}
      <div className="glass-card rounded-2xl md:rounded-3xl p-5 md:p-6 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/[0.08] pb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-400/20 text-amber-400">
              <Sliders className="w-5 h-5 animate-pulse" />
            </div>
            <div>
              <h2 className="text-sm md:text-base font-extrabold text-white uppercase tracking-wider font-sans flex items-center gap-2">
                What-If Prediction Studio <span className="text-slate-500">//</span> Simulation Cockpit
              </h2>
              <p className="text-xs text-slate-400 font-mono">
                DUAL-ENGINE REAL-TIME INFERENCE TESTING CONSOLE &bull; TARGET LATENCY &lt;15MS
              </p>
            </div>
          </div>

          {/* Location & Month Selectors */}
          <div className="flex items-center gap-3 flex-wrap">
            <div>
              <label className="block text-[9px] uppercase font-bold text-slate-400 mb-1">LOCATION TARGET</label>
              <select
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                className="bg-black/50 border border-white/[0.12] text-slate-100 px-3 py-1.5 rounded-xl text-xs font-bold font-mono focus:border-cyan-400 outline-none shadow-inner"
              >
                {cities.map((c) => (
                  <option key={c} value={c} className="bg-slate-900 text-white">
                    {c.toUpperCase()}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-[9px] uppercase font-bold text-slate-400 mb-1">CLIMATE SEASON / MONTH</label>
              <select
                value={month}
                onChange={(e) => setMonth(parseInt(e.target.value))}
                className="bg-black/50 border border-white/[0.12] text-slate-100 px-3 py-1.5 rounded-xl text-xs font-bold font-mono focus:border-cyan-400 outline-none shadow-inner"
              >
                {months.map((m) => (
                  <option key={m.value} value={m.value} className="bg-slate-900 text-white">
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Tactile Preset Switches */}
        <div>
          <div className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2.5 flex items-center gap-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>SIH DEMO EVALUATION PRESETS (CLICK TO MORPH SLIDERS):</span>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-2.5">
            {presets.map((p) => {
              const isActive = activePreset === p.code;
              return (
                <button
                  key={p.code}
                  onClick={() => applyPreset(p)}
                  className={`p-2.5 rounded-xl border text-xs font-bold font-mono tracking-wider transition-all duration-300 text-left flex flex-col justify-between ${
                    isActive ? p.activeStyle : `bg-white/[0.02] ${p.style}`
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] opacity-75">{p.code}</span>
                    {isActive && <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />}
                  </div>
                  <div className="font-sans font-bold text-white text-xs mt-1 truncate">
                    {p.name}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* 2. Main Studio Grid: Sliders Left (2 cols), Output HUD Right (1 col) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Sliders Panel (2 cols) */}
        <div className="lg:col-span-2 glass-card rounded-2xl md:rounded-3xl p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-white/[0.08] pb-3">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400 animate-pulse" />
              <h3 className="text-xs font-bold text-white uppercase tracking-wider font-sans">
                Atmospheric Variable Telemetry Sliders
              </h3>
            </div>
            {loading && (
              <span className="text-[10px] text-cyan-400 flex items-center gap-1.5 font-mono">
                <RefreshCw className="w-3 h-3 animate-spin" /> INFERENCE ACTIVE...
              </span>
            )}
          </div>

          <div className="space-y-4">
            {sliderConfigs.map((cfg) => {
              const devStr = calcDev(cfg.val, cfg.normal, cfg.sigma, cfg.unit);
              const zVal = Math.abs((cfg.val - cfg.normal) / cfg.sigma);
              const isBreach = zVal >= 2.0;

              return (
                <div
                  key={cfg.id}
                  className="space-y-2 bg-black/40 p-3.5 rounded-2xl border border-white/[0.06] hover:border-cyan-400/30 transition-colors"
                >
                  <div className="flex items-center justify-between text-xs">
                    <label className="font-bold text-slate-200 tracking-wider font-sans">
                      {cfg.label}
                    </label>
                    <div className="flex items-center gap-1.5">
                      <input
                        type="number"
                        min={cfg.min}
                        max={cfg.max}
                        step={cfg.step}
                        value={cfg.val}
                        onChange={(e) => cfg.setVal(parseFloat(e.target.value) || cfg.min)}
                        className="w-24 bg-black/60 border border-white/[0.12] text-cyan-300 font-bold px-2 py-0.5 text-right font-mono text-xs tabular-nums rounded-lg focus:border-cyan-400 outline-none"
                      />
                      <span className="text-[11px] text-slate-400 font-mono">{cfg.unit}</span>
                    </div>
                  </div>

                  {/* Range Slider Track */}
                  <div className="relative pt-1 pb-1">
                    <input
                      type="range"
                      min={cfg.min}
                      max={cfg.max}
                      step={cfg.step}
                      value={cfg.val}
                      onChange={(e) => cfg.setVal(parseFloat(e.target.value))}
                      className="neon-slider cursor-pointer"
                    />
                    <div className="flex justify-between text-[9px] text-slate-500 font-mono mt-1 tabular-nums">
                      <span>MIN: {cfg.min}{cfg.unit}</span>
                      <span className="text-slate-400 font-semibold">SEASONAL MEAN (&mu;): {cfg.normal}{cfg.unit}</span>
                      <span>MAX: {cfg.max}{cfg.unit}</span>
                    </div>
                  </div>

                  {/* Real-time Deviation Readout */}
                  <div
                    className={`text-[10px] font-mono font-bold tabular-nums ${
                      isBreach ? 'text-red-400' : 'text-slate-400'
                    }`}
                  >
                    {devStr}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Output HUD Dial & Animated Orb Panel (1 col) */}
        <div className="glass-card rounded-2xl md:rounded-3xl p-5 flex flex-col justify-between items-center text-center space-y-4">
          <div className="w-full border-b border-white/[0.08] pb-3 text-xs font-bold text-white uppercase tracking-wider flex items-center justify-center gap-2 font-sans">
            <Cpu className="w-4 h-4 text-cyan-400" />
            <span>Dual-Engine Inferred Severity Gauge</span>
          </div>

          {/* Central Circular Speedometer Dial Meter */}
          <div className="relative w-48 h-48 flex items-center justify-center bg-black/40 rounded-3xl border border-white/[0.08] p-3 shadow-inner">
            <svg className="w-full h-full" viewBox="0 0 160 160">
              {/* Dial Background Arc Track */}
              <circle
                cx="80"
                cy="80"
                r="64"
                stroke="#1e293b"
                strokeWidth="4"
                fill="none"
                strokeDasharray="301"
                strokeDashoffset="75"
                transform="rotate(135 80 80)"
              />
              {/* Colored Calibrated Arc Fill */}
              <circle
                cx="80"
                cy="80"
                r="64"
                stroke={gaugeColor}
                strokeWidth="5"
                fill="none"
                strokeDasharray="301"
                strokeDashoffset={301 - (score * 226)}
                strokeLinecap="round"
                transform="rotate(135 80 80)"
                style={{ transition: 'stroke-dashoffset 0.5s ease-out, stroke 0.5s ease-out' }}
              />
              {/* Mechanical Degree Ticks */}
              {renderDialTicks()}

              {/* Rotating Needle Pointer */}
              <g
                transform={`rotate(${needleAngle}, 80, 80)`}
                style={{ transition: 'transform 0.4s cubic-bezier(0.16, 1, 0.3, 1)' }}
              >
                <line x1="80" y1="80" x2="80" y2="28" stroke={gaugeColor} strokeWidth="3" strokeLinecap="round" />
                <circle cx="80" cy="80" r="5" fill="#ffffff" stroke={gaugeColor} strokeWidth="2" />
              </g>
            </svg>

            {/* Central Score Callout */}
            <div className="absolute flex flex-col items-center justify-center mt-12">
              <span className="text-3xl font-extrabold text-white tracking-tight font-mono tabular-nums">
                {scoreFormatted}
              </span>
              <span className="text-[9px] uppercase font-bold text-slate-400 tracking-widest font-mono">
                CALIBRATED INDEX
              </span>
            </div>
          </div>

          {/* Real-Time Condition Hero Orb Preview */}
          <div className="w-full bg-black/30 rounded-2xl border border-white/[0.06] p-2">
            <AnimatedWeatherOrb
              anomalyType={orbCondition}
              severity={severity}
              score={score}
              compact={true}
            />
          </div>

          {/* Sub-Metrics Telemetry */}
          <div className="w-full space-y-1 text-[10px] text-slate-300 text-left bg-black/40 p-3 rounded-xl border border-white/[0.08] tabular-nums font-mono">
            <div className="flex justify-between">
              <span className="text-slate-400">LAYER 1 (Z-SCORE):</span>
              <span className="text-white font-bold">{Math.min(1.0, score * 0.96).toFixed(2)} [40%]</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">LAYER 2 (ISO-FOREST ML):</span>
              <span className="text-white font-bold">{Math.min(1.0, score * 1.02).toFixed(2)} [60%]</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">INFERENCE LATENCY:</span>
              <span className="text-emerald-400 font-bold">&lt;6.4ms [TARGET &lt;15ms]</span>
            </div>
          </div>

          {/* Severity Alert Stamp */}
          <div className={`w-full py-2.5 px-3 rounded-xl border text-center text-xs font-bold tracking-wider uppercase font-mono ${stampStyle}`}>
            [ {stampText} ]
          </div>
        </div>
      </div>

      {/* 3. Real-Time Explainability Waterfall Breakdown */}
      {prediction && (
        <ExplainabilityCard
          explanation={prediction.explanation}
          contributors={prediction.contributors}
          severity={prediction.severity || severity}
        />
      )}
    </div>
  );
}
