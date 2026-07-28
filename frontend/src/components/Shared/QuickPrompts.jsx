import React from 'react'
import { Sparkles } from 'lucide-react'
import Chip from '../ui/Chip'

export function QuickPrompts({ options = [], onSelect }) {
  const defaultPrompts = [
    'Repeat last order',
    'Healthy lunch under ₹300',
    'Weekend dinner',
    'Office lunch',
    'High protein',
    'Family meal',
    'Dessert',
    'Late night snacks',
  ]

  const promptList = options.length > 0 ? options : defaultPrompts

  return (
    <div className="rounded-2xl border border-slate-200/80 bg-white/80 p-4 shadow-gourmet backdrop-blur-xl dark:border-slate-800 dark:bg-slate-900/80 transition-colors duration-300">
      <div className="mb-3 flex items-center justify-between gap-4 px-1">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-swiggy-500" />
          <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500 dark:text-slate-400">
            Quick AI Prompt Shortcuts
          </p>
        </div>
        <span className="text-xs text-slate-400 dark:text-slate-500 hidden sm:inline">
          Tap to run query
        </span>
      </div>

      <div className="flex items-center gap-2.5 overflow-x-auto pb-1.5 scrollbar-thin">
        {promptList.map((promptText) => (
          <Chip
            key={promptText}
            variant="default"
            size="md"
            onClick={() => onSelect(promptText)}
            className="hover:border-swiggy-500 hover:text-swiggy-700 dark:hover:text-swiggy-400 shrink-0"
          >
            {promptText}
          </Chip>
        ))}
      </div>
    </div>
  )
}

export default QuickPrompts
