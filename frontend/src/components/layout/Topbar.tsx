import { useState } from 'react'
import { Bell, RefreshCw, ShoppingBag } from 'lucide-react'
import { useCartStore } from '@/store/useCartStore'
import CartDrawer from '@/components/cart/CartDrawer'

interface TopbarProps {
  title: string
  subtitle?: string
  onRefresh?: () => void
}

export default function Topbar({ title, subtitle, onRefresh }: TopbarProps) {
  const [isCartOpen, setIsCartOpen] = useState(false)
  const items = useCartStore((s) => s.items)

  const totalCartCount = items.reduce((acc, i) => acc + i.qty, 0)

  return (
    <>
      <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-6 flex-shrink-0">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">{title}</h1>
          {subtitle && <p className="text-xs text-gray-500">{subtitle}</p>}
        </div>
        <div className="flex items-center gap-3">
          {/* Cart Button */}
          <button
            onClick={() => setIsCartOpen(true)}
            className="relative p-2 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors flex items-center gap-1.5 border border-gray-200"
            title="View Shopping Cart"
          >
            <ShoppingBag className="w-4 h-4 text-brand-600" />
            <span className="text-xs font-bold text-gray-800">Cart</span>
            {totalCartCount > 0 && (
              <span className="ml-0.5 bg-brand-600 text-white text-[10px] font-bold px-1.5 py-0.2 rounded-full min-w-[18px] text-center">
                {totalCartCount}
              </span>
            )}
          </button>

          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors"
              title="Refresh Page Data"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}

          <div className="relative">
            <button className="p-2 rounded-lg text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition-colors">
              <Bell className="w-4 h-4" />
            </button>
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full" />
          </div>

          <div className="w-8 h-8 rounded-full bg-brand-500 flex items-center justify-center text-white text-sm font-bold shadow-sm">
            A
          </div>
        </div>
      </header>

      {/* Cart Drawer */}
      <CartDrawer isOpen={isCartOpen} onClose={() => setIsCartOpen(false)} />
    </>
  )
}
