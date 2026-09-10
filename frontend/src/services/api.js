import axios from 'axios';
import {
  MOCK_LOCATIONS,
  MOCK_PREDICTION_RESPONSE,
  MOCK_WEATHER_SUMMARY,
} from './mockData';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Fetches all monitored Indian stations with active anomaly severity levels.
 * Falls back to MOCK_LOCATIONS if backend is offline.
 */
export const fetchLocations = async () => {
  try {
    const res = await apiClient.get('/locations');
    return res.data;
  } catch (err) {
    console.warn('[AeroSense-AI] Backend /locations offline, using mock locations:', err.message);
    return MOCK_LOCATIONS;
  }
};

/**
 * Fetches latest weather observation and historical normal departures for a city.
 */
export const fetchWeatherForLocation = async (location) => {
  try {
    const res = await apiClient.get(`/weather/${encodeURIComponent(location)}`);
    return res.data;
  } catch (err) {
    console.warn(`[AeroSense-AI] Backend /weather/${location} offline, using mock summary:`, err.message);
    return { ...MOCK_WEATHER_SUMMARY, location, city: location };
  }
};

/**
 * Fetches 30-day historical time-series corridor with +/- 2*sigma bounds for charts.
 */
export const fetchHistoricalCorridor = async (location, variable = 'temperature', days = 30) => {
  try {
    const res = await apiClient.get(`/history/${encodeURIComponent(location)}`, {
      params: { variable, days },
    });
    return res.data;
  } catch (err) {
    console.warn(`[AeroSense-AI] Backend /history/${location} offline, generating mock points:`, err.message);
    // Generate fallback series points
    const points = [];
    const now = new Date();
    for (let i = days - 1; i >= 0; i--) {
      const d = new Date(now);
      d.setDate(d.getDate() - i);
      const baseVal = variable === 'temperature' ? 27.0 : variable === 'rainfall' ? 15.0 : 1010.0;
      const sigma = variable === 'temperature' ? 2.5 : variable === 'rainfall' ? 20.0 : 4.0;
      const noise = (Math.sin(i * 0.5) + (Math.random() - 0.5)) * sigma * 0.8;
      const observed = Math.max(0, Math.round((baseVal + noise) * 10) / 10);
      points.push({
        timestamp: d.toISOString().split('T')[0],
        observed,
        expected_normal: baseVal,
        upper_bound: Math.round((baseVal + 2 * sigma) * 10) / 10,
        lower_bound: Math.max(0, Math.round((baseVal - 2 * sigma) * 10) / 10),
        is_anomaly: Math.random() < 0.08,
      });
    }
    return {
      location,
      variable,
      unit: variable === 'temperature' ? '°C' : variable === 'rainfall' ? 'mm' : 'hPa',
      days,
      data: points,
    };
  }
};

/**
 * Fetches recent national anomaly events log.
 */
export const fetchRecentAnomalies = async (limit = 20) => {
  try {
    const res = await apiClient.get('/anomalies', { params: { limit } });
    return res.data;
  } catch (err) {
    console.warn('[AeroSense-AI] Backend /anomalies offline, returning mock anomaly list:', err.message);
    return [
      {
        id: 1,
        location: 'Bengaluru',
        city: 'Bengaluru',
        timestamp: new Date(Date.now() - 7200000).toISOString(),
        anomaly_score: 0.94,
        severity: 'CRITICAL',
        current_severity: 'CRITICAL',
        anomaly_type: 'Extreme Rainfall',
        explanation: 'CRITICAL ALERT in Bengaluru: Severe Extreme Rainfall detected (+697% above baseline).',
        contributors: MOCK_PREDICTION_RESPONSE.contributors,
      },
    ];
  }
};

/**
 * Live inference: Posts real-time observation sliders to Dual-Engine anomaly predictor.
 */
export const predictWeatherAnomaly = async (payload) => {
  try {
    const res = await apiClient.post('/predict', payload);
    return res.data;
  } catch (err) {
    console.warn('[AeroSense-AI] Backend /predict offline, returning simulated prediction:', err.message);
    return {
      ...MOCK_PREDICTION_RESPONSE,
      location: payload.location || 'Bengaluru',
      city: payload.location || 'Bengaluru',
    };
  }
};

/**
 * Health probe check.
 */
export const checkHealth = async () => {
  try {
    const res = await apiClient.get('/health');
    return res.data;
  } catch (err) {
    return { status: 'mock_fallback', model_loaded: false, database_connectivity: false };
  }
};
