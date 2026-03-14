import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import CustomerPage from './pages/CustomerPage';
import DashboardPage from './pages/DashboardPage';
import DemoPage from './pages/DemoPage';
import ChatPage from './pages/ChatPage';
import RefundDetailPage from './pages/RefundDetailPage';

const NAV_ITEMS = [
  { path: '/', label: 'Submit Refund', icon: '📝' },
  { path: '/dashboard', label: 'Dashboard', icon: '📊' },
  { path: '/chat', label: 'Chat Refund', icon: '💬' },
  { path: '/demo', label: 'Live Demo', icon: '⚡' },
];

function Sidebar() {
  return (
    <aside className="hidden min-h-screen w-72 shrink-0 border-r border-slate-800/80 bg-slate-950/90 backdrop-blur lg:flex lg:flex-col">
      <div className="border-b border-slate-800/80 px-7 py-7">
        <h1 className="text-2xl font-semibold tracking-tight text-white">RefundPilot</h1>
        <p className="mt-2 text-sm text-slate-500">Instant refund operations for Pine Labs merchants</p>
      </div>

      <nav className="flex-1 space-y-1.5 px-5 py-5">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 rounded-xl px-4 py-3.5 text-[15px] font-medium transition-colors ${
                isActive
                  ? 'border border-blue-500/20 bg-blue-600/10 text-blue-300'
                  : 'text-slate-400 hover:bg-slate-800/70 hover:text-white'
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-slate-800/80 px-5 py-5">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500"></span>
          Agent Online
        </div>
        <p className="mt-2 text-xs uppercase tracking-[0.18em] text-slate-700">Pine Labs AI Hackathon 2026</p>
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-transparent">
        <Sidebar />
        <main className="flex-1 overflow-y-auto bg-transparent">
          <Routes>
            <Route path="/" element={<CustomerPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/demo" element={<DemoPage />} />
            <Route path="/refund/:id" element={<RefundDetailPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
