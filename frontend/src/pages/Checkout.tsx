import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  ShieldCheck, CreditCard, Smartphone, Building2, CheckCircle2,
  AlertTriangle, ArrowRight, RefreshCw, Lock, Sparkles, User, ShoppingBag, Eye, Brain, HelpCircle, CheckCircle, Scale, Play, Check, Plus, Minus, Trash2
} from 'lucide-react'
import { useCartStore } from '@/store/useCartStore'
import { formatINR, cn } from '@/lib/utils'
import api from '@/lib/api'

type Scenario = 'SUCCESS' | 'TEMPORARY_FAILURE' | 'TIMEOUT' | 'INSUFFICIENT_FUNDS' | 'WEBHOOK_FAILURE' | 'DUPLICATE_PAYMENT'

interface ScenarioOption {
  id: Scenario
  label: string
  desc: string
  badgeColor: string
}

const SCENARIOS: ScenarioOption[] = [
  { id: 'SUCCESS', label: '1. Success', desc: 'Normal successful checkout', badgeColor: 'bg-green-100 text-green-700 border-green-200' },
  { id: 'TEMPORARY_FAILURE', label: '2. Temp Gateway Error', desc: '503 Outage → AI Retry Recovery', badgeColor: 'bg-blue-100 text-blue-700 border-blue-200' },
  { id: 'WEBHOOK_FAILURE', label: '3. Webhook Sync Failure', desc: 'Captured but webhook lost → AI Replay', badgeColor: 'bg-amber-100 text-amber-700 border-amber-200' },
  { id: 'DUPLICATE_PAYMENT', label: '4. Duplicate Charge', desc: 'Double capture → Policy REVIEW Flag', badgeColor: 'bg-purple-100 text-purple-700 border-purple-200' },
  { id: 'INSUFFICIENT_FUNDS', label: '5. Insufficient Funds', desc: 'Bank decline → EMI / Alt Method Suggestion', badgeColor: 'bg-rose-100 text-rose-700 border-rose-200' },
  { id: 'TIMEOUT', label: '6. Payment Timeout', desc: 'Session expired → Session Re-initiate', badgeColor: 'bg-yellow-100 text-yellow-700 border-yellow-200' },
]

interface PayResponse {
  payment_id: string
  order_id: string
  status: string
  scenario: string
  amount: number
  gateway_payment_id: string
  timestamp: string
  is_webhook_delivered: boolean
  message?: string
  error_code?: string
  error_description?: string
  incident_id?: string
  duplicate_payment_id?: string
  ai_investigation?: {
    root_cause: string
    confidence_score: number
    recommended_action: string
    policy_result: string
    auto_executable: boolean
    requires_approval: boolean
    ai_explanation: string
    evidence: string[]
    risk_level: string
    expected_recovery: number
  }
}

