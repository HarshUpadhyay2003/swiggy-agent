import React from 'react'

export function DaySelector({ days = [], activeDayIndex = 0, onSelectDay }) {
  const shortDays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

  return (
    <div className="w-full flex items-center justify-between gap-2 overflow-x-auto scrollbar-thin py-2 mb-4">
      <div className="flex items-center gap-2">
        {days.map((dayData, idx) => {
          const isSelected = activeDayIndex === idx
          const shortName = shortDays[idx] || dayData.day?.substring(0, 3) || `Day ${idx + 1}`

          return (
            <button
              key={dayData.day || idx}
              type="button"
              onClick={() => onSelectDay && onSelectDay(idx, dayData.day)}
              className={`px-4 py-2 rounded-full text-xs font-semibold transition-all duration-200 shrink-0 ${
                isSelected
                  ? 'bg-swiggy-500 text-white shadow-md scale-105'
                  : 'glass-panel text-slate-700 dark:text-slate-200 hover:text-swiggy-600 hover:bg-white dark:hover:bg-slate-800'
              }`}
            >
              <span>{shortName}</span>
              <span className="ml-1.5 opacity-75 font-normal">₹{dayData.total_cost || 1250}</span>
            </button>
          )
        })}
      </div>
    </div>
  )
}

export default DaySelector
