import { useState } from 'react';
import { useRefund } from '../hooks/useRefund';
import { REFUND_REASONS, CUSTOMER_PRESETS, ORDER_PRESETS } from '../utils/constants';

export default function RefundForm({ onResult }) {
  const { submit, loading, error } = useRefund();
  const [selectedCustomer, setSelectedCustomer] = useState('');
  const [reason, setReason] = useState('damaged_in_transit');
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('en');

  const handleCustomerSelect = (customerId) => {
    setSelectedCustomer(customerId);
    // Auto-fill message based on customer preset
    const preset = ORDER_PRESETS[customerId];
    if (preset) {
      setMessage(`My ${preset.product} arrived damaged. I would like a refund please.`);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedCustomer) return;

    const preset = ORDER_PRESETS[selectedCustomer];
    const data = {
      customer_id: selectedCustomer,
      order_id: preset.order_id,
      reason,
      message,
      language,
    };

    try {
      const result = await submit(data);
      if (onResult) onResult(result);
    } catch (err) {
      // error is handled by hook
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Customer Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Select Customer</label>
        <div className="grid grid-cols-3 gap-2">
          {CUSTOMER_PRESETS.map((c) => (
            <button
              key={c.id}
              type="button"
              onClick={() => handleCustomerSelect(c.id)}
              className={`p-2.5 rounded-lg border text-left text-sm transition-all ${
                selectedCustomer === c.id
                  ? 'border-blue-500 bg-blue-500/10 text-white'
                  : 'border-gray-700 bg-gray-800/50 text-gray-400 hover:border-gray-600'
              }`}
            >
              <span className="font-medium">{c.name}</span>
              <span className="text-xs text-gray-600 block">{c.id}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Order Info (auto-filled) */}
      {selectedCustomer && ORDER_PRESETS[selectedCustomer] && (
        <div className="p-3 rounded-lg bg-gray-800/50 border border-gray-700">
          <p className="text-xs text-gray-500 mb-1">Order</p>
          <p className="text-sm text-white">
            {ORDER_PRESETS[selectedCustomer].order_id} — {ORDER_PRESETS[selectedCustomer].product}
          </p>
          <p className="text-sm text-gray-400">₹{ORDER_PRESETS[selectedCustomer].amount}</p>
        </div>
      )}

      {/* Reason */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Refund Reason</label>
        <select
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          className="w-full p-3 rounded-lg bg-gray-800 border border-gray-700 text-white text-sm focus:border-blue-500 focus:outline-none"
        >
          {REFUND_REASONS.map((r) => (
            <option key={r.value} value={r.value}>{r.label}</option>
          ))}
        </select>
      </div>

      {/* Message */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Message</label>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          rows={3}
          placeholder="Describe your issue..."
          className="w-full p-3 rounded-lg bg-gray-800 border border-gray-700 text-white text-sm focus:border-blue-500 focus:outline-none resize-none"
        />
      </div>

      {/* Language */}
      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">Language</label>
        <div className="flex gap-2">
          {['en', 'hi', 'ta'].map((lang) => (
            <button
              key={lang}
              type="button"
              onClick={() => setLanguage(lang)}
              className={`px-4 py-2 rounded-lg text-sm ${
                language === lang
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-400 border border-gray-700'
              }`}
            >
              {lang === 'en' ? 'English' : lang === 'hi' ? 'हिन्दी' : 'தமிழ்'}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <p className="text-red-400 text-sm">{error}</p>
      )}

      {/* Submit */}
      <button
        type="submit"
        disabled={!selectedCustomer || loading}
        className="w-full py-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {loading ? 'Processing...' : 'Submit Refund Request'}
      </button>
    </form>
  );
}
