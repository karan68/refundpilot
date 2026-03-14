import DashboardStats from '../components/DashboardStats';
import AlertBanner from '../components/AlertBanner';
import MerchantQuery from '../components/MerchantQuery';
import FraudGraph from '../components/FraudGraph';
import CohortInsights from '../components/CohortInsights';
import AuditLog from '../components/AuditLog';
import ReconciliationTab from '../components/ReconciliationTab';
import MerchantPresets from '../components/MerchantPresets';

export default function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white">Merchant Dashboard</h1>
        <p className="text-gray-400 mt-1">Real-time refund analytics, fraud detection, and agent performance</p>
      </div>

      <AlertBanner />
      <DashboardStats />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <MerchantQuery />
        <MerchantPresets />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <FraudGraph />
        <CohortInsights />
      </div>

      <div className="mt-6">
        <ReconciliationTab />
      </div>

      <div className="mt-6">
        <AuditLog />
      </div>
    </div>
  );
}
