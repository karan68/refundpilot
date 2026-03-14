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
    high: 'border-red-500/40 bg-red-500/5',
    medium: 'border-yellow-500/40 bg-yellow-500/5',
    low: 'border-blue-500/40 bg-blue-500/5',
  };

  const severityIcons = {
    high: '🚨',
    medium: '⚠️',
    low: 'ℹ️',
  };

  return (
    <div className="space-y-2 mb-6">
      {alerts.map((alert, i) => (
        <div key={i} className={`p-4 rounded-xl border ${severityColors[alert.severity] || severityColors.medium}`}>
          <div className="flex items-center gap-2 mb-1">
            <span>{severityIcons[alert.severity]}</span>
            <span className="text-sm font-semibold text-white">{alert.title}</span>
            <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-400 ml-auto">{alert.type}</span>
          </div>
          <p className="text-sm text-gray-400">{alert.message}</p>
        </div>
      ))}
    </div>
  );
}
