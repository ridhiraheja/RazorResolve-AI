import { useEffect, useState } from 'react'
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, PieChart, Pie, Legend
} from 'recharts'
import {
  TrendingUp, AlertTriangle, CreditCard, ShoppingCart,
  Zap, CheckCircle, Target, Activity
} from 'lucide-react'
import { getDashboardOverview, getRevenueTrend, getFailureBreakdown } from '@/lib/api'
import { formatINR } from '@/lib/utils'

interface OverviewData {
  total_revenue: number
  conversion_rate: number
  failed_payments: number
  abandoned_checkouts: number
  revenue_at_risk: number
  revenue_recovered: number
  ai_recovery_success_rate: number
  active_incidents: number
  total_orders: number
  payment_success_rate: number
  total_incidents: number
}

function MetricCard({
  icon: Icon, label, value, sub, color, trend
}: {
  icon: React.ElementType
  label: string
  value: string
  sub?: string
  color: string
  trend?: string
}) {
  return (
    <div className="card p-5">
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-gray-500 font-medium">{label}</span>
        <div className={`w-9 h-9 rounded-lg flex items-center justify-center ${color}`}>
          <Icon className="w-4 h-4" />
        </div>
      </div>
      <div className="text-2xl font-bold text-gray-900">{value}</div>
      {sub && <div className="text-xs text-gray-500 mt-1">{sub}</div>}
      {trend && <div className="text-xs text-green-600 mt-1 font-medium">{trend}</div>}
    </div>
  )
}

const FAILURE_COLORS = ['#ef4444', '#f97316', '#eab308', '#8b5cf6', '#06b6d4', '#10b981', '#6366f1', '#f43f5e']

