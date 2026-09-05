import { useEffect, useState } from 'react'
import { getProducts } from '@/lib/api'
import { formatINR, cn } from '@/lib/utils'
import { Star, Package, TrendingUp } from 'lucide-react'

interface Product {
  id: string; name: string; category: string; price: number; brand: string
  rating: number; review_count: number; stock: number
  popularity_score: number; conversion_rate: number; tags: string[]
}

const CATEGORIES = ['all', 'electronics', 'fashion', 'home', 'sports', 'books', 'beauty']

export default function Products() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [cat, setCat] = useState('all')

  useEffect(() => {
    setLoading(true)
    const params: Record<string, string> = {}
    if (cat !== 'all') params.category = cat
    getProducts(params).then(r => setProducts(r.data.products)).finally(() => setLoading(false))
  }, [cat])

  return (
    <div className="space-y-4">
      {/* Category filter */}
      <div className="card px-4 py-3 flex items-center gap-3 flex-wrap">
        <Package className="w-4 h-4 text-gray-400" />
        <span className="text-sm text-gray-600 font-medium">{products.length} products</span>
        <div className="flex items-center gap-2 ml-auto flex-wrap">
          {CATEGORIES.map(c => (
            <button
              key={c}
              onClick={() => setCat(c)}
              className={cn('px-3 py-1 rounded-full text-xs font-medium transition-colors capitalize', cat === c ? 'bg-brand-500 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200')}
            >
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Grid */}
      {loading ? (
        <div className="text-center py-12 text-gray-400 animate-pulse">Loading products…</div>
      ) : (
        <div className="grid grid-cols-4 gap-4">
          {products.map(p => {
            const discount = p.price * 1.2 > p.price ? Math.round((1 - p.price / (p.price * 1.2)) * 0) : 0
            return (
              <div key={p.id} className="card p-4 hover:shadow-md transition-shadow">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400 capitalize">{p.category}</span>
                  <span className="text-xs text-gray-500">{p.brand}</span>
                </div>
                <h3 className="text-sm font-semibold text-gray-900 leading-tight mb-2 line-clamp-2">{p.name}</h3>
                <div className="text-xl font-bold text-gray-900 mb-2">{formatINR(p.price)}</div>

                <div className="flex items-center gap-1 text-xs text-gray-500 mb-3">
                  <Star className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                  <span className="font-medium">{p.rating}</span>
                  <span>({p.review_count.toLocaleString()})</span>
                </div>

                <div className="space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">Popularity</span>
                    <span className="font-medium text-gray-700">{Math.round(p.popularity_score * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div className="bg-brand-500 h-1.5 rounded-full" style={{ width: `${p.popularity_score * 100}%` }} />
                  </div>

                  <div className="flex items-center justify-between text-xs">
                    <span className="text-gray-400">Conversion</span>
                    <span className="font-medium text-green-700">{Math.round(p.conversion_rate * 100)}%</span>
                  </div>
                  <div className="w-full bg-gray-100 rounded-full h-1.5">
                    <div className="bg-green-500 h-1.5 rounded-full" style={{ width: `${p.conversion_rate * 100}%` }} />
                  </div>
                </div>

                <div className="mt-3 flex flex-wrap gap-1">
                  {p.tags.slice(0, 3).map(t => (
                    <span key={t} className="text-xs px-1.5 py-0.5 bg-gray-100 text-gray-500 rounded">{t}</span>
                  ))}
                </div>

                <div className="mt-3 flex items-center gap-2 text-xs">
                  <TrendingUp className="w-3 h-3 text-green-500" />
                  <span className="text-gray-500">{p.stock} in stock</span>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
