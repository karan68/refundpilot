import { useState } from 'react';

const stepColors = {
  THOUGHT: { bg: 'bg-blue-500/10', border: 'border-blue-500/30', text: 'text-blue-400', icon: '🧠' },
  ACTION: { bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', text: 'text-yellow-400', icon: '⚡' },
  OBSERVATION: { bg: 'bg-green-500/10', border: 'border-green-500/30', text: 'text-green-400', icon: '👁️' },
  DECISION: { bg: 'bg-purple-500/10', border: 'border-purple-500/30', text: 'text-purple-400', icon: '✅' },
};

export default function ChatInterface({ reactSteps, decision, explanation }) {
  const [expanded, setExpanded] = useState(true);

  if (!reactSteps || reactSteps.length === 0) {
    return null;
  }

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-white flex items-center gap-2">
          🤖 Agent ReAct Loop
          <span className="text-xs bg-yellow-500/10 text-yellow-400 px-2 py-0.5 rounded-full">
            {reactSteps.length} steps
          </span>
        </h2>
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-xs text-gray-500 hover:text-gray-300"
        >
          {expanded ? 'Collapse' : 'Expand'}
        </button>
      </div>

      {expanded && (
        <div className="space-y-3">
          {reactSteps.map((step, idx) => {
            const type = step.type || 'THOUGHT';
            const colors = stepColors[type] || stepColors.THOUGHT;
            return (
              <div
                key={idx}
                className={`p-3 rounded-lg border ${colors.border} ${colors.bg}`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span>{colors.icon}</span>
                  <span className={`text-xs font-bold uppercase ${colors.text}`}>{type}</span>
                  {step.tool && (
                    <span className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-300">
                      {step.tool}
                    </span>
                  )}
                  <span className="text-xs text-gray-600 ml-auto">Step {idx + 1}</span>
                </div>
                <p className="text-sm text-gray-300">{step.content}</p>
              </div>
            );
          })}

          {decision && (
            <div className="p-3 rounded-lg border border-purple-500/30 bg-purple-500/10 mt-2">
              <div className="flex items-center gap-2 mb-1">
                <span>✅</span>
                <span className="text-xs font-bold uppercase text-purple-400">FINAL DECISION</span>
              </div>
              <p className="text-sm text-gray-300">{explanation || decision}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
