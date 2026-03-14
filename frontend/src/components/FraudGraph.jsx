import { useEffect, useState } from 'react';
import { getFraudGraph } from '../utils/api';

const GROUP_STYLES = {
  loyal: {
    label: 'Loyal',
    dot: 'bg-emerald-400',
    card: 'border-emerald-500/20 bg-emerald-500/10 text-emerald-100',
  },
  abuser: {
    label: 'Abuse risk',
    dot: 'bg-rose-400',
    card: 'border-rose-500/20 bg-rose-500/10 text-rose-100',
  },
  suspect: {
    label: 'Watchlist',
    dot: 'bg-amber-400',
    card: 'border-amber-500/20 bg-amber-500/10 text-amber-100',
  },
  new: {
    label: 'New',
    dot: 'bg-sky-400',
    card: 'border-sky-500/20 bg-sky-500/10 text-sky-100',
  },
  ring_member: {
    label: 'Linked',
    dot: 'bg-violet-400',
    card: 'border-violet-500/20 bg-violet-500/10 text-violet-100',
  },
};

export default function FraudGraph() {
  const [graph, setGraph] = useState(null);

  useEffect(() => {
    const loadGraph = async () => {
      try {
        const res = await getFraudGraph();
        setGraph(res.data);
      } catch {
        // silently ignore
      }
    };

    loadGraph();
  }, []);

  if (!graph) return null;

  const customerNodes = graph.nodes?.filter((node) => node.type === 'customer') || [];
  const addressNodes = graph.nodes?.filter((node) => node.type === 'address') || [];
  const customerMap = new Map(customerNodes.map((node) => [node.id, node]));
  const suspiciousCustomers = customerNodes
    .filter((node) => ['abuser', 'suspect', 'ring_member'].includes(node.group))
    .sort((left, right) => (right.refund_rate || 0) - (left.refund_rate || 0));

  const addressClusters = addressNodes
    .map((node) => ({
      ...node,
      customers: (graph.edges || [])
        .filter((edge) => edge.target === node.id)
        .map((edge) => customerMap.get(edge.source))
        .filter(Boolean),
    }))
    .sort((left, right) => right.customers.length - left.customers.length);

  const highlightedClusters =
    graph.rings?.length > 0
      ? graph.rings.map((ring) => ({
          address: ring.address,
          customers: ring.customers.map((id) => customerMap.get(id)).filter(Boolean),
        }))
      : addressClusters.slice(0, 2).map((cluster) => ({
          address: cluster.full_address || cluster.label,
          customers: cluster.customers,
        }));

  return (
    <div className="glass-panel p-7 xl:p-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="section-title">Linked-account map</h2>
          <p className="section-copy mt-2">Shared addresses and suspicious customer clusters that deserve merchant review before payout.</p>
        </div>
        <div className="rounded-full border border-slate-700/70 bg-slate-900/80 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
          {graph.rings?.length || 0} shared-address rings
        </div>
      </div>

      <div className="mt-6 grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
        <div className="space-y-4">
          {highlightedClusters.map((cluster, index) => (
            <div key={`${cluster.address}-${index}`} className="rounded-3xl border border-rose-500/20 bg-slate-950/40 p-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <p className="text-xs font-medium uppercase tracking-[0.18em] text-rose-300">Shared address {index + 1}</p>
                  <h3 className="mt-2 text-lg font-medium text-white">{cluster.address}</h3>
                </div>
                <div className="rounded-2xl border border-rose-500/20 bg-rose-500/10 px-4 py-3 text-right">
                  <p className="text-2xl font-semibold text-rose-100">{cluster.customers.length}</p>
                  <p className="text-xs uppercase tracking-[0.16em] text-rose-300">linked accounts</p>
                </div>
              </div>

              <div className="mt-5 grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                {cluster.customers.map((customer) => {
                  const style = GROUP_STYLES[customer.group] || GROUP_STYLES.new;

                  return (
                    <div key={customer.id} className={`rounded-2xl border p-4 ${style.card}`}>
                      <div className="flex items-center gap-2">
                        <span className={`h-2.5 w-2.5 rounded-full ${style.dot}`} />
                        <span className="text-xs font-medium uppercase tracking-[0.16em] opacity-80">{style.label}</span>
                      </div>
                      <p className="mt-3 text-base font-medium text-white">{customer.label}</p>
                      <p className="mt-2 text-sm opacity-85">Refund rate {(customer.refund_rate * 100).toFixed(0)}%</p>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>

        <div className="space-y-4">
          <div className="rounded-3xl border border-slate-800 bg-slate-950/45 p-5">
            <p className="text-xs font-medium uppercase tracking-[0.18em] text-slate-500">Network summary</p>
            <div className="mt-4 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
              <div>
                <p className="text-3xl font-semibold text-white">{graph.rings?.length || 0}</p>
                <p className="text-sm text-slate-400">Shared-address rings</p>
              </div>
              <div>
                <p className="text-3xl font-semibold text-white">{suspiciousCustomers.length}</p>
                <p className="text-sm text-slate-400">Profiles on watchlists</p>
              </div>
              <div>
                <p className="text-3xl font-semibold text-white">{addressClusters.length}</p>
                <p className="text-sm text-slate-400">Address hubs mapped</p>
              </div>
            </div>
          </div>

          <div className="rounded-3xl border border-slate-800 bg-slate-950/45 p-5">
            <p className="text-sm font-medium text-white">Profiles to watch</p>
            <div className="mt-4 space-y-3">
              {suspiciousCustomers.slice(0, 5).map((customer) => {
                const style = GROUP_STYLES[customer.group] || GROUP_STYLES.new;

                return (
                  <div key={customer.id} className="flex items-center justify-between rounded-2xl border border-gray-700 bg-gray-900/55 px-4 py-3">
                    <div className="flex items-center gap-3">
                      <span className={`h-2.5 w-2.5 rounded-full ${style.dot}`} />
                      <div>
                        <p className="text-sm font-medium text-white">{customer.label}</p>
                        <p className="text-xs uppercase tracking-[0.16em] text-slate-500">{style.label}</p>
                      </div>
                    </div>
                    <span className="text-sm text-slate-400">{(customer.refund_rate * 100).toFixed(0)}%</span>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
