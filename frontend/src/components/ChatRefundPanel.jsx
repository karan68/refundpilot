import { useState, useRef, useEffect } from 'react';
import { chatRefund } from '../utils/api';

const DEMO_CONVERSATION = [
  { role: 'agent', content: "Hi! I'm RefundPilot. I can help you process a refund. Just describe your issue — I understand English and Hindi. 🛍️", ts: '9:01 AM' },
  { role: 'user', content: "Hi, I bought a dress and it arrived torn. I want my money back.", ts: '9:02 AM' },
  { role: 'agent', content: "I'm sorry to hear that! I'd like to help. Could you share your Customer ID and Order ID? You can find them in your order confirmation email.\n\n💡 For example: \"My ID is CUST-001 and order is ORD-1001\"", ts: '9:02 AM' },
  { role: 'user', content: "My customer ID is CUST-001 and order number is ORD-1001", ts: '9:03 AM' },
  { role: 'agent', content: "✅ Got it! Processing your refund now...\n\n📋 Order: ORD-1001 — Cotton Kurta - Blue (₹800)\n🔍 Reason: Damaged\n\n🤖 Agent scored your request: 28/100 → Auto-Approved!\n⚡ Refund of ₹800 initiated. Return pickup will be scheduled.\n\nRefund ID: REF-DEMO-001", ts: '9:03 AM', submitted: true, refundId: 'REF-DEMO-001' },
];

const QUICK_PROMPTS = [
  "I bought a kurta and it's torn",
  "CUST-005 ka ORD-5001 ka refund chahiye",
  "My earbuds stopped working, order ORD-3001",
  "CUST-002 wants refund for ORD-2001, shoes damaged",
];

export default function ChatRefundPanel() {
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('en');
  const [history, setHistory] = useState(DEMO_CONVERSATION);
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const handleSend = async (text) => {
    const msg = text || message;
    if (!msg.trim()) return;
    const ts = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    setHistory(prev => [...prev, { role: 'user', content: msg, ts }]);
    setMessage('');
    setLoading(true);

    try {
      const res = await chatRefund(msg, language);
      const d = res.data;
      const agentTs = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

      if (d.refund_submitted) {
        setHistory(prev => [...prev, {
          role: 'agent',
          content: d.message,
          ts: agentTs,
          submitted: true,
          refundId: d.refund_id,
        }]);
      } else if (d.parsed && !d.parsed.customer_id) {
        // No customer ID found — ask for it conversationally
        setHistory(prev => [...prev, {
          role: 'agent',
          content: "I understand your issue! To process the refund, I need your Customer ID and Order ID. Could you share them?\n\n💡 Try: \"My ID is CUST-001 and order is ORD-1001\"\n\n📋 Available test customers: Priya (CUST-001), Rohit (CUST-002), Vikram (CUST-004), Meera (CUST-005)",
          ts: agentTs,
        }]);
      } else {
        setHistory(prev => [...prev, {
          role: 'agent',
          content: d.message,
          ts: agentTs,
          parsed: d.parsed,
        }]);
      }
    } catch {
      setHistory(prev => [...prev, { role: 'agent', content: 'Something went wrong. Please try again.', ts: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel flex flex-col overflow-hidden" style={{ minHeight: '680px', height: '72vh' }}>
      <div className="flex items-center gap-4 border-b border-gray-800 px-6 py-5">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-green-500/20 text-xl">🤖</div>
        <div>
          <h2 className="text-base font-semibold text-white">RefundPilot Agent</h2>
          <p className="text-sm text-green-400">Online · Responds instantly</p>
        </div>
        <div className="ml-auto flex gap-2">
          {['en', 'hi'].map(l => (
            <button key={l} onClick={() => setLanguage(l)}
              className={`rounded-full px-3 py-1 text-sm ${language === l ? 'bg-green-600 text-white' : 'bg-gray-800 text-gray-500'}`}>
              {l === 'en' ? 'EN' : 'हि'}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto p-5 xl:p-6" style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(30,40,60,0.3) 0%, transparent 100%)' }}>
        {history.map((msg, i) => (
          <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`max-w-[82%] whitespace-pre-line rounded-3xl p-4 text-base ${
              msg.role === 'user'
                ? 'bg-blue-600 text-white rounded-br-md'
                : 'bg-gray-800 text-gray-200 rounded-bl-md border border-gray-700'
            }`}>
              {msg.content}
              {msg.submitted && (
                <span className="mt-3 block text-sm font-medium text-green-300">✅ Refund {msg.refundId} processed</span>
              )}
              <span className={`mt-2 block text-xs ${msg.role === 'user' ? 'text-blue-200' : 'text-gray-500'}`}>{msg.ts}</span>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-md border border-gray-700 bg-gray-800 p-4">
              <span className="text-base text-gray-400">typing...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="flex gap-2 overflow-x-auto border-t border-gray-800/50 px-5 py-3">
        {QUICK_PROMPTS.map((p, i) => (
          <button key={i} onClick={() => handleSend(p)}
            className="shrink-0 rounded-full border border-gray-700 bg-gray-800 px-4 py-2 text-sm whitespace-nowrap text-gray-400 hover:border-gray-500 hover:text-white">
            {p}
          </button>
        ))}
      </div>

      <div className="flex gap-3 border-t border-gray-800 px-5 py-4">
        <input
          type="text"
          value={message}
          onChange={e => setMessage(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          placeholder="Type your refund request..."
          className="flex-1 rounded-full border border-gray-700 bg-gray-800 px-5 py-3.5 text-base text-white focus:border-green-500 focus:outline-none"
        />
        <button onClick={() => handleSend()} disabled={loading || !message.trim()}
          className="flex h-12 w-12 items-center justify-center rounded-full bg-green-600 text-white disabled:opacity-30">
          ➤
        </button>
      </div>
    </div>
  );
}
