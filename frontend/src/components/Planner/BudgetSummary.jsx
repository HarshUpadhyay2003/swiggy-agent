import React from 'react'

export function BudgetSummary({ budget = 3000, spent = 2450 }) {
  const percent = Math.min(100, Math.round((spent / budget) * 100))

  return (
    <div className="rounded-xl border border-slate-200/60 bg-white/60 p-3 dark:border-slate-800 dark:bg-slate-900/60 space-y-1.5">
      <div className="flex items-center justify-between text-xs font-semibold">
        <span className="text-slate-600 dark:text-slate-300">Weekly Budget Progress</span>
        <span className="text-swiggy-600 dark:text-swiggy-400">
          ₹{spent} / ₹{budget} ({percent}%)
        </span>
      </div>
      <div className="h-2 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
        <div
          className="h-full bg-swiggy-500 rounded-full transition-all duration-500"
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  )
}

export default BudgetSummary
