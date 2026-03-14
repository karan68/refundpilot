import { useEffect, useState } from 'react';
import { getProductCohorts } from '../utils/api';

export default function CohortInsights() {
  const [cohorts, setCohorts] = useState([]);

  useEffect(() => {
    loadCohorts();
  }, []);

  const loadCohorts = async () => {
    try {
      const res = await getProductCohorts();
      setCohorts(res.data || []);
    } catch {
      // silently ignore
    }
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">📊 Product Refund Cohorts</h2>
      <div className="space-y-3">
        {cohorts.map((c) => (
          <div
            key={c.sku}
            className={`p-3 rounded-lg border ${
              c.is_anomaly ? 'border-red-500/30 bg-red-500/5' : 'border-gray-700 bg-gray-800/50'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-white">{c.name}</span>
              <span className={`text-xs px-2 py-0.5 rounded ${
                c.is_anomaly ? 'bg-red-500/10 text-red-400' : 'bg-green-500/10 text-green-400'
              }`}>
                {c.actual_refund_pct}% refund rate
              </span>
            </div>
            <p className="text-xs text-gray-500">
              {c.total_refunds} refunds / {c.total_orders} orders · Expected: {(c.expected_refund_rate * 100).toFixed(0)}%
            </p>
            {c.is_anomaly && (
              <p className="text-xs text-red-400 mt-1">⚠️ {c.insight}</p>
            )}
          </div>
        ))}
        {cohorts.length === 0 && (
          <p className="text-gray-500 text-sm text-center py-4">No cohort data yet</p>
        )}
      </div>
    </div>
  );
}
