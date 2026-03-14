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
    <div className="page-shell">
      <div className="page-header">
        <div className="inline-flex w-fit items-center rounded-full border border-slate-700/80 bg-slate-900/80 px-3 py-1 text-xs font-medium uppercase tracking-[0.18em] text-slate-400">
          Merchant view
        </div>
        <h1 className="page-title">Merchant Dashboard</h1>
        <p className="page-subtitle">A clearer view of refund health, active risk clusters, and the actions that need merchant attention.</p>
      </div>

      <AlertBanner />
      <DashboardStats />

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
        <MerchantQuery />
        <MerchantPresets />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
        <FraudGraph />
        <CohortInsights />
      </div>

      <div className="mt-6 grid grid-cols-1 gap-6 xl:grid-cols-2">
        <ReconciliationTab />
        <AuditLog />
      </div>
    </div>
  );
}
