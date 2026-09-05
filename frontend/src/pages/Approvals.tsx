import { useEffect, useState } from 'react'
import { getIncidents, approveIncident, rejectIncident } from '@/lib/api'
import { formatINR, timeAgo, severityColor, policyColor, cn } from '@/lib/utils'
import { Shield, CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react'

interface Incident {
  id: string; type: string; severity: string; status: string
  customer_name: string | null; amount_at_risk: number
  root_cause: string; confidence_score: number
  recommended_action: string; expected_recovery: number
  risk_level: string; policy_result: string
  requires_approval: boolean; ai_explanation: string
  evidence: string[]; created_at: string
}

export default function Approvals() {
  const [incidents, setIncidents] = useState<Incident[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [acting, setActing] = useState<string | null>(null)

  const load = () => {
    setLoading(true)
    getIncidents({ status: 'action_required' })
      .then(r => setIncidents(r.data.incidents.filter((i: Incident) => i.requires_approval)))
      .finally(() => setLoading(false))
  }

  useEffect(() => { load() }, [])

  const handleApprove = async (id: string) => {
    setActing(id)
    await approveIncident(id)
    setActing(null)
    load()
  }
  const handleReject = async (id: string) => {
    setActing(id)
    await rejectIncident(id)
    setActing(null)
    load()
  }

  return (
    <div className="space-y-4">
      {/* Header info */}
      <div className="card px-5 py-4 flex items-center gap-3">
        <Shield className="w-5 h-5 text-yellow-500" />
        <div>
          <div className="font-semibold text-gray-900">Actions Requiring Human Approval</div>
          <div className="text-xs text-gray-500 mt-0.5">
            Policy Engine has flagged these actions as REVIEW — AI cannot auto-execute them.
          </div>
        </div>
        <div className="ml-auto text-2xl font-bold text-gray-900">{incidents.length}</div>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-400 animate-pulse">Loading approvals…</div>
      ) : incidents.length === 0 ? (
        <div className="card text-center py-16 text-gray-400">
          <Shield className="w-10 h-10 mx-auto mb-3 opacity-30" />
          <div className="font-medium">No pending approvals</div>
          <div className="text-sm mt-1">All actionable incidents have been resolved or are being handled automatically.</div>
        </div>
      ) : (
        <div className="space-y-3">
          {incidents.map(inc => {
            const isExp = expandedId === inc.id
            const isAct = acting === inc.id
            const typeLabel = inc.type.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())

            return (
              <div key={inc.id} className="card overflow-hidden border-l-4 border-l-yellow-400">
                <div className="px-5 py-4 flex items-start gap-4">
                  <div className={cn('px-2.5 py-1 rounded-lg text-xs font-semibold border capitalize flex-shrink-0', severityColor(inc.severity))}>
                    {inc.severity}
                  </div>
                  <div className="flex-1">
                    <div className="font-semibold text-gray-900">{typeLabel}</div>
                    <div className="text-sm text-gray-500 mt-0.5">{inc.root_cause}</div>
                    <div className="flex items-center gap-3 mt-2 text-xs text-gray-500">
                      {inc.customer_name && <span>Customer: {inc.customer_name}</span>}
                      <span>Confidence: <strong className="text-gray-700">{Math.round(inc.confidence_score * 100)}%</strong></span>
                      <span className={cn('px-2 py-0.5 rounded-full font-semibold', policyColor('REVIEW'))}>REVIEW</span>
                    </div>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <div className="text-xl font-bold text-gray-900">{formatINR(inc.amount_at_risk)}</div>
                    <div className="text-xs text-green-600 mt-0.5">Recovery: {formatINR(inc.expected_recovery)}</div>
                    <div className="text-xs text-gray-400 mt-0.5">{timeAgo(inc.created_at)}</div>
                  </div>
                </div>

                {/* Action strip */}
                <div className="px-5 pb-4 flex items-center gap-3">
                  <div className="flex-1 bg-yellow-50 border border-yellow-200 rounded-lg px-3 py-2 text-sm text-yellow-800">
                    <strong>AI recommends:</strong> {inc.recommended_action}
                  </div>
                  <button
                    onClick={() => setExpandedId(isExp ? null : inc.id)}
                    className="flex items-center gap-1 text-xs text-gray-500 hover:text-gray-700"
                  >
                    {isExp ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
                    Evidence
                  </button>
                  <button
                    disabled={isAct}
                    onClick={() => handleApprove(inc.id)}
                    className="flex items-center gap-1.5 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    <CheckCircle className="w-3.5 h-3.5" /> Approve
                  </button>
                  <button
                    disabled={isAct}
                    onClick={() => handleReject(inc.id)}
                    className="flex items-center gap-1.5 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    <XCircle className="w-3.5 h-3.5" /> Reject
                  </button>
                </div>

                {isExp && (
                  <div className="border-t border-gray-100 px-5 py-4 bg-gray-50 space-y-3">
                    <div>
                      <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">AI Explanation</div>
                      <p className="text-sm text-gray-700">{inc.ai_explanation}</p>
                    </div>
                    {inc.evidence && inc.evidence.length > 0 && (
                      <div>
                        <div className="text-xs font-semibold text-gray-400 uppercase tracking-wide mb-1.5">Evidence</div>
                        <ul className="space-y-1">
                          {inc.evidence.map((e, i) => (
                            <li key={i} className="text-sm text-gray-700 flex gap-2">
                              <span className="text-brand-400">•</span>{e}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
