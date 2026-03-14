import { useEffect, useState } from 'react';
import { getAuditLog } from '../utils/api';

export default function AuditLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    try {
      const res = await getAuditLog(30);
      setLogs(res.data || []);
    } catch {
      // silently ignore
    }
  };

  return (
    <div className="bg-gray-900 rounded-2xl p-6 border border-gray-800">
      <h2 className="text-lg font-semibold text-white mb-4">📋 Audit Trail</h2>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-gray-500 text-xs border-b border-gray-800">
              <th className="text-left p-2">Refund ID</th>
              <th className="text-left p-2">Event</th>
              <th className="text-left p-2">Time</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id} className="border-b border-gray-800/50 hover:bg-gray-800/20">
                <td className="p-2 font-mono text-gray-400 text-xs">{log.refund_id}</td>
                <td className="p-2">
                  <span className={`px-2 py-0.5 rounded text-xs ${
                    log.event_type?.includes('escalate') ? 'bg-red-500/10 text-red-400' :
                    log.event_type?.includes('approve') ? 'bg-green-500/10 text-green-400' :
                    log.event_type?.includes('evidence') ? 'bg-blue-500/10 text-blue-400' :
                    'bg-gray-700 text-gray-400'
                  }`}>
                    {log.event_type}
                  </span>
                </td>
                <td className="p-2 text-gray-500 text-xs">{log.created_at}</td>
              </tr>
            ))}
          </tbody>
        </table>
        {logs.length === 0 && (
          <p className="text-gray-500 text-sm text-center py-4">No audit logs yet</p>
        )}
      </div>
    </div>
  );
}
