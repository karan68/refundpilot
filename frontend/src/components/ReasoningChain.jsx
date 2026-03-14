export default function ReasoningChain({ steps }) {
  if (!steps || steps.length === 0) {
    return (
      <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
        <p className="text-gray-500 text-sm">Reasoning chain will appear here when agent processes a refund...</p>
      </div>
    );
  }

  const impactColors = {
    positive: 'text-green-400',
    negative: 'text-red-400',
    neutral: 'text-gray-400',
  };

  const impactIcons = {
    positive: '✅',
    negative: '🚩',
    neutral: '➖',
  };

  const impactBg = {
    positive: 'border-green-500/20',
    negative: 'border-red-500/20',
    neutral: 'border-gray-700',
  };

  return (
    <div className="space-y-2">
      {steps.map((step, idx) => (
        <div
          key={idx}
          className={`flex items-start gap-3 p-3 rounded-lg bg-gray-800/50 border ${impactBg[step.impact] || 'border-gray-700'}`}
          style={{ animationDelay: `${idx * 100}ms` }}
        >
          <span className="text-lg mt-0.5">{impactIcons[step.impact] || '➖'}</span>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <span className="text-xs font-mono bg-gray-700 px-2 py-0.5 rounded text-gray-300">
                S{step.step}
              </span>
              <span className="text-xs text-gray-500">{step.signal?.replace(/_/g, ' ')}</span>
              {step.weight != null && (
                <span className="text-xs text-gray-600">w={step.weight}</span>
              )}
            </div>
            <p className={`text-sm mt-1 ${impactColors[step.impact] || 'text-gray-400'}`}>
              {step.detail || step.value}
            </p>
          </div>
          <div className="text-right shrink-0">
            <span className={`text-sm font-bold ${impactColors[step.impact]}`}>
              {step.weighted != null ? (step.weighted >= 0 ? '+' : '') + step.weighted.toFixed(1) : '—'}
            </span>
            {step.score != null && (
              <p className="text-xs text-gray-600">{step.score}/100</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
