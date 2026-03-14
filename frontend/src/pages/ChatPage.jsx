import ChatRefundPanel from '../components/ChatRefundPanel';

export default function ChatPage() {
  return (
    <div className="max-w-4xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Conversational Refund</h1>
        <p className="text-gray-400 mt-1">Submit refund requests in natural language — English or Hindi</p>
      </div>
      <ChatRefundPanel />
    </div>
  );
}
