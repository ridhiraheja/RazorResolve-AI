import { create } from 'zustand'

export interface CartItem {
  product_id: string
  name: string
  qty: number
  price: number
}

export interface CustomerInfo {
  id: string
  name: string
  email: string
}

interface CartStore {
  items: CartItem[]
  customer: CustomerInfo
  addItem: (item: { product_id: string; name: string; price: number; qty?: number }) => void
  removeItem: (product_id: string) => void
  updateQty: (product_id: string, qty: number) => void
  clearCart: () => void
  setItems: (items: CartItem[]) => void
  getTotal: () => number
}

export const useCartStore = create<CartStore>((set, get) => ({
  items: [
    {
      product_id: 'demo_prod_macbook',
      name: 'Apple MacBook Air M2',
      qty: 1,
      price: 114900,
    },
  ],
  customer: {
    id: 'cust_demo_aarav',
    name: 'Aarav Sharma',
    email: 'aarav.sharma@example.com',
  },
  addItem: (item) => {
    const existing = get().items.find((i) => i.product_id === item.product_id)
    if (existing) {
      set({
        items: get().items.map((i) =>
          i.product_id === item.product_id ? { ...i, qty: i.qty + (item.qty || 1) } : i
        ),
      })
    } else {
      set({
        items: [
          ...get().items,
          {
            product_id: item.product_id,
            name: item.name,
            price: item.price,
            qty: item.qty || 1,
          },
        ],
      })
    }
  },
  removeItem: (product_id) => {
    set({ items: get().items.filter((i) => i.product_id !== product_id) })
  },
  updateQty: (product_id, qty) => {
    if (qty <= 0) {
      get().removeItem(product_id)
    } else {
      set({
        items: get().items.map((i) => (i.product_id === product_id ? { ...i, qty } : i)),
      })
    }
  },
  clearCart: () => set({ items: [] }),
  setItems: (items) => set({ items }),
  getTotal: () => get().items.reduce((sum, item) => sum + item.price * item.qty, 0),
}))
