import { useEffect, useRef, useState } from 'react';
import { chatRefund, getCustomerDetail } from '../utils/api';

const PERSONAS = [
  {
    id: 'CUST-001',
    name: 'Priya Sharma',
    avatar: 'PS',
    tag: 'Loyal',
    tagColor: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/25',
    desc: '23 orders · 2% refund rate',
  },
  {
    id: 'CUST-004',
    name: 'Vikram Singh',
    avatar: 'VS',
    tag: 'Watchlist',
    tagColor: 'bg-amber-500/15 text-amber-300 border-amber-500/25',
    desc: '8 orders · 50% refund rate',
  },
  {
    id: 'CUST-002',
    name: 'Rohit Mehta',
    avatar: 'RM',
    tag: 'Abuse risk',
    tagColor: 'bg-rose-500/15 text-rose-300 border-rose-500/25',
    desc: '12 orders · 67% refund rate',
  },
];

const ORDER_ID_PATTERN = /ORD-\d+/i;
const ITEM_ID_PATTERN = /\b[A-Z]{4,5}-\d{3}\b/i;

const now = () => new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

const WELCOME_MSG = {
  role: 'agent',
  content:
    "Welcome to RefundPilot. Pick one of the demo customers below and I will open their purchase history. You can then click a recent order or enter another order ID or item SKU manually.",
  ts: now(),
};

const DECISION_META = {
  AUTO_APPROVE: {
    title: 'Refund initiated',
    panel: 'border-green-500/25 bg-green-500/10',
    titleClass: 'text-green-300',
    detailClass: 'text-green-400/80',
  },
  INVESTIGATE: {
    title: 'Case under investigation',
    panel: 'border-amber-500/25 bg-amber-500/10',
    titleClass: 'text-amber-300',
    detailClass: 'text-amber-400/80',
  },
  ESCALATE: {
    title: 'Escalated to manual review',
    panel: 'border-rose-500/25 bg-rose-500/10',
    titleClass: 'text-rose-300',
    detailClass: 'text-rose-400/80',
  },
};

const normaliseReference = (value) => value.trim().toUpperCase();

const getFirstName = (fullName = '') => fullName.split(' ')[0] || fullName;

