import { useEffect, useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, LineChart, Line, FunnelChart, Funnel, LabelList, Cell
} from 'recharts'
import { getDashboardOverview, getRevenueTrend, getFailureBreakdown } from '@/lib/api'
import { formatINR } from '@/lib/utils'

const FUNNEL_DATA = [
  { name: 'Product Views', value: 12430, fill: '#3b5ef0' },
  { name: 'Add to Cart', value: 4210, fill: '#6366f1' },
  { name: 'Checkout Started', value: 2890, fill: '#8b5cf6' },
  { name: 'Payment Attempted', value: 2240, fill: '#a78bfa' },
  { name: 'Payment Captured', value: 1820, fill: '#22c55e' },
]

export default function Analytics() {
  const [overview, setOverview] = useState<Record<string, number>>({})
  const [trend, setTrend] = useState<{ date: string; revenue: number }[]>([])
  const [breakdown, setBreakdown] = useState<{ reason: string; count: number; amount: number }[]>([])

  useEffect(() => {
    Promise.all([getDashboardOverview(), getRevenueTrend(30), getFailureBreakdown()])
      .then(([ov, tr, br]) => {
        setOverview(ov.data)
        setTrend(tr.data.trend)
        setBreakdown(br.data.breakdown)
      })
  }, [])

  return (
    <div className="space-y-6">
      {/* Key numbers */}
      <div className="grid grid-cols-4 gap-4">
        {[
          { label: 'Total Revenue', value: formatINR(overview.total_revenue || 0), sub: `${overview.total_orders || 0} orders` },
          { label: 'Revenue at Risk', value: formatINR(overview.revenue_at_risk || 0), sub: 'Unrecovered' },
          { label: 'Revenue Recovered', value: formatINR(overview.revenue_recovered || 0), sub: 'AI-driven' },
          { label: 'Recovery Rate', value: `${overview.ai_recovery_success_rate || 0}%`, sub: 'AI success rate' },
        ].map(m => (
          <div key={m.label} className="card p-4">
            <div className="text-xs text-gray-500 mb-1">{m.label}</div>
            <div className="text-2xl font-bold text-gray-900">{m.value}</div>
            <div className="text-xs text-gray-400">{m.sub}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        {/* Revenue trend */}
        <div className="card p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Daily Revenue (30 days)</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={trend}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={v => v.slice(5)} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: number) => [formatINR(v), 'Revenue']} />
              <Line type="monotone" dataKey="revenue" stroke="#3b5ef0" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Failure breakdown */}
        <div className="card p-5">
          <h3 className="font-semibold text-gray-900 mb-4">Revenue at Risk by Failure Type</h3>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={breakdown}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis dataKey="reason" tick={{ fontSize: 10 }} angle={-15} textAnchor="end" height={40} />
              <YAxis tick={{ fontSize: 11 }} tickFormatter={v => `₹${(v/1000).toFixed(0)}k`} />
              <Tooltip formatter={(v: number) => [formatINR(v), 'Amount']} />
              <Bar dataKey="amount" fill="#ef4444" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Conversion funnel */}
      <div className="card p-5">
        <h3 className="font-semibold text-gray-900 mb-1">Conversion Funnel</h3>
        <p className="text-xs text-gray-500 mb-4">Simulated customer journey from browse to capture</p>
        <div className="space-y-2">
          {FUNNEL_DATA.map((step, i) => {
            const pct = Math.round((step.value / FUNNEL_DATA[0].value) * 100)
            const dropPct = i > 0 ? Math.round((1 - step.value / FUNNEL_DATA[i - 1].value) * 100) : 0
            return (
              <div key={step.name} className="flex items-center gap-3">
                <div className="w-36 text-sm text-gray-600 flex-shrink-0">{step.name}</div>
                <div className="flex-1 bg-gray-100 rounded-full h-6 relative overflow-hidden">
                  <div
                    className="h-6 rounded-full flex items-center justify-end pr-3 transition-all"
                    style={{ width: `${pct}%`, backgroundColor: step.fill }}
                  >
                    <span className="text-white text-xs font-semibold">{step.value.toLocaleString()}</span>
                  </div>
                </div>
                <div className="w-20 text-right">
                  <span className="text-sm font-medium text-gray-700">{pct}%</span>
                  {dropPct > 0 && <div className="text-xs text-red-500">-{dropPct}%</div>}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
