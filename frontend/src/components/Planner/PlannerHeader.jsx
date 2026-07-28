import React from 'react'
import { Sparkles, ShieldCheck, DollarSign, ShoppingBag } from 'lucide-react'

export function PlannerHeader({ onAddAllToCart, onMakeHealthier, onOptimizeBudget }) {
  return (
    <div className="flex flex-col md:flex-row md:items-end justify-between mb-8 space-y-4 md:space-y-0">
      <div>
        <h1 className="font-serif text-3xl sm:text-4xl font-bold text-slate-900 dark:text-slate-100 mb-2">
          Weekly Curation
        </h1>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 max-w-md font-sans">
          Your personalized dining schedule, optimized for taste, health, and budget.
        </p>
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={onMakeHealthier}
          className="glass-panel px-4 py-2.5 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-800 transition-colors flex items-center gap-2 ambient-shadow"
        >
          <ShieldCheck className="h-4 w-4 text-emerald-600" />
          <span>Make it Healthier</span>
        </button>

        <button
          type="button"
          onClick={onOptimizeBudget}
          className="glass-panel px-4 py-2.5 rounded-full text-xs font-semibold text-slate-700 dark:text-slate-200 hover:bg-white dark:hover:bg-slate-800 transition-colors flex items-center gap-2 ambient-shadow"
        >
          <DollarSign className="h-4 w-4 text-amber-600" />
          <span>Optimize for Budget</span>
        </button>

        <button
          type="button"
          onClick={onAddAllToCart}
          className="bg-swiggy-500 text-white px-6 py-2.5 rounded-full text-xs font-bold shadow-sm hover:bg-swiggy-600 transition-colors flex items-center gap-2"
        >
          <ShoppingBag className="h-4 w-4" />
          <span>Add all to Cart</span>
        </button>
      </div>
    </div>
  )
}

export default PlannerHeader
