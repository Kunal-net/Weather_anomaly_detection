# Antigravity Agent Guidelines — Weather Anomaly Detection System

You are pair programming on the **Weather Anomaly Detection, Monitoring and Explainability Platform (SIH Prototype)**.

## Key Project Truths
1. **Never use static thresholding** (e.g. `temp > 35`). The system is based on **deviation from historical location- and season-specific baselines**.
2. **Dual-Engine Detection**: Statistical Z-scores + Scikit-learn Isolation Forest on multivariable feature vectors.
3. **Calibrated Anomaly Score**: Scaled to $[0.00, 1.00]$ with four severities:
   - `0.00 - 0.39`: NORMAL (Emerald green)
   - `0.40 - 0.69`: WATCH (Amber yellow)
   - `0.70 - 0.89`: HIGH (Orange)
   - `0.90 - 1.00`: CRITICAL (Crimson red)
4. **Mandatory Explainability**: Every prediction must explain *why* it is anomalous (e.g. contributor ranking, percentage departure from expected seasonal normal, human-readable rationale).
5. **Always consult `memory.md` and `rules.md`** before making architectural changes or creating new components.

## Project Directories
- `data/`: Raw CSVs and processed baseline tables.
- `ml/`: Preprocessing, baseline calculation, Isolation Forest, explainability engine, training scripts.
- `backend/`: FastAPI application with typed Pydantic schemas, modular routes, and SQLAlchemy.
- `frontend/`: React + Vite + Tailwind CSS dashboard with Leaflet map, Recharts, and Prediction Studio.
- `docs/`: Architecture diagrams, SIH demo guide, and presentation scripts.
