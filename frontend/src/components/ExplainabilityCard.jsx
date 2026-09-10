import React from 'react';
import { ShieldAlert, Info, Activity, AlertTriangle } from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from 'recharts';

export default function ExplainabilityCard({
  explanation,
  contributors = [],
  severity = 'CRITICAL',
}) {
  const defaultExplanation =
    explanation ||
    'CRITICAL ALERT in Bengaluru: Severe Extreme Rainfall detected (+697% above baseline) accompanied by a rapid pressure drop (-19.5 hPa). High risk of localized urban flash flooding.';

  const defaultContributors = [
    { feature: 'rainfall', contribution_pct: 52.4, observed: 145.0, expected: 18.2, unit: 'mm' },
    { feature: 'pressure', contribution_pct: 28.1, observed: 994.0, expected: 1013.5, unit: 'hPa' },
    { feature: 'wind_speed', contribution_pct: 12.5, observed: 16.5, expected: 3.2, unit: 'm/s' },
    { feature: 'temperature', contribution_pct: 7.0, observed: 24.0, expected: 26.5, unit: '°C' },
  ];

  const dataList = contributors.length > 0 ? contributors : defaultContributors;

  // Format data for Recharts horizontal BarChart
  const chartData = dataList.map((item) => ({
    name:
      item.feature === 'rainfall'
        ? 'Rainfall'
        : item.feature === 'pressure'
        ? 'Pressure'
        : item.feature === 'temperature'
        ? 'Temperature'
        : item.feature === 'relative_humidity'
        ? 'Humidity'
        : item.feature === 'wind_speed'
        ? 'Wind Speed'
        : item.feature,
    contribution: item.contribution_pct,
    observed: item.observed,
    expected: item.expected,
    unit: item.unit || '',
  }));

  const getBannerStyle = (sev) => {
    switch (sev) {
      case 'CRITICAL':
        return 'bg-gradient-to-r from-red-950/80 via-red-900/60 to-slate-900 border-red-800/60 text-red-200';
      case 'HIGH':
        return 'bg-gradient-to-r from-orange-950/80 via-orange-900/60 to-slate-900 border-orange-800/60 text-orange-200';
      case 'WATCH':
        return 'bg-gradient-to-r from-amber-950/80 via-amber-900/60 to-slate-900 border-amber-800/60 text-amber-200';
      default:
        return 'bg-gradient-to-r from-emerald-950/80 via-emerald-900/60 to-slate-900 border-emerald-800/60 text-emerald-200';
    }
  };

  const colors = ['#ef4444', '#f97316', '#f59e0b', '#3b82f6', '#10b981'];

  return (
    <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl space-y-6">
      {/* 1. Prompt 4.16: High-Contrast Diagnostic Alert Banner */}
      <div className={`p-4 rounded-xl border ${getBannerStyle(severity)} shadow-lg flex items-start gap-3.5 relative overflow-hidden`}>
        <div className="p-2 rounded-lg bg-slate-950/60 border border-white/10 shrink-0 mt-0.5">
          <ShieldAlert className="w-5 h-5 text-amber-400 animate-pulse" />
        </div>
        <div>
          <div className="text-[10px] uppercase font-extrabold tracking-widest text-white/70 mb-1">
            Explainable AI Diagnostic Rationale
          </div>
          <p className="text-xs md:text-sm font-semibold leading-relaxed">
            {defaultExplanation}
          </p>
        </div>
      </div>

      {/* 2. Prompt 4.17: Horizontal Bar Chart Ranking Contributor Variables */}
      <div className="space-y-4">
        <div className="flex items-center justify-between border-b border-slate-800 pb-3">
          <div className="flex items-center gap-2">
            <Activity className="w-4 h-4 text-cyan-400" />
            <h3 className="text-sm font-bold text-white uppercase tracking-wider">
              Contributor Variable Ranking (% Influence)
            </h3>
          </div>
          <span className="text-xs text-slate-400 font-mono">
            SHAP / Feature Attribution Engine
          </span>
        </div>

        <div className="h-56 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              layout="vertical"
              data={chartData}
              margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
            >
              <XAxis
                type="number"
                domain={[0, 100]}
                unit="%"
                stroke="#64748b"
                fontSize={11}
                tickFormatter={(val) => `${val}%`}
              />
              <YAxis
                type="category"
                dataKey="name"
                stroke="#94a3b8"
                fontSize={12}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-slate-950 border border-slate-700 p-3 rounded-xl shadow-xl text-xs space-y-1">
                        <div className="font-bold text-cyan-400">{data.name}</div>
                        <div className="text-slate-300">
                          Contribution:{' '}
                          <span className="font-mono font-bold text-white">
                            {data.contribution.toFixed(1)}%
                          </span>
                        </div>
                        <div className="text-slate-400 text-[11px]">
                          Observed: {data.observed} {data.unit} (Normal: {data.expected} {data.unit})
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="contribution" radius={[0, 8, 8, 0]} barSize={20}>
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Detailed Breakdown Pill List */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 border-t border-slate-800">
          {chartData.map((item, idx) => (
            <div key={idx} className="bg-slate-950/60 border border-slate-800 rounded-xl p-2.5 text-xs">
              <div className="text-slate-400 font-medium">{item.name}</div>
              <div className="text-sm font-black text-white font-mono mt-0.5">
                {item.contribution.toFixed(1)}%
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                {item.observed} {item.unit} vs {item.expected} {item.unit}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
