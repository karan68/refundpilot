import { useState } from 'react';
import RiskScoreMeter from '../components/RiskScoreMeter';
import ReasoningChain from '../components/ReasoningChain';
import DecisionCard from '../components/DecisionCard';
import ChatInterface from '../components/ChatInterface';
import StoreCredit from '../components/StoreCredit';
import api from '../utils/api';

const SCENARIOS = [
  {
    key: 'priya',
    name: 'Priya Sharma',
    type: 'loyal',
    icon: '🟢',
    color: 'green',
    border: 'border-green-500/30',
    desc: 'Loyal Customer — 23 orders, 2% refund rate',
    request: '"My Cotton Kurta arrived with a tear on the sleeve"',
    order: 'ORD-1001 · ₹800 · Fashion',
    expected: 'AUTO_APPROVE',
  },
  {
    key: 'vikram',
    name: 'Vikram Singh',
    type: 'suspect',
    icon: '🟡',
    color: 'yellow',
    border: 'border-yellow-500/30',
    desc: 'Suspect — 8 orders, 50% refund rate, 1 cross-merchant claim',
    request: '"These shoes don\'t match the description at all"',
    order: 'ORD-4001 · ₹2,400 · Fashion',
    expected: 'INVESTIGATE',
  },
  {
    key: 'rohit',
    name: 'Rohit Mehta',
    type: 'abuser',
    icon: '🔴',
    color: 'red',
    border: 'border-red-500/30',
    desc: 'Serial Abuser — 12 orders, 67% refund rate, 2 cross-merchant claims',
    request: '"Shoes were damaged in transit, completely unusable"',
    order: 'ORD-2001 · ₹2,400 · Fashion',
    expected: 'ESCALATE',
  },
];

