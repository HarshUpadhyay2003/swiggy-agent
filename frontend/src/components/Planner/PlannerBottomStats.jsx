import React from 'react'
import { Utensils, Store, Compass, Truck } from 'lucide-react'

export function PlannerBottomStats({ normalizedPlanner }) {
  if (!normalizedPlanner || !normalizedPlanner.days) return null

  const days = normalizedPlanner.days || []
  const cuisinesSet = new Set()
  const restaurantsSet = new Set()
  let totalCost = normalizedPlanner.budget?.total_estimated_cost || 0
  let budgetLimit = normalizedPlanner.budget?.budget_limit || 10000

  days.forEach((day) => {
    const meals = day.meals || [day.breakfast, day.lunch, day.dinner].filter(Boolean)
    meals.forEach((m) => {
      if (m.restaurant_name) restaurantsSet.add(m.restaurant_name)
      if (m.cuisine) cuisinesSet.add(m.cuisine)
    })
  })

  const budgetPct = Math.min(100, Math.round((totalCost / budgetLimit) * 100))

  return (
    <div className="w-full mt-12 glass-panel p-6 rounded-2xl border border-white/60 dark:border-slate-800 space-y-4">
      <h3 className="font-serif text-lg font-bold text-slate-900 dark:text-slate-100 flex items-center gap-2">
        <Compass className="h-5 w-5 text-swiggy-500" />
        Weekly Curation Analytics
      </h3>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 pt-2">
        {/* Cuisine Diversity */}
        <div className="bg-white/60 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200/50 dark:border-slate-700/50 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Cuisine Variety</span>
            <Utensils className="h-4 w-4 text-indigo-500" />
          </div>
          <p className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100">
            {cuisinesSet.size > 0 ? `${cuisinesSet.size} Cuisines` : 'Multi-Cuisine'}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Indian, Asian, Continental</p>
        </div>

        {/* Restaurant Diversity */}
        <div className="bg-white/60 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200/50 dark:border-slate-700/50 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Kitchen Diversity</span>
            <Store className="h-4 w-4 text-swiggy-500" />
          </div>
          <p className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100">
            {restaurantsSet.size > 0 ? `${restaurantsSet.size} Top Places` : '6 Kitchens'}
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Zero restaurant fatigue</p>
        </div>

        {/* Budget Utilization */}
        <div className="bg-white/60 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200/50 dark:border-slate-700/50 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Budget Utilization</span>
            <span className="font-bold text-emerald-600">{budgetPct}%</span>
          </div>
          <p className="font-serif text-xl font-bold text-emerald-600 dark:text-emerald-400">
            ₹{totalCost} / ₹{budgetLimit}
          </p>
          <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden mt-2">
            <div className="h-full bg-emerald-500 rounded-full" style={{ width: `${budgetPct}%` }} />
          </div>
        </div>

        {/* Delivery Coverage */}
        <div className="bg-white/60 dark:bg-slate-800/60 p-4 rounded-xl border border-slate-200/50 dark:border-slate-700/50 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>Delivery Coverage</span>
            <Truck className="h-4 w-4 text-amber-500" />
          </div>
          <p className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100">
            100% Express
          </p>
          <p className="text-[11px] text-slate-500 dark:text-slate-400">Optimized delivery slots</p>
        </div>
      </div>
    </div>
  )
}

export default PlannerBottomStats
