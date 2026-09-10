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
import { AlertCircle, X, ShieldAlert, ChevronRight } from 'lucide-react';

export default function App() {
  const [locations, setLocations] = useState(MOCK_LOCATIONS);
  const [selectedCity, setSelectedCity] = useState('Bengaluru');
  const [activeTab, setActiveTab] = useState('overview');
  const [systemHealth, setSystemHealth] = useState({ status: 'checking', model_loaded: true });

  // Critical Escalation Toast Notification State
  const [criticalToast, setCriticalToast] = useState(null);

  useEffect(() => {
    // Initial fetch of monitored stations
    fetchLocations().then((data) => {
      if (data && data.length > 0) {
        setLocations(data);
        // Check for any Critical station and trigger toast alert
        const critLoc = data.find((l) => (l.severity || l.current_severity) === 'CRITICAL');
        if (critLoc) {
          setCriticalToast({
            location: critLoc.city || critLoc.location,
            score: critLoc.anomaly_score || critLoc.current_score || 0.94,
            explanation: `CRITICAL ALERT: Anomaly Score ${((critLoc.anomaly_score || 0.94) * 100).toFixed(0)}% in ${critLoc.city || critLoc.location}. Severe extreme weather event detected.`,
          });
        }
      }
    });

    checkHealth().then((h) => setSystemHealth(h));
  }, []);

  const handleSelectLocation = (cityName) => {
    setSelectedCity(cityName);
    // Auto switch tab to deepdive when location selected from map or bar
    setActiveTab('deepdive');
  };

  const selectedLocData = locations.find(
    (l) => (l.city || l.location).toLowerCase() === selectedCity.toLowerCase()
  ) || locations[0];

  return (
    <div className="min-h-screen bg-[#0b0f19] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30">
      {/* 1. Command Center Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemHealth={systemHealth}
      />

      {/* 2. Critical Alert Escalation Toast Notification */}
      {criticalToast && (
        <div className="bg-gradient-to-r from-red-600 via-rose-600 to-red-700 text-white px-4 py-3 shadow-2xl border-b border-red-400/40 relative z-40 animate-bounce-slow">
          <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="p-1.5 rounded-lg bg-black/20 border border-white/20">
                <ShieldAlert className="w-5 h-5 text-white animate-pulse" />
              </div>
              <div className="text-xs md:text-sm font-bold">
                <span className="uppercase tracking-wider font-extrabold px-2 py-0.5 rounded bg-black/30 border border-white/30 mr-2">
                  CRITICAL ESCALATION
                </span>
                {criticalToast.explanation}
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setSelectedCity(criticalToast.location);
                  setActiveTab('deepdive');
                }}
                className="px-3 py-1 rounded-lg bg-white text-red-700 font-extrabold text-xs hover:bg-slate-100 transition-colors shadow-sm flex items-center gap-1"
              >
                Inspect Station <ChevronRight className="w-3.5 h-3.5" />
              </button>
              <button
                onClick={() => setCriticalToast(null)}
                className="p-1 rounded-lg text-white/80 hover:text-white hover:bg-black/20"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 3. Main Command Center Content */}
      <main className="max-w-7xl mx-auto w-full px-4 md:px-6 py-6 space-y-6 flex-1">
        {/* Executive Summary Metric Cards */}
        <ExecutiveSummaryCards locations={locations} />

        {/* City Quick Selector Bar */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-3 flex items-center justify-between gap-2 overflow-x-auto">
          <span className="text-xs font-bold text-slate-400 uppercase tracking-wider whitespace-nowrap pl-1">
            Monitored Stations:
          </span>
          <div className="flex items-center gap-2">
            {locations.map((loc) => {
              const name = loc.city || loc.location;
              const sev = loc.severity || loc.current_severity;
              const isSelected = name.toLowerCase() === selectedCity.toLowerCase();
              return (
                <button
                  key={name}
                  onClick={() => setSelectedCity(name)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 flex items-center gap-2 border whitespace-nowrap ${
                    isSelected
                      ? 'bg-gradient-to-r from-cyan-500/20 to-blue-600/20 border-cyan-500 text-cyan-200 shadow-md shadow-cyan-500/10'
                      : 'bg-slate-800/60 border-slate-700/60 text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }`}
                >
                  <span>{name}</span>
                  <span
                    className={`w-2 h-2 rounded-full ${
                      sev === 'CRITICAL'
                        ? 'bg-red-500 animate-pulse'
                        : sev === 'HIGH'
                        ? 'bg-orange-500'
                        : sev === 'WATCH'
                        ? 'bg-amber-500'
                        : 'bg-emerald-500'
                    }`}
                  />
                </button>
              );
            })}
          </div>
        </div>

        {/* 4. Tab Navigation Views */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Map Column (2 cols) */}
            <div className="lg:col-span-2">
              <IndiaAnomalyMap
                locations={locations}
                selectedCity={selectedCity}
                onSelectLocation={handleSelectLocation}
              />
            </div>

            {/* Explainability Column (1 col) */}
            <div>
              <ExplainabilityCard
                explanation={
                  selectedLocData?.city === 'Bengaluru'
                    ? MOCK_PREDICTION_RESPONSE.explanation
                    : `Active monitoring for ${selectedLocData?.city || selectedLocData?.location}: Dual-engine evaluating departures from historical baseline.`
                }
                contributors={
                  selectedLocData?.city === 'Bengaluru'
                    ? MOCK_PREDICTION_RESPONSE.contributors
                    : []
                }
                severity={selectedLocData?.severity || selectedLocData?.current_severity || 'NORMAL'}
              />
            </div>
          </div>
        )}

        {activeTab === 'deepdive' && (
          <StationDeepDive
            stationData={selectedLocData}
            selectedCity={selectedCity}
            locations={locations}
          />
        )}

        {activeTab === 'prediction' && (
          <PredictionStudio defaultCity={selectedCity} />
        )}

        {activeTab === 'trends' && (
          <HistoricalTrends selectedCity={selectedCity} />
        )}
      </main>

      {/* 5. Footer */}
      <footer className="border-t border-slate-800/80 bg-[#0f172a]/80 px-6 py-4 text-xs text-slate-400 text-center">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2">
          <div>
            AeroSense-AI &copy; 2026 Team ILLUMINATI &bull; Smart India Hackathon Prototype (PS: SIH1642)
          </div>
          <div className="text-slate-500 text-[11px]">
            Dual-Engine Anomaly Infrastructure (Z-Score + Scikit-learn Isolation Forest) &bull; Response Time &lt; 4ms
          </div>
        </div>
      </footer>
    </div>
  );
}