function DemoCard({ scenario, result, loading, onRun }) {
  const decisionColors = {
    AUTO_APPROVE: 'border-green-500',
    INVESTIGATE: 'border-yellow-500',
    ESCALATE: 'border-red-500',
  };

  return (
    <div className={`bg-gray-900 rounded-2xl p-5 border-2 ${result ? decisionColors[result.decision] || scenario.border : scenario.border} transition-all`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-2xl">{scenario.icon}</span>
        <div>
          <h2 className="text-lg font-bold text-white">{scenario.name}</h2>
          <p className={`text-${scenario.color}-400 text-xs`}>{scenario.desc}</p>
        </div>
      </div>

      {/* Request */}
      <div className="bg-gray-800/50 rounded-lg p-3 mb-3">
        <p className="text-xs text-gray-500">Refund Request:</p>
        <p className="text-white text-sm mt-1">{scenario.request}</p>
        <p className="text-gray-600 text-xs mt-1">{scenario.order}</p>
      </div>

      {/* Run Button */}
      {!result && (
        <button
          onClick={onRun}
          disabled={loading}
          className={`w-full py-3 rounded-lg bg-${scenario.color}-600 hover:bg-${scenario.color}-700 text-white font-semibold text-sm transition-colors disabled:opacity-50`}
        >
          {loading ? '🤖 Agent Processing...' : `Run ${scenario.name.split(' ')[0]}'s Refund`}
        </button>
      )}

      {/* Result */}
      {result && (
        <div className="space-y-3 mt-2">
          {/* Decision + Score */}
          <div className="flex items-center gap-4">
            <RiskScoreMeter score={result.risk_score || 0} />
            <div className="flex-1">
              <DecisionCard
                decision={result.decision}
                riskScore={result.risk_score}
                processingTime={result.processing_time_ms}
                confidence={result.confidence}
              />
            </div>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-1.5">
            {result.is_cold_start && (
              <span className="px-2 py-0.5 rounded text-xs bg-blue-500/10 text-blue-400">🆕 Cold Start</span>
            )}
            {result.circuit_breaker_fired && (
              <span className="px-2 py-0.5 rounded text-xs bg-red-500/10 text-red-400">🚨 Circuit Breaker</span>
            )}
            {result.fraud_ring?.ring_detected && (
              <span className="px-2 py-0.5 rounded text-xs bg-red-500/10 text-red-400">🕸️ Fraud Ring ({result.fraud_ring.total_linked} linked)</span>
            )}
            <span className="px-2 py-0.5 rounded text-xs bg-gray-700 text-gray-300">⚡ {result.recommended_action?.replace(/_/g, ' ')}</span>
          </div>

          {/* Explanation */}
          <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
            <p className="text-xs text-gray-500 mb-1">Agent Explanation:</p>
            <p className="text-sm text-gray-300">{result.explanation}</p>
          </div>

          {/* ReAct Steps (for INVESTIGATE) */}
          {result.react_steps?.length > 0 && (
            <ChatInterface reactSteps={result.react_steps} decision={result.decision} />
          )}

          {/* Fraud Ring (for ESCALATE) */}
          {result.fraud_ring?.ring_detected && (
            <div className="p-3 rounded-lg border border-red-500/30 bg-red-500/5">
              <p className="text-xs text-red-400 font-semibold mb-1">🚨 Fraud Ring Detected</p>
              <p className="text-xs text-gray-400">{result.fraud_ring.message}</p>
            </div>
          )}

          {/* Case Brief (for ESCALATE) */}
          {result.action?.case_brief && (
            <div className="p-3 rounded-lg border border-gray-700 bg-gray-800/50">
              <p className="text-xs text-gray-500 mb-1">📋 Case Brief — Top Signals:</p>
              {result.action.case_brief.top_risk_signals?.slice(0, 3).map((sig, i) => (
                <p key={i} className="text-xs text-gray-400">• {sig.signal}: {sig.detail}</p>
              ))}
            </div>
          )}

          {/* Store Credit (for INVESTIGATE) */}
          {result.action?.type === 'store_credit_offer' && (
            <div className="p-3 rounded-lg border border-green-500/20 bg-green-500/5">
              <p className="text-xs text-green-400">🎁 Store credit offered: ₹{result.action.credit_amount} (₹{result.action.cash_refund_amount} + ₹{result.action.bonus} bonus)</p>
            </div>
          )}

          {/* Pine Labs ref (for AUTO_APPROVE) */}
          {result.action?.pine_labs && (
            <div className="p-3 rounded-lg border border-green-500/20 bg-green-500/5">
              <p className="text-xs text-green-400">✅ Pine Labs refund: {result.action.pine_labs.pine_labs_ref} — ₹{result.action.amount}</p>
              <p className="text-xs text-gray-500">{result.action.is_returnless ? 'Returnless' : 'Return pickup scheduled'}</p>
            </div>
          )}

          {/* Reasoning (collapsed) */}
          <details className="text-xs">
            <summary className="text-gray-500 cursor-pointer hover:text-gray-300">Show 10-signal breakdown</summary>
            <div className="mt-2">
              <ReasoningChain steps={result.reasoning_chain || []} />
            </div>
          </details>
        </div>
      )}
    </div>
  );
}

export default function DemoPage() {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const [allRunning, setAllRunning] = useState(false);

  const runScenario = async (key) => {
    setLoading(prev => ({ ...prev, [key]: true }));
    try {
      const res = await api.post(`/demo/run/${key}`);
      setResults(prev => ({ ...prev, [key]: res.data }));
    } catch (err) {
      console.error(`Demo ${key} failed:`, err);
    } finally {
      setLoading(prev => ({ ...prev, [key]: false }));
    }
  };

  const runAll = async () => {
    setAllRunning(true);
    setResults({});
    for (const s of SCENARIOS) {
      await runScenario(s.key);
    }
    setAllRunning(false);
  };

  const reset = () => {
    setResults({});
    setLoading({});
  };

  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <div className="mb-6 text-center">
        <h1 className="text-4xl font-bold text-white">⚡ RefundPilot Live Demo</h1>
        <p className="text-gray-400 mt-2 text-lg">3 customers. 3 outcomes. One autonomous agent.</p>
        <p className="text-gray-600 mt-1 text-sm">Same system, same 10 signals, same 4 seconds — but different decisions.</p>
      </div>

      {/* Controls */}
      <div className="flex justify-center gap-3 mb-6">
        <button
          onClick={runAll}
          disabled={allRunning}
          className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white font-bold text-sm disabled:opacity-50 transition-colors"
        >
          {allRunning ? '🤖 Running All 3...' : '🚀 Run All 3 Scenarios'}
        </button>
        {Object.keys(results).length > 0 && (
          <button onClick={reset} className="px-6 py-3 rounded-xl border border-gray-700 text-gray-400 text-sm hover:text-white">
            Reset
          </button>
        )}
      </div>

      {/* 3 Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        {SCENARIOS.map(s => (
          <DemoCard
            key={s.key}
            scenario={s}
            result={results[s.key]}
            loading={loading[s.key]}
            onRun={() => runScenario(s.key)}
          />
        ))}
      </div>

      {/* Pitch Points */}
      {Object.keys(results).length === 3 && (
        <div className="mt-8 p-6 bg-gray-900 rounded-2xl border border-gray-800">
          <h3 className="text-lg font-semibold text-white mb-3">Key Takeaways for Judges</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm text-gray-400">
            <p>⚡ Decision in {Math.max(...Object.values(results).map(r => r.processing_time_ms / 1000)).toFixed(1)}s — not 15 days</p>
            <p>🧮 Deterministic scoring: same input → same output, always</p>
            <p>🤖 AI decides gray areas, math decides clear cases</p>
            <p>🕸️ Cross-merchant + fraud ring detection — only on Pine Labs</p>
            <p>📋 Pre-built case briefs for escalated refunds</p>
            <p>🎁 Smart store credit negotiation retains revenue</p>
          </div>
        </div>
      )}
    </div>
  );
}
