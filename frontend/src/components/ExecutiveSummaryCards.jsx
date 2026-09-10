import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle, Radio } from 'lucide-react';

export default function ExecutiveSummaryCards({ locations = [] }) {
  const totalCount = locations.length;
  const criticalCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'CRITICAL'
  ).length;
  const highCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'HIGH'
  ).length;
  const watchCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'WATCH'
  ).length;
  const normalCount = locations.filter(
    (l) => (l.severity || l.current_severity) === 'NORMAL'
  ).length;

  const cards = [
    {
      title: 'Total Stations Monitored',
      count: totalCount,
      subtitle: '10 Indian Climate Zones',
      color: 'cyan',
      borderColor: 'border-slate-800 hover:border-cyan-500/40',
      textColor: 'text-white',
      badgeBg: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
      icon: Radio,
      glow: 'shadow-cyan-500/5',
      indicator: 'bg-cyan-400',
    },
    {
      title: 'Critical Alerts',
      count: criticalCount,
      subtitle: 'Score \u2265 0.90 (Immediate Hazard)',
      color: 'red',
      borderColor: 'border-red-900/40 hover:border-red-500/60',
      textColor: 'text-red-400',
      badgeBg: 'bg-red-500/15 text-red-400 border-red-500/30',
      icon: AlertCircle,
      glow: 'shadow-red-500/10',
      indicator: 'bg-red-500 animate-pulse shadow-md shadow-red-500/50',
    },
    {
      title: 'High Advisories',
      count: highCount,
      subtitle: 'Score 0.70 - 0.89 (Significant)',
      color: 'orange',
      borderColor: 'border-orange-900/40 hover:border-orange-500/60',
      textColor: 'text-orange-400',
      badgeBg: 'bg-orange-500/15 text-orange-400 border-orange-500/30',
      icon: AlertTriangle,
      glow: 'shadow-orange-500/10',
      indicator: 'bg-orange-500 animate-pulse shadow-md shadow-orange-500/50',
    },
    {
      title: 'Stations Normal',
      count: normalCount + watchCount,
      subtitle: `${normalCount} Normal \u2022 ${watchCount} Watch`,
      color: 'emerald',
      borderColor: 'border-emerald-900/40 hover:border-emerald-500/60',
      textColor: 'text-emerald-400',
      badgeBg: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
      icon: CheckCircle,
      glow: 'shadow-emerald-500/10',
      indicator: 'bg-emerald-400 shadow-md shadow-emerald-400/50',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div
            key={idx}
            className={`bg-slate-900/80 backdrop-blur-sm border ${card.borderColor} rounded-2xl p-5 shadow-lg ${card.glow} transition-all duration-300 hover:scale-[1.01] flex flex-col justify-between relative overflow-hidden group`}
          >
            {/* Ambient Background Gradient Accent */}
            <div className="absolute -top-10 -right-10 w-28 h-28 bg-gradient-to-br from-white/5 to-transparent rounded-full blur-2xl group-hover:scale-150 transition-all duration-500" />

            <div className="flex items-center justify-between mb-3 relative z-10">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                {card.title}
              </span>
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${card.indicator}`} />
                <div className={`p-2 rounded-xl border ${card.badgeBg}`}>
                  <Icon className="w-4 h-4" />
                </div>
              </div>
            </div>

            <div className="relative z-10">
              <div className={`text-3xl font-black ${card.textColor} tracking-tight font-mono`}>
                {card.count}
              </div>
              <div className="text-xs text-slate-400 mt-1 font-medium flex items-center gap-1.5">
                <span>{card.subtitle}</span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
