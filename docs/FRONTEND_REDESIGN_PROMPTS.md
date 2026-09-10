# AeroSense-AI — Frontend Anti-Slop Tactical Redesign Roadmap
**Smart India Hackathon 2026 | Team ILLUMINATI (ID: 27113) | Problem SIH1642**  
*Powered by installed Mac skills: `design-taste-frontend`, `industrial-brutalist-ui`, `redesign-existing-projects`, `generative_ui`*

---

## 🧭 Executive Design Read & Dials

> **Design Read:**  
> *"Reading this as: National Meteorological & Aerospace Anomaly Command Center for SIH Judges and Disaster Management Operators, with a Tactical Telemetry & Industrial Brutalism language, leaning toward high-density data grids, monospaced tabular figures, razor-thin structural dividers, and surgical calibrated severity indicators. Zero consumer AI-slop."*

### Dial Settings:
* **`DESIGN_VARIANCE: 7`** — Asymmetrical command-center compartments, deliberate functional hierarchy.
* **`MOTION_INTENSITY: 4`** — Precise, military-grade micro-transitions (150-200ms). No gratuitous bouncing, floating, or infinite glowing loops.
* **`VISUAL_DENSITY: 8`** — Cockpit-grade telemetry density. Maximum situational awareness per pixel, tabular numerals (`tabular-nums`), technical coordinate framing.

---

## 🚫 AI-Slop Patterns to Purge
1. **AI Gradients & Text Masks:** Remove all `bg-gradient-to-r ... bg-clip-text text-transparent` and purple/cyan glow blobs.
2. **Puffy 16px Rounded Cards:** Replace all `rounded-2xl` and `rounded-xl` cards with crisp `rounded-none` or subtle `rounded-sm` (2px-4px) industrial borders.
3. **Identical 4-Card Rows:** Replace cookie-cutter metric cards with a unified, high-density tactical telemetry strip.
4. **Gratuitous Animations:** Remove `animate-bounce-slow` and multi-ring pulsing blobs; use single-pixel status blinks and hardware-style indicator dots.
5. **Vague Copy:** Replace generic marketing copy with exact meteorological telemetry (`[LAT 12.97°N / LON 77.59°E]`, `Z = +5.4σ`, `QNH 994 hPa`).

---

## 📋 Vibe Coding Redesign Prompts

Feed these prompts sequentially into your AI coding assistant. Each prompt is engineered to directly trigger your installed anti-slop skills.

---

### 🛠️ PROMPT R1: Tactical Foundation & Monospace Typography Setup
**Target Files:** `frontend/tailwind.config.js`, `frontend/src/index.css`, `frontend/index.html`

```text
You are redesigning AeroSense-AI to eliminate AI slop and implement an authentic Aerospace & Tactical Telemetry Command Center interface.
Activate skills: 'design-taste-frontend', 'industrial-brutalist-ui', and 'redesign-existing-projects'.

Design Dials: VARIANCE=7, MOTION=4, DENSITY=8.

1. In index.html:
   - Import 'JetBrains Mono' (weights 400, 500, 700) and 'Geist' or 'Space Grotesk' via Google Fonts.
   - Set page background to matte carbon '#080c14'.

2. In tailwind.config.js:
   - Configure fontFamily:
     - sans: ['Space Grotesk', 'system-ui', 'sans-serif']
     - mono: ['JetBrains Mono', 'monospace']
   - Establish high-contrast Tactical Telemetry colors:
     - carbon: { 950: '#06080d', 900: '#080c14', 850: '#0d131f', 800: '#141c2c', 700: '#1e293b' }
     - border: '#1e293b' (razor-thin structural lines)
     - severity colors (uncompromising matte alerts):
       • normal: '#10b981' (Emerald)
       • watch: '#f59e0b' (Amber)
       • high: '#f97316' (Orange)
       • critical: '#ef4444' (Aviation Hazard Red)
       • telemetry: '#06b6d4' (Cyan HUD indicator)

3. In src/index.css:
   - Add `.tabular-nums` rule and apply font-variant-numeric: tabular-nums to all numbers.
   - Add a subtle CRT scanline effect overlay utility:
     .crt-grid { background-image: radial-gradient(rgba(255,255,255,0.04) 1px, transparent 0); background-size: 24px 24px; }
   - Enforce 90-degree corners or subtle 2px rounding on panels: reject puffy rounded-2xl blobs.
   - Eliminate all generic drop-shadows and purple gradients.
```

---

### 🛰️ PROMPT R2: Tactical Command Center Navbar Overhaul
**Target File:** `frontend/src/components/Navbar.jsx`

