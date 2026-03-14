import { useEffect, useState } from 'react';
import { getDashboardStats, getRecentRefunds } from '../utils/api';
import { DECISION_COLORS } from '../utils/constants';

export default function DashboardStats() {
  const [stats, setStats] = useState(null);
  const [refunds, setRefunds] = useState([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [statsRes, refundsRes] = await Promise.all([
        getDashboardStats(),
        getRecentRefunds(10),
      ]);
      setStats(statsRes.data);
      setRefunds(refundsRes.data);
    } catch (err) {
      console.error('Dashboard load error:', err);
    }
  };

  if (!stats) {
    return <div className="text-gray-500 text-center py-10">Loading dashboard...</div>;
  }

  const kpis = [
    { label: 'Total Refunds', value: stats.total_refunds, icon: '📦' },
    { label: 'Auto-Approved', value: stats.auto_approved, icon: '⚡' },
    { label: 'Investigated', value: stats.investigated, icon: '🔍' },
    { label: 'Escalated', value: stats.escalated, icon: '🚩' },
    { label: 'Avg Time', value: `${(stats.avg_processing_time_ms / 1000).toFixed(1)}s`, icon: '⏱️' },
    { label: 'Fraud Saved', value: `₹${(stats.fraud_savings / 1000).toFixed(1)}K`, icon: '🛡️' },
    { label: 'Auto-Approve Rate', value: `${stats.auto_approve_rate}%`, icon: '📈' },
    { label: 'Total Amount', value: `₹${(stats.total_refund_amount / 1000).toFixed(1)}K`, icon: '💰' },
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {kpis.map((kpi) => (
          <div key={kpi.label} className="p-4 rounded-xl bg-gray-800/50 border border-gray-700">
            <div className="flex items-center gap-2 mb-1">
              <span className="text-lg">{kpi.icon}</span>
              <span className="text-xs text-gray-500">{kpi.label}</span>
            </div>
            <p className="text-xl font-bold text-white">{kpi.value}</p>
          </div>
        ))}
      </div>

      {/* Recent Refunds Table */}
      <div className="rounded-xl bg-gray-800/50 border border-gray-700 overflow-hidden">
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-sm font-semibold text-white">Recent Refunds</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-gray-500 text-xs">
                <th className="text-left p-3">ID</th>
                <th className="text-left p-3">Customer</th>
                <th className="text-left p-3">Amount</th>
                <th className="text-left p-3">Reason</th>
                <th className="text-left p-3">Decision</th>
                <th className="text-left p-3">Score</th>
              </tr>
            </thead>
            <tbody>
              {refunds.map((r) => {
                const colors = DECISION_COLORS[r.decision] || {};
                return (
                  <tr key={r.id} className="border-t border-gray-700/50 hover:bg-gray-700/20">
                    <td className="p-3 font-mono text-gray-400">{r.id}</td>
                    <td className="p-3 text-white">{r.customer_name || r.customer_id}</td>
                    <td className="p-3 text-white">₹{r.amount}</td>
                    <td className="p-3 text-gray-400">{r.reason?.replace(/_/g, ' ')}</td>
                    <td className="p-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${colors.text || 'text-gray-400'} ${colors.bg || ''}`}>
                        {r.decision || 'Pending'}
                      </span>
                    </td>
                    <td className="p-3 font-mono text-gray-400">{r.risk_score ?? '—'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
