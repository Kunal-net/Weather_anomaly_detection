# System Architecture — Weather Anomaly Detection Platform

```mermaid
flowchart TD
    subgraph Data Layer
        A1[Raw Weather Data: output.csv / METAR / ISD] --> B1[Data Preprocessing & Bounds Validation]
        B1 --> C1[Temporal & Rolling Feature Engineering]
        C1 --> D1[(Clean Weather DB / Store)]
    end

    subgraph Intelligence Layer
        D1 --> E1[Historical Baseline Calculator\nLocation + Month: Mean, Std, IQR]
        E1 --> F1[Statistical Layer\nStandardized Z-scores]
        C1 --> G1[Isolation Forest Model\nUnsupervised Anomaly Detection]
        F1 --> H1[Calibrated Anomaly Scoring Engine\nScore: 0.00 to 1.00]
        G1 --> H1
        H1 --> I1[Severity Classifier\nNormal | Watch | High | Critical]
        H1 --> J1[Anomaly Type Classifier\nHeatwave, Extreme Rain, Storm, Compound]
        H1 --> K1[Explainability Engine\nFeature Contribution % & Natural Language Rationale]
    end

    subgraph API & Backend
        I1 --> L1[FastAPI Application]
        J1 --> L1
        K1 --> L1
        L1 --> M1[(Database: Observations & Anomaly Logs)]
        L1 --> N1[REST Endpoints:\n/health\n/locations\n/weather/{loc}\n/anomalies\n/predict\n/history/{loc}]
    end

    subgraph User Experience
        N1 --> O1[Executive Anomaly Overview & India Map]
        N1 --> P1[Location Deep-Dive & Baseline Gauges]
        N1 --> Q1[Interactive What-If Prediction Studio]
        N1 --> R1[Historical Analysis & Trend Charts]
    end
```

---

## 1. Data Pipeline

1. **Ingestion & Validation**:
   - Parses raw METAR/ISD datasets (`DATE`, `temperature`, `dew_point_temperature`, `relative_humidity`, `altimeter` as pressure, `wind_speed`, `wind_direction`, `visibility`, weather phenomena codes `pres_wx_MW1`).
   - Validates physical domain bounds to reject corrupted sensor records.
2. **Feature Engineering**:
   - Temporal: `month`, `day_of_year`, cyclical `sin(2π * day / 365)`, `cos(2π * day / 365)`.
   - Statistical context: Rolling 7-day and 30-day means and precipitation accumulation.
3. **Baseline Store**:
   - Location- and month-indexed statistical parameters ($\mu, \sigma, Q_{25}, Q_{75}$) exported to JSON for $< 1\text{ms}$ live API inference.

---

## 2. Dual Anomaly Engine

$$\text{Final Score} = w_1 \cdot \text{Normalized Z-Score} + w_2 \cdot \text{Isolation Forest Anomaly Score}$$

- **Statistical Deviation**: Pinpoints how many standard deviations a single metric deviates from historical normal.
- **Isolation Forest**: Identifies multidimensional compound anomalies (e.g. moderate heat + extreme humidity + sharp pressure drop that individually might look benign but together indicate an unprecedented storm event).

---

## 3. Explainability Model

For every observation, the system computes:
$$\text{Deviation}_i = X_{\text{obs}, i} - \mu_{\text{expected}, i}$$
$$\text{Relative Contribution}_i = \frac{|Z_i|}{\sum_j |Z_j|} \times 100\%$$

Enabling clear diagnostic explanations:
> *"Critical Compound Anomaly (Score: 94%). Primary drivers: Extreme Rainfall (+696% vs September normal), High Temperature (+9.9°C departure), and Severe Pressure Drop (-14 hPa)."*
