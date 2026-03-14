import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getProductCohorts } from '../utils/api';

export default function CohortInsights() {
  const [cohorts, setCohorts] = useState([]);

  useEffect(() => {
    const loadCohorts = async () => {
      try {
        const res = await getProductCohorts();
        setCohorts(res.data || []);
      } catch {
        // silently ignore
      }
    };

    loadCohorts();
  }, []);

  if (cohorts.length === 0) {
    return (
      <div className="glass-panel p-7 xl:p-8">
        <p className="text-center text-slate-500">No cohort data yet</p>
      </div>
    );
  }

  const chartData = cohorts.slice(0, 5).map((cohort) => ({
    label: cohort.name.replace(' - ', ' '),
    actual: cohort.actual_refund_pct,
    expected: Number((cohort.expected_refund_rate * 100).toFixed(1)),
  }));
  const anomalies = cohorts.filter((cohort) => cohort.is_anomaly).slice(0, 3);

  return (
    <div className="glass-panel p-7 xl:p-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="section-title">Product cohort health</h2>
          <p className="section-copy mt-2">Separate likely quality issues from fraud by comparing actual refund rates against expected product behaviour.</p>
        </div>
        <div className="rounded-full border border-slate-700/70 bg-slate-900/80 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
          {anomalies.length} anomalies
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="h-[320px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 0, right: 16, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 12 }} />
              <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
              <Tooltip
                formatter={(value, name) => [
                  `${value}%`,
                  name === 'actual' ? 'Actual refund rate' : 'Expected refund rate',
                ]}
                contentStyle={{
                  backgroundColor: '#0f172a',
                  border: '1px solid #1e293b',
                  borderRadius: '18px',
                }}
              />
              <Bar dataKey="actual" fill="#60a5fa" radius={[8, 8, 0, 0]} />
              <Bar dataKey="expected" fill="#34d399" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="space-y-3">
          {(anomalies.length > 0 ? anomalies : cohorts.slice(0, 3)).map((cohort) => (
            <div
              key={cohort.sku}
              className={`rounded-3xl border p-4 ${
                cohort.is_anomaly ? 'border-rose-500/20 bg-rose-500/10' : 'border-gray-700 bg-gray-800/45'
              }`}
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-base font-medium text-white">{cohort.name}</p>
                  <p className="mt-1 text-sm text-slate-400">{cohort.total_refunds} refunds from {cohort.total_orders} orders</p>
                </div>
                <span className={`rounded-full px-3 py-1 text-xs ${cohort.is_anomaly ? 'bg-rose-500/10 text-rose-200' : 'bg-emerald-500/10 text-emerald-200'}`}>
                  {cohort.actual_refund_pct}% actual
                </span>
              </div>
              <p className="mt-3 text-sm leading-relaxed text-slate-400">{cohort.insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
