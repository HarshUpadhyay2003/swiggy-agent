import React from 'react'
import { Star, Clock, Flame, Zap, ShieldCheck } from 'lucide-react'

export function RecommendationMeta({
  name = 'Gourmet Dish',
  restaurantName = 'Swiggy Kitchen',
  cuisine = 'Gourmet',
  rating = 4.7,
  deliveryTime = '25 mins',
  calories = null,
  protein = null,
  healthScore = null,
  reason = '',
}) {
  return (
    <div className="space-y-2.5">
      {/* Title & Restaurant */}
      <div>
        <div className="flex items-center justify-between gap-2">
          <h3 className="font-serif font-bold text-lg md:text-xl text-slate-950 dark:text-slate-50 leading-tight group-hover:text-swiggy-600 dark:group-hover:text-swiggy-400 transition-colors">
            {name}
          </h3>
        </div>
        <p className="text-xs font-medium text-slate-500 dark:text-slate-400">
          {restaurantName} • <span className="italic">{cuisine}</span>
        </p>
      </div>

      {/* Meta Stats: Rating, ETA, Nutrition */}
      <div className="flex flex-wrap items-center gap-3 text-xs text-slate-600 dark:text-slate-300">
        <div className="flex items-center gap-1 font-bold text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/40 px-2 py-0.5 rounded-full">
          <Star className="h-3.5 w-3.5 fill-current" />
          <span>{rating || 4.5}</span>
        </div>

        <div className="flex items-center gap-1">
          <Clock className="h-3.5 w-3.5 text-slate-400" />
          <span>{deliveryTime || '25-30 mins'}</span>
        </div>

        {calories && (
          <div className="flex items-center gap-1">
            <Flame className="h-3.5 w-3.5 text-rose-500" />
            <span>{calories} kcal</span>
          </div>
        )}

        {protein && (
          <div className="flex items-center gap-1">
            <Zap className="h-3.5 w-3.5 text-amber-500" />
            <span>{protein}g protein</span>
          </div>
        )}

        {healthScore && (
          <div className="flex items-center gap-1">
            <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" />
            <span>Health {healthScore}/10</span>
          </div>
        )}
      </div>

      {/* Reason snippet */}
      {reason && (
        <p className="text-xs text-slate-600 dark:text-slate-300 bg-slate-50 dark:bg-slate-800/60 p-2.5 rounded-xl italic line-clamp-2 border border-slate-200/50 dark:border-slate-700/50">
          "{reason}"
        </p>
      )}
    </div>
  )
}

export default RecommendationMeta
