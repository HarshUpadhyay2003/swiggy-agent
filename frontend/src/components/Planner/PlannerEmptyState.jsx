import React from 'react'
import { Calendar, Sparkles, ArrowRight } from 'lucide-react'
import Chip from '../ui/Chip'

export function PlannerEmptyState({ onSelectPrompt }) {
  const promptChips = [
    'Healthy Week',
    'Weight Loss',
    'High Protein',
    'Vegetarian',
    'Family Meals',
    'Budget Meals',
  ]

  return (
    <div className="glass-panel rounded-3xl p-10 flex flex-col items-center justify-center text-center max-w-2xl mx-auto space-y-6 ambient-shadow border border-white/60 dark:border-slate-800 my-8">
      {/* Decorative Icon */}
      <div className="relative">
        <div className="w-20 h-20 rounded-3xl bg-gradient-to-tr from-swiggy-500 to-amber-500 text-white flex items-center justify-center shadow-lg shadow-swiggy-500/20">
          <Calendar className="h-10 w-10" />
        </div>
        <div className="absolute -top-1 -right-1 w-7 h-7 rounded-full bg-white dark:bg-slate-900 border border-amber-300 text-amber-500 flex items-center justify-center shadow-sm">
          <Sparkles className="h-4 w-4" />
        </div>
      </div>

      {/* Copy */}
      <div className="space-y-2">
        <h2 className="font-serif text-3xl font-bold text-slate-900 dark:text-slate-100">
          Generate your personalised weekly food journey
        </h2>
        <p className="text-sm sm:text-base text-slate-600 dark:text-slate-300 max-w-md mx-auto leading-relaxed font-sans">
          Let CraveAI curate a 7-day dining schedule tailored to your dietary goals, protein targets, and weekly budget limit.
        </p>
      </div>

      {/* Prompt Chips */}
      {onSelectPrompt && (
        <div className="flex flex-wrap justify-center gap-2 max-w-md">
          {promptChips.map((chip) => (
            <Chip
              key={chip}
              variant="default"
              size="sm"
              onClick={() => onSelectPrompt(`Create a ${chip.toLowerCase()} 7 day meal plan`)}
            >
              {chip}
            </Chip>
          ))}
        </div>
      )}

      {/* Primary CTA */}
      <button
        type="button"
        onClick={() => onSelectPrompt && onSelectPrompt('Create a 7 day weekly meal plan')}
        className="bg-swiggy-500 hover:bg-swiggy-600 text-white px-8 py-3.5 rounded-full font-bold text-sm shadow-lg shadow-swiggy-500/25 transition-all flex items-center gap-2 active:scale-95"
      >
        <span>Generate 7-Day Meal Plan</span>
        <ArrowRight className="h-4 w-4" />
      </button>
    </div>
  )
}

export default PlannerEmptyState
