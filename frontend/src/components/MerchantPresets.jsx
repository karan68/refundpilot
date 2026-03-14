import { useState } from 'react';

const PRESETS = {
  default: { label: 'Default', desc: 'Balanced for general merchants' },
  fashion: { label: 'Fashion Mode', desc: 'Higher weight on delivery contradiction (wardrobing detection)' },
  electronics: { label: 'Electronics Mode', desc: 'Higher weight on amount risk (high-value items)' },
};

export default function MerchantPresets({ onPresetChange }) {
  const [active, setActive] = useState('default');

  const handleChange = (key) => {
    setActive(key);
    if (onPresetChange) onPresetChange(key);
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">⚙️ Merchant Weight Presets</h2>
      <p className="text-xs text-gray-500 mb-3">Different merchant categories have different fraud patterns. Select a preset to adjust signal weights.</p>

      <div className="grid grid-cols-3 gap-3">
        {Object.entries(PRESETS).map(([key, preset]) => (
          <button
            key={key}
            onClick={() => handleChange(key)}
            className={`p-4 rounded-xl border text-left transition-all ${
              active === key
                ? 'border-blue-500 bg-blue-500/10'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
            }`}
          >
            <p className={`text-sm font-semibold ${active === key ? 'text-blue-400' : 'text-white'}`}>
              {preset.label}
            </p>
            <p className="text-xs text-gray-500 mt-1">{preset.desc}</p>
          </button>
        ))}
      </div>

      {/* Weight comparison */}
      <div className="mt-4 p-3 rounded-lg bg-gray-800/50 border border-gray-700">
        <p className="text-xs text-gray-500 mb-2">Key weight differences for <span className="text-white">{PRESETS[active].label}</span>:</p>
        {active === 'fashion' && (
          <div className="text-xs text-gray-400 space-y-1">
            <p>📈 Delivery contradiction: 0.14 → <span className="text-yellow-400">0.18</span> (wardrobing)</p>
            <p>📉 Amount risk: 0.07 → <span className="text-green-400">0.05</span> (fashion is cheaper)</p>
          </div>
        )}
        {active === 'electronics' && (
          <div className="text-xs text-gray-400 space-y-1">
            <p>📈 Amount risk: 0.07 → <span className="text-yellow-400">0.12</span> (high-value items)</p>
            <p>📈 Sentiment: 0.06 → <span className="text-yellow-400">0.08</span> (scripted claims)</p>
          </div>
        )}
        {active === 'default' && (
          <p className="text-xs text-gray-400">Standard balanced weights across all 10 signals.</p>
        )}
      </div>
    </div>
  );
}
