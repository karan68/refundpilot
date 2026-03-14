import { useState } from 'react';

const PRESETS = {
  default: {
    label: 'Balanced',
    desc: 'Good default for mixed catalogs and regular refund flows.',
    summary: 'Keeps genuine refunds fast while still catching obvious abuse.',
    highlights: ['Broad retail coverage', 'Stable approval lane', 'Low tuning overhead'],
    emphasis: [
      { label: 'Delivery mismatch', value: 68 },
      { label: 'Cross-merchant history', value: 74 },
      { label: 'Amount sensitivity', value: 52 },
    ],
  },
  fashion: {
    label: 'Fashion',
    desc: 'Optimised for return-heavy categories and wardrobing behaviour.',
    summary: 'Adds more scrutiny when claims conflict with delivery signals or repeat return patterns.',
    highlights: ['Wardrobing control', 'Repeat fit claim tracking', 'Lower value item tolerance'],
    emphasis: [
      { label: 'Delivery mismatch', value: 84 },
      { label: 'Claim repetition', value: 76 },
      { label: 'Amount sensitivity', value: 38 },
    ],
  },
  electronics: {
    label: 'Electronics',
    desc: 'Built for higher-value items where a single fraudulent refund costs more.',
    summary: 'Leans harder on amount, scripted messaging, and suspicious loss claims.',
    highlights: ['High-value protection', 'Serial defect claim scrutiny', 'Escalation on costly outliers'],
    emphasis: [
      { label: 'Delivery mismatch', value: 66 },
      { label: 'Cross-merchant history', value: 72 },
      { label: 'Amount sensitivity', value: 88 },
    ],
  },
};

export default function MerchantPresets({ onPresetChange }) {
  const [active, setActive] = useState('default');

  const handleChange = (key) => {
    setActive(key);
    if (onPresetChange) onPresetChange(key);
  };

  const currentPreset = PRESETS[active];

  return (
    <div className="glass-panel p-7 xl:p-8">
      <h2 className="section-title">Merchant playbooks</h2>
      <p className="section-copy mt-2">Choose the operating profile that matches the catalog. The dashboard keeps the explanation merchant-facing instead of exposing raw model weights.</p>

      <div className="mt-5 grid gap-3 lg:grid-cols-3">
        {Object.entries(PRESETS).map(([key, preset]) => (
          <button
            key={key}
            onClick={() => handleChange(key)}
            className={`rounded-3xl border p-5 text-left transition-all ${
              active === key
                ? 'border-blue-500/40 bg-blue-500/10'
                : 'border-gray-700 bg-gray-800/50 hover:border-gray-600'
            }`}
          >
            <p className={`text-lg font-semibold ${active === key ? 'text-blue-300' : 'text-white'}`}>
              {preset.label}
            </p>
            <p className="mt-2 text-sm leading-relaxed text-gray-400">{preset.desc}</p>
          </button>
        ))}
      </div>

      <div className="mt-5 rounded-3xl border border-gray-700 bg-gray-800/45 p-5">
        <p className="text-xs font-medium uppercase tracking-[0.18em] text-gray-500">{currentPreset.label} playbook</p>
        <p className="mt-3 text-base leading-relaxed text-gray-200">{currentPreset.summary}</p>

        <div className="mt-5 grid gap-5 xl:grid-cols-[1.05fr_0.95fr]">
          <div>
            <p className="text-sm font-medium text-white">Focus areas</p>
            <div className="mt-4 space-y-4">
              {currentPreset.emphasis.map((item) => (
                <div key={item.label}>
                  <div className="mb-2 flex items-center justify-between text-sm">
                    <span className="text-gray-300">{item.label}</span>
                    <span className="text-white">{item.value}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-gray-700/80">
                    <div className="h-2 rounded-full bg-blue-400" style={{ width: `${item.value}%` }} />
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <p className="text-sm font-medium text-white">Why merchants use this</p>
            <div className="mt-4 space-y-2">
              {currentPreset.highlights.map((item) => (
                <div key={item} className="rounded-2xl border border-gray-700 bg-gray-900/50 px-4 py-3 text-sm text-gray-300">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
