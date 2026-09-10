// Starter mock data for frontend development
// Allows the React dashboard to run fully independently before backend API is running!

export const MOCK_LOCATIONS = [
  { location: "Bengaluru", lat: 12.9716, lon: 77.5946, state: "Karnataka", severity: "CRITICAL", anomaly_score: 0.94, temperature: 37.0, rainfall: 145.0 },
  { location: "Delhi", lat: 28.7041, lon: 77.1025, state: "Delhi", severity: "NORMAL", anomaly_score: 0.18, temperature: 31.0, rainfall: 0.0 },
  { location: "Mumbai", lat: 19.0760, lon: 72.8777, state: "Maharashtra", severity: "WATCH", anomaly_score: 0.48, temperature: 29.5, rainfall: 45.0 },
  { location: "Chennai", lat: 13.0827, lon: 80.2707, state: "Tamil Nadu", severity: "NORMAL", anomaly_score: 0.22, temperature: 32.0, rainfall: 5.0 },
  { location: "Kolkata", lat: 22.5726, lon: 88.3639, state: "West Bengal", severity: "HIGH", anomaly_score: 0.74, temperature: 34.5, rainfall: 68.0 },
  { location: "Hyderabad", lat: 17.3850, lon: 78.4867, state: "Telangana", severity: "NORMAL", anomaly_score: 0.15, temperature: 29.0, rainfall: 2.0 },
  { location: "Shimla", lat: 31.1048, lon: 77.1734, state: "Himachal Pradesh", severity: "NORMAL", anomaly_score: 0.12, temperature: 18.0, rainfall: 0.0 },
  { location: "Jaipur", lat: 26.9124, lon: 75.7873, state: "Rajasthan", severity: "NORMAL", anomaly_score: 0.25, temperature: 35.0, rainfall: 0.0 },
  { location: "Ahmedabad", lat: 23.0225, lon: 72.5714, state: "Gujarat", severity: "NORMAL", anomaly_score: 0.31, temperature: 36.0, rainfall: 0.0 },
  { location: "Bhubaneswar", lat: 20.2961, lon: 85.8245, state: "Odisha", severity: "WATCH", anomaly_score: 0.55, temperature: 33.0, rainfall: 35.0 }
];

export const MOCK_PREDICTION_RESPONSE = {
  location: "Bengaluru",
  timestamp: new Date().toISOString(),
  is_anomaly: true,
  anomaly_score: 0.94,
  severity: "CRITICAL",
  anomaly_type: "Compound Weather Anomaly",
  contributors: [
    { feature: "rainfall", contribution_pct: 52.4, observed: 145.0, expected: 18.2, unit: "mm", direction: "HIGH" },
    { feature: "temperature", contribution_pct: 28.1, observed: 37.0, expected: 27.1, unit: "°C", direction: "HIGH" },
    { feature: "pressure", contribution_pct: 19.5, observed: 994.0, expected: 1008.0, unit: "hPa", direction: "LOW" },
    { feature: "relative_humidity", contribution_pct: 0.0, observed: 92.0, expected: 74.0, unit: "%", direction: "HIGH" },
    { feature: "wind_speed", contribution_pct: 0.0, observed: 14.5, expected: 3.5, unit: "m/s", direction: "HIGH" }
  ],
  explanation: "CRITICAL COMPOUND ANOMALY: Observed rainfall is 696% above seasonal baseline, accompanied by an anomalous +9.9°C heat spike and a severe 14 hPa atmospheric pressure drop indicating deep depression."
};
