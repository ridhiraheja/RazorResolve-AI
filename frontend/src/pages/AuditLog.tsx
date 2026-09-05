import { useEffect, useState } from 'react'
import { getAuditLogs } from '@/lib/api'
import { timeAgo, policyColor, cn } from '@/lib/utils'
import { FileText } from 'lucide-react'

interface LogEntry {
  id: string; timestamp: string; agent: string; incident_id: string | null
  observation: string; decision: string; action: string
  policy_result: string; result: string; confidence: number
}

const RESULT_COLOR: Record<string, string> = {
  'Success':  'text-green-600 bg-green-50',
  'Pending':  'text-yellow-600 bg-yellow-50',
  'Failed':   'text-red-600 bg-red-50',
  'Escalated':'text-orange-600 bg-orange-50',
}

export default function AuditLog() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getAuditLogs({ limit: '100' })
      .then(r => setLogs(r.data.logs))
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-4">
      <div className="card px-5 py-3 flex items-center gap-2">
        <FileText className="w-4 h-4 text-gray-400" />
        <span className="font-medium text-gray-800">{logs.length} audit entries</span>
        <span className="text-xs text-gray-400 ml-2">Complete AI decision trail</span>
      </div>

      <div className="card overflow-hidden">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              {['Time', 'Agent', 'Observation', 'Decision', 'Action', 'Policy', 'Result', 'Confidence'].map(h => (
                <th key={h} className="text-left px-4 py-3 font-semibold text-gray-500 uppercase tracking-wide text-xs">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="text-center py-12 text-gray-400 animate-pulse">Loading audit logs…</td></tr>
            ) : logs.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-12 text-gray-400">No logs found.</td></tr>
            ) : (
              logs.map(l => (
                <tr key={l.id} className="border-b border-gray-50 hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-2.5 text-gray-500 whitespace-nowrap">{timeAgo(l.timestamp)}</td>
                  <td className="px-4 py-2.5 text-gray-700 font-medium max-w-24 truncate">{l.agent.replace('Agent', '').replace('Manager', '')}</td>
                  <td className="px-4 py-2.5 text-gray-600 max-w-40 truncate" title={l.observation}>{l.observation}</td>
                  <td className="px-4 py-2.5 text-gray-700 max-w-32 truncate" title={l.decision}>{l.decision}</td>
                  <td className="px-4 py-2.5 text-gray-600 max-w-40 truncate" title={l.action}>{l.action}</td>
                  <td className="px-4 py-2.5">
                    <span className={cn('px-1.5 py-0.5 rounded text-xs font-semibold', policyColor(l.policy_result))}>
                      {l.policy_result}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <span className={cn('px-1.5 py-0.5 rounded text-xs font-medium', RESULT_COLOR[l.result] || 'text-gray-600 bg-gray-50')}>
                      {l.result}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-gray-700 font-medium">{Math.round(l.confidence * 100)}%</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
