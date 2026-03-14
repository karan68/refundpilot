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
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">💬 Ask Your Data</h2>

      <div className="flex gap-2 mb-3">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSubmit()}
          placeholder="Ask anything about your refunds..."
          className="flex-1 p-3 rounded-lg bg-gray-800 border border-gray-700 text-white text-sm focus:border-blue-500 focus:outline-none"
        />
        <button
          onClick={() => handleSubmit()}
          disabled={loading}
          className="px-4 py-3 rounded-lg bg-blue-600 text-white text-sm disabled:opacity-50"
        >
          {loading ? '...' : 'Ask'}
        </button>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {presets.map((p) => (
          <button
            key={p}
            onClick={() => { setQuery(p); handleSubmit(p); }}
            className="px-3 py-1.5 rounded-lg bg-gray-800 border border-gray-700 text-gray-400 text-xs hover:text-white hover:border-gray-600"
          >
            {p}
          </button>
        ))}
      </div>

      {answer && (
        <div className="p-4 rounded-lg bg-gray-800/50 border border-gray-700">
          <p className="text-gray-200 text-sm leading-relaxed">{answer.answer}</p>
        </div>
      )}
    </div>
  );
}
