import { useState } from 'react';
import RefundForm from '../components/RefundForm';
import DecisionCard from '../components/DecisionCard';
import RiskScoreMeter from '../components/RiskScoreMeter';
import ReasoningChain from '../components/ReasoningChain';
import ChatInterface from '../components/ChatInterface';
import EvidenceViewer from '../components/EvidenceViewer';
import StoreCredit from '../components/StoreCredit';

export default function CustomerPage() {
  const [result, setResult] = useState(null);

  const handleResult = (data) => {
    setResult(data);
  };

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Submit Refund Request</h1>
        <p className="text-gray-400 mt-1">Select a customer profile and submit a refund to see the agent in action</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Left: Form */}
        <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
          <h2 className="text-lg font-semibold text-white mb-4">Refund Request</h2>
          <RefundForm onResult={handleResult} />
        </div>

        {/* Right: Result */}
        <div className="space-y-6">
          {result ? (
            <>
              <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
                <h2 className="text-lg font-semibold text-white mb-4">Agent Decision</h2>
                <div className="flex items-center gap-6 mb-4">
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
                <div className="flex flex-wrap gap-2 mt-3">
                  {result.is_cold_start && (
                    <span className="px-2 py-1 rounded text-xs bg-blue-500/10 text-blue-400 border border-blue-500/20">🆕 Cold Start</span>
                  )}
                  {result.circuit_breaker_fired && (
                    <span className="px-2 py-1 rounded text-xs bg-red-500/10 text-red-400 border border-red-500/20">🚨 Circuit Breaker</span>
                  )}
                  {result.seasonal?.season !== 'default' && (
                    <span className="px-2 py-1 rounded text-xs bg-yellow-500/10 text-yellow-400 border border-yellow-500/20">📅 {result.seasonal.season} (+{result.seasonal.threshold_shift})</span>
                  )}
                  <span className="px-2 py-1 rounded text-xs bg-gray-700 text-gray-300">⚡ {result.recommended_action?.replace(/_/g, ' ')}</span>
                </div>
              </div>

              <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
                <h2 className="text-lg font-semibold text-white mb-4">Reasoning Chain (10 Signals)</h2>
                <ReasoningChain steps={result.reasoning_chain || []} />
              </div>

              {result.explanation && (
                <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
                  <h2 className="text-lg font-semibold text-white mb-3">Agent Explanation</h2>
                  <p className="text-gray-300 text-sm leading-relaxed">{result.explanation}</p>
                </div>
              )}

              {result.counterfactuals && result.counterfactuals.length > 0 && (
                <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
                  <h2 className="text-lg font-semibold text-white mb-3">Counterfactual: What Would Change the Outcome?</h2>
                  <div className="space-y-2">
                    {result.counterfactuals.map((cf, i) => (
                      <div key={i} className="p-3 rounded-lg bg-gray-800/50 border border-gray-700 text-sm text-gray-300">
                        {cf.message}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ReAct Loop Steps (for INVESTIGATE decisions) */}
              <ChatInterface
                reactSteps={result.react_steps}
                decision={result.decision}
                explanation={result.explanation}
              />

              {/* Store Credit Offer */}
              <StoreCredit action={result.action} />

              {/* Evidence Upload (for INVESTIGATE decisions) */}
              {result.decision === 'INVESTIGATE' && (
                <EvidenceViewer refundId={result.refund_id} />
              )}

              {/* Fraud Ring Alert */}
              {result.fraud_ring?.ring_detected && (
                <div className="bg-gray-900 rounded-2xl p-6 border-2 border-red-500/40">
                  <h2 className="text-lg font-semibold text-red-400 mb-3">🚨 Fraud Ring Detected</h2>
                  <p className="text-gray-300 text-sm mb-3">{result.fraud_ring.message}</p>
                  <div className="space-y-1">
                    {result.fraud_ring.linked_accounts?.map((acc, i) => (
                      <div key={i} className="flex items-center gap-2 text-sm">
                        <span className="text-red-400">⚠</span>
                        <span className="text-white">{acc.name}</span>
                        <span className="text-gray-500">({acc.customer_id})</span>
                        <span className="text-gray-400">— {acc.refund_count} refund(s)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Case Brief (for ESCALATE decisions) */}
              {result.action?.case_brief && (
                <div className="bg-gray-900 rounded-2xl p-6 border border-red-500/30">
                  <h2 className="text-lg font-semibold text-white mb-3">📋 Escalation Case Brief</h2>
                  <div className="space-y-2 mb-4">
                    {result.action.case_brief.top_risk_signals?.map((sig, i) => (
                      <div key={i} className="p-2 rounded bg-gray-800/50 flex items-center justify-between text-sm">
                        <span className="text-gray-300">{sig.signal?.replace(/_/g, ' ')}</span>
                        <span className="text-red-400 font-mono">+{sig.weighted_impact?.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-gray-500 text-xs">Recommended: {result.action.case_brief.recommended_actions?.join(', ')}</p>
                </div>
              )}
            </>
          ) : (
            <div className="bg-gray-900 rounded-2xl p-12 border border-gray-800 flex flex-col items-center justify-center text-center">
              <span className="text-5xl mb-4">🤖</span>
              <h3 className="text-lg font-semibold text-white mb-2">RefundPilot Agent Ready</h3>
              <p className="text-gray-500 text-sm">
                Submit a refund request to see the autonomous agent analyze, reason, and decide in real-time
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
