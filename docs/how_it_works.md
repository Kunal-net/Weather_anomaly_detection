# 🌦️ How the Weather Anomaly Detection System Works — Complete Guide

> A beginner-friendly, end-to-end walkthrough of the architecture, data pipeline, AI/ML models, and user experience.

---

## 💡 1. The Core Idea: What Makes This System Different?

Most weather applications answer:
> **"What is the weather right now?"** (e.g., *"It is 35°C in Bengaluru."*)

Our platform answers a far more critical decision-support question:
> **"Is this weather normal for this specific location and this exact time of year, and if not, *how dangerous is it and why*?"**

### ❌ The Old Way: Static Thresholds
A naive approach would say:
```python
if temperature > 35:
    alert("Heatwave!")
```
This fails in reality:
- **35°C in Delhi in May** is completely **normal** (summer).
- **35°C in Bengaluru or Shimla in January** is an **extreme, unprecedented heat anomaly**.

### ✅ Our Way: Context-Aware Historical Baselines
Our system compares incoming weather against **what is historically expected for that city and that month**.

---

## 🏛️ 2. High-Level System Architecture

The entire platform is built in three interconnected layers:

```text
┌────────────────────────────────────────────────────────┐
│                   1. DATA FOUNDATION                   │
│   Raw Weather Data (METAR/ISD) → Clean Data            │
│   → Historical Baselines (Mean, Std Dev, Percentiles)  │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│               2. DUAL-ENGINE AI / ML BRAIN             │
│   ├── Statistical Layer: Standardized Z-Score Deviations│
│   └── Machine Learning: Scikit-learn Isolation Forest   │
│   → Calibrated Anomaly Score (0.00 to 1.00)            │
│   → Severity Engine (NORMAL / WATCH / HIGH / CRITICAL) │
│   → Explainability Engine (Contributor % Breakdown)    │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│              3. DELIVERY & USER EXPERIENCE             │
│   FastAPI REST Backend (Microsecond Inference)         │
│   → React + Leaflet Interactive National Dashboard     │
│   → Interactive "What-If" Prediction Studio            │
└────────────────────────────────────────────────────────┘
```

---

## 🔍 3. The Life of a Weather Reading (Step-by-Step Walkthrough)

To understand how the system works end-to-end, let's trace a single extreme weather event through the pipeline:

### 📍 The Scenario
A sensor station in **Bengaluru** records this reading on a day in **September**:
- **Temperature:** $37.0^\circ\text{C}$
- **Rainfall:** $145.0\text{ mm}$
- **Relative Humidity:** $92\%$
- **Atmospheric Pressure:** $994.0\text{ hPa}$
- **Wind Speed:** $14.5\text{ m/s}$

Here is what happens behind the scenes in under 15 milliseconds:

---

### Step 1: Input Validation & Preprocessing
1. **Physical Bounds Check**: Checks if the numbers are physically possible (e.g. humidity between 0–100%, pressure between 870–1085 hPa). If a sensor broke and sent $500\%$ humidity, it is flagged as bad data, not a valid weather anomaly.
2. **Feature Engineering**: Generates cyclical time coordinates ($\sin, \cos$ of day of year) and rolling trend features.

---

### Step 2: Historical Baseline Lookup
The system instantly looks up the precomputed historical statistics for **Bengaluru in September**:

| Variable | September Historical Normal ($\mu$) | Standard Deviation ($\sigma$) | Observed Reading | Deviation ($\Delta$) |
| :--- | :--- | :--- | :--- | :--- |
| **Temperature** | $27.1^\circ\text{C}$ | $\pm 1.8^\circ\text{C}$ | $37.0^\circ\text{C}$ | **$+9.9^\circ\text{C}$** |
| **Rainfall** | $18.2\text{ mm}$ | $\pm 14.5\text{ mm}$ | $145.0\text{ mm}$ | **$+126.8\text{ mm}$** |
| **Pressure** | $1008.0\text{ hPa}$ | $\pm 2.1\text{ hPa}$ | $994.0\text{ hPa}$ | **$-14.0\text{ hPa}$** |
| **Humidity** | $74.0\%$ | $\pm 8.2\%$ | $92.0\%$ | **$+18.0\%$** |
| **Wind Speed** | $3.5\text{ m/s}$ | $\pm 1.2\text{ m/s}$ | $14.5\text{ m/s}$ | **$+11.0\text{ m/s}$** |

---

### Step 3: Dual-Engine Detection

#### Engine 1: The Statistical Z-Score Layer
Calculates how many standard deviations ($Z$) each variable is from normal:
$$Z = \frac{X_{\text{observed}} - \mu}{\sigma}$$
- Rainfall: $Z = \frac{145.0 - 18.2}{14.5} = \mathbf{+8.74\sigma}$ (Extreme departure!)
- Temperature: $Z = \frac{37.0 - 27.1}{1.8} = \mathbf{+5.50\sigma}$ (Severe heat anomaly!)
- Pressure: $Z = \frac{994.0 - 1008.0}{2.1} = \mathbf{-6.67\sigma}$ (Severe low pressure depression!)

