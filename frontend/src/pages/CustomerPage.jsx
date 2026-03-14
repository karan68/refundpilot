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
    <div className="page-shell">
      <div className="page-header">
        <h1 className="page-title">Submit Refund Request</h1>
        <p className="page-subtitle">Select a customer profile and submit a refund to see the agent reason through the request in real time.</p>
      </div>

      <div className="grid grid-cols-1 gap-8 xl:grid-cols-[minmax(430px,520px)_minmax(0,1fr)]">
        <div className="glass-panel p-7 xl:p-8">
          <h2 className="section-title mb-5">Refund Request</h2>
          <RefundForm onResult={handleResult} />
        </div>

        <div className="space-y-6">
          {result ? (
            <>
              <div className="glass-panel p-7 xl:p-8">
                <h2 className="section-title mb-5">Agent Decision</h2>
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

              <div className="glass-panel p-7 xl:p-8">
                <h2 className="section-title mb-5">Reasoning Chain (10 Signals)</h2>
                <ReasoningChain steps={result.reasoning_chain || []} />
              </div>

              {result.explanation && (
                <div className="glass-panel p-7 xl:p-8">
                  <h2 className="section-title mb-3">Agent Explanation</h2>
                  <p className="text-base leading-relaxed text-gray-300">{result.explanation}</p>
                </div>
              )}

              {result.counterfactuals && result.counterfactuals.length > 0 && (
                <div className="glass-panel p-7 xl:p-8">
                  <h2 className="section-title mb-3">Counterfactual: What Would Change the Outcome?</h2>
                  <div className="space-y-2">
                    {result.counterfactuals.map((cf, i) => (
                      <div key={i} className="rounded-2xl border border-gray-700 bg-gray-800/50 p-4 text-base text-gray-300">
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

              <StoreCredit action={result.action} />

              {result.decision === 'INVESTIGATE' && (
                <EvidenceViewer refundId={result.refund_id} />
              )}

              {result.fraud_ring?.ring_detected && (
                <div className="glass-panel border-2 border-red-500/35 p-7 xl:p-8">
                  <h2 className="section-title mb-3 text-red-300">Fraud Ring Detected</h2>
                  <p className="mb-3 text-base text-gray-300">{result.fraud_ring.message}</p>
                  <div className="space-y-1">
                    {result.fraud_ring.linked_accounts?.map((acc, i) => (
                      <div key={i} className="flex items-center gap-2 text-base">
                        <span className="text-red-400">⚠</span>
                        <span className="text-white">{acc.name}</span>
                        <span className="text-gray-500">({acc.customer_id})</span>
                        <span className="text-gray-400">— {acc.refund_count} refund(s)</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {result.action?.case_brief && (
                <div className="glass-panel border border-red-500/30 p-7 xl:p-8">
                  <h2 className="section-title mb-3">Escalation Case Brief</h2>
                  <div className="space-y-2 mb-4">
                    {result.action.case_brief.top_risk_signals?.map((sig, i) => (
                      <div key={i} className="flex items-center justify-between rounded-2xl bg-gray-800/50 p-3 text-base">
                        <span className="text-gray-300">{sig.signal?.replace(/_/g, ' ')}</span>
                        <span className="text-red-400 font-mono">+{sig.weighted_impact?.toFixed(1)}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-sm text-gray-500">Recommended: {result.action.case_brief.recommended_actions?.join(', ')}</p>
                </div>
              )}
            </>
          ) : (
            <div className="glass-panel flex flex-col items-center justify-center p-14 text-center">
              <div className="mb-5 flex h-16 w-16 items-center justify-center rounded-full bg-blue-500/10 text-lg font-semibold text-blue-300">AI</div>
              <h3 className="mb-2 text-2xl font-semibold text-white">RefundPilot Agent Ready</h3>
              <p className="max-w-lg text-base text-gray-500">
                Submit a refund request to see the autonomous agent analyze, reason, and decide in real-time
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
