import { useEffect, useState } from 'react';
import { getReconciliation } from '../utils/api';

export default function ReconciliationTab() {
  const [data, setData] = useState(null);

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const res = await getReconciliation();
      setData(res.data);
    } catch { /* ignore */ }
  };

  if (!data) return null;

  const statusColors = {
    settled: 'text-green-400',
    pending: 'text-yellow-400',
    failed: 'text-red-400',
  };
  const statusIcons = {
    settled: '✅',
    pending: '🕐',
    failed: '🚩',
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">🏦 Settlement Reconciliation (F24)</h2>

      {/* Summary */}
      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="p-3 rounded-lg bg-green-500/5 border border-green-500/20 text-center">
          <p className="text-2xl font-bold text-green-400">{data.summary.settled}</p>
          <p className="text-xs text-gray-500">Settled</p>
        </div>
        <div className="p-3 rounded-lg bg-yellow-500/5 border border-yellow-500/20 text-center">
          <p className="text-2xl font-bold text-yellow-400">{data.summary.pending}</p>
          <p className="text-xs text-gray-500">Pending</p>
        </div>
        <div className="p-3 rounded-lg bg-red-500/5 border border-red-500/20 text-center">
          <p className="text-2xl font-bold text-red-400">{data.summary.failed}</p>
          <p className="text-xs text-gray-500">Failed</p>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-500 text-xs border-b border-gray-800">
              <th className="text-left p-2">Refund</th>
              <th className="text-left p-2">Customer</th>
              <th className="text-left p-2">Amount</th>
              <th className="text-left p-2">Pine Labs Ref</th>
              <th className="text-left p-2">Settlement</th>
            </tr>
          </thead>
          <tbody>
            {data.refunds?.slice(0, 15).map(r => (
              <tr key={r.id} className="border-b border-gray-800/50 hover:bg-gray-800/20">
                <td className="p-2 font-mono text-gray-400 text-xs">{r.id}</td>
                <td className="p-2 text-white text-xs">{r.customer_name}</td>
                <td className="p-2 text-white text-xs">₹{r.amount}</td>
                <td className="p-2 font-mono text-gray-500 text-xs">{r.pine_labs_ref || '—'}</td>
                <td className="p-2">
                  <span className={`text-xs ${statusColors[r.settlement_status] || 'text-gray-500'}`}>
                    {statusIcons[r.settlement_status] || '❓'} {r.settlement_status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
