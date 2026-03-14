import { useEffect, useState } from 'react';
import { getFraudGraph } from '../utils/api';

export default function FraudGraph() {
  const [graph, setGraph] = useState(null);

  useEffect(() => {
    loadGraph();
  }, []);

  const loadGraph = async () => {
    try {
      const res = await getFraudGraph();
      setGraph(res.data);
    } catch {
      // silently ignore
    }
  };

  if (!graph) return null;

  const customerNodes = graph.nodes?.filter(n => n.type === 'customer') || [];
  const addressNodes = graph.nodes?.filter(n => n.type === 'address') || [];

  const groupColors = {
    loyal: 'bg-green-500',
    abuser: 'bg-red-500',
    suspect: 'bg-yellow-500',
    new: 'bg-blue-500',
    ring_member: 'bg-purple-500',
    address: 'bg-gray-500',
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">🕸️ Fraud Network Graph</h2>

      {/* Rings detected */}
      {graph.rings?.length > 0 && (
        <div className="mb-4 p-3 rounded-lg border border-red-500/30 bg-red-500/5">
          <h3 className="text-sm font-semibold text-red-400 mb-2">
            🚨 {graph.rings.length} Fraud Ring(s) Detected
          </h3>
          {graph.rings.map((ring, i) => (
            <p key={i} className="text-xs text-gray-400">
              Address shared by: {ring.customers.join(', ')}
            </p>
          ))}
        </div>
      )}

      {/* Node visualization */}
      <div className="grid grid-cols-2 gap-4">
        {/* Customers */}
        <div>
          <h3 className="text-sm text-gray-500 mb-2">Customers ({customerNodes.length})</h3>
          <div className="space-y-1">
            {customerNodes.map(node => (
              <div key={node.id} className="flex items-center gap-2 p-2 rounded bg-gray-800/50">
                <span className={`w-2.5 h-2.5 rounded-full ${groupColors[node.group] || 'bg-gray-500'}`} />
                <span className="text-sm text-white">{node.label}</span>
                <span className="text-xs text-gray-500 ml-auto">{(node.refund_rate * 100).toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Addresses */}
        <div>
          <h3 className="text-sm text-gray-500 mb-2">Addresses ({addressNodes.length})</h3>
          <div className="space-y-1">
            {addressNodes.map(node => {
              const isRing = graph.rings?.some(r =>
                graph.edges?.filter(e => e.target === node.id).length >= 2
              );
              return (
                <div key={node.id} className={`flex items-center gap-2 p-2 rounded ${isRing ? 'bg-red-500/10 border border-red-500/20' : 'bg-gray-800/50'}`}>
                  <span className="text-sm">📍</span>
                  <span className="text-sm text-gray-300">{node.label}</span>
                  {isRing && <span className="text-xs text-red-400 ml-auto">RING</span>}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-3 mt-4 pt-4 border-t border-gray-800">
        {Object.entries(groupColors).filter(([k]) => k !== 'address').map(([label, color]) => (
          <div key={label} className="flex items-center gap-1.5">
            <span className={`w-2 h-2 rounded-full ${color}`} />
            <span className="text-xs text-gray-500">{label}</span>
          </div>
        ))}
      </div>

      <p className="text-xs text-gray-600 mt-2">{graph.nodes?.length} nodes, {graph.edges?.length} edges</p>
    </div>
  );
}
