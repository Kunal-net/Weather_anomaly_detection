import React, { useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { Target, Compass, ChevronRight, Activity } from 'lucide-react';

const CITY_CODES = {
  Bengaluru: 'BLR',
  Delhi: 'DEL',
  Mumbai: 'MUM',
  Chennai: 'CHE',
  Kolkata: 'KOL',
  Hyderabad: 'HYD',
  Ahmedabad: 'AMD',
  Jaipur: 'JAI',
  Shillong: 'SHI',
  Srinagar: 'SRI',
  Shimla: 'SML',
  Bhubaneswar: 'BBI',
};

const getCityCode = (city) => {
  if (CITY_CODES[city]) return CITY_CODES[city];
  return (city || 'LOC').substring(0, 3).toUpperCase();
};

/**
 * Creates custom tactical radar reticle marker icon with multi-ring expanding sonar waves.
 */
const createTacticalMarkerIcon = (loc) => {
  const cityName = loc.city || loc.location || 'Station';
  const code = getCityCode(cityName);
  const severity = loc.severity || loc.current_severity || 'NORMAL';
  const score = loc.anomaly_score ?? loc.current_score ?? loc.current_anomaly_score ?? 0;
  const scoreFormatted = score.toFixed(2);

  let colorHex = '#10b981'; // Emerald
  let bgTint = 'rgba(16, 185, 129, 0.2)';
  if (severity === 'CRITICAL') {
    colorHex = '#ef4444'; // Aviation Red
    bgTint = 'rgba(239, 68, 68, 0.25)';
  } else if (severity === 'HIGH') {
    colorHex = '#f97316'; // Orange
    bgTint = 'rgba(249, 115, 22, 0.2)';
  } else if (severity === 'WATCH') {
    colorHex = '#f59e0b'; // Amber
    bgTint = 'rgba(245, 158, 11, 0.2)';
  }

  const isCritical = severity === 'CRITICAL';

  const svgHtml = `
    <div style="position: relative; display: flex; flex-direction: column; align-items: center; justify-content: center; width: 72px; cursor: pointer;">
      <!-- Sonar Waves & Center Reticle -->
      <div style="position: relative; width: 26px; height: 26px; display: flex; align-items: center; justify-content: center;">
        <!-- Wave 1 (Outer Sonar) -->
        <div style="position: absolute; inset: -10px; border-radius: 9999px; border: 1.5px solid ${colorHex}; opacity: 0.7; animation: radar-sonar 2.4s cubic-bezier(0, 0.2, 0.8, 1) infinite;"></div>
        <!-- Wave 2 (Middle Sonar) -->
        <div style="position: absolute; inset: -4px; border-radius: 9999px; border: 1px solid ${colorHex}; opacity: 0.5; animation: radar-sonar 2.4s 0.8s cubic-bezier(0, 0.2, 0.8, 1) infinite;"></div>
        
        <!-- Precision Center Ring -->
        <div style="position: absolute; inset: 2px; border-radius: 9999px; border: 1.5px solid ${colorHex}; background: ${bgTint}; backdrop-filter: blur(4px);"></div>
        <!-- Solid Center Core -->
        <div style="width: 8px; height: 8px; border-radius: 9999px; background-color: ${colorHex}; box-shadow: 0 0 12px ${colorHex}; z-index: 2;"></div>
      </div>
      <!-- Tactical Monospace Callout Badge -->
      <div style="margin-top: 4px; font-family: 'JetBrains Mono', monospace; font-size: 9px; font-weight: 700; color: #ffffff; background: rgba(11, 15, 25, 0.9); border: 1px solid ${colorHex}; border-radius: 6px; padding: 1px 6px; white-space: nowrap; letter-spacing: 0.5px; box-shadow: 0 4px 12px rgba(0,0,0,0.8); backdrop-filter: blur(8px);">
        ${code} // <span style="color: ${colorHex};">${scoreFormatted}</span>
      </div>
    </div>
  `;

  return L.divIcon({
    html: svgHtml,
    className: 'tactical-radar-marker',
    iconSize: [72, 44],
    iconAnchor: [36, 13],
    popupAnchor: [0, -16],
  });
};

/**
 * Controller component for smooth re-centering on selection.
 */
function MapCenterController({ selectedLocation }) {
  const map = useMap();
  React.useEffect(() => {
    if (selectedLocation && selectedLocation.lat && selectedLocation.lon) {
      map.flyTo([selectedLocation.lat, selectedLocation.lon], 6, {
        duration: 1.4,
        easeLinearity: 0.25,
      });
    }
  }, [selectedLocation, map]);
  return null;
}

/**
 * Tracks mouse position & zoom level over Leaflet map.
 */
function MapHudTracker({ setPointerCoords, setZoomLevel }) {
  useMapEvents({
    mousemove(e) {
      setPointerCoords({ lat: e.latlng.lat, lon: e.latlng.lng });
    },
    zoomend(e) {
      setZoomLevel(e.target.getZoom());
    },
  });
  return null;
}

export default function IndiaAnomalyMap({
  locations = [],
  selectedCity,
  onSelectLocation,
}) {
  const center = [21.5, 78.9629]; // Balanced view of India
  const [zoomLevel, setZoomLevel] = useState(5);
  const [pointerCoords, setPointerCoords] = useState({ lat: 21.5, lon: 78.96 });

  const selectedLoc = locations.find(
    (l) => (l.city || l.location).toLowerCase() === (selectedCity || '').toLowerCase()
  );

  return (
    <div className="glass-card rounded-2xl md:rounded-3xl p-4 md:p-5 font-mono relative flex flex-col h-[580px] select-none group">
      {/* Precision Corner Crosshairs */}
      <span className="absolute top-3 left-3 text-cyan-500/40 font-mono text-xs select-none pointer-events-none z-20">+</span>
      <span className="absolute top-3 right-3 text-cyan-500/40 font-mono text-xs select-none pointer-events-none z-20">+</span>
      <span className="absolute bottom-3 left-3 text-cyan-500/40 font-mono text-xs select-none pointer-events-none z-20">+</span>
      <span className="absolute bottom-3 right-3 text-cyan-500/40 font-mono text-xs select-none pointer-events-none z-20">+</span>

      {/* Header & HUD Overhead Control Strip */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-3 pb-3 border-b border-white/[0.08]">
        <div className="flex items-center gap-2.5">
          <div className="p-1.5 rounded-lg bg-cyan-500/10 border border-cyan-400/20 text-cyan-400">
            <Target className="w-4 h-4 animate-pulse" />
          </div>
          <div>
            <h3 className="text-xs md:text-sm font-bold text-white uppercase tracking-wider font-sans">
              National Tactical Radar <span className="text-slate-500">//</span> Station Grid
            </h3>
            <p className="text-[10px] text-slate-400 font-mono">
              REAL-TIME GEOSPATIAL ANOMALY VECTOR TELEMETRY
            </p>
          </div>
        </div>

        {/* Live Coordinates HUD Readout */}
        <div className="flex items-center gap-3 text-[10px] text-slate-300 font-mono tabular-nums bg-black/40 px-3 py-1.5 rounded-xl border border-white/[0.08] backdrop-blur-md">
          <span>
            [LAT: <span className="text-white font-bold">{pointerCoords.lat.toFixed(2)}°N</span> / LON:{' '}
            <span className="text-white font-bold">{pointerCoords.lon.toFixed(2)}°E</span>]
          </span>
          <span className="text-slate-600">|</span>
          <span>
            ZOOM: <span className="text-cyan-400 font-bold">{zoomLevel}X</span>
          </span>
        </div>
      </div>

      {/* Leaflet Map Frame with Sleek Curved Inset */}
      <div className="flex-1 w-full rounded-2xl overflow-hidden border border-white/[0.08] relative z-0 shadow-inner">
        <MapContainer
          center={center}
          zoom={5}
          scrollWheelZoom={true}
          style={{ width: '100%', height: '100%', background: '#060913' }}
        >
          <TileLayer
            attribution='&copy; CartoDB Dark Matter'
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            maxZoom={18}
          />

          <MapCenterController selectedLocation={selectedLoc} />
          <MapHudTracker setPointerCoords={setPointerCoords} setZoomLevel={setZoomLevel} />

          {locations.map((loc) => {
            const cityName = loc.city || loc.location;
            const code = getCityCode(cityName);
            const severity = loc.severity || loc.current_severity || 'NORMAL';
            const icon = createTacticalMarkerIcon(loc);
            const score = loc.anomaly_score ?? loc.current_score ?? loc.current_anomaly_score ?? 0;
            const scoreFormatted = score.toFixed(2);

            const temp = loc.temperature ?? 27.0;
            const tempDiff =
              loc.temp_departure ?? (severity === 'CRITICAL' ? '+9.9' : severity === 'HIGH' ? '+4.2' : '+1.1');
            const rain = loc.rainfall ?? 0.0;
            const rainDiff =
              loc.rain_departure ?? (severity === 'CRITICAL' ? '+126.8mm // +697%' : '+15.2mm');
            const press = loc.pressure ?? 1008.0;
            const pressDiff =
              loc.press_departure ?? (severity === 'CRITICAL' ? '-14.0 hPa' : '-2.1 hPa');

            const stateCode = loc.state
              ? loc.state.includes('Karnataka')
                ? 'KA'
                : loc.state.includes('Delhi')
                ? 'DL'
                : loc.state.includes('Maharashtra')
                ? 'MH'
                : loc.state.includes('Tamil')
                ? 'TN'
                : loc.state.includes('West Bengal')
                ? 'WB'
                : loc.state.includes('Telangana')
                ? 'TS'
                : loc.state.includes('Gujarat')
                ? 'GJ'
                : loc.state.includes('Rajasthan')
                ? 'RJ'
                : loc.state.includes('Odisha')
                ? 'OD'
                : loc.state.includes('Himachal')
                ? 'HP'
                : code
              : code;

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
                  <div className="p-3 font-mono text-xs space-y-2.5 min-w-[240px] select-none">
                    {/* Header */}
                    <div className="flex items-center justify-between border-b border-white/10 pb-2">
                      <div>
                        <div className="font-bold text-white text-sm font-sans tracking-tight">
                          {cityName}
                        </div>
                        <div className="text-[10px] text-slate-400 font-mono">
                          ZONE: {stateCode}-STATION-01
                        </div>
                      </div>
                      <span
                        className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${
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

                    {/* Metrics Readout */}
                    <div className="space-y-1 text-[11px] text-slate-300 tabular-nums">
                      <div className="flex justify-between">
                        <span className="text-slate-400">ANOMALY INDEX:</span>
                        <span className="text-cyan-400 font-bold">{scoreFormatted} / 1.00</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">TEMPERATURE:</span>
                        <span className="text-white font-bold">
                          {temp.toFixed(1)}°C <span className="text-amber-400 text-[10px] font-normal">(Δ {tempDiff}°C)</span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">PRECIPITATION:</span>
                        <span className="text-white font-bold">
                          {rain.toFixed(1)}mm <span className="text-cyan-400 text-[10px] font-normal">(Δ {rainDiff})</span>
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">PRESSURE:</span>
                        <span className="text-white font-bold">
                          {press.toFixed(1)} hPa <span className="text-slate-400 text-[10px] font-normal">(Δ {pressDiff})</span>
                        </span>
                      </div>
                    </div>

                    {/* Deep-Dive CTA */}
                    <button
                      onClick={() => {
                        if (onSelectLocation) onSelectLocation(cityName);
                      }}
                      className="w-full mt-2 py-2 px-3 rounded-xl border border-cyan-400/40 bg-cyan-500/15 hover:bg-cyan-500 hover:text-black transition-all text-xs font-bold tracking-wider text-cyan-300 uppercase flex items-center justify-center gap-1.5 shadow-md shadow-cyan-950/40 group/btn"
                    >
                      <span>OPEN STATION TELEMETRY</span>
                      <ChevronRight className="w-3.5 h-3.5 group-hover/btn:translate-x-1 transition-transform" />
                    </button>
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
