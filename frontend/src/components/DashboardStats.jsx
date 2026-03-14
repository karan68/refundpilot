import { useEffect, useState } from 'react';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getCityCohorts, getDashboardStats, getReasonCohorts, getRecentRefunds } from '../utils/api';
import { DECISION_COLORS } from '../utils/constants';

const DECISION_SERIES = [
  { key: 'AUTO_APPROVE', label: 'Auto-approved', color: '#34d399' },
  { key: 'INVESTIGATE', label: 'Investigate', color: '#fbbf24' },
  { key: 'ESCALATE', label: 'Escalated', color: '#fb7185' },
];

const RISK_BANDS = [
  { label: 'Low risk', min: 0, max: 30, bar: 'bg-emerald-400', tone: 'text-emerald-200' },
  { label: 'Needs review', min: 31, max: 70, bar: 'bg-amber-400', tone: 'text-amber-200' },
  { label: 'High risk', min: 71, max: 100, bar: 'bg-rose-400', tone: 'text-rose-200' },
];

const formatReasonLabel = (value = 'unknown') =>
  value
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');

const formatCompactCurrency = (value) => {
  const amount = Number(value || 0);

  if (Math.abs(amount) >= 100000) {
    return `₹${(amount / 100000).toFixed(1)}L`;
  }

  if (Math.abs(amount) >= 1000) {
    return `₹${(amount / 1000).toFixed(1)}K`;
  }

  return `₹${amount.toFixed(0)}`;
};

const formatTimestamp = (value) => {
  if (!value) {
    return 'Just now';
  }

  const parsed = new Date(String(value).replace(' ', 'T'));
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  });
};

