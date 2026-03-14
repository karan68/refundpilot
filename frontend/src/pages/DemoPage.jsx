export default function DemoPage() {
  return (
    <div className="max-w-7xl mx-auto py-8 px-4">
      <div className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-white">⚡ RefundPilot Live Demo</h1>
        <p className="text-gray-400 mt-2 text-lg">Priya vs Rohit — Side by Side</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Priya's Side */}
        <div className="bg-gray-900 rounded-2xl p-6 border-2 border-green-500/30">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">🟢</span>
            <div>
              <h2 className="text-xl font-bold text-white">Priya Sharma</h2>
              <p className="text-green-400 text-sm">Loyal Customer — 23 orders, 2% refund rate</p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-400">Refund Request:</p>
            <p className="text-white mt-1">"My Cotton Kurta arrived with a tear on the sleeve"</p>
            <p className="text-gray-500 text-xs mt-1">Order: ORD-1001 · ₹800 · Fashion</p>
          </div>
          <div className="p-6 rounded-xl bg-green-500/5 border border-gray-700 flex flex-col items-center">
            <span className="text-gray-500 text-sm">Side-by-side demo will be activated in Phase 5</span>
            <span className="text-6xl mt-4">⚡</span>
          </div>
        </div>

        {/* Rohit's Side */}
        <div className="bg-gray-900 rounded-2xl p-6 border-2 border-red-500/30">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-3xl">🔴</span>
            <div>
              <h2 className="text-xl font-bold text-white">Rohit Mehta</h2>
              <p className="text-red-400 text-sm">Serial Abuser — 12 orders, 67% refund rate</p>
            </div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 mb-4">
            <p className="text-sm text-gray-400">Refund Request:</p>
            <p className="text-white mt-1">"Shoes were damaged in transit, I want a full refund"</p>
            <p className="text-gray-500 text-xs mt-1">Order: ORD-2001 · ₹2,400 · Fashion</p>
          </div>
          <div className="p-6 rounded-xl bg-red-500/5 border border-gray-700 flex flex-col items-center">
            <span className="text-gray-500 text-sm">Side-by-side demo will be activated in Phase 5</span>
            <span className="text-6xl mt-4">🚩</span>
          </div>
        </div>
      </div>

      <div className="mt-8 text-center">
        <p className="text-gray-500 text-sm">
          Demo mode with animated reasoning chains, live risk scoring, and simultaneous decisions coming in Phase 5
        </p>
      </div>
    </div>
  );
}
