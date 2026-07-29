import React, { useState, useEffect } from 'react'
import { ShoppingBag, ShieldCheck, DollarSign } from 'lucide-react'

export function StickyPlannerBar({ normalizedPlanner, onAddAllToCart, onMakeHealthier, onOptimizeBudget }) {
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 220) {
        setIsVisible(true)
      } else {
        setIsVisible(false)
      }
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  if (!normalizedPlanner || !isVisible) return null

  const totalCost = normalizedPlanner.budget?.total_estimated_cost || 0
  const days = normalizedPlanner.days || []
  let totalMeals = 0
  days.forEach((day) => {
    totalMeals += (day.meals || []).length
  })

  return (
    <div className="fixed top-16 left-0 right-0 z-40 px-4 md:px-8 py-2.5 bg-white/90 dark:bg-slate-900/90 backdrop-blur-xl border-b border-slate-200/80 dark:border-slate-800 shadow-md transition-all duration-300 animate-slideDown">
      <div className="max-w-[1440px] mx-auto flex items-center justify-between">
        {/* Compact Title & Cost */}
        <div className="flex items-center gap-4">
          <div>
            <h4 className="font-serif text-base font-bold text-slate-900 dark:text-slate-100 leading-tight">
              Weekly Curation
            </h4>
            <div className="flex items-center gap-3 text-xs text-slate-500 dark:text-slate-400 font-medium">
              <span className="font-semibold text-slate-900 dark:text-slate-100">₹{totalCost.toLocaleString('en-IN')}</span>
              <span>•</span>
              <span>{totalMeals || 21} Meals</span>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onMakeHealthier}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold glass-panel hover:bg-white text-slate-700 dark:text-slate-200 transition-colors"
          >
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
            <span>Healthier</span>
          </button>
          <button
            type="button"
            onClick={onOptimizeBudget}
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-semibold glass-panel hover:bg-white text-slate-700 dark:text-slate-200 transition-colors"
          >
            <DollarSign className="h-3.5 w-3.5 text-amber-600" />
            <span>Budget</span>
          </button>
          <button
            type="button"
            onClick={onAddAllToCart}
            className="bg-swiggy-500 hover:bg-swiggy-600 text-white px-4 py-1.5 rounded-full text-xs font-bold shadow-sm transition-colors flex items-center gap-1.5"
          >
            <ShoppingBag className="h-3.5 w-3.5" />
            <span>Add All</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default StickyPlannerBar
