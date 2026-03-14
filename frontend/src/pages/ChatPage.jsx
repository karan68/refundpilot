import ChatRefundPanel from '../components/ChatRefundPanel';

export default function ChatPage() {
  return (
    <div className="page-shell">
      <div className="page-header">
        <h1 className="page-title">Conversational Refund</h1>
        <p className="page-subtitle">
          Pick a customer, browse their real orders, and request a refund in plain language.
          The agent verifies the item was actually purchased before processing anything.
        </p>
      </div>
      <div style={{ height: 'calc(100vh - 210px)', minHeight: '620px' }}>
        <ChatRefundPanel />
      </div>
    </div>
  );
}
