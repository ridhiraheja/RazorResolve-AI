import { useEffect, useState } from 'react'
import { getPayments } from '@/lib/api'
import api from '@/lib/api'
import { formatINR, timeAgo, paymentStatusColor, cn } from '@/lib/utils'
import { CreditCard, ChevronDown, ChevronUp, Bot, RefreshCw, CheckCircle2, AlertTriangle, ShieldCheck } from 'lucide-react'

interface Payment {
  id: string
  order_id: string
  customer_name: string | null
  amount: number
  method: string
  status: string
  failure_reason: string | null
  failure_message: string | null
  attempt_count: number
  is_webhook_delivered: boolean
  created_at: string
  captured_at: string | null
  failed_at: string | null
}

interface PaymentTimelineData {
  payment: any
  order: any
  customer: any
  incident: any
  ai_diagnosis: any
  timeline: Array<{ time: string; event: string; label: string; detail: string; status: string }>
  audit_logs: Array<any>
}

const STATUS_FILTERS = ['all', 'captured', 'failed', 'authorized', 'timeout', 'refunded']

export default function Payments() {
  const [payments, setPayments] = useState<Payment[]>([])
  const [loading, setLoading] = useState(true)
  const [statusFilter, setStatusFilter] = useState('all')
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [timelineData, setTimelineData] = useState<Record<string, PaymentTimelineData>>({})
  const [fetchingTimeline, setFetchingTimeline] = useState<string | null>(null)
  const [replayingId, setReplayingId] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    const params: Record<string, string> = {}
    if (statusFilter !== 'all') params.status = statusFilter
    getPayments(params)
      .then(r => setPayments(r.data.payments))
      .finally(() => setLoading(false))
  }, [statusFilter])

  const toggleExpand = async (id: string) => {
    if (expandedId === id) {
      setExpandedId(null)
      return
    }
    setExpandedId(id)
    if (!timelineData[id]) {
      setFetchingTimeline(id)
      try {
        const res = await api.get(`/payments/${id}/timeline`)
        setTimelineData(prev => ({ ...prev, [id]: res.data }))
      } catch (err) {
        console.error(err)
      } finally {
        setFetchingTimeline(null)
      }
    }
  }

  const handleReplayWebhook = async (paymentId: string) => {
    setReplayingId(paymentId)
    try {
      await api.post(`/webhooks/${paymentId}/replay`)
      // Refresh timeline
      const res = await api.get(`/payments/${paymentId}/timeline`)
      setTimelineData(prev => ({ ...prev, [paymentId]: res.data }))
      // Refresh list
      const r = await getPayments(statusFilter !== 'all' ? { status: statusFilter } : {})
      setPayments(r.data.payments)
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to replay webhook')
    } finally {
      setReplayingId(null)
    }
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="card px-4 py-3 flex items-center gap-4 flex-wrap">
        <div className="flex items-center gap-2 text-sm text-gray-600">
          <CreditCard className="w-4 h-4 text-brand-600" />
          <span className="font-semibold">{payments.length} Payments Recorded</span>
        </div>
        <div className="flex items-center gap-2 ml-auto flex-wrap">
          {STATUS_FILTERS.map(f => (
            <button
              key={f}
              onClick={() => setStatusFilter(f)}
              className={cn('px-3 py-1 rounded-full text-xs font-medium transition-colors', statusFilter === f ? 'bg-brand-600 text-white shadow-sm' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="card overflow-hidden">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-gray-100 bg-gray-50">
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Payment ID</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Customer</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Amount</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Method</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Status</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Webhook</th>
              <th className="text-left px-4 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Time</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan={8} className="text-center py-12 text-gray-400 animate-pulse">Loading payments…</td></tr>
            ) : payments.length === 0 ? (
              <tr><td colSpan={8} className="text-center py-12 text-gray-400">No payments found.</td></tr>
            ) : (
              payments.map(p => {
                const tData = timelineData[p.id]
                const isExp = expandedId === p.id

                return (
                  <tbody key={p.id}>
                    <tr
                      className="border-b border-gray-50 hover:bg-gray-50 cursor-pointer transition-colors"
                      onClick={() => toggleExpand(p.id)}
                    >
                      <td className="px-4 py-3 font-mono text-xs font-semibold text-brand-700">{p.id.slice(0, 12)}…</td>
                      <td className="px-4 py-3 text-gray-800 font-medium">{p.customer_name || 'Demo Customer'}</td>
                      <td className="px-4 py-3 font-bold text-gray-900">{formatINR(p.amount)}</td>
                      <td className="px-4 py-3 text-gray-600 uppercase text-xs font-semibold">{p.method}</td>
                      <td className="px-4 py-3">
                        <span className={cn('px-2.5 py-0.5 rounded-full text-xs font-semibold', paymentStatusColor(p.status))}>
                          {p.status}
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        {p.is_webhook_delivered ? (
                          <span className="text-xs text-emerald-600 font-semibold flex items-center gap-1">
                            <CheckCircle2 className="w-3.5 h-3.5" /> Delivered
                          </span>
                        ) : (
                          <span className="text-xs text-rose-600 font-semibold flex items-center gap-1">
                            <AlertTriangle className="w-3.5 h-3.5" /> Failed
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-gray-500 text-xs">{timeAgo(p.created_at)}</td>
                      <td className="px-4 py-3 text-right">
                        {isExp ? <ChevronUp className="w-4 h-4 text-gray-400 inline" /> : <ChevronDown className="w-4 h-4 text-gray-400 inline" />}
                      </td>
                    </tr>

                    {/* EXPANDED DETAILS & TIMELINE PANEL */}
                    {isExp && (
                      <tr className="bg-slate-50 border-b border-gray-200">
                        <td colSpan={8} className="p-5">
                          {fetchingTimeline === p.id ? (
                            <div className="text-center py-6 text-xs text-gray-500 animate-pulse flex items-center justify-center gap-2">
                              <RefreshCw className="w-4 h-4 animate-spin text-brand-600" />
                              <span>Loading AI Diagnosis & Payment Timeline…</span>
                            </div>
                          ) : tData ? (
                            <div className="space-y-4">
                              {/* Metadata header */}
                              <div className="grid grid-cols-4 gap-3 bg-white p-3.5 rounded-xl border border-gray-200 text-xs">
                                <div>
                                  <span className="text-gray-400 block mb-0.5">Order ID</span>
                                  <span className="font-mono font-bold text-gray-800">{tData.payment.order_id}</span>
                                </div>
                                <div>
                                  <span className="text-gray-400 block mb-0.5">Payment Gateway ID</span>
                                  <span className="font-mono font-semibold text-gray-700">rzp_sim_{p.id.slice(0, 8)}</span>
                                </div>
                                <div>
                                  <span className="text-gray-400 block mb-0.5">Attempts Count</span>
                                  <span className="font-bold text-gray-900">{tData.payment.attempt_count}</span>
                                </div>
                                <div>
                                  <span className="text-gray-400 block mb-0.5">Failure Reason</span>
                                  <span className="font-bold text-rose-700 capitalize">
                                    {tData.payment.failure_reason?.replace(/_/g, ' ') || 'None (Captured)'}
                                  </span>
                                </div>
                              </div>

                              {/* AI Diagnosis block */}
                              {tData.ai_diagnosis && (
                                <div className="bg-gradient-to-r from-brand-900 to-slate-900 text-white p-4 rounded-xl space-y-2 shadow-md">
                                  <div className="flex items-center justify-between text-xs">
                                    <div className="flex items-center gap-2 font-bold text-brand-300">
                                      <Bot className="w-4 h-4 text-brand-400" />
                                      AI PAYMENT DIAGNOSIS & RECOVERY RECOMMENDATION
                                    </div>
                                    <div className="bg-brand-500/20 text-brand-200 border border-brand-400/30 px-2 py-0.5 rounded text-[10px] font-bold">
                                      Confidence: {Math.round(tData.ai_diagnosis.confidence_score * 100)}%
                                    </div>
                                  </div>
                                  <p className="text-sm font-semibold text-gray-100">{tData.ai_diagnosis.root_cause}</p>
                                  <div className="text-xs text-gray-300">
                                    <strong>Recommended Action:</strong> {tData.ai_diagnosis.recommended_action} |{' '}
                                    <strong>Policy Verdict:</strong>{' '}
                                    <span className="text-emerald-400 font-bold">{tData.ai_diagnosis.policy_result}</span>
                                  </div>
                                </div>
                              )}

                              {/* Webhook Replay Action if failed */}
                              {!p.is_webhook_delivered && (
                                <div className="bg-amber-50 border border-amber-200 p-3 rounded-xl flex items-center justify-between text-xs">
                                  <div className="flex items-center gap-2 text-amber-900 font-medium">
                                    <AlertTriangle className="w-4 h-4 text-amber-600" />
                                    <span>Payment captured, but webhook delivery failed. Order status is out of sync.</span>
                                  </div>
                                  <button
                                    onClick={(e) => {
                                      e.stopPropagation()
                                      handleReplayWebhook(p.id)
                                    }}
                                    disabled={replayingId === p.id}
                                    className="px-3 py-1.5 bg-amber-600 hover:bg-amber-700 text-white font-bold rounded-lg shadow text-xs flex items-center gap-1.5 transition-colors disabled:opacity-50"
                                  >
                                    {replayingId === p.id ? (
                                      <>
                                        <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                        <span>Replaying…</span>
                                      </>
                                    ) : (
                                      <>
                                        <RefreshCw className="w-3.5 h-3.5" />
                                        <span>Replay Webhook Now</span>
                                      </>
                                    )}
                                  </button>
                                </div>
                              )}

                              {/* Event Timeline */}
                              <div className="bg-white p-4 rounded-xl border border-gray-200 space-y-2">
                                <h4 className="text-xs font-bold text-gray-800 uppercase tracking-wider mb-2">Payment Event Timeline</h4>
                                <div className="space-y-2">
                                  {tData.timeline.map((item, idx) => (
                                    <div key={idx} className="flex items-center justify-between text-xs py-1 border-b border-gray-50 last:border-0">
                                      <div className="flex items-center gap-2">
                                        <div className={cn(
                                          'w-2 h-2 rounded-full',
                                          item.status === 'success' ? 'bg-emerald-500' :
                                          item.status === 'error' ? 'bg-rose-500' :
                                          item.status === 'ai' ? 'bg-brand-500' : 'bg-gray-400'
                                        )} />
                                        <span className="font-semibold text-gray-800">{item.label}</span>
                                        <span className="text-gray-400 text-[11px]">{item.detail}</span>
                                      </div>
                                      <span className="text-gray-400 text-[10px]">{item.time ? new Date(item.time).toLocaleTimeString() : ''}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            </div>
                          ) : (
                            <div className="text-xs text-gray-500">Failed to load payment timeline.</div>
                          )}
                        </td>
                      </tr>
                    )}
                  </tbody>
                )
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