export default function Checkout() {
  const { items, customer, getTotal, removeItem, updateQty } = useCartStore()
  const [method, setMethod] = useState<'upi' | 'card' | 'netbanking'>('upi')
  const [scenario, setScenario] = useState<Scenario>('TEMPORARY_FAILURE')
  const [loading, setLoading] = useState(false)
  const [payResult, setPayResult] = useState<PayResponse | null>(null)
  const [recoveryLoading, setRecoveryLoading] = useState(false)
  const [recoveryDone, setRecoveryDone] = useState(false)
  const [recoveryMsg, setRecoveryMsg] = useState('')

  const subtotal = getTotal()
  const finalAmount = subtotal

  const handlePay = async () => {
    if (items.length === 0) return
    setLoading(true)
    setPayResult(null)
    setRecoveryDone(false)
    setRecoveryMsg('')

    try {
      const resp = await api.post('/checkout/pay', {
        amount: finalAmount,
        payment_method: method,
        items: items,
        simulation_scenario: scenario,
        customer_id: customer.id,
      })
      setPayResult(resp.data)
    } catch (err: any) {
      console.error(err)
      alert(err.response?.data?.detail || 'Failed to simulate payment')
    } finally {
      setLoading(false)
    }
  }

  const handleExecuteRecovery = async () => {
    if (!payResult) return
    setRecoveryLoading(true)

    try {
      if (payResult.scenario === 'WEBHOOK_FAILURE') {
        const res = await api.post(`/webhooks/${payResult.payment_id}/replay`)
        setRecoveryDone(true)
        setRecoveryMsg(res.data.message || 'Webhook replayed successfully! Order status updated to COMPLETED.')
      } else {
        const res = await api.post('/checkout/recover', {
          payment_id: payResult.payment_id,
          recovery_action: 'RETRY_ALTERNATE',
        })
        setRecoveryDone(true)
        setRecoveryMsg(res.data.message || 'Payment retried via alternate method. Captured successfully!')
      }
    } catch (err: any) {
      console.error(err)
      alert(err.response?.data?.detail || 'Failed to execute recovery action')
    } finally {
      setRecoveryLoading(false)
    }
  }

  if (items.length === 0 && !payResult) {
    return (
      <div className="max-w-xl mx-auto py-12 px-4 text-center space-y-5">
        <div className="w-20 h-20 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-gray-400 shadow-sm border border-gray-200">
          <ShoppingBag className="w-10 h-10 text-brand-600" />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-900 tracking-tight">Your Cart is Empty</h2>
          <p className="text-sm text-gray-500 mt-1 max-w-sm mx-auto">
            You don't have any items in your checkout cart. Explore our products and add them to your cart.
          </p>
        </div>
        <Link
          to="/shopping"
          className="inline-flex items-center gap-2 px-6 py-3 bg-brand-600 hover:bg-brand-700 text-white font-bold text-sm rounded-xl transition-all shadow-md"
        >
          <span>← Continue Shopping</span>
        </Link>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      {/* Top Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-brand-950 to-slate-900 rounded-2xl p-6 text-white shadow-xl flex items-center justify-between border border-gray-800">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h1 className="text-xl font-bold tracking-tight">Live Checkout & Agentic Recovery</h1>
          </div>
          <p className="text-xs text-gray-300">
            RazorResolve AI Commerce Engine — Autonomous Payment Resolution
          </p>
        </div>
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-xl px-4 py-2 flex items-center gap-2">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-xs font-semibold text-emerald-300">SIMULATION ENVIRONMENT — Demo Transactions</span>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Left Column: Form & Options */}
        <div className="col-span-12 lg:col-span-7 space-y-5">
          {/* Customer info card */}
          <div className="card p-5 space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-900 border-b border-gray-100 pb-3">
              <User className="w-4 h-4 text-brand-600" />
              1. Customer Information
            </div>
            <div className="grid grid-cols-3 gap-3 text-xs">
              <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                <span className="text-gray-400 block mb-0.5">Name</span>
                <span className="font-semibold text-gray-800">{customer.name}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                <span className="text-gray-400 block mb-0.5">Email</span>
                <span className="font-semibold text-gray-800 truncate block">{customer.email}</span>
              </div>
              <div className="bg-gray-50 p-3 rounded-lg border border-gray-100">
                <span className="text-gray-400 block mb-0.5">Customer Tier</span>
                <span className="font-bold text-amber-600 bg-amber-50 px-2 py-0.5 rounded border border-amber-200">GOLD TIER</span>
              </div>
            </div>
          </div>

          {/* Payment Method */}
          <div className="card p-5 space-y-3">
            <div className="flex items-center gap-2 text-sm font-semibold text-gray-900 border-b border-gray-100 pb-3">
              <CreditCard className="w-4 h-4 text-brand-600" />
              2. Select Payment Method
            </div>
            <div className="grid grid-cols-3 gap-3">
              {[
                { id: 'upi', name: 'UPI / QR', icon: Smartphone, desc: 'Google Pay, PhonePe, Paytm' },
                { id: 'card', name: 'Credit / Debit Card', icon: CreditCard, desc: 'Visa, Mastercard, RuPay' },
                { id: 'netbanking', name: 'Net Banking', icon: Building2, desc: 'HDFC, ICICI, SBI, Axis' },
              ].map((m) => {
                const Icon = m.icon
                const active = method === m.id
                return (
                  <button
                    key={m.id}
                    onClick={() => setMethod(m.id as any)}
                    className={cn(
                      'flex flex-col p-3 rounded-xl border text-left transition-all',
                      active
                        ? 'border-brand-500 bg-brand-50/50 ring-2 ring-brand-500/20'
                        : 'border-gray-200 hover:border-gray-300 bg-white'
                    )}
                  >
                    <Icon className={cn('w-5 h-5 mb-2', active ? 'text-brand-600' : 'text-gray-400')} />
                    <span className="text-xs font-bold text-gray-900">{m.name}</span>
                    <span className="text-[10px] text-gray-400 mt-0.5">{m.desc}</span>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Demo Scenario Selector */}
          <div className="card p-5 space-y-3 border-2 border-brand-200/80 bg-gradient-to-br from-brand-50/30 via-white to-white">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-900">
                <Sparkles className="w-4 h-4 text-brand-600" />
                3. Select Payment Failure Scenario (Simulation)
              </div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-brand-700 bg-brand-100 px-2 py-0.5 rounded-full">
                Interactive Test
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2.5">
              {SCENARIOS.map((sc) => {
                const isSelected = scenario === sc.id
                return (
                  <button
                    key={sc.id}
                    onClick={() => setScenario(sc.id)}
                    className={cn(
                      'p-3 rounded-xl border text-left transition-all flex flex-col justify-between',
                      isSelected
                        ? 'border-brand-600 bg-white shadow-md ring-2 ring-brand-500/30'
                        : 'border-gray-200 bg-white hover:border-gray-300 opacity-80 hover:opacity-100'
                    )}
                  >
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-xs font-bold text-gray-900">{sc.label}</span>
                        {isSelected && <Check className="w-3.5 h-3.5 text-brand-600 stroke-[3]" />}
                      </div>
                      <p className="text-[11px] text-gray-500 leading-snug">{sc.desc}</p>
                    </div>
                  </button>
                )
              })}
            </div>
          </div>

          {/* Pay Button */}
          <button
            onClick={handlePay}
            disabled={loading || items.length === 0}
            className="w-full py-4 bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-700 hover:to-indigo-700 text-white font-bold text-base rounded-xl shadow-lg shadow-brand-500/25 flex items-center justify-center gap-2 transition-all transform active:scale-[0.99] disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-5 h-5 animate-spin" />
                <span>Simulating Payment Transaction…</span>
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" />
                <span>Pay {formatINR(finalAmount)} Now</span>
                <ArrowRight className="w-4 h-4 ml-1" />
              </>
            )}
          </button>
        </div>

        {/* Right Column: Order Summary & Agentic Simulation */}
        <div className="col-span-12 lg:col-span-5 space-y-5">
          {/* Order Summary Card */}
          <div className="card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-gray-100 pb-3">
              <div className="flex items-center gap-2 text-sm font-semibold text-gray-900">
                <ShoppingBag className="w-4 h-4 text-brand-600" />
                Order Summary
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-400 font-medium">{items.length} item(s)</span>
                <Link to="/shopping" className="text-xs font-bold text-brand-600 hover:underline">
                  + Add More
                </Link>
              </div>
            </div>

            <div className="space-y-3 max-h-60 overflow-y-auto pr-1">
              {items.length === 0 ? (
                <div className="text-xs text-gray-400 italic py-4 text-center">
                  Your cart is empty.
                </div>
              ) : (
                items.map((item) => (
                  <div key={item.product_id} className="bg-gray-50 border border-gray-100 rounded-xl p-3 text-xs space-y-2">
                    <div className="flex items-start justify-between gap-2">
                      <div className="font-semibold text-gray-800 line-clamp-1 flex-1">{item.name}</div>
                      <button
                        onClick={() => removeItem(item.product_id)}
                        className="text-gray-400 hover:text-rose-600 p-0.5"
                        title="Remove Item"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>

                    <div className="flex items-center justify-between">
                      {/* Quantity controls */}
                      <div className="flex items-center gap-1.5 bg-white px-2 py-1 rounded-lg border border-gray-200 shadow-sm">
                        <button
                          onClick={() => updateQty(item.product_id, Math.max(1, item.qty - 1))}
                          disabled={item.qty <= 1}
                          className="w-5 h-5 rounded hover:bg-gray-100 text-gray-600 flex items-center justify-center font-bold text-xs disabled:opacity-30"
                        >
                          <Minus className="w-3 h-3" />
                        </button>
                        <span className="w-4 text-center font-bold text-gray-900">{item.qty}</span>
                        <button
                          onClick={() => updateQty(item.product_id, item.qty + 1)}
                          className="w-5 h-5 rounded hover:bg-gray-100 text-gray-600 flex items-center justify-center font-bold text-xs"
                        >
                          <Plus className="w-3 h-3" />
                        </button>
                      </div>

                      <div className="font-bold text-gray-900">{formatINR(item.price * item.qty)}</div>
                    </div>
                  </div>
                ))
              )}
            </div>

            <div className="border-t border-gray-100 pt-3 space-y-1.5 text-xs">
              <div className="flex justify-between text-gray-500">
                <span>Subtotal</span>
                <span>{formatINR(subtotal)}</span>
              </div>
              <div className="flex justify-between text-gray-500">
                <span>Taxes & Gateway Fees</span>
                <span className="text-emerald-600 font-medium">FREE</span>
              </div>
              <div className="flex justify-between text-sm font-bold text-gray-900 pt-2 border-t border-gray-100">
                <span>Total Amount</span>
                <span className="text-brand-600 text-base">{formatINR(finalAmount)}</span>
              </div>
            </div>
          </div>

          {/* Agent Simulation & Timeline Output */}
          {payResult && (
            <div className="card p-5 space-y-4 border-2 border-brand-500/40 shadow-xl bg-white animate-fadeIn">
              {/* SUCCESS RESULTS */}
              {payResult.status === 'captured' && payResult.scenario === 'SUCCESS' && (
                <div className="space-y-4">
                  <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center space-y-2">
                    <div className="w-12 h-12 rounded-full bg-emerald-500 text-white flex items-center justify-center mx-auto shadow-md">
                      <CheckCircle2 className="w-7 h-7" />
                    </div>
                    <h3 className="text-lg font-bold text-emerald-900">Payment Successful</h3>
                    <p className="text-xs text-emerald-700">Order Confirmed & Payment Captured</p>
                  </div>

                  <div className="bg-gray-50 p-3.5 rounded-xl border border-gray-100 text-xs space-y-2">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Payment ID:</span>
                      <span className="font-mono font-bold text-gray-800">{payResult.payment_id.slice(0, 16)}…</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Order ID:</span>
                      <span className="font-mono font-bold text-gray-800">{payResult.order_id.slice(0, 16)}…</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Amount Charged:</span>
                      <span className="font-bold text-emerald-600">{formatINR(payResult.amount)}</span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 bg-blue-50 text-blue-800 text-xs p-3 rounded-xl border border-blue-200">
                    <ShieldCheck className="w-4 h-4 text-blue-600 flex-shrink-0" />
                    <span><strong>Agent Status:</strong> Payment processed cleanly. No recovery intervention needed.</span>
                  </div>
                </div>
              )}

              {/* FAILURE / AGENTIC RECOVERY TIMELINE */}
              {payResult.scenario !== 'SUCCESS' && payResult.ai_investigation && (
                <div className="space-y-4">
                  <div className="flex items-center justify-between border-b border-gray-100 pb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-2.5 h-2.5 rounded-full bg-amber-500 animate-pulse" />
                      <h3 className="font-bold text-sm text-gray-900">AI Commerce Agent Timeline</h3>
                    </div>
                    <span className="text-[10px] font-bold bg-gray-100 text-gray-700 px-2 py-0.5 rounded border border-gray-200">
                      Scenario: {payResult.scenario}
                    </span>
                  </div>

                  {/* AGENTIC LOOP TIMELINE STAGES */}
                  <div className="space-y-3">
                    {/* STAGE 1: OBSERVE */}
                    <div className="flex gap-3 text-xs">
                      <div className="flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-rose-500 text-white flex items-center justify-center font-bold text-[10px] shadow">
                          1
                        </div>
                        <div className="w-0.5 flex-1 bg-gray-200 my-1" />
                      </div>
                      <div className="bg-rose-50/70 border border-rose-200 rounded-xl p-3 flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-rose-900 uppercase text-[10px] tracking-wider flex items-center gap-1">
                            <Eye className="w-3 h-3 text-rose-600" /> OBSERVE
                          </span>
                          <span className="text-[10px] font-bold text-rose-700 bg-rose-100 px-1.5 py-0.5 rounded">FAILED EVENT</span>
                        </div>
                        <p className="text-gray-800 font-semibold">{payResult.error_description || payResult.ai_investigation.root_cause}</p>
                        <div className="text-[10px] text-gray-500 flex gap-3 pt-1">
                          <span>Amount: <strong>{formatINR(payResult.amount)}</strong></span>
                          <span>Method: <strong>{method.toUpperCase()}</strong></span>
                        </div>
                      </div>
                    </div>

                    {/* STAGE 2: UNDERSTAND */}
                    <div className="flex gap-3 text-xs">
                      <div className="flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-indigo-600 text-white flex items-center justify-center font-bold text-[10px] shadow">
                          2
                        </div>
                        <div className="w-0.5 flex-1 bg-gray-200 my-1" />
                      </div>
                      <div className="bg-indigo-50/70 border border-indigo-200 rounded-xl p-3 flex-1 space-y-1">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-indigo-900 uppercase text-[10px] tracking-wider flex items-center gap-1">
                            <Brain className="w-3 h-3 text-indigo-600" /> UNDERSTAND
                          </span>
                          <span className="text-[10px] font-semibold text-indigo-700">Intent Analysis</span>
                        </div>
                        <div className="text-gray-800">
                          Customer <strong>{customer.name}</strong> (Gold Tier) has <strong>HIGH purchase intent</strong> for cart value {formatINR(payResult.amount)}.
                        </div>
                      </div>
                    </div>

                    {/* STAGE 3: DIAGNOSE */}
                    <div className="flex gap-3 text-xs">
                      <div className="flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-[10px] shadow">
                          3
                        </div>
                        <div className="w-0.5 flex-1 bg-gray-200 my-1" />
                      </div>
                      <div className="bg-blue-50/70 border border-blue-200 rounded-xl p-3 flex-1 space-y-1.5">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-blue-900 uppercase text-[10px] tracking-wider flex items-center gap-1">
                            <HelpCircle className="w-3 h-3 text-blue-600" /> DIAGNOSE
                          </span>
                          <span className="text-[10px] font-bold text-blue-800 bg-blue-100 px-2 py-0.5 rounded border border-blue-200">
                            Confidence: {Math.round(payResult.ai_investigation.confidence_score * 100)}%
                          </span>
                        </div>
                        <p className="text-gray-900 font-semibold">{payResult.ai_investigation.root_cause}</p>
                        <div className="space-y-0.5 text-[10px] text-gray-600 bg-white/60 p-2 rounded border border-blue-100">
                          {payResult.ai_investigation.evidence.map((ev, i) => (
                            <div key={i} className="flex items-center gap-1">
                              <span className="text-blue-500">•</span>
                              <span>{ev}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* STAGE 4: DECIDE & POLICY CHECK */}
                    <div className="flex gap-3 text-xs">
                      <div className="flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-amber-500 text-white flex items-center justify-center font-bold text-[10px] shadow">
                          4
                        </div>
                        <div className="w-0.5 flex-1 bg-gray-200 my-1" />
                      </div>
                      <div className="bg-amber-50/70 border border-amber-200 rounded-xl p-3 flex-1 space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-amber-900 uppercase text-[10px] tracking-wider flex items-center gap-1">
                            <Scale className="w-3 h-3 text-amber-600" /> DECIDE & POLICY SAFETY CHECK
                          </span>
                          <span className={cn(
                            'text-[10px] font-bold px-2 py-0.5 rounded border',
                            payResult.ai_investigation.policy_result === 'ALLOW'
                              ? 'bg-emerald-100 text-emerald-800 border-emerald-300'
                              : 'bg-amber-100 text-amber-800 border-amber-300'
                          )}>
                            POLICY VERDICT: {payResult.ai_investigation.policy_result}
                          </span>
                        </div>

                        <div className="text-gray-900 font-medium">
                          <strong>Recommended Action:</strong> {payResult.ai_investigation.recommended_action}
                        </div>
                        <div className="text-[11px] text-gray-600">
                          {payResult.ai_investigation.ai_explanation}
                        </div>
                      </div>
                    </div>

                    {/* STAGE 5: ACT & VERIFY */}
                    <div className="flex gap-3 text-xs">
                      <div className="flex flex-col items-center">
                        <div className="w-7 h-7 rounded-full bg-emerald-600 text-white flex items-center justify-center font-bold text-[10px] shadow">
                          5
                        </div>
                      </div>
                      <div className="bg-emerald-50/70 border border-emerald-200 rounded-xl p-3 flex-1 space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="font-bold text-emerald-900 uppercase text-[10px] tracking-wider flex items-center gap-1">
                            <Play className="w-3 h-3 text-emerald-600" /> ACT & VERIFY
                          </span>
                          {recoveryDone && (
                            <span className="text-[10px] font-bold text-emerald-800 bg-emerald-200 px-2 py-0.5 rounded">
                              REVENUE RECOVERED
                            </span>
                          )}
                        </div>

                        {/* POLICY REVIEW SCENARIO (e.g. Duplicate Payment) */}
                        {payResult.ai_investigation.policy_result === 'REVIEW' ? (
                          <div className="bg-amber-100/70 border border-amber-300 p-3 rounded-lg text-amber-900 space-y-2">
                            <div className="flex items-center gap-2 font-bold text-xs">
                              <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                              <span>HUMAN APPROVAL MANDATORY (SAFE AGENT)</span>
                            </div>
                            <p className="text-[11px]">
                              The AI Policy Engine classified this financial action as <strong>REVIEW</strong>.
                              Automatic execution is blocked to protect merchant funds.
                            </p>
                            <Link
                              to="/approvals"
                              className="inline-flex items-center gap-1 text-xs font-bold bg-amber-600 hover:bg-amber-700 text-white px-3 py-1.5 rounded-md shadow transition-colors"
                            >
                              Go to Approval Center →
                            </Link>
                          </div>
                        ) : recoveryDone ? (
                          /* RECOVERY EXECUTED SUCCESS */
                          <div className="bg-emerald-100/80 border border-emerald-300 p-3 rounded-lg text-emerald-900 space-y-1 animate-fadeIn">
                            <div className="flex items-center gap-2 font-bold text-xs">
                              <CheckCircle className="w-4 h-4 text-emerald-600" />
                              <span>Recovery Executed & Verified</span>
                            </div>
                            <p className="text-[11px]">{recoveryMsg}</p>
                            <div className="text-[10px] text-emerald-700 font-semibold pt-1">
                              ✓ Revenue Recovered: {formatINR(payResult.amount)} | Audit Log Entry Recorded
                            </div>
                          </div>
                        ) : (
                          /* TRIGGER RECOVERY ACTION BUTTON */
                          <div className="space-y-2">
                            <p className="text-[11px] text-gray-700">
                              Policy status is <strong>ALLOW</strong>. Click below to execute the autonomous recovery workflow:
                            </p>
                            <button
                              onClick={handleExecuteRecovery}
                              disabled={recoveryLoading}
                              className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-lg shadow flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                            >
                              {recoveryLoading ? (
                                <>
                                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                                  <span>Executing Agentic Recovery…</span>
                                </>
                              ) : (
                                <>
                                  <Sparkles className="w-3.5 h-3.5" />
                                  <span>Execute AI Recovery ({payResult.scenario === 'WEBHOOK_FAILURE' ? 'Replay Webhook' : 'Retry Payment'})</span>
                                </>
                              )}
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
