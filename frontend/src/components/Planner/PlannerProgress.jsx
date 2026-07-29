import React from 'react'
import { CheckCircle2 } from 'lucide-react'

export function PlannerProgress({ days = [] }) {
  let plannedCount = 0
  const totalTarget = days.length * 3

  days.forEach((day) => {
    plannedCount += (day.meals || []).length
  })

  const target = totalTarget || 21
  const percentage = Math.min(100, Math.round((plannedCount / target) * 100))

  return (
    <div className="w-full glass-panel rounded-xl p-3 mb-6 border border-slate-200/60 dark:border-slate-800 flex items-center justify-between gap-4">
      <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 dark:text-slate-200 shrink-0">
        <CheckCircle2 className="h-4 w-4 text-emerald-600" />
        <span>Planning Complete</span>
        <span className="text-slate-400">({plannedCount} / {target} Meals)</span>
      </div>

      <div className="flex-1 flex items-center gap-3 max-w-md">
        <div className="h-2 w-full bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
          <div
            className="h-full bg-emerald-500 rounded-full transition-all duration-500"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <span className="text-xs font-bold text-emerald-600 dark:text-emerald-400 shrink-0">
          {percentage}%
        </span>
      </div>
    </div>
  )
}

export default PlannerProgress
