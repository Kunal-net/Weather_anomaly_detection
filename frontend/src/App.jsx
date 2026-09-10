import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ExecutiveSummaryCards from './components/ExecutiveSummaryCards';
import IndiaAnomalyMap from './components/IndiaAnomalyMap';
import StationDeepDive from './components/StationDeepDive';
import PredictionStudio from './components/PredictionStudio';
import ExplainabilityCard from './components/ExplainabilityCard';
import HistoricalTrends from './components/HistoricalTrends';
import { MOCK_LOCATIONS, MOCK_PREDICTION_RESPONSE } from './services/mockData';
import { fetchLocations, checkHealth } from './services/api';
import { ShieldAlert, X, ChevronRight, Sparkles, AlertTriangle } from 'lucide-react';

export default function App() {
  const [locations, setLocations] = useState(MOCK_LOCATIONS);
  const [selectedCity, setSelectedCity] = useState('Bengaluru');
  const [activeTab, setActiveTab] = useState('overview');
  const [systemHealth, setSystemHealth] = useState({ status: 'checking', model_loaded: true });

  // Critical Emergency Alert Toast State
  const [criticalBanner, setCriticalBanner] = useState(null);

  // Keyboard navigation shortcuts: '1', '2', '3', '4'
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (['INPUT', 'SELECT', 'TEXTAREA'].includes(document.activeElement?.tagName)) {
        return;
      }
      if (e.key === '1') setActiveTab('overview');
      if (e.key === '2') setActiveTab('deepdive');
      if (e.key === '3') setActiveTab('prediction');
      if (e.key === '4') setActiveTab('trends');
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  useEffect(() => {
    // Initial fetch of monitored stations
    fetchLocations().then((data) => {
      if (data && data.length > 0) {
        setLocations(data);
        const critLoc = data.find((l) => (l.severity || l.current_severity) === 'CRITICAL');
        if (critLoc) {
          setCriticalBanner({
            location: (critLoc.city || critLoc.location).toUpperCase(),
            score: (critLoc.anomaly_score || critLoc.current_score || 0.94).toFixed(2),
          });
        }
      }
    });

    checkHealth().then((h) => setSystemHealth(h));
  }, []);

  const handleSelectLocation = (cityName) => {
    setSelectedCity(cityName);
    setActiveTab('deepdive');
  };

  const selectedLocData =
    locations.find((l) => (l.city || l.location).toLowerCase() === selectedCity.toLowerCase()) ||
    locations[0];

  const isCriticalActive =
    (selectedLocData?.severity || selectedLocData?.current_severity) === 'CRITICAL' ||
    locations.some((l) => (l.severity || l.current_severity) === 'CRITICAL');

  return (
    <div className="min-h-screen bg-[#060913] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30 selection:text-cyan-200 relative overflow-x-hidden">
      {/* 1. Dynamic Morphing Ambient Aurora Lighting Mesh */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
        <div
          className={`absolute -top-40 -left-40 w-[650px] h-[650px] rounded-full blur-[150px] opacity-40 animate-aurora transition-all duration-1000 ${
            isCriticalActive ? 'bg-rose-600/30' : 'bg-indigo-600/25'
          }`}
        />
        <div className="absolute top-1/4 -right-40 w-[550px] h-[550px] rounded-full blur-[140px] opacity-35 animate-aurora [animation-delay:-5s] bg-cyan-600/20" />
        <div className="absolute -bottom-40 left-1/3 w-[600px] h-[600px] rounded-full blur-[150px] opacity-30 animate-aurora [animation-delay:-9s] bg-violet-600/25" />
      </div>

      {/* 2. Floating Command Center Navbar */}
      <div className="relative z-50 pt-2">
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          systemHealth={systemHealth}
        />
      </div>

      {/* 3. Global Emergency Alert Toast Notification */}
      {criticalBanner && (
        <div className="relative z-40 max-w-[1780px] w-full mx-auto px-3 md:px-6 pt-3">
          <div className="glass-card rounded-2xl border-red-500/40 bg-red-950/40 text-red-300 px-4 py-3 text-xs font-mono select-none flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 shadow-[0_8px_32px_rgba(239,68,68,0.25)] before:via-red-500/30">
            <div className="flex items-center gap-2.5 font-bold tracking-wider truncate">
              <span className="p-1 rounded-lg bg-red-500/20 border border-red-500/40 shrink-0">
                <ShieldAlert className="w-4 h-4 text-red-400 animate-pulse" />
              </span>
              <span className="truncate text-xs md:text-sm">
                [!] NATIONAL WEATHER HAZARD ACTIVE: {criticalBanner.location} STATION EXCEEDED CRITICAL BOUNDARY (SCORE: {criticalBanner.score})
              </span>
            </div>

            <div className="flex items-center gap-3 shrink-0 self-end sm:self-auto">
              <button
                onClick={() => {
                  setSelectedCity(criticalBanner.location);
                  setActiveTab('deepdive');
                }}
                className="px-3 py-1.5 rounded-xl border border-red-400/50 bg-red-500/20 hover:bg-red-500 hover:text-white transition-all text-xs font-bold tracking-wider text-red-200 uppercase flex items-center gap-1.5 shadow-md shadow-red-950/40"
              >
                <span>OPEN TELEMETRY</span>
                <ChevronRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setCriticalBanner(null)}
                className="p-1 text-red-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 4. Main Cockpit Dashboard Canvas */}
      <main className="relative z-10 max-w-[1780px] w-full mx-auto px-3 md:px-6 py-4 space-y-4 flex-1">
        {/* National High-Density Executive Telemetry Bento Strip */}
        <ExecutiveSummaryCards locations={locations} />

        {/* Tab 01: Overview (National Tactical Radar Map + Explainability Waterfall) */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Map Column (2 cols) */}
            <div className="lg:col-span-2">
              <IndiaAnomalyMap
                locations={locations}
                selectedCity={selectedCity}
                onSelectLocation={handleSelectLocation}
              />
            </div>

            {/* Forensic Explainability Column (1 col) */}
            <div>
              <ExplainabilityCard
                explanation={
                  selectedLocData?.explanation ||
                  MOCK_PREDICTION_RESPONSE.explanation ||
                  `Active monitoring for ${selectedLocData?.city || selectedLocData?.location}: Dual-engine evaluating departures from historical baseline.`
                }
                contributors={
                  selectedLocData?.contributors?.length
                    ? selectedLocData.contributors
                    : selectedLocData?.city === 'Bengaluru' || selectedLocData?.location === 'Bengaluru'
                    ? MOCK_PREDICTION_RESPONSE.contributors
                    : []
                }
                severity={selectedLocData?.severity || selectedLocData?.current_severity || 'NORMAL'}
              />
            </div>
          </div>
        )}

        {/* Tab 02: Station Telemetry (Station Switcher Strip + Instrument Panel) */}
        {activeTab === 'deepdive' && (
          <div className="space-y-4">
            {/* Station Selector Bar */}
            <div className="glass-card rounded-2xl p-2.5 flex items-center justify-between gap-3 overflow-x-auto text-xs font-mono select-none">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest whitespace-nowrap pl-2">
                STATION SELECTOR:
              </span>
              <div className="flex items-center gap-2 overflow-x-auto no-scrollbar">
                {locations.map((loc) => {
                  const name = loc.city || loc.location;
                  const sev = loc.severity || loc.current_severity || 'NORMAL';
                  const isSelected = name.toLowerCase() === selectedCity.toLowerCase();
                  let dotColor = 'bg-emerald-400';
                  if (sev === 'CRITICAL') dotColor = 'bg-red-500 animate-ping';
                  else if (sev === 'HIGH') dotColor = 'bg-orange-500';
                  else if (sev === 'WATCH') dotColor = 'bg-amber-500';

                  return (
                    <button
                      key={name}
                      onClick={() => setSelectedCity(name)}
                      className={`px-3 py-1.5 rounded-xl text-xs font-bold tracking-wider transition-all whitespace-nowrap flex items-center gap-2 border ${
                        isSelected
                          ? 'bg-gradient-to-r from-cyan-500/20 to-indigo-500/20 text-cyan-300 border-cyan-400/50 shadow-[0_0_12px_rgba(6,182,212,0.25)]'
                          : 'bg-white/[0.02] border-white/[0.08] text-slate-400 hover:text-white hover:bg-white/[0.05]'
                      }`}
                    >
                      <span>{name.toUpperCase()}</span>
                      <span className={`w-2 h-2 rounded-full ${dotColor}`} />
                    </button>
                  );
                })}
              </div>
            </div>

            <StationDeepDive
              stationData={selectedLocData}
              selectedCity={selectedCity}
              locations={locations}
            />
          </div>
        )}

        {/* Tab 03: What-If Prediction Studio Cockpit */}
        {activeTab === 'prediction' && (
          <PredictionStudio defaultCity={selectedCity} />
        )}

        {/* Tab 04: Historical Telemetry Corridors */}
        {activeTab === 'trends' && (
          <HistoricalTrends selectedCity={selectedCity} />
        )}
      </main>

      {/* 5. High-End Glassmorphic Telemetry Footer */}
      <footer className="relative z-10 max-w-[1780px] w-full mx-auto px-3 md:px-6 py-4 select-none font-mono">
        <div className="glass-card rounded-2xl px-5 py-3 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-400">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-200">AEROSENSE-AI &copy; 2026</span>
            <span className="text-slate-600">//</span>
            <span>TEAM ILLUMINATI [SIH-2026 PROTOTYPE PS-1642]</span>
          </div>
          <div className="text-[11px] text-slate-500 flex items-center gap-3">
            <span>DUAL-ENGINE TELEMETRY (ISO-FOREST + Z-SCORE)</span>
            <span className="text-slate-700">&bull;</span>
            <span className="text-cyan-400 font-bold">HOTKEYS: [1] MAP [2] STATION [3] WHAT-IF [4] TRENDS</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
