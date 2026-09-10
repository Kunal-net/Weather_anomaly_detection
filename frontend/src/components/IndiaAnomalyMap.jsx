import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { MapPin, Navigation, Thermometer, CloudRain, ShieldAlert } from 'lucide-react';

/**
 * Creates custom pulsating SVG marker icon based on station anomaly severity level.
 */
const createSeverityIcon = (severity) => {
  let colorHex = '#10b981'; // NORMAL - Emerald Green
  let pulseColor = 'rgba(16, 185, 129, 0.4)';
  let glowColor = '0 0 12px rgba(16, 185, 129, 0.8)';

  if (severity === 'CRITICAL') {
    colorHex = '#ef4444'; // CRITICAL - Crimson Red
    pulseColor = 'rgba(239, 68, 68, 0.6)';
    glowColor = '0 0 16px rgba(239, 68, 68, 0.9)';
  } else if (severity === 'HIGH') {
    colorHex = '#f97316'; // HIGH - Orange
    pulseColor = 'rgba(249, 115, 22, 0.5)';
    glowColor = '0 0 14px rgba(249, 115, 22, 0.8)';
  } else if (severity === 'WATCH') {
    colorHex = '#f59e0b'; // WATCH - Amber Yellow
    pulseColor = 'rgba(245, 158, 11, 0.5)';
    glowColor = '0 0 12px rgba(245, 158, 11, 0.8)';
  }

  const svgHtml = `
    <div style="position: relative; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center;">
      <!-- Outer Pulsating Ring -->
      <div style="
        position: absolute;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background: ${pulseColor};
        animation: pulse-ring 2s infinite ease-out;
      "></div>
      
      <!-- Inner Glowing Core -->
      <div style="
        position: relative;
        width: 18px;
        height: 18px;
        border-radius: 50%;
        background-color: ${colorHex};
        border: 2px solid #ffffff;
        box-shadow: ${glowColor};
        cursor: pointer;
        transition: transform 0.2s ease;
      "></div>
    </div>
  `;

  return L.divIcon({
    html: svgHtml,
    className: 'custom-leaflet-marker',
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -18],
  });
};

/**
 * Controller component to handle map re-centering when a location is selected.
 */
function MapCenterController({ selectedLocation }) {
  const map = useMap();
  React.useEffect(() => {
    if (selectedLocation && selectedLocation.lat && selectedLocation.lon) {
      map.flyTo([selectedLocation.lat, selectedLocation.lon], 6, {
        duration: 1.2,
      });
    }
  }, [selectedLocation, map]);
  return null;
}

export default function IndiaAnomalyMap({
  locations = [],
  selectedCity,
  onSelectLocation,
}) {
  const center = [20.5937, 78.9629]; // India geographic center
  const zoom = 5;

  const selectedLoc = locations.find(
    (l) => (l.city || l.location).toLowerCase() === (selectedCity || '').toLowerCase()
  );

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 shadow-xl relative overflow-hidden flex flex-col h-[520px]">
      {/* Header */}
      <div className="flex items-center justify-between mb-3 px-2">
        <div className="flex items-center gap-2">
          <div className="p-2 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
            <Navigation className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white tracking-tight">
              National Weather Anomaly Map (India)
            </h3>
            <p className="text-xs text-slate-400">
              Real-time multi-station pins color-coded by dual-engine anomaly severity
            </p>
          </div>
        </div>

        {/* Legend */}
        <div className="hidden sm:flex items-center gap-3 text-[11px] font-semibold bg-slate-800/80 px-3 py-1.5 rounded-xl border border-slate-700">
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 inline-block" /> Normal
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400 inline-block" /> Watch
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-500 inline-block" /> High
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 inline-block" /> Critical
          </span>
        </div>
      </div>

      {/* Leaflet Container */}
      <div className="flex-1 w-full rounded-xl overflow-hidden border border-slate-800 relative z-0">
        <MapContainer
          center={center}
          zoom={zoom}
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%' }}
        >
          <TileLayer
            attribution='&copy; <a href="https://carto.com/">CartoDB</a> Dark Matter'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            maxZoom={18}
          />

          <MapCenterController selectedLocation={selectedLoc} />

          {locations.map((loc) => {
            const cityName = loc.city || loc.location;
            const severity = loc.severity || loc.current_severity || 'NORMAL';
            const icon = createSeverityIcon(severity);
            const scorePct = Math.round(((loc.anomaly_score || loc.current_score || 0) * 100));

            return (
              <Marker
                key={cityName}
                position={[loc.lat, loc.lon]}
                icon={icon}
                eventHandlers={{
                  click: () => {
                    if (onSelectLocation) onSelectLocation(cityName);
                  },
                }}
              >
                <Popup>
                  <div className="p-1 space-y-2 min-w-[200px]">
                    <div className="flex items-center justify-between border-b border-slate-700/80 pb-2">
                      <div>
                        <h4 className="text-sm font-bold text-white flex items-center gap-1">
                          <MapPin className="w-3.5 h-3.5 text-cyan-400" />
                          {cityName}
                        </h4>
                        <span className="text-[10px] text-slate-400 font-mono">
                          {loc.lat.toFixed(2)}°N, {loc.lon.toFixed(2)}°E
                        </span>
                      </div>
                      <span
                        className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full border ${
                          severity === 'CRITICAL'
                            ? 'bg-red-500/20 text-red-400 border-red-500/40'
                            : severity === 'HIGH'
                            ? 'bg-orange-500/20 text-orange-400 border-orange-500/40'
                            : severity === 'WATCH'
                            ? 'bg-amber-500/20 text-amber-400 border-amber-500/40'
                            : 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40'
                        }`}
                      >
                        {severity}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-1.5 text-xs pt-1">
                      <div className="flex items-center gap-1 text-slate-300">
                        <Thermometer className="w-3.5 h-3.5 text-amber-400" />
                        <span>{loc.temperature ?? 27}°C</span>
                      </div>
                      <div className="flex items-center gap-1 text-slate-300">
                        <CloudRain className="w-3.5 h-3.5 text-cyan-400" />
                        <span>{loc.rainfall ?? 0} mm</span>
                      </div>
                    </div>

                    <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between">
                      <div className="text-[10px] text-slate-400 font-medium">
                        Anomaly Score: <span className="text-cyan-300 font-bold font-mono">{scorePct}%</span>
                      </div>
                      <button
                        onClick={() => {
                          if (onSelectLocation) onSelectLocation(cityName);
                        }}
                        className="text-[10px] font-bold text-cyan-400 hover:text-cyan-300 underline"
                      >
                        Deep Dive &rarr;
                      </button>
                    </div>
                  </div>
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </div>
    </div>
  );
}
