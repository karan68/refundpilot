export default function StoreCredit({ action }) {
  if (!action || action.type !== 'store_credit_offer') {
    return null;
  }

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-green-500/30">
      <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
        🎁 Store Credit Offer
      </h2>

      <div className="bg-gray-800/50 rounded-lg p-4 mb-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-gray-400 text-sm">Cash refund</span>
          <span className="text-white font-mono">₹{action.cash_refund_amount}</span>
        </div>
        <div className="flex items-center justify-between mb-3">
          <span className="text-gray-400 text-sm">Bonus added</span>
          <span className="text-green-400 font-mono">+₹{action.bonus}</span>
        </div>
        <div className="border-t border-gray-700 pt-3 flex items-center justify-between">
          <span className="text-white font-semibold">Store credit total</span>
          <span className="text-green-400 font-bold text-xl">₹{action.credit_amount}</span>
        </div>
      </div>

      <p className="text-gray-400 text-sm mb-4">{action.message}</p>

      {action.pine_labs_link && (
        <div className="flex gap-3">
          <a
            href={action.pine_labs_link.payment_link}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 py-3 rounded-lg bg-green-600 hover:bg-green-700 text-white font-semibold text-sm text-center transition-colors"
          >
            Accept Store Credit (₹{action.credit_amount})
          </a>
          <button className="px-4 py-3 rounded-lg border border-gray-700 text-gray-400 text-sm hover:text-white hover:border-gray-500 transition-colors">
            Prefer Cash
          </button>
        </div>
      )}

      {action.pine_labs_link?.simulated && (
        <p className="text-xs text-yellow-600 mt-3">⚠ Simulated Pine Labs payment link (demo mode)</p>
      )}
    </div>
  );
}