export default function Overview() {
  const [data, setData] = useState<OverviewData | null>(null)
  const [trend, setTrend] = useState<{ date: string; revenue: number }[]>([])
  const [breakdown, setBreakdown] = useState<{ reason: string; count: number; amount: number }[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      getDashboardOverview(),
      getRevenueTrend(30),
      getFailureBreakdown(),
    ]).then(([ov, tr, br]) => {
      setData(ov.data)
      setTrend(tr.data.trend)
      setBreakdown(br.data.breakdown)
    }).finally(() => setLoading(false))
  }, [])

  if (loading) return (
    <div className="flex items-center justify-center h-64">
      <div className="text-gray-400 animate-pulse">Loading dashboard…</div>
    </div>
  )

  if (!data) return <div className="text-red-500">Failed to load dashboard data.</div>

  const metrics = [
    {
      icon: TrendingUp, label: 'Total Revenue', color: 'bg-green-100 text-green-600',
      value: formatINR(data.total_revenue),
      sub: `${data.total_orders} orders processed`,
    },
    {
      icon: Target, label: 'Conversion Rate', color: 'bg-blue-100 text-blue-600',
      value: `${data.conversion_rate}%`,
      sub: `${data.payment_success_rate}% payment success`,
    },
    {
      icon: CreditCard, label: 'Failed Payments', color: 'bg-red-100 text-red-600',
      value: String(data.failed_payments),
      sub: formatINR(data.revenue_at_risk) + ' at risk',
    },
    {
      icon: ShoppingCart, label: 'Abandoned Checkouts', color: 'bg-orange-100 text-orange-600',
      value: String(data.abandoned_checkouts),
      sub: 'Awaiting recovery',
    },
    {
      icon: Zap, label: 'Revenue Recovered', color: 'bg-purple-100 text-purple-600',
      value: formatINR(data.revenue_recovered),
      trend: '↑ AI-driven recovery',
    },
    {
      icon: CheckCircle, label: 'AI Recovery Rate', color: 'bg-teal-100 text-teal-600',
      value: `${data.ai_recovery_success_rate}%`,
      sub: `${data.total_incidents} total incidents`,
    },
    {
      icon: AlertTriangle, label: 'Active Incidents', color: 'bg-yellow-100 text-yellow-600',
      value: String(data.active_incidents),
      sub: 'Requiring attention',
    },
    {
      icon: Activity, label: 'Revenue at Risk', color: 'bg-rose-100 text-rose-600',
      value: formatINR(data.revenue_at_risk),
      sub: 'Recoverable with AI action',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Alert banner */}
      {data.active_incidents > 0 && (
        <div className="flex items-center gap-3 bg-orange-50 border border-orange-200 rounded-xl px-4 py-3">
          <AlertTriangle className="w-4 h-4 text-orange-500 flex-shrink-0" />
          <span className="text-sm text-orange-800 font-medium">
            {data.active_incidents} active incident{data.active_incidents > 1 ? 's' : ''} require attention.
          </span>
          <a href="/incidents" className="ml-auto text-sm text-orange-700 underline">View all →</a>
        </div>
      )}

      {/* Metrics grid */}
      <div className="grid grid-cols-4 gap-4">
        {metrics.map((m) => (
          <MetricCard key={m.label} {...m} />
        ))}
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-3 gap-4">
        {/* Revenue trend */}
        <div className="card p-5 col-span-2">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-gray-900">Revenue Trend (30 days)</h3>
              <p className="text-xs text-gray-500">Daily captured revenue</p>
            </div>
          </div>
          {trend.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={trend}>
                <defs>
                  <linearGradient id="revGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3b5ef0" stopOpacity={0.15} />
                    <stop offset="95%" stopColor="#3b5ef0" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="date" tick={{ fontSize: 11 }} tickFormatter={(v) => v.slice(5)} />
                <YAxis tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                <Tooltip formatter={(v: number) => formatINR(v)} labelFormatter={(l) => `Date: ${l}`} />
                <Area type="monotone" dataKey="revenue" stroke="#3b5ef0" fill="url(#revGrad)" strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">
              No revenue data for the selected period
            </div>
          )}
        </div>

        {/* Failure breakdown */}
        <div className="card p-5">
          <h3 className="font-semibold text-gray-900 mb-1">Failure Breakdown</h3>
          <p className="text-xs text-gray-500 mb-4">By failure reason</p>
          {breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={200}>
              <PieChart>
                <Pie data={breakdown} dataKey="count" nameKey="reason" cx="50%" cy="50%" outerRadius={70} label={false}>
                  {breakdown.map((_, i) => (
                    <Cell key={i} fill={FAILURE_COLORS[i % FAILURE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number, name: string) => [v, name]} />
                <Legend iconSize={8} wrapperStyle={{ fontSize: '11px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400 text-sm">No failures</div>
          )}
        </div>
      </div>

      {/* Bottom row */}
      <div className="grid grid-cols-2 gap-4">
        {/* Failure amounts */}
        <div className="card p-5">
          <h3 className="font-semibold text-gray-900 mb-1">Revenue at Risk by Failure Type</h3>
          <p className="text-xs text-gray-500 mb-4">₹ amount of failed payments</p>
          {breakdown.length > 0 ? (
            <ResponsiveContainer width="100%" height={160}>
              <BarChart data={breakdown} layout="vertical" margin={{ left: 60 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis type="number" tick={{ fontSize: 11 }} tickFormatter={(v) => `₹${(v/1000).toFixed(0)}k`} />
                <YAxis dataKey="reason" type="category" tick={{ fontSize: 11 }} width={110} />
                <Tooltip formatter={(v: number) => formatINR(v)} />
                <Bar dataKey="amount" radius={[0, 4, 4, 0]}>
                  {breakdown.map((_, i) => <Cell key={i} fill={FAILURE_COLORS[i % FAILURE_COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-36 text-gray-400 text-sm">No data</div>
          )}
        </div>

        {/* Quick stats */}
        <div className="card p-5">
          <h3 className="font-semibold text-gray-900 mb-4">AI Agent Performance</h3>
          <div className="space-y-4">
            {[
              { label: 'Payment Success Rate', value: data.payment_success_rate, color: 'bg-green-500' },
              { label: 'AI Recovery Success Rate', value: data.ai_recovery_success_rate, color: 'bg-blue-500' },
              { label: 'Conversion Rate', value: data.conversion_rate, color: 'bg-purple-500' },
            ].map(({ label, value, color }) => (
              <div key={label}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-600">{label}</span>
                  <span className="font-semibold text-gray-900">{value.toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-100 rounded-full h-2">
                  <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${Math.min(value, 100)}%` }} />
                </div>
              </div>
            ))}
          </div>

          <div className="mt-5 pt-4 border-t border-gray-100 grid grid-cols-2 gap-3">
            <div className="text-center">
              <div className="text-xl font-bold text-gray-900">{data.total_incidents}</div>
              <div className="text-xs text-gray-500">Total Incidents</div>
            </div>
            <div className="text-center">
              <div className="text-xl font-bold text-green-600">{formatINR(data.revenue_recovered)}</div>
              <div className="text-xs text-gray-500">Recovered</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
