import { DECISION_COLORS } from '../utils/constants';

export default function DecisionCard({ decision, riskScore, processingTime, confidence }) {
  const d = decision || 'INVESTIGATE';
  const colors = DECISION_COLORS[d] || DECISION_COLORS.INVESTIGATE;

  return (
    <div className={`p-5 rounded-xl border-2 ${colors.border} ${colors.bg}`}>
      <div className="flex items-center justify-between mb-3">
        <span className={`text-2xl font-bold ${colors.text}`}>
          {colors.label}
        </span>
        {processingTime && (
          <span className="text-xs bg-gray-800 px-3 py-1 rounded-full text-gray-300 font-mono">
            ⏱️ {(processingTime / 1000).toFixed(1)}s
          </span>
        )}
      </div>

      <div className="flex gap-6 text-sm">
        <div>
          <span className="text-gray-500">Risk Score</span>
          <p className={`text-xl font-bold ${colors.text}`}>{riskScore ?? '—'}/100</p>
        </div>
        <div>
          <span className="text-gray-500">Confidence</span>
          <p className="text-xl font-bold text-white">{confidence ? `${(confidence * 100).toFixed(0)}%` : '—'}</p>
        </div>
      </div>
    </div>
  );
}
