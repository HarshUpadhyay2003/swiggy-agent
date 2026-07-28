import React, { useState } from 'react'
import { Sparkles, ShoppingBag, HelpCircle, Check } from 'lucide-react'
import Button from '../ui/Button'

export function MealActions({ meal, onAdd, onToggleWhyThis }) {
  const [added, setAdded] = useState(false)

  const handleAdd = () => {
    onAdd && onAdd(meal)
    setAdded(true)
    setTimeout(() => setAdded(false), 1800)
  }

  return (
    <div className="flex items-center gap-1.5 pt-2 border-t border-slate-200/50 dark:border-slate-800">
      <Button
        variant={added ? 'accent' : 'primary'}
        size="sm"
        icon={added ? Check : ShoppingBag}
        onClick={handleAdd}
        className="flex-1 text-xs"
      >
        {added ? 'Added' : 'Add to Cart'}
      </Button>

      <button
        type="button"
        onClick={onToggleWhyThis}
        className="p-1.5 text-slate-400 hover:text-swiggy-500 transition-colors rounded-full"
        title="Why this meal? AI breakdown"
      >
        <HelpCircle className="h-4 w-4" />
      </button>
    </div>
  )
}

export default MealActions
