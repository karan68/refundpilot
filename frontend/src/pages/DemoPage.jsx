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
    segment: 'Loyal customer',
    border: 'border-emerald-400/35',
    tint: 'from-emerald-500/12 via-transparent to-transparent',
    tag: 'border-emerald-400/20 bg-emerald-500/10 text-emerald-200',
    text: 'text-emerald-300',
    button: 'bg-emerald-600 hover:bg-emerald-500',
    desc: '23 orders, 2% refund rate, strong delivery history',
    request: '"My Cotton Kurta arrived with a tear on the sleeve"',
    order: 'ORD-1001 · ₹800 · Fashion',
    expected: 'AUTO_APPROVE',
  },
  {
    key: 'vikram',
    name: 'Vikram Singh',
    segment: 'Watchlist',
    border: 'border-amber-400/35',
    tint: 'from-amber-500/12 via-transparent to-transparent',
    tag: 'border-amber-400/20 bg-amber-500/10 text-amber-200',
    text: 'text-amber-300',
    button: 'bg-amber-600 hover:bg-amber-500',
    desc: '8 orders, 50% refund rate, one network claim elsewhere',
    request: '"These shoes don\'t match the description at all"',
    order: 'ORD-4001 · ₹2,400 · Fashion',
    expected: 'INVESTIGATE',
  },
  {
    key: 'rohit',
    name: 'Rohit Mehta',
    segment: 'Abuse risk',
    border: 'border-rose-400/35',
    tint: 'from-rose-500/12 via-transparent to-transparent',
    tag: 'border-rose-400/20 bg-rose-500/10 text-rose-200',
    text: 'text-rose-300',
    button: 'bg-rose-600 hover:bg-rose-500',
    desc: '12 orders, 67% refund rate, repeated cross-merchant behaviour',
    request: '"Shoes were damaged in transit, completely unusable"',
    order: 'ORD-2001 · ₹2,400 · Fashion',
    expected: 'ESCALATE',
  },
];