#### Engine 2: The Machine Learning Layer (Isolation Forest)
Why do we need machine learning if we already have Z-scores?
> **Compound Anomalies!**  
> Sometimes individual variables are only slightly elevated (e.g. $Z = +1.8$), but their **unusual combination** (e.g. high heat + dense humidity + plunging pressure) represents a developing cyclone or severe cloudburst.  
> An **Isolation Forest** isolates unusual data points in a high-dimensional feature space because abnormal combinations require far fewer decision tree splits to isolate than normal weather patterns.

---

### Step 4: Calibrated Anomaly Scoring
The outputs of the statistical deviations and the Isolation Forest decision function are blended and normalized onto a clean scale from **`0.00` to `1.00`**:

$$\text{Final Anomaly Score} = \mathbf{0.94}\text{ (94\%)}$$

---

### Step 5: Severity Classification
The score is mapped to one of four standardized operational tiers:

| Score Range | Severity Level | UI Color | Meaning |
| :--- | :--- | :--- | :--- |
| `0.00 - 0.39` | 🟢 **NORMAL** | Emerald Green | Weather is behaving according to seasonal expectations. |
| `0.40 - 0.69` | 🟡 **WATCH** | Amber Yellow | Noticeable departure; conditions should be monitored. |
| `0.70 - 0.89` | 🟠 **HIGH** | Vibrant Orange | Significant anomaly; advisory recommended. |
| `0.90 - 1.00` | 🔴 **CRITICAL** | Crimson Red | Extreme deviation or severe compound weather anomaly. |

In our scenario $\to$ **CRITICAL (0.94)**.

---

### Step 6: The Explainability Engine
Judges and disaster managers cannot act on a mysterious black-box number like *"0.94"*. They need to know **why**.

The explainability engine:
1. **Ranks Feature Contributions**:
   - 🌧️ **Rainfall:** $52.4\%$ contribution (Observed 145mm vs Normal 18.2mm — $+696\%$)
   - 🌡️ **Temperature:** $28.1\%$ contribution (Observed 37°C vs Normal 27.1°C — $+9.9°C$)
   - 📉 **Pressure:** $19.5\%$ contribution (Observed 994 hPa vs Normal 1008 hPa — severe drop)
2. **Generates Human-Readable Diagnostic Rationale**:
   > *"CRITICAL COMPOUND ANOMALY: Observed rainfall is 696% above seasonal baseline, accompanied by an unusual +9.9°C heat spike and a severe 14 hPa atmospheric pressure drop indicating deep depression."*

---

### Step 7: FastAPI REST API Delivery
FastAPI serializes the result into a clean JSON response in $<15\text{ms}$:

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
  "explanation": "Observed rainfall is 696% above seasonal baseline..."
}
```

---

### Step 8: Interactive React Dashboard Visualization
The frontend receives the API response and instantly updates:
1. **Interactive India Map**: The pin on Bengaluru glows **Crimson Red (🔴 CRITICAL)**.
2. **Executive Status Banner**: Counters update (Total Monitored, Critical alerts).
3. **Station Deep-Dive**: Visual dial gauges show the observed needle way outside the shaded green "Normal Corridor" ($\mu \pm 2\sigma$).
4. **Explainability Visualizer**: Color-coded horizontal bar chart ranking the top 3 drivers.

---

## 🎮 4. The 4 Key Dashboard Views (User Experience)

1. **National Anomaly Overview (Map View)**:
   - High-level bird’s eye view of India with real-time station statuses.
   - Allows disaster management officials to immediately spot regional anomaly clusters.
2. **Location Deep-Dive**:
   - Select any city (e.g. Bengaluru, Mumbai, Delhi, Chennai).
   - See current sensor values side-by-side with historical seasonal norms.
3. **Interactive "What-If" Prediction Studio**:
   - Interactive sliders for Temperature, Rainfall, Humidity, Pressure, and Wind Speed.
   - Allows users or judges during the demo to test hypothetical scenarios live:
     - *"What if Bengaluru suddenly gets 150mm rain tomorrow?"*
     - *"What if Delhi hits 48°C in May vs in December?"*
   - Watch the score and explainability change in real-time!
4. **Historical Trend Analysis**:
   - Multi-year charts showing actual weather vs normal corridor.
   - Anomaly frequency breakdowns across seasons.

---

## 🏆 5. Summary: Why This Wins at SIH

| Feature | Typical Student Project | Our SIH Platform |
| :--- | :--- | :--- |
| **Logic** | Static `if temp > 35` threshold | Contextual deviation from seasonal location baselines |
| **Model** | Single basic classifier | Dual-Engine: Statistical Z-scores + Scikit-learn Isolation Forest |
| **Output** | Just "Yes / No" or a raw score | Calibrated score ($0–1$) + 4 Severities + Contributor % Rankings |
| **Explainability** | Black box | Clear natural-language rationale for decision-makers |
| **Demo Readiness** | Boring command-line script | Interactive India Map + Live "What-If" Simulation Studio |
