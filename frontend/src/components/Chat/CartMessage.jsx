import React from 'react'
import { CheckCircle2, ShoppingBag, ArrowRight } from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Badge from '../ui/Badge'
import { useAppState } from '../../store/AppStore'

export function CartMessage({ cartActionData }) {
  const { cart } = useAppState()

  const items = cartActionData?.items || cart?.items || []
  const total = cartActionData?.total || cart?.total || 0

  return (
    <Card variant="glass" className="my-3 p-4 border-emerald-200/60 bg-emerald-50/40 dark:border-emerald-900/40 dark:bg-emerald-950/30">
      <div className="flex items-center justify-between pb-2">
        <div className="flex items-center gap-2">
          <CheckCircle2 className="h-5 w-5 text-emerald-600 dark:text-emerald-400 animate-bounce" />
          <h4 className="font-serif font-bold text-sm text-slate-900 dark:text-slate-100">
            Item Added to Cart
          </h4>
        </div>
        <Badge variant="success" size="sm">
          Updated
        </Badge>
      </div>

      <div className="py-2 text-xs space-y-1 text-slate-600 dark:text-slate-300">
        <div className="flex justify-between font-semibold">
          <span>Active Cart Total:</span>
          <span>₹{total}</span>
        </div>
        <p className="text-[11px] text-slate-500">
          {items.length} {items.length === 1 ? 'item' : 'items'} in your cart ready for checkout.
        </p>
      </div>
    </Card>
  )
}

export default CartMessage