```text
Redesign frontend/src/components/Navbar.jsx using 'industrial-brutalist-ui' and 'design-taste-frontend'.
Eliminate the consumer-app floating header and create a military-grade aerospace telemetry bar.

1. Structure & Layout:
   - Rigid 1px bottom border (#1e293b), background matte carbon (#080c14).
   - Height: compact 52px. Max-width container with zero wasted margin.

2. Brand & Mission Header:
   - Replace gradient text with crisp, heavy uppercase mono: "AEROSENSE // TELEMETRY"
   - Add technical metadata tag: "[SIH-2026 // PS-1642 // UNIT: ILLUMINATI]" in 10px mono tracking-widest text-slate-400.
   - Hardware status LED: small 6px solid emerald dot with subtle 1s blink rate: "SAT-LINK: ACTIVE".

3. Navigation Tabs:
   - Industrial segmented toggle style (rigid 1px borders, square corners, zero pill shapes).
   - Tabs: [01 // NATIONAL MAP], [02 // STATION TELEMETRY], [03 // WHAT-IF STUDIO], [04 // TIME-SERIES CORRIDOR].
   - Active state: Carbon-800 background, 2px top accent line (cyan or emerald), crisp white text. No soft gradient pills.

4. Right Readout Telemetry:
   - Dual-clock display: "IST: 13:20:45 | UTC: 07:50:45Z" in monospace tabular-nums.
   - Engine Mode indicator: "[DUAL-ENGINE: ISO-FOREST + Z-SCORE]" with live backend health status.
```

---

### 📊 PROMPT R3: High-Density Telemetry Strip (Replacing 4 Equal Cards)
**Target File:** `frontend/src/components/ExecutiveSummaryCards.jsx`