function DemoCard({ scenario, result, loading, onRun }) {
  const decisionColors = {
    AUTO_APPROVE: 'border-emerald-400/60',
    INVESTIGATE: 'border-amber-400/60',
    ESCALATE: 'border-rose-400/60',
  };

  return (
    <div className={`glass-panel relative overflow-hidden border-2 p-6 xl:p-7 ${result ? decisionColors[result.decision] || scenario.border : scenario.border}`}>
      <div className={`pointer-events-none absolute inset-x-0 top-0 h-28 bg-gradient-to-b ${scenario.tint}`} />

      <div className="relative">
        <div className={`inline-flex items-center rounded-full border px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] ${scenario.tag}`}>
          {scenario.segment}
        </div>
        <h2 className="mt-5 text-2xl font-semibold text-white xl:text-[1.85rem]">{scenario.name}</h2>
        <p className={`mt-2 text-sm xl:text-base ${scenario.text}`}>{scenario.desc}</p>
      </div>

      <div className="relative mt-5 rounded-3xl border border-gray-800 bg-gray-800/55 p-4 xl:p-5">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-gray-500">Refund request</p>
        <p className="mt-2 text-base text-white xl:text-lg">{scenario.request}</p>
        <p className="mt-2 text-sm text-gray-500">{scenario.order}</p>
      </div>

      {!result && (
        <button
          onClick={onRun}
          disabled={loading}
          className={`mt-5 w-full rounded-2xl px-5 py-4 text-base font-semibold text-white transition-colors disabled:opacity-50 ${scenario.button}`}
        >
          {loading ? 'Agent processing...' : `Run ${scenario.name.split(' ')[0]}'s refund`}
        </button>
      )}

      {result && (
        <div className="mt-5 space-y-4">
          <div className="flex items-center gap-5">
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

          <div className="flex flex-wrap gap-2">
            {result.is_cold_start && (
              <span className="rounded-full bg-blue-500/10 px-3 py-1 text-xs text-blue-300">Cold start</span>
            )}
            {result.circuit_breaker_fired && (
              <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs text-red-300">Circuit breaker</span>
            )}
            {result.fraud_ring?.ring_detected && (
              <span className="rounded-full bg-red-500/10 px-3 py-1 text-xs text-red-300">Fraud ring ({result.fraud_ring.total_linked} linked)</span>
            )}
            <span className="rounded-full bg-gray-700 px-3 py-1 text-xs text-gray-300">{result.recommended_action?.replace(/_/g, ' ')}</span>
          </div>

          <div className="rounded-3xl border border-gray-700 bg-gray-800/50 p-4 xl:p-5">
            <p className="mb-2 text-xs font-medium uppercase tracking-[0.18em] text-gray-500">Agent explanation</p>
            <p className="text-base text-gray-300">{result.explanation}</p>
          </div>

          {result.react_steps?.length > 0 && (
            <ChatInterface reactSteps={result.react_steps} decision={result.decision} />
          )}

          {result.fraud_ring?.ring_detected && (
            <div className="rounded-3xl border border-red-500/30 bg-red-500/5 p-4">
              <p className="mb-1 text-xs font-semibold uppercase tracking-[0.16em] text-red-300">Fraud ring detected</p>
              <p className="text-sm text-gray-400">{result.fraud_ring.message}</p>
            </div>
          )}

          {result.action?.case_brief && (
            <div className="rounded-3xl border border-gray-700 bg-gray-800/50 p-4">
              <p className="mb-2 text-xs font-medium uppercase tracking-[0.18em] text-gray-500">Case brief</p>
              {result.action.case_brief.top_risk_signals?.slice(0, 3).map((sig, i) => (
                <p key={i} className="text-sm text-gray-400">• {sig.signal}: {sig.detail}</p>
              ))}
            </div>
          )}

          {result.action?.type === 'store_credit_offer' && (
            <div className="rounded-3xl border border-green-500/20 bg-green-500/5 p-4">
              <p className="text-sm text-green-300">Store credit offered: ₹{result.action.credit_amount} (₹{result.action.cash_refund_amount} + ₹{result.action.bonus} bonus)</p>
            </div>
          )}

          {result.action?.pine_labs && (
            <div className="rounded-3xl border border-green-500/20 bg-green-500/5 p-4">
              <p className="text-sm text-green-300">Pine Labs refund: {result.action.pine_labs.pine_labs_ref} — ₹{result.action.amount}</p>
              <p className="mt-1 text-xs text-gray-500">{result.action.is_returnless ? 'Returnless' : 'Return pickup scheduled'}</p>
            </div>
          )}

          <details className="text-sm">
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
    <div className="page-shell">
      <div className="page-header items-center text-center">
        <div className="inline-flex items-center rounded-full border border-slate-700/80 bg-slate-900/80 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
          Live demo
        </div>
        <h1 className="page-title">RefundPilot Live Demo</h1>
        <p className="page-subtitle mx-auto">Three customer profiles, one decision engine, and a cleaner side-by-side view of how the system approves, investigates, or escalates.</p>
      </div>

      <div className="mb-8 flex flex-wrap justify-center gap-3">
        <button
          onClick={runAll}
          disabled={allRunning}
          className="rounded-2xl bg-blue-600 px-7 py-4 text-base font-semibold text-white transition-colors hover:bg-blue-500 disabled:opacity-50"
        >
          {allRunning ? 'Running all 3...' : 'Run all 3 scenarios'}
        </button>
        {Object.keys(results).length > 0 && (
          <button onClick={reset} className="rounded-2xl border border-gray-700 px-7 py-4 text-base text-gray-400 hover:text-white">
            Reset
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 xl:grid-cols-2 2xl:grid-cols-3">
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

      {Object.keys(results).length === 3 && (
        <div className="glass-panel mt-8 p-7 xl:p-8">
          <h3 className="section-title mb-4">Key Takeaways for Judges</h3>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
            <div className="rounded-3xl border border-gray-800 bg-gray-800/45 p-4 text-sm text-gray-400">
              Decisions completed in {Math.max(...Object.values(results).map(r => r.processing_time_ms / 1000)).toFixed(1)}s instead of a multi-day manual loop.
            </div>
            <div className="rounded-3xl border border-gray-800 bg-gray-800/45 p-4 text-sm text-gray-400">
              Deterministic scoring keeps the same input aligned to the same outcome every time.
            </div>
            <div className="rounded-3xl border border-gray-800 bg-gray-800/45 p-4 text-sm text-gray-400">
              The same engine can auto-approve, investigate, or escalate without changing modes.
            </div>
            <div className="rounded-3xl border border-gray-800 bg-gray-800/45 p-4 text-sm text-gray-400">
              Network intelligence spots cross-merchant fraud patterns that a single merchant cannot see alone.
            </div>
            <div className="rounded-3xl border border-gray-800 bg-gray-800/45 p-4 text-sm text-gray-400">
              Escalated refunds already include a case brief, so operations teams do not start from scratch.
            </div>
            <div className="rounded-3xl border border-gray-800 bg-gray-800/45 p-4 text-sm text-gray-400">
              Store credit negotiation helps recover margin while still closing borderline cases quickly.
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
