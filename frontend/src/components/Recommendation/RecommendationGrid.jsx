import React from 'react'
import { Utensils } from 'lucide-react'
import RecommendationCard from './RecommendationCard'
import RecommendationSkeleton from './RecommendationSkeleton'
import Chip from '../ui/Chip'

export function RecommendationGrid({ items = [], loading = false, onAdd, onReplace, onRemove, onSelectPrompt }) {
  const promptChips = [
    'Healthy',
    'Comfort Food',
    'High Protein',
    'Breakfast',
    'Dinner',
    'Budget Meals',
  ]

  if (loading) {
    return (
      <div className="flex gap-6 overflow-x-auto hide-scrollbar pb-6 pt-2">
        <RecommendationSkeleton />
        <RecommendationSkeleton />
      </div>
    )
  }

  if (!items || items.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center text-center p-8 rounded-2xl border border-dashed border-slate-300 dark:border-slate-800 bg-white/40 dark:bg-slate-900/40 space-y-4">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-swiggy-500/15 text-swiggy-600 dark:text-swiggy-400">
          <Utensils className="h-6 w-6" />
        </div>

        <div className="space-y-1 max-w-sm">
          <h4 className="font-serif font-bold text-lg text-slate-900 dark:text-slate-100">
            No recommendations yet
          </h4>
          <p className="text-xs text-slate-500 dark:text-slate-400">
            Ask CraveAI for dish suggestions or select a topic below to generate curated options.
          </p>
        </div>

        {onSelectPrompt && (
          <div className="flex flex-wrap justify-center gap-2 pt-2">
            {promptChips.map((chip) => (
              <Chip
                key={chip}
                variant="default"
                size="sm"
                onClick={() => onSelectPrompt(`Suggest ${chip.toLowerCase()} options`)}
              >
                {chip}
              </Chip>
            ))}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="w-full flex gap-6 overflow-x-auto scrollbar-thin pb-6 pt-2 snap-x snap-mandatory">
      {items.map((item, index) => (
        <div key={item.id || index} className="snap-start shrink-0 w-full sm:w-[320px] md:w-[340px]">
          <RecommendationCard
            item={item}
            index={index}
            onAdd={onAdd}
            onReplace={onReplace}
            onRemove={onRemove}
          />
        </div>
      ))}
    </div>
  )
}

export default RecommendationGrid
