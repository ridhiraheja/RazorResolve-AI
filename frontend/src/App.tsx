import { Routes, Route, useLocation } from 'react-router-dom'
import Sidebar from '@/components/layout/Sidebar'
import Topbar from '@/components/layout/Topbar'
import Overview from '@/pages/Overview'
import Incidents from '@/pages/Incidents'
import Payments from '@/pages/Payments'
import Recovery from '@/pages/Recovery'
import Agent from '@/pages/Agent'
import Shopping from '@/pages/Shopping'
import Products from '@/pages/Products'
import Analytics from '@/pages/Analytics'
import Approvals from '@/pages/Approvals'
import AuditLog from '@/pages/AuditLog'
import Checkout from '@/pages/Checkout'
import FinancialChat from '@/pages/FinancialChat'

const PAGE_META: Record<string, { title: string; subtitle: string }> = {
  '/':          { title: 'Overview',              subtitle: 'Revenue and recovery metrics' },
  '/incidents': { title: 'Incident Center',       subtitle: 'Active payment and checkout incidents' },
  '/payments':  { title: 'Payment Intelligence',  subtitle: 'AI-diagnosed payment events' },
  '/recovery':  { title: 'Checkout Recovery',     subtitle: 'Abandoned cart recovery opportunities' },
  '/agent':     { title: 'AI Commerce Agent',     subtitle: 'Agent decisions, actions, and reasoning' },
  '/shopping':  { title: 'AI Shopping Assistant', subtitle: 'Customer-facing smart shopping experience' },
  '/checkout':  { title: 'Live Agentic Checkout', subtitle: 'Simulate live payment failures and AI recovery' },
  '/financial': { title: 'AI Financial Chat',    subtitle: 'Educational stock analysis and company metrics' },
  '/products':  { title: 'Product Intelligence',  subtitle: 'Catalog, conversions, and recommendations' },
  '/analytics': { title: 'Revenue Analytics',     subtitle: 'Full revenue funnel and recovery metrics' },
  '/approvals': { title: 'Approval Center',       subtitle: 'Actions requiring human review' },
  '/audit':     { title: 'Audit Log',             subtitle: 'Complete AI decision trail' },
}

function useCurrentMeta() {
  const location = useLocation()
  return PAGE_META[location.pathname] ?? { title: 'RazorResolve AI', subtitle: '' }
}

export default function App() {
  const meta = useCurrentMeta()

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <div className="flex flex-col flex-1 ml-60 min-w-0 overflow-hidden">
        <Topbar title={meta.title} subtitle={meta.subtitle} />
        <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
          <Routes>
            <Route path="/"          element={<Overview />} />
            <Route path="/incidents" element={<Incidents />} />
            <Route path="/payments"  element={<Payments />} />
            <Route path="/recovery"  element={<Recovery />} />
            <Route path="/agent"     element={<Agent />} />
            <Route path="/shopping"  element={<Shopping />} />
            <Route path="/checkout"  element={<Checkout />} />
            <Route path="/financial" element={<FinancialChat />} />
            <Route path="/products"  element={<Products />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/approvals" element={<Approvals />} />
            <Route path="/audit"     element={<AuditLog />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}
