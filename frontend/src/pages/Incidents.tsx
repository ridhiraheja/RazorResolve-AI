import { useEffect, useState } from 'react'
import { getIncidents, approveIncident, rejectIncident } from '@/lib/api'
import { formatINR, timeAgo, severityColor, statusColor, policyColor, cn } from '@/lib/utils'
import { AlertTriangle, CheckCircle, XCircle, ChevronDown, ChevronUp, Shield } from 'lucide-react'

interface Incident {
  id: string
  type: string
  severity: string
  status: string
  customer_name: string | null
  amount_at_risk: number
  root_cause: string
  confidence_score: number
  recommended_action: string
  expected_recovery: number
  risk_level: string
  policy_result: string
  auto_executable: boolean
  requires_approval: boolean
  ai_explanation: string
  evidence: string[]
  created_at: string
  recovered_amount: number
}

function IncidentCard({ inc, onApprove, onReject }: {
  inc: Incident
  onApprove: (id: string) => void
  onReject: (id: string) => void
}) {
  const [expanded, setExpanded] = useState(false)
  const [acting, setActing] = useState(false)

  const handleApprove = async () => {
    setActing(true)
    await onApprove(inc.id)
    setActing(false)
  }
  const handleReject = async () => {
    setActing(true)
    await onReject(inc.id)
    setActing(false)
  }

  const typeLabel = inc.type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

  return (
    <div className="card overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 flex items-start gap-4">
        <div className={cn('px-2.5 py-1 rounded-lg text-xs font-semibold border capitalize', severityColor(inc.severity))}>
          {inc.severity}
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="font-semibold text-gray-900">{typeLabel}</span>
            <span className={cn('text-xs px-2 py-0.5 rounded-full font-medium', statusColor(inc.status))}>
              {inc.status.replace(/_/g, ' ').toUpperCase()}
            </span>
            {inc.requires_approval && (
              <span className="text-xs px-2 py-0.5 rounded-full bg-orange-100 text-orange-700 font-medium">
                APPROVAL REQUIRED
              </span>
            )}
          </div>
          <div className="text-sm text-gray-500 mt-0.5 truncate">{inc.root_cause}</div>
        </div>

        <div className="text-right flex-shrink-0">
          <div className="font-bold text-gray-900">{formatINR(inc.amount_at_risk)}</div>
          <div className="text-xs text-gray-500">{timeAgo(inc.created_at)}</div>
        </div>
      </div>

      {/* Sub-row */}
      <div className="px-5 pb-3 flex items-center gap-4 text-sm flex-wrap">
        {inc.customer_name && (
          <span className="text-gray-600">
            <span className="text-gray-400">Customer: </span>{inc.customer_name}
          </span>
        )}
        <span className="text-gray-600">
          <span className="text-gray-400">AI Confidence: </span>
          <span className="font-medium">{Math.round(inc.confidence_score * 100)}%</span>
        </span>
        <span className={cn('text-xs px-2 py-0.5 rounded-full font-semibold', policyColor(inc.policy_result))}>
          Policy: {inc.policy_result}
        </span>
        <button
          onClick={() => setExpanded(e => !e)}
          className="ml-auto flex items-center gap-1 text-xs text-brand-600 hover:text-brand-700"
        >
          {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
          {expanded ? 'Less' : 'Details'}
        </button>
      </div>

      {/* Expanded */}
      {expanded && (
        <div className="border-t border-gray-100 px-5 py-4 bg-gray-50 space-y-4">
          {/* AI Explanation */}
          <div>
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">AI Explanation</div>
            <p className="text-sm text-gray-700 leading-relaxed">{inc.ai_explanation}</p>
          </div>

          {/* Evidence */}
          {inc.evidence && inc.evidence.length > 0 && (
            <div>
              <div className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-1.5">Evidence</div>
              <ul className="space-y-1">
                {inc.evidence.map((e, i) => (
                  <li key={i} className="text-sm text-gray-700 flex items-start gap-2">
                    <span className="text-brand-500 mt-0.5">•</span>
                    {e}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Decision pathway */}
          <div className="grid grid-cols-3 gap-3">
            <div className="bg-white rounded-lg border border-gray-200 p-3">
              <div className="text-xs text-gray-400 mb-1">Recommended Action</div>
              <div className="text-sm font-medium text-gray-800">{inc.recommended_action}</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3">
              <div className="text-xs text-gray-400 mb-1">Expected Recovery</div>
              <div className="text-sm font-bold text-green-700">{formatINR(inc.expected_recovery)}</div>
            </div>
            <div className="bg-white rounded-lg border border-gray-200 p-3">
              <div className="text-xs text-gray-400 mb-1">Risk Level</div>
              <div className={cn('text-sm font-semibold capitalize', inc.risk_level === 'high' ? 'text-red-600' : inc.risk_level === 'medium' ? 'text-yellow-600' : 'text-green-600')}>
                {inc.risk_level}
              </div>
            </div>
          </div>

          {/* Actions */}
          {inc.requires_approval && inc.status !== 'resolved' && inc.status !== 'escalated' && (
            <div className="flex items-center gap-3 pt-1">
              <Shield className="w-4 h-4 text-yellow-500" />
              <span className="text-sm text-gray-600">Policy requires human approval before execution.</span>
              <button
                disabled={acting}
                onClick={handleApprove}
                className="ml-auto flex items-center gap-1.5 px-4 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                <CheckCircle className="w-3.5 h-3.5" /> Approve
              </button>
              <button
                disabled={acting}
                onClick={handleReject}
                className="flex items-center gap-1.5 px-4 py-1.5 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
              >
                <XCircle className="w-3.5 h-3.5" /> Reject
              </button>
            </div>
          )}

          {inc.status === 'resolved' && (
            <div className="flex items-center gap-2 text-green-700 text-sm">
              <CheckCircle className="w-4 h-4" />
              Resolved — recovered {formatINR(inc.recovered_amount)}
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const STATUS_FILTERS = ['all', 'new', 'investigating', 'action_required', 'recovering', 'resolved', 'escalated']
const SEV_FILTERS = ['all', 'critical', 'high', 'medium', 'low']

export default function Incidents() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('all')
  const [sevFilter, setSevFilter] = useState('all')

  const load = () => {
    setLoading(true)
    const params: Record<string, string> = {}
    if (statusFilter !== 'all') params.status = statusFilter
    if (sevFilter !== 'all') params.severity = sevFilter
    getIncidents(params)
      .then(r => setIncidents(r.data.incidents))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [statusFilter, sevFilter])

  const handleApprove = async (id: string) => {
    await approveIncident(id)
    load()
  }
  const handleReject = async (id: string) => {
    await rejectIncident(id)
    load()
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="card px-4 py-3 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <AlertTriangle className="w-4 h-4" />
          <span className="font-medium">{incidents.length} incidents</span>
        </div>
        <div className="flex items-center gap-2 ml-auto flex-wrap">
          <span className="text-xs text-gray-500">Status:</span>
          {STATUS_FILTERS.map(f => (
            <button
              key={f}
              onClick={() => setStatusFilter(f)}
              className={cn('px-3 py-1 rounded-full text-xs font-medium transition-colors', statusFilter === f ? 'bg-brand-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')}
            >
              {f === 'all' ? 'All' : f.replace(/_/g, ' ')}
            </button>
          ))}
          <span className="text-xs text-gray-500 ml-2">Severity:</span>
          {SEV_FILTERS.map(f => (
            <button
              key={f}
              onClick={() => setSevFilter(f)}
              className={cn('px-3 py-1 rounded-full text-xs font-medium transition-colors', sevFilter === f ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400 animate-pulse">Loading incidents…</div>
      ) : incidents.length === 0 ? (
        <div className="text-center py-12 text-gray-400">No incidents match the selected filters.</div>
      ) : (
        <div className="space-y-3">
          {incidents.map(inc => (
            <IncidentCard key={inc.id} inc={inc} onApprove={handleApprove} onReject={handleReject} />
          ))}
        </div>
      )}
    </div>
  )
}
