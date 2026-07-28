import React from 'react'
import Badge from '../ui/Badge'

export function PriceSection({ price = 240, originalPrice = null, discountLabel = null, className = '' }) {
  const finalOriginalPrice = originalPrice || (discountLabel ? Math.round(price * 1.25) : null)
  const savings = finalOriginalPrice ? finalOriginalPrice - price : 0

  return (
    <div className={`flex items-center gap-2 flex-wrap ${className}`}>
      <span className="font-sans text-xl font-bold text-slate-900 dark:text-slate-50 tracking-tight">
        ₹{price}
      </span>

      {finalOriginalPrice && finalOriginalPrice > price && (
        <span className="text-sm text-slate-400 dark:text-slate-500 line-through font-medium">
          ₹{finalOriginalPrice}
        </span>
      )}

      {savings > 0 && (
        <Badge variant="success" size="sm">
          Save ₹{savings}
        </Badge>
      )}
    </div>
  )
}

export default PriceSection
