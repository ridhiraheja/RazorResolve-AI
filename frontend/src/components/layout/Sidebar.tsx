import { NavLink } from 'react-router-dom'
import {
  LayoutDashboard, AlertTriangle, CreditCard, ShoppingCart,
  Bot, Package, BarChart3, CheckCircle, FileText, ShoppingBag, LineChart
} from 'lucide-react'
import { cn } from '@/lib/utils'

interface NavSection {
  title: string
  items: Array<{ to: string; icon: React.ElementType; label: string }>
}

const navSections: NavSection[] = [
  {
    title: 'COMMERCE',
    items: [
      { to: '/',          icon: LayoutDashboard, label: 'Overview' },
      { to: '/shopping',  icon: ShoppingBag,     label: 'AI Shopping' },
      { to: '/checkout',  icon: CheckCircle,     label: 'Live Checkout (Demo)' },
      { to: '/products',  icon: Package,         label: 'Product Intelligence' },
    ]
  },
  {
    title: 'PAYMENTS & RECOVERY',
    items: [
      { to: '/payments',  icon: CreditCard,      label: 'Payment Intelligence' },
      { to: '/incidents', icon: AlertTriangle,   label: 'Incident Center' },
      { to: '/recovery',  icon: ShoppingCart,    label: 'Checkout Recovery' },
      { to: '/approvals', icon: CheckCircle,     label: 'Approval Center' },
    ]
  },
  {
    title: 'AI AGENTS',
    items: [
      { to: '/agent',     icon: Bot,             label: 'AI Commerce Agent' },
      { to: '/financial', icon: LineChart,       label: 'AI Financial Chat' },
    ]
  },
  {
    title: 'INSIGHTS & AUDIT',
    items: [
      { to: '/analytics', icon: BarChart3,       label: 'Revenue Analytics' },
      { to: '/audit',     icon: FileText,        label: 'Audit Log' },
    ]
  }
]

export default function Sidebar() {
  return (
    <aside className="fixed inset-y-0 left-0 z-40 w-60 bg-gray-900 flex flex-col">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 h-16 border-b border-gray-800 flex-shrink-0">
        <div className="w-8 h-8 rounded-lg bg-brand-500 flex items-center justify-center flex-shrink-0 shadow-md">
          <Bot className="w-4 h-4 text-white" />
        </div>
        <div>
          <div className="text-white font-bold text-sm leading-tight tracking-wide">RazorResolve AI</div>
          <div className="text-gray-400 text-[10px]">AI Commerce Agent</div>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 overflow-y-auto py-3 px-3 space-y-4">
        {navSections.map((sec) => (
          <div key={sec.title} className="space-y-1">
            <div className="px-3 text-[10px] font-bold text-gray-400 tracking-wider uppercase mb-1">
              {sec.title}
            </div>
            {sec.items.map(({ to, icon: Icon, label }) => (
              <NavLink
                key={to}
                to={to}
                end={to === '/'}
                className={({ isActive }) =>
                  cn(
                    'flex items-center gap-2.5 px-3 py-1.5 rounded-lg text-xs transition-colors',
                    isActive
                      ? 'bg-brand-600 text-white font-semibold shadow'
                      : 'text-gray-400 hover:text-gray-100 hover:bg-gray-800/80'
                  )
                }
              >
                <Icon className="w-3.5 h-3.5 flex-shrink-0" />
                <span>{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-5 py-3.5 border-t border-gray-800 flex-shrink-0">
        <div className="text-[11px] font-semibold text-gray-300">
          RazorResolve AI v2.4
        </div>
        <div className="text-[10px] text-gray-500 mt-0.5">
          Autonomous Commerce Intelligence
        </div>
      </div>
    </aside>
  )
}