```text
Redesign frontend/src/components/ExecutiveSummaryCards.jsx using 'design-taste-frontend' and 'redesign-existing-projects'.
PURGE the generic 4 equal colored cards with pastel circles. Replace with a unified, high-density Tactical Telemetry HUD Strip.

1. Layout & Architecture:
   - CSS Grid with 1px border dividers (`divide-x divide-slate-800 bg-[#080c14] border border-slate-800 rounded-sm`).
   - Eliminate all rounded-2xl corners, drop shadows, and gradient backgrounds.

2. Cells in the Telemetry Strip:
   - Cell 1: NATIONAL THREAT LEVEL:
     Display highest current threat across India (e.g. "DEFCON-1 // CRITICAL HAZARD" or "DEFCON-4 // NORMAL").
     Color-coded tag with aviation red if score >= 0.90.
   - Cell 2: MONITORED STATIONS:
     Large tabular number "10 / 10 ONLINE" with subtext: "Coverage: 10 Indian Climate Zones".
   - Cell 3: ACTIVE ANOMALIES BREAKDOWN:
     Horizontal mini-matrix:
     [CRIT: {criticalCount}] in aviation red | [HIGH: {highCount}] in orange | [WATCH: {watchCount}] in amber | [NORM: {normalCount}] in emerald.
   - Cell 4: COMPOSITE NATIONAL ANOMALY INDEX:
     Average score across all 10 cities formatted in 14px mono tabular-nums with an ASCII visual meter: `[████░░░░░░] 0.42`.
   - Cell 5: METEOROLOGICAL ALERT TICKER:
     A single-line real-time alert summary: "LATEST: Bengaluru Cloudburst (+697% rain departure, -14 hPa pressure drop)".

3. Typography:
   - All labels in uppercase 10px monospace tracking-wider text-slate-400.
   - All numbers in bold `tabular-nums font-mono text-white`.
```

---

### 🗺️ PROMPT R4: Tactical India Anomaly Radar Map Overhaul
**Target File:** `frontend/src/components/IndiaAnomalyMap.jsx`

```text
Redesign frontend/src/components/IndiaAnomalyMap.jsx using 'industrial-brutalist-ui' and 'generative_ui'.
Transform the map from a generic Leaflet view into a tactical satellite radar monitoring station.

1. Map Container & Framing:
   - Strict 1px border (#1e293b) with industrial framing corners: add small "+" crosshairs at the 4 corners of the map card.
   - CartoDB Dark Matter tiles (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`).
   - Top-right overlay HUD: live coordinates of mouse pointer `[LAT: 12.97°N / LON: 77.59°E]`, zoom level, and active station counter.

2. Precision Target Markers (No puffy cartoon pins!):
   - Replace the glowing bouncy balls with precision targeting reticles:
     - Outer thin square bracket: `[  ]` that expands on hover.
     - Center 4px precision dot color-coded to severity:
       • CRITICAL: #ef4444 (Solid Aviation Red + razor 1px strobe ring)
       • HIGH: #f97316 (Orange target)
       • WATCH: #f59e0b (Amber target)
       • NORMAL: #10b981 (Emerald target)
     - Label directly below the reticle in 9px monospace uppercase: "BLR // 0.94" or "DEL // 0.18".

3. Tactical Leaflet Popup:
   - Dark technical HUD popup: matte carbon background, 1px severity border, monospace tabular metrics:
     "STATION: BENGALURU [KA-01]"
     "SEVERITY: CRITICAL (SCORE: 0.94 / 1.00)"
     "TEMP: 37.0°C (Δ +9.9°C)"
     "RAIN: 145.0mm (Δ +126.8mm // +697%)"
     "PRESS: 994 hPa (Δ -14.0 hPa)"
   - Button: `[ENGAGE DEEP-DIVE TELEMETRY >>>]` with hover background invert.
```

---

### 🎛️ PROMPT R5: Station Deep-Dive & Baseline Gauges Overhaul
**Target File:** `frontend/src/components/StationDeepDive.jsx`

```text
Redesign frontend/src/components/StationDeepDive.jsx using 'design-taste-frontend' and 'industrial-brutalist-ui'.
Eliminate soft consumer progress bars. Build an aerospace telemetry instrument panel.

1. Station Header Telemetry:
   - Industrial header with coordinates, elevation, and climate classification:
     `STATION: BENGALURU // ELEV: 920M // ZONE: DECCAN PLATEAU // COORDS: 12.9716°N, 77.5946°E`
   - Active Severity Badge: high-contrast angular tag: `[ STATUS: CRITICAL // HAZARD LEVEL 4 ]`.

2. 5 Variable Telemetry Gauges (Temperature, Rainfall, Pressure, Wind Speed, Humidity):
   - Replace toy progress bars with a technical $\mu \pm 2\sigma$ Corridor Gauge:
     - Display:
       • Observed Value in large bold monospace: `37.0°C`
       • Historical Normal ($\mu$): `27.1°C`
       • Standard Deviation ($\sigma$): `1.8°C`
       • Departure Delta ($\Delta$): `+9.9°C (+36.5% / Z = +5.5σ)` color-coded red.
     - Visual Corridor Bar:
       A horizontal linear scale showing:
       - Shaded bracket representing normal seasonal range `[ μ - 2σ ... μ + 2σ ]` (23.5°C to 30.7°C).
       - Precision vertical hairline needle pointing to the observed `37.0°C` far to the right, clearly indicating a statistical boundary breach!

3. Tabular Observation Log:
   - High-density data grid comparing Current Observation vs Expected Monthly Mean vs Departure vs Z-Score with zero wasted padding.
```

---

### 🧪 PROMPT R6: What-If Prediction Studio (Aerospace Cockpit) Overhaul
**Target File:** `frontend/src/components/PredictionStudio.jsx`

```text
Redesign frontend/src/components/PredictionStudio.jsx using 'generative_ui' and 'industrial-brutalist-ui'.
Transform the sliders section into a physical meteorological simulation testing console for SIH judges.

1. Preset Simulation Switches:
   - Industrial toggle buttons with mechanical click aesthetic:
     `[PRESET 01: NORMAL SEPTEMBER]`
     `[PRESET 02: EXTREME HEATWAVE]`
     `[PRESET 03: BENGALURU CLOUDBURST (145mm + 994 hPa)]`
     `[PRESET 04: CYCLONE DEPRESSION]`
   - Clicking immediately snaps sliders and updates live calculation.

2. Precision Parameter Sliders:
   - Industrial slider tracks: matte dark trough with tick marks at $\mu$ (historical mean) and $\pm 2\sigma$.
   - Live numerical input field synced with slider in 12px mono tabular-nums.
   - Directly underneath each slider, display real-time deviation from baseline:
     `Δ = +126.8 mm (+696.7% vs Normal, Z = +5.4σ)`.

3. Live Dual-Engine Output HUD:
   - Central Score Readout: Large circular SVG dial with mechanical degree tick marks (0° to 270°), needle pointer, and calibrated score: `0.94 / 1.00`.
   - Dual-Engine Contribution sub-metrics:
     `LAYER 1 (STATISTICAL Z-SCORE): 0.92 [WEIGHT: 40%]`
     `LAYER 2 (ISOLATION FOREST ML): 0.95 [WEIGHT: 60%]`
     `INFERENCE LATENCY: 6.4ms [TARGET: <15ms]`
   - Severity Alert Stamp: Angular military stamp: `CRITICAL // IMMEDIATE DISASTER ACTION REQUIRED`.
```

---

### 📑 PROMPT R7: Explainability & Contributor Waterfall Overhaul
**Target File:** `frontend/src/components/ExplainabilityCard.jsx`

```text
Redesign frontend/src/components/ExplainabilityCard.jsx using 'design-taste-frontend' and 'redesign-existing-projects'.
Eliminate generic pastel bar charts. Create an uncompromising forensic explainability report.

1. Natural Language Diagnostic Incident Banner:
   - High-contrast alert container with 1px border (#ef4444 for Critical, #f97316 for High).
   - Monospace header: `FORENSIC ANOMALY RATIONALE // GENERATED BY EXPLAINABILITY ENGINE`:
   - Diagnostic text formatted in high-legibility clean typography with bold metric callouts:
     "CRITICAL ALERT in Bengaluru: Severe Extreme Rainfall detected relative to September baseline. Primary drivers: Rainfall is +697% above normal (145.0mm vs 18.2mm normal, Z=+5.4); Atmospheric Pressure drop of -14.0hPa (994.0 vs 1008.0 normal, Z=-3.8)."

2. Contributor Waterfall Ranking:
   - Precision horizontal contribution ranking:
     - #1 RAINFALL: 52.4% Contribution `[████████████████████░░░░]` | +697% departure | Z = +5.4σ
     - #2 TEMPERATURE: 28.1% Contribution `[██████████░░░░░░░░░░░░]` | +9.9°C departure | Z = +3.8σ
     - #3 PRESSURE: 19.5% Contribution `[███████░░░░░░░░░░░░░░░]` | -14.0 hPa departure | Z = -3.8σ
     - #4 HUMIDITY: 0.0% Contribution `[░░░░░░░░░░░░░░░░░░░░░░]` | Within normal limits
     - #5 WIND SPEED: 0.0% Contribution `[░░░░░░░░░░░░░░░░░░░░░░]` | Within normal limits
   - Show formula note in 10px mono:
     `Formula: Contrib_i = (|Z_i| / Σ|Z_j|) × 100. Context-aware seasonal deviation, not static thresholding.`
```

---

### 📈 PROMPT R8: Precision Historical Trends Telemetry Overhaul
**Target File:** `frontend/src/components/HistoricalTrends.jsx`

```text
Redesign frontend/src/components/HistoricalTrends.jsx using 'design-taste-frontend' and 'industrial-brutalist-ui'.
Eliminate generic chart gradients and build a high-precision meteorological corridor chart.

1. Chart Controls & Variable Selector:
   - Segmented buttons: `[ TEMPERATURE (°C) ]`, `[ RAINFALL (MM) ]`, `[ PRESSURE (HPA) ]`, `[ WIND (M/S) ]`, `[ HUMIDITY (%) ]`.
   - Timeframe filter: `[ 7 DAYS ]`, `[ 14 DAYS ]`, `[ 30 DAYS ]`, `[ 90 DAYS ]`.

2. Recharts Corridor Chart Styling:
   - Area fill for Normal Baseline Corridor ($\mu \pm 2\sigma$): subtle low-opacity emerald `#10b98115` with dashed bounding lines.
   - Observed Series: crisp 2px solid cyan/white telemetry line `#38bdf8`.
   - Anomaly Breach Markers: sharp red diamond dots positioned on dates where observed points breach the corridor bounds.
   - Clean dark tooltips: monospace tabular readouts showing Date, Observed Value, Normal Mean, Upper Bound, and Lower Bound.

3. Seasonal Frequency Breakdown:
   - Secondary horizontal bar chart showing historical anomaly occurrences by season (Monsoon, Summer, Winter, Post-Monsoon).
```

---

### 🎛️ PROMPT R9: Master Assembly & Cockpit Polish in App.jsx
**Target File:** `frontend/src/App.jsx`

```text
Wire all redesigned components together in frontend/src/App.jsx.
Apply the 'design-taste-frontend' pre-flight checklist.

1. Layout & Grid Composition:
   - Zero layout shifts. Clean 1280px-1440px max-width container with auto margins.
   - Seamless responsive behavior for hackathon projectors (1920x1080 and 1366x768).
   - Tab switching or split-screen command layout:
     - Overview Tab: National Telemetry Strip + India Leaflet Map + Anomaly Log.
     - Station Tab: Station Selector Bar + Station Deep-Dive Instrument Panel.
     - What-If Tab: Prediction Studio Cockpit + Real-Time Explainability Waterfall.
     - Trends Tab: Historical Corridor Telemetry + Seasonal Anomaly Distribution.

2. Global Emergency Banner:
   - Sleek, non-bouncy alert banner at top when a station is in CRITICAL severity:
     `[!] NATIONAL WEATHER HAZARD ACTIVE: BENGALURU STATION EXCEEDED CRITICAL THRESHOLD (SCORE: 0.94)`
     Includes quick shortcut button: `[JUMP TO TELEMETRY >>>]`.

3. Keyboard Navigation:
   - Bind keys '1', '2', '3', '4' to quickly switch between tabs for a rapid, buttery-smooth SIH demo presentation.
```
