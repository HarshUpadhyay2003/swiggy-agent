import React from 'react'
import { Calendar, ChevronRight, Utensils } from 'lucide-react'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Badge from '../ui/Badge'

export function PlannerMessage({ plan }) {
  if (!plan) return null

  const days = plan.days || plan.weekly_plan || []
  const totalCost = plan.total_cost || plan.estimated_weekly_cost || 0

  return (
    <Card variant="glass" className="my-3 p-4 border-amber-200/60 bg-amber-50/40 dark:border-amber-900/40 dark:bg-amber-950/30">
      <div className="flex items-center justify-between pb-3 border-b border-amber-200/50 dark:border-amber-900/50">
        <div className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-500 text-white">
            <Calendar className="h-4 w-4" />
          </div>
          <div>
            <h4 className="font-serif font-bold text-sm text-slate-900 dark:text-slate-100">
              Weekly Meal Schedule Generated
            </h4>
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Tailored nutrition & balanced options
            </p>
          </div>
        </div>

        {totalCost > 0 && (
          <Badge variant="primary" size="sm">
            Est. ₹{totalCost}
          </Badge>
        )}
      </div>

      {days.length > 0 && (
        <div className="py-3 space-y-2">
          {days.slice(0, 3).map((day, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs py-1 px-2.5 rounded-lg bg-white/60 dark:bg-slate-900/60">
              <span className="font-semibold text-slate-700 dark:text-slate-300">
                {day.day || `Day ${idx + 1}`}
              </span>
              <span className="text-slate-500 dark:text-slate-400 truncate max-w-[200px]">
                {day.lunch?.name || day.dinner?.name || day.meals?.[0]?.name || 'Curated Meals'}
              </span>
            </div>
          ))}
          {days.length > 3 && (
            <p className="text-[11px] text-center text-slate-400 dark:text-slate-500 pt-1">
              + {days.length - 3} more days prepared
            </p>
          )}
        </div>
      )}

      <div className="pt-2 flex items-center justify-end">
        <Button variant="glass" size="sm" icon={ChevronRight} iconPosition="right">
          Review Full Planner
        </Button>
      </div>
    </Card>
  )
}

export default PlannerMessage
