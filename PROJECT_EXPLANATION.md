# 🌦️ Weather Anomaly Detection System — Complete Project Guide

> **AI/ML-Powered Weather Anomaly Detection, Monitoring, and Explainability Platform**  
> **Target:** Smart India Hackathon (SIH) Prototype  
> **North Star Question:** *"Is the current weather behaving abnormally compared to what is historically expected for this location and time, how unusual is it, and what variables are responsible?"*

---

## 💡 1. Executive Summary & Problem Statement

Traditional weather applications primarily answer:
> **"What is the weather?"** *(e.g. "It is 35°C with 80% humidity in Bengaluru.")*

Our system answers a fundamentally different, decision-critical question:
> **"Is this weather behaving unusually compared to historical expectations for this location and season?"**

### Why Static Thresholds Fail
A simple approach might say:
```python
if temperature > 35:
    alert("Heatwave Anomaly")
```
In meteorology, this is completely invalid:
- **35°C in Delhi or Rajasthan during May** is normal, expected summer weather.
- **35°C in Bengaluru or Shimla during January** is an extreme, unprecedented climate anomaly.
- Extreme weather can also occur when multiple variables have moderate departures that together form a dangerous **compound anomaly** (e.g., moderate heat + high humidity + sudden pressure plunge = developing severe depression/storm).

Therefore, our platform is built around **context-aware deviation from historical seasonal baselines**.

---

## 🏛️ 2. High-Level Architecture

The platform processes weather observations through three interconnected tiers:

```text
┌────────────────────────────────────────────────────────┐
│                   1. DATA FOUNDATION                   │
│   • Raw Weather Data (NOAA METAR / ISD Station Records)│
│   • Physical Bounds Verification (Reject bad sensor data)│
│   • Temporal & Rolling Feature Engineering             │
│   • Historical Baseline Engine (Location + Month Norms)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               2. DUAL-ENGINE AI / ML BRAIN             │
│   ├── Statistical Layer: Standardized Z-Score Deviations│
│   └── Machine Learning: Scikit-learn Isolation Forest   │
│   • Calibrated Anomaly Score (0.00 to 1.00)            │
│   • 4-Tier Severity Engine (Normal, Watch, High, Crit) │
│   • Explainability Engine (Feature Contribution Ranking)│
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              3. DELIVERY & USER EXPERIENCE             │
│   • High-Performance FastAPI Backend (REST Endpoints)  │
│   • Interactive React Dashboard with India Map         │
│   • Live "What-If" Prediction Studio with Sliders      │
│   • Historical Trend & Anomaly Timeline Charts         │
└────────────────────────────────────────────────────────┘
```

---

## 🔍 3. The Life of a Weather Reading (Step-by-Step Flow)

Let's walk through an end-to-end example of what happens when a weather observation is recorded:

### 📍 Example Input:
A ground station in **Bengaluru** records this observation in **September**:
- **Temperature:** $37.0^\circ\text{C}$
- **Rainfall:** $145.0\text{ mm}$
- **Relative Humidity:** $92\%$
- **Atmospheric Pressure:** $994.0\text{ hPa}$
- **Wind Speed:** $14.5\text{ m/s}$

---

### Step 1: Ingestion & Sanity Validation
1. **Physical Bounds Validation**: Checks that numbers fall within realistic meteorological ranges (e.g. Humidity $0-100\%$, Pressure $870-1085\text{ hPa}$).
   - If a broken sensor reported $500\%$ humidity or $-999^\circ\text{C}$, it is rejected as bad sensor data rather than being falsely flagged as a weather anomaly.
2. **Cyclic Temporal Encoding**: Computes $\sin$ and $\cos$ of the day of the year to capture seasonal continuity.

---

### Step 2: Historical Baseline Lookup
The system instantly queries precomputed historical baselines for **Bengaluru in September**:

| Weather Metric | September Historical Normal ($\mu$) | Normal Variation ($\sigma$) | Current Reading | Net Deviation ($\Delta$) |
| :--- | :--- | :--- | :--- | :--- |
| **Temperature** | $27.1^\circ\text{C}$ | $\pm 1.8^\circ\text{C}$ | $37.0^\circ\text{C}$ | **$+9.9^\circ\text{C}$** |
| **Rainfall** | $18.2\text{ mm}$ | $\pm 14.5\text{ mm}$ | $145.0\text{ mm}$ | **$+126.8\text{ mm}$** |
| **Pressure** | $1008.0\text{ hPa}$ | $\pm 2.1\text{ hPa}$ | $994.0\text{ hPa}$ | **$-14.0\text{ hPa}$** |
| **Humidity** | $74.0\%$ | $\pm 8.2\%$ | $92.0\%$ | **$+18.0\%$** |
| **Wind Speed** | $3.5\text{ m/s}$ | $\pm 1.2\text{ m/s}$ | $14.5\text{ m/s}$ | **$+11.0\text{ m/s}$** |

---

### Step 3: Dual-Engine Anomaly Detection

#### Engine 1 — Statistical Deviation (Z-Scores)
Quantifies individual variable deviations using standardized Z-scores:
$$Z = \frac{X_{\text{observed}} - \mu_{\text{baseline}}}{\sigma_{\text{baseline}}}$$
- Rainfall: $Z = \frac{145.0 - 18.2}{14.5} = \mathbf{+8.74\sigma}$ (Unprecedented rainfall)
- Temperature: $Z = \frac{37.0 - 27.1}{1.8} = \mathbf{+5.50\sigma}$ (Extreme heat anomaly)
- Pressure: $Z = \frac{994.0 - 1008.0}{2.1} = \mathbf{-6.67\sigma}$ (Deep pressure drop)

