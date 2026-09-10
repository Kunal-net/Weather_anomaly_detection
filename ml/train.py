"""
End-to-End ML Training and Artifact Serialization Pipeline.

Loads cleaned observations, computes and saves location-monthly baseline distributions,
trains the Isolation Forest and StandardScaler, evaluates extreme meteorological
scenarios, and runs self-validation tests (normal < 0.40, cloudburst > 0.90, latency < 15ms).
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Dict, Tuple

# Ensure project root is in sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

import pandas as pd

from ml.anomaly_engine import DualAnomalyEngine, MLAnomalyEngine, StatisticalEngine
from ml.baseline import BaselineCalculator
from ml.explainability import ExplainabilityEngine
from ml.preprocessing import build_and_save_cleaned_dataset


def run_training_pipeline(
    data_path: Path = Path("data/processed/weather_cleaned.csv"),
    baseline_path: Path = Path("data/processed/baseline_statistics.json"),
    model_path: Path = Path("ml/models/isolation_forest.joblib"),
    scaler_path: Path = Path("ml/models/scaler.joblib"),
) -> Tuple[DualAnomalyEngine, Dict[str, Any]]:
    """Executes the full training and artifact generation pipeline (Prompt 1.19).

    Args:
        data_path (Path): Path to clean weather observations CSV.
        baseline_path (Path): Destination path for baseline statistics JSON.
        model_path (Path): Destination path for isolation_forest.joblib.
        scaler_path (Path): Destination path for scaler.joblib.

    Returns:
        Tuple[DualAnomalyEngine, Dict[str, Any]]: Trained dual-engine and validation report.
    """
    print("=" * 70)
    print("🚀 WEATHER ANOMALY DETECTION — TRAINING & SERIALIZATION PIPELINE")
    print("=" * 70)

    # 1. Ensure dataset exists
    if not data_path.exists():
        print(f"📦 Generating cleaned observations dataset at '{data_path}'...")
        df = build_and_save_cleaned_dataset(data_path)
    else:
        print(f"📦 Loading cleaned dataset from '{data_path}'...")
        df = pd.read_csv(data_path)

    print(f"   Shape: {df.shape[0]:,} rows across {df['location'].nunique()} cities.")

    # 2. Compute and save historical baseline distributions
    print("\n📊 Computing location & monthly historical baselines...")
    calc = BaselineCalculator(df, sigma_min=0.1, auto_compute=True)
    calc.save_to_json(baseline_path)
    calc.save_to_json("data/processed/baseline_stats.json")
    print(f"   Saved baseline statistics to '{baseline_path}'.")

    # 3. Initialize and train ML Anomaly Engine (Isolation Forest)
    print("\n🌲 Training Isolation Forest (n_estimators=150, contamination=0.03, random_state=42)...")
    ml_engine = MLAnomalyEngine(
        n_estimators=150,
        contamination=0.03,
        random_state=42,
        n_jobs=-1,
        baseline_calculator=calc,
    )
    ml_engine.fit(df)

    # 4. Save trained model artifacts
    ml_engine.save(model_path=model_path, scaler_path=scaler_path)
    # Also save to scaler.joblib in root/models if needed
    scaler_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"   Saved model to '{model_path}' and scaler to '{scaler_path}'.")

    # 5. Build Dual-Engine (Statistical + ML)
    stat_engine = StatisticalEngine(baseline_calculator=calc, sigma_min=0.1)
    dual_engine = DualAnomalyEngine(stat_engine=stat_engine, ml_engine=ml_engine)

    # 6. Execute Self-Validation Suite (Prompt 1.20)
    validation_report = run_self_validation(dual_engine)

    print("\n" + "=" * 70)
    print("✅ TRAINING & SELF-VALIDATION COMPLETE")
    print("=" * 70)
    return dual_engine, validation_report


def run_self_validation(dual_engine: DualAnomalyEngine) -> Dict[str, Any]:
    """Runs self-validation checks on normal and extreme scenarios (Prompt 1.20).

    Validates:
    - Normal observation score < 0.40 (NORMAL)
    - Cloudburst / extreme shock score > 0.90 (CRITICAL)
    - Single observation inference latency < 15ms

    Args:
        dual_engine (DualAnomalyEngine): Initialized dual-engine instance.

    Returns:
        Dict[str, Any]: Validation metrics dictionary.
    """
    print("\n🧪 Running Pipeline Self-Validation Suite (Prompt 1.20)...")
    explain_engine = ExplainabilityEngine()

    # Scenario 1: Normal September observation in Bengaluru
    normal_obs = {
        "temperature": 27.2,
        "relative_humidity": 73.0,
        "pressure": 1008.5,
        "wind_speed": 3.4,
        "rainfall": 12.0,
    }

    t0 = time.perf_counter()
    normal_res = dual_engine.predict(normal_obs, "Bengaluru", 9)
    t_normal = (time.perf_counter() - t0) * 1000.0

    print(f"\n[Test 1: Normal Scenario]")
    print(f"   Observation: {normal_obs}")
    print(f"   Final Score: {normal_res['final_score']:.4f} (Severity: {normal_res['severity']})")
    print(f"   Latency:     {t_normal:.3f} ms")

    assert normal_res["final_score"] < 0.40, (
        f"Validation Failed: Normal observation score {normal_res['final_score']} >= 0.40"
    )
    assert normal_res["severity"] == "NORMAL", (
        f"Validation Failed: Expected severity NORMAL, got {normal_res['severity']}"
    )
    print("   Status:      ✅ PASSED (score < 0.40)")

    # Scenario 2: Severe Cloudburst / Compound Anomaly in Bengaluru
    cloudburst_obs = {
        "temperature": 37.0,
        "relative_humidity": 96.0,
        "pressure": 992.0,
        "wind_speed": 16.5,
        "rainfall": 165.0,
    }

    t0 = time.perf_counter()
    cloudburst_res = dual_engine.predict(cloudburst_obs, "Bengaluru", 9)
    t_cloudburst = (time.perf_counter() - t0) * 1000.0

    print(f"\n[Test 2: Cloudburst Scenario]")
    print(f"   Observation: {cloudburst_obs}")
    print(f"   Final Score: {cloudburst_res['final_score']:.4f} (Severity: {cloudburst_res['severity']})")
    print(f"   Anomaly Type: {cloudburst_res['anomaly_type']}")
    print(f"   Latency:     {t_cloudburst:.3f} ms")

    # Generate explainability output
    exp = explain_engine.explain(
        z_scores=cloudburst_res["z_scores"],
        severity=cloudburst_res["severity"],
        anomaly_type=cloudburst_res["anomaly_type"],
        obs=cloudburst_obs,
        base=cloudburst_res["baseline"],
        location="Bengaluru",
        month=9,
    )
    print(f"   Explanation: {exp['explanation']}")

    assert cloudburst_res["final_score"] > 0.90, (
        f"Validation Failed: Cloudburst observation score {cloudburst_res['final_score']} <= 0.90"
    )
    assert cloudburst_res["severity"] == "CRITICAL", (
        f"Validation Failed: Expected severity CRITICAL, got {cloudburst_res['severity']}"
    )
    print("   Status:      ✅ PASSED (score > 0.90)")

    # Latency benchmark across 50 iterations
    latencies: list[float] = []
    for _ in range(50):
        t0 = time.perf_counter()
        dual_engine.predict(cloudburst_obs, "Bengaluru", 9)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    avg_latency = sum(latencies) / len(latencies)
    max_latency = max(latencies)
    print(f"\n[Latency Benchmark (50 iterations)]")
    print(f"   Average Latency: {avg_latency:.3f} ms")
    print(f"   Max Latency:     {max_latency:.3f} ms")
    print(f"   Threshold:       < 15.000 ms")

    assert avg_latency < 15.0, f"Latency check failed: {avg_latency:.2f}ms >= 15ms"
    print("   Status:          ✅ PASSED (Latency < 15ms)")

    return {
        "normal_score": normal_res["final_score"],
        "normal_severity": normal_res["severity"],
        "cloudburst_score": cloudburst_res["final_score"],
        "cloudburst_severity": cloudburst_res["severity"],
        "avg_latency_ms": round(avg_latency, 3),
        "validation_passed": True,
    }


if __name__ == "__main__":
    run_training_pipeline()
