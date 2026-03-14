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
  const settlementRate = data.summary.total > 0 ? Math.round((data.summary.settled / data.summary.total) * 100) : 0;

  return (
    <div className="glass-panel p-7 xl:p-8">
      <h2 className="section-title">Settlement health</h2>
      <p className="section-copy mt-2">Auto-approved refunds and how far each one has progressed through Pine Labs settlement.</p>

      <div className="mt-6 rounded-3xl border border-slate-800 bg-slate-950/45 p-5">
        <div className="flex flex-wrap items-end justify-between gap-3">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Completion</p>
            <p className="mt-2 text-4xl font-semibold text-white">{settlementRate}%</p>
          </div>
          <p className="max-w-sm text-sm leading-relaxed text-slate-400">
            {data.summary.settled} settled, {data.summary.pending} pending, and {data.summary.failed} failed settlements across approved refunds.
          </p>
        </div>
        <div className="mt-4 h-2 rounded-full bg-slate-800">
          <div className="h-2 rounded-full bg-emerald-400" style={{ width: `${settlementRate}%` }} />
        </div>
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-3">
        <div className="rounded-3xl border border-green-500/20 bg-green-500/5 p-4 text-center">
          <p className="text-3xl font-semibold text-green-300">{data.summary.settled}</p>
          <p className="mt-1 text-sm text-slate-400">Settled</p>
        </div>
        <div className="rounded-3xl border border-yellow-500/20 bg-yellow-500/5 p-4 text-center">
          <p className="text-3xl font-semibold text-yellow-300">{data.summary.pending}</p>
          <p className="mt-1 text-sm text-slate-400">Pending</p>
        </div>
        <div className="rounded-3xl border border-red-500/20 bg-red-500/5 p-4 text-center">
          <p className="text-3xl font-semibold text-red-300">{data.summary.failed}</p>
          <p className="mt-1 text-sm text-slate-400">Failed</p>
        </div>
      </div>

      <div className="mt-6 overflow-x-auto rounded-3xl border border-slate-800 bg-slate-950/45">
        <table className="w-full min-w-[720px] text-left text-sm">
          <thead className="border-b border-slate-800 text-xs uppercase tracking-[0.16em] text-slate-500">
            <tr>
              <th className="px-4 py-4 font-medium">Refund</th>
              <th className="px-4 py-4 font-medium">Customer</th>
              <th className="px-4 py-4 font-medium">Amount</th>
              <th className="px-4 py-4 font-medium">Pine Labs Ref</th>
              <th className="px-4 py-4 font-medium">Settlement</th>
            </tr>
          </thead>
          <tbody>
            {data.refunds?.slice(0, 12).map(r => (
              <tr key={r.id} className="border-t border-slate-800/70 hover:bg-slate-900/55">
                <td className="px-4 py-4 font-mono text-slate-400">{r.id}</td>
                <td className="px-4 py-4 text-white">{r.customer_name}</td>
                <td className="px-4 py-4 text-white">₹{r.amount}</td>
                <td className="px-4 py-4 font-mono text-slate-500">{r.pine_labs_ref || '—'}</td>
                <td className="px-4 py-4">
                  <span className={`text-sm capitalize ${statusColors[r.settlement_status] || 'text-slate-500'}`}>
                    {r.settlement_status}
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
