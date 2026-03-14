import ChatRefundPanel from '../components/ChatRefundPanel';

export default function ChatPage() {
  return (
    <div className="page-shell max-w-[1380px]">
      <div className="page-header">
        <h1 className="page-title">Conversational Refund</h1>
        <p className="page-subtitle">Submit refund requests in natural language and see the agent respond with a full refund workflow.</p>
      </div>
      <ChatRefundPanel />
    </div>
  );
}
