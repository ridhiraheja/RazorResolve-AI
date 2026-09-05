import { useEffect, useState } from 'react'
import { getAIDecisions, getAuditLogs } from '@/lib/api'
import { timeAgo, policyColor, cn } from '@/lib/utils'
import { Bot, CheckCircle, Clock, Shield, Activity } from 'lucide-react'

interface Decision {
  id: string
  incident_id: string | null
  agent_name: string
  decision_type: string
  observation: string
  reasoning: string
  decision: string
  action_taken: string
  policy_result: string
  confidence_score: number
  expected_impact: number
  actual_result: string | null
  evidence: Record<string, unknown> | null
  created_at: string
}

interface AuditItem {
  id: string
  timestamp: string
  agent: string
  observation: string
  decision: string
  action: string
  policy_result: string
  result: string
  confidence: number
}

const AGENTS = [
  { name: 'PaymentInvestigationAgent', color: 'bg-blue-100 text-blue-700', icon: '🔍' },
  { name: 'RecoveryAgent',             color: 'bg-green-100 text-green-700', icon: '💚' },
  { name: 'PolicyAgent',               color: 'bg-yellow-100 text-yellow-700', icon: '🛡️' },
  { name: 'CustomerIntentAgent',       color: 'bg-purple-100 text-purple-700', icon: '🎯' },
  { name: 'CommerceAgent',             color: 'bg-orange-100 text-orange-700', icon: '🛒' },
  { name: 'IncidentManager',           color: 'bg-red-100 text-red-700', icon: '🚨' },
  { name: 'AnalyticsAgent',            color: 'bg-teal-100 text-teal-700', icon: '📊' },
]

function agentStyle(name: string) {
  return AGENTS.find(a => a.name === name) ?? { color: 'bg-gray-100 text-gray-700', icon: '🤖' }
}