export default function DashboardStats() {
  const [stats, setStats] = useState(null);
  const [refunds, setRefunds] = useState([]);
  const [cityCohorts, setCityCohorts] = useState([]);
  const [reasonCohorts, setReasonCohorts] = useState([]);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [statsRes, refundsRes, citiesRes, reasonsRes] = await Promise.all([
          getDashboardStats(),
          getRecentRefunds(18),
          getCityCohorts(),
          getReasonCohorts(),
        ]);

        setStats(statsRes.data);
        setRefunds(refundsRes.data || []);
        setCityCohorts(citiesRes.data || []);
        setReasonCohorts(reasonsRes.data || []);
      } catch (err) {
        console.error('Dashboard load error:', err);
      }
    };

    loadData();
  }, []);

  if (!stats) {
    return <div className="glass-panel py-14 text-center text-slate-500">Loading dashboard...</div>;
  }

  const totalClaims = stats.total_refunds || 0;
  const decisionData = DECISION_SERIES.map((item) => {
    const value =
      item.key === 'AUTO_APPROVE'
        ? stats.auto_approved
        : item.key === 'INVESTIGATE'
          ? stats.investigated
          : stats.escalated;

    return {
      ...item,
      value,
      share: totalClaims > 0 ? Math.round((value / totalClaims) * 100) : 0,
    };
  });

  const riskBands = RISK_BANDS.map((band) => ({
    ...band,
    value: refunds.filter((refund) => {
      const score = Number(refund.risk_score ?? -1);
      return score >= band.min && score <= band.max;
    }).length,
  }));

  const cityWatchlist = [...cityCohorts]
    .sort(
      (left, right) =>
        (Number(right.avg_risk_score) || 0) - (Number(left.avg_risk_score) || 0) ||
        (Number(right.refund_count) || 0) - (Number(left.refund_count) || 0),
    )
    .slice(0, 5)
    .map((city) => ({
      city: city.city,
      refunds: city.refund_count,
      avgRisk: city.avg_risk_score,
      totalAmount: city.total_amount,
    }));

  const reasonChartData = [...reasonCohorts].slice(0, 5).map((reason) => ({
    reason: formatReasonLabel(reason.reason),
    claims: reason.count,
    escalated: reason.escalated,
    avgScore: reason.avg_score,
  }));

  const priorityQueue = [...refunds]
    .sort((left, right) => (Number(right.risk_score) || 0) - (Number(left.risk_score) || 0))
    .slice(0, 8);

  const protectedShare =
    Number(stats.total_refund_amount) > 0
      ? Math.round((Number(stats.fraud_savings) / Number(stats.total_refund_amount)) * 100)
      : 0;
  const reviewShare = totalClaims > 0 ? Math.round(((stats.investigated + stats.escalated) / totalClaims) * 100) : 0;
  const topReason = reasonChartData[0];
  const topCity = cityWatchlist[0];
  const posture = reviewShare >= 60 ? 'Guarded' : reviewShare >= 35 ? 'Balanced' : 'Open';

  const heroStats = [
    {
      label: 'Value protected',
      value: formatCompactCurrency(stats.fraud_savings),
      detail: `${protectedShare}% of payout value held back from instant refund`,
    },
    {
      label: 'Fast-lane approvals',
      value: `${stats.auto_approve_rate}%`,
      detail: `${stats.auto_approved} claims cleared automatically`,
    },
    {
      label: 'Watchlist focus',
      value: topCity?.city || 'None',
      detail: topCity ? `Avg risk ${topCity.avgRisk}/100 across ${topCity.refunds} claims` : 'No concentration signal yet',
    },
  ];

  return (
    <div className="space-y-6">
      <div className="glass-panel overflow-hidden">
        <div className="grid gap-6 xl:grid-cols-[1.55fr_1fr]">
          <div className="p-7 xl:p-8">
            <div className="inline-flex items-center rounded-full border border-slate-700/80 bg-slate-900/70 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
              Live operations snapshot
            </div>
            <h2 className="mt-5 max-w-3xl text-3xl font-semibold leading-tight text-white xl:text-[2.65rem]">
              Keep genuine refunds moving while the risky claims surface themselves.
            </h2>
            <p className="mt-3 max-w-3xl text-base leading-relaxed text-slate-400 xl:text-lg">
              This view shifts the dashboard from raw tables to merchant decisions: how much value is being protected, what is creating pressure, and where the team should look next.
            </p>

            <div className="mt-6 grid gap-4 md:grid-cols-3">
              {heroStats.map((item) => (
                <div key={item.label} className="rounded-3xl border border-slate-800 bg-slate-950/45 p-5">
                  <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">{item.label}</p>
                  <p className="mt-3 text-3xl font-semibold text-white">{item.value}</p>
                  <p className="mt-2 text-sm leading-relaxed text-slate-400">{item.detail}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-800/90 p-7 xl:border-l xl:border-t-0 xl:p-8">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Current posture</p>
            <div className="mt-3 flex items-end gap-3">
              <p className="text-5xl font-semibold text-white">{posture}</p>
              <p className="pb-1 text-sm text-slate-400">{reviewShare}% of claims currently need manual review or escalation</p>
            </div>
            <p className="mt-4 text-sm leading-relaxed text-slate-400">
              {topReason
                ? `${topReason.reason} is the biggest driver right now, with ${topReason.escalated} escalations inside ${topReason.claims} recent claims.`
                : 'Monitoring live refund behaviour across the network.'}
            </p>

            <div className="mt-6 space-y-4">
              {decisionData.map((item) => (
                <div key={item.key}>
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-slate-300">{item.label}</span>
                    <span className="font-medium text-white">{item.share}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-800">
                    <div className="h-2 rounded-full" style={{ width: `${item.share}%`, backgroundColor: item.color }} />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 grid gap-3 sm:grid-cols-2">
              <div className="rounded-3xl border border-slate-800 bg-slate-950/45 p-4">
                <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Average decision time</p>
                <p className="mt-2 text-2xl font-semibold text-white">{(stats.avg_processing_time_ms / 1000).toFixed(1)}s</p>
              </div>
              <div className="rounded-3xl border border-slate-800 bg-slate-950/45 p-4">
                <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Total refund volume</p>
                <p className="mt-2 text-2xl font-semibold text-white">{formatCompactCurrency(stats.total_refund_amount)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
        <div className="glass-panel p-7 xl:p-8">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div>
              <h3 className="section-title">Decision mix</h3>
              <p className="section-copy mt-2">How the engine is splitting claims between instant resolution, investigation, and escalation.</p>
            </div>
            <div className="rounded-full border border-slate-700/70 bg-slate-900/80 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
              {totalClaims} total claims
            </div>
          </div>

          <div className="mt-6 grid gap-6 lg:grid-cols-[320px_minmax(0,1fr)]">
            <div className="relative h-[290px]">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={decisionData}
                    dataKey="value"
                    nameKey="label"
                    innerRadius={72}
                    outerRadius={102}
                    paddingAngle={3}
                    stroke="none"
                  >
                    {decisionData.map((entry) => (
                      <Cell key={entry.key} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    formatter={(value) => [`${value} claims`, 'Volume']}
                    contentStyle={{
                      backgroundColor: '#0f172a',
                      border: '1px solid #1e293b',
                      borderRadius: '18px',
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-4xl font-semibold text-white">{totalClaims}</span>
                <span className="text-sm text-slate-400">Total claims</span>
              </div>
            </div>

            <div className="space-y-4">
              {decisionData.map((item) => (
                <div key={item.key} className="rounded-3xl border border-slate-800 bg-slate-950/45 p-5">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="text-lg font-medium text-white">{item.label}</p>
                      <p className="mt-1 text-sm text-slate-400">{item.share}% of the full refund stream</p>
                    </div>
                    <div className="rounded-2xl px-3 py-2 text-right" style={{ backgroundColor: `${item.color}1A` }}>
                      <p className="text-2xl font-semibold text-white">{item.value}</p>
                      <p className="text-xs uppercase tracking-[0.16em] text-slate-400">Claims</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="glass-panel p-7 xl:p-8">
          <h3 className="section-title">Risk spread</h3>
          <p className="section-copy mt-2">A quick sense of how recent claims are distributed across low-risk, review, and high-risk bands.</p>

          <div className="mt-6 space-y-5">
            {riskBands.map((band) => {
              const width = refunds.length > 0 ? Math.max((band.value / refunds.length) * 100, band.value > 0 ? 10 : 0) : 0;

              return (
                <div key={band.label}>
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className={band.tone}>{band.label}</span>
                    <span className="text-white">{band.value} claims</span>
                  </div>
                  <div className="h-3 rounded-full bg-slate-800">
                    <div className={`h-3 rounded-full ${band.bar}`} style={{ width: `${width}%` }} />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="mt-6 rounded-3xl border border-slate-800 bg-slate-950/45 p-5">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Merchant readout</p>
            <div className="mt-3 space-y-3 text-sm text-slate-400">
              <p>{reviewShare}% of claims are leaving the instant refund lane and asking for merchant scrutiny.</p>
              <p>{topCity ? `${topCity.city} has the highest average risk score at ${topCity.avgRisk}/100.` : 'No city concentration has surfaced yet.'}</p>
              <p>{topReason ? `${topReason.reason} remains the leading claim reason.` : 'Claim reasons are still diversifying.'}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <div className="glass-panel p-7 xl:p-8">
          <h3 className="section-title">Claims by reason</h3>
          <p className="section-copy mt-2">Where refund demand is coming from, and how often those reasons end in escalation.</p>

          <div className="mt-6 h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={reasonChartData} layout="vertical" margin={{ top: 0, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis
                  type="category"
                  dataKey="reason"
                  width={125}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(148, 163, 184, 0.06)' }}
                  formatter={(value, name) => [value, name === 'claims' ? 'Claims' : 'Escalated']}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #1e293b',
                    borderRadius: '18px',
                  }}
                />
                <Bar dataKey="claims" fill="#60a5fa" radius={[0, 8, 8, 0]} />
                <Bar dataKey="escalated" fill="#fb7185" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel p-7 xl:p-8">
          <h3 className="section-title">City watchlist</h3>
          <p className="section-copy mt-2">Which cities deserve a closer look based on refund concentration and average risk score.</p>

          <div className="mt-6 h-[320px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cityWatchlist} layout="vertical" margin={{ top: 0, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} />
                <YAxis
                  type="category"
                  dataKey="city"
                  width={110}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <Tooltip
                  cursor={{ fill: 'rgba(148, 163, 184, 0.06)' }}
                  formatter={(value, name, item) => {
                    if (name === 'refunds') {
                      return [value, 'Claims'];
                    }

                    return [`₹${Number(item?.payload?.totalAmount || 0).toLocaleString('en-IN')}`, 'Total amount'];
                  }}
                  contentStyle={{
                    backgroundColor: '#0f172a',
                    border: '1px solid #1e293b',
                    borderRadius: '18px',
                  }}
                />
                <Bar dataKey="refunds" fill="#38bdf8" radius={[0, 8, 8, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="mt-5 flex flex-wrap gap-2">
            {cityWatchlist.map((city) => (
              <div key={city.city} className="rounded-full border border-slate-700/80 bg-slate-900/80 px-3 py-1 text-xs text-slate-300">
                {city.city} · avg risk {city.avgRisk}/100
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="glass-panel p-7 xl:p-8">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h3 className="section-title">Priority queue</h3>
            <p className="section-copy mt-2">The highest-risk recent claims, sorted so the merchant team sees the urgent cases first.</p>
          </div>
          <div className="rounded-full border border-slate-700/70 bg-slate-900/80 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
            {priorityQueue.length} high-priority claims
          </div>
        </div>

        <div className="mt-6 overflow-x-auto rounded-3xl border border-slate-800 bg-slate-950/45">
          <table className="w-full min-w-[760px] text-left text-sm">
            <thead className="border-b border-slate-800 text-xs uppercase tracking-[0.16em] text-slate-500">
              <tr>
                <th className="px-4 py-4 font-medium">Claim</th>
                <th className="px-4 py-4 font-medium">Customer</th>
                <th className="px-4 py-4 font-medium">Reason</th>
                <th className="px-4 py-4 font-medium">Decision</th>
                <th className="px-4 py-4 font-medium">Risk</th>
                <th className="px-4 py-4 font-medium">Time</th>
              </tr>
            </thead>
            <tbody>
              {priorityQueue.map((refund) => {
                const colors = DECISION_COLORS[refund.decision] || {};

                return (
                  <tr key={refund.id} className="border-t border-slate-800/70 text-slate-300 hover:bg-slate-900/55">
                    <td className="px-4 py-4 align-top">
                      <p className="font-mono text-slate-400">{refund.id}</p>
                      <p className="mt-1 text-xs uppercase tracking-[0.16em] text-slate-600">{refund.customer_type || 'Customer'}</p>
                    </td>
                    <td className="px-4 py-4 align-top text-white">{refund.customer_name || refund.customer_id}</td>
                    <td className="px-4 py-4 align-top">{formatReasonLabel(refund.reason)}</td>
                    <td className="px-4 py-4 align-top">
                      <span className={`inline-flex rounded-full px-3 py-1 text-xs font-medium ${colors.text || 'text-slate-300'} ${colors.bg || 'bg-slate-800'}`}>
                        {refund.decision || 'Pending'}
                      </span>
                    </td>
                    <td className="px-4 py-4 align-top font-medium text-white">{refund.risk_score ?? '—'}/100</td>
                    <td className="px-4 py-4 align-top text-slate-500">{formatTimestamp(refund.created_at)}</td>
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