#### Engine 2 — Machine Learning (Isolation Forest)
- Unsupervised tree-based algorithm that isolates rare, abnormal data points in multidimensional space.
- Detects non-linear compound anomalies where no single variable alone looks catastrophic, but their collective simultaneous combination indicates an imminent extreme event.

---

### Step 4: Calibrated Anomaly Scoring
The statistical deviations and the Isolation Forest decision function are combined and calibrated onto a standardized scale from **`0.00` to `1.00`**:

$$\text{Final Anomaly Score} = \mathbf{0.94}\text{ (94\%)}$$

---

### Step 5: Severity Classification
The score maps to one of four standardized severity levels:

| Score Range | Severity Level | Badge Color | Interpretation |
| :--- | :--- | :--- | :--- |
| `0.00 - 0.39` | 🟢 **NORMAL** | Emerald Green | Weather is behaving within expected seasonal limits. |
| `0.40 - 0.69` | 🟡 **WATCH** | Amber Yellow | Noticeable departure; station should be monitored. |
| `0.70 - 0.89` | 🟠 **HIGH** | Vibrant Orange | Significant anomaly; potential advisory needed. |
| `0.90 - 1.00` | 🔴 **CRITICAL** | Crimson Red | Severe compound anomaly or extreme meteorological event. |

In our Bengaluru scenario $\to$ **🔴 CRITICAL (0.94)**.

---

### Step 6: Transparent Explainability Engine
Rather than presenting a black-box percentage, the explainability engine computes:
1. **Ranked Feature Contributions**:
   - 🌧️ **Rainfall:** $52.4\%$ contribution (Observed 145mm vs Normal 18.2mm — $+696\%$)
   - 🌡️ **Temperature:** $28.1\%$ contribution (Observed 37°C vs Normal 27.1°C — $+9.9°C$)
   - 📉 **Pressure:** $19.5\%$ contribution (Observed 994 hPa vs Normal 1008 hPa — $-14\text{ hPa}$)
2. **Diagnostic Summary**:
   > *"CRITICAL COMPOUND ANOMALY: Observed rainfall is 696% above seasonal baseline, accompanied by an unusual +9.9°C heat spike and a severe 14 hPa atmospheric pressure drop indicating deep depression."*

---

### Step 7: FastAPI REST Endpoint
The backend processes the request and responds with typed JSON in $<15\text{ms}$:

```json
{
  "location": "Bengaluru",
  "timestamp": "2024-09-10T12:00:00",
  "is_anomaly": true,
  "anomaly_score": 0.94,
  "severity": "CRITICAL",
  "anomaly_type": "Compound Weather Anomaly",
  "contributors": [
    {"feature": "rainfall", "contribution_pct": 52.4, "observed": 145.0, "expected": 18.2, "unit": "mm", "direction": "HIGH"},
    {"feature": "temperature", "contribution_pct": 28.1, "observed": 37.0, "expected": 27.1, "unit": "°C", "direction": "HIGH"},
    {"feature": "pressure", "contribution_pct": 19.5, "observed": 994.0, "expected": 1008.0, "unit": "hPa", "direction": "LOW"}
  ],
  "explanation": "Observed rainfall is 696% above seasonal baseline with significant temperature and pressure deviations."
}
```

---

### Step 8: Interactive Dashboard Visualization
1. **Interactive India Map**: The station marker for Bengaluru glows **🔴 Crimson Red**.
2. **Dial Gauges**: Temperature, Rainfall, and Pressure needles swing far past the shaded green "Normal Corridor" ($\mu \pm 2\sigma$).
3. **Contributor Breakdown**: A ranked horizontal bar chart shows judges exactly which factors drove the alert.

---

## 🖥️ 4. The 4 Dashboard Views

1. **National Anomaly Overview (Map View)**:
   - High-level bird's-eye view of India with real-time status pins across monitored cities.
   - Allows disaster management officials to instantly spot regional anomalies.
2. **Station Deep-Dive**:
   - Detailed station view comparing observed weather against seasonal normals.
3. **Interactive "What-If" Prediction Studio**:
   - Interactive sliders for all 5 weather parameters.
   - Allows judges to simulate live scenarios (e.g. *"What happens if Mumbai gets 200mm rain?"* or *"What if Delhi hits 47°C in May vs December?"*).
4. **Historical Trend Analysis**:
   - Multi-year charts showing actual readings plotted against historical normal corridors and seasonal anomaly distributions.

---

## 🏆 5. SIH Pitch Summary

> *"We didn't just build a weather app. We created an **AI-powered early anomaly intelligence platform** that understands regional seasonality, catches multi-variable compound anomalies that static rules miss, and explains the meteorological drivers in plain language to disaster managers."*

---

## 🛠️ 6. Technology Stack

- **Machine Learning**: Scikit-learn (Isolation Forest), Pandas, NumPy, SciPy, Joblib
- **Backend API**: FastAPI, Pydantic v2, Uvicorn, SQLAlchemy (SQLite / PostgreSQL)
- **Frontend**: React (Vite), Tailwind CSS, Lucide Icons, Recharts, Leaflet
- **Data Source**: NOAA ISD / ICAO METAR station observations (Bangalore HAL Airport anchor + calibrated multi-city profiles)