export default function ChatRefundPanel() {
  const [persona, setPersona] = useState(null);
  const [customerProfile, setCustomerProfile] = useState(null);
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [manualReference, setManualReference] = useState('');
  const [lookupInput, setLookupInput] = useState('');
  const [loadingOrders, setLoadingOrders] = useState(false);
  const [history, setHistory] = useState([WELCOME_MSG]);
  const [message, setMessage] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [history]);

  const selectPersona = async (nextPersona) => {
    if (persona?.id === nextPersona.id) {
      return;
    }

    setPersona(nextPersona);
    setCustomerProfile(null);
    setOrders([]);
    setSelectedOrder(null);
    setManualReference('');
    setLookupInput('');
    setMessage('');
    setLoadingOrders(true);
    setHistory([
      {
        role: 'agent',
        content: `Opening ${getFirstName(nextPersona.name)}'s account. I will only process refunds for items that appear in this customer's purchase history.`,
        ts: now(),
      },
    ]);

    try {
      const res = await getCustomerDetail(nextPersona.id);
      const customer = res.data?.customer || null;
      const customerOrders = res.data?.orders || [];

      setCustomerProfile(customer);
      setOrders(customerOrders);

      if (customerOrders.length === 0) {
        setHistory([
          {
            role: 'agent',
            content: `I could not find any recent purchases for ${getFirstName(nextPersona.name)}. If you want to continue, enter an order ID or item SKU manually and I will verify it first.`,
            ts: now(),
          },
        ]);
        return;
      }

      setHistory([
        {
          role: 'agent',
          content: `Hi ${getFirstName(nextPersona.name)}. I found ${customerOrders.length} orders on this account. Pick one from the ledger on the right, or use the manual lookup box if the purchase is older.`,
          ts: now(),
        },
      ]);
    } catch {
      setHistory([
        {
          role: 'agent',
          content: `I could not load ${getFirstName(nextPersona.name)}'s order list just now. You can still type an order ID or item SKU manually and I will validate it before processing anything.`,
          ts: now(),
        },
      ]);
    } finally {
      setLoadingOrders(false);
    }
  };

  const selectOrder = (order) => {
    if (!persona || selectedOrder?.id === order.id) {
      return;
    }

    setSelectedOrder(order);
    setManualReference('');
    setLookupInput('');
    setHistory((prev) => [
      ...prev,
      {
        role: 'agent',
        content: `Pinned ${order.product_name} (${order.id}). Tell me what went wrong and I will validate the claim against ${getFirstName(persona.name)}'s purchase history before I submit anything.`,
        ts: now(),
        helper: true,
      },
    ]);
  };

  const handleLookupReference = () => {
    if (!persona) {
      return;
    }

    const reference = normaliseReference(lookupInput);
    if (!reference) {
      return;
    }

    const matchedOrder = orders.find(
      (order) => order.id.toUpperCase() === reference || order.product_sku?.toUpperCase() === reference,
    );

    setLookupInput('');

    if (matchedOrder) {
      selectOrder(matchedOrder);
      return;
    }

    setSelectedOrder(null);
    setManualReference(reference);
    setHistory((prev) => [
      ...prev,
      {
        role: 'agent',
        content: `Okay. Send the issue details for ${reference} and I will first check whether it belongs to ${getFirstName(persona.name)}'s account.`,
        ts: now(),
        helper: true,
      },
    ]);
  };

  const clearSelection = () => {
    setSelectedOrder(null);
    setManualReference('');
  };

  const handleSend = async (text) => {
    const visibleMessage = text || message;
    if (!visibleMessage.trim()) {
      return;
    }

    if (!persona) {
      setHistory((prev) => [
        ...prev,
        { role: 'user', content: visibleMessage, ts: now() },
        {
          role: 'agent',
          content: 'Pick a customer profile first so I know which account to validate against.',
          ts: now(),
        },
      ]);
      setMessage('');
      return;
    }

    let enrichedMessage = visibleMessage;
    const hasOrderId = ORDER_ID_PATTERN.test(enrichedMessage);
    const hasItemId = ITEM_ID_PATTERN.test(enrichedMessage);

    if (!/CUST-\d+/i.test(enrichedMessage)) {
      enrichedMessage = `${enrichedMessage} [customer: ${persona.id}]`;
    }

    if (!hasOrderId && selectedOrder) {
      enrichedMessage = `${enrichedMessage} [order: ${selectedOrder.id}]`;
    } else if (!hasOrderId && manualReference) {
      const manualIsOrder = ORDER_ID_PATTERN.test(manualReference);
      if (manualIsOrder || !hasItemId) {
        enrichedMessage = `${enrichedMessage} [${manualIsOrder ? 'order' : 'item'}: ${manualReference}]`;
      }
    }

    setHistory((prev) => [...prev, { role: 'user', content: visibleMessage, ts: now() }]);
    setMessage('');
    setLoading(true);

    try {
      const res = await chatRefund(enrichedMessage, language);
      const data = res.data;
      const agentTs = now();

      if (data.refund_id && data.decision) {
        setHistory((prev) => [
          ...prev,
          {
            role: 'agent',
            content: data.message,
            ts: agentTs,
            workflow: true,
            submitted: data.refund_submitted,
            refundId: data.refund_id,
            score: data.risk_score ?? '—',
            decision: data.decision,
            caseStatus: data.case_status,
          },
        ]);
        return;
      }

      setHistory((prev) => [...prev, { role: 'agent', content: data.message, ts: agentTs }]);
    } catch {
      setHistory((prev) => [
        ...prev,
        { role: 'agent', content: 'Something went wrong. Please try again.', ts: now() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const selectionLabel = selectedOrder
    ? `${selectedOrder.product_name} · ${selectedOrder.id}`
    : manualReference
      ? manualReference
      : null;

  const inputPlaceholder = !persona
    ? 'Pick a customer first...'
    : selectedOrder
      ? `Tell me what happened with ${selectedOrder.product_name.toLowerCase()}...`
      : manualReference
        ? `Describe the issue for ${manualReference}...`
        : `Message as ${getFirstName(persona.name)}...`;

  return (
    <div className="flex h-full gap-6">
      <div className="glass-panel flex min-w-0 flex-1 flex-col overflow-hidden">
        <div className="flex items-center gap-4 border-b border-slate-800 px-6 py-4">
          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-green-500/20 text-lg font-semibold text-green-300">
            RP
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-base font-semibold text-white">RefundPilot Agent</h2>
            <p className="text-sm text-green-400">Online · Validates every claim before refunding</p>
          </div>
          <div className="flex gap-2">
            {['en', 'hi'].map((option) => (
              <button
                key={option}
                onClick={() => setLanguage(option)}
                className={`rounded-full px-3 py-1 text-sm transition-colors ${
                  language === option ? 'bg-green-600 text-white' : 'bg-slate-800 text-slate-500 hover:text-white'
                }`}
              >
                {option === 'en' ? 'EN' : 'हि'}
              </button>
            ))}
          </div>
        </div>

        <div
          className="flex-1 space-y-4 overflow-y-auto px-5 py-5 xl:px-6"
          style={{ backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(30,40,60,0.25) 0%, transparent 100%)' }}
        >
          {history.map((entry, index) => (
            <div key={index} className={`flex ${entry.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div
                className={`max-w-[82%] whitespace-pre-line rounded-3xl p-4 text-[15px] leading-relaxed ${
                  entry.role === 'user'
                    ? 'rounded-br-md bg-blue-600 text-white'
                    : 'rounded-bl-md border border-slate-700 bg-slate-800 text-slate-200'
                }`}
              >
                {entry.helper && (
                  <span className="mb-2 block text-xs font-medium uppercase tracking-[0.16em] text-sky-300">
                    Account context updated
                  </span>
                )}
                {entry.content}
                {entry.workflow && (() => {
                  const meta = DECISION_META[entry.decision] || DECISION_META.INVESTIGATE;

                  return (
                    <div className={`mt-3 rounded-2xl border px-4 py-3 ${meta.panel}`}>
                      <p className={`text-sm font-medium ${meta.titleClass}`}>{meta.title}</p>
                      <p className="mt-1 text-xs text-white/80">Reference {entry.refundId}</p>
                      {entry.score && <p className={`mt-1 text-xs ${meta.detailClass}`}>Risk score {entry.score}/100</p>}
                      {entry.caseStatus && <p className="mt-1 text-xs text-white/60">Status {entry.caseStatus}</p>}
                    </div>
                  );
                })()}
                <span className={`mt-2 block text-xs ${entry.role === 'user' ? 'text-blue-200/70' : 'text-slate-500'}`}>
                  {entry.ts}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl rounded-bl-md border border-slate-700 bg-slate-800 px-5 py-3">
                <span className="text-sm text-slate-400">typing...</span>
              </div>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        <div className="border-t border-slate-800/70 px-4 py-3">
          <p className="mb-2 text-xs font-medium uppercase tracking-[0.16em] text-slate-500">Choose a customer</p>
          <div className="flex gap-2 overflow-x-auto pb-1">
            {PERSONAS.map((option) => (
              <button
                key={option.id}
                onClick={() => selectPersona(option)}
                className={`group flex shrink-0 items-center gap-3 rounded-2xl border px-4 py-3 text-left transition-all ${
                  persona?.id === option.id
                    ? 'border-blue-500/40 bg-blue-500/10'
                    : 'border-slate-700 bg-slate-800/60 hover:border-slate-600'
                }`}
              >
                <div className="flex h-9 w-9 items-center justify-center rounded-full bg-slate-700 text-xs font-bold text-white">
                  {option.avatar}
                </div>
                <div>
                  <p className={`text-sm font-medium ${persona?.id === option.id ? 'text-blue-300' : 'text-white'}`}>
                    {option.name}
                  </p>
                  <p className="text-xs text-slate-500">{option.desc}</p>
                </div>
                <span className={`ml-1 rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider ${option.tagColor}`}>
                  {option.tag}
                </span>
              </button>
            ))}
          </div>
        </div>

        <div className="border-t border-slate-800/70 px-5 py-3">
          {selectionLabel ? (
            <div className="flex items-center justify-between gap-3 rounded-2xl border border-blue-500/20 bg-blue-500/10 px-4 py-3">
              <div>
                <p className="text-xs font-medium uppercase tracking-[0.16em] text-blue-300">Current claim context</p>
                <p className="mt-1 text-sm text-white">{selectionLabel}</p>
              </div>
              <button
                type="button"
                onClick={clearSelection}
                className="rounded-full border border-slate-700 px-3 py-1 text-xs text-slate-400 transition-colors hover:text-white"
              >
                Clear
              </button>
            </div>
          ) : (
            <p className="text-sm text-slate-500">
              Pick an order from the right-side purchase ledger or enter another order ID or item SKU manually.
            </p>
          )}
        </div>

        <div className="flex gap-3 border-t border-slate-800 px-5 py-4">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder={inputPlaceholder}
            disabled={!persona}
            className="flex-1 rounded-full border border-slate-700 bg-slate-800 px-5 py-3.5 text-base text-white placeholder:text-slate-500 focus:border-green-500 focus:outline-none disabled:opacity-40"
          />
          <button
            onClick={() => handleSend()}
            disabled={loading || !message.trim() || !persona}
            className="flex h-12 w-12 items-center justify-center rounded-full bg-green-600 text-white transition-colors hover:bg-green-500 disabled:opacity-30"
          >
            ➤
          </button>
        </div>
      </div>

      <div className="hidden w-[390px] shrink-0 xl:block">
        <div className="glass-panel flex h-full flex-col overflow-hidden">
          <div className="border-b border-slate-800 px-5 py-4">
            <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">
              {persona ? `${persona.name}'s purchase context` : 'Purchase context'}
            </p>
            <p className="mt-1 text-sm text-slate-400">
              {persona
                ? 'Use this ledger to prove what the customer actually bought before refunding.'
                : 'Choose a customer below to load their orders here.'}
            </p>
          </div>

          {!persona && (
            <div className="flex flex-1 items-center justify-center px-6 text-center text-sm text-slate-500">
              Pick a scenario to open the customer profile, recent orders, and manual lookup tools.
            </div>
          )}

          {persona && (
            <>
              <div className="border-b border-slate-800 px-5 py-4">
                <div className="grid grid-cols-2 gap-3">
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Customer</p>
                    <p className="mt-2 text-lg font-semibold text-white">{persona.id}</p>
                    <p className="mt-1 text-sm text-slate-400">{customerProfile?.city || 'City unknown'}</p>
                  </div>
                  <div className="rounded-2xl border border-slate-800 bg-slate-950/50 p-4">
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Refund rate</p>
                    <p className="mt-2 text-lg font-semibold text-white">
                      {customerProfile ? `${(customerProfile.refund_rate * 100).toFixed(0)}%` : '--'}
                    </p>
                    <p className="mt-1 text-sm text-slate-400">
                      {customerProfile ? `${customerProfile.total_refunds} refunds on ${customerProfile.total_orders} orders` : 'Loading account'}
                    </p>
                  </div>
                </div>

                <div className="mt-4 rounded-2xl border border-slate-800 bg-slate-950/80 p-4 font-mono text-[11px] leading-relaxed text-slate-400">
                  <p>SELECT order_id, product_sku, product_name, amount</p>
                  <p>FROM orders</p>
                  <p>WHERE customer_id = '{persona.id}'</p>
                  <p>ORDER BY order_date DESC</p>
                  <p>LIMIT 8;</p>
                </div>
              </div>

              <div className="border-b border-slate-800 px-4 py-4">
                <div className="flex items-center justify-between gap-3 px-1">
                  <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">Purchase ledger</p>
                  {loadingOrders && <span className="text-xs text-slate-500">Loading...</span>}
                </div>

                <div className="mt-3 overflow-hidden rounded-2xl border border-slate-800 bg-slate-950/50">
                  <div className="grid grid-cols-[96px_86px_minmax(0,1fr)_68px] gap-2 border-b border-slate-800 px-3 py-2 font-mono text-[10px] uppercase tracking-[0.16em] text-slate-500">
                    <span>Order</span>
                    <span>Item</span>
                    <span>Product</span>
                    <span className="text-right">Value</span>
                  </div>

                  <div className="max-h-[360px] overflow-y-auto">
                    {!loadingOrders && orders.length === 0 && (
                      <p className="px-4 py-8 text-center text-sm text-slate-500">No orders found for this customer.</p>
                    )}

                    {orders.slice(0, 8).map((order) => {
                      const isSelected = selectedOrder?.id === order.id;

                      return (
                        <button
                          key={order.id}
                          onClick={() => selectOrder(order)}
                          className={`grid w-full grid-cols-[96px_86px_minmax(0,1fr)_68px] gap-2 border-t border-slate-800 px-3 py-3 text-left transition-colors ${
                            isSelected ? 'bg-blue-500/10' : 'hover:bg-slate-900/60'
                          }`}
                        >
                          <span className="font-mono text-[11px] text-slate-300">{order.id}</span>
                          <span className="font-mono text-[11px] text-sky-300">{order.product_sku}</span>
                          <span className="truncate pr-2 text-sm text-white">{order.product_name}</span>
                          <span className="text-right text-sm text-white">₹{order.amount}</span>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>

              <div className="border-b border-slate-800 px-5 py-4">
                <p className="text-xs font-medium uppercase tracking-[0.16em] text-slate-500">Other item</p>
                <p className="mt-1 text-sm text-slate-400">
                  Paste an order ID like ORD-1001 or an item SKU like FASH-001. I will verify it before processing the claim.
                </p>
                <div className="mt-3 flex gap-2">
                  <input
                    type="text"
                    value={lookupInput}
                    onChange={(e) => setLookupInput(e.target.value.toUpperCase())}
                    onKeyDown={(e) => e.key === 'Enter' && handleLookupReference()}
                    placeholder="ORD-1001 or FASH-001"
                    className="flex-1 rounded-2xl border border-slate-700 bg-slate-900 px-4 py-3 text-sm text-white placeholder:text-slate-500 focus:border-blue-500 focus:outline-none"
                  />
                  <button
                    type="button"
                    onClick={handleLookupReference}
                    disabled={!lookupInput.trim()}
                    className="rounded-2xl bg-slate-800 px-4 py-3 text-sm text-white transition-colors hover:bg-slate-700 disabled:opacity-40"
                  >
                    Use
                  </button>
                </div>
              </div>

              <div className="mt-auto px-5 py-4 text-[11px] leading-relaxed text-slate-500">
                RefundPilot blocks claims for items that do not belong to the selected customer. If the item is not in this ledger, the backend will reject the claim and ask for a valid purchase reference.
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
