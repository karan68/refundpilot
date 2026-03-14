import { useEffect, useState } from 'react';
import { getAuditLog } from '../utils/api';

const EVENT_STYLES = {
  escalate: 'bg-rose-400',
  approve: 'bg-emerald-400',
  evidence: 'bg-sky-400',
};

const formatEventLabel = (value = '') =>
  value
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (letter) => letter.toUpperCase());

const formatTimestamp = (value) => {
  if (!value) {
    return 'Just now';
  }

  const parsed = new Date(String(value).replace(' ', 'T'));
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }

  return parsed.toLocaleString('en-IN', {
    day: 'numeric',
    month: 'short',
    hour: 'numeric',
    minute: '2-digit',
  });
};

export default function AuditLog() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    const loadLogs = async () => {
      try {
        const res = await getAuditLog(30);
        setLogs(res.data || []);
      } catch {
        // silently ignore
      }
    };

    loadLogs();
  }, []);

  return (
    <div className="glass-panel p-7 xl:p-8">
      <h2 className="section-title">Decision audit trail</h2>
      <p className="section-copy mt-2">A readable event stream for what the agent did, when it did it, and which claim it affected.</p>

      <div className="mt-6 space-y-4">
        {logs.slice(0, 10).map((log) => {
          const tone =
            log.event_type?.includes('escalate')
              ? EVENT_STYLES.escalate
              : log.event_type?.includes('approve')
                ? EVENT_STYLES.approve
                : log.event_type?.includes('evidence')
                  ? EVENT_STYLES.evidence
                  : 'bg-slate-500';

          return (
            <div key={log.id} className="flex gap-4">
              <div className="flex flex-col items-center">
                <span className={`mt-2 h-3 w-3 rounded-full ${tone}`} />
                <span className="mt-2 h-full w-px bg-slate-800" />
              </div>

              <div className="flex-1 rounded-3xl border border-slate-800 bg-slate-950/45 p-4">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <p className="text-base font-medium text-white">{formatEventLabel(log.event_type)}</p>
                    <p className="mt-1 text-sm text-slate-400">Refund {log.refund_id}</p>
                  </div>
                  <span className="rounded-full border border-slate-700/80 bg-slate-900/80 px-3 py-1 text-xs text-slate-400">
                    {formatTimestamp(log.created_at)}
                  </span>
                </div>
              </div>
            </div>
          );
        })}

        {logs.length === 0 && (
          <p className="py-4 text-center text-sm text-slate-500">No audit logs yet</p>
        )}
      </div>
    </div>
  );
}
