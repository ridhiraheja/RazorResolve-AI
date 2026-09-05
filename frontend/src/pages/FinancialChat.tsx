import { useState, useRef, useEffect } from 'react'
import { sendFinancialChat } from '@/lib/api'
import { cn } from '@/lib/utils'
import {
  Send, Bot, Trash2, LineChart as LineChartIcon, ShieldAlert,
  TrendingUp, Activity, Sparkles, HelpCircle, User, ArrowUpRight
} from 'lucide-react'
import {
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts'

interface AnalysisMetrics {
  price?: string
  market_cap?: string
  pe_ratio?: string
  revenue_growth?: string
  profit_growth?: string
  operating_margin?: string
  '52_week_high'?: string
  '52_week_low'?: string
}

interface PriceTrendPoint {
  month: string
  price: number
}

interface ComparisonRow {
  metric: string
  c1: string
  c2: string
}

interface FinancialResponse {
  intent: string
  answer: string
  company?: string
  ticker?: string
  analysis?: AnalysisMetrics
  strengths?: string[]
  risks?: string[]
  risk_level?: string
  price_trend?: PriceTrendPoint[]
  comparison_table?: ComparisonRow[]
  company_1?: any
  company_2?: any
  disclaimer?: string
}

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  text?: string
  data?: FinancialResponse
  timestamp: Date
}

const SUGGESTED_PROMPTS = [
  'Analyze TCS',
  'Analyze Infosys stock',
  'Compare TCS and Infosys',
  'What are the key risks for Reliance?',
  'Show me the recent trend of TCS',
  'Explain P/E ratio',
  'What financial metrics should I look at before analyzing a stock?',
]

