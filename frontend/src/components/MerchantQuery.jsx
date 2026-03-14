import { useState } from 'react';
import { merchantQuery } from '../utils/api';

export default function MerchantQuery() {
  const [query, setQuery] = useState('');
  const [answer, setAnswer] = useState(null);
  const [loading, setLoading] = useState(false);

  const presets = [
    'Show me flagged refunds',
    'How much fraud did we catch?',
    'Top abusers by refund rate',
    'Product defect rates',
    'Fraud ring addresses',
  ];

  const handleSubmit = async (q) => {
    const text = q || query;
    if (!text) return;
    setLoading(true);
    try {
      const res = await merchantQuery(text);
      setAnswer(res.data);
    } catch {
      setAnswer({ answer: 'Query failed', data: null });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel p-7 xl:p-8">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="section-title">Ask the dashboard</h2>
          <p className="section-copy mt-2">Use plain language to pull out refunds, fraud clusters, or merchant-facing takeaways.</p>
        </div>
      </div>

      <div className="mt-5 flex flex-col gap-3 sm:flex-row">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="Ask about refunds, risk clusters, or product anomalies..."
          className="flex-1 rounded-2xl border border-gray-700 bg-gray-800 px-5 py-4 text-base text-white focus:border-blue-500 focus:outline-none"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={loading}
          className="rounded-2xl bg-blue-600 px-5 py-4 text-base font-medium text-white disabled:opacity-50"
        >
          {loading ? 'Thinking...' : 'Ask'}
        </button>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {presets.map((p) => (
          <button
            key={p}
            onClick={() => { setQuery(p); handleSubmit(p); }}
            className="rounded-full border border-gray-700 bg-gray-800 px-4 py-2 text-sm text-gray-400 hover:border-gray-600 hover:text-white"
          >
            {p}
          </button>
        ))}
      </div>

      {answer && (
        <div className="mt-5 rounded-3xl border border-gray-700 bg-gray-800/45 p-5">
          <p className="text-xs font-medium uppercase tracking-[0.18em] text-gray-500">Assistant summary</p>
          <p className="mt-3 text-base leading-relaxed text-gray-200">{answer.answer}</p>
        </div>
      )}
    </div>
  );
}
