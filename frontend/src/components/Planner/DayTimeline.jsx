import React from 'react'

export function DayTimeline({ type = 'Breakfast' }) {
  const colorMap = {
    Breakfast: 'bg-amber-500 text-amber-950',
    Lunch: 'bg-swiggy-500 text-white',
    Dinner: 'bg-indigo-600 text-white',
    Snack: 'bg-emerald-500 text-white',
  }

  return (
    <div className="flex items-center gap-2 mb-1.5">
      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${colorMap[type] || 'bg-slate-700 text-white'}`}>
        {type}
      </span>
      <div className="h-px flex-1 bg-slate-200/80 dark:bg-slate-800" />
    </div>
  )
}

export default DayTimeline