export default function FinancialChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'init_0',
      role: 'assistant',
      text: "Hello! I am your AI Financial Analyst.\n\nAsk me about Indian stocks (TCS, Infosys, Reliance, HDFC Bank, ICICI Bank, ITC, Wipro, HCLTech, L&T, Airtel), compare companies, or ask for financial metric explanations.",
      timestamp: new Date(),
    },
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async (queryText: string) => {
    const q = queryText.trim()
    if (!q || loading) return

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      text: q,
      timestamp: new Date(),
    }

    setMessages((prev) => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const resp = await sendFinancialChat(q)
      const data: FinancialResponse = resp.data
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        text: data.answer,
        data: data,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, aiMsg])
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          text: 'Sorry, I encountered an error retrieving financial data. Please try asking again.',
          timestamp: new Date(),
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  const clearChat = () => {
    setMessages([
      {
        id: Date.now().toString(),
        role: 'assistant',
        text: 'Chat cleared. Ask me about a stock, company comparison, or financial metric!',
        timestamp: new Date(),
      },
    ])
  }

  return (
    <div className="space-y-4">
      {/* Header Banner */}
      <div className="card p-5 bg-gradient-to-r from-slate-900 via-slate-800 to-slate-900 text-white flex items-center justify-between shadow-lg">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <LineChartIcon className="w-5 h-5 text-emerald-400" />
            <h1 className="text-lg font-bold tracking-tight">AI Financial Analyst</h1>
          </div>
          <p className="text-xs text-gray-300">
            Educational stock intelligence, company comparisons, and financial metric explanations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <div className="bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs px-3 py-1.5 rounded-lg flex items-center gap-1.5 font-medium">
            <ShieldAlert className="w-3.5 h-3.5 text-amber-400 flex-shrink-0" />
            <span>Demo Market Data — Educational Purpose Only</span>
          </div>
          <button
            onClick={clearChat}
            className="p-2 text-gray-400 hover:text-white bg-slate-800 hover:bg-slate-700 rounded-lg transition-colors text-xs flex items-center gap-1 border border-gray-700"
            title="Clear Chat History"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Clear</span>
          </button>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        {/* Main Chat Container */}
        <div className="col-span-12 lg:col-span-8 card flex flex-col h-[calc(100vh-14rem)] overflow-hidden">
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={cn(
                  'flex gap-3',
                  msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                )}
              >
                {msg.role === 'assistant' ? (
                  <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center flex-shrink-0 text-white shadow-md">
                    <Bot className="w-4 h-4" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center flex-shrink-0 text-white shadow-md">
                    <User className="w-4 h-4" />
                  </div>
                )}

                <div className={cn('max-w-2xl flex flex-col gap-2', msg.role === 'user' ? 'items-end' : 'items-start')}>
                  {/* Text bubble */}
                  {msg.text && (
                    <div
                      className={cn(
                        'px-4 py-3 rounded-2xl text-xs leading-relaxed whitespace-pre-line shadow-sm',
                        msg.role === 'user'
                          ? 'bg-brand-600 text-white rounded-tr-sm font-medium'
                          : 'bg-white border border-gray-200 text-gray-800 rounded-tl-sm'
                      )}
                    >
                      {msg.text}
                    </div>
                  )}

                  {/* STRUCTURED DATA OUTPUT: ANALYSIS CARDS & CHARTS */}
                  {msg.data && (
                    <div className="w-full space-y-3 mt-1">
                      {/* Analysis Cards Grid */}
                      {msg.data.analysis && (
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                          <div className="bg-slate-50 border border-slate-200 p-2.5 rounded-xl">
                            <span className="text-[10px] text-gray-400 font-medium block">Current Price</span>
                            <span className="text-sm font-bold text-gray-900">{msg.data.analysis.price}</span>
                          </div>
                          <div className="bg-slate-50 border border-slate-200 p-2.5 rounded-xl">
                            <span className="text-[10px] text-gray-400 font-medium block">Market Cap</span>
                            <span className="text-xs font-bold text-gray-900">{msg.data.analysis.market_cap}</span>
                          </div>
                          <div className="bg-slate-50 border border-slate-200 p-2.5 rounded-xl">
                            <span className="text-[10px] text-gray-400 font-medium block">P/E Ratio</span>
                            <span className="text-xs font-bold text-brand-700">{msg.data.analysis.pe_ratio}x</span>
                          </div>
                          <div className="bg-slate-50 border border-slate-200 p-2.5 rounded-xl">
                            <span className="text-[10px] text-gray-400 font-medium block">Revenue Growth</span>
                            <span className="text-xs font-bold text-emerald-600">{msg.data.analysis.revenue_growth}</span>
                          </div>
                        </div>
                      )}

                      {/* Stock Price Trend Chart */}
                      {msg.data.price_trend && msg.data.price_trend.length > 0 && (
                        <div className="bg-white border border-gray-200 rounded-xl p-3 shadow-sm space-y-2">
                          <div className="flex items-center justify-between text-xs">
                            <span className="font-bold text-gray-800 flex items-center gap-1.5">
                              <TrendingUp className="w-3.5 h-3.5 text-emerald-600" />
                              {msg.data.company} — Stock Price Trend
                            </span>
                            <span className="text-[10px] text-gray-400 bg-gray-100 px-2 py-0.5 rounded">
                              Demo Historical Data
                            </span>
                          </div>
                          <ResponsiveContainer width="100%" height={160}>
                            <AreaChart data={msg.data.price_trend}>
                              <defs>
                                <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.25} />
                                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                </linearGradient>
                              </defs>
                              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                              <XAxis dataKey="month" tick={{ fontSize: 10 }} />
                              <YAxis tick={{ fontSize: 10 }} domain={['auto', 'auto']} tickFormatter={(v) => `₹${v}`} />
                              <Tooltip formatter={(val: number) => [`₹${val}`, 'Price']} />
                              <Area type="monotone" dataKey="price" stroke="#10b981" fill="url(#priceGrad)" strokeWidth={2} />
                            </AreaChart>
                          </ResponsiveContainer>
                        </div>
                      )}

                      {/* Comparison Table View */}
                      {msg.data.comparison_table && msg.data.comparison_table.length > 0 && (
                        <div className="bg-white border border-gray-200 rounded-xl overflow-hidden shadow-sm">
                          <table className="w-full text-xs text-left">
                            <thead className="bg-slate-100 border-b border-gray-200 text-gray-700">
                              <tr>
                                <th className="p-2 font-bold">Metric</th>
                                <th className="p-2 font-bold text-brand-700">{msg.data.company_1?.name || 'Company A'}</th>
                                <th className="p-2 font-bold text-indigo-700">{msg.data.company_2?.name || 'Company B'}</th>
                              </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                              {msg.data.comparison_table.map((row, idx) => (
                                <tr key={idx} className="hover:bg-slate-50">
                                  <td className="p-2 font-medium text-gray-600">{row.metric}</td>
                                  <td className="p-2 font-semibold text-gray-900">{row.c1}</td>
                                  <td className="p-2 font-semibold text-gray-900">{row.c2}</td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      )}

                      {/* Disclaimer footer box */}
                      {msg.data.disclaimer && (
                        <div className="text-[10px] text-gray-500 bg-amber-50/80 border border-amber-200 p-2 rounded-lg leading-tight">
                          ℹ️ {msg.data.disclaimer}
                        </div>
                      )}
                    </div>
                  )}

                  <span className="text-[10px] text-gray-400 px-1">
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-3 items-center">
                <div className="w-8 h-8 rounded-full bg-emerald-600 flex items-center justify-center text-white shadow-md">
                  <Bot className="w-4 h-4" />
                </div>
                <div className="bg-gray-100 rounded-2xl px-4 py-2 text-xs text-gray-500 animate-pulse">
                  Analyzing market metrics and financial reports…
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Chat Input */}
          <div className="border-t border-gray-100 p-3 bg-white">
            <div className="flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSend(input)}
                placeholder="Ask about a stock, company, market or financial metric (e.g. 'Analyze TCS', 'Compare TCS and Infosys')…"
                className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-xs focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                disabled={loading}
              />
              <button
                onClick={() => handleSend(input)}
                disabled={loading || !input.trim()}
                className="px-4 py-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 text-white rounded-xl flex items-center justify-center transition-colors shadow-sm font-semibold text-xs gap-1"
              >
                <span>Send</span>
                <Send className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        {/* Right Sidebar: Suggested Prompts & Quick Guide */}
        <div className="col-span-12 lg:col-span-4 space-y-4">
          {/* Prompts Panel */}
          <div className="card p-4 space-y-3">
            <div className="flex items-center gap-2 text-xs font-bold text-gray-800 border-b border-gray-100 pb-2">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              Suggested Stock Prompts
            </div>
            <div className="space-y-1.5">
              {SUGGESTED_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleSend(prompt)}
                  disabled={loading}
                  className="w-full text-left text-xs text-gray-700 bg-gray-50 hover:bg-emerald-50 hover:text-emerald-800 border border-gray-200/60 hover:border-emerald-300 rounded-xl px-3 py-2 transition-all flex items-center justify-between group"
                >
                  <span className="truncate">{prompt}</span>
                  <ArrowUpRight className="w-3 h-3 text-gray-400 group-hover:text-emerald-600 flex-shrink-0" />
                </button>
              ))}
            </div>
          </div>

          {/* Educational Quick Guide */}
          <div className="card p-4 space-y-2 bg-gradient-to-br from-slate-900 to-slate-800 text-white">
            <div className="flex items-center gap-2 text-xs font-bold text-emerald-400">
              <HelpCircle className="w-4 h-4" />
              Supported Indian Companies
            </div>
            <p className="text-[11px] text-gray-300 leading-relaxed">
              TCS, Infosys, Reliance Industries, HDFC Bank, ICICI Bank, ITC, Wipro, HCLTech, Larsen & Toubro, Bharti Airtel.
            </p>
            <div className="pt-2 border-t border-gray-700/60 text-[10px] text-gray-400">
              ⚡ Safe Financial Engine: Provides neutral analytical summaries without investment advice.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
