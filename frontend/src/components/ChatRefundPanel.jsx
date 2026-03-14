import { useState } from 'react';
import { chatRefund } from '../utils/api';

export default function ChatRefundPanel() {
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('en');
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!message.trim()) return;
    const userMsg = message;
    setHistory(prev => [...prev, { role: 'user', content: userMsg }]);
    setMessage('');
    setLoading(true);

    try {
      const res = await chatRefund(userMsg, language);
      const d = res.data;
      setHistory(prev => [...prev, {
        role: 'agent',
        content: d.message,
        refundId: d.refund_id,
        submitted: d.refund_submitted,
        parsed: d.parsed,
      }]);
    } catch {
      setHistory(prev => [...prev, { role: 'agent', content: 'Something went wrong. Try again.' }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">💬 Chat Refund (F25)</h2>
      <p className="text-xs text-gray-500 mb-3">Type a refund request in natural language. Include customer ID and order ID.</p>

      {/* Language toggle */}
      <div className="flex gap-2 mb-3">
        {['en', 'hi'].map(l => (
          <button key={l} onClick={() => setLanguage(l)}
            className={`px-3 py-1 rounded text-xs ${language === l ? 'bg-blue-600 text-white' : 'bg-gray-800 text-gray-400 border border-gray-700'}`}>
            {l === 'en' ? 'English' : 'हिन्दी'}
          </button>
        ))}
      </div>

      {/* Chat history */}
      <div className="space-y-2 mb-3 max-h-64 overflow-y-auto">
        {history.map((msg, i) => (
          <div key={i} className={`p-3 rounded-lg text-sm ${
            msg.role === 'user' ? 'bg-blue-500/10 border border-blue-500/20 text-blue-300 ml-8' :
            'bg-gray-800/50 border border-gray-700 text-gray-300 mr-8'
          }`}>
            <span className="text-xs text-gray-500 block mb-1">{msg.role === 'user' ? '👤 You' : '🤖 Agent'}</span>
            {msg.content}
            {msg.submitted && (
              <span className="block mt-1 text-xs text-green-400">✅ Refund {msg.refundId} submitted</span>
            )}
            {msg.parsed && !msg.submitted && (
              <span className="block mt-1 text-xs text-yellow-400">Parsed: {JSON.stringify(msg.parsed)}</span>
            )}
          </div>
        ))}
        {loading && (
          <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700 text-gray-500 text-sm mr-8">
            🤖 Agent is thinking...
          </div>
        )}
      </div>

      {/* Input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder={language === 'en' ? 'e.g. CUST-001 wants refund for ORD-1001, kurta damaged' : 'e.g. CUST-001 ka ORD-1001 ka refund chahiye, kurta tuta hua'}
          className="flex-1 p-3 rounded-lg bg-gray-800 border border-gray-700 text-white text-sm focus:border-blue-500 focus:outline-none"
        />
        <button onClick={handleSend} disabled={loading}
          className="px-4 py-3 rounded-lg bg-blue-600 text-white text-sm disabled:opacity-50">
          Send
        </button>
      </div>
    </div>
  );
}
