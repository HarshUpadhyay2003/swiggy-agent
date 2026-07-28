import React from 'react'
import { Flame, Zap, ShieldCheck, DollarSign, Calendar, Sparkles } from 'lucide-react'
import Card from '../ui/Card'
import Badge from '../ui/Badge'

export function NutritionSummary({ plan }) {
  const totalCost = plan?.total_cost || plan?.estimated_weekly_cost || 2450
  const avgCalories = plan?.avg_daily_calories || 1750
  const totalProtein = plan?.total_protein || 140
  const healthPercent = plan?.health_score_percent || 92
  const mealsCount = plan?.total_meals || 21

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
      {/* Estimated Weekly Cost */}
      <Card variant="glass" padding="sm" className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Est. Weekly Cost
          </span>
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-swiggy-500/15 text-swiggy-600">
            <DollarSign className="h-3.5 w-3.5" />
          </div>
        </div>
        <p className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100">
          ₹{totalCost}
        </p>
        <span className="text-[10px] text-slate-400">~₹{Math.round(totalCost / 7)}/day avg</span>
      </Card>

      {/* Avg Daily Calories */}
      <Card variant="glass" padding="sm" className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Daily Calories
          </span>
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-rose-500/15 text-rose-600">
            <Flame className="h-3.5 w-3.5" />
          </div>
        </div>
        <p className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100">
          {avgCalories} kcal
        </p>
        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">Balanced Energy</span>
      </Card>

      {/* Protein Target */}
      <Card variant="glass" padding="sm" className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Protein Target
          </span>
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-amber-500/15 text-amber-600">
            <Zap className="h-3.5 w-3.5" />
          </div>
        </div>
        <p className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100">
          {totalProtein}g / day
        </p>
        <span className="text-[10px] text-amber-600 dark:text-amber-400 font-medium">High Muscle Recovery</span>
      </Card>

      {/* Health Score */}
      <Card variant="glass" padding="sm" className="space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Health Score
          </span>
          <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-500/15 text-emerald-600">
            <ShieldCheck className="h-3.5 w-3.5" />
          </div>
        </div>
        <p className="font-serif text-xl font-bold text-slate-900 dark:text-slate-100">
          {healthPercent}% Optimal
        </p>
        <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-medium">AI Verified Curation</span>
      </Card>
    </div>
  )
}

export default NutritionSummary
