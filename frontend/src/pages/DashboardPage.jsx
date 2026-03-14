import DashboardStats from '../components/DashboardStats';

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Merchant Dashboard</h1>
        <p className="text-gray-400 mt-1">Real-time refund analytics, fraud detection, and agent performance</p>
      </div>
      <DashboardStats />
    </div>
  );
}
