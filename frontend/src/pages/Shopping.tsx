import { useState, useRef, useEffect } from 'react'
import { getRecommendations, getProducts } from '@/lib/api'
import { formatINR, cn } from '@/lib/utils'
import { Send, Bot, ShoppingBag, Star } from 'lucide-react'

interface Product {
  id: string
  name: string
  category: string
  price: number
  original_price: number
  brand: string
  rating: number
  review_count: number
  popularity_score: number
  tags: string[]
  relevance_score?: number
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  text?: string
  products?: Product[]
  explanation?: string
  timestamp: Date
}

const SAMPLE_QUERIES = [
  'I need a laptop under ₹70,000 for coding',
  'Which phone has the best battery?',
  'Show me budget headphones under ₹2,000',
  'Best camera for travel photography?',
  'Something similar but cheaper to the MacBook',
  'Gaming laptop with good GPU',
]

import { useNavigate } from 'react-router-dom'
import { useCartStore } from '@/store/useCartStore'

function ProductCard({ p, onOpenCart }: { p: Product; onOpenCart: () => void }) {
  const navigate = useNavigate()
  const addItem = useCartStore((s) => s.addItem)
  const discount = p.original_price && p.original_price > p.price
    ? Math.round((1 - p.price / p.original_price) * 100)
    : null

  const handleAddToCart = () => {
    addItem({ product_id: p.id, name: p.name, price: p.price, qty: 1 })
    onOpenCart()
  }

  const handleAddAndCheckout = () => {
    addItem({ product_id: p.id, name: p.name, price: p.price, qty: 1 })
    navigate('/checkout')
  }

  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 w-52 flex-shrink-0 flex flex-col justify-between shadow-sm hover:border-brand-300 transition-all">
      <div>
        <div className="text-xs text-gray-400 mb-1 capitalize">{p.category} · {p.brand}</div>
        <div className="text-sm font-semibold text-gray-900 leading-tight line-clamp-2 mb-2">{p.name}</div>
        <div className="flex items-baseline gap-1.5 mb-1">
          <span className="text-lg font-bold text-gray-900">{formatINR(p.price)}</span>
          {discount && discount > 0 && (
            <span className="text-xs text-green-600 font-medium">-{discount}%</span>
          )}
        </div>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
          <span className="font-medium">{p.rating}</span>
          <span>({p.review_count.toLocaleString()})</span>
        </div>
        {p.relevance_score != null && (
          <div className="mt-2 text-xs text-brand-600 font-medium">
            {Math.round(p.relevance_score * 100)}% match
          </div>
        )}
      </div>

      <div className="grid grid-cols-2 gap-1.5 mt-3">
        <button
          onClick={handleAddToCart}
          className="py-1.5 px-2 bg-gray-100 hover:bg-gray-200 text-gray-800 text-[11px] font-bold rounded-lg transition-colors text-center truncate"
          title="Add to Cart"
        >
          + Add
        </button>

        <button
          onClick={handleAddAndCheckout}
          className="py-1.5 px-2 bg-brand-600 hover:bg-brand-700 text-white text-[11px] font-bold rounded-lg transition-colors shadow-sm text-center truncate"
          title="Buy Now"
        >
          Buy Now →
        </button>
      </div>
    </div>
  )
}

import CartDrawer from '@/components/cart/CartDrawer'

export default function Shopping() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0', role: 'assistant',
      text: "Hi! I'm your AI shopping assistant. Tell me what you're looking for — I'll find the best products for you.\n\nTry asking things like: \"laptop under ₹70,000 for coding\" or \"best camera for travel\".",
      timestamp: new Date(),
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [isCartOpen, setIsCartOpen] = useState(false)
  const endRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (query: string) => {
    if (!query.trim() || loading) return
    const userMsg: Message = { id: Date.now().toString(), role: 'user', text: query, timestamp: new Date() }
    setMessages(ms => [...ms, userMsg])
    setInput('')
    setLoading(true)

    try {
      const resp = await getRecommendations(query, 6)
      const data = resp.data
      const aiMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        products: data.recommendations,
        explanation: data.explanation,
        text: data.recommendations.length > 0 ? undefined : "I couldn't find specific products for that query. Try being more specific about category or budget.",
        timestamp: new Date(),
      }
      setMessages(ms => [...ms, aiMsg])
    } catch {
      setMessages(ms => [...ms, {
        id: (Date.now() + 1).toString(), role: 'assistant',
        text: 'Sorry, something went wrong. Please try again.',
        timestamp: new Date(),
      }])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex gap-4 h-[calc(100vh-10rem)]">
      {/* Chat */}
      <div className="flex flex-col flex-1 card overflow-hidden">
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map(msg => (
            <div key={msg.id} className={cn('flex gap-3', msg.role === 'user' ? 'flex-row-reverse' : 'flex-row')}>
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div className={cn('max-w-xl', msg.role === 'user' ? 'items-end' : 'items-start', 'flex flex-col gap-1.5')}>
                {msg.text && (
                  <div className={cn('px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-line',
                    msg.role === 'user'
                      ? 'bg-brand-500 text-white rounded-tr-sm'
                      : 'bg-gray-100 text-gray-800 rounded-tl-sm'
                  )}>
                    {msg.text}
                  </div>
                )}
                {msg.explanation && (
                  <div className="text-xs text-gray-500 px-1">{msg.explanation}</div>
                )}
                {msg.products && msg.products.length > 0 && (
                  <div className="flex gap-3 overflow-x-auto pb-2 max-w-full">
                    {msg.products.map(p => <ProductCard key={p.id} p={p} onOpenCart={() => setIsCartOpen(true)} />)}
                  </div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="flex gap-3">
              <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-white" />
              </div>
              <div className="bg-gray-100 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-gray-500 animate-pulse">
                Finding the best products for you…
              </div>
            </div>
          )}
          <div ref={endRef} />
        </div>

        {/* Input */}
        <div className="border-t border-gray-100 p-4">
          <div className="flex gap-2">
            <input
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && send(input)}
              placeholder="Ask me anything — 'laptop under ₹70,000 for coding'…"
              className="flex-1 border border-gray-200 rounded-xl px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              disabled={loading}
            />
            <button
              onClick={() => send(input)}
              disabled={loading || !input.trim()}
              className="w-10 h-10 bg-brand-500 hover:bg-brand-600 disabled:opacity-50 text-white rounded-xl flex items-center justify-center transition-colors"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Suggestion panel */}
      <div className="w-56 flex flex-col gap-3">
        <div className="card p-4">
          <div className="flex items-center gap-2 text-sm font-semibold text-gray-800 mb-3">
            <ShoppingBag className="w-4 h-4 text-brand-500" />
            Try asking…
          </div>
          <div className="space-y-2">
            {SAMPLE_QUERIES.map(q => (
              <button
                key={q}
                onClick={() => send(q)}
                disabled={loading}
                className="w-full text-left text-xs text-gray-600 bg-gray-50 hover:bg-brand-50 hover:text-brand-700 border border-gray-100 hover:border-brand-200 rounded-lg px-3 py-2 transition-colors"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Cart Drawer */}
      <CartDrawer isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </div>
  )
}
