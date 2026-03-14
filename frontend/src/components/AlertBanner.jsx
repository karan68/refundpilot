import { useEffect, useState } from 'react';
import { getAlerts } from '../utils/api';

export default function AlertBanner() {
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    loadAlerts();
  }, []);

  const loadAlerts = async () => {
    try {
      const res = await getAlerts();
      setAlerts(res.data.alerts || []);
    } catch {
      // silently ignore
    }
  };

  if (alerts.length === 0) return null;

  const severityColors = {
    high: {
      border: 'border-rose-500/30',
      glow: 'from-rose-500/12 to-rose-500/0',
      badge: 'bg-rose-500/10 text-rose-200',
      dot: 'bg-rose-400',
    },
    medium: {
      border: 'border-amber-500/30',
      glow: 'from-amber-500/12 to-amber-500/0',
      badge: 'bg-amber-500/10 text-amber-200',
      dot: 'bg-amber-400',
    },
    low: {
      border: 'border-sky-500/30',
      glow: 'from-sky-500/12 to-sky-500/0',
      badge: 'bg-sky-500/10 text-sky-200',
      dot: 'bg-sky-400',
    },
  };

  return (
    <div className="mb-6 grid gap-4 xl:grid-cols-3">
      {alerts.map((alert, i) => (
        <div
          key={i}
          className={`glass-panel relative overflow-hidden border p-5 xl:p-6 ${severityColors[alert.severity]?.border || severityColors.medium.border}`}
        >
          <div className={`pointer-events-none absolute inset-x-0 top-0 h-24 bg-gradient-to-b ${severityColors[alert.severity]?.glow || severityColors.medium.glow}`} />
          <div className="relative">
            <div className="flex items-center justify-between gap-3">
              <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
                <span className={`h-2.5 w-2.5 rounded-full ${severityColors[alert.severity]?.dot || severityColors.medium.dot}`} />
                {alert.severity || 'medium'} priority
              </div>
              <span className={`rounded-full px-3 py-1 text-xs ${severityColors[alert.severity]?.badge || severityColors.medium.badge}`}>
                {alert.type?.replace(/_/g, ' ')}
              </span>
            </div>
            <h3 className="mt-4 text-xl font-semibold text-white">{alert.title}</h3>
            <p className="mt-2 text-sm leading-relaxed text-slate-400 xl:text-base">{alert.message}</p>
          </div>
        </div>
      ))}
    </div>
  );
}
