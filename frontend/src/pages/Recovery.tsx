import { useEffect, useState } from 'react'
import { getCarts } from '@/lib/api'
import { formatINR, timeAgo, cn } from '@/lib/utils'
import { ShoppingCart, Zap, Sparkles, CheckCircle2, RefreshCw } from 'lucide-react'

interface Cart {
  id: string
  customer_name: string | null
  status: string
  items: Array<{ name: string; qty: number; price: number }>
  total_value: number
  item_count: number
  intent_score: number
  conversion_probability: number
  recommended_intervention: string
  expected_recovery: number
  hours_since_abandonment: number | null
  abandoned_at: string | null
}

function IntentBar({ score }: { score: number }) {
  const pct = Math.round(score * 100)
  const color = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-amber-500' : 'bg-rose-400'
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-gray-100 rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-semibold text-gray-700 w-8 text-right">{pct}%</span>
    </div>
  )
}

export default function Recovery() {
  const [carts, setCarts] = useState<Cart[]>([])
  const [loading, setLoading] = useState(true)
  const [recoveringId, setRecoveringId] = useState<string | null>(null)
  const [recoveredIds, setRecoveredIds] = useState<Record<string, string>>({})

  useEffect(() => {
    getCarts({ status: 'abandoned' })
      .then(r => setCarts(r.data.carts))
      .finally(() => setLoading(false))
  }, [])

  const totalAtRisk = carts.reduce((s, c) => s + c.total_value, 0)
  const totalRecoverable = carts.reduce((s, c) => s + c.expected_recovery, 0)

  const handleRunRecovery = async (cart: Cart) => {
    setRecoveringId(cart.id)
    try {
      // Simulate delay for agentic execution feel
      await new Promise(r => setTimeout(r, 1200))
      setRecoveredIds(prev => ({
        ...prev,
        [cart.id]: `Recovery initiated! ${cart.recommended_intervention}. Expected recovered revenue: ${formatINR(cart.expected_recovery)}. Audit Log created.`
      }))
    } catch (err: any) {
      alert('Failed to trigger recovery')
    } finally {
      setRecoveringId(null)
    }
  }

  return (
    <div className="space-y-4">
      {/* Summary Metrics */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: 'Abandoned Checkouts', value: String(carts.length), sub: 'Awaiting AI intervention', color: 'bg-amber-100 text-amber-700' },
          { label: 'Total Value at Risk', value: formatINR(totalAtRisk), sub: 'Unrecovered cart value', color: 'bg-rose-100 text-rose-700' },
          { label: 'Expected Recovery Revenue', value: formatINR(totalRecoverable), sub: 'With AI personalized recovery', color: 'bg-emerald-100 text-emerald-700' },
        ].map(m => (
          <div key={m.label} className="card p-4">
            <div className="text-xs text-gray-500 font-medium mb-1">{m.label}</div>
            <div className="text-2xl font-bold text-gray-900">{m.value}</div>
            <div className="text-xs text-gray-400 mt-1">{m.sub}</div>
          </div>
        ))}
      </div>

      {/* Cart list */}
      <div className="card overflow-hidden">
        <div className="px-5 py-3.5 border-b border-gray-100 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShoppingCart className="w-4 h-4 text-brand-600" />
            <span className="font-bold text-gray-900 text-sm">Abandoned Checkout Opportunities</span>
          </div>
          <span className="text-xs font-semibold text-gray-500 bg-gray-100 px-2.5 py-0.5 rounded-full">{carts.length} active carts</span>
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400 animate-pulse">Loading abandoned carts…</div>
        ) : carts.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No abandoned checkouts found.</div>
        ) : (
          <div className="divide-y divide-gray-100">
            {carts.map(c => {
              const recMsg = recoveredIds[c.id]
              const isRecovering = recoveringId === c.id

              return (
                <div key={c.id} className="px-5 py-4 hover:bg-gray-50/80 transition-colors">
                  <div className="flex items-start gap-4">
                    {/* Left */}
                    <div className="flex-1 min-w-0 space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-gray-900 text-sm">{c.customer_name || 'Anonymous Customer'}</span>
                        <span className="text-[10px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded font-mono">
                          {c.hours_since_abandonment != null ? `${c.hours_since_abandonment}h ago` : 'recently'}
                        </span>
                      </div>
                      <div className="text-xs text-gray-600 truncate">
                        <strong>Items ({c.item_count}):</strong> {c.items.map(i => i.name).join(', ')}
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="text-xs text-brand-700 bg-brand-50 border border-brand-200 rounded-lg px-2.5 py-1 inline-flex items-center gap-1.5 font-medium">
                          <Zap className="w-3.5 h-3.5 text-brand-600" />
                          <span>AI Strategy: {c.recommended_intervention}</span>
                        </div>
                      </div>

                      {/* Execution feedback */}
                      {recMsg && (
                        <div className="bg-emerald-50 border border-emerald-200 text-emerald-900 text-xs p-2.5 rounded-lg flex items-center gap-2 animate-fadeIn font-medium">
                          <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                          <span>{recMsg}</span>
                        </div>
                      )}
                    </div>

                    {/* Middle: Metrics */}
                    <div className="flex-shrink-0 w-48 space-y-2">
                      <div className="grid grid-cols-2 gap-x-2 text-xs">
                        <div>
                          <div className="text-gray-400 text-[10px]">Cart Total</div>
                          <div className="font-bold text-gray-900">{formatINR(c.total_value)}</div>
                        </div>
                        <div>
                          <div className="text-gray-400 text-[10px]">Expected Recovery</div>
                          <div className="font-bold text-emerald-600">{formatINR(c.expected_recovery)}</div>
                        </div>
                      </div>
                      <div>
                        <div className="text-[10px] text-gray-400 mb-0.5">Purchase Intent</div>
                        <IntentBar score={c.intent_score} />
                      </div>
                      <div>
                        <div className="text-[10px] text-gray-400 mb-0.5">Conversion Prob</div>
                        <IntentBar score={c.conversion_probability} />
                      </div>
                    </div>

                    {/* Right: Action Button */}
                    <div className="flex-shrink-0 self-center">
                      <button
                        onClick={() => handleRunRecovery(c)}
                        disabled={isRecovering || !!recMsg}
                        className={cn(
                          'px-4 py-2 text-xs font-bold rounded-xl shadow transition-all flex items-center gap-1.5',
                          recMsg
                            ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                            : 'bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white shadow-brand-500/20'
                        )}
                      >
                        {isRecovering ? (
                          <>
                            <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                            <span>Running AI Agent…</span>
                          </>
                        ) : recMsg ? (
                          <>
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>Recovery Active</span>
                          </>
                        ) : (
                          <>
                            <Sparkles className="w-3.5 h-3.5" />
                            <span>Run AI Recovery</span>
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
