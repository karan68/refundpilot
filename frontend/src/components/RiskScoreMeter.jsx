import { useEffect, useState } from 'react';

export default function RiskScoreMeter({ score = 0, animated = true }) {
  const [displayScore, setDisplayScore] = useState(0);

  useEffect(() => {
    if (!animated) {
      setDisplayScore(score);
      return;
    }

    let current = 0;
    const step = Math.max(1, Math.floor(score / 30));
    const interval = setInterval(() => {
      current += step;
      if (current >= score) {
        current = score;
        clearInterval(interval);
      }
      setDisplayScore(current);
    }, 50);

    return () => clearInterval(interval);
  }, [score, animated]);

  const getColor = (s) => {
    if (s <= 30) return { ring: 'text-green-500', bg: 'from-green-500/20', label: 'Low Risk' };
    if (s <= 70) return { ring: 'text-yellow-500', bg: 'from-yellow-500/20', label: 'Medium Risk' };
    return { ring: 'text-red-500', bg: 'from-red-500/20', label: 'High Risk' };
  };

  const colors = getColor(displayScore);
  const circumference = 2 * Math.PI * 54;
  const strokeDashoffset = circumference - (displayScore / 100) * circumference;

  return (
    <div className="flex flex-col items-center">
      <div className="relative w-36 h-36">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 120 120">
          {/* Background ring */}
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            stroke="#374151"
            strokeWidth="8"
          />
          {/* Score ring */}
          <circle
            cx="60" cy="60" r="54"
            fill="none"
            className={colors.ring}
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            style={{ transition: 'stroke-dashoffset 0.3s ease-out' }}
          />
        </svg>
        {/* Center text */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-3xl font-bold ${colors.ring}`}>{displayScore}</span>
          <span className="text-xs text-gray-500">/ 100</span>
        </div>
      </div>
      <span className={`mt-2 text-sm font-medium ${colors.ring}`}>{colors.label}</span>
    </div>
  );
}
