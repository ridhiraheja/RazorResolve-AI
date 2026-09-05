import { useCartStore } from '@/store/useCartStore'
import { formatINR, cn } from '@/lib/utils'
import { ShoppingBag, X, Plus, Minus, Trash2, ArrowRight } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

interface CartDrawerProps {
  isOpen: boolean
  onClose: () => void
}

export default function CartDrawer({ isOpen, onClose }: CartDrawerProps) {
  const { items, updateQty, removeItem, getTotal, clearCart } = useCartStore()
  const navigate = useNavigate()

  if (!isOpen) return null

  const subtotal = getTotal()

  const handleCheckout = () => {
    onClose()
    navigate('/checkout')
  }

  return (
    <div className="fixed inset-0 z-50 overflow-hidden animate-fadeIn">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />

      <div className="fixed inset-y-0 right-0 max-w-full flex pl-10">
        <div className="w-screen max-w-md bg-white shadow-2xl flex flex-col">
          {/* Header */}
          <div className="p-4 bg-slate-900 text-white flex items-center justify-between">
            <div className="flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-emerald-400" />
              <h2 className="font-bold text-base tracking-tight">Your Shopping Cart</h2>
              <span className="bg-emerald-500/20 text-emerald-300 text-xs px-2 py-0.5 rounded-full font-semibold border border-emerald-500/30">
                {items.length} {items.length === 1 ? 'item' : 'items'}
              </span>
            </div>
            <button
              onClick={onClose}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
              title="Close Cart"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Cart Items List */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-slate-50/50">
            {items.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-center p-6 space-y-4">
                <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center text-gray-400">
                  <ShoppingBag className="w-8 h-8" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-gray-900">Your cart is empty</h3>
                  <p className="text-xs text-gray-500 mt-1 max-w-xs">
                    Looks like you haven't added any products to your shopping cart yet.
                  </p>
                </div>
                <button
                  onClick={() => {
                    onClose()
                    navigate('/shopping')
                  }}
                  className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 text-white text-xs font-bold rounded-xl transition-all shadow-md"
                >
                  Continue Shopping
                </button>
              </div>
            ) : (
              items.map((item) => (
                <div
                  key={item.product_id}
                  className="bg-white border border-gray-200 rounded-xl p-3.5 shadow-sm space-y-3 transition-all hover:border-gray-300"
                >
                  <div className="flex justify-between items-start">
                    <div className="flex-1 pr-2">
                      <h4 className="text-xs font-bold text-gray-900 leading-snug line-clamp-2">
                        {item.name}
                      </h4>
                      <span className="text-[11px] font-semibold text-brand-700 block mt-0.5">
                        {formatINR(item.price)} each
                      </span>
                    </div>
                    <button
                      onClick={() => removeItem(item.product_id)}
                      className="p-1 text-gray-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                      title="Remove Item"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="flex items-center justify-between pt-2 border-t border-gray-100 text-xs">
                    {/* Quantity controls */}
                    <div className="flex items-center gap-2 bg-gray-100 p-1 rounded-lg border border-gray-200">
                      <button
                        onClick={() => updateQty(item.product_id, Math.max(1, item.qty - 1))}
                        disabled={item.qty <= 1}
                        className="w-6 h-6 rounded bg-white hover:bg-gray-200 disabled:opacity-40 text-gray-700 flex items-center justify-center font-bold text-xs shadow-sm transition-colors"
                        title="Decrease Quantity"
                      >
                        <Minus className="w-3 h-3" />
                      </button>
                      <span className="w-6 text-center font-bold text-gray-900 text-xs">
                        {item.qty}
                      </span>
                      <button
                        onClick={() => updateQty(item.product_id, item.qty + 1)}
                        className="w-6 h-6 rounded bg-white hover:bg-gray-200 text-gray-700 flex items-center justify-center font-bold text-xs shadow-sm transition-colors"
                        title="Increase Quantity"
                      >
                        <Plus className="w-3 h-3" />
                      </button>
                    </div>

                    {/* Total item cost */}
                    <div className="text-right">
                      <span className="text-[10px] text-gray-400 block">Item Total</span>
                      <span className="font-bold text-gray-900 text-sm">
                        {formatINR(item.price * item.qty)}
                      </span>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer Actions */}
          {items.length > 0 && (
            <div className="p-4 bg-white border-t border-gray-200 space-y-3">
              <div className="space-y-1 text-xs">
                <div className="flex justify-between text-gray-500">
                  <span>Subtotal</span>
                  <span>{formatINR(subtotal)}</span>
                </div>
                <div className="flex justify-between text-gray-500">
                  <span>Shipping & Delivery</span>
                  <span className="text-emerald-600 font-medium">FREE</span>
                </div>
                <div className="flex justify-between text-sm font-bold text-gray-900 pt-2 border-t border-gray-100">
                  <span>Total Amount</span>
                  <span className="text-brand-600 text-base">{formatINR(subtotal)}</span>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2 pt-1">
                <button
                  onClick={() => {
                    onClose()
                    navigate('/shopping')
                  }}
                  className="py-2.5 px-3 bg-gray-100 hover:bg-gray-200 text-gray-800 font-bold text-xs rounded-xl transition-colors text-center"
                >
                  Continue Shopping
                </button>

                <button
                  onClick={handleCheckout}
                  className="py-2.5 px-3 bg-brand-600 hover:bg-brand-700 text-white font-bold text-xs rounded-xl transition-all shadow-md flex items-center justify-center gap-1"
                >
                  <span>Checkout</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