export default function Agent() {
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [logs, setLogs] = useState<AuditItem[]>([])
  const [tab, setTab] = useState<'decisions' | 'activity'>('decisions')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([getAIDecisions(), getAuditLogs()])
      .then(([d, l]) => {
        setDecisions(d.data.decisions)
        setLogs(l.data.logs)
      })
      .finally(() => setLoading(false))
  }, [])

  const LOOP_STEPS = [
    { icon: Activity, label: 'OBSERVE', color: 'text-blue-600', desc: 'Monitor payment events' },
    { icon: Bot, label: 'UNDERSTAND', color: 'text-purple-600', desc: 'Diagnose root cause' },
    { icon: CheckCircle, label: 'DECIDE', color: 'text-yellow-600', desc: 'Select recovery action' },
    { icon: Shield, label: 'ACT', color: 'text-green-600', desc: 'Execute if policy allows' },
    { icon: Clock, label: 'VERIFY', color: 'text-orange-600', desc: 'Confirm outcome' },
    { icon: Activity, label: 'LEARN', color: 'text-teal-600', desc: 'Update confidence model' },
  ]

  return (
    <div className="space-y-4">
      {/* Agentic loop */}
      <div className="card p-5">
        <h3 className="font-semibold text-gray-900 mb-4">Agentic Loop</h3>
        <div className="flex items-center gap-0 overflow-x-auto">
          {LOOP_STEPS.map((step, i) => (
            <div key={step.label} className="flex items-center flex-shrink-0">
              <div className="flex flex-col items-center gap-1.5 px-4">
                <div className={cn('w-10 h-10 rounded-full border-2 flex items-center justify-center', step.color.replace('text-', 'border-'))}>
                  <step.icon className={cn('w-4 h-4', step.color)} />
                </div>
                <span className={cn('text-xs font-bold tracking-wide', step.color)}>{step.label}</span>
                <span className="text-xs text-gray-400 text-center max-w-20">{step.desc}</span>
              </div>
              {i < LOOP_STEPS.length - 1 && (
                <div className="w-8 h-px bg-gray-200 flex-shrink-0" />
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Agent status grid */}
      <div className="grid grid-cols-4 gap-3">
        {AGENTS.map(a => (
          <div key={a.name} className="card p-4">
            <div className={cn('inline-flex items-center gap-1.5 px-2 py-1 rounded-md text-xs font-medium mb-2', a.color)}>
              <span>{a.icon}</span>
              <span className="truncate">{a.name.replace('Agent', '').replace('Manager', '')}</span>
            </div>
            <div className="flex items-center gap-1.5">
              <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
              <span className="text-xs text-gray-500">Active</span>
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="card overflow-hidden">
        <div className="border-b border-gray-100 flex">
          {(['decisions', 'activity'] as const).map(t => (
            <button
              key={t}
              onClick={() => setTab(t)}
              className={cn('px-5 py-3 text-sm font-medium transition-colors', tab === t ? 'border-b-2 border-brand-500 text-brand-600' : 'text-gray-500 hover:text-gray-700')}
            >
              {t === 'decisions' ? 'AI Decisions' : 'Activity Timeline'}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-400 animate-pulse">Loading agent data…</div>
        ) : tab === 'decisions' ? (
          <div className="divide-y divide-gray-50">
            {decisions.length === 0 ? (
              <div className="text-center py-12 text-gray-400">No decisions recorded.</div>
            ) : decisions.map(d => {
              const style = agentStyle(d.agent_name)
              return (
                <div key={d.id} className="px-5 py-4">
                  <div className="flex items-start gap-3">
                    <span className={cn('px-2 py-0.5 rounded text-xs font-medium flex-shrink-0 mt-0.5', style.color)}>
                      {style.icon} {d.agent_name.replace('Agent', '').replace('Manager', '')}
                    </span>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1 flex-wrap">
                        <span className="text-sm font-semibold text-gray-900">{d.decision}</span>
                        <span className={cn('text-xs px-2 py-0.5 rounded-full font-semibold', policyColor(d.policy_result))}>
                          {d.policy_result}
                        </span>
                        <span className="text-xs text-gray-400 ml-auto">{timeAgo(d.created_at)}</span>
                      </div>

                      {/* OBSERVE → UNDERSTAND → DECIDE → ACT */}
                      <div className="grid grid-cols-2 gap-x-4 gap-y-1 mt-2 text-xs">
                        <div><span className="text-gray-400">Observation: </span><span className="text-gray-700">{d.observation}</span></div>
                        <div><span className="text-gray-400">Reasoning: </span><span className="text-gray-700">{d.reasoning}</span></div>
                        {d.action_taken && <div><span className="text-gray-400">Action: </span><span className="text-gray-700">{d.action_taken}</span></div>}
                        {d.actual_result && <div><span className="text-gray-400">Result: </span><span className="text-gray-700">{d.actual_result}</span></div>}
                      </div>

                      <div className="mt-2 flex items-center gap-3 text-xs text-gray-400">
                        <span>Confidence: <span className="font-semibold text-gray-700">{Math.round(d.confidence_score * 100)}%</span></span>
                        {d.expected_impact > 0 && (
                          <span>Expected impact: <span className="font-semibold text-green-700">₹{d.expected_impact.toLocaleString('en-IN')}</span></span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              )
            })}
          </div>
        ) : (
          <div className="divide-y divide-gray-50 max-h-96 overflow-y-auto">
            {logs.length === 0 ? (
              <div className="text-center py-12 text-gray-400">No activity logged.</div>
            ) : logs.map(l => {
              const style = agentStyle(l.agent)
              return (
                <div key={l.id} className="px-5 py-3 flex items-start gap-3">
                  <div className={cn('mt-0.5 px-1.5 py-0.5 rounded text-xs font-medium flex-shrink-0', style.color)}>
                    {style.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 text-xs flex-wrap">
                      <span className="font-medium text-gray-800">{l.agent}</span>
                      <span className={cn('px-1.5 py-0.5 rounded text-xs font-semibold', policyColor(l.policy_result))}>{l.policy_result}</span>
                      <span className="text-gray-400 ml-auto">{timeAgo(l.timestamp)}</span>
                    </div>
                    <div className="text-xs text-gray-700 mt-0.5">{l.action}</div>
                    <div className="text-xs text-gray-400 mt-0.5">
                      Decision: {l.decision} · Result: {l.result} · Confidence: {Math.round(l.confidence * 100)}%
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
