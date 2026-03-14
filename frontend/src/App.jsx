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
    <aside className="w-64 bg-gray-900 border-r border-gray-800 min-h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-800">
        <h1 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="text-2xl">🤖</span>
          RefundPilot
        </h1>
        <p className="text-xs text-gray-500 mt-1">The Instant Justice Machine</p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {NAV_ITEMS.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-blue-600/10 text-blue-400 border border-blue-500/20'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800'
              }`
            }
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <span className="w-2 h-2 rounded-full bg-green-500"></span>
          Agent Online
        </div>
        <p className="text-xs text-gray-700 mt-1">Pine Labs AI Hackathon 2026</p>
      </div>
    </aside>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <div className="flex min-h-screen bg-gray-950">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
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
